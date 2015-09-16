#! /bin/bash

# PAPER_ALL

#layer=conv1
#layer=conv2
#layer=conv3
#layer=conv4
#layer=conv5
#layer=fc6
#layer=fc7
layer=fc8

bigdir=results/150203_212645_2468771_priv_paper_all/$layer/$layer
pushd $bigdir
echo

for unit in `\ls -d unit*`; do
    cd $unit
    outfile=${layer}_${unit}_montage.jpg
    montage {hs0081,hs0141,hs0275,hs0287}/montage.jpg -mode concatenate -background '#333' -tile 2x2 -geometry +2+2 $outfile
    echo $outfile
    cd ..
done

echo
popd
