#!/usr/bin/env python

import os

import numpy as np
from PIL import Image

import chainer
import chainer.cuda
from chainer import Variable
import chainer.functions as F


def out_generated_image(gen, dis, rows, cols, train_iter, patch_iter, dst):
    @chainer.training.make_extension()
    def make_image(trainer):
        #np.random.seed(seed)
        #n_images = rows * cols
        xp = gen.xp
        #z = Variable(xp.asarray(gen.make_hidden(n_images)))

        image = train_iter.next()[0]
        patch = patch_iter.next()[0]

        image = Variable(xp.asarray(image))
        patch = Variable(xp.asarray(patch))

        concat_image = F.concat((image, patch), axis=0)
        concat_image = F.expand_dims(concat_image, axis=0)

        #import pdb; pdb.set_trace()
        with chainer.using_config('train', False):
            x = gen(concat_image)
        x = chainer.cuda.to_cpu(x.data)

        img = x[0].transpose(1, 2, 0) * 255.
        img = img.astype(np.uint8)
        img = Image.fromarray(img)

        preview_dir = '{}/preview'.format(dst)
        preview_path = preview_dir +\
            '/image{:0>8}.png'.format(trainer.updater.iteration)
        if not os.path.exists(preview_dir):
            os.makedirs(preview_dir)

        img.save(preview_path)

        """
        np.random.seed()

        x = np.asarray(np.clip(x * 255, 0.0, 255.0), dtype=np.uint8)
        _, _, H, W = x.shape
        x = x.reshape((rows, cols, 3, H, W))
        x = x.transpose(0, 3, 1, 4, 2)
        x = x.reshape((rows * H, cols * W, 3))

        preview_dir = '{}/preview'.format(dst)
        preview_path = preview_dir +\
            '/image{:0>8}.png'.format(trainer.updater.iteration)
        if not os.path.exists(preview_dir):
            os.makedirs(preview_dir)
        Image.fromarray(x).save(preview_path)
        """
    return make_image
