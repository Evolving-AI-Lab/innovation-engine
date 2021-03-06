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

#layer=conv1
#layer=conv2
#layer=conv3
#layer=conv4
#layer=conv5
#layer=fc6
#layer=fc7
layer=fc8
#layer=prob

case $layer in
    conv1 )
        #result_dir="results/150202_151620_6eaf854_priv_hp_search_0_conv1"
        xy="27,27"    # conv1
        #units="20 43 56"
        unit_starts="`seq 0 10 95`"
        ;;
    conv2 )
        #result_dir="results/150203_204913_1cf3a8c_priv_hp_search_0_conv2"
        xy="13,13"    # conv2
        unit_starts="`seq 0 10 255`"
        ;;
    conv3 )
        #result_dir="results/150203_204917_1cf3a8c_priv_hp_search_0_conv3"
        xy="6,6"
        #units="`seq 0 9` `seq 192 201`"
        #unit_starts="`seq 0 10 383`"
        units="94 76 17 13 12 161 290 79 65 252"
        ;;
    conv4 )
        #result_dir="results/150203_204920_1cf3a8c_priv_hp_search_0_conv4"
        xy="6,6"
        #units="`seq 0 9` `seq 192 201`"
        #unit_starts="`seq 0 10 383`"
        units="17 55 68 130 77 183 32 24 280 252"
        ;;
    conv5 )
        #result_dir="results/150202_152747_6eaf854_priv_hp_search_0_conv5"
        xy="6,6"      # conv345
        #units="151 4 0 1 2"
        #unit_starts="`seq 0 10 255`"
        #units="29 55 96 15 75 11 233 128 141 65"
        #units="113 111 153 255"
        units="202 82 26 43 88 117 24 106 21 126"
        ;;
    fc6 )
        #result_dir="results/150203_204924_1cf3a8c_priv_hp_search_0_fc6"
        xy="0,0"
        units="`seq 10 39`"
        #unit_starts="`seq 0 10 4095`"
        #unit_starts="`seq 0 10 19`"
        #units="2703 3552 1081 436 953 3804 3696 3433 2248 2057"
        units="1348 1464 1207 600 331  3651 631 167 2596"
        ;;
    fc7 )
        #result_dir="results/150203_204928_1cf3a8c_priv_hp_search_0_fc7"
        xy="0,0"
        units="`seq 10 39`"
        #unit_starts="`seq 0 10 4095`"
        #unit_starts="`seq 0 10 19`"
        #units="1435 3307 3875 3120 3145 3634 681 2612 1829 4083"
        units="3138 2053 2754 3800 3708 129 1828 4040 730 565"
        ;;
    fc8 )
        #result_dir="results/150202_151936_6eaf854_priv_hp_search_0_fc8"
        xy="0,0"
        #units="278 366 704 906 444 870 880"
        #unit_starts="`seq 0 10 999`"
        #units="402 409 414 426 436 437 445 454 468 484 504 527 540 547 555 575 607 624 627 642 655 665 670 671 679 698 717 724 725 736 765 779 817 839 850 916 917 919 920"
        units="285 508"
        ;;
    prob )
        #result_dir="results/150203_204934_1cf3a8c_priv_hp_search_0_prob"
        xy="0,0"
        #units="278 366 704 906"
        units="278 366 704 906 444 870 880"
        #unit_starts="`seq 0 10 19`"
        #unit_starts="`seq 0 10 999`"
        ;;
    * )
        echo "Unknown layer $layer"
        exit 1
        ;;
esac

result_dir="results/150203_212645_2468771_priv_paper_all/$layer/"   # Add slash

if [ "$units" = "" ]; then

    for unit_start in $unit_starts; do
        #for unit in $units; do
        #for hp_seed in 296; do
        #for hp_seed in 275 287 141 81; do
        for hp_seed in 275 287; do
            #for hp_seed in `seq 200 10 290`; do
            #for hp_seed in `seq 0 1`; do
            #for hp_seed in `seq 0 99`; do
            hp_seed_min=$hp_seed
            hp_seed_max=$(($hp_seed + 0))    # inclusive
            rand_seed_start=0
            rand_seed_end=8
            
            jobname=${layer}_${unit_start}_${hp_seed}_`datestamp -n`
            jobscript=$result_dir/$jobname.sh
            echo "#! /bin/bash" > $jobscript
            for unit in `seq $unit_start $(($unit_start + 9))`; do
                echo "$HOME/s/caffe/experiments/intermed-vis/1_run_hyperparam_search.sh $result_dir $layer \"($unit,$xy)\" $hp_seed_min $hp_seed_max $rand_seed_start $rand_seed_end 2>&1" >> $jobscript
            done
            chmod +x $jobscript
            
            qsub -N "$jobname" -A EvolvingAI -l nodes=1:ppn=16 -l walltime=24:00:00 -d $result_dir $jobscript || ( echo "fail"; exit 1 )
            echo "Submitted $jobname"

            #qstat -u `whoami`
            sleep .1
        done
    done

else

    for unit in $units; do
        #for hp_seed in 296; do
        for hp_seed in 275 287 141 81; do
            #for hp_seed in `seq 200 10 290`; do
            #for hp_seed in `seq 0 1`; do
            #for hp_seed in `seq 0 99`; do
            hp_seed_min=$hp_seed
            hp_seed_max=$(($hp_seed + 0))    # inclusive
            rand_seed_start=0
            rand_seed_end=8
            
            jobname=j${layer}_${unit}_${hp_seed}_`datestamp -n`
            jobscript=$result_dir/$jobname.sh
            echo "#! /bin/bash" > $jobscript
            echo "$HOME/s/caffe/experiments/intermed-vis/1_run_hyperparam_search.sh $result_dir $layer \"($unit,$xy)\" $hp_seed_min $hp_seed_max $rand_seed_start $rand_seed_end 2>&1" >> $jobscript
            chmod +x $jobscript
            
            qsub -N "$jobname" -A EvolvingAI -l nodes=1:ppn=16 -l walltime=6:00:00 -d $result_dir $jobscript || ( echo "fail"; exit 1 )
            echo "Submitted $jobname"

            #qstat -u `whoami`
            sleep .01
        done
    done

fi

