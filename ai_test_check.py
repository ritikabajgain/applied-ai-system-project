from pawpal_system import Task
from ai_engine import AIEngine


def run_basic_ai_test(ai_engine: AIEngine, sample_task: Task) -> str:
    """Smoke-test the AI engine against a known task.

    Checks that explain_task() returns a non-empty, meaningful string.
    Raises AssertionError with a descriptive message on failure so the
    caller can surface it in the UI without a silent miss.
    """
    result = ai_engine.explain_task(sample_task)

    assert result is not None, "explain_task() returned None"
    assert isinstance(result, str), "explain_task() did not return a string"
    assert len(result) > 10, (
        f"explain_task() response is too short ({len(result)} chars): {result!r}"
    )

    return "AI test passed"


def _make_sample_task() -> Task:
    """Return a representative Task used for internal smoke-testing."""
    t = Task(
        title="Morning walk",
        duration_minutes=30,
        priority="high",
        category="walk",
        frequency="daily",
        preferred_time="morning",
    )
    t.pet_name = "Mochi"
    return t


def run_all_checks() -> dict:
    """Run every AI reliability check and return a results dict.

    Keys:
        ai_test   — "AI test passed" or an error message string
        passed    — True if all checks succeeded
    """
    ai = AIEngine()
    task = _make_sample_task()

    try:
        ai_result = run_basic_ai_test(ai, task)
    except AssertionError as exc:
        return {"ai_test": str(exc), "passed": False}

    return {"ai_test": ai_result, "passed": True}
