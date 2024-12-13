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

app: Metashape.Application = Metashape.Application()
doc: Metashape.Document = app.document


def get_path(path):
    if os.path.exists(path):
        return path
    else:
        raise FileNotFoundError(f"Plik {path} nie istnieje")

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
    # ask the user for CRS
    photos = find_files(photo_folder, image_types)
    chunk.addPhotos(photos)
    for camera in chunk.cameras:
        camera.reference.location = crs.project(chunk.crs.unproject(camera.reference.location))
    chunk.crs = crs
    chunk.updateTransform()

def align_photos():
    chunk = doc.chunk
    if not chunk:
        app.messageBox("Error, please select a chunk with loaded photos first.")
        return
    accuracies = {0: "Highest", 1: "High", 2: "Medium", 4: "Low", 8: "Lowest"}
    acc_str = ""
    for key, value in accuracies.items():
        acc_str += f"{key} - {value}\n"
    downscale_string = f"Please enter the image alignment accuracy\n{acc_str}"

    downscale_int = -1
    while downscale_int not in accuracies:
        downscale_int = app.getInt(downscale_string)
        if downscale_int not in accuracies:
            app.messageBox("Invalid input, Please enter a valid integer.")

    gen_presel_string = "Enable generic preselection"
    gen_presel_bool = app.getBool(gen_presel_string)
    ref_presel_string = "Enable reference preselection"
    ref_presel_bool = app.getBool(ref_presel_string)
    reset_align_string = "Reset current alignment"
    reset_align_bool = app.getBool(reset_align_string)


    chunk.matchPhotos(downscale=downscale_int, generic_preselection=gen_presel_bool, reference_preselection=ref_presel_bool)
    chunk.alignCameras(reset_alignment=reset_align_bool)

def build_cloud():
    accuracies = {1: "Ultra high", 2: "High", 4: "Medium", 8: "Low", 16: "Lowest"}
    acc_str = ""
    for key, value in accuracies.items():
        acc_str += f"{key} - {value}\n"
    downscale_string = f"Please enter the depth map build accuracy\n{acc_str}"

    downscale_int = -1
    while downscale_int not in accuracies:
        downscale_int = app.getInt(downscale_string)
        if downscale_int not in accuracies:
            app.messageBox(f"Invalid input, please enter a valid integer from:\n{acc_str}")
    chunk = doc.chunk
    chunk.buildDepthMaps(downscale=downscale_int)
    chunk.buildPointCloud(point_colors=True)



image_types = [".jpg", ".jpeg", ".tif", ".tiff"]


app.removeMenuItem("Get Photos")
app.addMenuItem("Get Photos", get_photos)

app.removeMenuItem("Align Photos")
app.addMenuItem("Align Photos", align_photos)

app.removeMenuItem("Generate Depth Maps and Build Point Cloud")
app.addMenuItem("Generate Depth Maps and Build Point Cloud", build_cloud)

