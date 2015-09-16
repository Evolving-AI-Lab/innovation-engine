#! /usr/bin/env python

from pylab import *

# Make sure that caffe is on the python path:
caffe_root = '../../'  # this file is expected to be in {caffe_root}/experiments/something
import sys
sys.path.insert(0, caffe_root + 'python')
import caffe



def load_labels():
    with open('%s/data/ilsvrc12/synset_words.txt' % caffe_root) as ff:
        labels = [line.strip() for line in ff.readlines()]
    return labels


    
def load_trained_net(model_prototxt = None, model_weights = None):
    assert (model_prototxt is None) == (model_weights is None), 'Specify both model_prototxt and model_weights or neither'
    if model_prototxt is None:
        load_dir = '/home/jyosinsk/results/140311_234854_afadfd3_priv_netbase_upgraded/'
        model_prototxt = load_dir + 'deploy_1.prototxt'
        model_weights = load_dir + 'caffe_imagenet_train_iter_450000'

    net = caffe.Classifier(model_prototxt, model_weights, caffe.TEST)
    #net.set_phase_test()
    #net.set_mode_cpu()

    return net


    
def load_imagenet_mean():
    imagenet_mean = np.load(caffe_root + 'python/caffe/imagenet/ilsvrc_2012_mean.npy')
    imagenet_mean = imagenet_mean[:, 14:14+227, 14:14+227]    # (3,256,256) -> (3,227,227) Crop to center 227x227 section
    return imagenet_mean
