"""Test :mod:`galax.coordinates._utils`."""

import re
from typing import ClassVar

import pytest
from jaxtyping import Array, Float

import quaxed.numpy as jnp
import unxt as u

from galax.coordinates._src.psps.utils import HasShape, getitem_vec1time_index
from galax.typing import QuSz3

Sz3 = Float[Array, "3"]
QVec2x3 = Float[u.Quantity["time"], "2 3"]


class TestHasShape:
    """Test :class:`~galax.coordinates._utils.HasShape`."""

    def test_runtime(self) -> None:
        """Test Protocol at runtime."""

        class Test:
            shape = (1, 2, 3)

        assert isinstance(Test(), HasShape)


class Test_getitem_vec1time_index:
    """Test :func:`~galax.coordinates._utils.getitem_vec1time_index`."""

    get_index: ClassVar = staticmethod(getitem_vec1time_index)

    @pytest.fixture
    def t3(self) -> QuSz3:
        """Return a Array[Float, 3]."""
        return u.Quantity([1.0, 2.0, 3.0], "Myr")

    @pytest.fixture
    def t2x3(self) -> QVec2x3:
        """Return a Array[Float, 2x3]."""
        return u.Quantity([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], "Myr")

    # ===============================================================

    def test_integer(self, t3: QuSz3) -> None:
        """Test scalar index."""
        for i in range(3):
            assert self.get_index(i, t3) == i

    @pytest.mark.parametrize(
        "index",
        [slice(None), slice(0, 3), slice(1, 3), slice(0, 3, 2)],
    )
    def test_slice(self, t3: QuSz3, index: slice) -> None:
        """Test slice index."""
        assert self.get_index(index, t3) == index

    # -----------------------

    def test_tuple_empty(self, t3: QuSz3) -> None:
        """Test empty tuple."""
        assert self.get_index((), t3) == slice(None)

    def test_tuple_1d(self, t3: QuSz3) -> None:
        """Test tuple index."""
        index = (slice(None), 1)
        assert self.get_index(index, t3) == slice(None)

    def test_tuple_big_index(self, t2x3: Sz3) -> None:
        """Test tuple index."""
        index = (slice(0, 3), 1)

        msg = (
            f"Index {index} has too many dimensions for "
            f"time array of shape {t2x3.shape}"
        )
        with pytest.raises(IndexError, match=re.escape(msg)):
            self.get_index(index, t2x3)

    @pytest.mark.parametrize(
        "index", [slice(None), slice(0, 3), slice(1, 3), slice(0, 3, 2)]
    )
    def test_tuple(self, t2x3: Sz3, index: tuple) -> None:
        """Test tuple index."""
        assert self.get_index(index, t2x3) == index

    # -----------------------

    def test_shaped_1d(self, t3: QuSz3) -> None:
        """Test shaped index on 1D array."""
        # 1D shaped index
        index = jnp.array([True, False, True])
        assert self.get_index(index, t3) == jnp.asarray([True])

        # 2D shaped index
        index = jnp.array([[True, False, True], [False, True, False]])
        assert self.get_index(index, t3) == jnp.asarray([True])

    def test_shaped_nd(self, t2x3: QVec2x3) -> None:
        """Test shaped index on N-dimensional array."""
        # index.shape < t.shape
        index = jnp.array([True, False])
        assert jnp.array_equal(self.get_index(index, t2x3), index)

        index = jnp.array([[True, False], [False, True]])
        with pytest.raises(IndexError):
            self.get_index(index, t2x3)
