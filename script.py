import Metashape

def my_fun():
    print("Hello World")

doc = Metashape.Document()
chunk = doc.chunk
app = Metashape.Application()
app.removeMenuItem("mojprzycisk")
app.addMenuItem("mojprzycisk", my_fun)

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

