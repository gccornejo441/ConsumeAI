import httpx
from pydantic import BaseModel
import logging
from typing import Optional
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_employees(name: str, url: httpx.URL | str, api_key: str):
    """Search for employees in NetSuite by name."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=url,
                params={"code": api_key, "name": name}
            )
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        print(f"NetSuite API Error: {e}")
        return {"data": []}


class PhoneCallRequest(BaseModel):
    q: str
    entityType: str
    startDate: Optional[str] = None
    endDate: Optional[str] = None

async def get_phone_call_history(phone_call_request: PhoneCallRequest, url: httpx.URL | str, api_key: str):
    """Fetch phone call messages from NetSuite API based on search criteria."""
    params = {
        "code": api_key,
        "q": phone_call_request.q,
        "entityType": phone_call_request.entityType,
        "startDate": phone_call_request.startDate,
        "endDate": phone_call_request.endDate,
    }

    try: 
        async with httpx.AsyncClient() as client:
            # Make the post request to the specified url
            response = await client.post(url, params=params)
            
            # ?
            response.raise_for_status()
            
            #  If the status code indicates an error (4xx or 5xx), 
            #  it raises an HTTPError exception. If the status code 
            #  is successful (2xx), it does nothing.
            data = response.json()
            return data
    except httpx.RequestError as e:
        logger.error(f"NetSuite API Error (Phone Call Search): {e}")
        return {"data": []}
    
def summarize_messages(msgs: list) -> str:
    """Takes a list of messages and returns a concise summary string."""

    summary_prompt = "Please summarize the following conversation concisely, capturing the key context:\n\n"
    for msg in msgs:
        summary_prompt += f"{msg['role']}: {msg['content']}\n"