#!/bin/bash
#
# Usage: 
#
#  ./sar_seq.sh yyyymmdd1 ... yyyymmddn dims enl significance

echo '***** Multitemporal PolSAR Change Detection **********'
echo '***** Radarsat2 quadpol imagery **********************'
echo '***** Pre-processed with Sentinel-1 Toolbox **********'
echo '******************************************************'

n=$[$#-3]
declare -i nn
nn=$n-2
significance="${@: -1}"
enl=("${@: -2}")
dims=("${@: -3}")
last=("${@: -4}")
outfn='sarseq('$1'-'$nn'-'$last').tif'

echo 'number of images   ' $n
echo 'ENL                ' $enl
echo 'spatial subset     ' $dims
echo 'significance level ' $significance

imdir='/home/imagery/'

for ((i=1; i<=$n; i++))
do  
    dir=$imdir$(ls -l $imdir | grep $1 | awk '{print $9}')
    fni=$dir'/polSAR.tif'
    [[ $fni = None ]] && exit 1
    fn[i]=$fni
    shift  
done

s="${fn[*]}"
fns=${s//" "/","}

python /home/sar_seq.py -d $dims -s $significance -m $fns $outfn $enl 
