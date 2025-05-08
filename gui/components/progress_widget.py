from gui.common import MyProgressBar, VerticalFrame, VerticalCard
from qfluentwidgets import BodyLabel, StrongBodyLabel
from PySide6.QtGui import QColor


class ProgressWidget(VerticalFrame):
    def __init__(self, parent = None):
        super().__init__(parent = parent)
        self.show_percent = True
        self._main_text = None
        # self.setLayoutMargins(0, 0, 0, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.progress_bar = MyProgressBar(self)
        self.progress_bar.setValue(100)
        # self.progress_bar.setFixedHeight(40)

        self.addWidget(self.progress_bar)

        self.eta_label = BodyLabel(self)
        self.eta_label.raise_()

        self.main_text = StrongBodyLabel(self)
        self.main_text.raise_()

        self.steps_label = BodyLabel(self)
        self.steps_label.raise_()

        self.reset_state()

        self.set_text("Initializing")
        self.set_eta(0.0)
        self.set_steps(0, 0)

        self.setMinimumWidth((self.main_text.width() + self.steps_label.width() + self.eta_label.width()) + 45 )

    def set_text(self, text: str | None = "Generate"):
        if text is None:
            return
        self._main_text = text
        if self.show_percent:
            text = f"{text}--({self.progress_bar.text()})"
        else:
            text = f"{text}"
        self.main_text.setText(text)
        self.main_text.adjustSize()

    def set_eta(self, eta: float | None = 0.0):
        if eta is None:
            return
        self.eta_label.setText(f"ETA: {eta}s")
        self.eta_label.adjustSize()

    def set_steps(self, current: int | None = 0, total: int | None = 0):
        if current is None or total is None:
            return
        self.steps_label.setText(f"{current}/{total} steps")
        self.steps_label.adjustSize()

    def setValue(self, value: int):
        self.progress_bar.setValue(value)
        self.set_text(self._main_text)


    def set_progress(self, progress: dict):
        eta = progress.get("eta_relative", None)
        self.set_eta(eta)
        state =  progress.get("state", {})
        print(state)
        self.setValue(progress.get("progress", 0) * 100)

        self.set_text(state.get('job', None))
        current_step = state.get('sampling_step', None)
        total_steps = state.get('sampling_steps', None)

        if state.get('skipped', False):
            self.show_percent = False
            self.set_text("Skipped")
            self.progress_bar.set_bar_color(QColor(255, 255, 0))

        elif state.get('interrupted', False):
            self.show_percent = False
            self.set_text("Interrupted")
            self.progress_bar.set_bar_color(QColor(255, 0, 255))

        else:
            self.show_percent = True
            self.progress_bar.reset_bar_color()

        self.set_steps(current_step, total_steps)

    def reset_state(self):
        self.progress_bar.setValue(0)
        self.set_text("Initializing...")
        self.set_eta(0.0)
        self.set_steps(0, 0)
        self.show_percent = True
        self.progress_bar.reset_bar_color()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # self.progress_bar.setFixedHeight(self.height())
        # self.progress_bar.updateGeometry()
        progress_geo = self.progress_bar.geometry()


        center = progress_geo.center()
        self.eta_label.move(progress_geo.left() + 15, (center.y() - self.eta_label.height() // 2))
        self.main_text.move(center.x() - self.main_text.width()//2,  center.y() - self.main_text.height()//2)
        self.steps_label.move(progress_geo.right() - self.steps_label.width() - 15,  center.y() - self.steps_label.height()//2)

    def setError(self, error: str):
        self.progress_bar.set_bar_color(QColor(255, 0, 0))
        self.progress_bar.setValue(100)
        self.show_percent = False
        self.set_text(error)
        self.eta_label.setText("???")
        self.steps_label.setText("?/?")

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication([])
    window = ProgressWidget()
    progress = {
    "progress": 0.23,
    "eta_relative": 17.42,
    "state": {
        "skipped": False,
        "interrupted": True,
        "job": "Text",
        "job_count": 1,
        "job_timestamp": "20250427105454",
        "job_no": 0,
        "sampling_step": 7,
        "sampling_steps": 30
    }}
    window.set_progress(progress)
    window.progress_bar.setFixedHeight(30)
    window.show()
    window.setError("Error")
    app.exec()