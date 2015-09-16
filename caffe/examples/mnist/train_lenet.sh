#!/usr/bin/env sh

./build/tools/caffe train --solver=examples/mnist/lenet_solver.prototxt \
 -weights=/project/EvolvingAI/anguyen8/caffe/examples/mnist/lenet_iter_10000.caffemodel
