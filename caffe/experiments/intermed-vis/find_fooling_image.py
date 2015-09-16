#! /usr/bin/env python

import argparse

from loaders import *
from gradient_finder import *



def main():
    parser = argparse.ArgumentParser(description='Finds images that activate a network in various ways.')
    parser.add_argument('--lr', type = float, default = .01)
    parser.add_argument('--decay', type = float, default = .01)
    parser.add_argument('--N', type = int, default = 300)
    parser.add_argument('--rseed', type = int, default = 0)
    parser.add_argument('--push_idx', type = str, default = '278')
    parser.add_argument('--push_layer', type = str, default = 'prob')
    parser.add_argument('--start_at', type = str, default = 'mean_plus')
    #parser.add_argument('--prefix', type = str, default = 'junk_%(p._unit_channel)04d_')
    parser.add_argument('--prefix', type = str, default = 'junk_')
    args = parser.parse_args()

    try:
        # int format
        push_idx = int(args.push_idx)
    except ValueError:
        # (channel,x,y) format
        number_strs = args.push_idx.strip()[1:-1].split(',')
        push_idx = tuple([int(st) for st in number_strs])
        assert len(push_idx) == 3

    net = load_trained_net()
    imagenet_mean = load_imagenet_mean()
    labels = load_labels()

    params = FindParams(push_layer = args.push_layer,
                        max_iter = args.N,
                        decay = args.decay,
                        lr_policy = 'constant',
                        lr_params = {'lr': args.lr},
                        start_at = args.start_at)

    gf = GradientFinder(net, imagenet_mean, labels)

    im = gf.find_image(params, args.prefix)



if __name__ == '__main__':
    main()
