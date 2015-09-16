#! /bin/bash

#gen=5000
#dir=/project/RIISVis/anguyen8/r/caffe_net/10_crops/2015-01-06-imagenet-conv-layer-1-to-5/conv_1/mmm/map_gen_$gen
#size=11
#offset=$((108  + 14))

function make_montage() {
    dir="$1"
    size="$2"
    offset="$3"
    num="$4"
    tile="$5"
    outname="$6"

    tmpdir="tmp_`rand | cut -c 4-10`"
    mkdir $tmpdir

    for ii in `seq 0 $(($num - 1))`; do
        picname=`printf 'cropped_%05d.png' $ii`

        # Old working version
        #convert $dir/map_${gen}_${ii}_* -crop 11x11+122+122 $tmpdir/$picname

        # Normal
        #convert $dir/map_${gen}_${ii}_* -crop 227x227+14+14 +repage $tmpdir/$picname
        #convert $tmpdir/$picname       -crop 11x11+108+108 +repage $tmpdir/$picname
        
        # Faster
        convert $dir/map_${gen}_${ii}_* -crop ${size}x${size}+${offset}+${offset} +repage $tmpdir/$picname

        # Hack
        #convert $dir/map_${gen}_${ii}_* -crop 100x100+78+78 $tmpdir/$picname
    done

    montage $tmpdir/cropped_?????.png -mode concatenate -background '#333' -tile $tile -geometry +1+1 "$outname"

    rm -rf $tmpdir

    echo "Created $outname"
}

prefix=/project/RIISVis/anguyen8/r/caffe_net/10_crops

for gen in 0 1000 2000 3000 4000 5000; do
#    make_montage $prefix/2015-01-06-imagenet-conv-layer-1-to-5/conv_1/mmm/map_gen_${gen}/ 11  $((108 +14))  96 10x10 `printf montage_conv1_%05d.png $gen`
#    make_montage $prefix/2015-01-06-imagenet-conv-layer-1-to-5/conv_2/mmm/map_gen_${gen}/ 51  $((88  +14)) 256 16x16 `printf montage_conv2_%05d.png $gen`
#    make_montage $prefix/2015-01-06-imagenet-conv-layer-1-to-5/conv_3/mmm/map_gen_${gen}/ 99  $((64  +14)) 384 20x20 `printf montage_conv3_%05d.png $gen`
#    make_montage $prefix/2015-01-06-imagenet-conv-layer-1-to-5/conv_4/mmm/map_gen_${gen}/ 131 $((48  +14)) 384 20x20 `printf montage_conv4_%05d.png $gen`
#    make_montage $prefix/2015-01-06-imagenet-conv-layer-1-to-5/conv_5/mmm/map_gen_${gen}/ 163 $((32  +14)) 256 16x16 `printf montage_conv5_%05d.png $gen`
    echo
done

#for gen in `seq 0 1000 20000`; do
for gen in 19000 10000 5000; do
#    make_montage $prefix/2015-01-13-imagenet-fc-layer-6-to-8/fc_6/map_gen_${gen}/     227 14  4096 64x64  `printf montage_fc6_%05d.png $gen`
#    make_montage $prefix/2015-01-13-imagenet-fc-layer-6-to-8/fc_7/mmm/map_gen_${gen}/ 227 14  4096 64x64  `printf montage_fc7_%05d.png $gen`
#    make_montage $prefix/2015-01-13-imagenet-fc-layer-6-to-8/fc_8/map_gen_${gen}/     227 14  1000 32x32  `printf montage_fc8_%05d.png $gen`
    echo
done
