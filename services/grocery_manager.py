from datetime import datetime
from typing import List, Dict, Optional
import uuid

from data.grocery_store import GroceryStore
from models import InventoryItem, Order, User


class GroceryManager:
    def __init__(self, store: GroceryStore) -> None:
        self.store = store

    def get_users(self) -> List[User]:
        users = []
        for user in self.store.load_users():
            users.append(
                User(
                    user.get("username", ""),
                    user.get("password", ""),
                    user.get("role", "user"),
                    user.get("name", ""),
                    user.get("email", user.get("username", "")),
                )
            )
        return users

    def find_user_by_username(self, username: str) -> Optional[User]:
        username = username.strip().lower()
        for user in self.get_users():
            if user.username.lower() == username or user.email.lower() == username:
                return user
        return None

    def validate_login(self, username: str, password: str) -> Optional[User]:
        user = self.find_user_by_username(username)
        if user and user.password == password:
            return user
        return None

    def register_user(self, username: str, name: str, password: str, role: str):
        username = username.strip().lower()
        name = name.strip()

        if not username or not name or not password:
            return False, "Please complete every registration field."
        if "@" not in username:
            return False, "Please use an email address for the username."
        if len(password) < 3:
            return False, "Password must be at least 3 characters."
        if self.find_user_by_username(username):
            return False, "An account with that email already exists."

        users = self.get_users()
        new_user = User(username, password, role, name, username)
        users.append(new_user)
        self.store.save_users([user.to_dict() for user in users])
        return True, "Account created. You can log in now."

    def get_inventory(self) -> List[InventoryItem]:
        inventory = []
        for item in self.store.load_inventory():
            inventory.append(
                InventoryItem(
                    item["id"],
                    item["name"],
                    item["price"],
                    item["stock"],
                    item.get("category", "General"),
                )
            )
        return inventory

    def save_inventory(self, inventory: List[InventoryItem]):
        self.store.save_inventory([item.to_dict() for item in inventory])

    def get_orders(self) -> List[Order]:
        orders = []
        for order in self.store.load_orders():
            orders.append(
                Order(
                    order["id"],
                    order["item_id"],
                    order.get("item_name", "Unknown Item"),
                    order["quantity"],
                    order.get("status", "placed"),
                    order["total"],
                    order.get("user_email", "student@test.com"),
                    order.get("timestamp", ""),
                )
            )
        return orders

    def save_orders(self, orders: List[Order]):
        self.store.save_orders([order.to_dict() for order in orders])

    def available_inventory(self) -> List[InventoryItem]:
        return [item for item in self.get_inventory() if item.stock > 0]

    def filter_orders_by_user(self, user_email: str) -> List[Order]:
        return [order for order in self.get_orders() if order.user_email == user_email]

    def create_order(self, user_email: str, item_id: int, quantity: int):
        inventory = self.get_inventory()
        orders = self.get_orders()
        selected_item = None

        for item in inventory:
            if item.id == item_id:
                selected_item = item

        if selected_item is None:
            return False, "That item could not be found."
        if quantity < 1:
            return False, "Quantity must be at least 1."
        if selected_item.stock < quantity:
            return False, f"Only {selected_item.stock} {selected_item.name} available."

        selected_item.stock -= quantity
        new_order = Order(
            str(uuid.uuid4()),
            selected_item.id,
            selected_item.name,
            quantity,
            "placed",
            selected_item.price * quantity,
            user_email,
            datetime.now().strftime("%Y-%m-%d %H:%M"),
        )
        orders.append(new_order)

        self.save_inventory(inventory)
        self.save_orders(orders)
        return True, f"Order placed for {quantity} {selected_item.name}."

    def cancel_order(self, order_id: str, user_email=None):
        orders = self.get_orders()
        inventory = self.get_inventory()
        selected_order = None

        for order in orders:
            if order.id == order_id:
                selected_order = order

        if selected_order is None:
            return False, "Order not found."
        if user_email and selected_order.user_email != user_email:
            return False, "You can only cancel your own orders."
        if selected_order.status == "cancelled":
            return False, "That order is already cancelled."

        selected_order.cancel()
        for item in inventory:
            if item.id == selected_order.item_id:
                item.stock += selected_order.quantity

        self.save_orders(orders)
        self.save_inventory(inventory)
        return True, "Order cancelled and inventory restored."

    def add_inventory_item(self, name: str, price: float, stock: int, category: str):
        if not name.strip() or price < 0 or stock < 0:
            return False, "Name, price, and stock must be valid."

        inventory = self.get_inventory()
        next_id = 1
        if inventory:
            next_id = max([item.id for item in inventory]) + 1

        new_item = InventoryItem(next_id, name.strip(), price, stock, category.strip() or "General")
        inventory.append(new_item)
        self.save_inventory(inventory)
        return True, "Inventory item added."

    def update_inventory_item(self, item_id: int, name: str, price: float, stock: int, category: str):
        inventory = self.get_inventory()
        selected_item = None

        for item in inventory:
            if item.id == item_id:
                selected_item = item

        if selected_item is None:
            return False, "Item not found."
        if not name.strip() or price < 0 or stock < 0:
            return False, "Name, price, and stock must be valid."

        selected_item.name = name.strip()
        selected_item.price = price
        selected_item.stock = stock
        selected_item.category = category.strip() or "General"
        self.save_inventory(inventory)
        return True, "Inventory item updated."

    def dashboard_summary(self) -> Dict:
        inventory = self.get_inventory()
        orders = self.get_orders()
        low_stock = []
        revenue = 0

        for item in inventory:
            if item.is_low_stock():
                low_stock.append(item)

        for order in orders:
            if order.status != "cancelled":
                revenue += order.total

        return {
            "inventory_count": len(inventory),
            "order_count": len(orders),
            "low_stock_count": len(low_stock),
            "revenue": revenue,
        }
