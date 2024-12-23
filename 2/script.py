import Metashape
import os, sys, time

# Checking compatibility
# compatible_major_version = "2.1"
# found_major_version = ".".join(Metashape.app.version.split('.')[:2])
# if found_major_version != compatible_major_version:
#     raise Exception("Incompatible Metashape version: {} != {}".format(found_major_version, compatible_major_version))

def find_files(folder, types):
    return [entry.path for entry in os.scandir(folder) if (entry.is_file() and os.path.splitext(entry.name)[1].lower() in types)]


# if len(sys.argv) < 3:
#     print("Usage: general_workflow.py <image_folder> <output_folder>")
#     raise Exception("Invalid script arguments")

# image_folder = sys.argv[1]
# output_folder = sys.argv[2]

# photos = find_files(image_folder, [".jpg", ".jpeg", ".tif", ".tiff"])

app: Metashape.Application = Metashape.Application()
doc: Metashape.Document = app.document
# doc.save(output_folder + '/project.psx')

chunk = doc.chunk

# chunk.addPhotos(photos)

control_path = "/home/ard/prg/FTP/2/UAV/osnowa_UAV.txt"

# with open(control_path, 'r') as file:
#     for line in file:
#         parts = line.split()
#         if len(parts) == 4:
#             marker = chunk.addMarker()
#             marker.label = parts[0]
#             marker.reference.location = Metashape.Vector([float(parts[2]), float(parts[1]), float(parts[3])])
#             print(f"Added marker {marker.label} at {marker.reference.location}")

def ExportMarkers():
    File = Metashape.app.getSaveFileName('Export traces', filter="*.txt")
    if len(File) == 0:
        return
    File = open(File, 'w')
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
                            File.write(data)
    File.close()


app.removeMenuItem("ExportMarkers")
app.addMenuItem("ExportMarkers", ExportMarkers)
