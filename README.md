# Code Generation Agent

A coding agent that writes and executes Python code locally on your machine. The agent can manage files, execute code, and handle errors through iterative feedback loops.

## Features

- ✅ **Local Code Execution**: All code runs directly on your local machine (no sandbox required)
- ✅ **File Operations**: Read, write, search, and manage files
- ✅ **Streamlit**: Use a Streamlit web app to chat with the agent
- ✅ **Python 3.12 Compatible**: Works with Python 3.12

## Optional: Local Vector Database (vers)

This repo also includes an **educational vector database** in `AI-Agent-Code-Context/vers`:

- Written in Rust
- In‑memory single-instance vector DB
- Supports **IVFFlat**, **LSH**, and **HNSW** indexes
- Can be used as a building block for future code-context search (e.g., indexing `read_file` / `search_file_content` results), but is **not wired into the coding agent yet**.

If you want to experiment with it later:

- Rust crate: `AI-Agent-Code-Context/vers`
- Python bindings: `AI-Agent-Code-Context/vers/vers-py` (installed as `vers_py`)

### vers (Rust) quick start

- **Concept**: lightweight, single-instance, in-memory ANN (approximate nearest neighbour) vector database.
- **Indexes available**:
  - `IVFFlat` (k-means partitioning)
  - `LSH` (locality-sensitive hashing, inspired by fennel.ai’s 200-line Rust post)
  - `HNSW` (Hierarchical Navigable Small Worlds)

Basic Rust usage (inside a separate Rust project that depends on `vers`):

```rust
use vers::indexes::base::{Index, Vector};
use vers::indexes::ivfflat::IVFFlatIndex;
use vers::indexes::hnsw::HNSWIndex;

// Build an IVFFlat index
let mut index = IVFFlatIndex::build_index(
    num_clusters,
    num_attempts,
    max_iterations,
    &vectors,
);

// Or HNSW
let mut index = HNSWIndex::build_index(
    num_layers,
    ef_construction,
    ef_search,
    num_neighbours,
    vectors,
);

// Add a vector
index.add(Vector(*emb).normalize(), emb_unique_id);

// Save & load
let _ = index.save_index("wiki.index");
let index = IVFFlatIndex::load_index("wiki.index").expect("Failed to load index");

// Search
let results = index.search_approximate(query_vec, 10);
```

### vers Python bindings (via `vers_py`)

The `vers/vers-py` crate exposes a minimal Python API using **pyo3 + maturin**.

After building and installing the wheel (already done in this setup), you can:

```python
import vers_py as vers

# Simple smoke test
v = vers.get_sum([1.0] * 300, [2.0] * 300)
print(v.get_inner()[:3])  # [3.0, 3.0, 3.0]
```

> Note: The Python API is experimental and currently focused on helpers and wiki-vector tests; the coding agent itself does **not** depend on it.

### vers benchmarks

From `AI-Agent-Code-Context/vers` you can run adhoc benchmarks (HNSW / IVFFlat performance):

```bash
cd AI-Agent-Code-Context/vers
cargo +nightly build --release
cargo +nightly bench
```

The `benches/benchmark.rs` file uses `criterion` to benchmark IVFFlat index building on sample embeddings.

### Future: Scaling the Coding Agent with vers

The coding agent:

- Uses direct filesystem tools (`read_file`, `search_file_content`, `glob`, etc.).
- Works well for small–medium projects but will eventually hit limits when:
  - Searching across **thousands of files**
  - Needing **semantic** (embedding-based) search over code and docs
  - Keeping track of **high‑dimensional history/context** across many tool calls.

In the future, `vers` can be plugged in as a **local vector store** to:

- Periodically or on-demand **embed** file contents, code snippets, and tool outputs.
- Store embeddings in an HNSW / IVFFlat / LSH index for **fast approximate nearest‑neighbor search**.
- Let the agent:
  - Do “search in context” before answering (retrieve top‑k relevant files/snippets).
  - Narrow down huge codebases to a small relevant subset per query.
  - Maintain a **long‑term semantic memory** of previous conversations or edits, all locally.

Because `vers` is:

- **In‑memory**, single‑instance, and local
- Written in Rust with SIMD‑accelerated math

…it’s a good fit for **scaling the assistant’s retrieval** without introducing external services or remote databases. This integration path is optional and can be implemented incrementally (e.g., start by indexing only filenames + summaries, then full file contents, then tool traces, etc.).

## Prerequisites

- Python 3.12 (or Python 3.8+)
- OpenAI API key

## Installation

1. **Clone or navigate to this directory:**
   ```bash
   cd /Users/sitifatimahali/Desktop/exp/code_agent
   ```

2. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

   Or if you prefer to use a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set your OpenAI API key:**
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

   Or add it to your shell profile (`~/.zshrc` or `~/.bashrc`):
   ```bash
   echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.zshrc
   source ~/.zshrc
   ```

## Running the Application

### Using Streamlit (Recommended)
```bash
cd AI-Agent-Code-Context
streamlit run main.py
```

The web interface will automatically open in your browser at: **http://localhost:8501**

### Using Terminal Interface (Alternative)
If you prefer a terminal-based interface:
```bash
cd AI-Agent-Code-Context
python3 terminal_ui.py
```

## Usage

1. Open your browser and navigate to `http://localhost:7860`
2. Type your request in the chat interface (e.g., "Write a Python function to calculate fibonacci numbers")
3. The agent will write and execute code to fulfill your request
4. View the results, code, and any generated visualizations in the interface

## Example Queries

- "Create a Python script that reads a CSV file and plots a bar chart"
- "Write a function to sort a list of dictionaries by a specific key"
- "Generate a simple web server using Flask"
- "Create a data analysis script for a dataset"

## Troubleshooting

### Import Errors
If you encounter import errors, make sure you're running from the correct directory or using the `run.py` script.

### Missing Dependencies
If you get errors about missing packages, install them:
```bash
pip3 install rapidfuzz matplotlib numpy pandas
```

### OpenAI API Key
Make sure your `OPENAI_API_KEY` environment variable is set:
```bash
echo $OPENAI_API_KEY  # Should print your key
```

## Notes

- Code execution happens **locally** on your machine - be careful with what code you ask the agent to run
- The agent has access to your local filesystem (within the working directory)
- For fuzzy search functionality, make sure `rapidfuzz` is installed
- Matplotlib plots are automatically captured and displayed in the UI

