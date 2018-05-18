__author__ = 'Magnus Heitzler'

import sys, cv2, gdal, argparse
import numpy as np

from gdalconst import *
from osgeo import osr

from quadrilateralInterpolation import rectifyVectorized, rectify, rectifyVectorizedBilinear
from utils import intersections as _intersections, coordinates as _coordinates


def georeferenceImg(path, rectifiedImg, west, north, resolution, epsg, format = 'GTiff'):
    print("Writing image to " + path + ".")
    
    driver = gdal.GetDriverByName(format)
    ds = driver.Create(path, rectifiedImg.shape[1], rectifiedImg.shape[0], 3, GDT_Byte)

    ds.GetRasterBand(1).WriteArray(rectifiedImg[:,:,2])
    ds.GetRasterBand(2).WriteArray(rectifiedImg[:,:,1])
    ds.GetRasterBand(3).WriteArray(rectifiedImg[:,:,0])

    simpleGeoTransform = (west, resolution, 0.0, north, 0.0, -1*resolution)
    ds.SetGeoTransform(simpleGeoTransform)

    target_crs = osr.SpatialReference()
    target_crs.ImportFromEPSG(epsg)

    ds.SetProjection(target_crs.ExportToWkt())
    ds = None




def rectifyMap(fromImg, points, method):
    print("Rectifying image ... ")
    
    numPointY = len(points)
    numPointX = len(points[0])

    left   = points[0][0]["toImgX"]
    top    = points[0][0]["toImgY"]
    right  = points[numPointY-1][numPointX-1]["toImgX"]
    bottom = points[numPointY-1][numPointX-1]["toImgY"]

    toImgWidth  = (right - left)
    toImgHeight = (bottom - top)

    toImg = np.zeros([toImgHeight, toImgWidth, 3],dtype=np.uint8)


    for y in range(numPointY-1):
        for x in range(numPointX-1):
            print(" ... cell index: " + str(y+1) + "/" + str(x+1) + " of " + str(numPointY-1) + "/" + str(numPointX-1) + " ... ")
            point1 = points[y+1][x]
            point2 = points[y+1][x+1]
            point3 = points[y][x+1]
            point4 = points[y][x]

            px = np.asarray([point1["fromImgX"], point2["fromImgX"], point3["fromImgX"], point4["fromImgX"]])
            py = np.asarray([point1["fromImgY"], point2["fromImgY"], point3["fromImgY"], point4["fromImgY"]])

            patchWidth  = point3["toImgX"] - point4["toImgX"]
            patchHeight = point1["toImgY"] - point4["toImgY"]

            if method == "nearest":
                rectifiedImg = rectifyVectorized(fromImg, px, py, patchWidth, patchHeight)
            else:
                rectifiedImg = rectifyVectorizedBilinear(fromImg, px, py, patchWidth, patchHeight)

            toImg[point4["toImgY"]:point1["toImgY"],point1["toImgX"]:point2["toImgX"]] = rectifiedImg.copy()

    print(" ... finished.")
    return toImg




def calculateToImgCoordinates(points, resolution = 1.25):
    print("Calculating target image coordinates with resolution " + str(resolution) + " m/pixel.")

    numPointY = len(points)
    numPointX = len(points[0])


    left   = points[0][0]["fromImgWorldX"]
    top    = points[0][0]["fromImgWorldY"]
    

    for y in range(numPointY):
        for x in range(numPointX):
            p = points[y][x]
            pLeft = p["fromImgWorldX"]
            pTop  = p["fromImgWorldY"]

            diffLeft = (pLeft - left) / resolution
            diffTop  = (top   - pTop) / resolution

            p["toImgX"] = int(round(diffLeft))
            p["toImgY"] = int(round(diffTop))



def execute(inputImage, outputImage, intersections, coordinates, resolution = 1.25, minOffset = 250, method="bilinear", transformation="Siegfried2LV95"):
    points = _intersections.deserialize(intersections)
    
    cI = _coordinates.deserialize(coordinates)    
    coordinateInformation, epsg = _coordinates.transform(cI, transformation)
        
    pointsAssigned = _coordinates.assign(points, coordinateInformation, minOffset)
        
    fromImg = cv2.imread(inputImage)

    calculateToImgCoordinates(pointsAssigned, resolution)

    toImg = rectifyMap(fromImg, pointsAssigned, method)

    georeferenceImg(outputImage, toImg, coordinateInformation["cl"], coordinateInformation["ct"], resolution, epsg, format = 'GTiff')



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Quadrilateral-based interpolation for georeferencing historical maps.")
    
    parser.add_argument("inputImage", help="path to the scanned map sheet")
    parser.add_argument("outputImage", help="path to the resulting, georeferenced map sheet")
    parser.add_argument("intersections", help="path to the grid intersections")
    parser.add_argument("coordinates", help="path to the grid coordinates")
    parser.add_argument("-r", "--resolution", help="resampling resolution of the output image", type=float, default=1.25)
    parser.add_argument("-o", "--minOffset", help="minimum distance of neighboring grid lines", type=float, default=250.0)
    parser.add_argument("-m", "--method", help="resampling method", type=str, choices=["nearest", "bilinear"], default="bilinear")
    parser.add_argument("-t", "--transformation", help="name of the coordinate transformation", type=str, choices=["Siegfried2LV95"], default="Siegfried2LV95")
    
    args = parser.parse_args()

    execute(**vars(args))
    
    
    
    
    
    
    
    
    