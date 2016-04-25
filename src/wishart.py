#!/usr/bin/env python
#******************************************************************************
#  Name:     wishart.py
#  Purpose:  Perform change detection on bitemporal, polarimetric SAR imagery 
#            Based on Allan Nielsen's Matlab script
#            Condradsen et al. (2003) IEEE Transactions on Geoscience and Remote Sensing 41(1) 4-19
#
#  Usage:             
#    python wishart.py [-d dims] [-s significance] file1 file2 outfile enl1 enl2
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
from scipy import stats, ndimage
import os, sys, time, getopt, gdal 
from osgeo.gdalconst import GA_ReadOnly, GDT_Float32, GDT_Byte

                       
def main():
    usage = '''
Usage:
------------------------------------------------
    python %s [-h] [-d dims] [-s significance] file1 file2 outfile enl1 enl2
    outfile is without path (written to same directory as file1)
    
    Perform change detection on bitemporal, polarimetric SAR imagery.
--------------------------------------------'''%sys.argv[0]

    options,args = getopt.getopt(sys.argv[1:],'hd:s:')
    dims = None
    significance = 0.01
    for option, value in options: 
        if option == '-h':
            print usage
            return 
        elif option == '-d':
            dims = eval(value)  
        elif option == '-s':
            significance = eval(value)           
    if len(args) != 5:
        print 'Incorrect number of arguments'
        print usage
        sys.exit(1)        
    fn1 = args[0]
    fn2 = args[1]
    outfn = args[2]
    m1 = np.float64(eval(args[3]))
    m2 = np.float64(eval(args[4]))
    print '============================================'
    print 'Bi-temporal Complex Wishart Change Detection'
    print '============================================'
    print time.asctime()
    gdal.AllRegister()       
#  first SAR image                 
    inDataset1 = gdal.Open(fn1,GA_ReadOnly)     
    cols = inDataset1.RasterXSize
    rows = inDataset1.RasterYSize    
    bands = inDataset1.RasterCount
    if dims == None:
        dims = [0,0,cols,rows]
    x0,y0,cols,rows = dims 
    print 'first filename:  %s'%fn1
    print 'number of looks: %f'%m1 
#  second SAR image    
    print 'second filename:  %s'%fn2
    print 'number of looks: %f'%m2 
#  output file
    path = os.path.abspath(fn1)    
    dirn = os.path.dirname(path)
    outfn = dirn + '/' + outfn 
        
    start = time.time()    
    inDataset2 = gdal.Open(fn2,GA_ReadOnly)     
    if bands == 9:
        print 'Quad polarimetry'  
#      T11 (k1)
        b = inDataset1.GetRasterBand(1)
        k1 = m1*b.ReadAsArray(x0,y0,cols,rows)
#      T12  (a1)
        b = inDataset1.GetRasterBand(2)
        a1 = b.ReadAsArray(x0,y0,cols,rows)
        b = inDataset1.GetRasterBand(3)    
        im = b.ReadAsArray(x0,y0,cols,rows)
        a1 = m1*(a1 + 1j*im)
#      T13  (rho1)
        b = inDataset1.GetRasterBand(4)
        rho1 = b.ReadAsArray(x0,y0,cols,rows)
        b = inDataset1.GetRasterBand(5)
        im = b.ReadAsArray(x0,y0,cols,rows)
        rho1 = m1*(rho1 + 1j*im)      
#      T22 (xsi1)
        b = inDataset1.GetRasterBand(6)
        xsi1 = m1*b.ReadAsArray(x0,y0,cols,rows)    
#      T23 (b1)        
        b = inDataset1.GetRasterBand(7)
        b1 = b.ReadAsArray(x0,y0,cols,rows)
        b = inDataset1.GetRasterBand(8)
        im = b.ReadAsArray(x0,y0,cols,rows)
        b1 = m1*(b1 + 1j*im)      
#      T33 (zeta1)
        b = inDataset1.GetRasterBand(9)
        zeta1 = m1*b.ReadAsArray(x0,y0,cols,rows)              
#      T11 (k2)
        b = inDataset2.GetRasterBand(1)
        k2 = m2*b.ReadAsArray(0,0,cols,rows)
#      T12  (a2)
        b = inDataset2.GetRasterBand(2)
        a2 = b.ReadAsArray(0,0,cols,rows)
        b = inDataset2.GetRasterBand(3)
        im = b.ReadAsArray(0,0,cols,rows)
        a2 = m2*(a2 + 1j*im)
