module HABCDWrapper

using ABCDHypergraphGenerator
using Random
using SimpleHypergraphs

export BoolHypergraph, HABCDResult, generate_h_abcd, vertices_in_hyperedge

const BoolHypergraph =
    SimpleHypergraphs.Hypergraph{Bool,Nothing,Nothing,Dict{Int,Bool}}
const HABCDResult = @NamedTuple{
    hypergraph::BoolHypergraph,
    communities::Vector{Int},
}

const GENERATION_LOCK = ReentrantLock()

function composition_weights(
    ;
    q::AbstractVector{<:Real},
    mode::Symbol,
)::Matrix{Float64}
    mode in (:strict, :linear, :majority) ||
        throw(ArgumentError("composition must be :strict, :linear, or :majority"))

    w = zeros(Float64, length(q), length(q))
    for d in eachindex(q)
        first_majority = div(d, 2) + 1
        if mode == :strict
            w[d, d] = 1.0
        elseif mode == :linear
            for c in first_majority:d
                w[c, d] = c
            end
            w[:, d] ./= sum(w[:, d])
        else
            w[first_majority:d, d] .= 1.0 / (d - div(d, 2))
        end
    end
    return w
end

vertices_in_hyperedge(
    hypergraph::BoolHypergraph,
    hyperedge_id::Int,
)::Vector{Int} =
    collect(keys(SimpleHypergraphs.getvertices(hypergraph, hyperedge_id)))

function generate_h_abcd(;
    n::Integer=100,
    degree_exponent::Real=2.5,
    minimum_degree::Integer=5,
    maximum_degree::Integer=20,
    community_exponent::Real=1.5,
    minimum_community_size::Integer=10,
    maximum_community_size::Integer=30,
    mixing::Real=0.3,
    hyperedge_size_weights::AbstractVector{<:Real}=[0.0, 0.4, 0.3, 0.2, 0.1],
    composition::Symbol=:linear,
    seed::Integer=1234,
    maximum_iterations::Integer=100,
)::HABCDResult
    return lock(GENERATION_LOCK) do
        Random.seed!(seed)
        degrees = ABCDHypergraphGenerator.sample_degrees(
            degree_exponent,
            minimum_degree,
            maximum_degree,
            n,
        )
        community_sizes = ABCDHypergraphGenerator.sample_communities(
            community_exponent,
            minimum_community_size,
            maximum_community_size,
            n,
            1000,
        )
        q = Float64.(hyperedge_size_weights)
        params = ABCDHypergraphGenerator.ABCDHParams(
            degrees,
            community_sizes,
            mixing,
            q,
            composition_weights(; q=q, mode=composition),
            true,
            maximum_iterations,
        )
        generated = ABCDHypergraphGenerator.gen_hypergraph(params)

        hypergraph = SimpleHypergraphs.Hypergraph{Bool}(n, length(generated.hyperedges))
        for (hyperedge_id, vertices) in enumerate(generated.hyperedges)
            for node_id in vertices
                hypergraph[node_id, hyperedge_id] = true
            end
        end

        return (hypergraph=hypergraph, communities=copy(generated.clusters))
    end
end

end
