#!/usr/bin/env python

import os
from distutils.core import setup

plugins = []
for plugin in os.listdir('plugins'):
    if plugin.endswith(".py"):
        plugins.append(os.path.join('plugins', plugin))

setup(name="path",
      version="0.31",
      description="PATH programming language",
      author="Francis Rogers",
      author_email="exorcismtongs@users.sf.net",
      url="http://pathlang.sf.net/",
      package_dir={'': 'src'},
      py_modules = ['pathlang'],
      scripts = ['src/path'],
      data_files=[('/usr/share/man/man1/', ['doc/path.1']),
                  ('/usr/lib/path/', plugins)]
    )
