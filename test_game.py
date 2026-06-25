import unittest
from unittest.mock import MagicMock, patch
import sys
from panda3d.core import Vec3, Vec2, TransparencyAttrib

# Mock standard modules/objects before importing game files to prevent startup crashes
# (e.g. taskMgr and globalClock are defined in ShowBase/Panda3D runtime)
sys.modules['direct.task.Task'] = MagicMock()
class MockGlobalClock:
    def getDt(self):
        return 0.016

import builtins
builtins.globalClock = MockGlobalClock()
builtins.taskMgr = MagicMock()
builtins.render = MagicMock()

# Now import the modules under test
from game_object import GameObject
from input_handler import InputHandler
from player_controller import PlayerController
from enemy import Enemy

class TestGameObject(unittest.TestCase):
    def setUp(self):
        # Create a mock for ShowBase app
        self.app = MagicMock()
        self.app.render = MagicMock()
        self.app.bulletWorld = MagicMock()

    def test_health_alteration(self):
        # Instantiate GameObject
        go = GameObject(self.app, pos=Vec3(0, 0, 0), maxHealth=100, maxSpeed=10, colliderName="test_go")
        
        # Test default health values
        self.assertEqual(go.health, 100)
        self.assertEqual(go.maxHealth, 100)
        
        # Alter health downwards
        go.alterHealth(-30)
        self.assertEqual(go.health, 70)
        
        # Alter health upwards, should cap at maxHealth
        go.alterHealth(50)
        self.assertEqual(go.health, 100)
        
        # Alter health way below 0
        go.alterHealth(-150)
        self.assertEqual(go.health, -50)

    def test_velocity_clamping_and_friction(self):
        go = GameObject(self.app, pos=Vec3(0, 0, 0), maxHealth=100, maxSpeed=10, colliderName="test_go")
        
        # 1. Test speed clamping
        go.velocity = Vec3(20, 0, 0) # speed 20 is > maxSpeed 10
        go.walking = True
        go.update(0.1)
        self.assertAlmostEqual(go.velocity.length(), 10.0)
        
        # 2. Test friction application when not walking
        go.walking = False
        go.velocity = Vec3(5, 0, 0)
        # FRICTION = 150.0. For dt = 0.1, frictionVal = 150 * 0.1 = 15.0
        # Since frictionVal (15) > speed (5), velocity should be set to 0.
        go.update(0.1)
        self.assertEqual(go.velocity, Vec3(0, 0, 0))

        # 3. Test partial friction slowdown
        go.walking = False
        go.velocity = Vec3(20, 0, 0) # will clamp to 10 first
        # For dt = 0.01, frictionVal = 150 * 0.01 = 1.5
        # Since frictionVal (1.5) < clamped speed (10), velocity should decrease to 8.5
        go.update(0.01)
        self.assertAlmostEqual(go.velocity.length(), 8.5)


class TestInputHandler(unittest.TestCase):
    def test_key_mapping(self):
        app = MagicMock()
        ih = InputHandler(app)
        
        # Check initial state
        self.assertFalse(ih.keyMap["up"])
        self.assertFalse(ih.keyMap["shoot"])
        self.assertFalse(ih.keyMap["debug"])
        
        # Simulate button presses
        ih.updateKeyMap("up", True)
        self.assertTrue(ih.keyMap["up"])
        
        ih.updateKeyMap("shoot", True)
        self.assertTrue(ih.keyMap["shoot"])
        
        # Simulate button release
        ih.updateKeyMap("up", False)
        self.assertFalse(ih.keyMap["up"])


