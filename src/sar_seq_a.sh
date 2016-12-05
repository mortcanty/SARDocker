#!/bin/bash
#
# Usage: 
# sar_seq.sh dims enl significance
#

echo '***** Multitemporal PolSAR Change Detection ****************'
echo '***** Sentinel 1 IW singlepol (VV or VH) *******************'
echo '***** or dualpol diagonal (VVVH) imagery *******************'
echo '***** Time series downloaded from Google Earth Engine ******'
echo ' '
echo 'spatial subset: ' $1
echo 'ENL: ' $2
echo 'Significance: ' $3

imdir='/home/imagery/'
outfn='result.tif'
tmp=$(ls -l $imdir | grep [0-9]_warp\.tif$ | awk '{print $9}')
fns=$imdir$(echo $tmp | sed "s; ;,$imdir;g")
intervals=$(grep -o "," <<< "$fns" | wc -l)
# no dims, no median filter
python /home/sar_seq.py -s $3 $fns $outfn $2 
