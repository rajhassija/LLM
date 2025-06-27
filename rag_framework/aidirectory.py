import streamlit as st
import os
import json

# Placeholder for storing app configurations
APPS_CONFIG_FILE = "apps_config.json"

def load_apps():
    if os.path.exists(APPS_CONFIG_FILE):
        with open(APPS_CONFIG_FILE, "r") as file:
            return json.load(file)
    return {}

def save_apps(apps):
    with open(APPS_CONFIG_FILE, "w") as file:
        json.dump(apps, file, indent=4)

def main():
    st.title("AI RAG Chatbot Manager")
    
    apps = load_apps()
    
    if "selected_app" not in st.session_state:
        st.session_state["selected_app"] = None
    
    if "selected_files" not in st.session_state:
        st.session_state["selected_files"] = []
    
    if st.button("Create New App"):
        st.session_state["selected_app"] = "Create New App"
        st.experimental_rerun()
    
    if st.session_state["selected_app"] is None:
        st.subheader("Existing Apps")
        if apps:
            for app_name in apps.keys():
                if st.button(app_name):
                    st.session_state["selected_app"] = app_name
                    st.experimental_rerun()
        else:
            st.write("No apps created yet.")
    
    elif st.session_state["selected_app"] == "Create New App":
        st.subheader("Create a New Chatbot App")
        app_name = st.text_input("App Name")
        
        uploaded_files = st.file_uploader(
            "Select Files",
            accept_multiple_files=True,
            type=None
        )
        
        if uploaded_files:
            st.session_state["selected_files"].extend(uploaded_files)
        
        st.write("Selected Files:")
        for file in st.session_state["selected_files"]:
            st.text(file.name)
        
        if st.button("Save & Ingest Sources"):
            if app_name.strip() and st.session_state["selected_files"]:
                apps[app_name] = {
                    "sources": [file.name for file in st.session_state["selected_files"]]
                }
                save_apps(apps)
                st.success(f"App '{app_name}' created successfully!")
                st.session_state["selected_app"] = app_name
                st.experimental_rerun()
            else:
                st.error("App name and at least one source are required.")
    
    else:
        st.subheader(f"Chat with {st.session_state['selected_app']}")
        user_input = st.text_input("Ask a question:")
        if st.button("Submit"):
            st.session_state.setdefault("conversation", []).append(("User", user_input))
            
            # Placeholder for AI response
            response = "(AI Response Placeholder)"
            st.session_state["conversation"].append(("AI", response))
        
        # Display conversation
        if "conversation" in st.session_state:
            for speaker, text in st.session_state["conversation"]:
                st.text(f"{speaker}: {text}")
                
if __name__ == "__main__":
    main()
