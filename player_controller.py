from panda3d.core import WindowProperties, Vec3, Vec2, CardMaker
from direct.task import Task
from panda3d.core import SamplerState
from game_object import GameObject
from input_handler import InputHandler
from panda3d.core import TransparencyAttrib, BitMask32

class PlayerController(GameObject):

    def __init__(self, app):
        super().__init__(
            app,
            pos=Vec3(0, 0, 2),
            maxHealth=100,
            maxSpeed=500,
            colliderName="player_collider"
        )

        self.app = app
        self.inputHandler = InputHandler(app)

        # ===== PLAYER =====
        self.player = self.actor
        self.player.setPos(29.504173, -22.341251, 5.3599977)

        # ===== CAMERA =====
        app.disableMouse()
        app.camera.reparentTo(self.player)
        app.camera.setPos(0, 0, 1.4)
        app.camera.setHpr(0, 0, 0)

        self.pitch = 0
        self.mouse_sensitivity = 0.05

        # ===== MOVEMENT =====
        self.speed = 20
        self.jump_force = 30
        self.gravity = 30

        self.velocity = Vec3(1, 0, 0)
        self.grounded = False

        # ===== mouse center =====
        self.center_x = self.app.win.getXSize() // 2
        self.center_y = self.app.win.getYSize() // 2

        #=====GUN========
         # Load gun sprite
        self.gun = app.loader.loadTexture("gun.png")
        self.gun.setFormat(self.gun.F_rgba)
        self.gun.setMagfilter(SamplerState.FT_nearest)
        self.gun.setMinfilter(SamplerState.FT_nearest)
        # Create a card (2D quad)
        cm = CardMaker("gun")
        cm.setFrame(-0.6, 0.6, -0.6, 0.6)  # size of sprite

        self.gun_node = app.aspect2d.attachNewNode(cm.generate())
        self.gun_node.setTexture(self.gun)
        # Position it bottom-center (FPS style)
        self.gun_node.setPos(0, 0, -0.4)
        self.gun_node.setScale(2,1,1)

        # Ensure it renders on top
        self.gun_node.setDepthTest(False)
        self.gun_node.setDepthWrite(False)
        self.gun_node.setTransparency(TransparencyAttrib.MAlpha)
        self.capture_mouse()

        # ===== SOUND =====
        self.shoot_sound = app.loader.loadSfx("assets/shoot.wav")
        self.footstep_sound = app.loader.loadSfx("assets/footstep.wav")
        self.footstep_timer = 0.0
        self.footstep_delay = 0.35

        self.app.taskMgr.add(self.update, "player_update")

    # =========================================================
    # MOUSE (UNCHANGED LOGIC)
    # =========================================================
    def capture_mouse(self):
        props = WindowProperties()
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.M_absolute)

        self.app.win.requestProperties(props)

        self.center_x = self.app.win.getXSize() // 2
        self.center_y = self.app.win.getYSize() // 2

        self.app.win.movePointer(0, self.center_x, self.center_y)

    def update_mouse(self):
        md = self.app.win.getPointer(0)

        x = md.getX()
        y = md.getY()

        dx = x - self.center_x
        dy = y - self.center_y

        if dx == 0 and dy == 0:
            return

        # yaw
        self.player.setH(self.player.getH() - dx * self.mouse_sensitivity)

        # pitch
        self.pitch -= dy * self.mouse_sensitivity
        self.pitch = max(-89, min(89, self.pitch))

        self.app.camera.setP(self.pitch)
        self.app.camera.setH(0)
        self.app.camera.setR(0)

        self.app.win.movePointer(0, self.center_x, self.center_y)

    # =========================================================
    # MOVEMENT
    # =========================================================
    def get_input(self):
        move = Vec3(0, 0, 0)

        if self.inputHandler.keyMap["up"]:
            move.y += 1
        if self.inputHandler.keyMap["down"]:
            move.y -= 1
        if self.inputHandler.keyMap["left"]:
            move.x -= 1
        if self.inputHandler.keyMap["right"]:
            move.x += 1

        if move.length() > 0:
            move.normalize()

        return move

    def move(self):
        direction = self.get_input()

        # horizontal velocity
        self.velocity.x = direction.x * self.speed
        self.velocity.y = direction.y * self.speed


    def shoot_weapon(self):
        # Play shooting sound
        if self.shoot_sound:
            self.shoot_sound.play()

        # 1. Get camera lens and screen center
        lens = self.app.cam.node().getLens()
        screen_pos = (0, 0) # Exact center of the screen (crosshair)
        
        near_point = Vec3()
        far_point = Vec3()
        
        if lens.extrude(screen_pos, near_point, far_point):
            # Convert relative cam points to world space
            start_pos = render.getRelativePoint(self.app.cam, near_point)
            end_pos = render.getRelativePoint(self.app.cam, far_point)
            
            # Calculate range (e.g., weapon range of 200 units)
            direction = end_pos - start_pos
            direction.normalize()
            weapon_range = 20000.0
            target_pos = start_pos + (direction * weapon_range)
            
            # 2. Define what the ray is allowed to hit
            # This mask looks for bit 2 (Enemies) and optionally bit 1 (World/Walls)
            mask = BitMask32.bit(2) 
            
            # 3. Perform the raycast
            result = self.app.bulletWorld.rayTestClosest(start_pos, target_pos)
            
            if result.hasHit():
                hit_node = result.getNode()
                print(f"Bullet struck: {hit_node.getName()}")
                
                # 4. Check if the hit node contains an Enemy object
                if hit_node.hasPythonTag("object"):
                    hit_object = hit_node.getPythonTag("object")
                    
                    # Check if it has a takeDamage method and call it!
                    if hasattr(hit_object, "takeDamage"):
                        hit_object.takeDamage(damage=25)
    # =========================================================
    # JUMP (SMOOTHER)
    # =========================================================
    def jump(self):
        if self.grounded and self.inputHandler.keyMap["jump"]:
            self.velocity.z = self.jump_force
            self.grounded = False

    # =========================================================
    # GRAVITY (stable integration)
    # =========================================================
    def apply_gravity(self, dt):
        if not self.grounded:
            self.velocity.z -= self.gravity * dt


    # =========================================================
    # UPDATE
    # =========================================================
    def update(self, task):
        dt = globalClock.getDt()

        self.update_mouse()
        self.move()
        self.jump()
        self.apply_gravity(dt)
        if(self.inputHandler.keyMap["shoot"]):
            self.shoot_weapon()
            self.inputHandler.keyMap["shoot"] = False
        GameObject.update(self, dt)  # Call the parent update method

        # Update footsteps
        is_moving_horizontally = Vec2(self.velocity.x, self.velocity.y).length() > 0.1
        if self.grounded and is_moving_horizontally:
            self.footstep_timer += dt
            if self.footstep_timer >= self.footstep_delay:
                self.footstep_timer = 0.0
                if self.footstep_sound:
                    self.footstep_sound.play()
        else:
            self.footstep_timer = 0.0

        return Task.cont