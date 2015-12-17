#!/usr/bin/env python
#******************************************************************************
#  Name:     dispms.py
#  Purpose:  Display a multispectral image
#             allowed formats: uint8, uint16,float32,float64 
#  Usage (from command line):             
#    python dispms.py  
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

import sys, getopt, os
from osgeo import gdal
import matplotlib.pyplot as plt
import  auxil.auxil as auxil 
import numpy as np
from osgeo.gdalconst import GA_ReadOnly

def make_image(redband,greenband,blueband,rows,cols,enhance):
    X = np.zeros((rows*cols,3),dtype=np.uint8)  
    if enhance == 'linear255':
        i = 0
        for tmp in [redband,greenband,blueband]:
            tmp = tmp.ravel()
            tmp = np.where(tmp<0,0,tmp)  
            tmp = np.where(tmp>255,255,tmp)
            X[:,i] = np.byte(tmp)
            i += 1
    elif enhance == 'linear':
        i = 0
        for tmp in [redband,greenband,blueband]:             
            tmp = tmp.ravel()  
            mx = np.max(tmp)
            mn = np.min(tmp)  
            tmp = (tmp-mn)*255.0/(mx-mn)
            tmp = np.where(tmp<0,0,tmp)  
            tmp = np.where(tmp>255,255,tmp)
            X[:,i] = np.byte(tmp)
            i += 1
    elif enhance == 'linear2pc':
        i = 0
        for tmp in [redband,greenband,blueband]:     
            tmp = tmp.ravel()        
            mx = np.max(tmp)
            mn = np.min(tmp)  
            tmp = (tmp-mn)*255.0/(mx-mn)
            tmp = np.where(tmp<0,0,tmp)  
            tmp = np.where(tmp>255,255,tmp)
            hist,bin_edges = np.histogram(tmp,256,(0,256))
            cdf = hist.cumsum()
            lower = 0
            j = 0
            while cdf[j] < 0.02*cdf[-1]:
                lower += 1
                j += 1
            upper = 255    
            j = 255
            while cdf[j] > 0.98*cdf[-1]:
                upper -= 1
                j -= 1
            if upper==0:
                upper = 255
                print 'Saturated stretch failed'
            fp = (bin_edges-lower)*255/(upper-lower) 
            fp = np.where(bin_edges<=lower,0,fp)
            fp = np.where(bin_edges>=upper,255,fp)
            X[:,i] = np.byte(np.interp(tmp,bin_edges,fp))
            i += 1       
    elif enhance == 'equalization':   
        i = 0
        for tmp in [redband,greenband,blueband]:     
            tmp = tmp.ravel()    
            mx = np.max(tmp)
            mn = np.min(tmp)  
            tmp = (tmp-mn)*255.0/(mx-mn)
            tmp = np.where(tmp<0,0,tmp)  
            tmp = np.where(tmp>255,255,tmp)  
            hist,bin_edges = np.histogram(tmp,256,(0,256)) 
            cdf = hist.cumsum()
            lut = 255*cdf/float(cdf[-1]) 
            X[:,i] = np.byte(np.interp(tmp,bin_edges[:-1],lut))
            i += 1
    elif enhance == 'logarithmic':   
        i = 0
        for tmp in [redband,greenband,blueband]:     
            tmp = tmp.ravel() 
            mn = np.min(tmp)
            if mn < 0:
                tmp = tmp - mn
            idx = np.where(tmp == 0)
            tmp[idx] = np.mean(tmp)
            tmp = np.log(tmp) 
            mn =np.min(tmp)
            mx = np.max(tmp)
            tmp =(tmp-mn)*255.0/(mx-mn)  
            tmp = np.where(tmp<0,0,tmp)  
            tmp = np.where(tmp>255,255,tmp)
            X[:,i] = np.byte(tmp) 
            i += 1                           
    return np.reshape(X,(rows,cols,3))/255.

