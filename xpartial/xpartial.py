"""Library that eXtends functools.partial to allow for selective argument freezing.

Skip positional arguments one by one, assign from the end of the argument list, overwrite frozen arguments with kwargs,
and make use of default values in middle of your function calls.
"""


__all__ = ['Skip', 'SkipRest', 'xpartial']

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

    When used as an argument for `xpartial`, skips as many arguments as possible, freezing the n arguments
    that come after it in the functional as the last **n** arguments. If the function contains an `*args`,
    all the remaining positional arguments are skipped.

    Unlike `Skip`, `SkipRest` can't be used in partial function calls.
    Only a single `SkipRest` may be provided to an `xpartial`.
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
            iarg_it = iter(iargs)
            remaining = len(args)
            for arg in args:
                remaining -= 1
                if arg in ikwargs:
                    yield ikwargs.pop(arg)  # allow overwriting of frozen args if they're present in the kwargs
                elif arg is Skip:
                    try:
                        yield next(iarg_it)
                    except StopIteration:
                        return  # if the remaining args are all Skips then we're fine, if not, TypeError will be raised
                elif arg is SkipRest:
                    pass
                else:
                    yield arg
            for iarg in iarg_it:  # yield the remaining positional arguments after Skips
                yield iarg

        ikwargs |= kwargs
        return func(*process_args(), **ikwargs)

    return partial_func


def xpartialmethod():
    """Implement this later."""
    raise NotImplementedError()


if __name__ == '__main__':
    foo = lambda a, b=0, c=0, d=0, e=0: (a, b, c, d, e)  # noqa: E731
    f = xpartial(foo, 1, Skip, Skip, Skip, SkipRest, Skip)
    print(f(5))
