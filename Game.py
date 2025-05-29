import time # Necesario para el reinicio si hay elementos con temporizadores
from MiniGameEngine import GameWorld
from SpaceShip import SpaceShip
from AlienManager import AlienManager
from Bullet import Bullet # Necesario para limpiar las balas al reiniciar

class Game(GameWorld):
    def __init__(self):
        super().__init__(800, 600, title="Defensa Galáctica", bgpic="Recursos/Fondo.png")
        self.level = 1
        self.max_level = 3
    
        self.score = 0

        self.score_text_id = self._canvas.create_text(
            10, 10, text=f"Puntuación: {self.score}",
            fill="white", font=("Arial", 16), anchor="nw"
        )
        self.level_text_id = self._canvas.create_text(
        700, 10, text=f"Nivel: {self.level}",
        fill="white", font=("Arial", 16), anchor="ne"
        )
        self.message_text_id = None
        self.sub_message_text_id = None

        self.game_state = "initializing"  #  Estado temporal para bloquear la lógica

        self.init_game_elements()         #  Inicializa aliens, nave, etc.

        self.game_state = "playing"       #  Solo después de todo completamente listo

        




    def init_game_elements(self):
        """Inicializa o reinicializa los elementos del juego."""
        # Limpiar elementos antiguos si existieran (para reinicio)
        if hasattr(self, 'space_ship') and self.space_ship:
            self.space_ship.destroy()
        if hasattr(self, 'alien_manager') and self.alien_manager:
            for alien in list(self.alien_manager.aliens): # Usar una copia de la lista para iterar y modificar
                alien.destroy() # Esto debería eliminarlo de _gObjects
            self.alien_manager.aliens.clear()

        # Destruir balas existentes
        for gobj in list(self._gObjects): # Usar una copia de la lista
            if isinstance(gobj, Bullet): # O gobj.getTipo() == "Bullet"
                gobj.destroy()
        
        self.space_ship = SpaceShip(400, 540)
        #self.alien_manager = AlienManager(self) # Pasamos la instancia del juego
        self.alien_manager = AlienManager(self, speed=10 + self.level * 3)  # Aumenta velocidad con el nivel
        
        # Agregamos filas de alienígenas
        for y in range(50, 200, 40):
            for x in range(100, 700, 60):
                self.alien_manager.addAlien(x, y)
        
        # Asegurar que el score display se actualice si es un reinicio
        self.score = 0
        self._canvas.itemconfig(self.score_text_id, text=f"Puntuación: {self.score}")
        self._canvas.itemconfig(self.level_text_id, text=f"Nivel: {self.level}")

    def increment_score(self, points):
        if self.game_state == "playing": # Solo sumar puntos si se está jugando
            self.score += points
            self._canvas.itemconfig(self.score_text_id, text=f"Puntuación: {self.score}")

    def show_message(self, main_text, sub_text):
        """Muestra un mensaje en el centro de la pantalla."""
        self.clear_messages() # Limpia mensajes anteriores

        canvas_width = self.getWorldWidth()
        canvas_height = self.getWorldHeight()

        self.message_text_id = self._canvas.create_text(
            canvas_width / 2, canvas_height / 2 - 30,
            text=main_text, fill="yellow", font=("Arial", 32, "bold"), anchor="center"
        )
        self.sub_message_text_id = self._canvas.create_text(
            canvas_width / 2, canvas_height / 2 + 20,
            text=sub_text, fill="white", font=("Arial", 18), anchor="center"
        )

    def clear_messages(self):
        """Limpia los mensajes de la pantalla."""
        if self.message_text_id:
            self._canvas.delete(self.message_text_id)
            self.message_text_id = None
        if self.sub_message_text_id:
            self._canvas.delete(self.sub_message_text_id)
            self.sub_message_text_id = None
            
    def trigger_game_over(self):
        if self.game_state == "playing":
            self.game_state = "game_over"
            self.show_message("¡GAME OVER!", "Presiona R para reiniciar, ESC para salir")

    def trigger_win(self):
        if self.game_state == "playing":
            self.game_state = "win"
            self.show_message("¡GANASTE!", "")

    def restart_game(self):
        self.clear_messages()
        self.level = 1
        self.init_game_elements() # Reinicializa nave, aliens, etc.
        self.game_state = "playing"

    def onUpdate(self, dt):
        if self.game_state == "playing":
            # Actualizamos el movimiento de los alienígenas
            self.alien_manager.updateAliens(dt)
            
            # La nave y sus disparos se actualizan a través de _doUpdateGameObjects en GameWorld
            # No es necesario llamarlos explícitamente aquí si están en self._gObjects

            # Verificamos si todos los alienígenas han sido destruidos
            if self.alien_manager.allAliensDestroyed():
                if self.level < self.max_level:
                    self.level += 1
                    self.clear_messages()
                    self.init_game_elements()
                else:
                    self.trigger_final_win()


            # Salir si se presiona la tecla 'Escape' (solo si se está jugando activamente)
            if self.isPressed("Escape"):
                self.exitGame()

        elif self.game_state == "game_over" or self.game_state == "win":
            # En estado de fin de juego, solo procesamos teclas para reiniciar o salir
            if self.isPressed("r"): # 'r' para reiniciar
                self.restart_game()
            if self.isPressed("Escape"): # 'Escape' para salir
                self.exitGame()

    def trigger_final_win(self):
        self.game_state = "win"
        self.show_message("¡TODOS LOS NIVELES COMPLETOS!", "Presiona R para jugar de nuevo o ESC para salir")

# -- show time
game = Game()
game.gameLoop(60)