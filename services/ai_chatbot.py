import json
from pathlib import Path

from openai import APIError, AuthenticationError, OpenAI, RateLimitError


class OrderDataStore:
    def __init__(self, filepath: str) -> None:
        self.filepath = Path(filepath)

    def get_orders_as_string(self) -> str:
        if not self.filepath.exists():
            return "[]"
        with open(self.filepath, "r") as f:
            data = json.load(f)
        return json.dumps(data, indent=2)


class ChatLoggerStore:
    def __init__(self, filepath: str) -> None:
        self.filepath = Path(filepath)

    def load_logs(self) -> list:
        if self.filepath.exists():
            with open(self.filepath, "r") as f:
                return json.load(f)
        return []

    def save_logs(self, logs: list) -> None:
        self.filepath.parent.mkdir(exist_ok=True)
        with open(self.filepath, "w") as f:
            json.dump(logs, f, indent=2)


class OrderAssistantBot:
    def __init__(self, client: OpenAI | None, context_data: str) -> None:
        self.client = client
        self.context_data = context_data
        self.orders = json.loads(context_data)

    def build_ai_prompt(self) -> str:
        return (
            "You are a helpful grocery store order assistant.\n"
            "Answer user questions based ONLY on the order data provided below.\n"
            "If the answer is not in the order data, say you do not have enough information.\n"
            "Keep answers short and clear.\n\n"
            f"ORDER DATA:\n{self.context_data}"
        )

    def get_ai_response(self, chat_history: list) -> str:
        if self.client is None:
            return self.fallback_response(self.latest_user_question(chat_history))

        ai_prompt_message = [{"role": "system", "content": self.build_ai_prompt()}]
        visible_messages = [
            message
            for message in chat_history
            if message.get("role") in ["user", "assistant"] and message.get("content")
        ]

        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=ai_prompt_message + visible_messages,
                temperature=0.2,
            )
            return response.choices[0].message.content
        except RateLimitError as error:
            error_code = getattr(error, "code", None)
            if error_code == "insufficient_quota":
                return self.fallback_response(self.latest_user_question(chat_history))
            return self.fallback_response(self.latest_user_question(chat_history))
        except AuthenticationError:
            return self.fallback_response(self.latest_user_question(chat_history))
        except APIError:
            return self.fallback_response(self.latest_user_question(chat_history))

    def latest_user_question(self, chat_history: list) -> str:
        for message in reversed(chat_history):
            if message.get("role") == "user":
                return message.get("content", "")
        return ""

    def fallback_response(self, question: str) -> str:
        question = question.lower()
        orders = self.orders

        if not orders:
            return "I do not have any order data to answer from."

        if "cancel" in question or "cancelled" in question:
            cancelled_orders = [order for order in orders if order.get("status") == "cancelled"]
            return f"There are {len(cancelled_orders)} cancelled orders."

        if "placed" in question or "active" in question:
            placed_orders = [order for order in orders if order.get("status") == "placed"]
            return f"There are {len(placed_orders)} active placed orders."

        if "how many" in question or "total orders" in question or "number of orders" in question:
            return f"There are {len(orders)} total orders in the order data."

        if "most" in question or "highest" in question or "expensive" in question:
            highest_order = max(orders, key=lambda order: float(order.get("total", 0)))
            return (
                "The highest total order is "
                f"{highest_order.get('item_name', 'Unknown Item')} for ${float(highest_order.get('total', 0)):.2f}."
            )

        if "revenue" in question or "sales" in question or "money" in question:
            total = sum(float(order.get("total", 0)) for order in orders if order.get("status") != "cancelled")
            return f"Total non-cancelled order revenue is ${total:.2f}."

        if "items" in question or "products" in question or "ordered" in question:
            item_names = sorted({order.get("item_name", "Unknown Item") for order in orders})
            return "The ordered items are " + ", ".join(item_names) + "."

        return (
            "I can answer basic questions about total orders, active orders, "
            "cancelled orders, highest order, revenue, and ordered items."
        )
