from panda3d.core import TextNode, CardMaker, TransparencyAttrib

class GameHUD:
    def __init__(self, app):
        self.app = app
        
        self.create_status_text()
        

    def create_status_text(self):
        font = self.app.loader.loadFont("cmss12.egg") 
        
        self.enemies_node = TextNode("enemies_text")
        self.enemies_node.setFont(font)
        self.enemies_node.setTextColor(1, 0, 0, 1)
        self.enemies_node.setText("Inimigos: 10")
        
        self.enemies_np = aspect2d.attachNewNode(self.enemies_node)
        self.enemies_np.setScale(0.07) 
        self.enemies_np.setPos(-1.3, 0, 0.9) 
        
    def hide(self):
        self.enemies_np.hide()
    def show(self):
        self.enemies_np.show()
    def update_enemies(self, current, max_enemies):
        self.enemies_node.setText(f"Inimigos: {current}/{max_enemies}")
