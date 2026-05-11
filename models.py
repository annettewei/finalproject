class User:
    def __init__(self, username, password, role, name="", email=""):
        self.username = username
        self.password = password
        self.role = role
        self.name = name
        self.email = email or username

    def can_access_page(self, page):
        if page in ["Dashboard", "Assistant"]:
            return True
        if self.role == "employee":
            return page in ["Inventory", "Orders"]
        if self.role == "user":
            return page in ["Shop", "My Orders"]
        return False

    def to_dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "name": self.name,
            "password": self.password,
            "role": self.role,
        }


class InventoryItem:
    def __init__(self, item_id, name, price, stock, category="General"):
        self.id = int(item_id)
        self.name = name
        self.price = float(price)
        self.stock = int(stock)
        self.category = category

    def is_low_stock(self):
        return self.stock <= 5

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": round(self.price, 2),
            "stock": self.stock,
            "category": self.category,
        }


class Order:
    def __init__(self, order_id, item_id, item_name, quantity, status, total, user_email, timestamp):
        self.id = order_id
        self.item_id = int(item_id)
        self.item_name = item_name
        self.quantity = int(quantity)
        self.status = status
        self.total = float(total)
        self.user_email = user_email
        self.timestamp = timestamp

    def cancel(self):
        self.status = "cancelled"

    def to_dict(self):
        return {
            "id": self.id,
            "item_id": self.item_id,
            "item_name": self.item_name,
            "quantity": self.quantity,
            "status": self.status,
            "total": round(self.total, 2),
            "user_email": self.user_email,
            "timestamp": self.timestamp,
        }
