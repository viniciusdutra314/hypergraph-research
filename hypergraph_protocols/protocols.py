"""Structural Python equivalents of the ``hgraphs-core`` Rust traits.

The protocols are intentionally small and composable. Algorithms should accept
the weakest protocol, or intersection of protocols, that they need.

Rust ``Option`` values are represented by ``None`` when the successful value
cannot itself be ``None`` (for example, an incidence iterator). Property maps
use the distinct :data:`MISSING` sentinel so that storing ``None`` remains
unambiguous. Rust ``Result`` errors become typed Python exceptions. Rust
methods with default implementations that only bypass validation are not
protocol requirements: Python adapters expose the checked operation and keep
validation behavior at the language boundary.
"""

from __future__ import annotations

from collections.abc import Hashable, Iterator, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Final, Protocol, Self


class Directedness(Enum):
    """Directedness category exposed by a hypergraph implementation."""

    DIRECTED = "directed"
    UNDIRECTED = "undirected"


@dataclass(frozen=True, slots=True)
class NodeIndex[RawNodeIdT: Hashable]:
    """A node identifier whose raw value is meaningful only to its producer."""

    value: RawNodeIdT


@dataclass(frozen=True, slots=True)
class HyperEdgeIndex[RawHyperEdgeIdT: Hashable]:
    """A hyperedge identifier whose raw value is meaningful only to its producer."""

    value: RawHyperEdgeIdT


class HyperGraph[RawNodeIdT: Hashable, RawHyperEdgeIdT: Hashable](Protocol):
    """Base capability defining a hypergraph's directedness.

    The generic parameters take the place of Rust's associated raw identifier
    types. Concrete implementations must document identifier stability.
    """

    @property
    def directedness(self) -> Directedness:
        """Return the hypergraph's directedness category in ``O(1)`` time."""
        ...


class NodeCountable(Protocol):
    """Capability for obtaining the number of nodes."""

    def num_nodes(self) -> int:
        """Return the node count in baseline ``O(1)`` time and space."""
        ...


class HyperEdgeCountable(Protocol):
    """Capability for obtaining the number of hyperedges."""

    def num_hyperedges(self) -> int:
        """Return the hyperedge count in baseline ``O(1)`` time and space."""
        ...


class NodeList[RawNodeIdT: Hashable, RawHyperEdgeIdT: Hashable](
    HyperGraph[RawNodeIdT, RawHyperEdgeIdT],
    Protocol,
):
    """Capability for iterating over all currently valid node identifiers."""

    def node_identifiers(self) -> Iterator[NodeIndex[RawNodeIdT]]:
        """Yield every node exactly once; exhausting costs baseline ``O(n)``."""
        ...


class HyperEdgeList[RawNodeIdT: Hashable, RawHyperEdgeIdT: Hashable](
    HyperGraph[RawNodeIdT, RawHyperEdgeIdT],
    Protocol,
):
    """Capability for iterating over all currently valid hyperedge identifiers."""

    def hyperedge_identifiers(self) -> Iterator[HyperEdgeIndex[RawHyperEdgeIdT]]:
        """Yield every hyperedge exactly once; exhausting costs baseline ``O(m)``."""
        ...


class HyperEdgeIncidence[RawNodeIdT: Hashable, RawHyperEdgeIdT: Hashable](
    HyperGraph[RawNodeIdT, RawHyperEdgeIdT],
    Protocol,
):
    """Capability for traversing node-to-hyperedge incidence."""

    def incident_edges(
        self, node: NodeIndex[RawNodeIdT]
    ) -> Iterator[HyperEdgeIndex[RawHyperEdgeIdT]] | None:
        """Return incident hyperedges, or ``None`` for an invalid node.

        A valid node yields every incident hyperedge exactly once. Creating the
        iterator is baseline ``O(1)`` and exhausting it is ``O(d(node))``.
        """
        ...


class NodeIncidence[RawNodeIdT: Hashable, RawHyperEdgeIdT: Hashable](
    HyperGraph[RawNodeIdT, RawHyperEdgeIdT],
    Protocol,
):
    """Capability for traversing hyperedge-to-node incidence."""

    def incident_nodes(
        self, hyperedge: HyperEdgeIndex[RawHyperEdgeIdT]
    ) -> Iterator[NodeIndex[RawNodeIdT]] | None:
        """Return incident nodes, or ``None`` for an invalid hyperedge.

        A valid hyperedge yields every incident node exactly once. Creating the
        iterator is baseline ``O(1)`` and exhausting it is ``O(|e|)``.
        """
        ...


class ContiguousHyperEdgeIncidence[RawNodeIdT: Hashable, RawHyperEdgeIdT: Hashable](
    HyperGraph[RawNodeIdT, RawHyperEdgeIdT],
    Protocol,
):
    """Capability exposing a borrowed, read-only node-incidence sequence.

    Python's type system cannot express Rust's contiguous borrowed slice. The
    ``Sequence`` return type captures its safe observable contract; binding
    implementations should return a zero-copy view when they can guarantee the
    view's lifetime and mutation behavior.
    """

    def incident_edges_slice(
        self, node: NodeIndex[RawNodeIdT]
    ) -> Sequence[HyperEdgeIndex[RawHyperEdgeIdT]] | None:
        """Return an ``O(1)`` incidence view, or ``None`` for an invalid node."""
        ...


