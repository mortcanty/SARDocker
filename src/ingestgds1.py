#!/usr/bin/env python
#******************************************************************************
#  Name:     ingestgds1.py
#  Purpose:  ingest dual pol diagonal only sentinel-1 time series image exported to
#            and downloaded from Google Drive to a series of 2-band images 
#   
#  Usage:     
#    import ingestgds1
#    ingestgds1.ingest(path)
#              or 
#    python ingestsars1.py [OPTIONS] path 
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
import sys, getopt, gdal, os, re, time
from osgeo.gdalconst import GA_ReadOnly, GDT_Float32

def ingest(path):
    print '========================='
    print '     Ingest VVVH'
    print '========================='
    print time.asctime()  
    print 'Directory %s'%path 
    
    gdal.AllRegister()
    try:  
        files = os.listdir(path)
        for afile in files:
            if re.search('sentinel-1.tif',afile):   
                infile = afile
        infile = path+infile
        inDataset = gdal.Open(infile,GA_ReadOnly) 
        driver = inDataset.GetDriver() 
        cols = inDataset.RasterXSize
        rows = inDataset.RasterYSize  
        bands = inDataset.RasterCount      
        for i in range(bands/2):
            outfile = path+'sentinel1_VVVH_%i.tif'%(i+1)            
            geotransform = inDataset.GetGeoTransform()
            projection = inDataset.GetProjection()
            outDataset = driver.Create(outfile,cols,rows,2,GDT_Float32)
            if geotransform is not None:
                outDataset.SetGeoTransform(geotransform)        
            if projection is not None:
                outDataset.SetProjection(projection)
            inArray = inDataset.GetRasterBand(2*i+1).ReadAsArray(0,0,cols,rows)
            outBand = outDataset.GetRasterBand(1)    
            outBand.WriteArray(inArray,0,0)
            outBand.FlushCache()
            outBand = outDataset.GetRasterBand(2)
            inArray = inDataset.GetRasterBand(2*i+2).ReadAsArray(0,0,cols,rows)
            outBand.WriteArray(inArray,0,0) 
            outBand.FlushCache()
            outDataset = None
            print 'created file %s'%outfile
        inDataset = None   
    except Exception as e:
        print 'Error %s'%e 
        return None     

def main():
    usage = '''
Usage:
------------------------------------------------

python %s [OPTIONS] PATH

    ingest dual pol diagonal only sentinel-1 time series image exported to
    and downloaded from Google Drive to a series of 2-band images
    
Options:

   -h    this help

--------------------------------------------'''%sys.argv[0]
    options,args = getopt.getopt(sys.argv[1:],'h')
    for option,_ in options: 
        if option == '-h':
            print usage
            return 
    if len(args) != 1:              
        print 'Incorrect number of arguments'
        print usage
        sys.exit(1)   
    ingest(args[0])
    
    
if __name__ == '__main__':
    main()    