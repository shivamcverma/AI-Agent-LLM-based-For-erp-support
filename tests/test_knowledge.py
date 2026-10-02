from app.rag.knowledge import KnowledgeBase


knowledge_base = KnowledgeBase()


def test_knowledge_loaded():
    assert len(knowledge_base.knowledge) > 0


def test_class_search():
    results = knowledge_base.search(
        "mujhe class create karni hai"
    )

    assert len(results) > 0

    print("\nCLASS SEARCH RESULTS:")
    for result in results:
        print(result)


def test_fees_search():
    results = knowledge_base.search(
        "fees kaise collect kare"
    )

    assert len(results) > 0

    print("\nFEES SEARCH RESULTS:")
    for result in results:
        print(result)