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
hp_which="$4"
hp_frac="$5"
rand_seed_start="$6"   # 0
rand_seed_end="$7"     # 8

set -x

./hyperparam_sweep.py --brave --result_prefix $result_dir --layer $layer --unit_idx "$unit" --hp_which $hp_which --hp_frac $hp_frac --rand_seed_start $rand_seed_start --rand_seed_end $(($rand_seed_end + 1))   #> ${result_dir}/sweep.${jobid}.hw${hp_which}.${hp_frac}.log 2>&1