#      T13  (rho2)
        b = inDataset2.GetRasterBand(4)
        rho2 = b.ReadAsArray(0,0,cols,rows)
        b = inDataset2.GetRasterBand(5)
        im = b.ReadAsArray(0,0,cols,rows)
        rho2 = m2*(rho2 + 1j*im)        
#      T22 (xsi2)
        b = inDataset2.GetRasterBand(6)
        xsi2 = m2*b.ReadAsArray(0,0,cols,rows)    
#      T23 (b2)        
        b = inDataset2.GetRasterBand(7)
        b2 = b.ReadAsArray(0,0,cols,rows)
        b = inDataset2.GetRasterBand(8)
        im = b.ReadAsArray(0,0,cols,rows)
        b2 = m2*(b2 + 1j*im)        
#      T33 (zeta2)
        b = inDataset2.GetRasterBand(9)
        zeta2 = m2*b.ReadAsArray(0,0,cols,rows)           
        k3    = k1 + k2  
        a3    = a1 + a2
        rho3  = rho1 + rho2
        xsi3  = xsi1 + xsi2
        b3    = b1 + b2
        zeta3 = zeta1 + zeta2           
        det1 = k1*xsi1*zeta1 + 2*np.real(a1*b1*np.conj(rho1)) - xsi1*(abs(rho1)**2) - k1*(abs(b1)**2) - zeta1*(abs(a1)**2)    
        det2 = k2*xsi2*zeta2 + 2*np.real(a2*b2*np.conj(rho2)) - xsi2*(abs(rho2)**2) - k2*(abs(b2)**2) - zeta2*(abs(a2)**2)       
        det3 = k3*xsi3*zeta3 + 2*np.real(a3*b3*np.conj(rho3)) - xsi3*(abs(rho3)**2) - k3*(abs(b3)**2) - zeta3*(abs(a3)**2)       
        p = 3
        f = p**2
        cst = p*((m2+m1)*np.log(m2+m1)-m2*np.log(m2)-m1*np.log(m1)) 
        rho = 1. - (2.*p**2-1.)*(1./m2 + 1./m1 - 1./(m2+m1))/(6.*p)    
        omega2 = -(p*p/4.)*(1. - 1./rho)**2 + p**2*(p**2-1.)*(1./m2**2 + 1./m1**2 - 1./(m2+m1)**2)/(24.*rho**2)        
    elif bands == 4:
        print 'Dual polarimetry'  
#      C11 (k1)
        b = inDataset1.GetRasterBand(1)
        k1 = m1*b.ReadAsArray(x0,y0,cols,rows)
#      C12  (a1)
        b = inDataset1.GetRasterBand(2)
        a1 = b.ReadAsArray(x0,y0,cols,rows)
        b = inDataset1.GetRasterBand(3)
        im = b.ReadAsArray(x0,y0,cols,rows)
        a1 = m1*(a1 + 1j*im)        
#      C22 (xsi1)
        b = inDataset1.GetRasterBand(4)
        xsi1 = m1*b.ReadAsArray(x0,y0,cols,rows)          
#      C11 (k2)
        b = inDataset2.GetRasterBand(1)
        k2 = m2*b.ReadAsArray(0,0,cols,rows)
#      C12  (a2)
        b = inDataset2.GetRasterBand(2)
        a2 = b.ReadAsArray(0,0,cols,rows)
        b = inDataset2.GetRasterBand(3)
        im = b.ReadAsArray(0,0,cols,rows)
        a2 = m2*(a2 + 1j*im)        
#      C22 (xsi2)
        b = inDataset2.GetRasterBand(4)
        xsi2 = m2*b.ReadAsArray(0,0,cols,rows)        
        k3    = k1 + k2  
        a3    = a1 + a2
        xsi3  = xsi1 + xsi2       
        det1 = k1*xsi1 - abs(a1)**2
        det2 = k2*xsi2 - abs(a2)**2 
        det3 = k3*xsi3 - abs(a3)**2        
        p = 2 
        cst = p*((m2+m1)*np.log(m2+m1)-m2*np.log(m2)-m1*np.log(m1)) 
        f = p**2
        rho = 1-(2*f-1)*(1./m2+1./m1-1./(m2+m1))/(6.*p)
        omega2 = -f/4.*(1-1./rho)**2 + f*(f-1)*(1./m2**2+1./m1**2-1./(m2+m1)**2)/(24.*rho**2)  
    elif bands == 1:
        print 'Single polarimetry'         
