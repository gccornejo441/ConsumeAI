

import logging
import httpx
from main import NETSUITE_API_KEY, NETSUITE_ITEM_INVENTORY_URL

logger = logging.getLogger(__name__)

async def search_item_inventory(sku: str, location: str, description: str, classification: str, sub_classification: str):
    params = {
        "sku": sku,
        "location": location,
        "description": description,
        "classification": classification,
        "subClassification": sub_classification,
    }

    headers = {
        "x-functions-key": NETSUITE_API_KEY
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(NETSUITE_ITEM_INVENTORY_URL, params=params, headers=headers)
            response.raise_for_status()
            return response.json() 
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error while calling NetSuite: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while searching item inventory: {e}")
            raise
