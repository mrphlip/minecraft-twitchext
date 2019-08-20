# build with
# python3 setup.py py2exe
from distutils.core import setup
import py2exe
from constants import APP_NAME
setup(name=APP_NAME,scripts=["main.py"],)
