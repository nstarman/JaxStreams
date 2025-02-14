"""Utilities for phase-space positions."""

__all__: list[str] = []

from typing import TYPE_CHECKING, Any, Protocol, TypeAlias, cast, runtime_checkable

import coordinax as cx
import quaxed.numpy as jnp

import galax.typing as gt


@runtime_checkable
class HasShape(Protocol):
    """Protocol for an object with a shape attribute."""

    shape: gt.Shape


# -----------------------------------------------------------------------------

if TYPE_CHECKING:
    from typing import NotRequired, TypedDict

    class PSPVConvertOptions(TypedDict):
        q: type[cx.vecs.AbstractPos]
        p: NotRequired[type[cx.vecs.AbstractVel] | None]

else:  # need runtime for jaxtyping
    PSPVConvertOptions: TypeAlias = dict[
        str, type[cx.vecs.AbstractPos] | type[cx.vecs.AbstractVel] | None
    ]

# -----------------------------------------------------------------------------


def _getitem_vec1time_index_tuple(index: tuple[Any, ...], t: gt.FloatQuSzAny) -> Any:
    """Get the time index from a slice."""
    if len(index) == 0:  # slice is an empty tuple
        return slice(None)
    if t.ndim == 1:  # slicing a Sz1
        return slice(None)
    if len(index) >= t.ndim:
        msg = f"Index {index} has too many dimensions for time array of shape {t.shape}"
        raise IndexError(msg)
    return index


def _getitem_vec1time_index_shaped(index: HasShape, t: gt.FloatQuSzAny) -> HasShape:
    """Get the time index from a shaped index array."""
    if t.ndim == 1:  # Sz1
        return cast(HasShape, jnp.asarray([True]))
    if len(index.shape) >= t.ndim:
        msg = f"Index {index} has too many dimensions for time array of shape {t.shape}"
        raise IndexError(msg)
    return index


def getitem_vec1time_index(index: Any, t: gt.FloatQuSzAny) -> Any:
    """Get the time index from an index.

    Parameters
    ----------
    index : Any
        The index to get the time index from.
    t : FloatQuSzAny
        The time array.

    Returns
    -------
    Any
        The time index.

    Examples
    --------
    We set up a time array.
    >>> import jax.numpy as jnp
    >>> import unxt as u
    >>> t = u.Quantity(jnp.ones((10, 3), dtype=float), "s")

    Some standard indexes.
    >>> getitem_vec1time_index(0, t)
    0

    >>> getitem_vec1time_index(slice(0, 10), t)
    slice(0, 10, None)

    Tuples:
    >>> getitem_vec1time_index((0,), t)
    (0,)

    >>> t = u.Quantity(jnp.ones((1, 2, 3), dtype=float), "s")
    >>> getitem_vec1time_index((0, 1), t)
    (0, 1)

    Shaped:
    >>> import jax.numpy as jnp
    >>> index = jnp.asarray([True, False, True])
    >>> getitem_vec1time_index(index, t)
    Array([ True, False,  True], dtype=bool)
    """
    if isinstance(index, tuple):
        return _getitem_vec1time_index_tuple(index, t)
    if isinstance(index, HasShape):
        return _getitem_vec1time_index_shaped(index, t)
    return index
