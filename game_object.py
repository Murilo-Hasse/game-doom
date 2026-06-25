from panda3d.core import Vec3, Vec2
from direct.actor.Actor import Actor
from panda3d.core import CollisionSphere, CollisionNode, BitMask32
from panda3d.bullet import BulletCharacterControllerNode, BulletCapsuleShape
FRICTION = 150.0

class GameObject():
    def __init__(self, app, pos, maxHealth, maxSpeed, colliderName,colliderHeight=1.4):
        self.app = app

        # --- health ---
        self.maxHealth = maxHealth
        self.health = maxHealth

        # --- movement ---
        self.maxSpeed = maxSpeed
        self.walking = False
        self.grounded = True
        # --- BULLET PLAYER SHAPE ---
        self.shape = BulletCapsuleShape(1.4, colliderHeight, 2)  

        self.playerNode = BulletCharacterControllerNode(self.shape, 0.4, colliderName)

        self.playerNP = app.render.attachNewNode(self.playerNode)
        self.playerNP.setPos(pos)
        app.bulletWorld.attachCharacter(self.playerNode)
        self.velocity = Vec3(0, 0, 0)

        self.actor = self.playerNP  



    def update(self, dt):
        speed = self.velocity.length()
        if speed > self.maxSpeed:
            self.velocity.normalize()
            self.velocity *= self.maxSpeed
            speed = self.maxSpeed

        if not self.walking:
            frictionVal = FRICTION*dt
            if frictionVal > speed:
                self.velocity.set(0, 0, 0)
            else:
                frictionVec = -self.velocity
                frictionVec.normalize()
                frictionVec *= frictionVal

                self.velocity += frictionVec

        self.playerNode.setLinearMovement(self.velocity, True)
        if self.playerNode.isOnGround():
            self.grounded = True
        else:
            self.grounded = False
        
    def alterHealth(self, dHealth):
        self.health += dHealth

        if self.health > self.maxHealth:
            self.health = self.maxHealth

    def cleanup(self):
        if hasattr(self, "playerNode"):
            self.app.bulletWorld.removeCharacter(self.playerNode)

        if self.playerNP:
            self.playerNP.removeNode()
            self.playerNP = None