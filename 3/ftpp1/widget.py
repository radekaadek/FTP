import sys
import Metashape
import os

from PySide6.QtWidgets import QApplication, QWidget
from ui_form import Ui_Widget

# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
app: Metashape.Application = Metashape.Application()
doc: Metashape.Document = app.document

class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)

image_types = [".jpg", ".jpeg", ".tif", ".tiff"]

def find_files(folder, types):
    return [entry.path for entry in os.scandir(folder) if (entry.is_file() and os.path.splitext(entry.name)[1].lower() in types)]

def get_photos():
    chunk = doc.chunk
    if not chunk:
        chunk = doc.addChunk()
    photo_folder = app.getExistingDirectory("Please select the folder of photos to load.")
    if not photo_folder:
        return
    crs = app.getCoordinateSystem()


    photos = find_files(photo_folder, image_types)
    chunk.addPhotos(photos)
    for camera in chunk.cameras:
        camera.reference.location = crs.project(chunk.crs.unproject(camera.reference.location))
    chunk.crs = crs
    chunk.updateTransform()

def run():
    app = QApplication(sys.argv)
    widget = Widget()
    # set get_photos to run on click
    button = widget.ui.pb
    button.clicked.connect(get_photos)
    widget.show()


    sys.exit(app.exec())

app.removeMenuItem("Run")
app.addMenuItem("Run", run)

if __name__ == "__main__":
    run()

