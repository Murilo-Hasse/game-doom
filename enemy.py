from panda3d.core import Vec3, CardMaker
from game_object import GameObject
from panda3d.core import SamplerState
from panda3d.core import TransparencyAttrib, BitMask32
from panda3d.bullet import BulletCharacterControllerNode, BulletRigidBodyNode, BulletCapsuleShape

class Enemy(GameObject):
    def __init__(self, app,pos):
        super().__init__(
            app,
            pos=pos, 
            maxHealth=80,
            maxSpeed=400,
            colliderName="enemy_collider"
        )
        
        cm = CardMaker('enemy_billboard_card')
        cm.setFrame(-1, 1, -1, 1) 

        self.billboard = self.actor.attachNewNode(cm.generate())
        
        texture = app.loader.loadTexture("imp.png")
        texture.setFormat(texture.F_rgba)
        texture.setMagfilter(SamplerState.FT_nearest)
        texture.setMinfilter(SamplerState.FT_nearest)
        self.billboard.setTransparency(TransparencyAttrib.MAlpha)

        self.billboard.setTexture(texture)
        self.billboard.setScale(2,1,3) 
        self.billboard.setBillboardPointEye()
        self.billboard.setZ(1.0)

        ##Collision mask
        self.enemy_mask = BitMask32.bit(2) # Define mask for enemies

        enemy_shape = BulletCapsuleShape(1.4, 1.4, 1) # radius, height, up-axis
        enemy_node = BulletRigidBodyNode('Enemy')
        enemy_node.addShape(enemy_shape)
        enemy_node.setIntoCollideMask(self.enemy_mask)
        enemy_node.setPythonTag("object", self) 
        app.bulletWorld.attachRigidBody(enemy_node)
        self.app.taskMgr.add(self.update, "enemy_update_task")


    def takeDamage(self, damage):
        self.health -= damage
        print(f"Enemy took damage! Remaining health: {self.health}")
        
        if self.health <= 0:
            self.die()

    def die(self):
        print("Enemy died!")
        self.app.bulletWorld.removeRigidBody(self.playerNode)
        self.actor.removeNode()
    
    def update(self, task):
        dt = globalClock.getDt()

        GameObject.update(self, dt)  # Call the parent update method
        return task.cont