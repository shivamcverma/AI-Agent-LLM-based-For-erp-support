import os
import httpx


import httpx

from app.config.settings import settings


BASE_URL = settings.erp_chatbot_base_url


async def get_staff_summary(school_id: int):
    """
    Get staff summary and designation-wise staff count
    for a specific school.
    """

    url = f"{BASE_URL}/staff"

    params = {
        "school_id": school_id
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                url,
                params=params,
                headers={"X-Chatbot-Key": settings.erp_chatbot_key, "Accept": "application/json"}
            )

            response.raise_for_status()

            return response.json()

    except httpx.HTTPStatusError as e:
        return {
            "status": "error",
            "message": f"ERP API returned status {e.response.status_code}"
        }

    except httpx.RequestError as e:
        return {
            "status": "error",
            "message": f"Unable to connect to ERP API: {str(e)}"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

async def get_staff_list(
    school_id: int
):
    """
    Get a list of all staff members and their designations.
    """

    url = f"{BASE_URL}/staff/list"

    params = {
        "school_id": school_id
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                url,
                params=params,
                headers={"X-Chatbot-Key": settings.erp_chatbot_key, "Accept": "application/json"}
            )

            response.raise_for_status()

            return response.json()

    except httpx.HTTPStatusError as e:
        return {
            "status": "error",
            "message": f"ERP API returned status {e.response.status_code}"
        }

    except httpx.RequestError as e:
        return {
            "status": "error",
            "message": f"Unable to connect to ERP API: {str(e)}"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }