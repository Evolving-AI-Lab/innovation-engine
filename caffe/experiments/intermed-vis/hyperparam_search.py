#! /usr/bin/env python

from pylab import *
import os
import sys
import argparse

from loaders import *
from gradient_finder import *



def rchoose(choices, prob=None):
    if prob is None:
        prob = ones(len(choices))
    prob = array(prob, dtype='float')
    return np.random.choice(choices, p=prob/prob.sum())



def do_one(gf, hp_seed, rand_seed, layer, unit_idx, start_at, prefix_template, brave=False):
    pp = FindParams()

    pp.rand_seed = rand_seed
    pp.push_layer = layer
    pp.unit_idx = unit_idx
    pp.start_at = start_at
    
    if hp_seed == -1:
        # Special hp_seed of -1 to do gradient descent without any regularization
        pp.decay = 0
        pp.max_iter = 500
        #pp.early_prog = .02
        #pp.late_prog_mult = .1
        pp.lr_policy = 'constant'
        pp.lr_params = {'lr': 1.0}
        pp.blur_radius = 0
        pp.blur_every = 1
        pp.small_norm_percentile = 0
        pp.small_val_percentile = 0
        pp.px_benefit_percentile = 0
        pp.px_abs_benefit_percentile = 0
    else:
        np.random.seed(hp_seed)

        # Choose hyperparameter values given this seed
        pp.decay = rchoose((0, .0001, .001, .01, .1, .2, .3),
                           (4,     1,    1,   2,  1,  1,  1))
        pp.max_iter = rchoose((250, 500, 750, 1000, 1500))     # maybe higher vals?
        #early_prog = rchoose(
        #    (.02, .03, .04),
        #    (1, 2, 1))
        #late_prog_mult = rchoose((.02, .05, .1, .2))
        pp.blur_radius = rchoose(
            (0, .3, .4, .5, 1.0),
            (10, 2,  1,  1,  1))
        pp.blur_every = rchoose((1, 2, 3, 4))          # should add higher values (see 275)
        pp.small_val_percentile = 0
        pp.small_norm_percentile = rchoose(
            (0, 10, 20, 30, 50, 80, 90),
            (10, 10, 5, 2,  2,  2,  2))
        pp.px_benefit_percentile = rchoose(            # should eliminate this one (set to 0)
            (0,  10, 20, 30, 50, 80, 90),
            (20, 10,  5,  2,  2,  2,  2))
        pp.px_abs_benefit_percentile = rchoose(
            (0,  10, 20, 30, 50, 80, 90),
            (10, 10,  5,  2,  2,  2,  2))
        pp.lr_policy = rchoose(
            ('progress', 'constant'),
            (10, 5))
        if pp.lr_policy == 'constant':
            pp.lr_params = {'lr': rchoose((.001, .01, .1, 1, 10, 100))}      # should add higher options (see 275)
        elif pp.lr_policy == 'progress':
            max_lr = rchoose(
                (1e2, 1e4, 1e6, 1e8))
            desired_prog = rchoose(
                (.1, .2, .5, 1.0, 2.0, 5.0))
            pp.lr_params = {'max_lr': max_lr, 'desired_prog': desired_prog}
        else:
            raise Exception('unknown lr_policy')

    im = gf.find_image(pp, prefix_template, brave=brave)



def main():
    parser = argparse.ArgumentParser(description='Hyperparam search')
    parser.add_argument('--result_prefix', type = str, default = './junk')
    parser.add_argument('--hp_seed_start', type = int, default = 0)
    parser.add_argument('--hp_seed_end', type = int, default = 1)
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

    print 'loading mean...'
    sys.stdout.flush()
    imagenet_mean = load_imagenet_mean()
    print 'loading net...'
    net = load_trained_net()
    print 'loading labels...'
    labels = load_labels()
    gf = GradientFinder(net, imagenet_mean, labels)

    for hp_seed in xrange(args.hp_seed_start, args.hp_seed_end):
        for rand_seed in xrange(args.rand_seed_start, args.rand_seed_end):
            unit_str = 'unit_%04d_%d_%d' % unit_idx
            per_seed_prefix = '%s/%s/hs%04d/rs%04d_' % (args.layer, unit_str, hp_seed, rand_seed)
            prefix_template = args.result_prefix + per_seed_prefix
            print 'Starting one optimization: %s' % prefix_template
            print 'Flushing stdout. Next message may be a while...'
            sys.stdout.flush()
            do_one(gf, hp_seed, rand_seed, args.layer, unit_idx, start_at, prefix_template, brave=args.brave)
            print 'Finished one optimization: %s' % prefix_template
            sys.stdout.flush()

    print 'hyperparam_search.py: Finished with all optimizations.'
    sys.stdout.flush()


if __name__ == '__main__':
    main()
