from libs.filterlib.filter import FilterLib
from libs.screenlib.screen import Screen
from cv2 import destroyAllWindows, waitKey
from libs.utilslib import getDictV
import threading

class App:
    screens: list[Screen] = list()
    configData: dict = dict()

    def __init__(self, configData: dict):
        self.configData = configData
        self.setupScreens()
        self._running = False

        self.capture_thread = threading.Thread(target=self.captureThread)
        self.display_thread = threading.Thread(target=self.displayThread)

    def setupScreens(self):
        for k, v in self.configData["screens"].items():
            scale: float = getDictV(v, "scale", default=1.0)
            screen: Screen = Screen(v["source"], k, scale=scale)

            self.setupRecord(screen, v)
            self.setupFilter(screen, v.get("filter", dict()))

            self.screens.append(screen)

    def setupFilter(self, screen: Screen, v: dict) -> None:
        yoloConfig = self.configData.get("yolo")
        filterLib = FilterLib(yoloConfig)

        if filterLib.yoloModel is not None:
            screen.addFilter(filterLib.yoloModel.update)

        v = {
            key: val for key, val in sorted(v.items(), key=lambda ele: ele[1]["index"])
        }

        for key, params in v.items():
            func = None

            if key == "trailBalls":
                func = filterLib.trailBalls

                if filterLib.yoloModel is None:
                    continue

                maxBalls: int = getDictV(params, "maxBalls", default=30)
                filterLib.yoloModel.maxBallTrack = maxBalls

                ballThickness: int = getDictV(params, "ballThickness", default=5)
                filterLib.yoloModel.ballThickness = ballThickness

            elif key == "stopBoxes":
                func = filterLib.stopBoxes

                if filterLib.yoloModel is None:
                    continue

                stopTime: int = getDictV(params, "stopTime", default=5)
                filterLib.yoloModel.stopTimeThreshold = stopTime

                triggerColor: list = getDictV(
                    params, "triggerColor", default=[56, 26, 211]
                )
                filterLib.yoloModel.triggerColor = triggerColor

            elif key == "fps":
                func = filterLib.displayFPS

            if func is None:
                continue
            screen.addFilter(func)

    def setupRecord(self, screen: Screen, v: dict) -> None:
        record: dict[str, int | str] = v.get("record", dict())
        output: str = str(record.get("output", ""))
        fps: int = int(record.get("fps", 24))
        fourcc: str = str(record.get("fourcc", "XVID"))
        screen.setupOutSource(output, fourcc, fps)

    def run(self, display=False):
        if not display:
            return 

        self._running = True
        self.capture_thread.start()
        self.display_thread.start()

    def captureThread(self):
        while self._running:
            for screen in self.screens:
                screen.getNextFrame()

        for screen in self.screens:
            screen.close()

        destroyAllWindows()

    def displayThread(self):
        while self._running:
            for screen in self.screens:
                screen.applyFilter()
                screen.displayScreen(screen.name)

            if waitKey(1) & 0xFF == ord('q'):
                self._running = False
                break

