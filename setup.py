#!/usr/bin/env python
from distutils.core import setup
from distutils.command.install import install
import sys

def check_dependencies():
    try:
       __import__('argparse')
       __import__('requests')
    except ImportError, e:
       print 'Dependencies error : %s' % e
       sys.exit()

class Install(install):
    def run(self):
        check_dependencies()
        install.run(self) # proceed with the installation

setup(name='senslabcli',
      version='1.1',
      description='Senslab testbed command-line client',
      author='Senslab Team',
      author_email='admin@senslab.info',
      url='http://www.senslab.info',
      download_url='http://www.senslab.info',
      packages = ['senslabcli'],
      scripts = ["experiment-cli","profile-cli","node-cli","auth-cli"],
      classifiers = [ 'Development Status :: 1 - Alpha',
                    'Programming Language :: Python',
                    'Intended Audience :: End Users/Desktop',
                    'Environment :: Console',
                    'Topic :: Utilities',
                    ],
      cmdclass={'install': Install}
      )
