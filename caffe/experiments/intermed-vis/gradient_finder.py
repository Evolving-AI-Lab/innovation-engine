#! /usr/bin/env python

import os
import errno
import pickle
import StringIO
from pylab import *
from scipy.ndimage.filters import gaussian_filter
#from collections import OrderedDict
#import ipdb as pdb
#%matplotlib inline
plt.rcParams['image.interpolation'] = 'nearest'
plt.rcParams['image.cmap'] = 'gray'

from plotting import *



def mkdir_p(path):
    # From https://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise



def combine_dicts(dicts_tuple):
    '''Combines multiple dictionaries into one by adding a prefix to keys'''
    ret = {}
    for prefix,dictionary in dicts_tuple:
        for key in dictionary.keys():
            ret['%s%s' % (prefix, key)] = dictionary[key]
    return ret
    
    
    
class FindParams(object):
    def __init__(self, **kwargs):
        default_params = dict(
            # Starting
            rand_seed = 0,
            start_at = 'mean_plus',
            
            # Optimization
            push_layer = 'prob',
            unit_idx = 278,
            push_dir = 1.0,
            decay = .01,
            blur_radius = None,   # 0 or at least .3
            blur_every = None,
            small_val_percentile = None,
            small_norm_percentile = None,
            px_benefit_percentile = None,
            px_abs_benefit_percentile = None,

            lr_policy = 'constant',
            lr_params = {'lr': 1.0},
            #lr_policy = 'progress',
            #lr_params = {'max_lr': 1e6, 'desired_prog': .5},

            # Terminating
            max_iter = 300)

        self.__dict__.update(default_params)

        for key,val in kwargs.iteritems():
            assert key in self.__dict__, 'Unknown param: %s' % key
            self.__dict__[key] = val

        self._validate_and_normalize()

    def _validate_and_normalize(self):
        if self.lr_policy == 'progress01':
            assert 'max_lr' in self.lr_params
            assert 'early_prog' in self.lr_params
            assert 'late_prog_mult' in self.lr_params
        elif self.lr_policy == 'progress':
            assert 'max_lr' in self.lr_params
            assert 'desired_prog' in self.lr_params
        elif self.lr_policy == 'constant':
            assert 'lr' in self.lr_params
        else:
            raise Exception('Unknown lr_policy: %s' % self.lr_policy)

        try:
            self.unit_idx = tuple(self.unit_idx)
        except TypeError:
            self.unit_idx = (self.unit_idx, 0, 0)   # int given
        assert len(self.unit_idx) == 3, 'provide unit_idx in the form: int or (channel, x, y) tuple'

        #print 'Bug here with _unit_channel (is not update when unit_idx changes)'
        #self._unit_channel = self.unit_idx[0]   # Useful when an int is needed and we don't care about spatial loction

    def __str__(self):
        ret = StringIO.StringIO()
        print >>ret, 'FindParams:'
        for key in sorted(self.__dict__.keys()):
            print >>ret, '%30s: %s' % (key, self.__dict__[key])
        return ret.getvalue()



class FindResults(object):
    def __init__(self):
        self.ii = []
        self.obj = []
        self.idxmax = []
        self.ismax = []
        self.norm = []
        self.dist = []
        self.std = []
        self.x0 = None
        self.majority_obj = None
        self.majority_xx = None
        self.best_obj = None
        self.best_xx = None
        self.last_obj = None
        self.last_xx = None
        self.meta_result = None
        
    def update(self, params, ii, acts, idxmax, xx, x0):
        assert params.push_dir > 0, 'push_dir < 0 not yet supported'
        
        self.ii.append(ii)
        self.obj.append(acts[params.unit_idx])
        self.idxmax.append(idxmax)
        self.ismax.append(idxmax == params.unit_idx)
        self.norm.append(norm(xx))
        self.dist.append(norm(xx-x0))
        self.std.append(xx.flatten().std())
        if self.x0 is None:
            self.x0 = x0.copy()

        # Snapshot when the unit first becomes the highest of its layer
        if params.unit_idx == idxmax and self.majority_xx is None:
            self.majority_obj = self.obj[-1]
            self.majority_xx = xx.copy()
            self.majority_ii = ii

        # Snapshot of best-ever objective
        if self.obj[-1] > self.best_obj:
            self.best_obj = self.obj[-1]
            self.best_xx = xx.copy()
            self.best_ii = ii

        # Snapshot of last
        self.last_obj = self.obj[-1]
        self.last_xx = xx.copy()
        self.last_ii = ii

    def trim_arrays(self):
        for key,val in self.__dict__.iteritems():
            if isinstance(val, ndarray):
                valstr = '%s array [%s, %s, ...]' % (val.shape, val.flatten()[0], val.flatten()[1])
                self.__dict__[key] = 'Trimmed %s' % valstr

    def __str__(self):
        ret = StringIO.StringIO()
        print >>ret, 'FindResults:'
        for key in sorted(self.__dict__.keys()):
            val = self.__dict__[key]
            if isinstance(val, list) and len(val) > 4:
                valstr = '[%s, %s, ..., %s, %s]' % (val[0], val[1], val[-2], val[-1])
            elif isinstance(val, ndarray):
                valstr = '%s array [%s, %s, ...]' % (val.shape, val.flatten()[0], val.flatten()[1])
            else:
                valstr = '%s' % val
            print >>ret, '%30s: %s' % (key, valstr)
        return ret.getvalue()



