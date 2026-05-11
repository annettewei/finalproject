import os

from openai import OpenAI


class AIChatAssistant:
    def __init__(self, store_service) -> None:
        self.store_service = store_service
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None

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

    def generate_response(self, question: str, user_role: str, user_email: str) -> str:
        if not self.client:
            return "OpenAI is not connected yet. Add your OPENAI_API_KEY, then restart Streamlit."

        context = self.build_store_context(user_role, user_email)
        response = self.client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant inside a grocery store ordering app. "
                        "Answer using the current store context, keep responses short, "
                        "and help users understand inventory, orders, and next actions."
                    ),
                },
                {"role": "user", "content": f"{context}\n\nQuestion: {question}"},
            ],
        )
        return response.output_text
