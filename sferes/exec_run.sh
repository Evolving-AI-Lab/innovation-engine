#!/bin/bash
if [ "$#" -eq 2 ]; then
  ./build/default/exp/$1/$1 $2
elif [ "$#" -eq 3 ]; then 
  ./build/default/exp/$1/$2 $3
fi
