'''
Class/decorator for memoizing BSE functionality
'''

import functools
import pickle

# If set to True, memoization of some internal functions
# will be used. Generally safe to leave enabled - it
# won't use that much memory
memoize_enabled = True


class BSEMemoize:
    def __init__(self, f):
        self.__f = f
        self.__memo = {}
        functools.update_wrapper(self, f)

    def __call__(self, *args):
        if memoize_enabled is not True:
            return self.__f(*args)

        if args in self.__memo:
            return pickle.loads(self.__memo[args])

        ret = self.__f(*args)
        self.__memo[args] = pickle.dumps(ret)
        return ret
