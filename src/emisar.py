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
    outfn = '/home/imagery/'+root+'.tif'     
    outDataset = driver.Create(outfn,cols,rows,9,GDT_Float32)  
    dtr = np.dtype(np.float32).newbyteorder('B')
    dtc = np.dtype(np.complex64).newbyteorder('B')
    fn = path+'/'+root+'hhhh.emi'
#    a = np.reshape(np.fromfile(fn,dtr),(rows,cols))
    a = np.reshape(np.fromfile(fn,dtr)[1024::],(rows,cols)) # 4096 byte offset
    a = np.rot90(a)
    outBand = outDataset.GetRasterBand(1)
    outBand.WriteArray(a.byteswap(),0,0) 
    outBand.FlushCache() 
    fn = path+'/'+root+'hhhv.emi'             
#    a = np.reshape(np.fromfile(fn,dtc),(rows,cols)) 
    a = np.reshape(np.fromfile(fn,dtc)[1024::],(rows,cols)) # 8192 byte offset
    a = np.rot90(a)
    outBand = outDataset.GetRasterBand(2)
    outBand.WriteArray(np.real(a).byteswap(),0,0) 
    outBand.FlushCache()  
    outBand = outDataset.GetRasterBand(3)
    outBand.WriteArray(np.imag(a).byteswap(),0,0)  
    outBand.FlushCache()          
    fn = path+'/'+root+'hhvv.emi' 
#    a = np.reshape(np.fromfile(fn,dtc),(rows,cols)) 
    a = np.reshape(np.fromfile(fn,dtc)[1024::],(rows,cols)) # 8192 byte offset
    a = np.rot90(a)
    outBand = outDataset.GetRasterBand(4)
    outBand.WriteArray(np.real(a).byteswap(),0,0)  
    outBand.FlushCache() 
    outBand = outDataset.GetRasterBand(5)
    outBand.WriteArray(np.imag(a).byteswap(),0,0) 
    outBand.FlushCache()  
    fn = path+'/'+root+'hvhv.emi'    
#    a = np.reshape(np.fromfile(fn,dtr),(rows,cols)) 
    a = np.reshape(np.fromfile(fn,dtr)[1024::],(rows,cols)) # 4096 byte offset
    a = np.rot90(a)
    outBand = outDataset.GetRasterBand(6)
    outBand.WriteArray(a.byteswap(),0,0) 
    outBand.FlushCache() 
    fn = path+'/'+root+'hvvv.emi'  
#    a = np.reshape(np.fromfile(fn,dtc),(rows,cols))
    a = np.reshape(np.fromfile(fn,dtc)[1024::],(rows,cols)) # 8192 byte offset
    a = np.rot90(a) 
    outBand = outDataset.GetRasterBand(7)
    outBand.WriteArray(np.real(a).byteswap(),0,0)  
    outBand.FlushCache() 
    outBand = outDataset.GetRasterBand(8)
    outBand.WriteArray(np.imag(a).byteswap(),0,0)  
    outBand.FlushCache() 
    fn = path+'/'+root+'vvvv.emi' 
#    a = np.reshape(np.fromfile(fn,dtr),(rows,cols)) 
    a = np.reshape(np.fromfile(fn,dtr)[1024::],(rows,cols)) # 4096 byte offset
    a = np.rot90(a)
    outBand = outDataset.GetRasterBand(9)
    outBand.WriteArray(a.byteswap(),0,0)  
    outBand.FlushCache() 
    outDataset = None
    print 'emisar data written to %s'%outfn
    
if __name__=='__main__':
    read_emisar('/home/imagery/fl062_l/fl062_l.hdr')
    