# x86 architecture 
FROM     debian:jessie 
           
# arm (raspberry pi) architecture       
#FROM     resin/rpi-raspbian 

MAINTAINER Mort Canty "mort.canty@gmail.com"

RUN rm -rf /var/lib/apt/lists/partial

RUN apt-get update && apt-get install -y --no-install-recommends \
    python \
    build-essential \
    make \
    gcc \
    g++ \
    xutils-dev \
    pandoc \
    python-dev \ 
    python-pygments \
    python-zmq \
    python-pip 

# install python environment for crc scripts
RUN     apt-get install -y --no-install-recommends \
         python-numpy python-scipy \
         python-gdal python-matplotlib libgdal-dev gdal-bin

# package imported by auxil package (but not used)
RUN     apt-get install -y --no-install-recommends python-tk

# setup the prov_means library
COPY    prov_means.c /home/prov_means.c
WORKDIR /home
RUN     gcc -shared -Wall -g -o libprov_means.so -fPIC prov_means.c
RUN     cp libprov_means.so /usr/lib/libprov_means.so


# asf prerequisites
RUN     apt-get install -y \
         pkg-config bison flex  \
          gettext libgsl0-dev \
         libgsl0ldbl zlib1g-dev \
         libgdal-dev gdal-bin    
RUN     mv  /usr/include/zlib.h /usr/local/include/zlib.h         
    
# build           
WORKDIR /
COPY    mapready-3.2.1-src.tar.gz /mapready-3.2.1-src.tar.gz  
COPY    install_asf.sh /install_asf.sh
RUN     chmod u+x /install_asf.sh 
RUN     ./install_asf.sh

WORKDIR /
RUN     rm mapready-3.2.1-src.tar.gz


# ipython notebook
RUN     pip install "ipython[notebook]"

# enable parallel computing
RUN     pip install ipyparallel
RUN     jupyter notebook --generate-config
RUN     sed -i "/# Configuration file for jupyter-notebook./a  \ 
                c.NotebookApp.password = u'sha1:e008edc6061d:7960c7798fffe65531a2073e85e219e3fd61f3d0'" \
                /root/.jupyter/jupyter_notebook_config.py
                
            
#  my auxil
COPY    dist/auxil-1.1.tar.gz /auxil-1.1.tar.gz
WORKDIR /
RUN     tar -xzvf auxil-1.1.tar.gz
WORKDIR /auxil-1.1
RUN     python setup.py install  
WORKDIR /
RUN     rm -rf auxil-1.1/
RUN     rm auxil-1.1.tar.gz

# ipython notebook startup script 
ADD     notebook.sh  /
RUN     chmod u+x /notebook.sh

EXPOSE 8888

# add the Python scripts and set the startup command
COPY    dispms.py /home/dispms.py
COPY    ingestsar.py /home/ingestsar.py
COPY    ingests1s2.py /home/ingests1s2.py
COPY    ingestrs2quad.py /home/ingestrs2quad.py
COPY    ingests1.py /home/ingests1.py
COPY    register.py /home/register.py
COPY    enlml.py /home/enlml.py
COPY    subset.py /home/subset.py
COPY    sar_seq.py /home/sar_seq.py
COPY    gamma_filter.py /home/gamma_filter.py

COPY    mapready.sh /home/mapready.sh
COPY    sar_seq_rs2.sh /home/sar_seq_rs2.sh
COPY    sar_seq_rs2quad.sh /home/sar_seq_rs2quad.sh
COPY    sar_seq_s1.sh /home/sar_seq_s1.sh
COPY    sar_seq_tsx.sh /home/sar_seq_tsx.sh
COPY    sar_seq.sh /home/sar_seq.sh
COPY    sar_seq_a.sh /home/sar_seq_a.sh
RUN     chmod u+x /home/mapready.sh
RUN     chmod u+x /home/sar_seq_rs2.sh
RUN     chmod u+x /home/sar_seq_rs2quad.sh
RUN     chmod u+x /home/sar_seq_s1.sh
RUN     chmod u+x /home/sar_seq_tsx.sh 
RUN     chmod u+x /home/sar_seq.sh 
RUN     chmod u+x /home/sar_seq_a.sh 

# for rpis    
#COPY    start4engines.sh /home/start4engines.sh    
#RUN     chmod u+x /home/start4engines.sh

COPY    utm.prj /home/utm.prj
COPY    radarsat2quadpol.template /home/radarsat2quadpol.template
COPY    terrasarxdualpol.template /home/terrasarxdualpol.template

COPY    tutorialsar.ipynb /home/tutorialsar.ipynb 

WORKDIR /home  
CMD     ["/notebook.sh"]
#CMD      ["/bin/bash"]

