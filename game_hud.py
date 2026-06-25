from panda3d.core import TextNode, CardMaker, TransparencyAttrib

class GameHUD:
    def __init__(self, app):
        self.app = app
        
        # Create UI elements
        self.create_status_text()
        

    def create_status_text(self):
        # Load a font (or use Panda3D's default)
        font = self.app.loader.loadFont("cmss12.egg") 
        
        # 1. Setup Ammo Text Node
        self.enemies_node = TextNode("enemies_text")
        self.enemies_node.setFont(font)
        self.enemies_node.setTextColor(1, 0, 0, 1)
        self.enemies_node.setText("Inimigos: 10")
        
        # Attach and position it (Bottom Left)
        # aspect2d coordinates: Left is roughly -1.3 to -1.7 (depending on aspect ratio), Right is positive, Bottom is -1, Top is 1
        self.enemies_np = aspect2d.attachNewNode(self.enemies_node)
        self.enemies_np.setScale(0.07) # Scale text down to standard size
        self.enemies_np.setPos(-1.3, 0, 0.9) 
        
    def hide(self):
        self.enemies_np.hide()
    def show(self):
        self.enemies_np.show()
    def update_enemies(self, current, max_enemies):
        self.enemies_node.setText(f"Inimigos: {current}/{max_enemies}")
