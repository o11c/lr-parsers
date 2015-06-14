#!/usr/bin/env python

from __future__ import print_function

import sys

if sys.version_info[0] >= 3:
    print('PY3: OK')
else:
    sys.exit('PY3: FAIL')
