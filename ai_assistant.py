import json
import os
import tomllib
from pathlib import Path
from tomllib import TOMLDecodeError

import streamlit as st
from openai import APIError, AuthenticationError, OpenAI, RateLimitError
from streamlit.errors import StreamlitSecretNotFoundError


class AIChatAssistant:
    def __init__(self, store_service) -> None:
        self.store_service = store_service
        self.log_path = Path("json_data") / "ai_logs.json"

    def api_key(self) -> str | None:
        if os.getenv("OPENAI_API_KEY"):
            return os.getenv("OPENAI_API_KEY")
        try:
            key = st.secrets.get("OPENAI_API_KEY")
            if key:
                return key
        except (StreamlitSecretNotFoundError, TOMLDecodeError):
            pass

        secrets_path = Path(".streamlit") / "secrets.toml"
        if secrets_path.exists():
            try:
                with open(secrets_path, "rb") as f:
                    return tomllib.load(f).get("OPENAI_API_KEY")
            except TOMLDecodeError:
                return self.read_unquoted_secret(secrets_path, "OPENAI_API_KEY")
        return None

    def read_unquoted_secret(self, secrets_path: Path, key_name: str) -> str | None:
        for line in secrets_path.read_text().splitlines():
            name, separator, value = line.partition("=")
            if separator and name.strip() == key_name:
                return value.strip().strip('"').strip("'")
        return None

    def client(self):
        key = self.api_key()
        if not key:
            return None
        return OpenAI(api_key=key)

    def load_logs(self) -> list:
        if self.log_path.exists():
            with open(self.log_path, "r") as f:
                return json.load(f)
        return []

    def save_logs(self, logs: list):
        self.log_path.parent.mkdir(exist_ok=True)
        with open(self.log_path, "w") as f:
            json.dump(logs, f, indent=2)

    def default_messages(self) -> list:
        logs = self.load_logs()
        if logs:
            return logs
        return [
            {
                "role": "assistant",
                "content": "Hi! I can help with orders, inventory, and store questions.",
            }
        ]

    def build_store_context(self, user_role: str, user_email: str) -> str:
        inventory = self.store_service.get_inventory()
        orders = self.store_service.get_orders()
        if user_role == "user":
            orders = self.store_service.filter_orders_by_user(user_email)

        inventory_summary = ", ".join(
            f"{item.name}: ${item.price:.2f}, {item.stock} in stock" for item in inventory[:10]
        )
        order_summary = ", ".join(
            f"{order.item_name} x{order.quantity} ({order.status})" for order in orders[-8:]
        ) or "No orders yet"

        return (
            f"User role: {user_role}. "
            f"Inventory: {inventory_summary}. "
            f"Relevant orders: {order_summary}."
        )

    def build_prompt(self, user_role: str, user_email: str) -> str:
        context = self.build_store_context(user_role, user_email)
        return (
            "You are an AI assistant inside a grocery store ordering app. "
            "Use the store context to answer questions about groceries, stock, orders, "
            "cancellations, and how to use the app. "
            "If the user asks about previous messages, use the chat history. "
            "Keep answers short and helpful. "
            f"Store context: {context}"
        )

    def get_ai_response(self, client: OpenAI, chat_history: list, user_role: str, user_email: str) -> str:
        messages = [
            {
                "role": "system",
                "content": self.build_prompt(user_role, user_email),
            }
        ]
        messages.extend(
            message
            for message in chat_history
            if message.get("role") in ["user", "assistant"] and message.get("content")
        )

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content

    def generate_response(self, chat_history: list, user_role: str, user_email: str) -> str:
        client = self.client()
        if not client:
            return (
                "OpenAI is not connected yet. Add OPENAI_API_KEY to your environment "
                "or to .streamlit/secrets.toml, then restart Streamlit."
            )

        try:
            answer = self.get_ai_response(client, chat_history, user_role, user_email)
        except RateLimitError as error:
            error_code = getattr(error, "code", None)
            if error_code == "insufficient_quota":
                answer = (
                    "Your OpenAI key is connected, but this account has no available API quota. "
                    "Check your OpenAI billing or project credits, then try again."
                )
            else:
                answer = "The OpenAI API rate limit was reached. Please wait a little and try again."
        except AuthenticationError:
            answer = "OpenAI rejected this API key. Check that the key is copied correctly in .streamlit/secrets.toml."
        except APIError:
            answer = "OpenAI had a temporary API problem. Please try again in a moment."

        self.save_logs(chat_history + [{"role": "assistant", "content": answer}])
        return answer
