from app.agents.router import QuestionRouter


router = QuestionRouter()


def test_static_question():

    result = router.detect_type(
        "mujhe class create karni hai"
    )

    print("\nSTATIC:", result)

    assert result["type"] == "static"


def test_dynamic_question():

    result = router.detect_type(
        "meri fees kitni pending hai"
    )

    print("\nDYNAMIC:", result)

    assert result["type"] == "dynamic"


def test_hybrid_question():

    result = router.detect_type(
        "fees kaha se check karu aur meri kitni pending hai"
    )

    print("\nHYBRID:", result)

    assert result["type"] == "hybrid"