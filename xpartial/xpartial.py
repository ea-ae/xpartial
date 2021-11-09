"""Extend functools.partial to allow for selective argument freezing."""


__all__ = ['Skip', 'SkipAll', 'xpartial']

from typing import TypeVar, Callable, Generator, NoReturn, Any


class Constant:
    """Do not allow instantiation of class. Allows us to create subclass docstrings."""

    def __new__(cls, *args: Any, **kwargs: Any) -> NoReturn:  # type: ignore
        """Do not allow instantiation of class."""
        raise TypeError('Skip may not be instantiated.')


class Skip(Constant):
    """Skip a single positional argument."""


class SkipAll(Constant):
    """Skip as many positional arguments as possible, allowing one to freeze arguments at the end of the function."""


R = TypeVar('R')


def xpartial(func: Callable[..., R], /, *args: Any, **kwargs: Any) -> Callable[..., R]:
    """Return a new function with partially frozen arguments.

    :param func: Function to apply arguments to.
    :param args: Positional arguments to be frozen.
    :param kwargs: Keyword arguments to be frozen.
    :return: Function with frozen arguments.
    """
    def partial_func(*iargs: Any, **ikwargs: Any) -> R:
        """Partial function with frozen arguments.

        :param iargs: Positional arguments.
        :param ikwargs: Keyword arguments.
        :return: Result of function with frozen arguments.
        """
        def process_args() -> Generator[Any, None, None]:
            """Yield processed function arguments."""
            iarg_it = iter(iargs)
            for arg in args:
                if arg in ikwargs:
                    yield ikwargs.pop(arg)  # allow overwriting of frozen args if they're present in the kwargs
                elif arg is Skip:
                    yield next(iarg_it)
                elif arg is SkipAll:
                    pass
                else:
                    yield arg
            for iarg in iarg_it:  # yield the remaining positional arguments after Skips
                yield iarg

        ikwargs |= kwargs
        return func(*process_args(), **ikwargs)
    return partial_func


if __name__ == '__main__':
    foo = lambda a, b=0, c=0, d=0, e=0: (a, b, c, d, e)  # noqa: E731
    f = xpartial(foo, Skip, 5)
    print(f(2, 333))
