# ensure this module is never imported under python2
# (mostly to avoid garbage *.pyc files)
def check_python3() -> 'python3 is required':
    pass
del check_python3
