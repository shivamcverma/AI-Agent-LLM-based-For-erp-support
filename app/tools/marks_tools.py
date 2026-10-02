import os
import httpx


import httpx

from app.config.settings import settings


BASE_URL = settings.erp_chatbot_base_url


async def get_student_marks(
    school_id: int,
    student_id: int
):
    """
    Get exam marks/results for a specific student.
    """

    url = f"{BASE_URL}/marks"

    params = {
        "school_id": school_id,
        "student_id": student_id
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

async def get_student_subject_marks(
    school_id: int,
    student_id: int,
    exam_id: int
):
    """
    Get detailed subject-wise marks for a student in a specific exam.
    """

    url = f"{BASE_URL}/marks/subjects"

    params = {
        "school_id": school_id,
        "student_id": student_id,
        "exam_id": exam_id
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