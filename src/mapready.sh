#!/bin/bash
# Usage:
#
#  ./mapready.sh yyyymmdd platform
#
echo 'Geocoding polSARpro multilook polarimetric matrix image with mapready ...'
#
# platform: rs2quad, tsxdual

imdir='/sar/imagery/'

if [ $2 == 'rs2quad' ] 
then 
# prepare the MapReady configuration file
	basename=$imdir$(ls -l $imdir | grep 'RS2_OK' | grep '_SLC$' | grep $1 | awk '{print $9}') 
    sed 's:basename:'$basename':g' /sar/radarsat2quadpol.template > /sar/mapready.cfg
# Edit the first ENVI header in the PolSARPro directory
	pspdir=$basename'/polsarpro/T3'	
	if [[ $(cat $pspdir/T11.bin.hdr | grep 'description' | grep '}$') ]]
	then 	
        sed -i s/"{"/"{\n"/ $pspdir/T11.bin.hdr
    fi    
# get the number of looks
    dos2unix $pspdir/'config.txt'	
    rows=$(grep -m1 "[0-9]" $pspdir/'config.txt')
    cols=$(grep  -A 1 "Ncol" $pspdir/'config.txt' | grep "[0-9]")
	rows0=$(grep -oPm1 "(?<=<numberOfLines>)[^<]+" $basename'/product.xml') 
	cols0=$(grep -oPm1 "(?<=<numberOfSamplesPerLine>)[^<]+" $basename'/product.xml') 
	echo "Original SLC image dimensions:      rows "$rows0"  cols "$cols0
    echo "After multi-looking with polSARpro: rows "$rows"  cols "$cols
	echo 'Azimuth looks: '$((rows0/rows))
	echo 'Range looks:   '$((cols0/cols))
elif [ $2 == 'tsxdual' ]
then 
# prepare the MapReady configuration file
    basename=$imdir$(ls -l $imdir | grep 'TSX$' | grep $1 | awk '{print $9}')
	ancillary=$basename'/'$(ls -l $basename | grep $1 | awk '{print $9}')
	sed -e 's:basename:'$basename':g' -e 's:auxil:'$ancillary':g' /sar/terrasarxdualpol.template > /sar/mapready.cfg
# Edit the first ENVI header in the PolSARPro directory
	pspdir=$basename'/polsarpro/C2'
	if [[ $(cat $pspdir/C11.bin.hdr | grep 'description' | grep '}$') ]]
	then 	
        sed -i s/"{"/"{\n"/ $pspdir/C11.bin.hdr
    fi 
# get the number of looks
    dos2unix $pspdir/'config.txt'
    rows=$(grep -m1 "[0-9]" $pspdir/'config.txt')
    cols=$(grep  -A 1 "Ncol" $pspdir/'config.txt' | grep "[0-9]")
    rows0=$(grep -oPm1 "(?<=<numberOfRows>)[^<]+" $ancillary) 
	cols0=$(grep -oPm1 "(?<=<numberOfColumns>)[^<]+" $ancillary) 
    echo "Original SLC image dimensions:      rows "$rows0"  cols "$cols0
    echo "After multi-looking with polSARpro: rows "$rows"  cols "$cols
	echo 'Azimuth looks: '$((rows0/rows))
	echo 'Range looks:   '$((cols0/cols))	
fi

cd /sar
    
echo '***** processing polSARpro polarimetric matrix image:'

echo '***** '$basename

echo '***** ...'

asf_mapready mapready.cfg > mapready.log

echo '***** Done, see mapready.log'

echo '***** Combining into a single image file ...'

# test for T3 (quadpol) or C2 (dualpol) directory
dir=$imdir$(ls -l $imdir | grep 'MapReady$' | grep $1 | awk '{print $9}')
subdir='/'$(ls -l $dir | grep [CT][23] | awk '{print $9}')'/'

dir=$imdir$(ls -l $imdir | grep 'MapReady$' | grep $1 | awk '{print $9}')$subdir
fn=$dir$(python /sar/ingest.py $dir | tee /dev/tty | grep 'written' | awk '{print $5}')