import time
import ctypes
import tkinter as tk

try:
    TIME_BEGIN_PERIOD = ctypes.windll.winmm.timeBeginPeriod
    TIME_END_PERIOD = ctypes.windll.winmm.timeEndPeriod
except:
    TIME_BEGIN_PERIOD = lambda n: True
    TIME_END_PERIOD = lambda n: True


class GameWorld:
    __instance__ = None

    def _getInstance():
        return GameWorld.__instance__

    # ---
    def __init__(
        self,
        width: int,
        height: int,
        title: str = "MiniGameEngine",
        bgcolor: str = "gray",
        bgpic: str = None,
    ):
        """Constructor de la clase GameWorld que inicializa una instancia del mundo de juego.

        Args:
            width (int): Ancho de la ventana del juego.
            height (int): Altura de la ventana del juego.
            title (str, optional): Título de la ventana del juego (opcional, por defecto es "MiniGameEngine").
            bgcolor (str, optional): Color de fondo de la ventana del juego (opcional, por defecto es "gray").
            bgpic (str, optional): Ruta de la imagen de fondo de la ventana del juego (opcional, por defecto es None).

        Raises:
            Exception: Solo puede haber una instancia del jeugo en ejecucion
        """
        if not GameWorld.__instance__ is None:
            raise Exception("Ya existe una instancia de GameWorld activa!!!")

        self._win = tk.Tk()
        self._win.geometry("%dx%d" % (width, height))
        self._win.title(title)

        self._canvas = tk.Canvas(self._win, width=width, height=height, bg=bgcolor)
        self._canvas.place(x=0, y=0)

        if not bgpic is None:
            self._bgpic = tk.PhotoImage(file=bgpic)
            self._canvas.create_image(0, 0, image=self._bgpic, anchor="nw")

        self._keys = {}
        self._tick_prev = 0
        self._fps = 0
        self._gObjects = []
        self._running = False
        GameWorld.__instance__ = self

    def _getCanvas(self) -> tk.Canvas:
        return self._canvas

    # ---
    def gameLoop(self, fps: int):
        """
        Inicia el loop principal del juego.

        Args:
            fps (int): Fotogramas por segundo del juego.
        """
        self._fps = fps
        self._fps_time = 1 / self._fps
        self._tick_prev = time.perf_counter()

        self._running = True
        self._win.protocol("WM_DELETE_WINDOW", self.exitGame)
        while self._running:
            self._doAddGameObjects()
            dt = self._doRefresh()
            self.onUpdate(dt)
            self._doUpdateGameObjects(dt)
            self._doCollisions(dt)
            self._doDelGameObjects()
        self._win.destroy()

    def exitGame(self):
        """
        Finaliza el loop principal del juego
        """
        self._running = False

    def onUpdate(self, dt: float):
        """
        Llamada por cada ciclo dentro del loop (1/fps veces por segundo)

        Args:
            dt (float): Tiempo en segundos desde la ultima llamada
        """
        pass

    def _addGObject(self, gobj):
        if not hasattr(gobj, "__status__"):
            gobj.__status__ = "new"
            self._gObjects.append(gobj)

    def _doAddGameObjects(self):
        for o in self._gObjects:
            if o.__status__ == "new":
                o.__status__ = "alive"

    def _delGObject(self, gobj):
        if hasattr(gobj, "__status__"):
            gobj.__status__ = "dead"

    def _doDelGameObjects(self):
        gobjs = [o for o in self._gObjects if o.__status__ == "dead"]
        for o in gobjs:
            self._gObjects.remove(o)

    def _doUpdateGameObjects(self, dt):
        for o in self._gObjects:
            if o.__status__ == "alive":
                o.onUpdate(dt)

    def _doCollisions(self, dt):
        gobjs1 = [o for o in self._gObjects if o.__status__ == "alive"]
        gobjs2 = gobjs1.copy()
        for o1 in gobjs1:
            gobjs2.pop(0)
            if o1.__status__ != "alive":
                continue
            for o2 in gobjs2:
                if o2.__status__ != "alive":
                    continue
                if self._collides(o1, o2):
                    o1.onCollision(dt, o2)
                    o2.onCollision(dt, o1)

    def _doRefresh(self):
        self._win.update_idletasks()
        self._win.update()

        # usaremos 1ms de precision debido a Windows
        dt = self._fps_time - (time.perf_counter() - self._tick_prev) - 0.001
        dr = round(dt, 3)
        if dt > 0:
            TIME_BEGIN_PERIOD(1)
            time.sleep(dt)
            TIME_END_PERIOD(1)

        now = time.perf_counter()
        dt = now - self._tick_prev
        self._tick_prev = now

        return dt

    def _collides(self, o1, o2):
        if o1 == o2:
            return False
        if o1.__status__ != "alive" or o2.__status__ != "alive":
            return False

        o1x1 = o1.getX() - o1.getWidth() / 2
        o1y1 = o1.getY() - o1.getHeight() / 2
        o1x2 = o1x1 + o1.getWidth() - 1
        o1y2 = o1y1 + o1.getHeight() - 1

        o2x1 = o2.getX() - o2.getWidth() / 2
        o2y1 = o2.getY() - o2.getHeight() / 2
        o2x2 = o2x1 + o2.getWidth() - 1
        o2y2 = o2y1 + o2.getHeight() - 1

        return o1x1 <= o2x2 and o2x1 <= o1x2 and o1y1 <= o2y2 and o2y1 <= o1y2

    # ---
    def isPressed(self, key_name: str) -> bool:
        """
        Verifica si una tecla específica está presionada.

        Args:
            key_name (str): Nombre de la tecla a verificar.

        Returns:
            bool: True si la tecla está presionada, False en caso contrario.
        """
        if not key_name in self._keys:
            self._keys[key_name] = False
            self._win.bind(
                "<KeyPress-%s>" % key_name, lambda e: self._setPressed(key_name, True)
            )
            self._win.bind(
                "<KeyRelease-%s>" % key_name,
                lambda e: self._setPressed(key_name, False),
            )
        return self._keys[key_name]

    def _setPressed(self, key_name: str, pressed: bool):
        self._keys[key_name] = pressed

    # --
    def getWorldWidth(self) -> int:
        """
        Obtiene el ancho del mundo de juego.

        Returns:
            int: Ancho del mundo de juego.
        """
        return self._win.winfo_width()

    def getWorldHeight(self) -> int:
        """
        Obtiene la altura del mundo de juego.

        Returns:
            int: Altura del mundo de juego.
        """
        return self._win.winfo_height()


