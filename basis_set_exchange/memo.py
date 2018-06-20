'''
Class/decorator for memoizing BSE functionality
'''

import functools
import pickle

from . import api


class BSEMemoize:
    def __init__(self, f):
        self.__f = f
        self.__memo = {}
        functools.update_wrapper(self, f)

    def __call__(self, *args):
        if api.memoize_enabled is not True:
            return self.__f(*args)

        if args in self.__memo:
            return pickle.loads(self.__memo[args])

        ret = self.__f(*args)
        self.__memo[args] = pickle.dumps(ret)
        return ret
