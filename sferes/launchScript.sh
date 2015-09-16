#!/bin/bash

#Do not edit. File automatically generated

#SBATCH --ntasks=128
#SBATCH --nodes=8
#SBATCH -A EvolvingAI 
#SBATCH -t 120:00:00        # run time (hh:mm:ss) - 48 hours 
#SBATCH --mail-user=anguyen8@uwyo.edu 
#SBATCH --mail-type=begin  # email me when the job starts 
#SBATCH --mail-type=end    # email me when the job finishes 
module load gnu/4.8.3
module load openmpi/1.8.4
seed_number="${1}" 
experimentDir="${2}" 
export OMPI_MCA_orte_tmpdir_base=/gscratch/EvolvingAI/anguyen8/log/$SLURM_JOBID 
export TEST_TMPDIR=/gscratch/EvolvingAI/anguyen8/log/$SLURM_JOBID 
export TMPDIR=/gscratch/EvolvingAI/anguyen8/log/$SLURM_JOBID 
export TMP=/gscratch/EvolvingAI/anguyen8/log/$SLURM_JOBID 
mkdir /gscratch/EvolvingAI/anguyen8/log/$SLURM_JOBID 
echo "Changing to directory: " $experimentDir
cd $experimentDir

echo " /project/EvolvingAI/anguyen8/x/all_layers/build/default/exp/images/images_sine $seed_num  > thisistheoutput 2> err.log" > runToBe
srun /project/EvolvingAI/anguyen8/x/all_layers/build/default/exp/images/images_sine $seed_num  > output.log 2> err.log
rm -rf /gscratch/EvolvingAI/anguyen8/log/$SLURM_JOBID 

echo "Done with run"
