"""Library that eXtends functools.partial to allow for selective argument freezing.

Skip positional arguments one by one, assign from the end of the argument list, overwrite frozen arguments with kwargs,
and make use of default values in middle of your function calls.
"""


__all__ = ['xpartial', 'xpartialmethod', 'Skip', 'SkipRest']

from typing import TypeVar, Callable, Generator, NoReturn, Any


class _Constant:  # pragma: no cover
    """Do not allow instantiation of class. Allows us to create subclass docstrings."""

    def __new__(cls, *args: Any, **kwargs: Any) -> NoReturn:  # type: ignore
        """Do not allow instantiation of class."""
        raise TypeError('Skip may not be instantiated.')


class Skip(_Constant):
    """Skip a single positional argument.

    When used as argument for `xpartial`, this constant skips over a single positional argument of the target function,
    requiring said argument to be later provided to the partial function.
    When used as an argument for a partial function created by `xpartial`, the argument is set to its default value
    (if there isn't one, an error is thrown).
    """


class SkipRest(_Constant):
    """Skip as many positional arguments as possible, allowing one to freeze arguments at the end of the function.

    When used as an argument for `xpartial`, skips as many arguments as possible, leaving the remaining frozen
    arguments and Skips to the end of the argument list. Only the first `SkipRest` provided `xpartial` has an effect,
    the rest are ignored entirely. Unlike `Skip`, `SkipRest` can't be used in partial function calls.
    """


R = TypeVar('R')


def xpartial(func: Callable[..., R], /, *args: Any, **kwargs: Any) -> Callable[..., R]:
    """Return a new function with partially frozen arguments.

    An eXtended partial utility function that allows you to selectively freeze any parameters with specified values,
    creating a partial function. Frozen arguments in partial functions can be overwritten through keyword arguments.
    Function `xpartialmethod` behaves just like `xpartial`, but is instead used for method definitions.

    :param func: Function to apply arguments to.
    :param args: Positional arguments to be frozen.
    :param kwargs: Keyword arguments to be frozen.
    :return: Function with frozen arguments.
    """
    def partial_func(*iargs: Any, **ikwargs: Any) -> R:
        """Callable partial function with frozen arguments.

        :param iargs: Positional arguments.
        :param ikwargs: Keyword arguments.
        :return: Returned result of partial function.
        """
        def process_args() -> Generator[Any, None, None]:
            """Yield processed function arguments.

            :return: Yield processed argument.
            """
            iargs_i, skips_left, skiprest_done = 0, args.count(Skip), False
            for arg in args:
                if arg in ikwargs:
                    yield ikwargs.pop(arg)  # allow overwriting of frozen args if they're present in the kwargs
                elif arg is Skip:
                    try:
                        yield iargs[iargs_i]
                        iargs_i += 1
                        skips_left -= 1
                    except IndexError:
                        return  # if the remaining args are all Skips then we're fine, if not, TypeError will be raised
                elif arg is SkipRest:
                    if skiprest_done:
                        continue
                    skiprest_done = True
                    for i in range(iargs_i, len(iargs) - skips_left):  # exhaust as many as possible
                        yield iargs[i]
                    iargs_i = len(iargs) - skips_left
                else:
                    yield arg
            for i in range(iargs_i, len(iargs)):  # exhaust all
                yield iargs[i]

        ikwargs |= kwargs
        return func(*process_args(), **ikwargs)

    return partial_func


def xpartialmethod() -> NoReturn:
    """Return a new method with partially frozen arguments.

    An eXtra eXtended partial function with syntactic sugar for convenience when writing simple partials.
    `Skip` and `SkipRest` can be optionally replaced with `...` and `{...}`, respectively.
    Not recommended for dynamically created partial functions that accept `Ellipsis` or `set(Ellipsis)` arguments.
    """
    raise NotImplementedError()


if __name__ == '__main__':
    foo = lambda a, b=0, c=0, d=0, e=0, *args: (a, b, c, d, e, (*args,))  # noqa: E731
    f = xpartial(foo, 1, SkipRest, 4, Skip, 5)
    print(f(20, 30, 40, 50, 60))
