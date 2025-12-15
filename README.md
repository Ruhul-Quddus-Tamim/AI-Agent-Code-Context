# Code Generation Agent

A coding agent that writes and executes Python code locally on your machine. The agent can manage files, execute code, and handle errors through iterative feedback loops.

## Features

- ✅ **Local Code Execution**: All code runs directly on your local machine (no sandbox required)
- ✅ **File Operations**: Read, write, search, and manage files
- ✅ **Streamlit Web UI**: Interface for chatting with the agent
- ✅ **Python 3.12 Compatible**: Works with Python 3.12

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

## Example Queries

- "Create a Python script that reads a CSV file and plots a bar chart"
- "Generate a simple web server using Flask"
- "Create a data analysis script for a dataset"
- "List all the files in my current directory?"
- "Which files have these green menu label colors?"

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

