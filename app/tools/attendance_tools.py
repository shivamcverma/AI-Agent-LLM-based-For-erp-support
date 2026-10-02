import os
import httpx


import httpx

from app.config.settings import settings


BASE_URL = settings.erp_chatbot_base_url


async def get_attendance_summary(
    school_id: int,
    date: str | None = None,
    student_id: int | None = None,
    class_id: int | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
):
    """
    Get attendance information for a school, class, or student.
    """

    url = f"{BASE_URL}/attendance"

    params = {
        "school_id": school_id
    }

    if date is not None:
        params["date"] = date

    if student_id is not None:
        params["student_id"] = student_id

    if class_id is not None:
        params["class_id"] = class_id

    if from_date is not None:
        params["from_date"] = from_date

    if to_date is not None:
        params["to_date"] = to_date

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