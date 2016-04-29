#!/bin/bash
#
# Usage: 
# sar_seq_s1.sh yyyymmdd1 yyyymmdd2 ... yyyymmddn dims enl significance 
#

echo '***** Multitemporal PolSAR Change Detection **********'
echo '***** Sentenel-1 dualpol imagery *********************'
echo '******************************************************'

n=$[$#-3]
declare -i nn

nn=$n-2
significance="${@: -1}"
enl=("${@: -2}")
dims=("${@: -3}")
last=("${@: -4}")
outfn='sarseq('$1'-'$nn'-'$last').tif'

echo 'number of images ' $n
echo 'ENL              ' $enl
echo 'spatial subset   ' $dims

imdir='/home/imagery/'

for ((i=1; i<=$n; i++))
do  
    fni=$imdir$(ls -l $imdir | grep $1 | grep -v "enl" | grep -v "sub" | grep -v "map" | grep -v "warp" |awk '{print $9}')
    [[ $fni = None ]] && exit 1
    fn[i]=$fni
    shift  
done

s="${fn[*]}"
fns=${s//" "/","}

python /home/sar_seq.py -d $dims -s $significance -m $fns $outfn $enl 
 