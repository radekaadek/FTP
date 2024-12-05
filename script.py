import Metashape


doc = Metashape.Document()
chunk = doc.chunk
app = Metashape.Application()

# chunk.matchPhotos(1, generic_preselection=True, reference_preselection=False())
# chunk.alignCameras()
# chunk.buildDepthMaps()
# chunk.buildModel()
# chunk.buildUV()
# chunk.buildTexture()
# doc.save()



def DefineBundleAdjustmentParameters(MarkerLocationAccuracy = Metashape.Vector([0.1, 0.1, 0.1]),
                                     CameraLocationAccuracy = Metashape.Vector([100, 100, 100]),
                                     CameraRotationAccuracy = Metashape.Vector([100, 100, 100]),
                                     TiePointAccuracy = 200, MarkerProjectionAccuracy = 100,
                                     ScalebareAccuracy = 0.2):
    chunk = Metashape.app.document.chunk
    chunk.marker_location_accuracy = MarkerLocationAccuracy
    chunk.marker_projection_accuracy = MarkerProjectionAccuracy
    chunk.tie_point_accuracy = TiePointAccuracy
    chunk.scalebar_accuracy = ScalebareAccuracy
    chunk.camera_rotation_accuracy = CameraRotationAccuracy
    chunk.camera_location_accuracy = CameraLocationAccuracy
    # chunk.save()

def ExportMarkers():
    File = Metashape.Application.getSaveFileName('Export traces', filter="*.txt")
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
                        ReprojectionError = camera.project(marker.position)-marker.projections[camera].coord
                        if ReprojectionError is not None:
                            File.write(marker.label)
                            File.write(' ')
                            File.write(camera.label)
                            File.write(' ')
                            File.write(ReprojectionError[0])
                            File.write(ReprojectionError[1])
                            File.write(marker.projections[camera].coord[0])
                            File.write(marker.projections[camera].coord[1])
                            File.write('\n')
    File.close()


app.addMenuItem("mojprzycisk")

app.removeMenuItem("mojprzycisk")
app.addMenuItem("mojprzycisk", DefineBundleAdjustmentParameters)

app.removeMenuItem("ExportMarkers")
app.addMenuItem("ExportMarkers", DefineBundleAdjustmentParameters)
