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
chunk = doc.chunk

def get_path(path):
    if os.path.exists(path):
        return path
    else:
        raise FileNotFoundError(f"Plik {path} nie istnieje")

def find_files(folder, types):
    return [entry.path for entry in os.scandir(folder) if (entry.is_file() and os.path.splitext(entry.name)[1].lower() in types)]

def get_photos():
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
    chunk.alignCameras()
    chunk.matchPhotos()

def build_cloud():
    chunk.buildPointCloud(point_colors=True)



image_types = [".jpg", ".jpeg", ".tif", ".tiff"]


app.removeMenuItem("GetPhotosAlign")
app.addMenuItem("GetPhotosAlign", get_photos)

app.removeMenuItem("Build Point Cloud")
app.addMenuItem("Build Point Cloud", build_cloud)
