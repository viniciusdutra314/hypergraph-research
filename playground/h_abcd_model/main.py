from hyperglue.generators.h_abcd import (
    generate_h_abcd,
    hypergraph_type,
    number_of_hyperedges,
    number_of_vertices,
    vertices_in_hyperedge,
)


def main() -> None:
    generated = generate_h_abcd(
        n=100,
        degree_exponent=2.5,
        minimum_degree=5,
        maximum_degree=20,
        community_exponent=1.5,
        minimum_community_size=10,
        maximum_community_size=30,
        mixing=0.3,
        hyperedge_size_weights=[0.0, 0.4, 0.3, 0.2, 0.1],
        composition="linear",
        seed=1234,
        maximum_iterations=100,
    )
    hypergraph = generated.hypergraph
    communities = generated.communities

    print("Hypergraph type:", hypergraph_type(hypergraph))
    print("Number of vertices:", number_of_vertices(hypergraph))
    print("Number of hyperedges:", number_of_hyperedges(hypergraph))
    print("Number of communities:", len(set(communities)))
    print(
        "Vertices in hyperedge 1:",
        vertices_in_hyperedge(hypergraph, 1),
    )


if __name__ == "__main__":
    main()
