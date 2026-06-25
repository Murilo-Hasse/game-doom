from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight, Vec4, Vec3, DirectionalLight, loadPrcFileData
from panda3d.bullet import (
    BulletWorld,
    BulletRigidBodyNode,
    BulletTriangleMeshShape,
    BulletTriangleMesh,
    BulletDebugNode
)

from input_handler import InputHandler
from player_controller import PlayerController
from level import Level
from enemy import Enemy

loadPrcFileData("", """
    fullscreen true
    win-size 1920 1080
""")


class MyApp(ShowBase):
    def __init__(self):
        super().__init__()

        self.disableMouse()

        # ---------------- INPUT ----------------
        self.inputHandler = InputHandler(self)

        # ---------------- LEVEL ROOT ----------------
        self.level_root = self.render.attachNewNode("level_root")
        self.current_level = None

        # ---------------- SCENE (STATIC ENV ROOT) ----------------
        self.map_root = self.level_root.attachNewNode("map_root")

        # ---------------- LIGHTS ----------------
        ambientLight = AmbientLight("ambient light")
        ambientLight.setColor(Vec4(0.2, 0.2, 0.2, 1))
        self.ambientLightNodePath = self.render.attachNewNode(ambientLight)
        self.render.setLight(self.ambientLightNodePath)

        mainLight = DirectionalLight("main light")
        self.mainLightNodePath = self.render.attachNewNode(mainLight)
        self.mainLightNodePath.setHpr(45, -45, 0)
        self.render.setLight(self.mainLightNodePath)

        self.render.setShaderAuto()

        # ---------------- PHYSICS ----------------
        self.bulletWorld = BulletWorld()
        self.bulletWorld.setGravity(Vec3(0, 0, -9.81))

        # ---------------- DEBUG ----------------
        debugNode = BulletDebugNode('Debug')
        debugNode.showWireframe(True)
        debugNode.showConstraints(True)
        debugNode.showBoundingBoxes(False)
        debugNode.showNormals(False)

        self.debugNP = self.render.attachNewNode(debugNode)
        #self.debugNP.show()

        self.bulletWorld.setDebugNode(debugNode)

        # ---------------- PLAYER ----------------
        self.player = PlayerController(self)

        # ---------------- UPDATE LOOP ----------------
        self.updateTask = taskMgr.add(self.update, "update")

        # ---------------- LOAD FIRST LEVEL ----------------
        self.switch_level(
            "maps/doorless2.glb",
            Vec3(20.504173, 22.341251, 5.3599977)
        )
        enemy = Enemy(self, Vec3(22, 22, 5))

    # =========================================================
    # LEVEL SYSTEM
    # =========================================================
    def switch_level(self, level_path, spawn_pos):

        # ---- remove previous level ----
        if self.current_level is not None:

            if hasattr(self.current_level, "root"):
                self.current_level.root.removeNode()

            if hasattr(self.current_level, "collision_body"):
                self.bulletWorld.removeRigidBody(self.current_level.collision_body)

        # ---- load new level ----
        self.current_level = Level(
            level_path,
            spawn_pos,
            [],
            self.loader,
            self.level_root
        )


        # ensure scene is parented properly
        if hasattr(self.current_level, "root"):
            self.current_level.root.reparentTo(self.level_root)

        # ---- reset player ----
    
          # ---------------- LIGHTS ----------------
        ambientLight = AmbientLight("ambient light")
        ambientLight.setColor(Vec4(0.2, 0.2, 0.2, 1))
        self.ambientLightNodePath = self.render.attachNewNode(ambientLight)
        self.render.setLight(self.ambientLightNodePath)

        mainLight = DirectionalLight("main light")
        self.mainLightNodePath = self.render.attachNewNode(mainLight)
        self.mainLightNodePath.setHpr(45, -45, 0)
        self.render.setLight(self.mainLightNodePath)

        self.render.setShaderAuto()

        # ---------------- PHYSICS ----------------
        self.bulletWorld = BulletWorld()
        self.bulletWorld.setGravity(Vec3(0, 0, -9.81))
        self.current_level.build_collision(self.bulletWorld)

        # ---------------- DEBUG ----------------
        debugNode = BulletDebugNode('Debug')
        debugNode.showWireframe(True)
        debugNode.showConstraints(True)
        debugNode.showBoundingBoxes(False)
        debugNode.showNormals(False)
        self.bulletWorld.setDebugNode(debugNode)
        self.debugNP = self.render.attachNewNode(debugNode)
        #self.debugNP.show()
        self.player.__init__(self)
        self.player.playerNP.setPos(spawn_pos)


    # =========================================================
    # UPDATE LOOP
    # =========================================================
    def update(self, task):
        dt = globalClock.getDt()

        self.bulletWorld.doPhysics(dt)
        return task.cont


app = MyApp()
app.run()