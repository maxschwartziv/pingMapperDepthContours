import matplotlib.pyplot as plt
import csv
import matplotlib.tri as tri
import cv2
from osgeo import gdal, osr

humminbirdDataPath = 'meta\B001_ds_highfreq_meta.csv'

x = []
y = []
z = []
with open(humminbirdDataPath, 'r') as csvfile:
    plots = csv.reader(csvfile, delimiter=',')
    next(plots) # skip header
    for (row) in plots:
        x.append(float((row)[20]))
        y.append(float((row)[21]))
        z.append(float((row)[8]))
csvfile.close()

latmin = min(x)
latmax = max(x)
lngmin = min(y)
lngmax = max(y)
shallowest = min(z)
deepest = max(z)

npts = 150
ngridx = 150
ngridy = 150

colorMap="gist_rainbow"

fig = plt.figure(frameon=False)
ax = fig.add_axes([0, 0, 1, 1])

cntr = ax.tricontourf(x, y, z, levels=20, cmap = colorMap) #depth points into mesh grid
cntr = ax.tricontour(x, y, z, levels=20, colors='k', linewidths=0.5)
clabels = ax.clabel(cntr, fmt='%2.1f', colors='w', levels = cntr.levels[::2], 
                    fontsize=10, inline=True, inline_spacing=5) #label every other contour

#[txt.set_backgroundcolor('white') for txt in clabels] #changes background color of labels
#[txt.set_bbox(dict(facecolor='white', edgecolor='none', pad=0)) for txt in clabels] #smaller bbox around labels

ax.plot(x, y, 'ko', ms=0) #ms = positive for tracklines
ax.axis('off')
plt.savefig("depthmap.png", dpi=220)



# Define the input and output file paths
input_file = "depthmap.png"
output_file = "output_with_gcps.tif"
warped_output_file = "output_warped.tif"

# Read the image to get its dimensions
img = cv2.imread(input_file, cv2.IMREAD_UNCHANGED)
height, width = img.shape[:2]
print("Image dimensions - Height:", height, "Width:", width)

# Open the input file as a GDAL dataset
ds = gdal.Open(input_file, gdal.GA_ReadOnly)

# Set spatial reference (WGS84 in decimal degrees)
sr = osr.SpatialReference()
sr.ImportFromEPSG(4326)  # EPSG:4326 corresponds to WGS84 in decimal degrees

# Define GCPs (map coordinates in decimal degrees and corresponding image pixel coordinates)
gcps = [
    gdal.GCP(latmin, lngmax, 0, 0, 0),  # Top-left corner
    gdal.GCP(latmin, lngmin, 0, 0, height),  # Bottom-left corner
    gdal.GCP(latmax, lngmax, 0, width, 0),  # Top-right corner
    gdal.GCP(latmax, lngmin, 0, width, height)  # Bottom-right corner
]

# Apply the GCPs to the dataset and save as GeoTIFF
ds_with_gcps = gdal.Translate(
    output_file,
    ds,
    GCPs=gcps,
    outputSRS=sr.ExportToWkt(),
    format="GTiff"
)

# Close the dataset
ds_with_gcps = None
print(f"GeoTIFF with GCPs saved: {output_file}")

# Warp the image to create a geotransform (required for Google Earth)
gdal.Warp(
    warped_output_file,
    output_file,
    dstSRS="EPSG:4326"
)
print(f"Warped GeoTIFF saved: {warped_output_file}")

# Optional: Print GeoTIFF metadata for verification
gdalinfo = gdal.Info(warped_output_file)
print(gdalinfo)






