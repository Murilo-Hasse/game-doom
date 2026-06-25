class InputHandler:
    def __init__(self,app):
        self.app = app
        self.keyMap = {
            "up" : False,
            "down" : False,
            "left" : False,
            "right" : False,
            "shoot" : False,
            "jump" : False,
            "debug": False
        }
        app.accept("w", self.updateKeyMap, ["up", True])
        app.accept("w-up", self.updateKeyMap, ["up", False])
        app.accept("s", self.updateKeyMap, ["down", True])
        app.accept("s-up", self.updateKeyMap, ["down", False])
        app.accept("a", self.updateKeyMap, ["left", True])
        app.accept("a-up", self.updateKeyMap, ["left", False])
        app.accept("d", self.updateKeyMap, ["right", True])
        app.accept("d-up", self.updateKeyMap, ["right", False])
        app.accept("mouse1", self.updateKeyMap, ["shoot", True])
        app.accept("mouse1-up", self.updateKeyMap, ["shoot", False])
        app.accept("space", self.updateKeyMap, ["jump", True])
        app.accept("space-up", self.updateKeyMap, ["jump", False])
        app.accept("f3", self.updateKeyMap, ["debug", True])
        app.accept("f3-up", self.updateKeyMap, ["debug", False])


    def updateKeyMap(self, controlName, controlState):
        self.keyMap[controlName] = controlState
    