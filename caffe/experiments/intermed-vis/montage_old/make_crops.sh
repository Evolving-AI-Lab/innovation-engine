#! /bin/bash

gen=5000
dir=/project/RIISVis/anguyen8/r/caffe_net/10_crops/2015-01-06-imagenet-conv-layer-1-to-5/conv_1/mmm/map_gen_$gen

mkdir tmpcrops

for ii in `seq 0 95`; do
    picname=`printf 'cropped_%03d.png' $ii`
    convert $dir/map_${gen}_${ii}_* -crop 11x11+122+122 tmpcrops/$picname
done

montage tmpcrops/cropped_???.png -mode concatenate -background '#333' -tile 10x10 -geometry +1+1 montage.png

rm -rf tmpcrops
