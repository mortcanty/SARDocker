#!/usr/bin/env python
#******************************************************************************
#  Name:     subset.py
#  Purpose:  spatial and spectral subsetting
#  Usage (from command line):             
#    python subset.py  [-d spatialDimensions] [-p spectral dimernsions] fileNmae
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
import numpy as np
import os, sys, getopt, time
from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly,GDT_Float32

def main(): 
    usage = '''Usage: python %s  [-d dims] [-p pos] fileName\n
            spatial and spectral dimensions are lists, e.g., -d [0,0,400,400] \n'''%sys.argv[0]
    options,args = getopt.getopt(sys.argv[1:],'hnd:p:')
    dims = None
    pos = None
    graphics = True
    for option, value in options: 
        if option == '-h':
            print usage
            return 
        elif option == '-n':
            graphics = False
        elif option == '-d':
            dims = eval(value)  
        elif option == '-p':
            pos = eval(value)
    gdal.AllRegister()
    infile = args[0] 
    path = os.path.dirname(infile)
    basename = os.path.basename(infile)
    root, ext = os.path.splitext(basename)
    outfile = path+'/'+root+'_sub'+ext    
    print '==========================='
    print 'Spatial/spectral subsetting'
    print '==========================='
    print time.asctime()     
    print 'Input %s'%infile
    start = time.time()    
    inDataset = gdal.Open(infile,GA_ReadOnly)
    try:                         
        cols = inDataset.RasterXSize
        rows = inDataset.RasterYSize    
        bands = inDataset.RasterCount
    except Exception as e:
        print 'Error: %s  -- Could not read in file'%e
        sys.exit(1)
    if dims:
        x0,y0,cols,rows = dims
    else:
        x0 = 0
        y0 = 0       
    if pos is not None:
        bands = len(pos)
    else:
        pos = range(1,bands+1)     
#   subset
    G = np.zeros((rows,cols,bands)) 
    k = 0                               
    for b in pos:
        band = inDataset.GetRasterBand(b)
        G[:,:,k] = band.ReadAsArray(x0,y0,cols,rows)\
                              .astype(float)
        k += 1         
#  write to disk       
    driver = inDataset.GetDriver() 
    outDataset = driver.Create(outfile,
                cols,rows,bands,GDT_Float32)
    projection = inDataset.GetProjection()
    geotransform = inDataset.GetGeoTransform()
    if geotransform is not None:
        gt = list(geotransform)
        gt[0] = gt[0] + x0*gt[1]
        gt[3] = gt[3] + y0*gt[5]
        outDataset.SetGeoTransform(tuple(gt))
    if projection is not None:
        outDataset.SetProjection(projection)        
    for k in range(bands):        
        outBand = outDataset.GetRasterBand(k+1)
        outBand.WriteArray(G[:,:,k],0,0) 
        outBand.FlushCache() 
    outDataset = None    
    inDataset = None        
    print 'result written to: %s'%outfile
    print 'elapsed time: %s'%str(time.time()-start) 
     
if __name__ == '__main__':
    main()    