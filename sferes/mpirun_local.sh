#!/bin/bash

rm -rf mmm
rm err.log output.log

echo "Removed log files."

echo "Running..."
mpirun --mca mpi_leave_pinned 0 --mca mpi_warn_on_fork 0 -np 4 ./build/debug/exp/images/images 1 2> /home/anh/workspace/sferes/err.log
