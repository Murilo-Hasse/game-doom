from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight
from panda3d.core import Vec4, Vec3
from panda3d.core import DirectionalLight
from panda3d.core import BitMask32, loadPrcFileData
from input_handler import InputHandler
from player_controller import PlayerController
from panda3d.bullet import (
    BulletWorld,
    BulletRigidBodyNode,
    BulletTriangleMeshShape,
    BulletTriangleMesh
)
from panda3d.bullet import BulletDebugNode
loadPrcFileData("", """
    fullscreen true
    win-size 1920 1080
""")
class MyApp(ShowBase):

    def __init__(self):
        super().__init__()
        self.inputHandler = InputHandler(self)
        self.map_root = self.render.attachNewNode("map_root")

        # Load the environment model.
        self.scene = self.loader.loadModel("maps/untitled.glb")
        self.scene.reparentTo(self.map_root)
        self.map_root.setScale(2, 2, 2)

        self.scene.setPos(0, 0, 0)
        self.scene.setHpr(0, -270, 0)
        ambientLight = AmbientLight("ambient light")
        ambientLight.setColor(Vec4(0.2, 0.2, 0.2, 1))
        self.ambientLightNodePath = self.render.attachNewNode(ambientLight)
        self.render.setLight(self.ambientLightNodePath)
        mainLight = DirectionalLight("main light")
        self.mainLightNodePath = self.render.attachNewNode(mainLight)
        # Turn it around by 45 degrees, and tilt it down by 45 degrees
        self.mainLightNodePath.setHpr(45, -45, 0)
        self.render.setLight(self.mainLightNodePath)
        self.render.setShaderAuto()
    
        self.updateTask = taskMgr.add(self.update, "update")
        self.disableMouse()

        # Collision system
        self.bulletWorld = BulletWorld()
        self.bulletWorld.setGravity(Vec3(0, 0, -9.81))
        mesh = BulletTriangleMesh()
        terrain_col_np = self.scene.find("**/TERRAIN_COL*")
        mesh = BulletTriangleMesh()

        geom_node = terrain_col_np.node()

        for geom in geom_node.getGeoms():
            mesh.addGeom(geom)

        shape = BulletTriangleMeshShape(mesh, dynamic=False)

        body = BulletRigidBodyNode("terrain")
        body.addShape(shape)
        body.setMass(0)  # IMPORTANT: static object

        terrain_np = self.render.attachNewNode(body)
        terrain_np.setScale(2, 2, 2)

        terrain_np.setHpr(0, -270, 0)
        terrain_np.setPos(0,0,0)

        self.bulletWorld.attachRigidBody(body)

        
        debugNode = BulletDebugNode('Debug')
        debugNode.showWireframe(True)
        debugNode.showConstraints(True)
        debugNode.showBoundingBoxes(False)
        debugNode.showNormals(False)
        debugNP = render.attachNewNode(debugNode)
        #debugNP.show()

        debugNP = self.render.attachNewNode(debugNode)
        self.bulletWorld.setDebugNode(debugNode)
        self.bulletWorld.attachRigidBody(body)
        self.player = PlayerController(self)

    def update(self, task):
        dt = globalClock.getDt()
        self.bulletWorld.doPhysics(dt)
        print("Player Position:", self.player.playerNP.getPos())
        return task.cont
app = MyApp()
app.run()   

