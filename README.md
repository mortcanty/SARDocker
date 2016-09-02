# Change Detection with Multitemporal Polarimetric SAR Imagery

This repo contains the source files for the Docker image mort/sardocker, which wraps
command line versions of several polarimetric SAR Python scripts, most of which are described  the textbook 
<a href="http://www.amazon.com/Analysis-Classification-Change-Detection-Sensing/dp/1466570377/ref=dp_ob_title_bk">Canty (2104). Image Analysis, Classification and Change Detection in Remote Sensing, 3rd Ed., CRC Press 2014</a>. 

### Installation 
 1. <a href="https://docs.docker.com/">Install Docker</a>
 2. In a terminal, run the command 
      __sudo docker run -d -p 433:8888 --name=sar -v your_image_directory:/sar/imagery mort/sardocker__       
 where *your_image_directory* is the path to your SAR data. 
 3. Point your browser to  
    __localhost:433__
 4. Click on the tutorial, or open a new notebook with __New/Python 2__.
 
 https://microscaling-dot-yamm-track.appspot.com/Redirect?ukey=1DJB55A5hlrac5x9c6lXCxctwB9cJaRW_zrTt6tbcGQ8-381850004&key=YAMMID-25680887&link=https%3A%2F%2Fgithub.com%2Fmortcanty%2FSARDocker
