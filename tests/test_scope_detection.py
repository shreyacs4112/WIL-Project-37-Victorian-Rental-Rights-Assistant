from rag.pipeline import is_rental_rights_question


def test_in_scope_questions():
    """Victorian rental-rights questions should be accepted."""
    questions = [
        "How do I get my bond back?",
        "My landlord has not repaired the heater.",
        "Can my property manager enter without notice?",
        "Can my rent be increased?",
        "What are the minimum standards for a rental property?",
    ]

    for question in questions:
        assert is_rental_rights_question(question) is True


def test_out_of_scope_questions():
    """Unrelated questions should be rejected."""
    questions = [
        "What is the capital of Japan?",
        "What is the current weather?",
        "How do I cook pasta?",
        "Who won the football match?",
    ]

    for question in questions:
        assert is_rental_rights_question(question) is False


def test_non_victorian_rental_questions():
    """Rental questions explicitly about other jurisdictions should be rejected."""
    questions = [
        "What are the rental laws in New South Wales?",
        "Can my landlord increase my rent in NSW?",
        "What are the tenancy rules in Queensland?",
        "How do I get my bond back in Tasmania?",
    ]

    for question in questions:
        assert is_rental_rights_question(question) is False


def test_substring_does_not_trigger_scope():
    """Rental keywords inside unrelated words should not create false matches."""
    assert is_rental_rights_question("What is the current weather?") is False