#!/bin/bash
#
# Usage: 
# sar_seq.sh 1 2 ... n dims enl significance VV|VH|VVVH
#

echo '***** Multitemporal PolSAR Change Detection ****************'
echo '***** Sentinel1 IW singlepol (VV or VH) imagery ************'
echo '***** Time series downloaded from Google Earth Engine ******'
echo '************************************************************'

n=$[$#-4]
declare -i nn

nn=$n-2
pol="${@: -1}"
significance=("${@: -2}")
enl=("${@: -3}")
dims=("${@: -4}")
last=("${@: -5}")
outfn=$pol'('$1'-'$nn'-'$last').tif'

echo 'number of images ' $n
echo 'ENL              ' $enl
echo 'significance     ' $significance
echo 'spatial subset   ' $dims
echo 'polarization     ' $pol

imdir='/home/imagery/'

for ((i=1; i<=$n; i++))
do  
    pat=$pol"_"$1".tif"
    fni=$imdir$(ls -l $imdir | grep $pat | grep -v "enl" | grep -v "sub" | grep -v "map" | grep -v "warp" |awk '{print $9}')
    [[ $fni = None ]] && exit 1
    fn[i]=$fni
    shift  
done

s="${fn[*]}"
fns=${s//" "/","}

python /home/sar_seq.py -d $dims -s $significance -m $fns $outfn $enl 
