import streamlit as st

from ai_assistant import AIChatAssistant
from services.grocery_manager import GroceryManager


class GroceryDashboard:
    def __init__(self, manager: GroceryManager, assistant: AIChatAssistant) -> None:
        self.manager = manager
        self.assistant = assistant

    def main(self):
        self.setup_session()

        if not st.session_state["logged_in"]:
            self.show_login_page()
            return

        user = self.current_user()
        if user is None:
            self.logout()
            return

        self.show_sidebar(user)

        if not user.can_access_page(st.session_state["page"]):
            st.error("You do not have access to that page.")
            return

        if st.session_state["page"] == "Dashboard":
            self.show_dashboard(user)
        elif st.session_state["page"] == "Shop":
            self.show_shop(user)
        elif st.session_state["page"] == "My Orders":
            self.show_my_orders(user)
        elif st.session_state["page"] == "Inventory":
            self.show_inventory_manager()
        elif st.session_state["page"] == "Orders":
            self.show_order_manager()
        elif st.session_state["page"] == "Assistant":
            self.show_assistant(user)

    def setup_session(self):
        if "logged_in" not in st.session_state:
            st.session_state["logged_in"] = False
        if "current_user" not in st.session_state:
            st.session_state["current_user"] = None
        if "page" not in st.session_state:
            st.session_state["page"] = "Login"
        if "messages" not in st.session_state:
            st.session_state["messages"] = self.assistant.default_messages()

    def current_user(self):
        user_data = st.session_state.get("current_user")
        if user_data:
            return self.manager.find_user_by_username(user_data["username"])
        return None

    def login(self, username, password):
        user = self.manager.validate_login(username, password)
        if user:
            st.session_state["logged_in"] = True
            st.session_state["current_user"] = user.to_dict()
            st.session_state["page"] = "Dashboard"
            st.rerun()
        else:
            st.error("Login failed. Check your email and password.")

    def logout(self):
        st.session_state["logged_in"] = False
        st.session_state["current_user"] = None
        st.session_state["page"] = "Login"
        st.session_state["messages"] = [
            {"role": "assistant", "content": "Hi! I can help with orders, inventory, and store questions."}
        ]
        st.rerun()

    def money(self, value):
        return f"${value:,.2f}"

    def orders_table(self, orders):
        table = []
        for order in orders:
            table.append(
                {
                    "Order": order.id[:8],
                    "Customer": order.user_email,
                    "Item": order.item_name,
                    "Qty": order.quantity,
                    "Status": order.status.title(),
                    "Total": self.money(order.total),
                    "Date": order.timestamp,
                }
            )
        return table

    def inventory_table(self, inventory):
        table = []
        for item in inventory:
            status = "Low stock" if item.is_low_stock() else "In stock"
            table.append(
                {
                    "ID": item.id,
                    "Name": item.name,
                    "Category": item.category,
                    "Price": self.money(item.price),
                    "Stock": item.stock,
                    "Status": status,
                }
            )
        return table

    def show_login_page(self):
        st.markdown("# 🍎 New London Grocery Store")
        st.caption("By Annette Wei and Mythili Satheesh")

        login_col, register_col, accounts_col = st.columns([1.1, 1.1, 0.9])

        with login_col:
            with st.container(border=True):
                st.subheader("Login")
                with st.form("login_form"):
                    username = st.text_input("Email", value="student@test.com")
                    password = st.text_input("Password", type="password", value="student123")
                    submitted = st.form_submit_button("Login", type="primary", use_container_width=True)
                if submitted:
                    self.login(username, password)

        with register_col:
            with st.container(border=True):
                st.subheader("Register")
                with st.form("register_form", clear_on_submit=True):
                    email = st.text_input("Email", key="register_email")
                    name = st.text_input("Full name")
                    password = st.text_input("Password", type="password", key="register_password")
                    role = st.selectbox("Role", ["user", "employee"])
                    created = st.form_submit_button("Create Account", use_container_width=True)
                if created:
                    success, message = self.manager.register_user(email, name, password, role)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

        with accounts_col:
            with st.container(border=True):
                st.subheader("Test Accounts")
                st.markdown("**Customer**")
                st.code("Email: student@test.com\nPassword: student123")
                st.markdown("**Employee**")
                st.code("Email: employee@test.com\nPassword: employee123")

    def show_sidebar(self, user):
        with st.sidebar:
            st.title("New London Grocery Store")
            st.caption(f"{user.name or user.username} | {user.role.title()}")

            pages = ["Dashboard", "Assistant"]
            if user.role == "user":
                pages.extend(["Shop", "My Orders"])
            elif user.role == "employee":
                pages.extend(["Inventory", "Orders"])

            page_index = 0
            if st.session_state["page"] in pages:
                page_index = pages.index(st.session_state["page"])

            st.session_state["page"] = st.radio("Navigation", pages, index=page_index)
            st.divider()

            if st.button("Log out", use_container_width=True):
                self.logout()

    def show_dashboard(self, user):
        st.markdown("# Dashboard")
        summary = self.manager.dashboard_summary()
        my_orders = self.manager.filter_orders_by_user(user.email)

        if user.role == "employee":
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Inventory Items", summary["inventory_count"])
            col2.metric("Orders", summary["order_count"])
            col3.metric("Low Stock", summary["low_stock_count"])
            col4.metric("Revenue", self.money(summary["revenue"]))

            st.divider()
            left, right = st.columns([1.2, 1])

            with left:
                st.subheader("Recent Orders")
                st.dataframe(self.orders_table(self.manager.get_orders()[-8:]), use_container_width=True, hide_index=True)

            with right:
                st.subheader("Low Stock Items")
                low_stock = []
                for item in self.manager.get_inventory():
                    if item.is_low_stock():
                        low_stock.append(item)
                st.dataframe(self.inventory_table(low_stock), use_container_width=True, hide_index=True)
        else:
            active_orders = []
            spending = 0
            for order in my_orders:
                if order.status == "placed":
                    active_orders.append(order)
                if order.status != "cancelled":
                    spending += order.total

            col1, col2, col3 = st.columns(3)
            col1.metric("My Orders", len(my_orders))
            col2.metric("Active Orders", len(active_orders))
            col3.metric("My Spending", self.money(spending))

            st.divider()
            st.subheader("Available Groceries")
            st.dataframe(self.inventory_table(self.manager.available_inventory()), use_container_width=True, hide_index=True)

    def show_shop(self, user):
        st.markdown("# Shop")
        inventory = self.manager.available_inventory()

        if not inventory:
            st.warning("No inventory is available right now.")
            return

        left, right = st.columns([1, 1])
        with left:
            st.subheader("Place an Order")
            with st.form("create_order_form"):
                selected_item = st.selectbox(
                    "Item",
                    inventory,
                    format_func=lambda item: f"{item.name} - {self.money(item.price)} ({item.stock} available)",
                )
                quantity = st.number_input("Quantity", min_value=1, max_value=max(1, selected_item.stock), step=1)
                submitted = st.form_submit_button("Create Order", type="primary", use_container_width=True)

            if submitted:
                success, message = self.manager.create_order(user.email, selected_item.id, quantity)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

        with right:
            st.subheader("Inventory")
            st.dataframe(self.inventory_table(inventory), use_container_width=True, hide_index=True)

    def show_my_orders(self, user):
        st.markdown("# My Orders")
        orders = self.manager.filter_orders_by_user(user.email)
        active_orders = []

        for order in orders:
            if order.status == "placed":
                active_orders.append(order)

        history_tab, cancel_tab = st.tabs(["Order History", "Cancel Order"])

        with history_tab:
            if orders:
                st.dataframe(self.orders_table(orders), use_container_width=True, hide_index=True)
            else:
                st.info("You do not have orders yet.")

        with cancel_tab:
            if not active_orders:
                st.info("No active orders to cancel.")
                return

            selected_order = st.selectbox(
                "Select an active order",
                active_orders,
                format_func=lambda order: f"{order.item_name} x{order.quantity} | {self.money(order.total)} | {order.timestamp}",
            )

            if st.button("Cancel Selected Order", type="primary"):
                success, message = self.manager.cancel_order(selected_order.id, user.email)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    def show_inventory_manager(self):
        st.markdown("# Inventory")
        items = self.manager.get_inventory()
        inventory_tab, add_tab, edit_tab = st.tabs(["Current Inventory", "Add Item", "Edit Item"])

        with inventory_tab:
            st.dataframe(self.inventory_table(items), use_container_width=True, hide_index=True)

        with add_tab:
            with st.form("add_inventory_form", clear_on_submit=True):
                name = st.text_input("Item name")
                category = st.text_input("Category", value="General")
                price = st.number_input("Price", min_value=0.0, step=0.25)
                stock = st.number_input("Stock", min_value=0, step=1)
                submitted = st.form_submit_button("Add Item", type="primary")

            if submitted:
                success, message = self.manager.add_inventory_item(name, price, stock, category)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

        with edit_tab:
            if not items:
                st.info("No items to edit.")
                return

            selected_item = st.selectbox("Choose item", items, format_func=lambda item: item.name)

            with st.form("edit_inventory_form"):
                name = st.text_input("Item name", value=selected_item.name)
                category = st.text_input("Category", value=selected_item.category)
                price = st.number_input("Price", min_value=0.0, value=float(selected_item.price), step=0.25)
                stock = st.number_input("Stock", min_value=0, value=int(selected_item.stock), step=1)
                submitted = st.form_submit_button("Save Changes", type="primary")

            if submitted:
                success, message = self.manager.update_inventory_item(
                    selected_item.id, name, price, stock, category
                )
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    def show_order_manager(self):
        st.markdown("# Orders")
        orders = self.manager.get_orders()

        if not orders:
            st.info("No orders have been placed yet.")
            return

        st.dataframe(self.orders_table(orders), use_container_width=True, hide_index=True)
        active_orders = []

        for order in orders:
            if order.status == "placed":
                active_orders.append(order)

        with st.expander("Cancel an active order"):
            if active_orders:
                selected_order = st.selectbox(
                    "Order",
                    active_orders,
                    format_func=lambda order: f"{order.user_email} | {order.item_name} x{order.quantity}",
                )
                if st.button("Cancel Order"):
                    success, message = self.manager.cancel_order(selected_order.id)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.info("There are no active orders.")

    def show_assistant(self, user):
        st.markdown("# AI Assistant")
        st.caption("Ask about grocery availability, orders, restocking, or how to use the app.")

        for message in st.session_state["messages"]:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        prompt = st.chat_input("Ask the store assistant...")
        if prompt:
            st.session_state["messages"].append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    answer = self.assistant.generate_response(st.session_state["messages"], user.role, user.email)
                    st.write(answer)

            st.session_state["messages"].append({"role": "assistant", "content": answer})

        if st.button("Clear Chat"):
            st.session_state["messages"] = [
                {"role": "assistant", "content": "Hi! I can help with orders, inventory, and store questions."}
            ]
            self.assistant.save_logs(st.session_state["messages"])
            st.rerun()
