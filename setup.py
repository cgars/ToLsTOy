#-------------------------------------------------------------------------------
# Copyright (c) 2015 Christian Garbers.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Simplified BSD License
# which accompanies this distribution
# 
# Contributors:
#     Christian Garbers - initial API and implementation
#-------------------------------------------------------------------------------
#!/usr/bin/env python

from distutils.core import setup

setup(name='ToLsTOy',
      version='0.9',
      description='Twenty Led Tower cOntrol',
      author='Christian Garbers',
      author_email='christian@stuebeweg50.de',
      packages=['ToLsTOy'],
      package_dir={'ToLsTOy': 'ToLsTOy'},
      package_data={'ToLsTOy': ['PCI-DASK.dll', 'PCI-DASK.lib', 'ColSymb.gif']}, requires=['mock']
     )
