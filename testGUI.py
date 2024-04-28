import sys
from PySide6.QtCore import QThread, Signal, Slot, Qt
from PySide6.QtGui import QImage, QAction, QKeySequence, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QCheckBox,
    QFormLayout,
    QSpinBox,
)
from libs.screenlib import Screen

source = "http://220.254.72.200/nphMotionJpeg?Resolution=640x640&Quality=Standard"
src = "rtsp://192.168.1.105:554/user=admin&password=&channel=2&stream=0.sdp?"


class ScreenThread(QThread):
    updateFrame: Signal = Signal(QImage)

    def __init__(self, src: str, name: str, parent=None):
        QThread.__init__(self, parent)
        self._status: bool = True
        self._origin: bool = True
        self._screen = Screen(src, name)

    def run(self):
        while self._status:
            if not self._screen.getNextFrame():
                continue

            img = self._screen.getQImage()
            self.updateFrame.emit(img)

        self._screen.close()

    def close(self):
        self._status = False


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        ## +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        ## ===========================Threads=============================

        self.th = ScreenThread(src, "test", self)
        self.th.finished.connect(self.close)
        self.th.updateFrame.connect(self.setImage)

        ## ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        ## =============================Window=============================

        self.setWindowTitle("CCTVTracker")
        self.setGeometry(0, 0, 1024, 640)

        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        self.windowLayout = QHBoxLayout(centralWidget)

        ## ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        ## =============================Main=============================

        self.windowLayout.addWidget(self.createMainDisplayScreen())
        self.windowLayout.addWidget(self.createControllGroupbox())

        self.initMenuBar()

        self.start()

    def createMainDisplayScreen(self) -> QWidget:
        mainScreenwidget = QWidget()

        layout = QVBoxLayout(mainScreenwidget)

        group_box = QGroupBox("Screen cam 1")
        group_layout = QVBoxLayout(group_box)

        self.imageLabel = QLabel()
        # self.imageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.imageLabel.setMaximumSize(1280, 640)

        group_layout.addWidget(self.imageLabel)
        layout.addWidget(group_box)

        return mainScreenwidget

    def createControllGroupbox(self) -> QWidget:
        controllGroup = QGroupBox("Settings")
        controllGroup.setMinimumWidth(220)
        mainLayout = QVBoxLayout()
        controllGroup.setLayout(mainLayout)

        objTrailingGroupbox = QGroupBox("Object Trailing")
        objTrailingLayout = QFormLayout()
        objTrailingGroupbox.setLayout(objTrailingLayout)

        toggleTrailingButton = QCheckBox("On/Off")
        lengthInput = QSpinBox()
        lengthInput.setRange(1, 100)
        sizeInput = QSpinBox()
        sizeInput.setRange(1, 100)

        objTrailingLayout.addRow(toggleTrailingButton)
        objTrailingLayout.addRow("Length:", lengthInput)
        objTrailingLayout.addRow("Size:", sizeInput)

        stopDetectionGroupbox = QGroupBox("Stop Detection")
        stopDetectionLayout = QFormLayout()
        stopDetectionGroupbox.setLayout(stopDetectionLayout)

        toggleTimeStopButton = QCheckBox("On/Off")
        stopTimeThresholdInput = QSpinBox()
        stopTimeThresholdInput.setMinimum(1)

        stopDetectionLayout.addRow(toggleTimeStopButton)
        stopDetectionLayout.addRow("Stop Threshold:", stopTimeThresholdInput)

        mainLayout.addWidget(objTrailingGroupbox)
        mainLayout.addWidget(stopDetectionGroupbox)

        return controllGroup

    def initMenuBar(self):
        self.menu = self.menuBar()

        menuScreen = self.menu.addMenu("Screen")
        exitAction = QAction("Exit", self)
        exitAction.setShortcut("Ctrl+q")
        exitAction.triggered.connect(self.kill_thread)
        menuScreen.addAction(exitAction)

        menuAbout = self.menu.addMenu("&About")
        about = QAction("About Qt", self)
        about.setShortcut(QKeySequence.StandardKey.HelpContents)
        about.triggered.connect(QApplication.aboutQt)
        menuAbout.addAction(about)

    @Slot()
    def kill_thread(self):
        self.th.close()
        self.th.wait()
        self.th.terminate()

    @Slot()
    def start(self):
        self.th.start()

    @Slot(QImage)
    def setImage(self, image: QImage):
        image = image.scaled(1280, 720, Qt.AspectRatioMode.KeepAspectRatio)
        pixmap: QPixmap = QPixmap.fromImage(image)
        self.imageLabel.setPixmap(pixmap)
        self.imageLabel.setFixedSize(pixmap.size())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