class TestPlayerController(unittest.TestCase):
    def setUp(self):
        self.app = MagicMock()
        self.app.render = MagicMock()
        self.app.bulletWorld = MagicMock()
        self.app.win = MagicMock()
        self.app.win.getXSize.return_value = 800
        self.app.win.getYSize.return_value = 600
        
        # Mock pointer to return screen center so update_mouse returns early
        pointer_mock = MagicMock()
        pointer_mock.getX.return_value = 400
        pointer_mock.getY.return_value = 300
        self.app.win.getPointer.return_value = pointer_mock
        
        # Mock loaders/textures to prevent loading actual assets during test
        self.app.loader = MagicMock()
        self.app.loader.loadTexture.return_value = MagicMock()
        self.app.loader.loadSfx.return_value = MagicMock()
        self.app.taskMgr = MagicMock()
        
    def test_player_controller_movement_inputs(self):
        pc = PlayerController(self.app)
        
        # Test input mapping to movement vectors
        pc.inputHandler.keyMap["up"] = True
        pc.inputHandler.keyMap["left"] = True
        move_dir = pc.get_input()
        
        # Normalize of (-1, 1, 0) should have length 1.0, facing forward-left
        self.assertAlmostEqual(move_dir.length(), 1.0, places=5)
        self.assertLess(move_dir.x, 0)
        self.assertGreater(move_dir.y, 0)
        
        # Apply to move
        pc.move()
        self.assertAlmostEqual(pc.velocity.x, move_dir.x * pc.speed, places=5)
        self.assertAlmostEqual(pc.velocity.y, move_dir.y * pc.speed, places=5)

    def test_player_cooldown_timer(self):
        pc = PlayerController(self.app)
        pc.shoot_timer = 0.2
        pc.inputHandler.keyMap["shoot"] = True
        
        # Call update with dt = 0.1: shoot_timer should reduce to 0.1, and shooting should NOT trigger
        pc.shoot_weapon = MagicMock()
        pc.update(None)
        self.assertAlmostEqual(pc.shoot_timer, 0.2 - 0.016)  # globalClock.getDt() returns 0.016 in MockGlobalClock
        pc.shoot_weapon.assert_not_called()

    def test_footsteps_timer(self):
        pc = PlayerController(self.app)
        pc.footstep_sound = MagicMock()
        pc.footstep_timer = 0.3
        pc.footstep_delay = 0.35
        pc.grounded = True
        pc.velocity = Vec3(5, 5, 0) # Moving horizontally
        
        # Update footsteps with dt = 0.1. 0.3 + 0.1 = 0.4 > 0.35. Footstep should trigger.
        pc.update_footsteps(0.1)
        self.assertEqual(pc.footstep_timer, 0.0) # Reset to 0
        pc.footstep_sound.play.assert_called_once()
        
        # Reset mock
        pc.footstep_sound.reset_mock()
        
        # Update footsteps when not moving. Timer should reset to 0.
        pc.velocity = Vec3(0, 0, 0)
        pc.update_footsteps(0.1)
        self.assertEqual(pc.footstep_timer, 0.0)
        pc.footstep_sound.play.assert_not_called()


class TestEnemy(unittest.TestCase):
    def setUp(self):
        self.app = MagicMock()
        self.app.render = MagicMock()
        self.app.bulletWorld = MagicMock()
        self.app.loader = MagicMock()
        self.app.loader.loadTexture.return_value = MagicMock()
        self.app.taskMgr = MagicMock()
        
    def test_enemy_take_damage_and_die(self):
        enemy = Enemy(self.app, pos=Vec3(0, 0, 0))
        enemy.die = MagicMock()
        
        # Enemy starts with health = 80
        self.assertEqual(enemy.health, 80)
        
        # Take partial damage
        enemy.takeDamage(30)
        self.assertEqual(enemy.health, 50)
        enemy.die.assert_not_called()
        
        # Take lethal damage
        enemy.takeDamage(50)
        self.assertEqual(enemy.health, 0)
        enemy.die.assert_called_once()

    def test_enemy_death_sound(self):
        enemy = Enemy(self.app, pos=Vec3(0, 0, 0))
        self.app.death_sound = MagicMock()
        self.app.enemy_count = 10
        
        enemy.die()
        self.app.death_sound.play.assert_called_once()
        self.assertEqual(self.app.enemy_count, 9)


if __name__ == "__main__":
    unittest.main()
