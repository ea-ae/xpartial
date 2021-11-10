# xpartial

[![GitHub license](https://img.shields.io/github/license/ea-ae/xpartial?color=%20%232e3133)](https://github.com/ea-ae/xpartial/blob/master/LICENSE)
![GitHub Pipenv locked Python version](https://img.shields.io/github/pipenv/locked/python-version/ea-ae/xpartial)


Library that e**X**tends [`functools.partial`](https://docs.python.org/3/library/functools.html#functools.partial) to allow for selective argument freezing. Skip positional arguments one by one, assign from the end of the argument list, overwrite frozen arguments with kwargs, and make use of default values in middle of your function calls.

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

foo = lambda a, b, c=0, d=0, e=0: (a, b, c, d, e)  # takes+returns 5 args
g = xpartial(foo, 10, SkipRest, 40, 50)  # 'SkipRest' greedily skips args
g(20, 30)  # -> 10, 20, 30, 40, 50
g(20)  # -> 10, 20, 0, 40, 50

bar = lambda a=3, b=5, *args: (a, b, *args)
h = xxpartial({...}, 15)  # alternative syntax: ...=Skip, {...}=SkipRest
h(1, 2, 3)  # -> 1, 2, 3, 15  (frozen args are in the very end)
h()  # -> 3, 5, 15  (default values are applied)
h(Skip, 42, 1337)  # -> 3, 42, 1337, 15 (Skips here use default values)
```

## Docs

You may [read the documentation here](https://ea-ae.github.io/xpartial/).

## License

This project is licensed under [The Unlicense](LICENSE). Started in 2021.
