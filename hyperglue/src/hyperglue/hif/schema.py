"""Typed representation of the Hypergraph Interchange Format."""

from typing import Literal, NotRequired, TypedDict

type HIF_ID = str | int
type Weight = int | float
type JSONValue = (
    None | bool | int | float | str | list["JSONValue"] | dict[str, "JSONValue"]
)
type Metadata = dict[str, JSONValue]
type NetworkType = Literal["asc", "directed", "undirected"]
type Direction = Literal["head", "tail"]
type UndirectedEdge = tuple[HIF_ID, ...]
type DirectedEdge = tuple[tuple[HIF_ID, ...], tuple[HIF_ID, ...]]
type EdgeKey = UndirectedEdge | DirectedEdge
type UndirectedEdgeMembers = list[HIF_ID]
type DirectedEdgeMembers = tuple[list[HIF_ID], list[HIF_ID]]


class HIFNodeRecord(TypedDict):
    node: HIF_ID
    weight: NotRequired[Weight]
    attrs: NotRequired[Metadata]


class HIFEdgeRecord(TypedDict):
    edge: HIF_ID
    weight: NotRequired[Weight]
    attrs: NotRequired[Metadata]


class HIFIncidenceRecord(TypedDict):
    edge: HIF_ID
    node: HIF_ID
    weight: NotRequired[Weight]
    direction: NotRequired[Direction]
    attrs: NotRequired[Metadata]


HIFJson = TypedDict(
    "HIFJson",
    {
        "network-type": NotRequired[NetworkType],
        "metadata": NotRequired[Metadata],
        "incidences": list[HIFIncidenceRecord],
        "nodes": NotRequired[list[HIFNodeRecord]],
        "edges": NotRequired[list[HIFEdgeRecord]],
    },
)