class GradientFinder(object):
    '''Finds images by gradient'''
    
    def __init__(self, net, data_mean, labels = None):
        self.net = net
        self.data_mean = data_mean
        self.labels = labels if labels else ['labels not provided' for ii in range(1000)]

        self._data_mean_img = self.data_mean[::-1].transpose((1,2,0))  # (227,227,3) in RGB order.

    def find_image(self, params, prefix_template = None, brave = False):
        '''All images are in Caffe format, e.g. shape (3, 227, 227) in BGR order.'''

        x0 = self._get_x0(params)
        xx, results = self._optimize(params, x0)
        self.save_results(params, results, prefix_template, brave = brave)

        print results.meta_result
        
        return xx

    def _get_x0(self, params):
        '''Chooses a starting location'''
        
        np.random.seed(params.rand_seed)

        if params.start_at == 'mean_plus':
            x0 = np.random.normal(0, 10, self.data_mean.shape)
        elif params.start_at == 'randu':
            x0 = uniform(0, 255, self.data_mean.shape) - self.data_mean
        elif params.start_at == 'zero':
            x0 = zeros(self.data_mean.shape)
        else:
            raise Exception('Unknown start conditions: %s' % params.start_at)

        return x0
        
    def _optimize(self, params, x0):
        xx = x0.copy()
        xx = xx[newaxis,:]

        results = FindResults()
        
        print '\nParameters:'
        print params
        #print '\nResults so far:'
        #print results
        
        # Whether or not the unit being optimized corresponds to one of the 1000 classes
        is_class_unit = params.push_layer in ('fc8', 'prob')
        if is_class_unit:
            assert params.unit_idx[1] == 0, 'trailing dims should be 0'
            assert params.unit_idx[2] == 0, 'trailing dims should be 0'
            push_label = self.labels[params.unit_idx[0]]
        else:
            push_label = None
        

        for ii in range(params.max_iter):
            # 0. Crop data
            xx = minimum(255.0, maximum(0.0, xx + self.data_mean)) - self.data_mean     # Crop all values to [0,255]


            # 1. Push data through net
            out = self.net.forward_all(data = xx)
            #shownet(net)

            acts = self.net.blobs[params.push_layer].data[0]    # chop off batch dimension
            idxmax = unravel_index(acts.argmax(), acts.shape)
            # idxmax for fc or prob layer will be like:  (278, 0, 0)
            # idxmax for conv layer will be like:        (37, 4, 37)
            obj = acts[params.unit_idx]

            
            # 3. Update results
            results.update(params, ii, acts, idxmax, xx[0], x0)

            
            # 2. Print progress STILL MESSY
            if ii > 0 and params.lr_policy == 'progress':
                print '   pred_prog: ', pred_prog, 'actual:', obj - old_obj
            if is_class_unit:
                print '%-4d' % ii, 'Unit idx: %d, val: %g (%s)\n      Max idx: %d, val: %g (%s)' % (params.unit_idx[0], acts[params.unit_idx], push_label, idxmax[0], acts.max(), self.labels[idxmax[0]])
            else:
                print '%-4d' % ii, 'Unit idx: %s, val: %g\n      Max idx: %s, val: %g' % (params.unit_idx, acts[params.unit_idx], idxmax, acts.max())
            print '         X: ', xx.min(), xx.max(), norm(xx)



            
            diffs = self.net.blobs[params.push_layer].diff * 0
            diffs[0][params.unit_idx] = params.push_dir
            #backout = net.backward(prob = probdiffs)
            backout = self.net.backward_from_layer(params.push_layer, diffs)
            #diffs = net.deprocess('data', backout['data'])   # converts bgr -> rgb

            grad = backout['data'].copy()
            #rms = sqrt((grad**2).mean())
            #nrmgrad = grad / (rms + 1e-6)
            #left_to_go = 1 - acts[params.unit_idx]   # How close we are to 1.0 probability
            #denom_normalizing_constant = min(100, 1 / (100*left_to_go + 1e-12))   # 1/100 when ltg = 1, 100 when ltg = 0
            #nrmgrad = grad / (abs(grad).max() + denom_normalizing_constant)
            #nrmgrad = grad * 255 / (abs(grad).max() + 1e-12)
            #nrmgrad = grad
            print '      grad:', grad.min(), grad.max(), norm(grad)
            if norm(grad) == 0:
                print 'Grad 0, failed'
                results.meta_result = 'Metaresult: grad 0 failure'
                break
            #print '       dnc:', denom_normalizing_constant
            #print '   nrmgrad:', nrmgrad.min(), nrmgrad.max(), norm(nrmgrad), 'scaled by', 1/(abs(grad).max())

            # progress-based lr
            if params.lr_policy == 'progress01':
                late_prog = params.lr_params['late_prog_mult'] * (1-obj)
                desired_prog = min(params.lr_params['early_prog'], late_prog)
                prog_lr = desired_prog / norm(grad)**2
                lr = min(params.lr_params['max_lr'], prog_lr)
                print '    desired_prog:', desired_prog, 'prog_lr:', prog_lr, 'lr:', lr
                pred_prog = lr * dot(grad.flatten(), grad.flatten())
            elif params.lr_policy == 'progress':
                prog_lr = params.lr_params['desired_prog'] / norm(grad)**2
                lr = min(params.lr_params['max_lr'], prog_lr)
                print '    desired_prog:', params.lr_params['desired_prog'], 'prog_lr:', prog_lr, 'lr:', lr
                pred_prog = lr * dot(grad.flatten(), grad.flatten())
            elif params.lr_policy == 'constant':
                lr = params.lr_params['lr']
            else:
                raise Exception('Unimlemented lr_policy')

            print '     change size:', abs(lr * grad).max()
            old_obj = obj

            #print results

            if ii < params.max_iter-1:
                xx += lr * grad
                xx *= (1 - params.decay)

                if params.blur_radius > 0:
                    if params.blur_radius < .3:
                        print 'Warning: blur-radius of .3 or less works very poorly'
                        #raise Exception('blur-radius of .3 or less works very poorly')
                    #oldX = xx.copy()
                    if params.blur_every is not None and ii % params.blur_every == 0:
                        for channel in range(3):
                            cimg = gaussian_filter(xx[0,channel], params.blur_radius)
                            xx[0,channel] = cimg
                        #print '  **max change:', abs(xx-oldX).max()

                        #print 'maxes: old X, X, cimg', oldX[0,2].max(), X[0,2].max(), cimg.max()
                        #pdb.set_trace()
                if params.small_val_percentile > 0:
                    small_entries = (abs(xx) < percentile(abs(xx), params.small_val_percentile))
                    xx = xx - xx*small_entries   # set smallest 50% of xx to zero

                if params.small_norm_percentile > 0:
                    pxnorms = norm(xx, axis=1)
                    smallpx = pxnorms < percentile(pxnorms, params.small_norm_percentile)
                    smallpx3 = tile(smallpx[:,newaxis,:,:], (1,3,1,1))
                    xx = xx - xx*smallpx3

                if params.px_benefit_percentile > 0:
                    pred_0_benefit = grad * -xx
                    px_benefit = pred_0_benefit.sum(1)
                    smallben = px_benefit < percentile(px_benefit, params.px_benefit_percentile)
                    smallben3 = tile(smallben[:,newaxis,:,:], (1,3,1,1))
                    #pdb.set_trace()
                    xx = xx - xx*smallben3

                if params.px_abs_benefit_percentile > 0:
                    pred_0_benefit = grad * -xx
                    px_benefit = pred_0_benefit.sum(1)
                    smallaben = abs(px_benefit) < percentile(abs(px_benefit), params.px_abs_benefit_percentile)
                    smallaben3 = tile(smallaben[:,newaxis,:,:], (1,3,1,1))
                    xx = xx - xx*smallaben3

        if results.meta_result is None:
            if results.majority_obj is not None:
                results.meta_result = 'Metaresult: majority success'
            else:
                results.meta_result = 'Metaresult: majority failure'

        return xx, results

    def save_results(self, params, results, prefix_template, brave = False):
        if prefix_template is None:
            return

        results_and_params = combine_dicts((('p.', params.__dict__),
                                            ('r.', results.__dict__)))
        prefix = prefix_template % results_and_params
        
        if os.path.isdir(prefix):
            if prefix[-1] != '/':
                prefix += '/'   # append slash for dir-only template
        else:
            dirname = os.path.dirname(prefix)
            if dirname:
                mkdir_p(dirname)

        # Don't overwrite previous results
        if os.path.exists('%sinfo.txt' % prefix) and not brave:
            raise Exception('Cowardly refusing to overwrite ' + '%sinfo.txt' % prefix)

        if results.majority_xx is not None:
            asimg = results.majority_xx[::-1].transpose((1,2,0))
            saveimagescc('%smajority_X.jpg' % prefix, asimg, 0)
            saveimagesc('%smajority_Xpm.jpg' % prefix, asimg + self._data_mean_img)

        if results.best_xx is not None:
            asimg = results.best_xx[::-1].transpose((1,2,0))
            saveimagescc('%sbest_X.jpg' % prefix, asimg, 0)
            saveimagesc('%sbest_Xpm.jpg' % prefix, asimg + self._data_mean_img)

        with open('%sinfo.txt' % prefix, 'w') as ff:
            print >>ff, params
            print >>ff
            print >>ff, results
        with open('%sinfo_big.pkl' % prefix, 'w') as ff:
            pickle.dump((params, results), ff, protocol=-1)
        results.trim_arrays()
        with open('%sinfo.pkl' % prefix, 'w') as ff:
            pickle.dump((params, results), ff, protocol=-1)
