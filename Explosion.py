import time
from MiniGameEngine import GameObject

class Explosion(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, "Recursos/Explosion.png", "Explosion")
        self.created_at = time.time()

    def onUpdate(self, dt):
        if time.time() - self.created_at >= 3:
            self.destroy()
