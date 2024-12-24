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
import PyQt6
from PyQt6.QtWidgets import *

app: Metashape.Application = Metashape.Application()
doc: Metashape.Document = app.document

image_types = [".jpg", ".jpeg", ".tif", ".tiff"]

def get_path(path):
    if os.path.exists(path):
        return path
    else:
        raise FileNotFoundError(f"Plik {path} nie istnieje")

def find_files(folder, types):
    return [entry.path for entry in os.scandir(folder) if (entry.is_file() and os.path.splitext(entry.name)[1].lower() in types)]

def getMarker(chunk, Label):
    for marker in chunk.markers:
        if marker.label == Label:
            return marker
    return None
 
def getCamera(chunk, Label):
    for camera in chunk.cameras:
        if camera.label == Label:
            return camera
    return None

def export_markers():
    chunk = doc.chunk
    file_name = app.getSaveFileName('Export traces', filter="*.txt")
    if len(file_name) == 0:
        return
    with open(file_name, 'w') as f:
        for marker in chunk.markers:
            if marker.type == Metashape.Marker.Type.Regular:
                for camera in chunk.cameras:
                    if camera.enabled == 1:
                        Point2D = marker.projections[camera]
                        ReprojectionError = []
                        if Point2D is not None:
                            ReprojectionError = camera.project(marker.position)-marker.projections[camera].coord[:-1]
                            if ReprojectionError is not None:
                                data = (
                                    f"{marker.label} {camera.label} "
                                    f"{ReprojectionError[0]} {ReprojectionError[1]} "
                                    f"{marker.projections[camera].coord[0]} {marker.projections[camera].coord[1]}\n"
                                )
                                print(data)
                                f.write(data)
 
def import_markers():
    chunk = doc.chunk
    name = app.getOpenFileName('Import traces',filter="*.txt")
    if len(name) == 0:
        return
    File = open(name, "r")
    content = File.readlines()
    for line in content:
        MarkerLabel, CameraLabel, ErrorX, ErrorY, XFeatureCoordinates, YFeatureCoordinates = line.split()
        marker = getMarker(chunk, MarkerLabel)
        if not marker:
            marker = chunk.addMarker()
            marker.reference.accuracy = Metashape.Vector([0.03,0.03,0.05])
            marker.label = MarkerLabel
        camera = getCamera(chunk, CameraLabel)
        if not camera:
            print(CameraLabel + " camera not found in project")
            continue
        marker.projections[camera] = Metashape.Marker.Projection(Metashape.Vector([float(XFeatureCoordinates), float(YFeatureCoordinates)]), True)
    File.close()

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

def wizard():
    qt_app = QApplication.instance()  # Get the existing QApplication instance if it exists
    if not qt_app:  # If no instance exists, create a new one
        qt_app = QApplication([])
    window = QWidget()
    layout = QVBoxLayout()

    # add a big label with the title
    title_label = QLabel("Agisoft Metashape Pro Wizard")
    layout.addWidget(title_label)

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
    gen_presel_checkbox.setChecked(True)

    ref_presel_checkbox = QCheckBox("Enable reference preselection")
    layout.addWidget(ref_presel_checkbox)
    ref_presel_checkbox.setChecked(True)

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


    btn_depth_maps = QPushButton("Generate Depth Maps")
    btn_depth_maps.clicked.connect(build_depth_maps)
    layout.addWidget(btn_depth_maps)

    btn_point_colors = QCheckBox("Calculate Point Colors")
    layout.addWidget(btn_point_colors)
    btn_point_colors.setChecked(True)
    btn_point_confidence = QCheckBox("Calculate Point Confidence")
    layout.addWidget(btn_point_confidence)
    btn_point_confidence.setChecked(True)

    def build_point_cloud():
        chunk = doc.chunk
        if not chunk:
            app.messageBox("Error, please select a chunk with depth maps first.")
            return
        save_cloud = save_cloud_checkbox.isChecked()
        name = None
        if save_cloud:
            name = app.getSaveFileName('Export point cloud path', filter="*.las")
        chunk.buildPointCloud(point_colors=btn_point_colors.isChecked(), point_confidence=btn_point_confidence.isChecked())
        if save_cloud and name is not None:
            chunk.exportPointCloud(name)



    btn_build_point_cloud = QPushButton("Build Point Cloud")
    btn_build_point_cloud.clicked.connect(build_point_cloud)
    layout.addWidget(btn_build_point_cloud)

    face_count_label = QLabel("Model face count target:")
    layout.addWidget(face_count_label)

    face_counts = {0: "Low", 1: "Medium", 2: "High", 3: "Custom"}
    face_count_combo = QComboBox()
    for key, value in face_counts.items():
        face_count_combo.addItem(value, key)
    layout.addWidget(face_count_combo)

    save_model = QCheckBox("Save generated model")
    layout.addWidget(save_model)

    def build_model():
        chunk = doc.chunk
        if not chunk:
            app.messageBox("Error, please select a chunk with depth maps first.")
            return
        name = None
        if save_model.isChecked():
            name = app.getSaveFileName('Export model', filter="*.obj")

        face_count_int = face_count_combo.currentData()
        if face_count_int == 3:  # Custom face count
            face_num = -1
            while face_num < 1:
                face_num = app.getInt("Please enter the desired number of faces")
                if face_num is None:
                    return
                if face_num < 1:
                    app.messageBox("Invalid input, please enter a positive integer")
            face_count = Metashape.FaceCount.CustomFaceCount(face_count=face_count_int, face_size=face_num)
        else:
            face_count = {0: Metashape.FaceCount.LowFaceCount, 1: Metashape.FaceCount.MediumFaceCount, 2: Metashape.FaceCount.HighFaceCount}[face_count_int]

        chunk.buildModel(face_count=face_count)
        if save_model.isChecked() and name is not None:
            chunk.exportModel(name)

    # Button to build model
    btn_build_model = QPushButton("Build Model")
    btn_build_model.clicked.connect(build_model)
    layout.addWidget(btn_build_model)

    btn_import_markers = QPushButton("Import Markers")
    btn_import_markers.clicked.connect(import_markers)
    layout.addWidget(btn_import_markers)

    btn_export_markers = QPushButton("Export Markers")
    btn_export_markers.clicked.connect(export_markers)
    layout.addWidget(btn_export_markers)

    window.setLayout(layout)
    window.show()
    qt_app.exec()



app.removeMenuItem("Wizard")
app.addMenuItem("Wizard", wizard)

