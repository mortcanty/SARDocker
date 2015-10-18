FROM     debian:jessie
MAINTAINER Mort Canty "mort.canty@gmail.com"

ENV    IMAGE REFRESHED_AT 2015-04-06
#-----------------------------------
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
    python-pip 
 

ENV    PYTHON_PACKAGES 2105-04-04a
#--------------------------------
# ipython notebook
RUN     pip install "ipython[notebook]"

# install python environment for crc scripts
RUN     apt-get install -y --no-install-recommends \
         python-numpy python-scipy \
         python-gdal python-matplotlib 

# package imported by auxil package (but not used)
RUN     apt-get install -y --no-install-recommends python-tk

# setup the prov_means library
COPY    prov_means.c /sar/prov_means.c
WORKDIR /sar
RUN     gcc -shared -Wall -g -o libprov_means.so -fPIC prov_means.c
RUN     cp libprov_means.so /usr/lib/libprov_means.so


ENV    ASF_TOOLS_PREREQUISITES REFRESHED_AT 2015-04-06a
#----------------------------------------
# prerequisites
RUN     apt-get install -y \
         pkg-config bison flex  \
          gettext libgsl0-dev \
         libgsl0ldbl zlib1g-dev \
         libgdal-dev gdal-bin    
RUN     mv  /usr/include/zlib.h /usr/local/include/zlib.h         
#RUN     apt-get install -y libgtk2.0-dev  libglade2-dev    

ENV     ASF_TOOLS 2015-04-07
#---------------------------            
WORKDIR /
COPY    mapready-3.2.1-src.tar.gz /mapready-3.2.1-src.tar.gz  
COPY    install_asf.sh /install_asf.sh
RUN     chmod u+x /install_asf.sh 
RUN     ./install_asf.sh

WORKDIR /
RUN     rm mapready-3.2.1-src.tar.gz

ENV     SCRIPTS_CHANGED 2015-10-16
#---------------------------------
COPY    dist/auxil-1.1.tar.gz /auxil-1.1.tar.gz
WORKDIR /
RUN     tar -xzvf auxil-1.1.tar.gz
WORKDIR /auxil-1.1
RUN     python setup.py install  
WORKDIR /
RUN     rm -rf auxil-1.1/
RUN     rm auxil-1.1.tar.gz

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

COPY    dispms.py /sar/dispms.py
COPY    ingest.py /sar/ingest.py
COPY    register.py /sar/register.py
COPY    enlml.py /sar/enlml.py
COPY    wishart.py /sar/wishart.py
COPY    omnibus.py /sar/omnibus.py

COPY    mapready.sh /sar/mapready.sh
COPY    wishart.sh /sar/wishart.sh
COPY    omnibus.sh /sar/omnibus.shjupyt
RUN     chmod u+x /sar/mapready.sh
RUN     chmod u+x /sar/wishart.sh
RUN     chmod u+x /sar/omnibus.sh

COPY    utm.prj /sar/utm.prj
COPY    radarsat2quadpol.template /sar/radarsat2quadpol.template
COPY    terrasarxdualpol.template /sar/terrasarxdualpol.template

COPY    tutorialsar.ipynb /sar/tutorial.ipynb 

#COPY    gamma_filter.py /sar/gamma_filter.py

WORKDIR /sar  
CMD     ["/notebook.sh"]
