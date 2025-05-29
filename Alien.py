import time
from MiniGameEngine import GameObject
from Explosion import Explosion

class Alien(GameObject):
    def __init__(self, x, y, manager, speed=20, image_path="Recursos/Alien.png"):
        super().__init__(x, y, image_path, "Alien")
        #AlienManager controla el movimiento individual
        self.manager = manager
        # self.direction y self.last_move ahora son controlados por AlienManager

    def onUpdate(self, dt):
        # El movimiento es manejado por AlienManager.
        # La comprobación de si un alien ha llegado abajo la hace AlienManager.
        pass 

    def onCollision(self, dt, gobj):
        if gobj.getTipo() == "Bullet":
            Explosion(self.getX(), self.getY())
            
            if hasattr(self._gw, 'increment_score'):
                self._gw.increment_score(10) 
            
            self.manager.removeAlien(self) 
            self.destroy()