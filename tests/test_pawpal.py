from datetime import date, timedelta
from pawpal_system import Pet, Task, Owner, Scheduler


# ── Existing tests ──────────────────────────────────────────────


def test_task_completion():
    task = Task("Morning walk", duration_minutes=30, priority="high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_to_pet():
    pet = Pet("Mochi", species="dog", age=3)
    assert len(pet.tasks) == 0
    pet.add_task(Task("Feed Mochi", duration_minutes=10, priority="high"))
    assert len(pet.tasks) == 1
    pet.add_task(Task("Evening walk", duration_minutes=20, priority="medium"))
    assert len(pet.tasks) == 2


# ── Required: Sorting Correctness ───────────────────────────────


def test_plan_chronological_order():
    """Plan returns tasks in chronological time-slot order (morning → afternoon → evening)."""
    owner = Owner("Alice", time_available=120)
    pet = Pet("Mochi", species="dog", age=3)
    # Add in reverse chronological order to prove sorting fixes it
    pet.add_task(Task("Evening groom", duration_minutes=15, priority="high", preferred_time="evening"))
    pet.add_task(Task("Afternoon play", duration_minutes=15, priority="high", preferred_time="afternoon"))
    pet.add_task(Task("Morning walk", duration_minutes=15, priority="high", preferred_time="morning"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    time_slots = [t.preferred_time for t in plan]
    assert time_slots == ["morning", "afternoon", "evening"]


# ── Required: Recurrence Logic ──────────────────────────────────


def test_complete_daily_task_creates_tomorrow():
    """Marking a daily task complete via the Scheduler creates a new task due tomorrow."""
    owner = Owner("Alice", time_available=120)
    pet = Pet("Mochi", species="dog", age=3)
    task = Task("Morning walk", duration_minutes=30, priority="high", frequency="daily")
    pet.add_task(task)
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    next_task = scheduler.complete_task(task)

    # Original is done
    assert task.completed is True
    # New task exists with correct due date
    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(days=1)
    assert next_task.completed is False
    # New task was added to the same pet
    assert next_task in pet.tasks


# ── Required: Conflict Detection ────────────────────────────────


def test_conflict_two_tasks_exact_same_time_slot():
    """Two tasks in the exact same time slot whose durations exceed the slot budget are flagged."""
    owner = Owner("Alice", time_available=120)
    pet = Pet("Mochi", species="dog", age=3)
    # Morning budget = 60 min; two 35-min tasks = 70 min → conflict
    pet.add_task(Task("Walk", duration_minutes=35, priority="high", preferred_time="morning"))
    pet.add_task(Task("Train", duration_minutes=35, priority="high", preferred_time="morning"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()
    warnings = scheduler.detect_conflicts()

    assert len(warnings) > 0
    assert any("morning" in w for w in warnings)


def test_no_conflict_when_same_slot_within_budget():
    """Two tasks in the same slot that fit within the budget produce no warnings."""
    owner = Owner("Alice", time_available=120)
    pet = Pet("Mochi", species="dog", age=3)
    # Afternoon budget = 90 min; two 30-min tasks = 60 min → no conflict
    pet.add_task(Task("Feed", duration_minutes=30, priority="high", preferred_time="afternoon"))
    pet.add_task(Task("Play", duration_minutes=30, priority="high", preferred_time="afternoon"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()
    warnings = scheduler.detect_conflicts()

    assert warnings == []


# ── Happy-path: Sorting ────────────────────────────────────────


def test_sort_by_priority_descending():
    """High-priority tasks appear before low-priority ones in the plan."""
    owner = Owner("Alice", time_available=120)
    pet = Pet("Mochi", species="dog", age=3)
    pet.add_task(Task("Low task", duration_minutes=10, priority="low", preferred_time="morning"))
    pet.add_task(Task("High task", duration_minutes=10, priority="high", preferred_time="morning"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    assert plan[0].title == "High task"
    assert plan[1].title == "Low task"


def test_sort_by_time_slot():
    """Morning tasks sort before afternoon, which sort before evening (same priority)."""
    owner = Owner("Alice", time_available=120)
    pet = Pet("Mochi", species="dog", age=3)
    pet.add_task(Task("Evening task", duration_minutes=10, priority="high", preferred_time="evening"))
    pet.add_task(Task("Morning task", duration_minutes=10, priority="high", preferred_time="morning"))
    pet.add_task(Task("Afternoon task", duration_minutes=10, priority="high", preferred_time="afternoon"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    assert [t.title for t in plan] == ["Morning task", "Afternoon task", "Evening task"]


def test_sort_tiebreak_by_duration():
    """When priority and time slot are equal, shorter tasks come first."""
    owner = Owner("Alice", time_available=120)
    pet = Pet("Mochi", species="dog", age=3)
    pet.add_task(Task("Long task", duration_minutes=45, priority="high", preferred_time="morning"))
    pet.add_task(Task("Short task", duration_minutes=15, priority="high", preferred_time="morning"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    assert plan[0].title == "Short task"
    assert plan[1].title == "Long task"


# ── Happy-path: Recurring tasks ────────────────────────────────


def test_daily_task_creates_next_occurrence():
    """Completing a daily task creates a new one due tomorrow."""
    task = Task("Walk", duration_minutes=30, priority="high", frequency="daily")
    task.pet_name = "Mochi"
    next_task = task.create_next_occurrence()

    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(days=1)
    assert next_task.frequency == "daily"
    assert next_task.pet_name == "Mochi"


def test_weekly_task_creates_next_occurrence():
    """Completing a weekly task creates a new one due in 7 days."""
    task = Task("Bath", duration_minutes=60, priority="medium", frequency="weekly")
    next_task = task.create_next_occurrence()

    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(days=7)


def test_complete_task_adds_next_to_pet():
    """Scheduler.complete_task() adds the next occurrence to the correct pet."""
    owner = Owner("Alice", time_available=120)
    pet = Pet("Mochi", species="dog", age=3)
    task = Task("Walk", duration_minutes=30, priority="high", frequency="daily")
    pet.add_task(task)
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    next_task = scheduler.complete_task(task)

    assert next_task is not None
    assert len(pet.tasks) == 2  # original + new occurrence
    assert next_task in pet.tasks


# ── Happy-path: Plan generation & filtering ─────────────────────


def test_greedy_packing_respects_time_budget():
    """Tasks are packed greedily by priority within the time budget."""
    owner = Owner("Alice", time_available=40)
    pet = Pet("Mochi", species="dog", age=3)
    pet.add_task(Task("High", duration_minutes=30, priority="high"))
    pet.add_task(Task("Medium", duration_minutes=20, priority="medium"))  # won't fit
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    assert len(plan) == 1
    assert plan[0].title == "High"


def test_filter_by_pet_and_status():
    """Filtering by pet name and status returns correct subset."""
    owner = Owner("Alice", time_available=120)
    mochi = Pet("Mochi", species="dog", age=3)
    luna = Pet("Luna", species="cat", age=2)
    t1 = Task("Walk", duration_minutes=30, priority="high")
    t2 = Task("Feed", duration_minutes=10, priority="high")
    t1.mark_complete()
    mochi.add_task(t1)
    mochi.add_task(t2)
    luna.add_task(Task("Groom", duration_minutes=20, priority="low"))
    owner.add_pet(mochi)
    owner.add_pet(luna)

    scheduler = Scheduler(owner)
    result = scheduler.filter_tasks(pet_name="Mochi", status="pending")

    assert len(result) == 1
    assert result[0].title == "Feed"


# ── Edge cases: Empty / missing data ───────────────────────────


def test_pet_with_no_tasks():
    """A pet with zero tasks doesn't break plan generation."""
    owner = Owner("Alice", time_available=120)
    owner.add_pet(Pet("Mochi", species="dog", age=3))

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    assert plan == []


def test_owner_with_no_pets():
    """An owner with no pets produces an empty plan."""
    owner = Owner("Alice", time_available=120)
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    assert plan == []


def test_all_tasks_completed():
    """If every task is completed, the plan is empty."""
    owner = Owner("Alice", time_available=120)
    pet = Pet("Mochi", species="dog", age=3)
    t = Task("Walk", duration_minutes=30, priority="high")
    t.mark_complete()
    pet.add_task(t)
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    assert plan == []


# ── Edge cases: Time conflicts ──────────────────────────────────


def test_same_pet_overlap_conflict():
    """Two tasks for the same pet in one slot exceeding the budget triggers a warning."""
    owner = Owner("Alice", time_available=120)
    pet = Pet("Mochi", species="dog", age=3)
    # Evening budget is 60 min; two tasks totalling 75 min
    pet.add_task(Task("Walk", duration_minutes=45, priority="high", preferred_time="evening"))
    pet.add_task(Task("Bath", duration_minutes=30, priority="high", preferred_time="evening"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()
    warnings = scheduler.detect_conflicts()

    assert any("[Same-pet overlap]" in w for w in warnings)


def test_cross_pet_overlap_conflict():
    """Tasks for different pets in the same slot exceeding the budget triggers a warning."""
    owner = Owner("Alice", time_available=120)
    mochi = Pet("Mochi", species="dog", age=3)
    luna = Pet("Luna", species="cat", age=2)
    mochi.add_task(Task("Walk Mochi", duration_minutes=45, priority="high", preferred_time="morning"))
    luna.add_task(Task("Feed Luna", duration_minutes=30, priority="high", preferred_time="morning"))
    owner.add_pet(mochi)
    owner.add_pet(luna)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()
    warnings = scheduler.detect_conflicts()

    assert any("[Cross-pet overlap]" in w for w in warnings)


def test_slot_overflow_conflict():
    """Total minutes in a slot exceeding the budget triggers a slot overflow warning."""
    owner = Owner("Alice", time_available=120)
    pet = Pet("Mochi", species="dog", age=3)
    # Morning budget is 60 min
    pet.add_task(Task("Walk", duration_minutes=35, priority="high", preferred_time="morning"))
    pet.add_task(Task("Play", duration_minutes=35, priority="high", preferred_time="morning"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()
    warnings = scheduler.detect_conflicts()

    assert any("[Slot overflow]" in w for w in warnings)


# ── Edge cases: Time budget boundaries ──────────────────────────


def test_exact_fit():
    """Tasks that sum to exactly the available time all get included."""
    owner = Owner("Alice", time_available=60)
    pet = Pet("Mochi", species="dog", age=3)
    pet.add_task(Task("Walk", duration_minutes=30, priority="high"))
    pet.add_task(Task("Feed", duration_minutes=30, priority="medium"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    assert scheduler.get_total_planned_time() == 60
    assert scheduler.get_remaining_time() == 0
    assert len(plan) == 2


def test_one_minute_over_excluded():
    """A task that would push total 1 minute past the budget is excluded."""
    owner = Owner("Alice", time_available=59)
    pet = Pet("Mochi", species="dog", age=3)
    pet.add_task(Task("Walk", duration_minutes=30, priority="high"))
    pet.add_task(Task("Feed", duration_minutes=30, priority="medium"))  # 30+30=60 > 59
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    assert len(plan) == 1
    assert plan[0].title == "Walk"


def test_single_task_exceeds_total_budget():
    """A task longer than the entire budget is skipped even if it's the only one."""
    owner = Owner("Alice", time_available=20)
    pet = Pet("Mochi", species="dog", age=3)
    pet.add_task(Task("Long grooming", duration_minutes=60, priority="high"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    assert plan == []


# ── Edge cases: Sorting edge cases ──────────────────────────────


def test_unknown_preferred_time_sorts_last():
    """A task with an unrecognized preferred_time sorts after morning/afternoon/evening."""
    owner = Owner("Alice", time_available=120)
    pet = Pet("Mochi", species="dog", age=3)
    pet.add_task(Task("Midnight snack", duration_minutes=10, priority="high", preferred_time="midnight"))
    pet.add_task(Task("Morning walk", duration_minutes=10, priority="high", preferred_time="morning"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    assert plan[0].title == "Morning walk"
    assert plan[1].title == "Midnight snack"


# ── Edge cases: Recurring task edge cases ───────────────────────


def test_one_time_task_no_next_occurrence():
    """A 'once' frequency task returns None from create_next_occurrence."""
    task = Task("Vet visit", duration_minutes=60, priority="high", frequency="once")
    assert task.create_next_occurrence() is None


def test_complete_recurring_task_orphaned_pet_name():
    """If pet_name doesn't match any pet, the next occurrence is created but not added."""
    owner = Owner("Alice", time_available=120)
    pet = Pet("Mochi", species="dog", age=3)
    task = Task("Walk", duration_minutes=30, priority="high", frequency="daily")
    pet.add_task(task)
    owner.add_pet(pet)
    # Override pet_name AFTER add_task to simulate a mismatch
    task.pet_name = "Ghost"

    scheduler = Scheduler(owner)
    original_task_count = len(pet.tasks)
    result = scheduler.complete_task(task)

    assert task.completed is True
    assert result is None  # next task created but not added to any pet
    assert len(pet.tasks) == original_task_count  # no new task added


# ── Edge cases: Filtering ───────────────────────────────────────


def test_filter_nonexistent_pet():
    """Filtering by a pet name that doesn't exist returns an empty list."""
    owner = Owner("Alice", time_available=120)
    pet = Pet("Mochi", species="dog", age=3)
    pet.add_task(Task("Walk", duration_minutes=30, priority="high"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    assert scheduler.filter_tasks(pet_name="NoSuchPet") == []


def test_filter_invalid_status_returns_all():
    """An unrecognized status string skips status filtering and returns all tasks."""
    owner = Owner("Alice", time_available=120)
    pet = Pet("Mochi", species="dog", age=3)
    t1 = Task("Walk", duration_minutes=30, priority="high")
    t2 = Task("Feed", duration_minutes=10, priority="low")
    t1.mark_complete()
    pet.add_task(t1)
    pet.add_task(t2)
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    result = scheduler.filter_tasks(status="invalid")

    assert len(result) == 2  # both completed and pending returned


def test_filter_nonexistent_category():
    """Filtering by a category no task has returns an empty list."""
    owner = Owner("Alice", time_available=120)
    pet = Pet("Mochi", species="dog", age=3)
    pet.add_task(Task("Walk", duration_minutes=30, priority="high", category="exercise"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    assert scheduler.filter_tasks(category="grooming") == []
