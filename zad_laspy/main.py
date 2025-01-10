import laspy
import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt

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
# las.write("las.laz")

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

def manualne_przycinanie_chmury_punktów(chmura_punktow):
    print("Manualne przycinanie chmury punktów")
    print("Etapy przetwarzania danych:")
    print(" (0) Manualne zdefiniowanie widoku poprzez obrót myszka lub:")
    print(" (0.1) Podwójne wciśnięcie klawisza X - zdefiniowanie widoku ortogonalnego względem osi X")
    print(" (0.2) Podwójne wciśnięcie klawisza Y - zdefiniowanie widoku ortogonalnego względem osi Y")
    print(" (0.3) Podwójne wciśnięcie klawisza Z - zdefiniowanie widoku ortogonalnego względem osi Z")
    print(" (1) Wciśnięcie klawisza K - zmiana na tryb rysowania")
    print(" (2.1) Wybór zaznaczenia poprzez wciśnięcie lewego przycisku myszy i interaktywnego narysowania prostokąta lub")
    print(" (2.2) przytrzymanie przycisku ctrl i wybór wierzchołków poligonu lewym przyciskiem myszy")
    print(" (3) Wciśnięcie klawisza C - wybór zaznaczonego fragmentu chmury punktów i zapis do pliku")
    print(" (4) Wciśnięcie klawisza F - powrót do interaktywnego wyświetlania chmury punktów")
    #o3d.visualization.draw_geometries_with_editing(self, window_name='Open3D', width=1920, height=1080, left=50, top=50, visible=True)
    o3d.visualization.draw_geometries_with_editing([chmura_punktow],window_name='Przycianie chmury punktow')


x, y, z = las.x, las.y, las.z
las_points = np.vstack((x,y,z)).transpose()
las_colors = np.vstack((r,g,b)).transpose()
chmura_punktow = o3d.geometry.PointCloud()
chmura_punktow.points = o3d.utility.Vector3dVector(las_points)
# o3d.visualization.draw_geometries_with_editing([chmura_punktow],window_name='Przycianie chmury punktow')

# get only points that are buildings
buildings = las[las.classification == 6]
vegetation = las[np.logical_or.reduce((las.classification == 3, las.classification == 4, las.classification == 5))]
ground = las[las.classification == 2]

print(len(buildings), len(vegetation), len(ground))

lens = np.array([len(buildings), len(vegetation), len(ground)])
plt.bar(np.arange(3), lens)
# add labels
plt.title('Liczba punktów w każdej klasie')
plt.xticks([0, 1, 2], ['budynki', 'roślinność', 'grunt'])
# plt.show()

# color chmura by classification
red = np.array([255, 0, 0])
green = np.array([0, 255, 0])
blue = np.array([0, 0, 255])
colors = np.zeros_like(las_colors)
colors[las.classification == 6] = red
colors[np.logical_or.reduce((las.classification == 3, las.classification == 4, las.classification == 5))] = green
colors[las.classification == 2] = blue
chmura_punktow.colors = o3d.utility.Vector3dVector(colors)
# o3d.visualization.draw_geometries_with_editing([chmura_punktow],window_name='Kolorowanie po klasie')

# count density with knn
knn = o3d.geometry.KDTreeFlann(chmura_punktow)
pts = np.array(chmura_punktow.points)
[k, idx, _] = knn.search_knn_vector_3d(pts[100], 5)
print(f"k: {k}, idx: {np.array(idx)}")

