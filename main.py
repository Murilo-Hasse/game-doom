from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight, Vec4, Vec3, DirectionalLight, loadPrcFileData, WindowProperties
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
from game_hud import GameHUD
from ui import MenuUI

loadPrcFileData("", """
    fullscreen true
    win-size 1920 1080
""")

class MyApp(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()

        # Flag para controlar se a simulação física/gameplay está rodando
        self.game_running = False

        # ---------------- SYSTEM UI ----------------
        self.ui = MenuUI(self)
        self.game_hud = GameHUD(self)
        self.game_hud.hide() # Esconde o HUD no menu principal

        # ---------------- INPUT ----------------
        self.inputHandler = InputHandler(self)
        self.player = None  
        self.enemies = []   
        self.death_sound = self.loader.loadSfx("assets/dead.wav")

        # ---------------- LEVEL ROOT ----------------
        # Esse node vai conter tudo relacionado ao gameplay (mapa, jogador, inimigos)
        self.level_root = self.render.attachNewNode("level_root")
        self.level_root.hide() # Começa escondido enquanto estamos no menu principal
        self.current_level = None

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
        self.debugNP = self.render.attachNewNode(debugNode)
        self.bulletWorld.setDebugNode(debugNode)

        # ---------------- UPDATE LOOP ----------------
        self.updateTask = taskMgr.add(self.update, "update")

        # Inicia mostrando o Menu Principal
        self.ui.create_main_menu(on_play=self.start_game)

    def start_game(self):
        self.ui.clear_menu()
        self.ui.clear_game_over()
        
        self.level_root.show()

        props = WindowProperties()
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.M_confined)
        self.win.requestProperties(props)

        self.switch_level(
            "maps/doorless2.glb",
            Vec3(29.929702, -23.101972, 5.3600015)
        )
        
        self.game_hud.show()
        self.game_running = True

    def game_over(self):
        self.game_running = False
        self.game_hud.hide()
        self.level_root.hide()
        self.player.cleanup()
        self.enemies.clear()
        self.ui.create_game_over_screen(on_restart=self.start_game)

    # =========================================================
    # LEVEL SYSTEM
    # =========================================================
    def switch_level(self, level_path, spawn_pos):
        # Limpa os inimigos da partida anterior
        if hasattr(self, 'enemies') and self.enemies:
            for enemy in self.enemies:
                if hasattr(enemy, 'destroy'):
                    enemy.destroy()
            self.enemies.clear()

        # Limpa o jogador anterior se existir
        if hasattr(self, 'player') and self.player is not None:
            if hasattr(self.player, 'destroy'):
                self.player.destroy()

        # Remove o cenário antigo
        if self.current_level is not None:
            if hasattr(self.current_level, "root"):
                self.current_level.root.removeNode()
            if hasattr(self.current_level, "collision_body"):
                self.bulletWorld.removeRigidBody(self.current_level.collision_body)

        # Carrega o mapa novo anexado à raiz do cenário do gameplay
        self.current_level = Level(
            level_path,
            spawn_pos,
            [],
            self.loader,
            self.level_root
        )

        if hasattr(self.current_level, "root"):
            self.current_level.root.reparentTo(self.level_root)

        # Recria as colisões estáticas no mundo físico
        self.current_level.build_collision(self.bulletWorld)
        
        # Instancia o jogador passando "self" para que ele seja filho do level_root interna/externamente
        self.player = PlayerController(self)
        self.player.playerNP.setPos(spawn_pos)
        
        # Gera os Inimigos
        self.enemy_count = 10
        self.enemies = [
            Enemy(self, Vec3(22, 22, 5)),
            Enemy(self, Vec3(35.693195, 45.9015, 6.359986)),
            Enemy(self, Vec3(22.48859, 45.908767, 4.3599963)),
            Enemy(self, Vec3(23.459482, 54.044605, -12.640005)),
            Enemy(self, Vec3(-0.5993993, 104.69268, -12.640011)),
            Enemy(self, Vec3(40.782073, 104.492454, -12.64001)),
            Enemy(self, Vec3(-20.766042, 135.44317, -8.640012)),
            Enemy(self, Vec3(-33.921745, 173.79516, -6.6400136)),
            Enemy(self, Vec3(27.136106, 169.1285, -3.6400151)),
            Enemy(self, Vec3(25.280292, 185.7949, -3.6400141))
        ]

    # =========================================================
    # UPDATE LOOP
    # =========================================================
    def update_enemies(self):
        if hasattr(self, 'game_hud'):
            self.game_hud.update_enemies(self.enemy_count, 10)
        
        if self.enemy_count <= 0:
            self.game_over()

    def update(self, task):
        dt = globalClock.getDt()
        
        if self.game_running:
            self.update_enemies()
            self.bulletWorld.doPhysics(dt)
            
        return task.cont

app = MyApp()
app.run()