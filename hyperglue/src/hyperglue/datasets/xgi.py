import warnings
from pathlib import Path

import xgi

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
