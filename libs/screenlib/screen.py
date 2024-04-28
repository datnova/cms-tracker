from cv2.typing import MatLike
from cv2 import VideoWriter, VideoCapture, cvtColor, imshow, resize, COLOR_BGR2RGB
from typing import Callable
from PySide6.QtGui import QImage
from numpy import empty
from typing import Optional
from time import time
import pafy


class Screen:
    def __init__(
        self,
        source: str,
        name: str,
        scale: float = 1.0,
        output: str = "",
        fourcc: str = "XVID",
        fps: int = 24,
    ):
        self._filterFuncs: list = list()
        self._name: str = name
        self._output: str = output

        if "youtu" in source:
            video = pafy.new(source)
            best = video.getbest(preftype="mp4")
            if best is None:
                raise ValueError(f"Video source {source} not found")
            source = best.url

        self._captureSource: VideoCapture = VideoCapture(source)
        self._scale: float = scale
        self._resolution: tuple[int, int] = (
            int(self._captureSource.get(3) * self._scale),
            int(self._captureSource.get(4) * self._scale),
        )
        self._lastTimeUpdate: float = time()
        self._originScreenBuffer: MatLike = empty(self._resolution)
        self._filterScreenBuffer: MatLike = empty(self._resolution)
        self._fourcc: int = VideoWriter.fourcc(*fourcc)
        self._recordFPS: int = fps
        self._outSource: Optional[VideoWriter] = (
            VideoWriter(output, self._fourcc, self._recordFPS, self._resolution)
            if self._output
            else None
        )

    @property
    def originScreenBuffer(self) -> MatLike:
        return self._originScreenBuffer

    @property
    def name(self) -> str:
        return self._name

    @property
    def scale(self) -> float:
        return self._scale

    @property
    def filterScreenBuffer(self) -> MatLike:
        return self._filterScreenBuffer

    @scale.setter
    def scale(self, value: float):
        if not isinstance(value, float):
            raise TypeError("Scale must be a float")
        if value <= 0.0:
            raise ValueError("Scale must be positive")
        if self._outSource is not None:
            newRes = (
                int(self._resolution[0] * self._scale),
                int(self._resolution[1] * self._scale),
            )
            self._resolution = newRes
            self.setupOutSource(self._output, self._fourcc, self._recordFPS)
        self._scale = value

    @filterScreenBuffer.setter
    def filterScreenBuffer(self, value: MatLike):
        self._filterScreenBuffer = value

    def setupOutSource(
        self, output: str | None, fourcc: str | int = "XVID", fps: int = 24
    ) -> None:
        if not output:
            return

        self._fourcc: int = (
            VideoWriter.fourcc(*fourcc) if isinstance(fourcc, str) else fourcc
        )
        self._recordFPS: int = fps
        self._output: str = output

        self._outSource: Optional[VideoWriter] = VideoWriter(
            self._output, self._fourcc, self._recordFPS, self._resolution
        )

    def update(self) -> bool:
        ret = self.getNextFrame()
        if self._outSource is not None:
            self._outSource.write(self._originScreenBuffer)
        self.applyFilter()
        return ret

    def run(self, windowName: str, display: bool = False, origin: bool = False):
        self.update()
        self.displayScreen(windowName, origin) if display else None

    def displayScreen(self, windowName: str, origin: bool):
        frame = self._originScreenBuffer if origin else self._filterScreenBuffer
        imshow(windowName, frame)

    def getNextFrame(self) -> bool:
        ret, self._originScreenBuffer = self._captureSource.read()
        if not ret:
            return ret
        self._originScreenBuffer = resize(self._originScreenBuffer, self._resolution)
        self._filterScreenBuffer = self._originScreenBuffer
        return ret

    def getQImage(self, origin: bool = True) -> QImage:
        image = self._originScreenBuffer if origin else self._filterScreenBuffer
        image = cvtColor(image, COLOR_BGR2RGB)
        h, w, ch = image.shape
        img = QImage(image.data, w, h, ch * w, QImage.Format.Format_RGB888)
        return img

    def addFilter(self, filter: Callable, **kwargs):
        self._filterFuncs.append((filter, kwargs))

    def applyFilter(self):
        for func, params in self._filterFuncs:
            self.filterScreenBuffer = func(self.filterScreenBuffer, **params)

    def close(self):
        if self._outSource:
            self._outSource.release()
        self._captureSource.release()
