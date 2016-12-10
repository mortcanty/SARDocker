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
tmp1=$(ls -l $imdir | grep H_[0-9]\.tif$ | awk '{print $9}') 
tmp2=$(ls -l $imdir | grep H_[1-9][0-9]\.tif$ | awk '{print $9}')
tmp=$tmp1' '$tmp2
fns=$imdir$(echo $tmp | sed "s; ;,$imdir;g")
intervals=$(grep -o "," <<< "$fns" | wc -l)
echo 'intervals: ' $intervals
python /home/sar_seq.py -d $1 -s $3 $fns $outfn $2 
