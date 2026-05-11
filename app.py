from pathlib import Path

import streamlit as st

from ai_assistant import AIChatAssistant
from data.grocery_store import GroceryStore
from services.grocery_manager import GroceryManager
from ui.grocery_dashboard import GroceryDashboard


st.set_page_config(
    page_title="finalproject",
    page_icon="apple",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def create_app():
    store = GroceryStore(Path("json_data"))
    manager = GroceryManager(store)
    assistant = AIChatAssistant(manager)
    return GroceryDashboard(manager, assistant)


dashboard = create_app()
dashboard.main()
