#!/usr/bin/env sh

./build/tools/caffe test \
 -weights=/project/EvolvingAI/anguyen8/caffe/examples/mnist/lenet_iter_10000.caffemodel \
 -model=/project/EvolvingAI/anguyen8/caffe/examples/mnist/lenet_train_test_x.prototxt
