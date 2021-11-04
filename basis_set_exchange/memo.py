# Copyright (c) 2017-2022 The Molecular Sciences Software Institute, Virginia Tech
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived
# from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

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
        # Return None to signal an issue with the argument list
        return None

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
        if not memoize_enabled:
            return self.__f(*args, **kwargs)

        arg_key = _make_key(self.args_spec, *args, **kwargs)

        if arg_key is None:
            # There was a problem with the arguments. Just call the
            # function to trigger the error
            return self.__f(*args, **kwargs)

        if arg_key in self.__memo:
            return pickle.loads(self.__memo[arg_key])

        ret = self.__f(*args, **kwargs)
        self.__memo[arg_key] = pickle.dumps(ret)
        return ret
