from typing import DefaultDict
from itertools import pairwise
from math import sqrt
from random import sample
from time import time

from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator

from cv2.typing import MatLike
from cv2 import polylines

from numpy import hstack, int32


class YoloDecLib:
    def __init__(
        self,
        modelPath,
        yoloTracker: str = "bytetrack.yaml",
        persist: bool = False,
        conf: float = 0.7,
        classes: list = [],
        maxBallTrack: int = 30,
        ballThickness: int = 5,
    ) -> None:
        self._centerPoints: dict = DefaultDict(lambda: [list(), 0, False])
        self._currentBoxes: list = list()
        self._currentIDs: list = list()
        self._maxBallTrack: int = maxBallTrack
        self._ballThickness: int = ballThickness
        self._sampleRate: float = 0.2

        self._stopTimeThreshold: int = 10
        self._triggerColor: list = [56, 26, 211]
        self._neutralColor: list = [128, 128, 128]

        self._modelPath: str = modelPath
        self._yoloTracker: str = yoloTracker
        self._model: YOLO = YOLO(self._modelPath)
        self._persist: bool = persist
        self._conf: float = conf
        self._classes: list = classes

    @property
    def triggerColor(self) -> list:
        return self._triggerColor

    @property
    def neutralColor(self) -> list:
        return self._neutralColor

    @property
    def stopTimeThreshold(self) -> int:
        return self._stopTimeThreshold

    @property
    def ballThickness(self) -> int:
        return self._ballThickness

    @property
    def maxBallTrack(self) -> int:
        return self._maxBallTrack

    @triggerColor.setter
    def triggerColor(self, value: list) -> None:
        if len(value) != 3:
            raise ValueError("Color must have 3 elements BGR")
        self._triggerColor = value

    @neutralColor.setter
    def neutralColor(self, value: list) -> None:
        if len(value) != 3:
            raise ValueError("Color must have 3 elements BGR")
        self._neutralColor = value

    @neutralColor.setter
    def neutralColor(self, value: list) -> None:
        self._neutralColor = value

    @stopTimeThreshold.setter
    def stopTimeThreshold(self, value: int) -> None:
        if value <= 0:
            raise ValueError("stopTime must be greater than 0")
        self._stopTimeThreshold = value

    @ballThickness.setter
    def ballThickness(self, value: int) -> None:
        if value <= 0:
            raise ValueError("ballThickness must be greater than 0")
        self._ballThickness = value

    @maxBallTrack.setter
    def maxBallTrack(self, value: int) -> None:
        if value <= 0:
            raise ValueError("maxBallTrack must be greater than 0")
        self._maxBallTrack = value

    def _overlapSample(self, container: list, threshole: float) -> bool:
        for x, y in pairwise(container):
            if sqrt((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2) > threshole:
                return False
        return True

    def _randomSample(self, lst: list) -> list:
        sampleSize = max(round(len(lst) * self._sampleRate), 2)
        return sample(lst, sampleSize)

    def _secToTimeString(self, timeSec: int) -> str:
        hours = timeSec // 3600  # Integer division to get the number of hours
        minutes = timeSec % 3600 // 60  # Modulo operation to get the remaining minutes
        seconds = timeSec % 60  # Modulo operation to get the remaining seconds

        if hours == 0:
            return f"{minutes:02d}:{seconds:02d}"

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _appendTrackBalls(self, track: list, box: list) -> None:
        cx = box[0] + (box[2] - box[0]) / 2
        cy = box[1] + (box[3] - box[1]) / 2
        track.append((cx, cy))
        track.pop(0) if len(track) > self._maxBallTrack else None

    def update(self, frame: MatLike) -> MatLike:
        results = self._model.track(
            source=frame,
            persist=self._persist,
            tracker=self._yoloTracker,
            verbose=False,
            conf=self._conf,
            classes=self._classes,
        )

        try:
            self._currentBoxes = results[0].boxes.xyxy.cpu()
            self._currentIDs = results[0].boxes.id.int().cpu().tolist()

            for box, id in zip(self._currentBoxes, self._currentIDs):
                track = self._centerPoints[id][0]
                timestamp = self._centerPoints[id][1]

                # update center point
                self._appendTrackBalls(track, box)

                # set up tracking points for detect stop vehicles
                if timestamp != 0:
                    sample = self._randomSample(track)
                    overlap = self._overlapSample(sample, self._ballThickness)
                    self._centerPoints[id][2] = overlap

                    if not overlap:
                        self._centerPoints[id][1] = time()
                else:
                    self._centerPoints[id][1] = time()

        except AttributeError:
            print("Dont detect any object in frame, skip.")
            self._currentBoxes = list()
            self._currentIDs = list()

        return frame

    def trailBalls(self, frame: MatLike) -> MatLike:
        for id in self._currentIDs:
            # Draw the tracking lines
            points = hstack(self._centerPoints[id][0]).astype(int32).reshape((-1, 1, 2))
            polylines(
                frame,
                [points],
                isClosed=False,
                color=(
                    (100 + hash(id * 2) % 150),
                    (100 + hash(id * 4) % 150),
                    (100 + hash(id * 6) % 150),
                ),
                thickness=self._ballThickness,
            )
        return frame

    def stopBoxes(self, frame: MatLike) -> MatLike:
        annotator = Annotator(frame)

        for box, id in zip(self._currentBoxes, self._currentIDs):
            if self._centerPoints[id][2]:
                beginStopTime = self._centerPoints[id][1]
                currentTime = time()
                duration = int(currentTime - beginStopTime)
                ti = self._secToTimeString(duration)

                if duration < self._stopTimeThreshold:
                    annotator.box_label(box, f"[{id}] {ti}")
                else:
                    annotator.box_label(box, f"[{id}] {ti}", color=(56, 26, 211))

        return annotator.result()
