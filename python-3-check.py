#!/usr/bin/env python

from __future__ import print_function

import sys

print('platform:', sys.platform)
print('executable:', sys.executable)
print('Python', sys.version)
if sys.version_info[0] >= 3:
    print('OK')
else:
    sys.exit('FAIL')
