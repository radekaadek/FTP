import Metashape



app: Metashape.Application = Metashape.Application()
doc: Metashape.Document = app.document
chunk = doc.chunk



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
 
def ReadFileWithPixelCoordinates(stripNumber = 0, pairNumber = 0):
    name = app.getSaveFileName('Import traces',filter="*.txt")
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


app.removeMenuItem("ImportMarkers")
app.addMenuItem("ImportMarkers", ReadFileWithPixelCoordinates)
