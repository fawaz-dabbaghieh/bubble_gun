#!/usr/bin/env python3
import sys
from BubbleGun.__version__ import version
from setuptools import setup, find_packages, Extension

CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 3)

# This check and everything above must remain compatible with Python 2.7.
if CURRENT_PYTHON < REQUIRED_PYTHON:
    sys.stderr.write("BubbleGun requires Python 3.3 or higher and "
                     "you current version is {}".format(CURRENT_PYTHON))
    sys.exit(1)


extra_compile_args = []
if sys.platform != "win32":
    extra_compile_args.append("-std=c++11")

setup(name='BubbleGun',
      version=version,
      description='Detection of Bubble and Superbubble chains in genome graphs',
      author='Fawaz Dabbaghie',
      author_email='fawaz.dabbaghieh@gmail.com',
      url='https://github.com/fawaz-dabbaghieh/bubble_gun',
      packages=find_packages(),
      # scripts=['bin/main.py'],
      license="LICENSE.TXT",
      long_description=open("README.md").read(),
      long_description_content_type='text/markdown',
      ext_modules=[
          Extension(
              "BubbleGun._graph_cpp",
              sources=["BubbleGun/_graph_cpp.cpp"],
              language="c++",
              extra_compile_args=extra_compile_args,
          )
      ],
#      install_requires=["protobuf == 3.11.3",
#                        "pystream-protobuf == 1.5.1"],
      # other arguments here...
      entry_points={
          "console_scripts": [
              "BubbleGun=BubbleGun.main:main"
          ]}
      )
