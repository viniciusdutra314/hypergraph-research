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

### Views and materialization

Adapters and facades must be `O(1)` to construct, zero-copy live wrappers. Their
construction must not traverse, copy, snapshot, or materialize the underlying
hypergraph. Individual operations may derive data or allocate required result
containers, but must document meaningful time, memory, and snapshot-versus-view
behavior.

Never silently materialize a concrete target object as a fallback for an
unsupported facade operation. Raise a specific unsupported-operation error
instead. Full conversions must be explicit in the API and clearly named, such
as `materialize_xgi` or `materialize_hypernetx`. An explicit conversion must
document that it creates an independent object, its complexity, its identity
and ordering guarantees, and every required loss policy.

Use `Adapter`, `Facade`, `View`, or `as_*` for live zero-copy wrappers. Reserve
`to_*`, `convert_*`, or `materialize_*` for operations that allocate an
independent concrete representation.

## Python standards

- Target CPython according to `requires-python` in `pyproject.toml`; other
  Python interpreters are not a compatibility requirement.
- Use precise annotations on public and internal reusable code. Avoid `Any`;
  isolate unavoidable `Any` at third-party boundaries and narrow it promptly.
- Use `typing.Protocol`, generic node and hyperedge ID parameters, and
  `collections.abc` collection types. Prefer composition of narrow protocols.
- Project-owned adapters must explicitly inherit the canonical capability
  protocol they promise. Project-owned facades and their views must explicitly
  inherit narrow project-owned protocols for the supported target API; never
  inherit a third-party concrete hypergraph class.
- Mark required protocol members with `@abstractmethod` so an incomplete
  explicit implementation cannot be instantiated. Mark implementation members
  with `@override` so the strict type checker verifies names and signatures.
  External implementations may continue to satisfy protocols structurally.
- Do not use `@runtime_checkable` unless runtime structural checks are actually
  required.
- Raise specific exceptions for invalid external data. Do not use `assert` for
  validation or type narrowing.
- Reusable code belongs in importable packages, not in `main.py` or notebooks.

Rust code exposed to free-threaded CPython must be explicitly thread-safe. Do
not rely on the GIL to protect Rust or binding state. Document whether exposed
objects support concurrent reads or mutations, and detach from Python while
performing long Rust-only computations when appropriate.

## Python-Julia interoperability

Julia interoperability exists to call external research code from Python, not
to develop a separate Julia implementation in this repository. Treat the
external Julia package or paper implementation as the source of truth.

- Put the typed Python wrapper in `<name>.py` and call its public functions the
  same names as the Julia functions whenever practical.
- Put JuliaCall objects in private names such as `_jl` and `_julia_module`.
  Isolate unavoidable `Any` there and give every public Python function a
  precise signature and return type.
- Define the shared JuliaCall `LazyLoader` in `hyperglue.__init__`. Importing
  HyperGlue must not start Julia. Julia-backed modules consume that shared lazy
  module; do not add per-integration import loaders or function caches.
- Convert values explicitly at the boundary, such as Python sequences to Julia
  vectors, Python strings to Julia symbols, and returned Julia scalars to Python
  values.
- Add `<name>_bridge.jl` only when a small Julia adapter is required to call or
  reshape the external code. Do not reimplement its algorithms. Use
  `juliapkg.json` to declare and pin the external Julia dependencies.
- In Julia bridge implementations, prefer explicitly named keyword arguments
  when the called API supports them, especially when positional parameters are
  easy to confuse. Do not add a helper or wrapper solely to turn positional
  arguments into named arguments.
- Keep reusable wrappers out of `main.py`; use `main.py` only for an example or
  executable entry point.

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
uv run basedpyright
```

Every adapter and facade should share semantic conformance tests covering at
least empty hypergraphs, isolated nodes, empty and singleton hyperedges,
disconnected hypergraphs, non-integer and non-contiguous identifiers,
incidence equivalence, unsupported or lossy features, and live-view mutation
visibility when applicable. Compare communities independently of arbitrary
community labels or iteration order.

Prefer a small correct abstraction driven by a concrete algorithm over a
speculative universal API.
