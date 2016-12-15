#!/usr/bin/env python
#******************************************************************************
#  Name:     ingests1s2.py
#  Purpose:  Unpack and ingest time series of sentinel-1 vv, vh single pol 
#            SAR or VVVH dual pol diagonal only images 
#            exported from Earth Engine to and downloaded from from Google Drive 
#            to a series of 2-band images (dual pol diagonal only polarimetric matrix).
#            If present, also unpack and ingest a single 4-band sentinel-2 image downloaded
#            from earth engine in ZIP format. 
#   
#  Usage:     
#    import ingests1s2
#    ingests1s2.ingest(path,s1infile)
#              or 
#    python ingests1s2.py [OPTIONS] path 
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
from zipfile import ZipFile
from osgeo.gdalconst import GA_ReadOnly, GDT_Float32, GDT_Int16

def ingest(path,s1infile):
    print '========================='
    print '   Ingesting S1 (and S2)'
    print '========================='
    print time.asctime()  
    print 'Directory: %s'%path  
    print 'Sentinel-1 filename: %s'%s1infile   
    gdal.AllRegister()
    start = time.time()
    os.chdir(path)
    try:    
        files = os.listdir(path)
        for afile in files:
#          unpack VNIR archive in path       
            if re.search('.zip',afile):  
                ZipFile(afile).extractall(path)   
    #  get sorted list of VNIR files
        files = os.listdir(path)
        files1 = []
        for afile in files:
            if re.search('B[1-8].tif',afile):  
                files1.append(afile)
        if len(files1) > 0:
            files1.sort()        
            bands = len(files1)
            outfn = path+'sentinel2.tif' 
            inDataset = gdal.Open(files1[0],GA_ReadOnly)
            cols = inDataset.RasterXSize
            rows = inDataset.RasterYSize       
        #  ingest to a single file
            driver = gdal.GetDriverByName('GTiff') 
            outDataset = driver.Create(outfn,cols,rows,bands,GDT_Int16)
            projection = inDataset.GetProjection()
            geotransform = inDataset.GetGeoTransform()
            if geotransform is not None:
                outDataset.SetGeoTransform(geotransform)
            if projection is not None:
                outDataset.SetProjection(projection)    
            for i in range(bands):
                print 'writing band %i'%(i+1)
                inDataset = gdal.Open(files1[i])
                inBand = inDataset.GetRasterBand(1)
                band = inBand.ReadAsArray(0,0,cols,rows)
                outBand = outDataset.GetRasterBand(i+1)
                outBand.WriteArray(band)
                outBand.FlushCache()
                inDataset = None
                os.remove(files1[i].replace('.tif','.tfw'))
                os.remove(files1[i])
            outDataset = None   
            print 'created file %s' %outfn
#      ingest the SAR image to a time series of files                
        infile = path+s1infile
        inDataset = gdal.Open(infile,GA_ReadOnly) 
        driver = inDataset.GetDriver() 
        cols = inDataset.RasterXSize
        rows = inDataset.RasterYSize  
        bands = inDataset.RasterCount      
        if bands == 2:
#          dual pol diagonal only  
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
        else:
#          single pol VV or VH 
            for i in range(bands):
                outfile = path+'sentinel1_VV_%i.tif'%(i+1)            
                geotransform = inDataset.GetGeoTransform()
                projection = inDataset.GetProjection()
                outDataset = driver.Create(outfile,cols,rows,1,GDT_Float32)
                if geotransform is not None:
                    outDataset.SetGeoTransform(geotransform)        
                if projection is not None:
                    outDataset.SetProjection(projection)
                inArray = inDataset.GetRasterBand(i+1).ReadAsArray(0,0,cols,rows)
                outBand = outDataset.GetRasterBand(1)    
                outBand.WriteArray(inArray,0,0)
                outBand.FlushCache()
                outDataset = None
                print 'created file %s'%outfile                
        inDataset = None   
        print 'elapsed time: ' + str(time.time() - start)
    except Exception as e:
        print 'Error %s'%e         
        return None     

def main():
    usage = '''
Usage:
------------------------------------------------

python %s [OPTIONS] PATH S1_INFILENAME

     Unpack and ingest time series of sentinel-1 vv, vh single pol 
     SAR or VVVH dual pol diagonal only images 
     exported from Earth Engine to and downloaded from from Google Drive 
     to a series of 2-band images (dual pol diagonal only polarimetric matrix).
     If present, also unpack and ingest a single 4-band sentinel-2 image downloaded
     from earth engine in ZIP format. 

Options:

   -h    this help

--------------------------------------------'''%sys.argv[0]
    options,args = getopt.getopt(sys.argv[1:],'h')
    for option,_ in options: 
        if option == '-h':
            print usage
            return 
    if len(args) != 2:              
        print 'Incorrect number of arguments'
        print usage
        sys.exit(1)   
    ingest(args[0],args[1])
    
    
if __name__ == '__main__':
    main()    