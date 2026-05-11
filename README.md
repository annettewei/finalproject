# finalproject

A Streamlit grocery ordering and inventory app with role-based dashboards, JSON storage, CRUD features, and an OpenAI-powered assistant.

## How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

To enable the AI assistant, set an OpenAI API key before starting Streamlit:

```bash
export OPENAI_API_KEY="your-api-key-here"
streamlit run app.py
```

You can also put the key in `.streamlit/secrets.toml`:

```toml
OPENAI_API_KEY = "your-api-key-here"
```

## Test Accounts

Customer:

```text
Email: student@test.com
Password: student123
```

Employee:

```text
Email: employee@test.com
Password: employee123
```

Both accounts include visible sample data so the dashboards, order history, inventory tables, and role-specific pages can be tested immediately.

## Project Structure

- `app.py`: small Streamlit starter file that creates the app objects.
- `data/grocery_store.py`: data layer for loading and saving JSON records.
- `services/grocery_manager.py`: service layer for authentication, registration, orders, inventory updates, and summaries.
- `ui/grocery_dashboard.py`: Streamlit UI layer, layout, forms, routing, and display logic.
- `models.py`: object-oriented models for users, inventory items, and orders.
- `ai_assistant.py`: OpenAI assistant class that answers questions using current inventory and order context.
- `json_data/`: sample JSON data for users, inventory, orders, and saved AI chat logs.

## Final Project Improvements

- Real login validation and registration persistence.
- Sidebar navigation with role-based pages.
- Customer dashboard, shopping page, order history, and cancellation workflow.
- Employee dashboard, inventory CRUD tools, order review, and order cancellation workflow.
- Cleaner separation between UI, data, service, model, and AI assistant code.
- Functions, methods, and classes used throughout the app.
- Sample data and test accounts shown directly on the login page.
- AI assistant prompt building, chat history, and JSON log saving based on the reference assistant structure.