#      C11 (k1)
        b = inDataset1.GetRasterBand(1)
        k1 = m1*b.ReadAsArray(x0,y0,cols,rows) 
#      C11 (k2)
        b = inDataset2.GetRasterBand(1)
        k2 = m2*b.ReadAsArray(0,0,cols,rows) 
        k3 = k1 + k2
        det1 = k1 
        det2 = k2
        det3 = k3    
        p = 1 
        cst = p*((m2+m1)*np.log(m2+m1)-m2*np.log(m2)-m1*np.log(m1)) 
        f = p**2
        rho = 1-(2.*f-1)*(1./m2+1./m1-1./(m2+m1))/(6.*p)
        omega2 = -f/4.*(1-1./rho)**2+f*(f-1)*(1./m2**2+1./m1**2-1./(m2+m1)**2)/(24.*rho**2)  
    else:   
        print 'Incorrect number of bands'
        return   
    idx = np.where(det1 <= 0.0)
    det1[idx] = 0.0000001   
    idx = np.where(det2 <= 0.0)
    det2[idx] = 0.0000001 
    idx = np.where(det3 <= 0.0)
    det3[idx] = 0.0000001  
    lnQ = cst+m1*np.log(det1)+m2*np.log(det2)-(m2+m1)*np.log(det3)
#  test statistic    
    Z = -2*rho*lnQ
#  change probabilty
    P =  (1.-omega2)*stats.chi2.cdf(Z,[f])+omega2*stats.chi2.cdf(Z,[f+4])
    P =  ndimage.filters.median_filter(P, size = (3,3))
#  change map
    a255 = np.ones((rows,cols),dtype=np.byte)*255
    a0 = a255*0
    c11 = np.log(k1+0.0000001) 
    min1 =np.min(c11)
    max1 = np.max(c11)
    c11 = (c11-min1)*255.0/(max1-min1)  
    c11 = np.where(c11<0,a0,c11)  
    c11 = np.where(c11>255,a255,c11) 
    c11 = np.where(P>(1.0-significance),a0,c11)      
    cmap = np.where(P>(1.0-significance),a255,c11)
    cmap0 = np.where(P>(1.0-significance),a255,a0)
#  write to file system        
    driver = inDataset1.GetDriver()    
    outDataset = driver.Create(outfn,cols,rows,3,GDT_Float32)
    geotransform = inDataset2.GetGeoTransform()
    if geotransform is not None:
        outDataset.SetGeoTransform(geotransform)
    projection = inDataset2.GetProjection()        
    if projection is not None:
        outDataset.SetProjection(projection) 
    outBand = outDataset.GetRasterBand(1)
    outBand.WriteArray(Z,0,0) 
    outBand.FlushCache() 
    outBand = outDataset.GetRasterBand(2)
    outBand.WriteArray(P,0,0) 
    outBand.FlushCache()   
    outBand = outDataset.GetRasterBand(3)
    outBand.WriteArray(cmap0,0,0) 
    outBand.FlushCache()     
    outDataset = None
    print 'test statistic, change probabilities and change map written to: %s'%outfn 
    basename = os.path.basename(outfn)
    name, ext = os.path.splitext(basename)
    outfn=outfn.replace(name,name+'_cmap')
    outDataset = driver.Create(outfn,cols,rows,3,GDT_Byte)
    geotransform = inDataset2.GetGeoTransform()
    if geotransform is not None:
        outDataset.SetGeoTransform(geotransform)
    projection = inDataset2.GetProjection()        
    if projection is not None:
        outDataset.SetProjection(projection)     
    outBand = outDataset.GetRasterBand(1)
    outBand.WriteArray(cmap,0,0) 
    outBand.FlushCache() 
    outBand = outDataset.GetRasterBand(2)
    outBand.WriteArray(c11,0,0) 
    outBand.FlushCache()  
    outBand = outDataset.GetRasterBand(3)
    outBand.WriteArray(c11,0,0) 
    outBand.FlushCache()  
    outDataset = None    
    inDataset1 = None
    inDataset2 = None
    print 'change map image written to: %s'%outfn   
    print 'elapsed time: '+str(time.time()-start)  
                
if __name__ == '__main__':
    main()     