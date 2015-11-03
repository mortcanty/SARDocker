import numpy as np
import os, header, gdal
from osgeo.gdalconst import GDT_Float32

def read_emisar(fname):
#  read quadpol emisar files and return 9-band geotiff
#  for testing purposes
    gdal.AllRegister()
    path = os.path.dirname(fname)
    basename = os.path.basename(fname)
    root, _ = os.path.splitext(basename)   
    f = open(fname)
    hdr = header.Header()
    hdr.read(f.read())
    cols = int(hdr['samples'])
    rows = int(hdr['lines'])
    f.close()   
    driver = gdal.GetDriverByName('GTiff') 
    outfn = path+'/'+root+'.tif'     
    outDataset = driver.Create(outfn,cols,rows,9,GDT_Float32)  
    dtr = np.dtype(np.float32).newbyteorder('B')
    dtc = np.dtype(np.complex64).newbyteorder('B')
    fn = path+'/'+root+'hhhh'
    a = np.reshape(np.fromfile(fn,dtr),(rows,cols)) 
    a = np.rot90(a)
    outBand = outDataset.GetRasterBand(1)
    outBand.WriteArray(a.byteswap(),0,0) 
    outBand.FlushCache() 
    fn = path+'/'+root+'hhhv'             
    a = np.reshape(np.fromfile(fn,dtc),(rows,cols)) 
    a = np.rot90(a)
    outBand = outDataset.GetRasterBand(2)
    outBand.WriteArray(np.real(a).byteswap(),0,0) 
    outBand.FlushCache()  
    outBand = outDataset.GetRasterBand(3)
    outBand.WriteArray(np.imag(a).byteswap(),0,0)  
    outBand.FlushCache()          
    fn = path+'/'+root+'hhvv' 
    a = np.reshape(np.fromfile(fn,dtc),(rows,cols)) 
    a = np.rot90(a)
    outBand = outDataset.GetRasterBand(4)
    outBand.WriteArray(np.real(a).byteswap(),0,0)  
    outBand.FlushCache() 
    outBand = outDataset.GetRasterBand(5)
    outBand.WriteArray(np.imag(a).byteswap(),0,0) 
    outBand.FlushCache()  
    fn = path+'/'+root+'hvhv'    
    a = np.reshape(np.fromfile(fn,dtr),(rows,cols)) 
    a = np.rot90(a)
    outBand = outDataset.GetRasterBand(6)
    outBand.WriteArray(a.byteswap(),0,0) 
    outBand.FlushCache() 
    fn = path+'/'+root+'hvvv'  
    a = np.reshape(np.fromfile(fn,dtc),(rows,cols))
    a = np.rot90(a) 
    outBand = outDataset.GetRasterBand(7)
    outBand.WriteArray(np.real(a).byteswap(),0,0)  
    outBand.FlushCache() 
    outBand = outDataset.GetRasterBand(8)
    outBand.WriteArray(np.imag(a).byteswap(),0,0)  
    outBand.FlushCache() 
    fn = path+'/'+root+'vvvv' 
    a = np.reshape(np.fromfile(fn,dtr),(rows,cols)) 
    a = np.rot90(a)
    outBand = outDataset.GetRasterBand(9)
    outBand.WriteArray(a.byteswap(),0,0)  
    outBand.FlushCache() 
    outDataset = None
    print 'emisar data writen to %s'%outfn
    
if __name__=='__main__':
    read_emisar('/home/mort/imagery/sar/emisar/fl074_l.hdr')
    