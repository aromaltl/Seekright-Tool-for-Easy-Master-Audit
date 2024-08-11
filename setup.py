from setuptools import setup, Extension
import os
try:
    import pybind11
except:
    os.system("pip3 install pybind11")
import glob
import pybind11
# Define the extension module
ext_modules = [
    Extension(
        'jetils',
        sources=glob.glob(os.path.join('srcs', '*.cpp')),
        include_dirs=[pybind11.get_include(), pybind11.get_include(user=True)],
        language='c++'
    ),
]

# Setup configuration
setup(
    name='JET_UTILS',
    version='0.1',
    ext_modules=ext_modules,
    # This is important to ensure setuptools uses the correct compiler
    # and other settings to build the extension module.
    install_requires=open('requirements.txt').read().splitlines(),
)
#python3 setup.py build_ext --inplace