import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from data.grocery_store import GroceryStore
from services.ai_chatbot import ChatLoggerStore, OrderAssistantBot, OrderDataStore
from services.grocery_manager import GroceryManager
from ui.grocery_dashboard import GroceryDashboard


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key) if api_key else None

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
    order_store = OrderDataStore("json_data/order.json")
    chat_logger = ChatLoggerStore("json_data/chat_logs.json")
    assistant_bot = OrderAssistantBot(client=client, context_data=order_store.get_orders_as_string())
    return GroceryDashboard(manager, assistant_bot, chat_logger)


dashboard = create_app()
dashboard.main()
