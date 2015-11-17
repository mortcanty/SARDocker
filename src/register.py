 #!/usr/bin/env python
#  Name:  
#    register.py
#
#  Purpose:  
#    Perfrom image-image registration of two polarimetric SAR images 
#    via similarity warping. Assumes 9-band quad pol, 4-band dual pol
#    or one-band single pol SAR images.
#
#  Usage:     
#    import register
#    register.register(reffilename,warpfilename,dims,outfile) 
#          or        
#    python register.py [-h] [-d dims] reffilename warpfilename
#
#  Copyright (c) 2015, Mort Canty
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

import auxil.auxil as auxil
import os, sys, getopt, time
import numpy as np
from osgeo import gdal
import scipy.ndimage.interpolation as ndii
from osgeo.gdalconst import GA_ReadOnly, GDT_Float32
  
def register(file0, file1, dims=None, outfile=None): 
    print '========================='
    print '     Register SAR'
    print '========================='
    print time.asctime()      
    try: 
        if outfile == None:
            path = os.path.abspath(file1)    
            dirn = os.path.dirname(path)
            path = os.path.dirname(file1)    
            basename = os.path.basename(file1)
            root, ext = os.path.splitext(basename)
            outfile = dirn + '/' + root + '_warp' + ext  
        start = time.time()   
        gdal.AllRegister()
    #  reference    
        inDataset0 = gdal.Open(file0, GA_ReadOnly)     
        cols = inDataset0.RasterXSize
        rows = inDataset0.RasterYSize
        bands = inDataset0.RasterCount
        print 'Reference image: %s' % file0   
        if dims == None:
            dims = [0,0,cols,rows]
        x0,y0,cols,rows = dims 
    #  target                   
        inDataset1 = gdal.Open(file1, GA_ReadOnly)   
        cols1 = inDataset1.RasterXSize
        rows1 = inDataset1.RasterYSize  
        bands1 = inDataset1.RasterCount
        print 'Target image: %s' % file1      
        if  bands != bands1:
            print 'Number of bands must be equal'
            return 0
    #  create the output file 
        driver = inDataset1.GetDriver() 
        outDataset = driver.Create(outfile,cols,rows,bands,GDT_Float32)
        projection0 = inDataset0.GetProjection()
        geotransform0 = inDataset0.GetGeoTransform()
        geotransform1 = inDataset1.GetGeoTransform()
        gt0 = list(geotransform0)               
        gt1 = list(geotransform1)    
        if projection0 is not None:
            outDataset.SetProjection(projection0)                          
    #  find the upper left corner (x0,y0) of reference subset in target (x1,y1)    
        ulx0 = gt0[0] + x0*gt0[1] + y0*gt0[2]
        uly0 = gt0[3] + x0*gt0[4] + y0*gt0[5]
        GT1 = np.mat([[gt1[1],gt1[2]],[gt1[4],gt1[5]]])
        ul1 = np.mat([[ulx0-gt1[0]],[uly0-gt1[3]]])
        tmp = GT1.I*ul1
        x1 = int(round(tmp[0,0]))
        y1 = int(round(tmp[1,0]))
    #  create output geotransform 
        gt1 = gt0   
        gt1[0] = ulx0 
        gt1[3] = uly0   
        outDataset.SetGeoTransform(tuple(gt1)) 
    #  get matching subsets from geotransform     
        rasterBand = inDataset0.GetRasterBand(1)   
        span0 = rasterBand.ReadAsArray(x0, y0, cols, rows)
        rasterBand = inDataset1.GetRasterBand(1)
        span1 = rasterBand.ReadAsArray(x1, y1, cols, rows)
        if bands == 9:
    #      get warp parameters using span images         
            print 'warping 9 bands (quad pol)...' 
            rasterBand = inDataset0.GetRasterBand(6)
            span0 += rasterBand.ReadAsArray(x0, y0, cols, rows)
            rasterBand = inDataset0.GetRasterBand(9)
            span0 += rasterBand.ReadAsArray(x0, y0, cols, rows)  
            span0 = np.log(np.nan_to_num(span0)+0.001)                                   
            rasterBand = inDataset1.GetRasterBand(6)
            span1 += rasterBand.ReadAsArray(x1, y1, cols, rows)
            rasterBand = inDataset1.GetRasterBand(9)
            span1 += rasterBand.ReadAsArray(x1, y1, cols, rows)  
            span1 = np.log(np.nan_to_num(span1)+0.001)                           
            scale, angle, shift = auxil.similarity(span0, span1)   
    #      warp the target to the reference and clip
            for k in range(9): 
                rasterBand = inDataset1.GetRasterBand(k+1)
                band = rasterBand.ReadAsArray(0, 0, cols1, rows1).astype(np.float32)
                bn1 = np.nan_to_num(band)                  
                bn2 = ndii.zoom(bn1, 1.0 / scale)
                bn2 = ndii.rotate(bn2, angle)
                bn2 = ndii.shift(bn2, shift)
                bn = bn2[y1:y1+rows,x1:x1+cols] 
                outBand = outDataset.GetRasterBand(k+1)
                outBand.WriteArray(bn)
                outBand.FlushCache()
        elif bands == 4:
    #      get warp parameters using span images         
            print 'warping 4 bands (dual pol)...' 
            rasterBand = inDataset0.GetRasterBand(4)
            span0 += rasterBand.ReadAsArray(x0, y0, cols, rows)
            span0 = np.log(np.nan_to_num(span0)+0.001)                                   
            rasterBand = inDataset1.GetRasterBand(4)
            span1 += rasterBand.ReadAsArray(x1, y1, cols, rows)
            span1 = np.log(np.nan_to_num(span1)+0.001)                           
            scale, angle, shift = auxil.similarity(span0, span1)   
    #      warp the target to the reference and clip
            for k in range(4): 
                rasterBand = inDataset1.GetRasterBand(k+1)
                band = rasterBand.ReadAsArray(0, 0, cols1, rows1).astype(np.float32)
                bn1 = np.nan_to_num(band)                  
                bn2 = ndii.zoom(bn1, 1.0 / scale)
                bn2 = ndii.rotate(bn2, angle)
                bn2 = ndii.shift(bn2, shift)
                bn = bn2[y1:y1+rows,x1:x1+cols] 
                outBand = outDataset.GetRasterBand(k+1)
                outBand.WriteArray(bn)
                outBand.FlushCache()           
        elif bands == 1:
     #      get warp parameters using span images         
            print 'warping 1 band (single pol)...' 
            span0 = np.log(np.nan_to_num(span0)+0.001)                                   
            span1 = np.log(np.nan_to_num(span0)+0.001)                           
            scale, angle, shift = auxil.similarity(span0, span1)   
    #      warp the target to the reference and clip
            for k in range(1): 
                rasterBand = inDataset1.GetRasterBand(k+1)
                band = rasterBand.ReadAsArray(0, 0, cols1, rows1).astype(np.float32)
                bn1 = np.nan_to_num(band)                  
                bn2 = ndii.zoom(bn1, 1.0 / scale)
                bn2 = ndii.rotate(bn2, angle)
                bn2 = ndii.shift(bn2, shift)
                bn = bn2[y1:y1+rows,x1:x1+cols] 
                outBand = outDataset.GetRasterBand(k+1)
                outBand.WriteArray(bn)
                outBand.FlushCache()           
        inDataset0 = None
        inDataset1 = None
        outDataset = None    
        print 'elapsed time: ' + str(time.time() - start)   
        return outfile
    except Exception as e:
        print 'register failed: %s'%e    
        return None     
    
def main(): 
    usage = '''
Usage:
------------------------------------------------
    python %s [-h] [-d DIMS] reffilename warpfilename
    
    
    Perform image-image registration of two polarimetric SAR images 
    via similarity warping. Assumes 9-band quad pol, 4-band dual pol
    or one-band single pol SAR images.
    NOTE: Both images must completely include the spatial subset DIMS
--------------------------------------------'''%sys.argv[0]

    options,args = getopt.getopt(sys.argv[1:],'hd:')
    dims = None
    for option, value in options: 
        if option == '-h':
            print usage
            return 
        elif option == '-d':
            dims = eval(value)         
    if len(args) != 2:
        print 'Incorrect number of arguments'
        print usage
        sys.exit(1)        
    fn0 = args[0]
    fn1 = args[1]
    outfile = register(fn0,fn1,dims)
    if outfile is not None:
        print 'Warped image written to: %s' % outfile  

if __name__ == '__main__':
    main()    
