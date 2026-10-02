import httpx
import os


import httpx

from app.config.settings import settings


BASE_URL = settings.erp_chatbot_base_url


async def get_school_info(school_id: int):
    """
    Get information of a specific school.
    """

    url = f"{BASE_URL}/school-info"

    params = {
        "school_id": school_id
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                url,
                params=params
            )

            response.raise_for_status()

            return response.json()

    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"ERP API returned status {e.response.status_code}"
        }

    except httpx.RequestError as e:
        return {
            "success": False,
            "error": f"Unable to connect to ERP API: {str(e)}"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }