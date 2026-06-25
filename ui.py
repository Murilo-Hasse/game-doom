from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from panda3d.core import WindowProperties, TextNode


class MenuUI:
    """Gerencia as telas de Menu Principal e Game Over."""

    def __init__(self, app):
        self.app = app
        self.menu_elements = []
        self.game_over_elements = []
        self.pause_elements = []


    # =========================================================
    # MENU PRINCIPAL
    # =========================================================
    def create_main_menu(self, on_play):
        self.release_mouse()

        panel = DirectFrame(
            frameColor=(0.05, 0.05, 0.08, 0.85),
            frameSize=(-1.0, 1.0, -0.75, 0.75),
            pos=(0, 0, 0)
        )

        accent = DirectFrame(
            frameColor=(0.6, 0.1, 0.1, 1),
            frameSize=(-0.5, 0.5, -0.01, 0.01),
            pos=(0, 0, 0.5)
        )

        title = OnscreenText(
            text="DOORLEES",
            pos=(0, 0.55), scale=0.22,
            fg=(0.95, 0.85, 0.2, 1),
            shadow=(0, 0, 0, 1), shadowOffset=(0.01, 0.01),
            align=TextNode.ACenter
        )

        subtitle = OnscreenText(
            text="um jogo da UTFPR",
            pos=(0, 0.43), scale=0.05,
            fg=(0.7, 0.7, 0.7, 1), align=TextNode.ACenter
        )

        instructions = OnscreenText(
            text="W A S D — Movimentação\nESPAÇO — Pular\nMOUSE — Câmera",
            pos=(0, 0.1), scale=0.06,
            fg=(0.85, 0.85, 0.85, 1), align=TextNode.ACenter
        )

        play_button = DirectButton(
            text="JOGAR",
            scale=0.12,
            pos=(0, 0, -0.45),
            text_fg=(1, 1, 1, 1),
            frameColor=(
                (0.6, 0.1, 0.1, 1),
                (0.4, 0.05, 0.05, 1),
                (0.75, 0.15, 0.15, 1),
                (0.3, 0.3, 0.3, 1)
            ),
            relief=1,
            command=on_play
        )

        self.menu_elements.extend([panel, accent, title, subtitle, instructions, play_button])

    def clear_menu(self):
        for element in self.menu_elements:
            element.destroy()
        self.menu_elements.clear()

    # =========================================================
    # GAME OVER
    # =========================================================
    def create_game_over_screen(self, on_restart):
        self.release_mouse()

        panel = DirectFrame(
            frameColor=(0.08, 0.02, 0.02, 0.88),
            frameSize=(-1.0, 1.0, -0.6, 0.6),
            pos=(0, 0, 0)
        )

        go_text = OnscreenText(
            text="FIM DE JOGO",
            pos=(0, 0.25), scale=0.2,
            fg=(0.85, 0.1, 0.1, 1),
            shadow=(0, 0, 0, 1), shadowOffset=(0.01, 0.01),
            align=TextNode.ACenter
        )
        
        go_text2 = OnscreenText(
            text="Todos os inimigos foram derrotados!",
            pos=(0, 0.17), scale=0.05,
            fg=(0.7, 0.7, 0.7, 1), align=TextNode.ACenter
        )

        menu_button = DirectButton(
            text="RECOMEÇAR",
            scale=0.09,
            pos=(0, 0, -0.15),
            text_fg=(1, 1, 1, 1),
            frameColor=(
                (0.3, 0.3, 0.3, 1),
                (0.15, 0.15, 0.15, 1),
                (0.45, 0.45, 0.45, 1),
                (0.2, 0.2, 0.2, 1)
            ),
            relief=1,
            command=on_restart
        )

        self.game_over_elements.extend([panel, go_text, go_text2, menu_button])

    def clear_game_over(self):
        for element in self.game_over_elements:
            element.destroy()
        self.game_over_elements.clear()

    # =========================================================
    # COMUM
    # =========================================================
    def release_mouse(self):
        """Faz o cursor do mouse reaparecer e se mover livremente pelas telas de UI."""
        props = WindowProperties()
        props.setCursorHidden(False)
        props.setMouseMode(WindowProperties.M_relative)
        self.app.win.requestProperties(props)
        
    def create_pause_screen(self, on_resume, on_quit):
        self.release_mouse()

        panel = DirectFrame(
            frameColor=(0.05, 0.05, 0.08, 0.85),
            frameSize=(-0.6, 0.6, -0.5, 0.5),
            pos=(0, 0, 0)
        )

        title = OnscreenText(
            text="PAUSADO",
            pos=(0, 0.3), scale=0.15,
            fg=(0.95, 0.85, 0.2, 1),
            shadow=(0, 0, 0, 1), shadowOffset=(0.01, 0.01),
            align=TextNode.ACenter
        )

        resume_button = DirectButton(
            text="CONTINUAR",
            scale=0.09,
            pos=(0, 0, 0.0),
            text_fg=(1, 1, 1, 1),
            frameColor=(
                (0.6, 0.1, 0.1, 1),
                (0.4, 0.05, 0.05, 1),
                (0.75, 0.15, 0.15, 1),
                (0.3, 0.3, 0.3, 1)
            ),
            relief=1,
            command=on_resume
        )

        quit_button = DirectButton(
            text="SAIR PARA O MENU",
            scale=0.07,
            pos=(0, 0, -0.25),
            text_fg=(1, 1, 1, 1),
            frameColor=(
                (0.3, 0.3, 0.3, 1),
                (0.15, 0.15, 0.15, 1),
                (0.45, 0.45, 0.45, 1),
                (0.2, 0.2, 0.2, 1)
            ),
            relief=1,
            command=on_quit
        )

        self.pause_elements = [panel, title, resume_button, quit_button]

    def clear_pause(self):
        if hasattr(self, "pause_elements"):
            for element in self.pause_elements:
                element.destroy()
            self.pause_elements = []