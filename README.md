# WDSS2 Python Library

The beginnings of a Python library and ArcToolbox collection for working with [National Severe Storms Laboratory] (http://www.nssl.noaa.gov/) and [WDSSII data sets] (http://www.wdssii.org/).  Basically at NSSL, there are custom internal dataset formats for Raster grids and Polar data.  This is mostly for speed purposes, because we deal with very large datasets for multiphase radar research, where we have particular needs not met by other standard formats. To display this stuff, we use a custom GUI called the WDSSII GUI, or another experimental one called [WG2] (https://github.com/retoomey/wg2). I haven't done the readme for the WG2 port to github yet, that can still be found on google code at (WG2 Google Code)[https://code.google.com/p/wg2].  Anyway, the problem of course is that these are custom data formats.  If you're wanting to create an awesome and accurate picture of your data for a poster or paper, maybe using a particular projection, or mixing with custom maps..then you want to be able to use that data quickly and easily within a GIS system.  ArcMap is a great system for doing that, so this library will work towards making that easy and convenient for you.

## Current Status/Features

* Import LatLonGrid NetCDF file to ArcGIS Raster, optionally generating a PNG CONUS image with USA map and HTML file.
* Allow the inclusion of our toolbox scripts into a standard ArcGIS model builder. (Still need to test this..it should work)

## Requirements

* ArcGIS (arcpy library)
* [Scientific Python] (http://www.scipy.org) for the fast NetCDF reader.  You really want this, the ArcGIS one is slow as snails.

## Getting Started

Basically for now, it is designed to be used by creating a standard folder connection within ArcGIS.
Two ways to play with it
* Download the zipfile from the [Downloads](https://github.com/retoomey/WDSS2Python/archive/master.zip).  Create a folder connection in ArcToolbox or ArcMap to the WDSS2Python-master folder, and open the NSSL WDSS2 Tools python toolbox.  Inside will be the basic toolboxes for working with data.
* Checkout the source: `git clone git://github.com/retoomey/WDSS2Python.git` to modify.  You can still connect to the project folder from ArcToolbox, and change or add to the code.

## Future goals

* Add NSSL RadialSets and XML tables for import.  RadialSets have all that polar math, attenuation, etc.  So that will be a fun add-on.
* Maybe add export ability from Raster to Netcdf, allowing you to work with and output new NetCDF files.
* Currently depends on Arcpy to run.  As the library grows, it could gain non-arcpy related tools.