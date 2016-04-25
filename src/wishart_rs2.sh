#!/bin/bash
#
# Usage:
#
#  ./wishart.sh yyyymmdd1 yyyymmdd2 dims enl1 enl2

echo '***** Bitemporal PolSAR Change Detection ************'
echo '***** Radarsat2 quad or dualpol imagery *************'
echo '*****************************************************'

imdir='/home/imagery/'

# test for T3 (quadpol) or C2 (dualpol) directory
dir=$imdir$(ls -l $imdir | grep 'MapReady$' | grep $1 | awk '{print $9}')
subdir='/'$(ls -l $dir | grep [CT][23] | awk '{print $9}')'/'
dir=$imdir$(ls -l $imdir | grep 'MapReady$' | grep $1 | awk '{print $9}')$subdir
fn1=$dir'polSAR.tif'

dir=$imdir$(ls -l $imdir | grep 'MapReady$' | grep $2 | awk '{print $9}')$subdir
fn2=$dir'polSAR.tif'

echo '***** registering ...'

fn2=$(python /home/register.py -d $3 $fn1 $fn2 | tee /dev/tty | grep written | awk '{print $5}')

outfn='wishart('$1'-'$2').tif'

echo '***** complex Wishart change detection ...'

python /home/wishart.py -d $3 $fn1 $fn2 $outfn $4 $5 