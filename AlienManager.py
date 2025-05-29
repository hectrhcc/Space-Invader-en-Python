import time
from Alien import Alien

class AlienManager:
    def __init__(self, game_instance,speed=10):
        self.aliens = []
        self.direction = 1
        self.last_move_time = time.time()
        self.move_interval = 0.5 
        self.speed = 10
        self.descend_amount = 20
        self.game = game_instance 
        self.speed = speed
        # Asumimos que la nave está en la parte inferior, calculamos una línea de colisión.
        # Podrías obtener la altura de la nave del jugador desde self.game.space_ship.getHeight() si es necesario.
        #self.player_zone_y = self.game.getWorldHeight() - 100 # Ejemplo de zona de invasión

    def addAlien(self, x, y):
        alien = Alien(x, y, manager=self)
        self.aliens.append(alien)

    def updateAliens(self, dt):
        if self.game.game_state != "playing": # No mover aliens si el juego no está activo
            return

        if not self.aliens:
            return

        # Obtener el ancho del mundo desde el primer alien (o desde self.game)
        # Es mejor obtenerlo de self.game si es posible para evitar errores si no hay aliens.
        current_world_width = self.game.getWorldWidth()

        if time.time() - self.last_move_time > self.move_interval:
            move_down = False
            
            for alien in self.aliens:
                if self.direction == 1 and alien.getX() + alien.getWidth() / 2 + self.speed > current_world_width:
                    move_down = True
                    self.direction = -1
                    break 
                elif self.direction == -1 and alien.getX() - alien.getWidth() / 2 - self.speed < 0:
                    move_down = True
                    self.direction = 1
                    break 
            
           

            for alien in self.aliens:
                current_x = alien.getX()
                current_y = alien.getY()
                new_y = current_y
                new_x = current_x

                if move_down:
                    new_y += self.descend_amount
                else:
                    new_x += self.direction * self.speed
                
                alien.setPosition(new_x, new_y)
                
                # Verificar si un alien ha llegado a la zona del jugador
                player_zone_y = self.game.getWorldHeight() - 80
                if new_y + alien.getHeight() / 2 >= player_zone_y:
                    print(f"Alien alcanzó zona segura: y={new_y + alien.getHeight() / 2}, límite={player_zone_y}")
                    self.game.trigger_game_over()
                    return
                    print(f"Alien alcanzó zona segura: y={new_y + alien.getHeight() / 2}, límite={self.player_zone_y}")
                    self.game.trigger_game_over() # Llama al método en Game.py
                    return # Salir para evitar más procesamiento este frame

            self.last_move_time = time.time()

    def removeAlien(self, alien):
        if alien in self.aliens:
            self.aliens.remove(alien)

    def allAliensDestroyed(self):
        return len(self.aliens) == 0