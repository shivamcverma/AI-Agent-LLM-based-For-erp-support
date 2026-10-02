import httpx

from app.config.settings import settings


BASE_URL = settings.erp_chatbot_base_url
CHATBOT_KEY = settings.erp_chatbot_key


# ==========================================================
# COMMON API REQUEST
# ==========================================================

async def _get(
    endpoint: str,
    params: dict
):
    url = f"{BASE_URL}{endpoint}"

    headers = {
        "X-Chatbot-Key": CHATBOT_KEY,
        "Accept": "application/json"
    }

    try:

        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            response = await client.get(
                url,
                params=params,
                headers=headers
            )

            print(
                "ERP REQUEST URL =",
                response.request.url
            )

            response.raise_for_status()

            return response.json()

    except httpx.HTTPStatusError as e:

        return {
            "status": "error",
            "message": (
                f"ERP API returned status "
                f"{e.response.status_code}"
            )
        }

    except httpx.RequestError as e:

        return {
            "status": "error",
            "message": (
                "Unable to connect to ERP API: "
                f"{str(e)}"
            )
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }


# ==========================================================
# STUDENT SUMMARY
# /students
# /students?class_id=
# ==========================================================

async def get_student_summary(
    school_id: int,
    class_id: int | None = None,
    gender: str | None = None,
    section_name: str | None = None,
    student_name: str | None = None,
  
):

    params = {
        "school_id": school_id
    }

    if class_id is not None:
        params["class_id"] = class_id

    if gender:
        params["gender"] = gender

    if section_name:
        params["section_name"] = section_name

    if student_name:
        params["student_name"] = student_name

    print(
        "ERP STUDENT SUMMARY PARAMS =",
        params
    )

    return await _get(
        "/students",
        params
    )


# ==========================================================
# STUDENT SEARCH
# /students/search
#
# Existing fee flow ke liye preserve kiya gaya hai.
# ==========================================================

# ==========================================================
# SEARCH STUDENTS
# ==========================================================

async def search_students(
    school_id: int,
    search: str
):

    params = {
        "school_id": school_id,
        "search": search
    }

    return await _get(
        "/students/search",
        params
    )


async def find_student(
    school_id: int,
    search_text: str,
    class_id: int | None = None,
):

    search_text = search_text.strip()

    # ======================================================
    # 1. FULL SEARCH
    # ======================================================

    result = await get_student_list(
        school_id=school_id,
        search=search_text,
        class_id=class_id
    )

    if result.get("status") == "success":

        students = result.get(
            "data",
            {}
        ).get(
            "students",
            []
        )

        # Exact full-name matches
        exact_matches = [
            student
            for student in students
            if student.get("name", "").strip().lower()
            == search_text.lower()
        ]

        if exact_matches:

            if len(exact_matches) == 1:
                return {
                    "status": "success",
                    "student": exact_matches[0]
                }

            return {
                "status": "multiple",
                "students": exact_matches
            }

    # ======================================================
    # 2. SPLIT FULL NAME
    # ======================================================

    words = search_text.split()

    print("SEARCH WORDS =", words)

    for word in words:

        if len(word) < 2:
            continue

        print("FALLBACK SEARCH WORD =", word)

        result = await get_student_list(
            school_id=school_id,
            search=word
        )

        print(
            "FALLBACK SEARCH RESULT =",
            result
        )

        if result.get("status") != "success":
            continue

        students = result.get(
            "data",
            {}
        ).get(
            "students",
            []
        )

        # ==================================================
        # EXACT FULL NAME MATCH
        # ==================================================

        exact_matches = [
            student
            for student in students
            if student.get("name", "").strip().lower()
            == search_text.lower()
        ]

        print(
            "EXACT NAME MATCHES =",
            exact_matches
        )

        if len(exact_matches) == 1:

            return {
                "status": "success",
                "student": exact_matches[0]
            }

        if len(exact_matches) > 1:

            return {
                "status": "multiple",
                "students": exact_matches
            }

    # ======================================================
    # 3. NOT FOUND
    # ======================================================

    return {
        "status": "not_found",
        "students": []
    }
# ==========================================================
# SINGLE STUDENT DETAILS
# /students/{student_id}
# ==========================================================

async def get_student_details(
    school_id: int,
    student_id: int
):

    params = {
        "school_id": school_id
    }

    return await _get(
        f"/students/{student_id}",
        params
    )


