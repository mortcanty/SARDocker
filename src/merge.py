#!/usr/bin/env python
#******************************************************************************
#  Name:     merge.py
#  Purpose:  merge vv and vh single pol sequential SAR change maps
#   
#  Usage:     
#    import merge
#    merge.merge(VV_bmap,VH_bmap)
#              or 
#    python merge.py [OPTIONS] VV_bmap VH_bmap
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
import sys, getopt, gdal
from osgeo.gdalconst import GA_ReadOnly, GDT_Byte
import numpy as np

def merge(inbmapfn1,inbmapfn2):
    incmapfn1 = inbmapfn1.replace('bmap','cmap')
    incmapfn2 = inbmapfn2.replace('bmap','cmap')
    insmapfn1 = inbmapfn1.replace('bmap','smap')
    insmapfn2 = inbmapfn2.replace('bmap','smap')    
#  output file names
    outbmapfn = inbmapfn1.replace('VV','VVVH')
    outcmapfn = outbmapfn.replace('bmap','cmap')
    outsmapfn = outbmapfn.replace('bmap','smap')
    outfmapfn = outbmapfn.replace('bmap','fmap')
#  change map dimensions and georeferencing
    gdal.AllRegister()
    inDataset1 = gdal.Open(inbmapfn1,GA_ReadOnly)
    inDataset2 = gdal.Open(inbmapfn2,GA_ReadOnly)
    geotransform = inDataset1.GetGeoTransform()
    projection = inDataset1.GetProjection() 
    driver = inDataset1.GetDriver()
    cols = inDataset1.RasterXSize
    rows = inDataset1.RasterYSize    
    bands = inDataset1.RasterCount 
#  merge the VV and VH bmaps by inclusive OR
    bmap = np.zeros((rows,cols,bands),dtype=np.int16)
    for k in range(bands):
        vvband = inDataset1.GetRasterBand(k+1).ReadAsArray(0,0,cols,rows)
        vhband = inDataset2.GetRasterBand(k+1).ReadAsArray(0,0,cols,rows)
        bmap[:,:,k] = (vvband | vhband)/255  
    bmap = np.byte(bmap)  
#  merged frequency map
    fmap = np.sum(bmap,axis=2)
#  merged last change map
    inDataset1 = gdal.Open(incmapfn1,GA_ReadOnly)
    inDataset2 = gdal.Open(incmapfn2,GA_ReadOnly)
    tmp = np.zeros((rows,cols,2),dtype=np.byte)
    tmp[:,:,0] = inDataset1.GetRasterBand(1).ReadAsArray(0,0,cols,rows)
    tmp[:,:,1] = inDataset2.GetRasterBand(1).ReadAsArray(0,0,cols,rows)
    cmap = np.max(tmp,axis=2)
#  merged first change map
    inDataset1 = gdal.Open(insmapfn1,GA_ReadOnly)
    inDataset2 = gdal.Open(insmapfn2,GA_ReadOnly)
    tmp[:,:,0] = inDataset1.GetRasterBand(1).ReadAsArray(0,0,cols,rows)
    tmp[:,:,1] = inDataset2.GetRasterBand(1).ReadAsArray(0,0,cols,rows)
    smap = np.max(tmp,axis=2)    
#  write merged bmap to disk
    outDataset = driver.Create(outbmapfn,cols,rows,bands,GDT_Byte)
    if geotransform is not None:
        outDataset.SetGeoTransform(geotransform)        
    if projection is not None:
        outDataset.SetProjection(projection)
    for k in range(bands):        
        outBand = outDataset.GetRasterBand(k+1)
        outBand.WriteArray(bmap[:,:,k],0,0) 
        outBand.FlushCache()
    print 'bmap written to %s'%outbmapfn    
#  write merged cmap to disk
    outDataset = driver.Create(outcmapfn,cols,rows,1,GDT_Byte)
    if geotransform is not None:
        outDataset.SetGeoTransform(geotransform)        
    if projection is not None:
        outDataset.SetProjection(projection)   
    outBand = outDataset.GetRasterBand(1)
    outBand.WriteArray(cmap,0,0)
    outBand.FlushCache()
    print 'cmap written to %s'%outcmapfn    
#  write merged smap to disk
    outDataset = driver.Create(outsmapfn,cols,rows,1,GDT_Byte)
    if geotransform is not None:
        outDataset.SetGeoTransform(geotransform)        
    if projection is not None:
        outDataset.SetProjection(projection)   
    outBand = outDataset.GetRasterBand(1)
    outBand.WriteArray(smap,0,0) 
    outBand.FlushCache()
    print 'smap written to %s'%outsmapfn   
#  write merged fmap to disk
    outDataset = driver.Create(outfmapfn,cols,rows,1,GDT_Byte)
    if geotransform is not None:
        outDataset.SetGeoTransform(geotransform)        
    if projection is not None:
        outDataset.SetProjection(projection)   
    outBand = outDataset.GetRasterBand(1)
    outBand.WriteArray(fmap,0,0)  
    outBand.FlushCache()
    print 'fmap written to %s'%outfmapfn       
    outDataset = None

def main():
    usage = '''
Usage:
------------------------------------------------

python %s [OPTIONS] VV_bmap VH_bmap
       
merge VV and VH single pol sequential SAR  bitemporal change maps
writes combined cmap, smap, fmap and bmap to same directory
    
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
    merge(args[0],args[1])
    
    
if __name__ == '__main__':
    main()    