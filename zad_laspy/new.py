import subprocess
from tempfile import TemporaryFile
import click
import laspy
import json
import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt
import rasterio

def visualize_3d(points, colors, title="3D Visualization"):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.colors = o3d.utility.Vector3dVector(colors)
    o3d.visualization.draw_geometries([pcd], window_name=title)

@click.group()
def cli():
    pass

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
def analyze(input_file):
    """Analyze LAS/LAZ file and generate visualizations."""
    las = laspy.read(input_file)
    classifications = las.classification
    unique_classes, counts = np.unique(classifications, return_counts=True)

    plt.bar(unique_classes, counts)
    plt.title("Point Count by Classification")
    plt.xlabel("Class")
    plt.ylabel("Count")
    # set ticks to be integers
    plt.show()

    points = np.vstack((las.x, las.y, las.z)).T
    colors = np.zeros_like(points)
    
    for cls, color in zip([6, 2], [[1, 0, 0], [0, 1, 0]]):
        mask = classifications == cls
        colors[mask] = color
    mask = np.logical_or.reduce((classifications == 3, classifications == 4, classifications == 5))
    colors[mask] = [0, 0, 1]

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--3d', 'three_d', is_flag=True, default=False, help="Calculate 3D density.")
@click.option('--ground-only', is_flag=True, default=False, help="Analyze ground points only.")
def density(input_file, three_d, ground_only):
    """Calculate point density of a LAS/LAZ file."""
    las = laspy.read(input_file)
    points = np.vstack((las.x, las.y, las.z)).T

    if ground_only:
        mask = las.classification == 2
        points = points[mask]

    if three_d:
        volume = np.ptp(points[:, 0]) * np.ptp(points[:, 1]) * np.ptp(points[:, 2])
        density = len(points) / volume
    else:
        area = np.ptp(points[:, 0]) * np.ptp(points[:, 1])
        density = len(points) / area

    chmura_punktow = o3d.geometry.PointCloud()

    if not three_d:
        # set zs to 0
        points[:, 2] = 0

    chmura_punktow.points = o3d.utility.Vector3dVector(points)

    click.echo(f"Density: {density:.2f} points per {'m^3' if three_d else 'm^2'}")
    neighbours_density: dict[int, int] = {}
    knn = o3d.geometry.KDTreeFlann(chmura_punktow)
    for point in points:
        [k, idx, _] = knn.search_radius_vector_3d(point, 1)
        k -= 1
        if k not in neighbours_density:
            neighbours_density[k] = 0
        neighbours_density[k] += 1

    print(neighbours_density[0])
    # create 2 lists out of the dict
    pair = list(neighbours_density.items())
    counts = [v for k, v in pair]
    neighbours_density_list = [k for k, v in pair]


    plt.bar(neighbours_density_list, counts)
    name = "Ground " if ground_only else ""
    name += "Point Count by Neighbours (3D)" if three_d else "Point Count by Neighbours (2D)"
    plt.title(name)
    plt.xlabel("Neighbours")
    plt.ylabel("Count")
    plt.show()



@cli.command()
@click.argument('input_file1', type=click.Path(exists=True))
@click.argument('input_file2', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
def difference(input_file1, input_file2, output_file):
    """Generate a difference raster from two LAS/LAZ files."""
    las = laspy.read(input_file1)
    # select only the ground points and write to a new file
    new_file = laspy.create(point_format=las.header.point_format, file_version=las.header.version)
    new_file.points = las.points[las.classification == 2]
    ground_name = "ground_nmt.las"
    new_file.write(ground_name)

    las = laspy.read(input_file2)
    # # where class is 2 or 3 or 4 or 5 or 6
    new_file = laspy.create(point_format=las.header.point_format, file_version=las.header.version)

    new_file.points = las.points[np.logical_or.reduce((las.classification == 2, las.classification == 3, las.classification == 4, las.classification == 5, las.classification == 6))]
    building_name = "building_nmpt.las"
    las.write(building_name)

    config = {
      "pipeline": [
        {
          "type": "readers.las",
          "filename": ground_name
        },
        {
          "type": "writers.gdal",
          "filename": "output.tif",
          "resolution": 1,
          "data_type": "float",
          "gdaldriver": "GTiff",
          "output_type": "mean",
          "spatialreference": "EPSG:2180"
        }
      ]
    }

    pipeline_str = json.dumps(config)
    # save to file
    pipeline_file = "config.json"
    with open(pipeline_file, "w") as f:
        f.write(pipeline_str)

    # Execute the PDAL pipeline
    command = f"pdal pipeline {pipeline_file}"
    subprocess.run(command, shell=True, check=True)

    config2 = {
      "pipeline": [
        {
          "type": "readers.las",
          "filename": building_name
        },
        {
          "type": "writers.gdal",
          "filename": "output2.tif",
          "resolution": 1,
          "data_type": "float",
          "gdaldriver": "GTiff",
          "output_type": "mean",
          "spatialreference": "EPSG:2180"
        }
      ]
    }

    pipeline_str2 = json.dumps(config2)
    # save to file
    pipeline_file2 = "config2.json"
    with open(pipeline_file2, "w") as f:
        f.write(pipeline_str2)
    # Execute the PDAL pipeline
    command2 = f"pdal pipeline {pipeline_file2}"
    subprocess.run(command2, shell=True, check=True)

    # read with rasterio
    with rasterio.open("output.tif") as src:
        data = src.read()

    with rasterio.open("output2.tif") as src:
        profile = src.profile
        data2 = src.read()

    # calculate difference with reduced dimensions
    dims1 = data.shape
    dims2 = data2.shape
    min_dims = tuple(min(d1, d2) for d1, d2 in zip(dims1, dims2))
    data = data[:, :min_dims[1], :min_dims[2]]
    data2 = data2[:, :min_dims[1], :min_dims[2]]
    diff = data - data2

    # save to file
    with rasterio.open(output_file, "w", **profile) as dst:
        dst.write(diff)


if __name__ == "__main__":
    cli()

