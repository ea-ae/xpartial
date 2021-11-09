# xpartial

[![GitHub license](https://img.shields.io/github/license/ea-ae/xpartial?color=%20%232e3133)](https://github.com/ea-ae/xpartial/blob/master/LICENSE)
![GitHub Pipenv locked Python version](https://img.shields.io/github/pipenv/locked/python-version/ea-ae/xpartial)


Library that e**X**tends [`functools.partial`](https://docs.python.org/3/library/functools.html#functools.partial) to allow for selective argument freezing.

## Installation and Examples

Install the package (todo) with:

    pip install xpartial

Basic usage:

```python
from xpartial import xpartial, Skip, SkipRest

# Same as: xpartial(range, stop=5)
f = xpartial(range, Skip, 6)  # 'Skip' skips a single positional arg
f(2)  # -> 2, 3, 4, 5
f(1, 2)  # -> 1, 3, 5

foo = lambda a, b, c=0, d=0, e=0: (a, b, c, d, e)  # takes & returns 5 args

g = xpartial(foo, 10, SkipRest, 40, 50)  # 'SkipRest' greedily skips args
g(20, 30)  # -> 10, 20, 30, 40, 50
g(20)  # -> 10, 20, 0, 40, 50
```

## Implementation Details

### xpartial(func, *args, **kwargs)

This function allows you to selectively freeze any parameters with specified values, creating a partial function. Frozen arguments in partial functions can be overwritten through keyword arguments.

### Skip

When used as argument for `xpartial`, this constant skips over a single positional argument of the target function, requiring said argument to be later provided to the partial function.

When used as an argument for a partial function created by `xpartial`, the argument is set to its default value (if there isn't one, an error is thrown).

### SkipAll

Same as `Skip` in both cases, but skips as many arguments as possible, freezing the **n** arguments that come after it in the functional as the last **n** arguments. Only a single `SkipAll` may be provided in a function call.

## License

Licensed under [The Unlicense](LICENSE).
