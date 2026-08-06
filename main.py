import time
from pathlib import Path
from typing import Any

import xgi
from xgi.core import Hypergraph

CACHE_DIR = Path(__file__).parent / ".cache" / "xgi"


def cache_datasets_if_not_present(datasets: list[str]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    for dataset in datasets:
        cache_file = CACHE_DIR / f"{dataset}.json"
        if not cache_file.exists():
            xgi.download_xgi_data(dataset, path=str(CACHE_DIR))


def load_hypergraph(dataset: str) -> Hypergraph:
    h = xgi.load_xgi_data(dataset, read=True, path=str(CACHE_DIR), cache=False)
    assert isinstance(h, Hypergraph)
    return h


def main() -> None:
    cache_datasets_if_not_present(["physics-cocitations"])
    time_start = time.time()
    hypergraph = load_hypergraph("physics-cocitations")
    time_end = time.time()
    print(f"Time taken: {time_end - time_start}")


if __name__ == "__main__":
    main()
