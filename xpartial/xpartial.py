"""Library that eXtends functools.partial to allow for selective argument freezing.

Skip positional arguments one by one, assign from the end of the argument list, overwrite frozen arguments with kwargs,
and make use of default values in middle of your function calls.

Quickstart::

    from xpartial import xpartial, Skip, SkipRest

    # Same as: xpartial(range, stop=5)
    >>> f = xpartial(range, Skip, 6)  # `Skip` skips a single positional arg
    >>> f(2)  # -> 2, 3, 4, 5
    range(2, 6)
    >>> f(1, 2)  # -> 1, 3, 5
    range(1, 6, 2)

    >>> g = xpartial(range, SkipRest, 2)  # `2` is the last positional arg
    >>> g(1, 6)  # -> 1, 3, 5
    range(1, 6, 2)
"""


__all__ = ['xpartial', 'xxpartial', 'Skip', 'SkipRest']

from typing import TypeVar, Callable, Generator, NoReturn, Any


R = TypeVar('R')


def xpartial(func: Callable[..., R], /, *args: Any, **kwargs: Any) -> Callable[..., R]:
    """Return a new function with partially frozen arguments.

    An eXtended partial utility function that allows you to selectively freeze any parameters with specified values,
    creating a partial function. Frozen arguments in partial functions can be overwritten through keyword arguments.
    Function `xpartialmethod` behaves just like `xpartial`, but is instead used for method definitions.

    Args:
        func: Target function to apply arguments to.
        args: Positional arguments to be frozen.
        kwargs: Keyword arguments to be frozen.

    Returns:
        Partial function with frozen arguments.
    """
    def partial_func(*iargs: Any, **ikwargs: Any) -> R:
        """Callable partial function with frozen arguments.

        Args:
            iargs: Positional arguments.
            ikwargs: Keyword arguments that may overwrite frozen arguments.

        Returns:
            Returned result of partial function execution.
        """
        def process_args() -> Generator[Any, None, None]:
            """Yield processed function arguments.

            Yields:
                Yield processed argument.
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


def xxpartial() -> NoReturn:
    """Return a new function with partially frozen arguments.

    An eXtra eXtended partial function with syntactic sugar for convenience when writing simple partials.
    `Skip` and `SkipRest` can be optionally replaced with `...` and `{...}`, respectively.
    Not recommended for dynamically created partial functions that accept `Ellipsis` or `set(Ellipsis)` arguments.
    """
    raise NotImplementedError()


class _Constant:  # pragma: no cover
    """Do not allow instantiation of class. Allows us to create subclass docstrings."""

    def __new__(cls) -> NoReturn:  # type: ignore
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
    arguments and Skips to the end of the argument list. In case the positional argument list ends with `*args`,
    the rest of the frozen arguments go in the end of it.

    Only the first `SkipRest` provided to `xpartial` has an effect, the rest are ignored entirely.
    Unlike `Skip`, `SkipRest` can't be used in partial function calls.

    Examples:
        >>> foo = lambda a, b, c=0, d=0, e=0: (a, b, c, d, e)  # takes+returns 5 args
        >>> f = xpartial(foo, 10, SkipRest, 40, 50)  # `SkipRest` skips greedily
        >>> f(20, 30)
        (10, 20, 30, 40, 50)
        >>> f(20)
        (10, 20, 0, 40, 50)

        >>> bar = lambda a, b=0, c=0, *args: (a, b, c, args)
        >>> g = xpartial(bar, 10, SkipRest, 40, 50)  # `SkipRest` makes use of default vals and `*args`
        >>> g(20)  # `50` is in `*args`, not `c`
        (10, 20, 0, 40, 50)
    """


if __name__ == '__main__':
    foos = lambda a, b=0, c=0, d=0, e=0, *args: (a, b, c, d, e, (*args,))  # noqa: E731
    ff = xpartial(foos, 1, SkipRest, 4, Skip, 5)
    print(ff(20, 30, 40, 50, 60))
