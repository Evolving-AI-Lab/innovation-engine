#! /bin/bash

echo "Beginning Script."
echo "  Script dir:      `dirname $0`"
echo "  Script:          `basename $0`"
echo "  Date:            `date`"
echo "  Hostname:        `hostname`"
echo "  Starting in dir: `pwd`"
olddir="`pwd`"
cd $(dirname $0)
echo "  cd to dir:       `pwd`"
jobid="$PBS_JOBID"

echo "  python:          `which python`"
echo "  python env:"
env | grep -i python
echo "time to complete matrix multiplication (should be around 0.025)"
python -c "import numpy as N; import time;a=N.random.randn(800, 800); tic=time.time(); N.dot(a, a); print time.time()-tic;"
echo "Starting to run commands:"
echo

result_dir="$1"
layer="$2"
unit="$3"
#( for unit in 151 0 1 2 3 4 5 6 7 8; do
hp_seed_min="$4"
hp_seed_max="$5"
rand_seed_start="$6"   # 0
rand_seed_end="$7"     # 8

#set -x

( for hp_seed in `seq $hp_seed_min $hp_seed_max`; do
        #for rand_seed in `seq $rand_seed_start $rand_seed_end`; do
        echo "./hyperparam_search.py --brave --result_prefix $result_dir --layer $layer --unit_idx \"$unit\" --hp_seed_start $hp_seed --hp_seed_end $(($hp_seed + 1)) --rand_seed_start $rand_seed_start --rand_seed_end $(($rand_seed_end + 1))   > ${result_dir}/search.${jobid}.hp${hp_seed}.log 2>&1"
        #done
done ) | parallel -j 15 -t --joblog $result_dir/parallel.${jobid}.log
