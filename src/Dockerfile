# x86 architecture 
FROM     debian:jessie  
           
# arm (raspberry pi) architecture       
#FROM     resin/rpi-raspbian 

MAINTAINER Mort Canty "mort.canty@gmail.com"

ENV    IMAGE REFRESHED_AT 2015-12-10
#------------------------------

RUN apt-get update && apt-get install -y --no-install-recommends \
    python \
    build-essential \
    make \
    gcc \
    g++ \
    xutils-dev \
    pandoc \
    dos2unix \
    python-dev \
    python-pygments \
    python-zmq \
    python-pip 

# install python environment for crc scripts
RUN     apt-get install -y --no-install-recommends \
         python-numpy python-scipy \
         python-gdal python-matplotlib 

# package imported by auxil package (but not used)
RUN     apt-get install -y --no-install-recommends python-tk

# setup the prov_means library
COPY    prov_means.c /home/prov_means.c
WORKDIR /home
RUN     gcc -shared -Wall -g -o libprov_means.so -fPIC prov_means.c
RUN     cp libprov_means.so /usr/lib/libprov_means.so


ENV    ASF_TOOLS REFRESHED_AT 2015-11-20
#----------------------------------------
# prerequisites
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

ENV     SCRIPTS_CHANGED 2016-01.27
#---------------------------------
COPY    dist/auxil-1.1.tar.gz /auxil-1.1.tar.gz
WORKDIR /
RUN     tar -xzvf auxil-1.1.tar.gz
WORKDIR /auxil-1.1
RUN     python setup.py install  
WORKDIR /
RUN     rm -rf auxil-1.1/
RUN     rm auxil-1.1.tar.gz

# ipython notebook
#RUN     pip install "ipython[notebook]"
RUN     pip install jupyter

# enable parallel computing
RUN     pip install ipyparallel
RUN     jupyter notebook --generate-config
RUN     sed -i "/# Configuration file for jupyter-notebook./a  \ 
                c.NotebookApp.server_extensions.append('ipyparallel.nbextension')" \
            /root/.jupyter/jupyter_notebook_config.py

# ipython notebook startup script 
ADD     notebook.sh  /
RUN     chmod u+x /notebook.sh
RUN     dos2unix /notebook.sh

EXPOSE 8888

# add the Python scripts and set the startup command

COPY    dispms.py /home/dispms.py
COPY    ingest.py /home/ingest.py
COPY    register.py /home/register.py
COPY    enlml.py /home/enlml.py
COPY    wishart.py /home/wishart.py
COPY    omnibus.py /home/omnibus.py

COPY    mapready.sh /home/mapready.sh
COPY    wishart.sh /home/wishart.sh
COPY    omnibus.sh /home/omnibus.sh
COPY    omnibus_s1.sh /home/omnibus_s1.sh
RUN     chmod u+x /home/mapready.sh
RUN     chmod u+x /home/wishart.sh
RUN     chmod u+x /home/omnibus.sh
RUN     chmod u+x /home/omnibus_s1.sh

COPY    utm.prj /home/utm.prj
COPY    radarsat2quadpol.template /home/radarsat2quadpol.template
COPY    terrasarxdualpol.template /home/terrasarxdualpol.template

COPY    tutorial.ipynb /home/tutorial.ipynb 

COPY    gamma_filter.py /home/gamma_filter.py

WORKDIR /home  
CMD     ["/notebook.sh"]
