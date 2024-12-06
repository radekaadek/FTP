import laspy
import numpy as np
# Odczyt pliku LAS
las = laspy.read("79529_1503958_M-34-5-C-b-4-4-3-4.laz")
# Ekstrakcja współrzędnych
x, y, z = las.x, las.y, las.z
# Konwersja do tablicy NumPy
points = np.vstack((x, y, z)).T
print("Liczba punktów:", len(points))
# Odczyt nagłówka pliku LAS
header = las.header
print(header)
# Wyświetlenie podstawowych informacji o nagłówku
print("Wersja LAS:", header.version)
print("Identyfikator systemu:", header.system_identifier)
print("Oprogramowanie generujące:", header.generating_software)
print("Wartości minimalne i maksymalne:")
print("Min X, Y, Z:", header.min)
print("Max X, Y, Z:", header.max)
# Uzyskanie dostępu do danych punktów
point_format = las.point_format
# Wyświetlenie dostępnych wartości punktów
for spec in point_format:
    print(spec.name)
# Normalizacja wartości RGB
r = las.red / max(las.red)
g = las.green / max(las.green)
b = las.blue / max(las.blue)

# set top 10 values to 90 percentile
perc = 95
intensity_perc = np.percentile(las.intensity, perc)
i = las.intensity
i[i > intensity_perc] = intensity_perc

rescaled_intensity = (i - np.min(i)) / (np.max(i) - np.min(i)) * 255
# round to ints
# rescaled_intensity = np.round(rescaled_intensity)
print(rescaled_intensity)
las.red = rescaled_intensity
las.green = rescaled_intensity
las.blue = rescaled_intensity

# save to file
las.write("las.laz")

def point_extraction_based_on_the_class(las, class_type):
    if class_type == 'buildings':
        print('Ekstrakcja punktów budynków')
# Klasyfikacja 6 oznacza budynki
        buildings_only = np.where(las.classification == 6)
        buildings_points = las.points[buildings_only]
        return buildings_points
    elif class_type == 'vegetation':
        print('Ekstrakcja punktów roślinności')
        vegetation_low = np.where(las.classification == 3)
        vegetation_medium = np.where(las.classification == 4)
        vegetation_high = np.where(las.classification == 5)
        vegetation = np.concatenate((vegetation_low, vegetation_medium,
        vegetation_high))
        vegetation_points = las.points[vegetation]
        return vegetation_points
    else:
        print('Ekstrakcja punktów gruntu')
# Klasyfikacja 2 oznacza grunt
        ground_only = np.where(las.classification == 2)
        ground_points = las.points[ground_only]
        return ground_points

# 1. Create a new header
my_data = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
header = laspy.LasHeader(point_format=3, version="1.2")
header.offsets = np.min(my_data, axis=0)
header.scales = np.array([0.1, 0.1, 0.1])
# 3. Create a LasWriter and a point record, then write it
with laspy.open("somepath.las", mode="w", header=header) as writer:
    point_record = laspy.ScaleAwarePointRecord.zeros(my_data.shape[0],
header=header)
    point_record.x = my_data[:, 0]
    point_record.y = my_data[:, 1]
    point_record.z = my_data[:, 2]
    writer.write_points(point_record)
