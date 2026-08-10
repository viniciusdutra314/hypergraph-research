import time
import warnings
from pathlib import Path
from typing import cast

import matplotlib.pyplot as plt
import networkx
import numpy as np
import xgi
from matplotlib.axes import Axes

CACHE_DIR = Path(__file__).parent / ".cache" / "xgi"


def cache_datasets_if_not_present(datasets: list[str]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    for dataset in datasets:
        cache_file = CACHE_DIR / f"{dataset}.json"
        if not cache_file.exists():
            xgi.download_xgi_data(dataset, path=str(CACHE_DIR))


def load_hypergraph(dataset: str) -> xgi.Hypergraph:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        h = xgi.load_xgi_data(dataset, read=True, path=str(CACHE_DIR), cache=False)
        assert isinstance(h, xgi.Hypergraph)
        return h


def main() -> None:
    cache_datasets_if_not_present(["physics-cocitations"])
    h = load_hypergraph("physics-cocitations")
    fig, ax = plt.subplots(1, 2)
    ax_degree = cast(Axes, ax[0])
    ax_edges = cast(Axes, ax[1])
    ax_degree.bar(
        *np.unique(h.nodes.degree.asnumpy(), return_counts=True), color="blue"
    )
    ax_degree.set_xlabel("Degree")
    ax_degree.set_ylabel("Count")
    ax_edges.bar(*np.unique(h.edges.size.asnumpy(), return_counts=True), color="red")
    ax_edges.set_xlabel("Edge Size")
    ax_edges.set_ylabel("Count")
    plt.show()


if __name__ == "__main__":
    main()
