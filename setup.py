#!/usr/bin/env python

from distutils.core import setup

setup(name='ToLsTOy',
      version='0.9',
      description='Twenty Led Tower cOntrol',
      author='Christian Garbers',
      author_email='christian@stuebeweg50.de',
      packages=['ToLsTOy'],
      package_dir={'ToLsTOy': 'ToLsTOy'},
      package_data={'ToLsTOy': ['PCI-DASK.dll', 'PCI-DASK.lib', 'ColSymb.gif']},
     )