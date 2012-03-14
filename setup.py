###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

from distutils.core import setup
from turses import __version__


setup(
    name='turses',
    version='%s' % __version__,
    author='Nicolas Paris and Alejandro Gómez',
    author_email='alejandroogomez@gmail.com',
    license='GPLv3',
    description='A ncurses Twitter client.',
    long_description="""`turses` is a Twitter client with a sexy 
                        ncurses interface.
                        
                        http://github.com/alejandrogomez/turses""",
    packages = [
        'turses', 
        'turses.ui'
    ],
    package_dir={'turses':'turses'},
    scripts=["bin/turses"],
    platforms=['linux'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console :: Curses',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
    ],
    install_requires=[
        'python-twitter',
        'argparse',
        'httplib2',
        'urwid',
        'oauth2',
    ],
    test_requires=['mock==0.8.0'],
)