class ContiguousNodeIncidence[RawNodeIdT: Hashable, RawHyperEdgeIdT: Hashable](
    HyperGraph[RawNodeIdT, RawHyperEdgeIdT],
    Protocol,
):
    """Capability exposing a borrowed, read-only hyperedge-incidence sequence."""

    def incident_nodes_slice(
        self, hyperedge: HyperEdgeIndex[RawHyperEdgeIdT]
    ) -> Sequence[NodeIndex[RawNodeIdT]] | None:
        """Return an ``O(1)`` incidence view, or ``None`` for an invalid hyperedge."""
        ...


@dataclass(frozen=True, slots=True)
class Capacity:
    """Additional node and hyperedge capacity requested from an implementation."""

    num_nodes: int | None = None
    num_hyperedges: int | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("num_nodes", self.num_nodes),
            ("num_hyperedges", self.num_hyperedges),
        ):
            if value is not None and (
                not isinstance(value, int) or isinstance(value, bool) or value < 0
            ):
                raise ValueError(f"{name} must be a non-negative integer or None")


class AllocatableHyperGraph[RawNodeIdT: Hashable, RawHyperEdgeIdT: Hashable](
    HyperGraph[RawNodeIdT, RawHyperEdgeIdT],
    Protocol,
):
    """Capability for explicitly reserving storage capacity."""

    def try_reserve_exact(self, additional: Capacity) -> None:
        """Reserve capacity without mutation; raise ``MemoryError`` on failure."""
        ...


class ExtendableHyperGraph[RawNodeIdT: Hashable, RawHyperEdgeIdT: Hashable](
    HyperGraph[RawNodeIdT, RawHyperEdgeIdT],
    Protocol,
):
    """Capability for bulk insertion of isolated nodes and empty hyperedges."""

    def add_nodes(self, num_nodes: int) -> Iterator[NodeIndex[RawNodeIdT]]:
        """Add and yield ``num_nodes`` isolated nodes atomically.

        Raise ``ValueError`` for a negative count and ``MemoryError`` if
        allocation fails. Baseline time and retained space are ``O(num_nodes)``.
        """
        ...

    def add_hyperedges(
        self, num_hyperedges: int
    ) -> Iterator[HyperEdgeIndex[RawHyperEdgeIdT]]:
        """Add and yield ``num_hyperedges`` empty hyperedges atomically.

        Raise ``ValueError`` for a negative count and ``MemoryError`` if
        allocation fails. Baseline time and retained space are
        ``O(num_hyperedges)``.
        """
        ...


class MutableIncidenceHyperGraph[RawNodeIdT: Hashable, RawHyperEdgeIdT: Hashable](
    HyperGraph[RawNodeIdT, RawHyperEdgeIdT],
    Protocol,
):
    """Capability for idempotent mutation of the incidence relation."""

    def add_incidence(
        self,
        node: NodeIndex[RawNodeIdT],
        hyperedge: HyperEdgeIndex[RawHyperEdgeIdT],
    ) -> bool:
        """Ensure incidence and return whether both identifiers were valid.

        ``False`` corresponds to Rust's ``None`` and requires no logical
        mutation. ``True`` corresponds to ``Some(())`` and is idempotent.
        """
        ...

    def remove_incidence(
        self,
        node: NodeIndex[RawNodeIdT],
        hyperedge: HyperEdgeIndex[RawHyperEdgeIdT],
    ) -> bool:
        """Ensure non-incidence and return whether both identifiers were valid."""
        ...


class Missing:
    """Type of the property-map sentinel denoting an absent value."""

    __slots__ = ()
    _instance: ClassVar[Missing | None] = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "MISSING"


MISSING: Final = Missing()


class PropertyMapError(Exception):
    """Base class for checked property-map mutation errors."""


class PropertyMapKeyNotFoundError(PropertyMapError, KeyError):
    """The key is outside a property map's supported key domain."""


class PropertyMapBase[PropertyKeyT, PropertyValueT](Protocol):
    """Declares a property map's generic key and value types."""


class PropertyMapReadable[PropertyKeyT, PropertyValueT](
    PropertyMapBase[PropertyKeyT, PropertyValueT],
    Protocol,
):
    """Capability for checked property-map reads."""

    def get(self, key: PropertyKeyT) -> PropertyValueT | Missing:
        """Return the stored value or :data:`MISSING` in baseline ``O(1)``."""
        ...


class PropertyMapWritable[PropertyKeyT, PropertyValueT](
    PropertyMapBase[PropertyKeyT, PropertyValueT],
    Protocol,
):
    """Capability for checked property-map mutation."""

    def set(self, key: PropertyKeyT, value: PropertyValueT) -> PropertyValueT | Missing:
        """Set a value and return the previous value or :data:`MISSING`.

        Raise :class:`PropertyMapKeyNotFoundError` for a key outside the
        supported domain, leaving the map unchanged.
        """
        ...

    def remove(self, key: PropertyKeyT) -> PropertyValueT | Missing:
        """Remove and return a value, or :data:`MISSING` if none was stored.

        Raise :class:`PropertyMapKeyNotFoundError` for a key outside the
        supported domain, leaving the map unchanged.
        """
        ...


class PropertyMapReadWrite[PropertyKeyT, PropertyValueT](
    PropertyMapReadable[PropertyKeyT, PropertyValueT],
    PropertyMapWritable[PropertyKeyT, PropertyValueT],
    Protocol,
):
    """A property map supporting both reads and writes."""
