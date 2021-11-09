"""Test XPartial."""

import pytest
from xpartial.xpartial import xpartial, Skip  # , SkipRest
from typing import Callable, Any
from string import ascii_letters, ascii_lowercase
from itertools import repeat


def func_factory(args_amount: int) -> Callable[..., str]:
    """Create testable functions."""
    arg_list = ', '.join(ascii_letters[:args_amount])
    exec(f'def t({arg_list}): return "".join(({arg_list}))', globals(), globals())
    return t  # type: ignore # noqa


@pytest.mark.parametrize('letters', ('abcd', ascii_lowercase, 'x'))
def test_xpartial__zero_freezes(letters: str):
    """Test zero freezes."""
    func = func_factory(len(letters))
    assert xpartial(func)(*letters) == letters


@pytest.mark.parametrize('amounts', ((3, 3), (1, 1), (5, 2), (2, 5)))
def test_xpartial__skips_only(amounts: tuple[int, int]):
    """Test zero freezes with skips."""
    func = func_factory(amounts[0])
    binds = repeat(Skip, amounts[1])
    expected = 'a' * amounts[0]
    assert xpartial(func, *binds)(*expected) == expected


@pytest.mark.parametrize('amounts', ((3, 3), (1, 1), (5, 2)))
def test_xpartial__start_freeze(amounts: tuple[int, int]):
    """Test freezes at start."""
    func = func_factory(amounts[0])
    binds = ['a'] * amounts[1]
    args = 'b' * (amounts[0] - amounts[1])
    expected = 'a' * amounts[1] + args
    assert xpartial(func, *binds)(*args) == expected


@pytest.mark.parametrize('amounts', ((3, 1, 1), (10, 2, 6), (5, 2, 1)))
def test_xpartial__middle_freeze(amounts: tuple[int, int, int]):
    """Test freezes at middle."""
    func = func_factory(amounts[0])
    binds: list[Any] = list([Skip] * amounts[1])
    binds.extend(['f'] * amounts[2])
    args = 'a' * (amounts[0] - amounts[2])
    expected = ''.join('a' if el is Skip else el for el in binds) + 'a' * int(len(args) / 2)
    print('\n', binds, args, 'xxx', expected)
    assert xpartial(func, *binds)(*args) == expected
