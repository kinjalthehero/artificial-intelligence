import os
import streamlit as st


def get_config_value(name: str) -> str:
    secret_value = st.secrets.get(name)
    if secret_value:
        return str(secret_value)
    return os.getenv(name, "")


def consume_hosted_quota(max_requests: int) -> bool:
    used = st.session_state.get("hosted_requests_used", 0)
    if used >= max_requests:
        return False
    st.session_state["hosted_requests_used"] = used + 1
    return True
