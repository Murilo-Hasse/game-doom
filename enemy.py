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
            colliderName="enemy_collider",
            colliderHeight=2.4
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
        self.billboard.setPos(0, 0, -0.4)  # Adjust the Z position to be above the ground
        self.enemy_mask = BitMask32.bit(2) # Define mask for enemies

        self.playerNode.setIntoCollideMask(self.enemy_mask)
        self.playerNode.setPythonTag("object", self)
        self.task_name = f"enemy_update_task_{id(self)}"
        self.app.taskMgr.add(self.update, self.task_name)


    def takeDamage(self, damage):
        self.health -= damage        
        if self.health <= 0:
            self.die()

    def die(self):
        if hasattr(self.app, 'death_sound') and self.app.death_sound:
            self.app.death_sound.play()
        self.app.enemy_count -= 1  
        self.cleanup() 
    
    def cleanup(self):
        self.app.bulletWorld.removeCharacter(self.playerNode)
        self.app.taskMgr.remove(self.task_name)
        self.actor.removeNode()

    def update(self, task):
        dt = globalClock.getDt()

        GameObject.update(self, dt)  # Call the parent update method
        return task.cont