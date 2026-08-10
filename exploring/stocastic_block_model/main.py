import itertools
import random

import networkx as nx


def simple_SBM(partitions_sizes: list[int], prob_matrix: list[list[float]]) -> nx.Graph:
    g: nx.Graph = nx.empty_graph(sum(partitions_sizes))
    num_blocks = len(partitions_sizes)
    cumulative_sum = [0, *itertools.accumulate(partitions_sizes)]

    for s_block, t_block in itertools.combinations_with_replacement(
        range(num_blocks), 2
    ):
        s_nodes = range(
            cumulative_sum[s_block],
            cumulative_sum[s_block + 1],
        )
        t_nodes = range(
            cumulative_sum[t_block],
            cumulative_sum[t_block + 1],
        )
        probability = prob_matrix[s_block][t_block]
        pairs = (
            itertools.product(s_nodes, t_nodes)
            if s_block != t_block
            else itertools.combinations(s_nodes, 2)
        )
        for s, t in pairs:
            if probability > random.random():
                g.add_edge(s, t)
    return g


def main():
    g = simple_SBM(
        [15, 15, 15, 15],
        [
            [0.45, 0.08, 0.01, 0.08],
            [0.08, 0.45, 0.08, 0.01],
            [0.01, 0.08, 0.45, 0.08],
            [0.08, 0.01, 0.08, 0.45],
        ],
    )
    import matplotlib.pyplot as plt

    nx.draw(g, with_labels=True)
    plt.show()


if __name__ == "__main__":
    main()
