#! /bin/bash

# Instructions:
#   - Change result_dir
#   - Pick layer, units, hp_seed_range
#   - Make sure to select correct x,y unit in the given channel!
#       conv1   unit 27,27
#       conv2   unit 13,13
#       conv3   unit 6,6
#       conv4   unit 6,6
#       conv5   unit 6,6
#       others  unit 0,0


basedir=results/150203_212645_2468771_priv_paper_all/
required_dirs="hs0081 hs0141 hs0275 hs0287"

check_layer() {

    layer="$1"
    nunits="$2"

    here=`pwd`
    cd $basedir/$layer/$layer

    for unitid in `seq -f %04g 0 $(($nunits - 1))`; do
    #for unitid in 0029 0030 0031; do
        for dd in $required_dirs; do
            missing=0
            for ii in `seq -f %04g 0 8`; do
                filename=unit_${unitid}_*/$dd/rs${ii}_best_X.jpg
                #ls $filename || echo "Missing $filename"
                identify $filename 2>/dev/null | grep 227 >/dev/null || missing=1    #echo "Missing: $unitid Bad $filename"
            done
            if [ $missing = 1 ]; then
                echo "Missing: $layer $unitid $dd"
            fi
        done
    done

    cd "$here"
}

check_layer conv1   96
check_layer conv2  256
check_layer conv3  384
check_layer conv4  384
check_layer conv5  256
check_layer fc8   1000
check_layer prob  1000
check_layer fc6   4096
check_layer fc7   4096
