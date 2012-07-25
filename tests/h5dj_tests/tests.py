
from __future__ import print_function

from django.conf import settings
from django.test import TestCase
import numpy
import imread
import random
import sys
import os

class StorageTests(TestCase):
    def setUp(self):
        from h5dj import HDF5Storage
        self.h5file = os.path.join(settings.tempdata, 'test.hdf5')
        self.h5 = HDF5Storage(self.h5file)
    
    def tearDown(self):
        self.h5.hdf5.close()
        os.unlink(self.h5file)
    
    def test_storage(self):
        zeros = numpy.zeros((101, 101), dtype=numpy.uint64)
        self.h5.save('zeros.nda', zeros)
        self.h5._repack()
    
    def test_store_image(self):
        #img = random.choice(os.listdir(settings.testimages))
        
        print('', file=sys.stderr)
        for img in os.listdir(settings.testimages):
            
            print("Reading image:", img, file=sys.stderr)
            nda = imread.imread(os.path.join(settings.testimages, img))
            self.h5.save('%s.nda' % img, nda)
            
            print("Repacking HDF5 storage...", file=sys.stderr)
            self.h5._repack()
            nda2 = self.h5.open('/%s.nda' % img)
            self.assertEqual(nda.sum(), nda2.sum())
            self.assertTrue(numpy.equal(nda, nda2).all())
    
    def test_store_image_path(self):
        img = random.choice(os.listdir(settings.testimages))

        print('', file=sys.stderr)
        #for img in os.listdir(settings.testimages):
        
        print("Reading image:", img, file=sys.stderr)
        self.h5.save('%s-filename.nda' % img,
            os.path.join(settings.testimages, img))
        nda = imread.imread(
            os.path.join(settings.testimages, img))
        self.h5.save('%s.nda' % img, nda)

        print("Repacking HDF5 storage...", file=sys.stderr)
        self.h5._repack()
        nda2 = self.h5.open('/%s-filename.nda' % img)
        self.assertEqual(nda.sum(), nda2.sum())
        self.assertTrue(numpy.equal(nda, nda2).all())
    
    def test_store_image_PIL_object(self):
        from PIL import Image
        img = random.choice(os.listdir(settings.testimages))
        
        print('', file=sys.stderr)
        #for img in os.listdir(settings.testimages):

        print("Reading image:", img, file=sys.stderr)
        self.h5.save('%s-PIL.nda' % img,
            Image.open(
                os.path.join(settings.testimages, img)))
        nda = imread.imread(
            os.path.join(settings.testimages, img))
        self.h5.save('%s.nda' % img, nda)

        print("Repacking HDF5 storage...", file=sys.stderr)
        self.h5._repack()
        nda2 = self.h5.open('/%s-PIL.nda' % img)
        self.assertEqual(nda.sum(), nda2.sum())
        self.assertTrue(numpy.equal(nda, nda2).all())
