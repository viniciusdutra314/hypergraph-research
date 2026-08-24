# pyright: reportAny=false, reportExplicitAny=false, reportMissingImports=false, reportMissingTypeStubs=false, reportUnknownMemberType=false, reportUnnecessaryCast=false

from pathlib import Path
from typing import Any, cast

import juliacall

jl = cast(Any, juliacall.newmodule("HABCD"))
h_abcd = cast(Any, jl.include(str(Path(__file__).with_name("h_wrapper_abcd.jl"))))


def main() -> None:
    generated = h_abcd.generate_h_abcd()
    hypergraph = generated.hypergraph
    communities = generated.communities

    print("Hypergraph type:", jl.typeof(hypergraph))
    print("Number of vertices:", h_abcd.SimpleHypergraphs.nhv(hypergraph))
    print("Number of hyperedges:", h_abcd.SimpleHypergraphs.nhe(hypergraph))
    print("Number of communities:", len(set(map(int, communities))))
    print(
        "Vertices in hyperedge 1:",
        list(h_abcd.vertices_in_hyperedge(hypergraph, 1)),
    )


if __name__ == "__main__":
    main()
