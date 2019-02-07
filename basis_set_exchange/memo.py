'''
Class/decorator for memoizing BSE functionality
'''

import functools
import pickle
import inspect

# If set to True, memoization of some internal functions
# will be used. Generally safe to leave enabled - it
# won't use that much memory
memoize_enabled = True


def _make_key(args_spec, *args, **kwargs):
    left_args = args_spec.args[len(args):]
    num_defaults = len(args_spec.defaults or ())
    defaults_names = args_spec.args[-num_defaults:]

    if not set(left_args).symmetric_difference(kwargs).issubset(defaults_names):
        # We got an error in the function call. Let's simply trigger it
        func(*args, **kwargs)

    start = 0
    key = []
    for arg, arg_name in zip(args, args_spec.args):
        key.append(arg)
        if arg_name in defaults_names:
            start += 1

    for left_arg in left_args:
        try:
            key.append(kwargs[left_arg])
        except KeyError:
            key.append(args_spec.defaults[start])

        # Increase index if we used a default, or if the argument was provided
        if left_arg in defaults_names:
            start += 1

    return pickle.dumps(key)


class BSEMemoize:
    def __init__(self, f):
        self.__f = f
        self.args_spec = inspect.getfullargspec(f)
        self.__memo = {}
        functools.update_wrapper(self, f)

    def __call__(self, *args, **kwargs):
        if memoize_enabled is not True:
            return self.__f(*args, **kwargs)

        arg_key = _make_key(self.args_spec, *args, **kwargs)

        if arg_key in self.__memo:
            return pickle.loads(self.__memo[arg_key])

        ret = self.__f(*args, **kwargs)
        self.__memo[arg_key] = pickle.dumps(ret)
        return ret
