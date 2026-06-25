from panda3d.core import WindowProperties, Vec3, Vec2, CardMaker, SequenceNode
from direct.task import Task
from panda3d.core import SamplerState
from game_object import GameObject
from input_handler import InputHandler
from panda3d.core import TransparencyAttrib, BitMask32, TextureStage
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

        cm = CardMaker("gun")
        cm.setFrame(-0.6, 0.6, -0.6, 0.6) 

        self.gun_node = app.aspect2d.attachNewNode(cm.generate())
        self.gun_node.setTexture(self.gun)
        self.gun_node.setPos(0, 0, -0.4)
        self.gun_node.setScale(2,1,1)

        self.gun_node.setDepthTest(False)
        self.gun_node.setDepthWrite(False)
        self.gun_node.setTransparency(TransparencyAttrib.MAlpha)
        self.current_frame = 0
        self.frame_duration = 0.08
        self.anim_timer = 0
        self.is_shooting = False
        self.gun_frames = 8
        self.set_frame(0)
        # ===== GUN COOLDOWN =====
        self.shoot_cooldown = 0.4  
        self.shoot_timer = 0.0    

        # ===== SOUND =====
        self.shoot_sound = app.loader.loadSfx("assets/shoot.wav")
        self.footstep_sound = app.loader.loadSfx("assets/footstep.wav")
        self.footstep_timer = 0.0
        self.footstep_delay = 0.35

        self.capture_mouse()
        self.app.taskMgr.add(self.update, "player_update")

    # =========================================================
    # MOUSE
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

        start_pos = self.app.cam.getPos(render)
        
        forward_vector = render.getRelativeVector(self.app.cam, Vec3(0, 1, 0))
        forward_vector.normalize() 
        
        weapon_range = 2000.0
        target_pos = start_pos + (forward_vector * weapon_range)
                
        mask = BitMask32.bit(2)
        result = self.app.bulletWorld.rayTestClosest(start_pos, target_pos, mask)
        if result.hasHit():
            hit_node = result.getNode() 
            hit_pos = result.getHitPos()
            self.spawn_hit_particle(hit_pos-forward_vector*0.5) 

            if hit_node.hasPythonTag("object"):
                enemy = hit_node.getPythonTag("object")
                if hasattr(enemy, "takeDamage"):
                    enemy.takeDamage(50)

    def spawn_hit_particle(self, position):
        anim_node = SequenceNode("spark_animation")
        
        cm = CardMaker("spark_frame")
        cm.setFrame(-1, 1, -1, 1)
        
        for i in range(1, 7):
            frame_card = cm.generate() 
            frame_nodepath = render.attachNewNode(frame_card)
            
            texture = self.app.loader.loadTexture(f"particles/spark{i}.png")
            frame_nodepath.setTexture(texture)
            
            anim_node.addChild(frame_nodepath.node())
            
            frame_nodepath.removeNode()

        anim_node.setFrameRate(30) 
        anim_node.loop(False)      
        anim_node.play()         
        
        spark = render.attachNewNode(anim_node)
        spark.setPos(position)
        spark.setScale(0.5)
        
        spark.setTransparency(TransparencyAttrib.MAlpha)
        spark.setBillboardPointEye()
        
        taskMgr.doMethodLater(0.2, lambda task: spark.removeNode(), "CleanUpSpark")

    ### JUMP 
    def jump(self):
        if self.grounded and self.inputHandler.keyMap["jump"]:
            self.velocity.z = self.jump_force
            self.grounded = False
    ### Cleanup
    def cleanup(self):
            if hasattr(self, "playerNode"):
                self.app.bulletWorld.removeCharacter(self.playerNode)

            if self.playerNP:
                self.playerNP.removeNode()
            self.app.taskMgr.remove("player_update")

    ### GRAVITY
    def apply_gravity(self, dt):
        if not self.grounded:
            self.velocity.z -= self.gravity * dt


    # =========================================================
    # UPDATE
    # =========================================================
    def set_frame(self, frame):
        frame_width = 1 / self.gun_frames

        self.gun_node.setTexScale(
            TextureStage.getDefault(),
            frame_width,
            1
        )

        self.gun_node.setTexOffset(
            TextureStage.getDefault(),
            frame * frame_width,
            0
        )


    def play_gun_animation(self):
        self.current_frame = 0
        self.anim_timer = 0
        self.is_shooting = True

        self.set_frame(0)


    def update_gun_animation(self, dt):
        if not self.is_shooting:
            return

        self.anim_timer += dt

        if self.anim_timer >= self.frame_duration:

            self.anim_timer = 0
            self.current_frame += 1

            if self.current_frame >= self.gun_frames:
                self.current_frame = 0
                self.is_shooting = False

            self.set_frame(self.current_frame)
    
    def update(self, task):
        dt = globalClock.getDt()

        self.update_gun_animation(dt)

        if self.shoot_timer > 0:
            self.shoot_timer -= dt

        self.update_mouse()
        self.move()
        self.jump()
        self.apply_gravity(dt)

        if self.inputHandler.keyMap["shoot"] and self.shoot_timer <= 0:
            self.shoot_weapon()

            self.play_gun_animation()   # ← add this

            self.shoot_timer = self.shoot_cooldown

        GameObject.update(self, dt)
        self.update_footsteps(dt)

        return Task.cont

    def update_footsteps(self, dt):
        is_moving_horizontally = Vec2(self.velocity.x, self.velocity.y).length() > 0.1
        if self.grounded and is_moving_horizontally:
            self.footstep_timer += dt
            if self.footstep_timer >= self.footstep_delay:
                self.footstep_timer = 0.0
                if self.footstep_sound:
                    self.footstep_sound.play()
        else:
            self.footstep_timer = 0.0