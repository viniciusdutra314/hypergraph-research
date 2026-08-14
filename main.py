import sys
import time
import warnings
from pathlib import Path
from string.templatelib import convert
from typing import cast

import hypergraphx as hgx
import hypernetx as hnx
import matplotlib.pyplot as plt
import networkx
import numpy as np
import xgi
from matplotlib.axes import Axes

CACHE_DIR = Path(__file__).parent / ".cache" / "xgi"


def load_hypergraph(dataset: str) -> xgi.Hypergraph:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{dataset}.json"

    if not cache_file.exists():
        xgi.download_xgi_data(dataset, path=str(CACHE_DIR))

    # warning interno da lib desnecessário
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        hypergraph = xgi.load_xgi_data(
            dataset,
            read=True,
            path=str(CACHE_DIR),
            cache=False,
        )
        assert isinstance(hypergraph, xgi.Hypergraph)
        return hypergraph


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


def main() -> None:
    h = load_hypergraph("physics-cocitations")
    h2 = convert_hypergraph(h, hnx.Hypergraph)


if __name__ == "__main__":
    main()