# ---


class GameObject:
    _images = {}

    def _getImage(imagePath: str) -> tk.PhotoImage:
        if not imagePath in GameObject._images:
            GameObject._images[imagePath] = tk.PhotoImage(file=imagePath)
        return GameObject._images[imagePath]

    def __init__(self, x: int, y: int, imagePath: str, tipo: str = "undef"):
        """
        Constructor de la clase GameObject que inicializa un objeto en el mundo de juego.

        Args:
            x (int): Coordenada x inicial del objeto.
            y (int): Coordenada y inicial del objeto.
            imagePath (str): Ruta de la imagen del objeto.
            tipo (str, optional): Tipo del objeto (opcional, por defecto es "undef").
        """
        self._gw = GameWorld._getInstance()
        if self._gw is None:
            raise ("No existe una instancia de GameWorld activa!!!")

        self._x = x
        self._y = y
        img = GameObject._getImage(imagePath)
        self._width = img.width()
        self._height = img.height()
        self._shape = self._gw._getCanvas().create_image(
            self._x - self._width / 2,
            self._y - self._height / 2,
            image=img,
            anchor="nw",
        )
        self._tipo = tipo
        self._gw._addGObject(self)

    def getX(self) -> int:
        """
        Obtiene la coordenada x actual del objeto.

        Returns:
            int: Coordenada x del objeto.
        """
        return self._x

    def getY(self) -> int:
        """
        Obtiene la coordenada y actual del objeto.

        Returns:
            int: Coordenada y del objeto.
        """
        return self._y

    def setPosition(self, x: int, y: int):
        """
        Establece la posición del objeto en el mundo de juego.

        Args:
            x (int): Nueva coordenada x del objeto.
            y (int): Nueva coordenada y del objeto.
        """
        self._x, self._y = int(x), int(y)
        self._gw._getCanvas().moveto(
            self._shape, self._x - self._width / 2, self._y - self._height / 2
        )

    def setShape(self, imagePath: str):
        """
        Cambia la forma del objeto reemplazando su imagen.

        Args:
            imagePath (str): Ruta de la nueva imagen del objeto.
        """
        img = GameObject._getImage(imagePath)
        self._width = img.width()
        self._height = img.height()
        self._gw._getCanvas().itemconfig(self._shape, image=img)
        self.setPosition(self._x, self._y)

    def getWidth(self) -> int:
        """
        Obtiene el ancho del objeto.

        Returns:
            int: Ancho del objeto.
        """
        return self._width

    def getHeight(self) -> int:
        """
        Obtiene la altura del objeto.

        Returns:
            int: Altura del objeto.
        """
        return self._height

    def getTipo(self) -> str:
        """
        Obtiene el tipo del objeto.

        Returns:
            str: Tipo del objeto.
        """
        return self._tipo

    def destroy(self):
        """
        Elimina el objeto del mundo de juego.
        """
        self._gw._getCanvas().delete(self._shape)
        self._gw._delGObject(self)

    def getWorldWidth(self) -> int:
        """
        Obtiene el ancho del mundo de juego.

        Returns:
            int: Ancho del mundo de juego.
        """
        return self._gw.getWorldWidth()

    def getWorldHeight(self) -> int:
        """
        Obtiene la altura del mundo de juego.

        Returns:
            int: Altura del mundo de juego.
        """
        return self._gw.getWorldHeight()

    def isPressed(self, key_name: str) -> bool:
        """
        Verifica si una tecla específica está presionada.

        Args:
            key_name (str): Nombre de la tecla a verificar.

        Returns:
            bool: True si la tecla está presionada, False en caso contrario.
        """
        return self._gw.isPressed(key_name)

    def onUpdate(self, dt: float):
        """
        Llamado en cada actualización del juego para el objeto.

        Args:
            dt (float): Tiempo en segundos desde la ultima llamada.
        """
        pass

    def onCollision(self, dt: float, gobj):
        """
        Llamado cuando el objeto colisiona con otro objeto.

        Args:
            dt (float): Tiempo en segundos desde la ultima llamada.
            gobj (GameObject): Objeto con el que colisiona.
        """
        pass
