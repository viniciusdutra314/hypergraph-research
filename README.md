# hypergraph-research

The `hypergraph_protocols` package maps the HGraphs Rust capability traits into
Python protocols and integrates them with XGI and HyperNetX.

## XGI and HyperNetX interoperability

Backend adapters expose live third-party storage through the canonical
protocols. Target façades expose a documented read-only subset of the target
library's public shape without creating a new concrete hypergraph:

```python
from hypergraph_protocols.adapters import HyperNetXAdapter
from hypergraph_protocols.facades import XGIFacade

adapter = HyperNetXAdapter[str, str](hypernetx_hypergraph)
xgi_view = XGIFacade(adapter)
components = list(xgi.connected_components(xgi_view))
```

`XGIAdapter` preserves isolated nodes and empty hyperedges stored by XGI.
HyperNetX 2.4 derives both identity sets from its incidence store, so
`HyperNetXAdapter` cannot recover isolated nodes or empty hyperedges discarded
by a concrete `hnx.Hypergraph`. A façade over another canonical backend can
still present those identities without performing a lossy conversion.
