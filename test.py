from fastapi import Query
from main import ChatRequest


def get_employees():
    return {"data": [
        {"FullName": "Alice", "Email": "alice@example.com"},
        {"FullName": "Bob", "Email": "bob@example.com"},
        {"FullName": "Charlie", "Email": "charlie@example.com"},
    ]}


def get_groceries():
    return {
        "fruits": [
            {"id": 1,
             "name": "apple", "price": 0.5},
            {
                "id": 2,
                "name": "banana", "price": 0.3
            }
        ]
    }


def netsuite_chat(chat_request: ChatRequest, name: str = Query(..., description="Employee name to search")):
    employees = get_employees()

    if "data" not in employees or not employees["data"]:
        return {"response": f"No employees found with the name '{name}' in NetSuite."}
    else:
        return {"response": f"Employees found with the name '{name}' in NetSuite."}


chat = ChatRequest(prompt="Hello", user_id="Alice")

print(netsuite_chat(chat, "Alice"))


def fruits():
    groceries = get_groceries()
    
    if "fruits" not in groceries:
        return {"response": "No fruits found"}