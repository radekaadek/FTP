# Przygotowanie kreatora (Wizard) dla niedoświadczonych użytkowników, w którym zostaną zdefiniowane predefiniowane parametry, takie jak:ościeżka dostępu oraz wczytywanie zdjęć na podstawie wskazanego folderu,oorientacja zdjęć,ogenerowanie gęstych chmur punktów,ogenerowanie modeli 3D.2.Użytkownik będzie mógł zmieniać powyższe parametry, np. poprzez ich wybór z listy lub odznaczenie checkboxów.3.Kluczowym założeniem będzie wybór układu odniesienia (z listy dostępnych danych) oraz wykonanie konwersji współrzędnych punktów osnowy fotogrametrycznej lub przybliżonych elementów orientacji zewnętrznej.4.Po wywołaniu procesu jednym przyciskiem aplikacja powinna przeprowadzić wszystkie kroki, a wynikowy plik zapisać w katalogu zawierającym zdjęcia
# okienko wyświetlane po odpaleniu skrytpu w Agisoft Metashape
# wybór folderu z zdjęciami - przycisk
# wybór układu współrzędnych (lista) - przycisk
# wybór orientacji zdjęć - przycisk
# Accuracy - lista
# generic preselection (domyślnie zaznaczone)
# replace preselection (domyślnie zaznaczone)
# reset current alignment (domyślnie odznaczone)
# Build Point Cloud - lista
# calculate point colors (domyślnie zaznaczone)
# calcualte point confidence  (domyślnie zaznaczone)
# replace default point cloud (domyślnie odznaczone)
# Build Model
# source - depth maps
# quality - medium
# face count - medium
# przycisk zapisu do pliku

import Metashape
import os
from PyQt6.QtWidgets import *

app: Metashape.Application = Metashape.Application()
doc: Metashape.Document = app.document


def get_path(path):
    if os.path.exists(path):
        return path
    else:
        raise FileNotFoundError(f"Plik {path} nie istnieje")

def find_files(folder, types):
    return [entry.path for entry in os.scandir(folder) if (entry.is_file() and os.path.splitext(entry.name)[1].lower() in types)]

