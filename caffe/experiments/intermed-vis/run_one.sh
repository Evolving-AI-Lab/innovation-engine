#! /bin/bash -x

# Args like:
#   conv1 0030 hs0081
layer="$1"
unit="$2"
unit_short=$(($unit))
hs="$3"
hs_short=$(echo "$hs" | egrep -o '[1-9][0-9]*')
hs_short=275

case $layer in
    conv1 )
        xy="27,27";;
    conv2 )
        xy="13,13";;
    conv3 | conv4 | conv5 )
        xy="6,6";;
    fc6 | fc7 | fc8 | prob )
        xy="0,0";;
    * )
        echo "Unknown layer $layer"
        exit 1;;
esac

result_dir="results/150203_212645_2468771_priv_paper_all/$layer/"   # Add slash

seed_end=$((hs_short+1))

./hyperparam_search.py \
    --brave \
    --result_prefix $result_dir \
    --layer $layer \
    --unit_idx  "($unit,$xy)" \
    --hp_seed_start $hs_short \
    --hp_seed_end ${seed_end} \
    --rand_seed_start 0 \
    --rand_seed_end 9
