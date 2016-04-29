#!/bin/bash
#
# Usage: 
#
#  ./sar_seq.sh yyyymmdd1 ... yyyymmddn dims enl significance

echo '***** Multitemporal PolSAR Change Detection **********'
echo '***** Radarsat2 quad or dualpol imagery **************'
echo '***** Pre-processed with MapReady ********************'
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

# test for T3 (quadpol) or C2 (dualpol) directory
dir=$imdir$(ls -l $imdir | grep 'MapReady$' | grep $1 | awk '{print $9}')
subdir='/'$(ls -l $dir | grep [CT][23] | awk '{print $9}')'/'
dir=$imdir$(ls -l $imdir | grep 'MapReady$' | grep $1 | awk '{print $9}')$subdir

for ((i=1; i<=$n; i++))
do  
    dir=$imdir$(ls -l $imdir | grep 'MapReady$' | grep $1 | awk '{print $9}')$subdir
    fni=$dir'polSAR.tif'
    [[ $fni = None ]] && exit 1
    fn[i]=$fni
    shift  
done

s="${fn[*]}"
fns=${s//" "/","}

python /home/sar_seq.py -d $dims -s $significance -m $fns $outfn $enl 
