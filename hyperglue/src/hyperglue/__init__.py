"""Interoperability tools for the Python hypergraph ecosystem."""

import importlib.util
import sys
from typing import cast

import hypergraphx as hgx  # pyright: ignore[reportMissingTypeStubs]
import hypernetx as hnx  # pyright: ignore[reportMissingTypeStubs]
import xgi


def _lazy_import(name: str):  # taken from python docs and correctly typed
    spec = importlib.util.find_spec(name)
    assert spec is not None
    spec_loader = spec.loader
    assert spec_loader is not None
    loader = importlib.util.LazyLoader(spec_loader)
    spec.loader = loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    loader.exec_module(module)
    return module


juliacall = _lazy_import("juliacall")


def convert_hypergraph[
    T: (xgi.Hypergraph, hnx.Hypergraph | hgx.Hypergraph),
](value: xgi.Hypergraph | hnx.Hypergraph | hgx.Hypergraph, desired_type: type[T]) -> T:
    match value:
        case xgi.Hypergraph():
            hif_data = xgi.to_hif_dict(value)
        case hnx.Hypergraph():
            hif_data = hnx.to_hif(value)
        case hgx.Hypergraph():
            hif_data = hgx.readwrite.to_hif_dict(value)
    hif_data = cast(hgx.readwrite.HIFJson, hif_data)
    match desired_type:
        case xgi.Hypergraph:
            converted = xgi.from_hif_dict(hif_data)
        case hnx.Hypergraph:
            converted = hnx.from_hif(hif=hif_data)
        case hgx.Hypergraph:
            converted = hgx.readwrite.from_hif_dict(hif_data)
        case _:
            raise TypeError(f"Unsupported target hypergraph: {desired_type!r}")

    if not isinstance(converted, desired_type):
        raise TypeError(
            f"HIF conversion produced {type(converted)!r}, expected {desired_type!r}"
        )
    return cast(T, converted)
