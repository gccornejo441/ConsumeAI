from dotenv import load_dotenv
import os

import httpx
import ollama
from fastapi import FastAPI, HTTPException, Query
from collections import defaultdict
from pydantic import BaseModel
import logging
import json

from services.employee_service import PhoneCallRequest, get_employees, get_phone_call_history
# from services.item_inventory_service import search_item_inventory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

MODEL_NAME = "qwen2.5-coder:1.5b"
NETSUITE_BASE_URL = os.getenv("NETSUITE_BASE_URL")
NETSUITE_PHONECALL_BASE_URL = os.getenv("NETSUITE_PHONECALL_BASE_URL")
NETSUITE_API_KEY = os.getenv("NETSUITE_API_KEY")
NETSUITE_ITEM_INVENTORY_URL = os.getenv("NETSUITE_ITEM_INVENTORY_URL")
MAX_HISTORY = 10
# When history exceeds this, summarize older messages.
SUMMARIZATION_THRESHOLD = 6
HISTORY_TO_KEEP = 2         # Keep the last 2 messages un-summarized.

chat_history = defaultdict(list)


class ChatRequest(BaseModel):
    prompt: str
    user_id: str


def summarize_messages(messages: list) -> str:
    """
    Takes a list of messages and returns a concise summary string.
    """
    summary_prompt = "Please summarize the following conversation concisely, capturing the key context:\n\n"
    for msg in messages:
        summary_prompt += f"{msg['role']}: {msg['content']}\n"
    summary_prompt += "\nSummary:"

    # Call the model to generate a summary.
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": summary_prompt}]
    )
    return response['message']['content']


@app.post("/search-employee")
async def netsuite_chat(
    chat_request: ChatRequest,
    name: str = Query(..., description="Employee name to search")
):
    employees = await get_employees(name)

    if "data" not in employees or not employees["data"]:
        return {"response": f"No employees found with the name '{name}' in NetSuite."}

    # Create a system message based on employee search results.
    employee_list = employees["data"]
    employee_details = "\n".join(
        [f"- {emp.get('FullName', 'Unknown')} ({emp.get('Email', 'No email')})" for emp in employee_list]
    )
    system_message = (
        f"Here are the employees matching '{name}' in NetSuite:\n{employee_details}\n\n"
        f"Use this data to answer the user's request."
    )

    conv_key = f"search_employee_{chat_request.user_id}"

    # Initialize conversation with the system message if not already set.
    if not chat_history[conv_key] or chat_history[conv_key][0]["role"] != "system":
        chat_history[conv_key] = [
            {"role": "system", "content": system_message}]

    # Append the new user prompt.
    chat_history[conv_key].append(
        {"role": "user", "content": chat_request.prompt})

    # If conversation history exceeds the summarization threshold, summarize older messages.
    if len(chat_history[conv_key]) > SUMMARIZATION_THRESHOLD:
        # Extract older messages (everything except the last HISTORY_TO_KEEP messages).
        older_messages = chat_history[conv_key][:-HISTORY_TO_KEEP]
        summary = summarize_messages(older_messages)
        # Replace older messages with the summary.
        chat_history[conv_key] = [
            {"role": "system", "content": summary}] + chat_history[conv_key][-HISTORY_TO_KEEP:]

    # Trim conversation history to the last MAX_HISTORY messages.
    chat_history[conv_key] = chat_history[conv_key][-MAX_HISTORY:]
    messages = chat_history[conv_key]

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=messages
        )
        bot_reply = response['message']['content']

        # Append the assistant's reply to the conversation history.
        chat_history[conv_key].append(
            {"role": "assistant", "content": bot_reply})

        return {"response": bot_reply}
    except Exception as e:
        print(f"Ollama Chat Error: {e}")
        raise HTTPException(
            status_code=500, detail="Error communicating with the LLM model."
        )


