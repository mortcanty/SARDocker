#!/usr/bin/env python
#******************************************************************************
#  Name:  ingestvnir.py
#  Purpose:
#    utility to ingest georeferenced VNIR bands downloaded from Earth Engine 
#    and convert to a single mult-band image
#
#   Usage:
#   import ingestvnir
#   ingestvnir.ingest(path)
#        or
#   python ingestvnir.py [-h] indir
#
# MIT License
# 
# Copyright (c) 2016 Mort Canty
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os, re, sys, getopt, time
from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly, GDT_Int16

def ingest(path):    
    print '========================='
    print '     Ingest VNIR'
    print '========================='
    print time.asctime()  
    print 'Directory %s'%path 
    
    start = time.time()
    try:
    #  get sorted list of VNIR files    
        files1 = os.listdir(path)
        files = []
        for afile in files1:
            if re.search('B[1-8].tif',afile):  
                files.append(afile)
        files.sort()        
        bands = len(files)
    #  get image dimensions
        outfn = 'VNIR.tif'
        gdal.AllRegister()   
        inDataset = gdal.Open(files[0],GA_ReadOnly)
        cols = inDataset.RasterXSize
        rows = inDataset.RasterYSize       
    #  create the output file
        driver = gdal.GetDriverByName('GTiff') 
        outDataset = driver.Create(outfn,cols,rows,bands,GDT_Int16)
        projection = inDataset.GetProjection()
        geotransform = inDataset.GetGeoTransform()
        if geotransform is not None:
            outDataset.SetGeoTransform(geotransform)
        if projection is not None:
            outDataset.SetProjection(projection)
        inDataset = None     
    #  ingest
        for i in range(bands):
            print 'writing band %i'%(i+1)
            inDataset = gdal.Open(files[i])
            inBand = inDataset.GetRasterBand(1)
            band = inBand.ReadAsArray(0,0,cols,rows)
            outBand = outDataset.GetRasterBand(i+1)
            outBand.WriteArray(band)
            outBand.FlushCache()
            inDataset = None
            os.remove(files[i])
        outDataset = None 
        print 'elapsed time: ' + str(time.time() - start)
        return outfn
    except Exception as e:
        print 'Error %s  --Image could not be read in'%e 
        return None     
     
    
def main():
    usage = '''
Usage:
------------------------------------------------

python %s [OPTIONS] indir

Options:

   -h     this help

indir: directory containing the geo-referenced VNIR bands 
downloaded from GEE

------------------------------------------------''' %sys.argv[0]

    options, args = getopt.getopt(sys.argv[1:],'h')  
    for option, _ in options:
        if option == '-h':
            print usage
            return        
    if len(args) != 1:
        print 'Incorrect number of arguments'
        print usage
        sys.exit(1)  
    os.chdir(args[0])
    if os.path.isfile('VNIR.tif'):
        print 'Overwriting previous combined image'
    outfn = ingest(args[0])
    if outfn is not None:
        print 'Multiband image written to %s'%(args[0]+outfn)
    
if __name__ == '__main__':
    main()
    