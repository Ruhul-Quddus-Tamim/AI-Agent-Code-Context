# vers

Lightweight, simple, single instance, local in-memory vector database written in Rust.

Currently supports the following indexing strategies:

1. IVFFlat (k-means for partitioning)
2. Locality-sensitive hashing (LSH) heavily inspired by [fennel.ai's blog post](https://fennel.ai/blog/vector-search-in-200-lines-of-rust/).
3. Hierachical Navigable Small Worlds (HNSW)

This repository is educational. It was meant to understand how ANN search algorithms work under the hood for modern machine learning and is not meant for production (as a cursory scan of the codebase can probably tell you).

_"What I cannot build, I do not understand."_ - Feynman

### Getting Started

Like any sensible package, the API aims to be dead simple.

0. Import, obviously:

```rust
    use vers::indexes::base::{Index, Vector};
    use vers::indexes::ivfflat::IVFFlatIndex;
    use vers::indexes::hnsw::HNSWIndex;
```

1. Build an index:

```rust
    let mut index = IVFFlatIndex::build_index(
        num_clusters,
        num_attempts,
        max_iterations,
        &vectors
    );

    // or hnsw
    let mut index = HNSWIndex::build_index(
        num_layers,
        ef_construction,
        ef_search,
        num_neighbours,
        vectors
    )
```

2. Add an embedding vector into the index:

```rust
    index.add(Vector(*emb).normalize(), emb_unique_id);
```

3. Persist the index to disk:

```rust
    let _ = index.save_index("wiki.index");
```

4. Load the index from disk:

```rust
    // or use HNSWIndex::load_index, ANNIndex::load_index
    let index = match IVFFlatIndex::load_index("wiki.index") {
        Ok(index) => index,
        Err(e) => panic!("Failed to load index! {}", e),
    };
```

5. And of course, actually search the index:

```rust
    let results = hnsw.search_approximate(
        embs.get("king"),   // query vector
        10                  // top_k
    ); // kings, queen, monarch, ...
```

As shown above, all the indexes share the same API, whether IVFFlat, HNSW or LSH.

---

## How this relates to the Coding Agent

This project lives inside the broader **Code Generation Agent** repo (Python coding agent that can `read_file`, `search_file_content`, edit files, etc.).

At the moment:

- The coding agent does **not** yet use `vers` for its file/context search.
- All file operations are direct (no vector DB in the loop).

Future direction (optional, not implemented yet):

- Use `vers` as a **local vector store** to:
  - Index code snippets, file contents, or tool call logs
  - Do semantic search over project files to give the agent better context

Keeping `vers` separate makes it easy to:

- Iterate on ANN algorithms and data structures independently
- Plug it into the Python agent later (or into other projects) via clean APIs / bindings

If you only care about the coding agent, you can ignore this folder for now.

If you want to play with ANN/vector search, this is your playground.

---

### Python Bindings (via `vers_py`)

There is a small Python wrapper crate in `vers/vers-py` built with **pyo3 + maturin**, which exposes a limited API (e.g. a `get_sum` helper and wiki-vector tests).

After building and installing the wheel (see `vers/vers-py/pyproject.toml`), you can do:

```python
import vers_py as vers

# simple smoke test
v = vers.get_sum([1.0] * 300, [2.0] * 300)
print(v.get_inner()[:3])  # -> [3.0, 3.0, 3.0]
```

### Running adhoc benchmark tests

```
    cargo build --release
    samply record ./target/release/vers
```
