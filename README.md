# Change Detection with Multitemporal Polarimetric SAR Imagery

This repo contains the source files for the Docker image mort/sardocker, which wraps
command line versions of several polarimetric SAR Python scripts, most of which are described  the textbook 
<a href="http://www.amazon.com/Analysis-Classification-Change-Detection-Sensing/dp/1466570377/ref=dp_ob_title_bk">Canty (2014). 
Image Analysis, Classification and Change Detection in Remote Sensing, 3rd Ed., CRC Press 2014</a>. In addition new sequential change
detection scripts implement the algorthms described in 
<a href = "http://www2.imm.dtu.dk/pubdb/views/publication_details.php?id=6825"> Conradsen et al. (2016). Determining the points of
change in time series of polarimetric SAR data. IEEE TGRS 54 (5) 3007-3024.</a>

### Installation 
 1. <a href="https://docs.docker.com/">Install Docker</a>
 2. In a terminal, run the command 
      __sudo docker run -d -p 433:8888 --name=sar -v your_image_directory:/sar/imagery mort/sardocker__       
 where *your_image_directory* is the path to your SAR data. 
 3. Point your browser to  
    __localhost:433__
 4. If asked for a password, enter 'mort'	    
 5. Click on the <a href="http://mortcanty.github.io/src/tutorialsar.html"> tutorial</a>, or open a new notebook with __New/Python 2__.
 