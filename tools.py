import json
import subprocess
import sys
import io
import contextlib
from typing import Callable, Optional
from sbx_tools import (
    list_directory,
    read_file,
    write_file,
    replace_in_file,
    search_file_content,
    glob,
    secure_path,
    ToolError,
)


def execute_code(code: str, language: str = "python"):
    """Execute code locally and return results."""
    metadata = {}
    
    if language == "python":
        # Capture stdout and stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        # Create a namespace for code execution
        namespace = {
            "__builtins__": __builtins__,
            "__name__": "__main__",
        }
        
        # Try to import common libraries that might be used
        try:
            import matplotlib
            matplotlib.use("Agg")  # Use non-interactive backend
            import matplotlib.pyplot as plt
            namespace["plt"] = plt
            namespace["matplotlib"] = matplotlib
        except ImportError:
            pass
        
        try:
            import numpy as np
            namespace["np"] = np
        except ImportError:
            pass
        
        try:
            import pandas as pd
            namespace["pd"] = pd
        except ImportError:
            pass
        
        result_value = None
        error = None
        
        try:
            with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
                # Execute the code
                exec(code, namespace)
                # Try to get the last expression result if it's a single expression
                if code.strip() and not code.strip().endswith(":"):
                    try:
                        result_value = eval(code.strip(), namespace)
                    except:
                        pass
        except Exception as e:
            error = str(e)
        
        stdout_text = stdout_capture.getvalue()
        stderr_text = stderr_capture.getvalue()
        
        # Check for matplotlib figures and convert to base64
        try:
            import matplotlib.pyplot as plt
            import base64
            from io import BytesIO
            
            if plt.get_fignums():
                buf = BytesIO()
                plt.savefig(buf, format="png", bbox_inches="tight")
                buf.seek(0)
                img_base64 = base64.b64encode(buf.read()).decode("utf-8")
                metadata["images"] = [img_base64]
                plt.close("all")
        except:
            pass
        
        # Build result
        result = {
            "stdout": stdout_text,
            "stderr": stderr_text,
        }
        
        if error:
            result["error"] = error
        elif result_value is not None:
            result["result"] = str(result_value)
        
        return result, metadata
        
    elif language == "bash":
        # Execute bash command using subprocess
        try:
            process = subprocess.run(
                code,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
            result = {
                "stdout": process.stdout,
                "stderr": process.stderr,
                "returncode": process.returncode,
            }
            if process.returncode != 0:
                result["error"] = f"Command failed with return code {process.returncode}"
            return result, metadata
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out after 30 seconds"}, metadata
        except Exception as e:
            return {"error": str(e)}, metadata
    else:
        return {"error": f"Unsupported language: {language}"}, metadata


tools = {
    "execute_code": lambda code, language="python": execute_code(code, language),
    "execute_bash": lambda code: execute_code(code, language="bash"),
    "list_directory": lambda path=".", ignore=None, offset=0, limit=16: (
        list_directory(secure_path(path), ignore, offset, limit),
        {},
    ),
    "read_file": lambda file_path, limit=None, offset=0: (
        read_file(secure_path(file_path), limit, offset),
        {},
    ),
    "write_file": lambda content, file_path: (
        write_file(content, secure_path(file_path)),
        {},
    ),
    "replace_in_file": lambda file_path, old_string, new_string, expected_replacements=1: (
        replace_in_file(
            secure_path(file_path), old_string, new_string, expected_replacements
        ),
        {},
    ),
    "search_file_content": lambda pattern, include=None, path=".", use_regex=False, fuzzy_threshold=None, offset=0, limit=16: (
        search_file_content(
            pattern, include, secure_path(path), use_regex, fuzzy_threshold, offset, limit
        ),
        {},
    ),
    "glob": lambda pattern, path=".", ignore=None, offset=0, limit=16: (
        glob(pattern, secure_path(path), ignore, offset, limit),
        {},
    ),
}


def execute_tool(name: str, args: str, tools: dict[str, Callable], **kwargs):
    metadata = {}
    try:
        args = json.loads(args)
        if name not in tools:
            return {"error": f"Tool {name} doesn't exist."}
        result, metadata = tools[name](**args)
    except json.JSONDecodeError as e:
        result = {"error": f"{name} failed to parse arguments: {str(e)}"}
    except ToolError as e:
        result = {"error": str(e)}
    except KeyError as e:
        result = {"error": f"Missing key in arguments: {str(e)}"}
    except Exception as e:
        result = {"error": str(e)}
    return result, metadata
