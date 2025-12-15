"""
Main entry point for the Code Generation Agent application.
Run this file with: streamlit run main.py
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the package
# This allows running the script from the AI-Agent-Code-Context directory
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Set default API key if not in environment
if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = "sk-proj-"

# Import and run Streamlit app
if __name__ == "__main__":
    from streamlit_ui import main
    main()

