#!/bin/bash
#
# Usage: 
# omnibus.sh yyyymmdd1 yyyymmdd2 ... yyyymmddn dims enl significance 
#
# Example:
#
# ./omnibus.sh 20141108 20150507 20150612 [400,400,1600,1600] 12 0.01

echo '***** Multitemporal PolSAR Change Detection **********'
echo '******************************************************'

n=$[$#-3]
declare -i nn
nn=$n-2
significance="${@: -1}"
enl=("${@: -2}")
dims=("${@: -3}")
last=("${@: -4}")
outfn='omnibus('$1'-'$nn'-'$last').tif'

echo 'number of images ' $n
echo 'ENL              ' $enl
echo 'spatial subset   ' $dims

imdir='/home/imagery/'
fn1=$(ls -l $imdir | grep $1 | grep -v "enl" | grep -v "warp" | grep -v "cmap" | grep -v "omnibus" | awk '{print $9}')
shift

for ((i=1; i<$n; i++))
do  
    fn2=$(ls -l $imdir | grep $1 | grep -v "enl" | grep -v "warp" | grep -v "cmap" | grep -v "omnibus" | awk '{print $9}' )
    fni=$(python /home/register.py -d $dims $fn1 $fn2 | tee /dev/tty | grep written | awk '{print $5}')
    [[ $fni = None ]] && exit 1
    fn[i]=$fni
    shift  
done

s="$fn1 ${fn[*]}"
fns=${s//" "/","}
python /home/omnibus.py -d $dims -s $significance -m $fns  $outfn $enl 
