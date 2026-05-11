import json
from pathlib import Path
from typing import List, Dict


class GroceryStore:
    def __init__(self, data_path: Path) -> None:
        self.data_path = data_path
        self.data_path.mkdir(exist_ok=True)

    def file_path(self, filename: str) -> Path:
        return self.data_path / filename

    def load(self, filename: str) -> List[Dict]:
        path = self.file_path(filename)
        if path.exists():
            with open(path, "r") as f:
                return json.load(f)
        else:
            return []

    def save(self, filename: str, records: List[Dict]):
        path = self.file_path(filename)
        with open(path, "w") as f:
            json.dump(records, f, indent=2)

    def load_users(self) -> List[Dict]:
        return self.load("users.json")

    def save_users(self, users: List[Dict]):
        self.save("users.json", users)

    def load_inventory(self) -> List[Dict]:
        return self.load("inventory.json")

    def save_inventory(self, inventory: List[Dict]):
        self.save("inventory.json", inventory)

    def load_orders(self) -> List[Dict]:
        return self.load("order.json")

    def save_orders(self, orders: List[Dict]):
        self.save("order.json", orders)
