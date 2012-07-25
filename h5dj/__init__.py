
#from h5dj.storage import HDF5Storage

# package path-extension snippet.
from setuptools.package_index import declare_namespace
declare_namespace('h5dj')

from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)
