#! /bin/bash

function maketopbot() {
    name="$1"; shift
    layer="$1"; shift
    topbot="$1"; shift
    units=""
    while [ "$1" != "" ]; do
        units+=" `printf '%04d' $1`"; shift
    done
    echo "units is $units"

    bigdir=results/150203_212645_2468771_priv_paper_all/$layer/$layer
    cd $bigdir
    finished=""
    for unit in $units; do
        finished+=" `ls unit_$unit*/*montage.jpg`"
    done
    finished="$(echo $finished | sed -e 's/^ *//' -e 's/ *$//')"
    echo "Finished: $finished"
    if [ "$finished" != "" ]; then
        montage $finished -mode concatenate -background '#333' -geometry +2+2 ${name}_${layer}_${topbot}_montage.jpg
        echo "Created montage:  ${name}_${layer}_${topbot}_montage.jpg"
    else
        echo "No files to make: ${name}_${layer}_${topbot}_montage.jpg"
    fi
    cd -
}

# Unicycle
maketopbot unicycle fc7   top   1435 3307 3875 3120 3145
maketopbot unicycle fc7   bot   3634 681 2612 1829 4083
maketopbot unicycle fc6   top   2703 3552 1081 436 953
maketopbot unicycle fc6   bot   3804 3696 3433 2248 2057
maketopbot unicycle conv5 top   29 55 96 15 75
maketopbot unicycle conv5 bot   11 233 128 141 65
maketopbot unicycle conv4 top   17 55 68 130 77
maketopbot unicycle conv4 bot   183 32 24 280 252
maketopbot unicycle conv3 top   94 76 17 13 12
maketopbot unicycle conv3 bot   161 290 79 65 252
maketopbot unicycle conv2 top   129 158 250 153 54
maketopbot unicycle conv2 bot   231 50 17 36 194
maketopbot unicycle conv1 top   67 53 90 56 48
maketopbot unicycle conv1 bot   95 51 57 75 65

# Tricycle
maketopbot tricycle fc7   top   129 1828 4040 730 565 
maketopbot tricycle fc7   bot   3138 2053 2754 3800 3708
maketopbot tricycle fc6   top   1348 1464 1207 600 331 
maketopbot tricycle fc6   bot   3651 631 167 3804 2596
maketopbot tricycle conv5 top   202 82 26 43 88 
maketopbot tricycle conv5 bot   117 24 106 21 126
maketopbot tricycle conv4 top   13 68 356 38 90 
maketopbot tricycle conv4 bot   115 247 12 266 114
maketopbot tricycle conv3 top   125 308 98 295 122 
maketopbot tricycle conv3 bot   231 22 42 74 37
maketopbot tricycle conv2 top   80 90 194 36 12 
maketopbot tricycle conv2 bot   169 124 70 216 96
maketopbot tricycle conv1 top   31 19 2 56 22 
maketopbot tricycle conv1 bot   12 29 18 39 52
