#! /bin/bash

for ii in `seq 0 299`; do
    hs=`printf 'hs%04d' $ii`
    inputfiles=`ls results/{150202_151620_6eaf854_priv_hp_search_0_conv1/conv1,150202_152747_6eaf854_priv_hp_search_0_conv5/conv5,150202_151936_6eaf854_priv_hp_search_0_fc8/fc8}/unit*/$hs/montage.jpg`
    montage $inputfiles -mode concatenate -background '#333' -tile 4x3 -geometry +1+1 results/150203_000000_6eaf854_priv_hp_search_0_metamontage/meta_montage_$hs.jpg
    echo meta_montage_$hs.jpg
done

