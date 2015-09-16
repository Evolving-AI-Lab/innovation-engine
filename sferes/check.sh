#!/bin/bash
for i in {0..4}; do if [ -d run_${i} ]; then echo "run ${i} -----------" && echo "`ls run_${i}/mmm`"; fi; done
