#!/usr/bin/env python

# because setuptools has sucky documentation
from distutils.core import setup

setup(
        name='lr-parsers',
        version='0.1',
        description='LR state machine and various parser generators',
        author='Ben Longbons',
        author_email='b.r.longbons@gmail.com',
        url='https://github.com/o11c/lr-parsers',
        packages=['lr'],
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3 :: Only',
            'Topic :: Software Development :: Code Generators',
            'Topic :: Software Development :: Libraries',
        ],
)
