# Change Detection with Multitemporal Polarimetric SAR Imagery

Source code for a Docker image  for carrying out change detection on
polarimetric SAR images in multi-look covariance matrix format. The 
bash and Python are served in an IPython notebook.

###Installation
On 64-bit Ubuntu Linux:
 1. <a href="https://docs.docker.com/installation/ubuntulinux/">install Docker</a>
 2. In a terminal, run the command<br />
      __sudo docker run -d -p 433:8888 --name=sar -v *your_image_directory*:/sar/imagery mort/sardocker__<br />
     where *your_image_directory* is the path to your SAR data. 
 3. Point your browser to<br /> 
    __localhost:433__
 4. Click on this tutorial, or open a new notebook with __New/Python 2__.
 
On WIndows (or Mac), <a href="https://docs.docker.com/installation/windows/">install boot2docker</a>, share your image directory with VirtualBox and proceed from step 2. above.

 