def wizard():
    qt_app = QApplication.instance()  # Get the existing QApplication instance if it exists
    if not qt_app:  # If no instance exists, create a new one
        qt_app = QApplication([])
    window = QWidget()
    layout = QVBoxLayout()

    # Button to get photos
    btn_get_photos = QPushButton("Get Photos")
    btn_get_photos.clicked.connect(get_photos)
    layout.addWidget(btn_get_photos)


    accuracies = {0: "Highest", 1: "High", 2: "Medium", 4: "Low", 8: "Lowest"}

    # window = QWidget()
    # layout = QVBoxLayout()

    accuracy_label = QLabel("Image alignment accuracy:")
    layout.addWidget(accuracy_label)

    accuracy_combo = QComboBox()
    for key, value in accuracies.items():
        accuracy_combo.addItem(value, key)
    layout.addWidget(accuracy_combo)

    gen_presel_checkbox = QCheckBox("Enable generic preselection")
    layout.addWidget(gen_presel_checkbox)

    ref_presel_checkbox = QCheckBox("Enable reference preselection")
    layout.addWidget(ref_presel_checkbox)

    reset_align_checkbox = QCheckBox("Reset current alignment")
    layout.addWidget(reset_align_checkbox)

    def confirm_alignment():
        chunk = doc.chunk
        if not chunk:
            app.messageBox("Error, please select a chunk with loaded photos first.")
            return
        downscale_int = accuracy_combo.currentData()
        gen_presel_bool = gen_presel_checkbox.isChecked()
        ref_presel_bool = ref_presel_checkbox.isChecked()
        reset_align_bool = reset_align_checkbox.isChecked()
        print(f"{downscale_int=} {gen_presel_bool=} {ref_presel_bool=} {reset_align_bool=}")
        print(f"{type(downscale_int)=} {type(gen_presel_bool)=} {type(ref_presel_bool)=} {type(reset_align_bool)=}")

        chunk.matchPhotos(downscale=downscale_int, generic_preselection=gen_presel_bool, reference_preselection=ref_presel_bool)
        chunk.alignCameras(reset_alignment=reset_align_bool)
        # window.close()

    confirm_button = QPushButton("Align Photos")
    confirm_button.clicked.connect(confirm_alignment)
    layout.addWidget(confirm_button)

    depth_accuracy_label = QLabel("Depth map build accuracy:")
    layout.addWidget(depth_accuracy_label)

    accuracies_cloud = {1: "Ultra high", 2: "High", 4: "Medium", 8: "Low", 16: "Lowest"}
    depth_accuracy_combo = QComboBox()
    for key, value in accuracies_cloud.items():
        depth_accuracy_combo.addItem(value, key)
    layout.addWidget(depth_accuracy_combo)

    save_cloud_checkbox = QCheckBox("Save the created point cloud")
    layout.addWidget(save_cloud_checkbox)

    def build_depth_maps():
        chunk = doc.chunk
        if not chunk:
            app.messageBox("Error, please select a chunk with aligned photos first.")
            return
        downscale_int = depth_accuracy_combo.currentData()
        chunk.buildDepthMaps(downscale=downscale_int)

    def build_point_cloud():
        chunk = doc.chunk
        if not chunk:
            app.messageBox("Error, please select a chunk with depth maps first.")
            return
        save_cloud = save_cloud_checkbox.isChecked()
        name = None
        if save_cloud:
            name = app.getSaveFileName('Export point cloud path', filter="*.las")
        chunk.buildPointCloud(point_colors=True)
        if save_cloud and name is not None:
            chunk.exportPointCloud(name)


    btn_depth_maps = QPushButton("Generate Depth Maps")
    btn_depth_maps.clicked.connect(build_depth_maps)
    layout.addWidget(btn_depth_maps)

    btn_build_point_cloud = QPushButton("Build Point Cloud")
    btn_build_point_cloud.clicked.connect(build_point_cloud)
    layout.addWidget(btn_build_point_cloud)


    # Button to build model
    btn_build_model = QPushButton("Build Model")
    btn_build_model.clicked.connect(build_model)
    layout.addWidget(btn_build_model)

    window.setLayout(layout)
    window.show()
    qt_app.exec()


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

def build_cloud():
    pass

def build_model():
    # get depth map

    face_counts = Metashape.FaceCount
    num_to_face = {0: face_counts.LowFaceCount, 1: face_counts.MediumFaceCount, 2: face_counts.HighFaceCount, 3: face_counts.CustomFaceCount}
    cnt = -1
    while cnt not in num_to_face.keys():
        cnt = app.getInt(f"Please enter the model's desired face count\n"
                         "0: Low face count\n"
                         "1: Medium face count\n"
                         "2: High face count\n"
                         "3: Custom face count")
        if cnt is None:
            return
        if cnt not in num_to_face.keys():
            app.messageBox(f"Invalid input, please enter a valid integer from:\n{num_to_face.keys()}")
    face_cnt = num_to_face[cnt]

    chunk = doc.chunk
    save_model = app.getBool("Save the created model?")


    chunk = doc.chunk
    if face_cnt == face_counts.CustomFaceCount:
        face_num = -1
        while face_num < 1:
            face_num = app.getInt("Please enter the desired number of faces")
            if face_num is None:
                return
            if face_num < 1:
                app.messageBox("Invalid input, please enter a positive integer")
        face_cnt = face_counts.CustomFaceCount(face_count=face_cnt, face_size=face_num)
    else:
        chunk.buildModel(face_count=face_cnt)
    if save_model:
        chunk.exportModel(app.getSaveFileName('Export model', filter="*.obj"))


image_types = [".jpg", ".jpeg", ".tif", ".tiff"]


app.removeMenuItem("Get Photos")
app.addMenuItem("Get Photos", get_photos)

app.removeMenuItem("Generate Depth Maps and Build Point Cloud")
app.addMenuItem("Generate Depth Maps and Build Point Cloud", build_cloud)

app.removeMenuItem("Build Model")
app.addMenuItem("Build Model", build_model)

app.removeMenuItem("Wizard")
app.addMenuItem("Wizard", wizard)