def dispms(filename1=None,filename2=None,dims=None,DIMS=None,rgb=None,RGB=None,enhance=None,ENHANCE=None,cls=False,CLS=False):
    gdal.AllRegister()
    if filename1 == None:        
        filename1 = raw_input('Enter image filename: ')
    inDataset1 = gdal.Open(filename1,GA_ReadOnly)    
    try:                   
        cols = inDataset1.RasterXSize    
        rows = inDataset1.RasterYSize  
        bands1 = inDataset1.RasterCount  
    except Exception as e:
        print 'Error in dispms: %s  --could not read image file'%e
        return   
    if filename2 is not None:                
        inDataset2 = gdal.Open(filename2,GA_ReadOnly) 
        try:       
            cols2 = inDataset2.RasterXSize    
            rows2 = inDataset2.RasterYSize            
            bands2 = inDataset2.RasterCount       
        except Exception as e:
            print 'Error in dispms: %s  --could not read second image file'%e
            return       
    if dims == None:
        dims = [0,0,cols,rows]
    x0,y0,cols,rows = dims
    if rgb == None:
        rgb = [1,1,1]
    r,g,b = rgb
    r = int(np.min([r,bands1]))
    g = int(np.min([g,bands1]))
    b = int(np.min([b,bands1]))
    
    if enhance == None:
        enhance = 5
    if enhance == 1:
        enhance1 = 'linear255'
    elif enhance == 2:
        enhance1 = 'linear'
    elif enhance == 3:
        enhance1 = 'linear2pc'
    elif enhance == 4:
        enhance1 = 'equalization'
    elif enhance == 5:
        enhance1 = 'logarithmic'    
    else:
        enhance = 'linear2pc' 
    try:  
        if not cls:
            redband   = np.nan_to_num(inDataset1.GetRasterBand(r).ReadAsArray(x0,y0,cols,rows)) 
            greenband = np.nan_to_num(inDataset1.GetRasterBand(g).ReadAsArray(x0,y0,cols,rows)) 
            blueband  = np.nan_to_num(inDataset1.GetRasterBand(b).ReadAsArray(x0,y0,cols,rows))
        else:
            classimg = inDataset1.GetRasterBand(1).ReadAsArray(x0,y0,cols,rows).ravel()
            ctable = np.reshape(auxil.ctable,(18,3))
            classes = range(1,np.max(classimg)+1)
            redband = classimg*0
            greenband = classimg*0
            blueband = classimg*0
            for k in classes:
                idx = np.where(classimg==k)
                redband[idx] = ctable[k,0]
                greenband[idx] = ctable[k,1]
                blueband[idx] = ctable[k,2]
            redband = np.reshape(redband,(rows,cols))    
            greenband = np.reshape(greenband,(rows,cols))
            blueband = np.reshape(blueband,(rows,cols))
        inDataset1 = None   
    except  Exception as e:
        print 'Error in dispms: %s'%e  
        return
    X1 = make_image(redband,greenband,blueband,rows,cols,enhance1)
    if filename2 is not None:
        if DIMS == None:
            DIMS = [0,0,cols2,rows2]
        x0,y0,cols,rows = DIMS
        if RGB == None:
            RGB = rgb
        r,g,b = RGB
        r = int(np.min([r,bands2]))
        g = int(np.min([g,bands2]))
        b = int(np.min([b,bands2]))
        enhance = ENHANCE
        if enhance == None:
            enhance = 5
        if enhance == 1:
            enhance2 = 'linear255'
        elif enhance == 2:
            enhance2= 'linear'
        elif enhance == 3:
            enhance2 = 'linear2pc'
        elif enhance == 4:
            enhance2 = 'equalization'
        elif enhance == 5:
            enhance2 = 'logarithmic'    
        else:
            enhance = 'logarithmic'          
        try:  
            if not CLS:
                redband   = np.nan_to_num(inDataset2.GetRasterBand(r).ReadAsArray(x0,y0,cols,rows))
                greenband = np.nan_to_num(inDataset2.GetRasterBand(g).ReadAsArray(x0,y0,cols,rows)) 
                blueband  = np.nan_to_num(inDataset2.GetRasterBand(b).ReadAsArray(x0,y0,cols,rows))
            else:
                classimg = inDataset2.GetRasterBand(1).ReadAsArray(x0,y0,cols,rows).ravel()
                ctable = np.reshape(auxil.ctable,(18,3))
                classes = range(1,np.max(classimg)+1)
                redband = classimg*0
                greenband = classimg*0
                blueband = classimg*0
                for k in classes:
                    idx = np.where(classimg==k)
                    redband[idx] = ctable[k,0]
                    greenband[idx] = ctable[k,1]
                    blueband[idx] = ctable[k,2]
                redband = np.reshape(redband,(rows,cols))    
                greenband = np.reshape(greenband,(rows,cols))
                blueband = np.reshape(blueband,(rows,cols))
            inDataset2 = None   
        except  Exception as e:
            print 'Error in dispms: %s'%e  
            return
        X2 = make_image(redband,greenband,blueband,rows,cols,enhance2)    
        f, ax = plt.subplots(1,2,figsize=(20,10))
        ax[0].imshow(X1)
        ax[0].set_title('%s: %s: %s:  %s\n'%(os.path.basename(filename1),enhance1, str(rgb), str(dims)))
        ax[1].imshow(X2)
        ax[1].set_title('%s: %s: %s: %s\n'%(os.path.basename(filename2),enhance2, str(RGB), str(DIMS)))
    else:
        f, ax = plt.subplots(figsize=(10,10))
        ax.imshow(X1)
        ax.set_title('%s: %s: %s: %s\n'%(os.path.basename(filename1),enhance1, str(rgb), str(dims))) 
    plt.show()
                      

def main():
    usage = '''Usage: python %s [-c] [-C] [-f filename1] [-F filename2] [-p posf] [P posF [-d dimsf] [-D dimsF]\n
                                        [-e enhancementf] [-E enhancement]\n
            if -f is not specified it will be queried\n
            use -c or -C for classification image\n 
            RGB bandPositions and spatialDimensions are lists, e.g., -p [1,4,3] -d [0,0,400,400] \n
            enhancements: 1=linear255 2=linear 3=linear2pc 4=equalization 5=logarithmic\n'''%sys.argv[0]
    options,args = getopt.getopt(sys.argv[1:],'hcCf:F:p:P:d:D:e:E:')
    filename1 = None
    filename2 = None
    dims = None
    rgb = None
    DIMS = None
    RGB = None
    enhance = None   
    ENHANCE = None
    cls = False
    CLS = False
    for option, value in options: 
        if option == '-h':
            print usage
            return 
        elif option == '-f':
            filename1 = value
        elif option == '-F':
            filename2 = value    
        elif option == '-p':
            rgb = tuple(eval(value))
        elif option == '-P':
            RGB = tuple(eval(value))    
        elif option == '-d':
            dims = eval(value) 
        elif option == '-D':
            DIMS = eval(value)    
        elif option == '-e':
            enhance = eval(value)  
        elif option == '-E':
            ENHANCE = eval(value)    
        elif option == '-c':
            cls = True  
        elif option == '-C':
            CLS = True                
                    
    dispms(filename1,filename2,dims,DIMS,rgb,RGB,enhance,ENHANCE,cls,CLS)

if __name__ == '__main__':
    main()