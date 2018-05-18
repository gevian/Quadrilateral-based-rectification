__author__ = 'Magnus Heitzler'

import numpy as np
from numpy import linalg

import cv2, fiona, json, ast
from shapely.geometry import Point, mapping
from sklearn.cluster import DBSCAN

           

class intersections():
    def deserialize(location):
        intersectionPoints = []
        xRange = 0
        yRange = 0
        with fiona.open(location) as intersections:
            for intersection in intersections:
                fromImgX = intersection["geometry"]["coordinates"][0]
                fromImgY = -intersection["geometry"]["coordinates"][1]
                xid = int(intersection["properties"]["xid"])
                yid = int(intersection["properties"]["yid"])

                intersectionPoints.append({
                    "fromImgX" : fromImgX,
                    "fromImgY" : fromImgY,
                    "xid" : xid,
                    "yid" : yid
                })


                if xid > xRange:
                    xRange = int(intersection["properties"]["xid"])

                if yid > yRange:
                    yRange = int(intersection["properties"]["yid"])

        points = []
        for y in range(yRange + 1):
            yList = []
            for x in range(xRange + 1):
                yList.append([])

            points.append(yList)


        for iP in intersectionPoints:
            points[iP["yid"]][iP["xid"]] = {"fromImgX" : iP["fromImgX"], "fromImgY" : iP["fromImgY"]}


        return points




class coordinates:
    def deserialize(location):

        cI = {}
        coordinates = fiona.open(location, 'r', 'ESRI Shapefile')
        for coordinate in coordinates:
            props = coordinate["properties"]
            if props["pos"] == "top":
                cI["ct"] = float(props["coords"])
                cI["ot"] = props["dir"]

            elif props["pos"] == "bottom":
                cI["cb"] = float(props["coords"])
                cI["ob"] = props["dir"]

            elif props["pos"] == "left":
                cI["cl"] = float(props["coords"])
                cI["ol"] = props["dir"]

            elif props["pos"] == "right":
                cI["cr"] = float(props["coords"])
                cI["or"] = props["dir"]


        return cI





    def assign(points, cI, roundTo = 250):
        yRange = range(len(points))
        xRange = range(len(points[0]))

        xMinWorld = cI["cl"]
        xMaxWorld = cI["cr"]
        yMinWorld = cI["ct"]
        yMaxWorld = cI["cb"]

        for y in yRange:
            xMin = points[y][0]["fromImgX"]
            xMax = points[y][-1]["fromImgX"]

            for x in xRange:
                xPoint = points[y][x]
                xNorm = (xPoint["fromImgX"] - xMin) / (xMax - xMin)
                xWorld = xMinWorld + xNorm * (xMaxWorld - xMinWorld)
                points[y][x]["fromImgWorldX"] = int(roundTo * round(float(xWorld)/roundTo)) # round to nearest "roundTo"


        for x in xRange:
            yMin = points[0][x]["fromImgY"]
            yMax = points[-1][x]["fromImgY"]

            for y in yRange:
                yPoint = points[y][x]
                yNorm = (yPoint["fromImgY"] - yMin) / (yMax - yMin)
                yWorld = yMinWorld + yNorm * (yMaxWorld - yMinWorld)
                points[y][x]["fromImgWorldY"] = int(roundTo * round(float(yWorld)/roundTo)) # round to nearest "roundTo"



        return points



    def transform(cI, transformation="Siegfried2LV95"):
        
        if transformation == "Siegfried2LV95":
            cILV95 = {}

            LV95FalseEasting = 2600000
            LV95FalseNorthing = 1200000

            if cI["ol"] == "W":
                  cILV95["cl"] = LV95FalseEasting - cI["cl"]
            elif cI["ol"] == "O":
                  cILV95["cl"] = LV95FalseEasting + cI["cl"]

            if cI["or"] == "W":
                  cILV95["cr"] = LV95FalseEasting - cI["cr"]
            elif cI["or"] == "O":
                  cILV95["cr"] = LV95FalseEasting + cI["cr"]

            if cI["ot"] == "N":
                  cILV95["ct"] = LV95FalseNorthing + cI["ct"]
            elif cI["ot"] == "S":
                  cILV95["ct"] = LV95FalseNorthing - cI["ct"]

            if cI["ob"] == "N":
                  cILV95["cb"] = LV95FalseNorthing + cI["cb"]
            elif cI["ob"] == "S":
                  cILV95["cb"] = LV95FalseNorthing - cI["cb"]

            return cILV95, 2056
        
        else:
           return None, None
        
        
        
        
        
        
        
