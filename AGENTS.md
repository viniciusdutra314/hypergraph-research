# HGraphs Python interoperability guide

This repository integrates the Rust HGraphs library with the Python hypergraph
ecosystem. Python code provides typed protocols, bindings, adapters, explicit
conversions, experiments, and interoperability with libraries such as XGI and
HyperNetX. Algorithms and data structures that belong to the reusable
computational core remain in Rust.

For work under `HGraphs/`, also follow `HGraphs/AGENTS.md`. Its more specific
instructions take precedence within that workspace.

## Source of truth

The Rust traits and their documentation are the authoritative semantic
contract. Python protocols map those traits into Python; they do not define an
independent hypergraph model.

- Do not duplicate complete Rust documentation in Python docstrings.
- Give each Python protocol a short reference to its corresponding Rust trait.
- Document Python-specific mappings and deliberate differences, including
  exceptions, `None` or sentinel values, iterator and view lifetimes, ownership,
  mutability, and concurrency behavior.
- Do not repeat Rust complexity guarantees for third-party adapters unless the
  adapter independently provides and documents the same guarantee.
- Keep an explicit mapping between Rust traits and Python protocols. Test every
  observable semantic translation at the language boundary.

## Interoperability design

Use a hub-and-spoke, capability-based architecture:

```text
source object -> backend adapter -> canonical protocols -> project algorithm
                                                    -> target facade
                                                    -> explicit conversion
```

- Define small, project-owned `Protocol` interfaces corresponding to Rust
  capabilities.
- Write algorithms against the weakest sufficient protocols.
- Implement one backend adapter per storage library, including HGraphs, XGI,
  and HyperNetX. Do not create converters for every ordered pair of libraries.
- Use a target facade only for a documented public duck-typed API. If a
  consumer needs a concrete third-party class or private state, perform an
  explicit materialized conversion.
- Prefer composition over subclassing third-party hypergraph classes.
- Start with read-only views. Put mutation in separate protocols with explicit
  visibility, invalidation, and atomicity guarantees.
- Keep bindings thin and use bulk typed operations across the Rust/Python
  boundary. Domain logic stays in Rust.

Preserve node and hyperedge identity, incidence, isolated nodes, empty and
singleton hyperedges, directedness, multiplicity, weights, attributes, and any
promised ordering. Keep node and hyperedge identifiers as distinct generic
types; never assume they are integers, contiguous, interchangeable, or stable
after mutation. When a target cannot represent a feature, require an explicit
loss policy or raise a typed error.

Use a canonical incidence snapshot for conversions. It must represent nodes,
hyperedges, and incidences separately so that isolated nodes and empty
hyperedges are not lost. Add optional metadata only for concrete use cases.

## Python standards

- Target CPython according to `requires-python` in `pyproject.toml`; other
  Python interpreters are not a compatibility requirement.
- Use precise annotations on public and internal reusable code. Avoid `Any`;
  isolate unavoidable `Any` at third-party boundaries and narrow it promptly.
- Use `typing.Protocol`, generic node and hyperedge ID parameters, and
  `collections.abc` collection types. Prefer composition of narrow protocols.
- Do not use `@runtime_checkable` unless runtime structural checks are actually
  required.
- Raise specific exceptions for invalid external data. Do not use `assert` for
  validation or type narrowing.
- Reusable code belongs in importable packages, not in `main.py` or notebooks.

Rust code exposed to free-threaded CPython must be explicitly thread-safe. Do
not rely on the GIL to protect Rust or binding state. Document whether exposed
objects support concurrent reads or mutations, and detach from Python while
performing long Rust-only computations when appropriate.

## Tooling

Use `uv` for all Python environments, dependencies, and commands. Treat
`pyproject.toml` and `uv.lock` as authoritative and commit them together.

- Add runtime dependencies with `uv add` and development tools with
  `uv add --dev`. Do not invoke `pip` directly.
- Write native pytest tests and use fixtures and parametrization for shared
  adapter conformance suites. Do not add `unittest.TestCase` tests.
- Use Ruff as both formatter and linter.
- Keep code compatible with the project's configured strict type checker. Do
  not suppress errors broadly; narrow third-party types locally and explain any
  unavoidable targeted suppression.

Before handing off a normal Python change, run the relevant subset of:

```text
uv run ruff format --check .
uv run ruff check .
uv run pytest
uv run <configured-type-checker>
```

Every adapter and facade should share semantic conformance tests covering at
least empty hypergraphs, isolated nodes, empty and singleton hyperedges,
disconnected hypergraphs, non-integer and non-contiguous identifiers,
incidence equivalence, unsupported or lossy features, and live-view mutation
visibility when applicable. Compare communities independently of arbitrary
community labels or iteration order.

Prefer a small correct abstraction driven by a concrete algorithm over a
speculative universal API.
