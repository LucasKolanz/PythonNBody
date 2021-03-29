#By Lucas Kolanz


#This file compiles the cython file 'data.pyx'


from setuptools import setup
from setuptools.extension import Extension
from Cython.Build import cythonize
import numpy as np

# distutils: define_macros=NPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION


# extensions = [
# 	# Extension(define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],),
# 	Extension('numerics',['data.pyx'])
#     # ext_modules = [Extension('bar/reduce', ['reduce.pyx'])]
# ]
ext_modules = Extension(
	name='data',
	sources=['data.pyx'],
	define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
	include_dirs=[np.get_include(), 'data'],
	)
# 
# cmdclass = {'build_ext': build_ext},
setup(
    ext_modules = cythonize(ext_modules,language_level='3')

)