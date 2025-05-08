from qfluentwidgets import Dialog, BodyLabel, CheckBox, StrongBodyLabel
from PySide6.QtWidgets import QApplication, QVBoxLayout, QDialog, QDialogButtonBox


class BackupOptionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Backup Options")
        # self.setFixedSize(400, 300)

        layout = QVBoxLayout(self)

        # Add checkboxes for backup options
        self.txt2img_cb = CheckBox("txt2img")
        self.txt2img_cb.setChecked(True)
        self.img2img_cb = CheckBox("img2img")
        self.img2img_cb.setChecked(True)
        self.controls_cb = CheckBox("controls")
        self.controls_cb.setChecked(True)
        self.extras_cb = CheckBox("extras")
        self.extras_cb.setChecked(True)
        self.backup_configs = CheckBox("Backup Configurations")
        self.backup_configs.setChecked(True)

        layout.addWidget(StrongBodyLabel("Select Backup Options"))
        layout.addWidget(self.txt2img_cb)
        layout.addWidget(self.img2img_cb)
        layout.addWidget(self.controls_cb)
        layout.addWidget(self.extras_cb)
        layout.addWidget(self.backup_configs)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(button_box)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

    def get_selected(self):
        return {
            "txt2img": self.txt2img_cb.isChecked(),
            "img2img": self.img2img_cb.isChecked(),
            "controls": self.controls_cb.isChecked(),
            "extras": self.extras_cb.isChecked(),
            "configs": self.backup_configs.isChecked()
        }


if __name__ == "__main__":
    app = QApplication([])
    dialog = BackupOptionsDialog()
    dialog.show()
    app.exec()