import httpx

from app.config.settings import settings


BASE_URL = settings.erp_chatbot_base_url
CHATBOT_KEY = settings.erp_chatbot_key


async def get_fees_summary(school_id: int):

    url = f"{BASE_URL}/fees"

    params = {
        "school_id": school_id
    }

    headers = {
        "X-Chatbot-Key": CHATBOT_KEY,
        "Accept": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:

            response = await client.get(
                url,
                params=params,
                headers=headers
            )

            print("ERP REQUEST URL =", response.request.url)

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

async def get_student_fee(
    school_id: int,
    student_id: int,
):
    """
    Get fee information for a specific student.
    """

    url = f"{BASE_URL}/student-fee"

    params = {
        "school_id": school_id,
        "student_id": student_id
    }
    headers = {
        "X-Chatbot-Key": CHATBOT_KEY,
        "Accept": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:

            response = await client.get(
                url,
                params={
                    "school_id": school_id,
                    "student_id": student_id
                },
                headers=headers
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