"""
Streamlit-based UI for the coding agent.
"""

import streamlit as st
import json
from coding_agent import coding_agent
from tools import tools
from tools_schemas import tools_schemas
from openai import OpenAI
import base64
from PIL import Image
from io import BytesIO


def display_message(part_dict):
    """Display a message part in Streamlit."""
    part_type = part_dict.get("type")
    
    if part_type == "reasoning":
        st.info("🤔 Thinking...")
    elif part_type == "message":
        content = part_dict.get("content")
        if content:
            if isinstance(content, list):
                for item in content:
                    if item.get("text"):
                        st.write(item["text"])
            elif isinstance(content, str):
                st.write(content)
    elif part_type == "function_call":
        name = part_dict.get("name")
        arguments = part_dict.get("arguments")
        with st.expander(f"🛠️ Using {name}", expanded=False):
            st.code(json.dumps(json.loads(arguments), indent=2), language="json")
    elif part_type == "function_call_output":
        output = part_dict.get("output")
        result = json.loads(output)
        with st.expander("✅ Tool Result", expanded=False):
            st.json(result)
        
        # Display images if any
        metadata = part_dict.get("_metadata")
        if metadata and "images" in metadata:
            for img_base64 in metadata["images"]:
                img_data = base64.b64decode(img_base64)
                img = Image.open(BytesIO(img_data))
                st.image(img, caption="Generated Plot")


def main():
    st.set_page_config(
        page_title="Code Generation Agent",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Code Generation Agent")
    st.markdown("Ask the agent to write and execute Python code for you!")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "usage" not in st.session_state:
        st.session_state.usage = 0
    if "client" not in st.session_state:
        # Get API key from environment, secrets, or sidebar
        import os
        api_key = os.getenv("OPENAI_API_KEY", "")
        
        # Try to get from Streamlit secrets (if available)
        try:
            if hasattr(st, "secrets") and "OPENAI_API_KEY" in st.secrets:
                api_key = st.secrets["OPENAI_API_KEY"]
        except (FileNotFoundError, KeyError):
            pass
        
        # If still no key, get from sidebar
        if not api_key:
            api_key = st.sidebar.text_input(
                "OpenAI API Key",
                type="password",
                help="Enter your OpenAI API key. You can also set it as an environment variable OPENAI_API_KEY."
            )
            if not api_key:
                st.error("Please enter your OpenAI API key in the sidebar or set OPENAI_API_KEY environment variable")
                st.stop()
        
        st.session_state.client = OpenAI(api_key=api_key)
    
    # Display chat history
    for message in st.session_state.messages:
        # Handle different message types
        if "role" in message:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message.get("content", ""))
            elif message["role"] == "assistant":
                with st.chat_message("assistant"):
                    content = message.get("content", "")
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and "text" in item:
                                st.write(item["text"])
                    else:
                        st.write(content)
        elif "type" in message:
            # Handle function calls and other special message types
            display_message(message)
    
    # Chat input
    if prompt := st.chat_input("Ask the agent to write some code..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # Run the agent
                agent_gen = coding_agent(
                    client=st.session_state.client,
                    query=prompt,
                    tools=tools,
                    tools_schemas=tools_schemas,
                    system="You are a senior python programmer. Write clean, efficient, and well-documented code.",
                    messages=st.session_state.messages[:-1],  # Exclude the just-added user message
                    usage=st.session_state.usage,
                )
                
                # Process the generator
                for part_dict, messages, usage in agent_gen:
                    st.session_state.messages = messages
                    st.session_state.usage = usage
                    
                    # Display the part
                    display_message(part_dict)
                
                # Get final response text for the chat message
                for msg in reversed(messages):
                    if msg.get("role") == "assistant":
                        content = msg.get("content")
                        if content:
                            if isinstance(content, list):
                                for item in content:
                                    if isinstance(item, dict) and item.get("text"):
                                        full_response = item["text"]
                                        break
                            elif isinstance(content, str):
                                full_response = content
                            if full_response:
                                break
                
                if full_response:
                    message_placeholder.write(full_response)
                else:
                    message_placeholder.write("✅ Task completed. Check the tool results above.")
                
                # Show token usage
                st.caption(f"Total tokens used: {st.session_state.usage}")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
    
    # Sidebar info
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        This agent can:
        - Write and execute Python code
        - Manage files (read, write, search)
        - Create visualizations
        - Handle errors and iterate
        """)
        
        if st.button("Clear Conversation"):
            st.session_state.messages = []
            st.session_state.usage = 0
            st.rerun()
        
        st.metric("Total Tokens", st.session_state.usage)

