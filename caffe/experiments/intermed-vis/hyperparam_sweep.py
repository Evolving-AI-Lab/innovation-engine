#! /usr/bin/env python

from pylab import *
import os
import sys
import argparse

from loaders import *
from gradient_finder import *



def do_one_in_sweep(gf, hp_which, hp_frac, rand_seed, layer, unit_idx, start_at, prefix_template, brave=False):
    hp_frac = float(hp_frac)
    
    pp = FindParams()

    pp.rand_seed = rand_seed
    pp.push_layer = layer
    pp.unit_idx = unit_idx
    pp.start_at = start_at

    pp.decay = 0
    pp.max_iter = 1000
    pp.lr_policy = 'constant'
    pp.lr_params = {'lr': 100.0}
    pp.blur_radius = 0
    pp.blur_every = 0
    pp.small_norm_percentile = 0
    pp.px_abs_benefit_percentile = 0

    if hp_which == 0:
        pp.decay = .5 * hp_frac

    elif hp_which == 1:
        pp.blur_every = 4 + int((1-hp_frac)*6)
        pp.blur_radius = 1.0 * hp_frac

    elif hp_which == 2:
        pp.lr_policy = 'progress'
        pp.lr_params = {'max_lr': 100.0, 'desired_prog': 2.0}
        pp.px_abs_benefit_percentile = 95 * hp_frac

    elif hp_which == 3:
        pp.lr_policy = 'progress'
        pp.lr_params = {'max_lr': 100.0, 'desired_prog': 2.0}
        pp.small_norm_percentile = 95 * hp_frac

    else:
        raise Exception('bad hp_which %s ' % hp_which)

    im = gf.find_image(pp, prefix_template, brave=brave)



def main():
    parser = argparse.ArgumentParser(description='Hyperparam sweep')
    parser.add_argument('--result_prefix', type = str, default = './junk')
    parser.add_argument('--hp_which', type = int, default = 0, choices = (0, 1, 2, 3))      # 0, 1, 2, 3
    parser.add_argument('--hp_frac', type = float, default = 0.0)                           # 0..1
    parser.add_argument('--rand_seed_start', type = int, default = 0)
    parser.add_argument('--rand_seed_end', type = int, default = 1)
    parser.add_argument('--unit_idx', type = str, default = '278')
    parser.add_argument('--layer', type = str, default = 'prob')
    parser.add_argument('--startat', type = int, default = 0, choices = (0, 1))
    parser.add_argument('--brave', action = 'store_true')
    args = parser.parse_args()

    try:
        # int format
        unit_idx = (int(args.unit_idx), 0, 0)
    except ValueError:
        # (channel,x,y) format
        number_strs = args.unit_idx.strip()[1:-1].split(',')
        unit_idx = tuple([int(st) for st in number_strs])
        assert len(unit_idx) == 3
    start_at = 'mean_plus' if args.startat == 0 else 'randu'

    assert args.hp_frac >= 0 and args.hp_frac <= 1, 'hp_frac out of range'

    print 'loading mean...'
    sys.stdout.flush()
    imagenet_mean = load_imagenet_mean()
    print 'loading net...'
    net = load_trained_net()
    print 'loading labels...'
    labels = load_labels()
    gf = GradientFinder(net, imagenet_mean, labels)

    for rand_seed in xrange(args.rand_seed_start, args.rand_seed_end):
        unit_str = 'unit_%04d_%d_%d' % unit_idx
        per_seed_prefix = '%s/%s/hsweep%02d_%.4f/rs%04d_' % (args.layer, unit_str, args.hp_which, args.hp_frac, rand_seed)
        prefix_template = args.result_prefix + per_seed_prefix
        print 'Starting one optimization: %s' % prefix_template
        print 'Flushing stdout. Next message may be a while...'
        sys.stdout.flush()
        do_one_in_sweep(gf, args.hp_which, args.hp_frac, rand_seed, args.layer, unit_idx, start_at, prefix_template, brave=args.brave)
        print 'Finished one optimization: %s' % prefix_template
        sys.stdout.flush()

    print 'hyperparam_search.py: Finished with all optimizations.'
    sys.stdout.flush()


if __name__ == '__main__':
    main()
