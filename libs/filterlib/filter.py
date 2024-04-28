from .yololib import YoloDecLib
from libs.utilslib import getDictV
from time import time
from cv2.typing import MatLike
from cv2 import putText, FONT_HERSHEY_SIMPLEX


class FilterLib:
    def __init__(self, yoloConfig: dict | None = None) -> None:
        self._yoloModel: YoloDecLib | None = self.setYoloConfig(yoloConfig)
        self._lastUpdateTime: float = time()

    @property
    def yoloModel(self) -> YoloDecLib | None:
        return self._yoloModel

    def setYoloConfig(self, yoloConfig: dict | None) -> YoloDecLib | None:
        if yoloConfig is None:
            return None

        conf: float = getDictV(yoloConfig, "conf", 0.7)
        persist: bool = getDictV(yoloConfig, "persist", False)
        classes: list = getDictV(yoloConfig, "classes", [0])

        self._yoloModel = YoloDecLib(
            modelPath=yoloConfig["model"],
            yoloTracker=str(yoloConfig["tracker"]),
            persist=persist,
            conf=conf,
            classes=classes,
        )

        return self._yoloModel

    def yoloUpdate(self, frame: MatLike) -> MatLike:
        if self._yoloModel is None:
            raise ValueError(f"Yolo model not set, receive {type(self._yoloModel)}")
        return self._yoloModel.update(frame)

    def trailBalls(self, frame: MatLike) -> MatLike:
        if self._yoloModel is None:
            raise ValueError(f"Yolo model not set, receive {type(self._yoloModel)}")
        return self._yoloModel.trailBalls(frame)

    def stopBoxes(self, frame: MatLike) -> MatLike:
        if self._yoloModel is None:
            raise ValueError(f"Yolo model not set, receive {type(self._yoloModel)}")
        return self._yoloModel.stopBoxes(frame)

    def displayFPS(self, frame: MatLike) -> MatLike:
        oldTime: float = self._lastUpdateTime
        self._lastUpdateTime = time()
        fps = 1 / (self._lastUpdateTime - oldTime)
        text = f"FPS: {fps:.2f}"
        color = (0, 0, 255)
        position = (frame.shape[1] - 10 - len(text) * 20, frame.shape[0] - 10)
        putText(frame, text, position, FONT_HERSHEY_SIMPLEX, 1, color, 2)
        return frame
