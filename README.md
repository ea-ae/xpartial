# xpartial

[![GitHub license](https://img.shields.io/github/license/ea-ae/xpartial?color=%20%232e3133)](https://github.com/ea-ae/xpartial/blob/master/LICENSE)
![GitHub Pipenv locked Python version](https://img.shields.io/github/pipenv/locked/python-version/ea-ae/xpartial)


Library that e**X**tends [`functools.partial`](https://docs.python.org/3/library/functools.html#functools.partial) to allow for selective argument freezing.

## Installation and Usage

Install the package (todo) with:

    pip install xpartial

Basic usage examples:

```python
from xpartial import xpartial, Skip, SkipRest

# Same as: xpartial(range, stop=5)
f = xpartial(range, Skip, 5)  # 'Skip' skips a single positional arg
f(2)  # -> 2, 3, 4
f(2, -1)  # -> 4, 3, 2

foo = lambda a, b=0, c=1, d=2, e=3: a, b, c, d, e  # takes & returns 5 args

g = xpartial(foo, 10, SkipRest, 40, 50)  # 'SkipRest' greedily skips args
g(20, 30)  # -> 10, 20, 30, 40, 50
g(20)  # -> 10, 20, 1, 40, 50
```

## License

Licensed under [The Unlicense](LICENSE).