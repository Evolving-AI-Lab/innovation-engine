#! /usr/bin/env python

from pylab import *



def figsize(width,height):
    rcParams['figure.figsize'] = (width,height)



def norm01(arr):
    arr = arr.copy()
    arr -= arr.min()
    arr /= arr.max()
    return arr



def norm01c(arr, center):
    '''Maps the center value to .5'''
    arr = arr.copy()
    arr -= center
    arr /= max(2 * arr.max(), -2 * arr.min())
    arr += .5
    assert arr.min() >= 0
    assert arr.max() <= 1
    return arr



def showimage(im, c01=False, bgr=False, axes=None):
    if c01:
        # switch order from c,0,1 -> 0,1,c
        im = im.transpose((1,2,0))
    if im.ndim == 3 and bgr:
        # Change from BGR -> RGB
        im = im[:, :, ::-1]
    if axes is None:
        plt.imshow(im)
    else:
        axes.imshow(im)
    #axis('tight')

def showimagesc(im, c01=False, bgr=False, center=None, axes=None):
    if center is None:
        showimage(norm01(im), c01=c01, bgr=bgr, axes=axes)
    else:
        showimage(norm01c(im, center), c01=c01, bgr=bgr, axes=axes)



def saveimage(filename, im):
    matplotlib.image.imsave(filename, im)

def saveimagesc(filename, im):
    saveimage(filename, norm01(im))

def saveimagescc(filename, im, center):
    saveimage(filename, norm01c(im, center))



def tile_images(data, padsize=1, padval=0, c01=False, width=None):
    '''take an array of shape (n, height, width) or (n, height, width, channels)
    and visualize each (height, width) thing in a grid. If width = None, produce
    a square image of size approx. sqrt(n) by sqrt(n), else calculate height.'''
    data = data.copy()
    if c01:
        # Convert c01 -> 01c
        data = data.transpose(0, 2, 3, 1)
    data -= data.min()
    data /= data.max()
    
    # force the number of filters to be square
    if width == None:
        width = int(np.ceil(np.sqrt(data.shape[0])))
        height = width
    else:
        assert isinstance(width, int)
        height = int(np.ceil(float(data.shape[0]) / width))
    padding = ((0, width*height - data.shape[0]), (0, padsize), (0, padsize)) + ((0, 0),) * (data.ndim - 3)
    data = np.pad(data, padding, mode='constant', constant_values=(padval, padval))
    
    # tile the filters into an image
    data = data.reshape((height, width) + data.shape[1:]).transpose((0, 2, 1, 3) + tuple(range(4, data.ndim + 1)))
    data = data.reshape((height * data.shape[1], width * data.shape[3]) + data.shape[4:])
    data = data[0:-padsize, 0:-padsize]  # remove excess padding
    
    return data



def vis_square(data, padsize=1, padval=0, c01=False):
    data = tile_images(data, padsize, padval, c01)
    showimage(data, c01=False)



def looser(ax, xfrac = .05, yfrac=None, semilogx = False, semilogy = False, loglog = False):
    '''Returns a loosened version of the axies specified in ax'''

    ax = list(ax)

    if yfrac is None:
        yfrac = xfrac
        
    if loglog:
        semilogx = True
        semilogy = True

    if semilogx:
        ax[0] = log(ax[0])
        ax[1] = log(ax[1])
    if semilogy:
        ax[2] = log(ax[2])
        ax[3] = log(ax[3])

    ax = [(1+xfrac) * ax[0] - xfrac * ax[1], (1+xfrac) * ax[1] - xfrac * ax[0],
          (1+yfrac) * ax[2] - yfrac * ax[3], (1+yfrac) * ax[3] - yfrac * ax[2]]

    if semilogx:
        ax[0] = exp(ax[0])
        ax[1] = exp(ax[1])
    if semilogy:
        ax[2] = exp(ax[2])
        ax[3] = exp(ax[3])

    return tuple(ax)
