from panda3d.core import Vec3
from panda3d.bullet import (
    BulletRigidBodyNode,
    BulletTriangleMeshShape,
    BulletTriangleMesh
)

class Level:
    def __init__(self, map_path, start_pos, entities, loader, parent_node):
        self.map_path = map_path
        self.start_pos = start_pos
        self.entities = entities

        # ---------------- ROOT ----------------
        self.root = parent_node.attachNewNode(f"level-{map_path}")

        # ---------------- MODEL ----------------
        self.model = loader.loadModel(map_path)
        self.model.reparentTo(self.root)

        self.model.setPos(0, 0, 0)
        self.model.setScale(2, 2, 2)
        self.model.setHpr(0, -270, 0)

        # ---------------- COLLISION ----------------
        self.collision_body = None
    def build_collision(self, bullet_world):

        terrain_col_np = self.model.find("**/TERRAIN_COL*")

        if terrain_col_np.isEmpty():
            print("[Level] TERRAIN_COL not found")
            return

        geom_node = terrain_col_np.node()

        mesh = BulletTriangleMesh()

        # IMPORTANT: apply model transform manually
        transform = terrain_col_np.getNetTransform()

        for geom in geom_node.getGeoms():
            mesh.addGeom(geom)

        shape = BulletTriangleMeshShape(mesh, dynamic=False)

        body = BulletRigidBodyNode("terrain")
        body.addShape(shape)
        body.setMass(0)

        body_np = self.root.attachNewNode(body)

        # ONLY position/rotation once (NO scale)
        body_np.setTransform(self.model.getTransform())

        bullet_world.attachRigidBody(body)

        self.collision_body = body