@app.post("/search-phonecall")
async def netsuite_phonecall_chat(
    chat_request: ChatRequest,
    q: str = Query(..., description="Partial name to search (matches against customer or employee name)"),
    entityType: str = Query(
        "CUSTOMER", description="Entity type: CUSTOMER, EMPLOYEE, or ALL"),
    startDate: str = Query(
        None, description="Start date filter in format YYYY-MM-DD"),
    endDate: str = Query(
        None, description="End date filter in format YYYY-MM-DD")
):
    # Log search parameters
    logger.info(
        f"Phone call search requested: q={q}, entityType={entityType}, startDate={startDate}, endDate={endDate}"
    )

    # Create a PhoneCallRequest object from the query parameters
    phone_call_request = PhoneCallRequest(
        q=q,
        entityType=entityType,
        startDate=startDate,
        endDate=endDate
    )

    # Fetch phone call messages from NetSuite API using the proper arguments
    phone_call_data = await get_phone_call_history(
        phone_call_request,
        NETSUITE_PHONECALL_BASE_URL,
        NETSUITE_API_KEY
    )

    # Log the raw API response
    logger.info(
        f"NetSuite Phone Call API Response: {json.dumps(phone_call_data, indent=2)}")

    # Build a system message based on the phone call results
    if phone_call_data.get("data"):
        system_message = f"Phone call records retrieved from NetSuite for query '{q}':\n\n"
        for record in phone_call_data["data"]:
            system_message += (
                f"- **Title:** {record.get('title', 'No Title')}\n"
                f"  - **Assigned To:** {record.get('assignedtoname', 'Unknown')}\n"
                f"  - **Date Created:** {record.get('createddate', 'N/A')}\n"
                f"  - **Status:** {record.get('status', 'N/A')}\n"
                f"  - **Priority:** {record.get('priority', 'N/A')}\n"
                f"  - **Message:** {record.get('message', 'No message provided.')}\n\n"
            )
    else:
        system_message = f"No phone call records found for '{q}'."

    # Log the formatted system message
    logger.info(f"Formatted system message for LLM:\n{system_message}")

    # Define a unique conversation key
    conv_key = f"phonecall_{chat_request.user_id}"

    # Ensure conversation history starts with system context
    if not chat_history[conv_key] or chat_history[conv_key][0]["role"] != "system":
        chat_history[conv_key] = [
            {"role": "system", "content": system_message}]
    else:
        # Update the existing system message if necessary
        chat_history[conv_key][0]["content"] = system_message

    # Append the user’s query
    chat_history[conv_key].append(
        {"role": "user", "content": chat_request.prompt})

    # Summarize older messages if conversation history is long
    if len(chat_history[conv_key]) > SUMMARIZATION_THRESHOLD:
        older_messages = chat_history[conv_key][:-HISTORY_TO_KEEP]
        summary = summarize_messages(older_messages)
        chat_history[conv_key] = [
            {"role": "system", "content": summary}] + chat_history[conv_key][-HISTORY_TO_KEEP:]

    # Trim history to keep it within MAX_HISTORY
    chat_history[conv_key] = chat_history[conv_key][-MAX_HISTORY:]
    messages = chat_history[conv_key]

    # Log the full conversation history before sending it to the LLM
    logger.info(
        f"Conversation history sent to LLM:\n{json.dumps(messages, indent=2)}")

    try:
        # Get LLM response
        response = ollama.chat(
            model=MODEL_NAME,
            messages=messages
        )
        bot_reply = response['message']['content']

        # Log the LLM's response
        logger.info(f"LLM Response: {bot_reply}")

        # Save the assistant's reply in conversation history
        chat_history[conv_key].append(
            {"role": "assistant", "content": bot_reply})
        return {"response": bot_reply}

    except Exception as e:
        logger.error(f"Ollama Chat Error: {e}")
        raise HTTPException(
            status_code=500, detail="Error communicating with the LLM model.")


@app.post("/search-item-inventory")
async def netsuite_item_inventory_search(
    chat_request: ChatRequest,
    sku: str = Query("", description="SKU filter. Filters on the item ID."),
    location: str = Query(
        "", description="Location filter. Filters on the location name."),
    description: str = Query(
        "", description="Description filter. Filters on the item description."),
    classification: str = Query(
        "", description="Classification filter. Filters on the classification name."),
    sub_classification: str = Query(
        "", alias="subClassification", description="Subclassification filter. Filters on the Subclassification name.")
):
    logger.info(
        f"Item inventory search requested with parameters: sku='{sku}', location='{location}', "
        f"description='{description}', classification='{classification}', subClassification='{sub_classification}'"
    )

    sku = sku.strip()
    location = location.strip()
    description = description.strip()
    classification = classification.strip()
    sub_classification = sub_classification.strip()

    try:
        search_results = await search_item_inventory(sku, location, description, classification, sub_classification)
    except Exception as e:
        logger.error(f"Error occurred while searching for item inventory: {e}")
        raise HTTPException(
            status_code=500, detail="An error occurred while processing your request."
        )

    if search_results and len(search_results) > 0:
        item_details = "\n".join(
            [
                f"- SKU: {item.get('sku', 'N/A')}, Location: {item.get('location', 'N/A')}, Description: {item.get('description', 'N/A')}, Classification: {item.get('classification', 'N/A')}, Subclassification: {item.get('subClassification', 'N/A')}"
                for item in search_results
            ]
        )
        system_message = (
            f"Here are the item inventory details matching your search criteria:\n{item_details}\n\n"
            f"Use this data to answer the user's request."
        )
    else:
        system_message = "No item inventory records found matching the provided search criteria."

    conv_key = f"item_inventory_{chat_request.user_id}"

    if not chat_history[conv_key] or chat_history[conv_key][0]["role"] != "system":
        chat_history[conv_key] = [
            {"role": "system", "content": system_message}]
    else:
        chat_history[conv_key][0]["content"] = system_message

    chat_history[conv_key].append(
        {"role": "user", "content": chat_request.prompt})

    if len(chat_history[conv_key]) > SUMMARIZATION_THRESHOLD:
        older_messages = chat_history[conv_key][:-HISTORY_TO_KEEP]
        summary = summarize_messages(older_messages)
        chat_history[conv_key] = [
            {"role": "system", "content": summary}] + chat_history[conv_key][-HISTORY_TO_KEEP:]

    chat_history[conv_key] = chat_history[conv_key][-MAX_HISTORY:]
    messages = chat_history[conv_key]

    logger.info(
        f"Conversation history for item inventory search:\n{json.dumps(messages, indent=2)}")

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=messages
        )
        bot_reply = response['message']['content']

        chat_history[conv_key].append(
            {"role": "assistant", "content": bot_reply})
        return {"response": bot_reply}
    except Exception as e:
        logger.error(f"Ollama Chat Error: {e}")
        raise HTTPException(
            status_code=500, detail="Error communicating with the LLM model."
        )


