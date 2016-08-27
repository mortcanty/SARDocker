#!/usr/bin/env python
#******************************************************************************
#  Name:     mergevvvh.py
#  Purpose:  merge time series of vv and vh single pol SAR images to a series
#            of 2-band images (dual pol diagonal only polarimetric matrix)
#   
#  Usage:     
#    import mergevvvh
#    mergevvvh.merge(VV_bmap,VH_bmap)
#              or 
#    python mergevvvh.py [OPTIONS] path 
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

def merge(path):
    print '========================='
    print '     Merge VV and VH'
    print '========================='
    print time.asctime()  
    print 'Directory %s'%path 
    
    gdal.AllRegister()
    try:
    #  get sorted lists of VV and VH files    
        files = os.listdir(path)
        vvfiles = []
        vhfiles = []
        for afile in files:
            if re.search('\.VV_[0-9]{1,2}\.tif',afile):   
                vvfiles.append(afile)
            elif re.search('\.VH_[0-9]{1,2}\.tif',afile): 
                vhfiles.append(afile)
        if (len(vvfiles) != len(vhfiles)) or (len(vvfiles)==0) :
            raise Exception('file mismatch or no files found')
        os.chdir(path)
        vvfiles.sort()
        vhfiles.sort()
        inDataset1 = gdal.Open(vvfiles[0],GA_ReadOnly) 
        driver = inDataset1.GetDriver() 
        cols = inDataset1.RasterXSize
        rows = inDataset1.RasterYSize        
        for i in range(len(vvfiles)):
            outfile = vvfiles[i].replace('VV','VVVH')
            inDataset1 = gdal.Open(vvfiles[i],GA_ReadOnly)  
            inDataset2 = gdal.Open(vhfiles[i],GA_ReadOnly)   
            geotransform = inDataset1.GetGeoTransform()
            projection = inDataset1.GetProjection()
            outDataset = driver.Create(outfile,cols,rows,2,GDT_Float32)
            if geotransform is not None:
                outDataset.SetGeoTransform(geotransform)        
            if projection is not None:
                outDataset.SetProjection(projection)
            inArray = inDataset1.GetRasterBand(1).ReadAsArray(0,0,cols,rows)
            outBand = outDataset.GetRasterBand(1)    
            outBand.WriteArray(inArray,0,0)
            outBand.FlushCache()
            outBand = outDataset.GetRasterBand(2)
            inArray = inDataset2.GetRasterBand(1).ReadAsArray(0,0,cols,rows)
            outBand.WriteArray(inArray,0,0) 
            outBand.FlushCache()
            print '%s and %s merged to %s'%(vvfiles[i],vhfiles[i],outfile) 
        inDataset1 = None
        inDataset2 = None
        outDataset = None     
        for i in range(len(vvfiles)):
            os.remove(vvfiles[i].replace('.tif','.tfw'))
            os.remove(vhfiles[i].replace('.tif','.tfw'))
            os.remove(vvfiles[i])
            os.remove(vhfiles[i])
    except Exception as e:
        print 'Error %s'%e 
        return None     

def main():
    usage = '''
Usage:
------------------------------------------------

python %s [OPTIONS] PATH

    merge time series of vv and vh single pol SAR images in PATH
    to a series of 2-band images (dualpol diagonal only polarimetric matrix)
    
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
    merge(args[0])
    
    
if __name__ == '__main__':
    main()    