"""Extend functools.partial to allow for selective argument freezing."""


__all__ = ['Skip', 'SkipRest', 'xpartial']

from typing import TypeVar, Callable, Generator, NoReturn, Any


class Constant:
    """Do not allow instantiation of class. Allows us to create subclass docstrings."""

    def __new__(cls, *args: Any, **kwargs: Any) -> NoReturn:  # type: ignore
        """Do not allow instantiation of class."""
        raise TypeError('Skip may not be instantiated.')


class Skip(Constant):
    """Skip a single positional argument."""


class SkipRest(Constant):
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
        """Callable partial function with frozen arguments.

        :param iargs: Positional arguments.
        :param ikwargs: Keyword arguments.
        :return: Result of function with frozen arguments.
        """
        def process_args() -> Generator[Any, None, None]:
            """Yield processed function arguments."""
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

    # print(id(partial_func))
    return partial_func


if __name__ == '__main__':
    foo = lambda a, b=0, c=0, d=0, e=0: (a, b, c, d, e)  # noqa: E731
    f = xpartial(foo, 1, Skip, Skip, Skip, SkipRest, Skip)
    print(f(5))
