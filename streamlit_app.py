import streamlit as st

# --- DEBUGGING SECRETS ---
with st.sidebar:
    st.write("### 🛠 Secrets Debugger")
    if "google_client_id" in st.secrets:
        st.success("✅ google_client_id found!")
    else:
        st.error("❌ google_client_id NOT found.")
        st.write("Keys currently in secrets:", list(st.secrets.keys()))

# Rest of your Firebase and App code follows...