@app.post("/short-item-inventory-search")
async def netsuite_short_item_inventory_search(
    chat_request: ChatRequest,
    sku: str = Query("", description="SKU filter. Filters on the item ID."),
    location: str = Query("", description="Location filter. Filters on the location name."),
    description: str = Query("", description="Description filter. Filters on the item description."),
    classification: str = Query("", description="Classification filter. Filters on the classification name."),
    sub_classification: str = Query("", alias="subClassification", description="Subclassification filter. Filters on the Subclassification name.")
):
    logger.info(f"User chat request: {chat_request.prompt}")
    logger.info(
        f"Item inventory search requested with parameters: sku='{sku}', location='{location}', "
        f"description='{description}', classification='{classification}', subClassification='{sub_classification}'"
    )

    sku = sku.strip()
    location = location.strip()
    description = description.strip()
    classification = classification.strip()
    sub_classification = sub_classification.strip()

    try:
        item_results = await netsuite_item_inventory_service(sku, location, description, classification, sub_classification)
    except Exception as e:
        logger.error(f"Error occurred while searching for item inventory: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")

    if item_results and len(item_results) > 0:
        item_details = "\n".join(
            [
                f"- SKU: {item.get('ItemId', 'N/A')}, Description: {item.get('Description', 'N/A')}, "
                f"Available: {item.get('QuantityAvailable', 'N/A')}, Location: {item.get('LocationName', 'N/A')}, "
                f"Classification: {item.get('Classification', 'N/A')}, Subclassification: {item.get('SubClassification', 'N/A')}"
                for item in item_results
            ]
        )
        system_message = (
            f"NetSuite returned the following inventory items:\n{item_details}\n\n"
            "Use the above data to answer the user's query in a conversational tone."
        )
    else:
        system_message = "No inventory records found matching your search criteria."

    conv_key = f"item_inventory_{chat_request.user_id}"

    if not chat_history[conv_key] or chat_history[conv_key][0]["role"] != "system":
        chat_history[conv_key] = [{"role": "system", "content": system_message}]
    else:
        chat_history[conv_key][0]["content"] = system_message

    chat_history[conv_key].append({"role": "user", "content": chat_request.prompt})

    if len(chat_history[conv_key]) > SUMMARIZATION_THRESHOLD:
        older_messages = chat_history[conv_key][:-HISTORY_TO_KEEP]
        summary = summarize_messages(older_messages)
        chat_history[conv_key] = [{"role": "system", "content": summary}] + chat_history[conv_key][-HISTORY_TO_KEEP:]

    chat_history[conv_key] = chat_history[conv_key][-MAX_HISTORY:]
    messages = chat_history[conv_key]

    logger.info(f"Conversation history for item inventory search:\n{json.dumps(messages, indent=2)}")

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=messages
        )
        bot_reply = response['message']['content']
        chat_history[conv_key].append({"role": "assistant", "content": bot_reply})
        return {"response": bot_reply}
    except Exception as e:
        logger.error(f"Ollama Chat Error: {e}")
        raise HTTPException(status_code=500, detail="Error communicating with the LLM model.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

async def netsuite_item_inventory_service(
    sku="900002963",
    location=None,
    description=None,
    classification=None,
    sub_classification=None
):
    """
    Calls the NetSuite Item Inventory API using provided search filters.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                NETSUITE_ITEM_INVENTORY_URL,
                params={
                    "sku": sku,
                    "location": location,
                    "description": description,
                    "classification": classification,
                    "subClassification": sub_classification
                },
                headers={
                    "x-functions-key": NETSUITE_API_KEY
                }
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error fetching item inventory: {response.text}"
                )
            logger.info(f"Item inventory search successful: {response.status_code}")
            logger.info(f"NetSuite Item Inventory API Response: {json.dumps(response.json(), indent=2)}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error while calling NetSuite: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Error fetching item inventory: {e.response.text}"
        )
    except Exception as e:
        logger.error(f"Unexpected error while searching item inventory: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your request."
        )
