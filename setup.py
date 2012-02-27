###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

from distutils.core import setup


setup(
    name='turses',
    version='alpha',
    author='Nicolas Paris and Alejandro Gómez',
    author_email='alejandroogomez@gmail.com',
    license='GPLv3',
    description='Twitter and Identica ncurses client.',
    #long_description=open('README.md').read(),
    packages=['turses',],
    package_dir={'turses':'turses'},
    scripts=["bin/turses"],
    platforms=['linux'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console :: Curses',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
    ],
    install_requires=[
        'python-twitter>=0.8.2',
        'argparse',
        'httplib2==0.6.0',
        'urwid',
    ],
    test_requires=['mock==0.8.0'],
)
