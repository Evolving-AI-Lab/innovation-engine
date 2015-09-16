#! /bin/bash 

qsub -N slave -A EvolvingAI -l nodes=1:ppn=1 -l walltime=168:00:00 -d . ./bound_worker.sh
