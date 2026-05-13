# finalproject

A Streamlit grocery ordering and inventory app with role-based dashboards, JSON storage, CRUD features, and an OpenAI-powered assistant.

## How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

To enable the AI assistant, create a `.env` file in the project folder:

```env
OPENAI_API_KEY="your-api-key-here"
```

Then restart Streamlit. The `.env` file is ignored by Git so the API key stays private.

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
- `services/ai_chatbot.py`: OOD chatbot classes for order data, chat logging, hidden prompts, and OpenAI responses.
- `ui/grocery_dashboard.py`: Streamlit UI layer, layout, forms, routing, and display logic.
- `models.py`: object-oriented models for users, inventory items, and orders.
- `ai_assistant.py`: small compatibility import file for the chatbot classes.
- `json_data/`: sample JSON data for users, inventory, orders, and saved chat logs.

## Final Project Improvements

- Real login validation and registration persistence.
- Sidebar navigation with role-based pages.
- Customer dashboard, shopping page, order history, and cancellation workflow.
- Employee dashboard, inventory CRUD tools, order review, and order cancellation workflow.
- Cleaner separation between UI, data, service, model, and AI assistant code.
- Functions, methods, and classes used throughout the app.
- Sample data and test accounts shown directly on the login page.
- AI assistant OOD structure with separate order data, chat logging, and bot service classes.
