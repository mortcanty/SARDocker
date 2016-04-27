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
fn1=$dir'polSAR.tif'
shift

for ((i=1; i<$n; i++))
do  
    dir=$imdir$(ls -l $imdir | grep 'MapReady$' | grep $1 | awk '{print $9}')$subdir
    fn2=$dir'polSAR.tif'
    fni=$(python /home/register.py -d $dims $fn1 $fn2 | tee /dev/tty | grep written | awk '{print $5}')
    [[ $fni = None ]] && exit 1
    fn[i]=$fni
    shift  
done

fn1=$(python /home/subset.py -d $dims $fn1 | tee /dev/tty | grep written | awk '{print $4}')

s="$fn1 ${fn[*]}"
fns=${s//" "/","}

python /home/sar_seq.py -s $significance -m $fns $outfn $enl 
