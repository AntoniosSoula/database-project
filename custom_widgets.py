from PyQt6.QtWidgets import QLabel, QMessageBox, QFileDialog
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import os
import shutil

class DraggableLabel(QLabel):
    def __init__(self, player_id, parent=None):
        super().__init__(parent)
        self.player_id = player_id
        self.image_path = f"images/{self.player_id}.png"
        self.default_image = "images/defaultpicture.png"  # Προεπιλεγμένη εικόνα
        self.setAcceptDrops(True)
        self.setScaledContents(True)
        self.load_image()

    def load_image(self):
        if os.path.exists(self.image_path):
            self.setPixmap(QPixmap(self.image_path))
        else:
            self.setPixmap(QPixmap(self.default_image))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                local_file = url.toLocalFile()
                if local_file.lower().endswith('.png'):  # Ελέγχει αν είναι PNG
                    shutil.copy(local_file, self.image_path)
                    self.load_image()
                    break

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.download_image()

    def download_image(self):
        if not os.path.exists(self.image_path):
            QMessageBox.warning(self, "Σφάλμα", "Η εικόνα δεν υπάρχει για λήψη.")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Αποθήκευση Εικόνας", f"{self.player_id}.png", "PNG Files (*.png)")
        if save_path:
            try:
                shutil.copy(self.image_path, save_path)
                QMessageBox.information(self, "Επιτυχία", f"Η εικόνα αποθηκεύτηκε στο {save_path}.")
            except Exception as e:
                QMessageBox.critical(self, "Σφάλμα", f"Αποτυχία αποθήκευσης της εικόνας: {e}")
