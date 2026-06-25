from panda3d.core import WindowProperties, Vec3
from direct.task import Task

from game_object import GameObject
from input_handler import InputHandler


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

        self.capture_mouse()

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

        GameObject.update(self, dt)  # Call the parent update method


        return Task.cont