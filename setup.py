# from ez_setup import use_setuptools
# use_setuptools()

from setuptools import setup, find_packages
import sys, os

version = '0.4'

setup(name='nohrio',
      version=version,
      description="Binary manipulation and text serialization of OHRRPGCE formats",
      long_description="""\
Binary manipulation and text serialization of OHRRPGCE formats""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='ohrrpgce i/o yaml serialization binary',
      author='David Gowers',
      author_email='00ai99@gmail.com',
      url='https://github.com/ohrrpgce/nohrio/',
      license='GPLv3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