# ==========================================================
# STUDENT LIST
#
# /student-list
# /student-list?class_id=
# /student-list?class_id=&section_id=&gender=
# /student-list?search=
# ==========================================================

async def get_student_list(
    school_id: int,
    class_id: int | None = None,
    section_id: int | None = None,
    gender: str | None = None,
    search: str | None = None,
):
    params = {
        "school_id": school_id
    }
    if class_id is not None:
        params["class_id"] = class_id

    if section_id is not None:
        params["section_id"] = section_id

    if gender:
        params["gender"] = gender

    if search:
        params["search"] = search
    print("ERP STUDENT LIST PARAMS =", params)
    return await _get(
        "/student-list",
        params=params
    )

# ==========================================================
# CLASS NAME NORMALIZATION
# ==========================================================

def normalize_class_name(class_name: str):

    value = class_name.strip().lower()

    # Remove common words
    value = value.replace("standard", "")
    value = value.replace("std", "")
    value = value.replace("class", "")
    value = value.strip()

    # Roman numerals
    roman_map = {
        "i": "1",
        "ii": "2",
        "iii": "3",
        "iv": "4",
        "v": "5",
        "vi": "6",
        "vii": "7",
        "viii": "8",
        "ix": "9",
        "x": "10",
        "xi": "11",
        "xii": "12",
    }

    if value in roman_map:
        return f"class {roman_map[value]}"

    # Number words
    number_map = {
        "one": "1",
        "first": "1",

        "two": "2",
        "second": "2",

        "three": "3",
        "third": "3",

        "four": "4",
        "fourth": "4",

        "five": "5",
        "fifth": "5",

        "six": "6",
        "sixth": "6",

        "seven": "7",
        "seventh": "7",

        "eight": "8",
        "eighth": "8",

        "nine": "9",
        "ninth": "9",

        "ten": "10",
        "tenth": "10",

        "eleven": "11",
        "eleventh": "11",

        "twelve": "12",
        "twelfth": "12",
    }

    if value in number_map:
        return f"class {number_map[value]}"

    # Numeric class
    if value.isdigit():
        return f"class {value}"

    # KG / Nursery etc.
    return value

# ==========================================================
# FIND ACTUAL ERP CLASS
# ==========================================================

async def find_class_id(
    school_id: int,
    class_name: str
):

    result = await get_student_summary(
        school_id
    )

    if result.get("status") != "success":

        return None

    breakdown = result.get(
        "data",
        {}
    ).get(
        "class_breakdown",
        []
    )

    requested_class = normalize_class_name(
        class_name
    )

    print(
        "NORMALIZED CLASS =",
        requested_class
    )

    for item in breakdown:

        api_class_name = str(
            item.get(
                "class_name",
                ""
            )
        ).strip().lower()

        normalized_api_class = normalize_class_name(
            api_class_name
        )

        print(
            "CHECKING CLASS =",
            api_class_name,
            "=>",
            normalized_api_class
        )

        if requested_class == normalized_api_class or requested_class.startswith(normalized_api_class + " "):

            print(
                "MATCHED CLASS =",
                item.get("class_name"),
                "CLASS ID =",
                item.get("class_id")
            )

            return item.get("class_id")

    return None

# ==========================================================
# CLASS INFORMATION
#
# Used when user asks:
# "Class X me kitne student hain"
# ==========================================================

# ==========================================================
# CLASS STUDENT SUMMARY
# ==========================================================

async def get_class_student_summary(
    school_id: int,
    class_name: str,
    gender: str | None = None,
    section_name: str | None = None,
    student_name: str | None = None,

):

    class_id = await find_class_id(
        school_id,
        class_name
    )

    if class_id is None:

        return {
            "status": "error",
            "message": (
                f"Class '{class_name}' "
                "not found."
            )
        }

    print(
        "USING ACTUAL ERP CLASS ID =",
        class_id
    )

    print(
        "GENDER FILTER =",
        gender
    )

    return await get_student_summary(
        school_id=school_id,
        class_id=class_id,
        gender=gender,
        section_name=section_name,
        student_name=student_name,
  
    )

async def get_student_details_by_search(
    school_id: int,
    search: str | None = None,
    class_id: int | None = None,
    section_id: int | None = None,
    gender: str | None = None,
):
    return await get_student_list(
        school_id=school_id,
        class_id=class_id,
        section_id=section_id,
        gender=gender,
        search=search,
    )