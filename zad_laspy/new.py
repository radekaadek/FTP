import click
import laspy
import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt

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
    plt.gca().set_yticks(np.arange(0, max(counts) + 1, 1))
    plt.gca().set_xticks(np.arange(0, len(unique_classes), 1))
    plt.show()

    points = np.vstack((las.x, las.y, las.z)).T
    colors = np.zeros_like(points)
    
    for cls, color in zip([6, 2, 3], [[1, 0, 0], [0, 1, 0], [0, 0, 1]]):
        mask = classifications == cls
        colors[mask] = color

    visualize_3d(points, colors, title="3D Visualization by Class")

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
        # remove third dimension from points
        points = points[:, :2]

    chmura_punktow = o3d.geometry.PointCloud()
    if three_d:
        chmura_punktow.points = o3d.utility.Vector3dVector(points)
    else:
        chmura_punktow.points = o3d.utility.Vector2dVector(points)

    click.echo(f"Density: {density:.2f} points per {'m^3' if three_d else 'm^2'}")
    neighbours_density: dict[int, int] = {}
    knn = o3d.geometry.KDTreeFlann(chmura_punktow)
    for point in points:
        [k, idx, _] = knn.search_radius_vector_3d(point, 1)
        print(f"len(idx): {len(idx)}")
        if k not in neighbours_density:
            neighbours_density[k] = 0
        neighbours_density[k] += len(idx)

    # create 2 lists out of the dict
    pair = list(neighbours_density.items())
    counts = [v for k, v in pair]
    neighbours_density_list = [k for k, v in pair]


    plt.bar(neighbours_density_list, counts)
    plt.title("Point Count by Neighbours")
    plt.xlabel("Neighbours")
    plt.ylabel("Count")
    plt.show()



@cli.command()
@click.argument('input_file1', type=click.Path(exists=True))
@click.argument('input_file2', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
def difference(input_file1, input_file2, output_file):
    """Generate a difference raster from two LAS/LAZ files."""
    def generate_raster(las, classification, resolution=1):
        mask = las.classification == classification
        x, y, z = las.x[mask], las.y[mask], las.z[mask]

        xmin, ymin = np.floor([np.min(x), np.min(y)])
        xmax, ymax = np.ceil([np.max(x), np.max(y)])

        xbins = np.arange(xmin, xmax + resolution, resolution)
        ybins = np.arange(ymin, ymax + resolution, resolution)

        grid, _, _ = np.histogram2d(x, y, bins=[xbins, ybins], weights=z)
        counts, _, _ = np.histogram2d(x, y, bins=[xbins, ybins])
        return grid / np.maximum(counts, 1)

    las1 = laspy.read(input_file1)
    las2 = laspy.read(input_file2)

    nmt1 = generate_raster(las1, 2)
    nmt2 = generate_raster(las2, 2)

    difference_raster = nmt2 - nmt1

    import rasterio
    from rasterio.transform import from_origin

    rows, cols = difference_raster.shape
    transform = from_origin(np.min(las1.x), np.max(las1.y), 1, 1)

    with rasterio.open(
        output_file,
        'w',
        driver='GTiff',
        height=rows,
        width=cols,
        count=1,
        dtype=difference_raster.dtype,
        crs='+proj=latlong',
        transform=transform,
    ) as dst:
        dst.write(difference_raster, 1)

    click.echo(f"Difference raster saved to {output_file}")

    click.echo(f"Difference raster saved to {output_file}")

if __name__ == "__main__":
    cli()

