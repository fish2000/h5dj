
from __future__ import with_statement, print_function
from django.core.files.storage import Storage

from django.core.exceptions import SuspiciousOperation
from datetime import datetime

import os
import shutil
import types
import tempfile
import h5py


def nda_from_path(image_file):
    try:
        from imread import imread
    except ImportError:
        from PIL import Image
        import numpy
        return numpy.array(Image.open(image_file))
    else:
        return imread(os.path.abspath(image_file))

def nda_from_url(image_url):
    import requests
    tmp = tempfile.mktemp()
    with open(tmp, 'wb') as f:
        f.write(requests.get(image_url).content)
        f.flush()
    return nda_from_path(tmp)

def nda_from_file_object(file_object):
    from PIL import Image
    from cStringIO import StringIO
    if hasattr(file_object, 'seek'):
        file_object.seek(0)
    return Image.open(StringIO(file_object))


class HDF5Storage(Storage):
    
    group = h5py._hl.group.Group
    dataset = h5py._hl.dataset.Dataset
    location = "/"
    
    def __init__(self,
        hdf5_file, base_url=None, repack=False):
        
        self.base_url = base_url
        self.hdf5_file = os.path.normpath(
            os.path.abspath(hdf5_file))
        
        if repack is True:
            self._repack(reopen=False)
        
        if base_url is None:
            from django.conf import settings
            base_url = settings.MEDIA_URL
        
        self.hdf5 = h5py.File(self.hdf5_file)
    
    def _is_group(self, path):
        return type(self.path(path)) == self.group
    
    def _is_dataset(self, path):
        return type(self.path(path)) == self.dataset
    
    def _repack(self, reopen=True):
        if hasattr(self, 'hdf5'):
            if hasattr(self.hdf5, 'flush') and hasattr(self.hdf5, 'close'):
                self.hdf5.flush()
                self.hdf5.close()
            self.hdf5 = None
        
        if not os.path.isfile(self.hdf5_file):
            raise IOError(
                "Can't repack non-existing file %s" % self.hdf5_file)
        
        tmp = tempfile.mktemp()
        tmp_repacked = tempfile.mktemp()
        orig = tempfile.mktemp(suffix='.hdf5', dir="/tmp")
        shutil.copyfile(self.hdf5_file, tmp)
        os.system('h5repack -i %s -o %s -f GZIP=1' % (
            tmp, tmp_repacked))
        
        if not os.path.isfile(tmp_repacked):
            raise IOError(
                "Repack data not saved in temporary file %s" % tmp_repacked)
        shutil.move(self.hdf5_file, orig)
        shutil.move(tmp_repacked, self.hdf5_file)
        
        if reopen:
            self.hdf5 = h5py.File(self.hdf5_file)
        
        os.unlink(orig)
        return
    
    def open(self, name, **kwargs):
        if self._is_dataset(name):
            import numpy
            pth = self.path(name)
            out = numpy.ndarray(pth.shape, dtype=pth.dtype)
            pth.read_direct(out)
            return out
    
    def save(self, name, content):
        import numpy
        
        if type(content) in types.StringTypes:
            if os.path.isfile(content):
                content = nda_from_path(content)
            elif content.startswith('http://'):
                content = nda_from_url(content)
        elif hasattr(content, 'read'):
            content = nda_from_file_object(content)
        elif getattr(content, '__module__', '').startswith('PIL'):
            content = numpy.array(content)
        
        ncontent = numpy.asanyarray(content)
        
        full_path = os.path.normpath(os.path.join(self.location, name))
        dirname = os.path.dirname(full_path)
        filename = os.path.basename(full_path)
        directory = self.hdf5.require_group(dirname)
        
        save_data = directory.require_dataset(
            filename, shape=ncontent.shape, dtype=ncontent.dtype)
        save_data.write_direct(ncontent)
        save_data.file.flush()
    
    def path(self, name):
        if type(name) in types.StringTypes:
            try:
                path = os.path.join(self.location, name)
            except ValueError:
                raise SuspiciousOperation("Attempted access to '%s' denied." % name)
            return self.hdf5[path]
        elif type(name) in (self.group, self.dataset):
            return name
        else:
            raise TypeError("Can't determine path from %s (type %s)" % (
                name, type(name)))
    
    def delete(self, name):
        pth = self.path(name)
        if self.exists(pth):
            nm = pth.name
            pth = None
            del self.hdf5[nm]
            self.hdf5.flush()
    
    def exists(self, name):
        try:
            return (self.path(name) is not None)
        except KeyError:
            return False
        return False
    
    def listdir(self, path):
        pth = self.path(path)
        groups, datasets = [], []
        for pthname, obj in pth.items():
            if self._is_group(obj):
                groups.append(pthname)
            else:
                datasets.append(pthname)
        return groups, datasets
    
    def size(self, name):
        pth = self.path(name)
        if hasattr(pth, 'value'):
            return pth.value.size
        elif hasattr(pth, 'values'):
            pthdir = self.listdir(pth)
            siz = sum(self.size(nm) for nm in pthdir[0])
            siz += sum(self.size(nm) for nm in pthdir[1])
            return siz
        return 0
    
    def __getitem__(self, idx):
        return self.open(idx)
    
    def __setitem__(self, idx, value):
        self.save(idx, value)
    
    def url(self, name):
        pass
    
    def accessed_time(self, name):
        return datetime.fromtimestamp(
            os.path.getatime(
                self.path(name).file.filename))
    
    def created_time(self, name):
        return datetime.fromtimestamp(
            os.path.getctime(
                self.path(name).file.filename))
    
    def modified_time(self, name):
        return datetime.fromtimestamp(
            os.path.getmtime(
                self.path(name).file.filename))
