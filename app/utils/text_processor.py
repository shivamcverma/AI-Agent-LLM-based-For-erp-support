import re
from rapidfuzz import process, fuzz


class TextProcessor:

    # ---------------------------------------------------------
    # COMMON CHAT / ERP WORDS
    # ---------------------------------------------------------

    VOCABULARY = {
        # Fee
        "fee": "fee",
        "fees": "fees",
        "due": "due",
        "pending": "pending",
        "paid": "paid",
        "payment": "payment",
        "receipt": "receipt",
        "collection": "collection",

        # Common actions
        "batao": "batao",
        "bata": "batao",
        "btao": "batao",
        "bta": "batao",
        "batado": "batao",
        "btado": "batao",
        "dikhao": "dikhao",
        "dikha": "dikhao",
        "do": "do",
        "chahiye": "chahiye",

        # Student
        "student": "student",
        "students": "students",
        "admission": "admission",
        "number": "number",
        "details": "details",
        "detail": "details",
        "profile": "profile",
        "information": "information",

        # Attendance
        "attendance": "attendance",
        "present": "present",
        "absent": "absent",

        # Exam
        "exam": "exam",
        "examination": "examination",
        "result": "result",
        "results": "results",
        "marks": "marks",
        "mark": "marks",
        "grade": "grade",

        # Homework
        "homework": "homework",
        "assignment": "assignment",
        "classwork": "classwork",

        # Library
        "library": "library",
        "book": "book",
        "books": "books",

        # Transport
        "transport": "transport",
        "bus": "bus",
        "route": "route",

        # Hostel
        "hostel": "hostel",
        "room": "room",

        # HR
        "teacher": "teacher",
        "teachers": "teachers",
        "staff": "staff",
        "employee": "employee",
        "salary": "salary",
        "payroll": "payroll",
        "leave": "leave",

        # Common question words
        "kitna": "kitna",
        "kitni": "kitni",
        "kitne": "kitne",
        "kya": "kya",
        "ka": "ka",
        "ki": "ki",
        "ke": "ke",
        "hai": "hai",
        "hain": "hain",
        "meri": "meri",
        "mera": "mera",
        "mere": "mere",
    }

    # ---------------------------------------------------------
    # NORMALIZE BASIC TEXT
    # ---------------------------------------------------------

    @staticmethod
    def basic_normalize(text: str) -> str:

        text = text.lower().strip()

        # punctuation remove
        text = re.sub(r"[^\w\s]", " ", text)

        # extra spaces
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    # ---------------------------------------------------------
    # FUZZY WORD CORRECTION
    # ---------------------------------------------------------

    @classmethod
    def correct_word(cls, word: str):

        # Very small words should not be fuzzy corrected
        if len(word) <= 2:
            return word

        vocabulary = list(cls.VOCABULARY.keys())

        match = process.extractOne(
            word,
            vocabulary,
            scorer=fuzz.ratio,
            score_cutoff=75
        )

        if not match:
            return word

        matched_word, score, _ = match

        return cls.VOCABULARY[matched_word]

    # ---------------------------------------------------------
    # PROCESS COMPLETE MESSAGE
    # ---------------------------------------------------------

    @classmethod
    def process(cls, text: str):

        original_text = text

        normalized = cls.basic_normalize(text)

        words = normalized.split()

        corrected_words = []

        for word in words:

            corrected_word = cls.correct_word(word)

            corrected_words.append(corrected_word)

        corrected_text = " ".join(corrected_words)

        return {
            "original": original_text,
            "normalized": normalized,
            "corrected": corrected_text
        }