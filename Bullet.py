from MiniGameEngine import GameObject


class Bullet(GameObject):
    # inicializamos la Bala
    def __init__(self, x, y):
        super().__init__(x, y, "Recursos/Bullet.png", "Bullet")

    # actualizamos el estado de la Bala en cada frame
    def onUpdate(self, dt):
        x = self.getX()
        y = self.getY()

        y = y - 8
        if y < 0:
            self.destroy()
        else:
            self.setPosition(x, y)

    # manejamos las colisiones
    def onCollision(self, dt, gobj):
        self.destroy()
