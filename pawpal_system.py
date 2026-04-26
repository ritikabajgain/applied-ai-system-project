from datetime import date, timedelta
from collections import defaultdict


class Task:
    """Represents a single pet care activity."""

    PRIORITY_MAP = {"low": 1, "medium": 2, "high": 3}
    TIME_SLOT_ORDER = {"morning": 0, "afternoon": 1, "evening": 2}
    FREQUENCY_DAYS = {"daily": 1, "weekly": 7, "biweekly": 14, "monthly": 30}

    def __init__(self, title: str, duration_minutes: int, priority: str,
                 category: str = "", frequency: str = "daily",
                 preferred_time: str = "morning",
                 due_date: date | None = None):
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.category = category
        self.frequency = frequency
        self.preferred_time = preferred_time
        self.due_date = due_date if due_date else date.today()
        self.completed = False
        self.last_completed_date: date | None = None
        self.pet_name: str = ""

    def edit(self, title: str = None, duration_minutes: int = None,
             priority: str = None):
        if title is not None:
            self.title = title
        if duration_minutes is not None:
            self.duration_minutes = duration_minutes
        if priority is not None:
            self.priority = priority

    def priority_value(self) -> int:
        return self.PRIORITY_MAP.get(self.priority, 0)

    def is_due(self) -> bool:
        """Check if a task is due based on its due_date and completion status."""
        if self.completed:
            return False
        return self.due_date <= date.today()

    def mark_complete(self):
        self.completed = True
        self.last_completed_date = date.today()

    def mark_incomplete(self):
        self.completed = False

    def create_next_occurrence(self) -> "Task | None":
        """Create the next occurrence of a recurring task using timedelta.

        Uses FREQUENCY_DAYS to calculate the next due_date:
          daily  -> today + timedelta(days=1)
          weekly -> today + timedelta(days=7)
          etc.

        Returns a new Task instance, or None if the task is non-recurring ("once").
        """
        if self.frequency == "once":
            return None

        interval = self.FREQUENCY_DAYS.get(self.frequency)
        if interval is None:
            return None

        next_due = date.today() + timedelta(days=interval)

        next_task = Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            category=self.category,
            frequency=self.frequency,
            preferred_time=self.preferred_time,
            due_date=next_due,
        )
        next_task.pet_name = self.pet_name
        return next_task

    def __repr__(self):
        status = "done" if self.completed else "pending"
        return f"Task({self.title!r}, {self.duration_minutes}min, {self.priority}, {status}, due={self.due_date})"


class Pet:
    """Stores pet details and a list of tasks."""

    def __init__(self, name: str, species: str, age: int):
        self.name = name
        self.species = species
        self.age = age
        self.tasks: list[Task] = []

    def add_task(self, task: Task):
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task):
        self.tasks.remove(task)

    def get_pending_tasks(self) -> list[Task]:
        return [t for t in self.tasks if not t.completed]

    def get_info(self) -> dict:
        return {
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "total_tasks": len(self.tasks),
            "pending_tasks": len(self.get_pending_tasks()),
        }

    def __repr__(self):
        return f"Pet({self.name!r}, {self.species}, {len(self.tasks)} tasks)"


class Owner:
    """Manages multiple pets and provides access to all their tasks."""

    def __init__(self, name: str, time_available: int, preferences: list[str] = None):
        self.name = name
        self.time_available = time_available
        self.preferences = preferences if preferences is not None else []
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet):
        self.pets.append(pet)

    def add_preference(self, preference: str):
        if preference not in self.preferences:
            self.preferences.append(preference)

    def set_available_time(self, minutes: int):
        self.time_available = minutes

    def get_all_tasks(self) -> list[Task]:
        return [task for pet in self.pets for task in pet.tasks]

    def get_all_pending_tasks(self) -> list[Task]:
        return [task for pet in self.pets for task in pet.get_pending_tasks()]

    def __repr__(self):
        return f"Owner({self.name!r}, {len(self.pets)} pets)"


class Scheduler:
    """The brain that retrieves, organizes, and manages tasks across pets."""

    def __init__(self, owner: Owner):
        self.owner = owner
        self.plan: list[Task] = []

    @property
    def available_time(self) -> int:
        return self.owner.time_available

    def generate_plan(self) -> list[Task]:
        # Frequency-aware: only include tasks that are actually due
        pending = [t for t in self.owner.get_all_tasks() if t.is_due()]

        # Multi-key sort: priority (desc), time-of-day (asc), duration (asc)
        sorted_tasks = sorted(pending, key=lambda t: (
            -t.priority_value(),
            Task.TIME_SLOT_ORDER.get(t.preferred_time, 99),
            t.duration_minutes
        ))

        self.plan = []
        time_used = 0
        for task in sorted_tasks:
            if time_used + task.duration_minutes <= self.available_time:
                self.plan.append(task)
                time_used += task.duration_minutes

        return self.plan

    def filter_tasks(self, pet_name: str = None, status: str = None,
                     category: str = None) -> list[Task]:
        """Filter all tasks by pet name, status ('pending'/'done'), and/or category."""
        tasks = self.owner.get_all_tasks()
        if pet_name:
            tasks = [t for t in tasks if t.pet_name == pet_name]
        if status == "pending":
            tasks = [t for t in tasks if not t.completed]
        elif status == "done":
            tasks = [t for t in tasks if t.completed]
        if category:
            tasks = [t for t in tasks if t.category == category]
        return tasks

    def detect_conflicts(self) -> list[str]:
        """Detect scheduling conflicts and return warning messages.

        Checks three conflict types:
          1. Same-pet overlap — two tasks for the same pet in the same time slot
             whose combined duration exceeds the slot budget (the owner can't
             walk a dog and brush it at the same time).
          2. Cross-pet overlap — tasks for different pets in the same slot that
             overlap because the owner only has one pair of hands.
          3. Slot overflow — total minutes scheduled in a slot exceed the budget
             regardless of pet.

        Returns a list of human-readable warning strings (empty = no conflicts).
        """
        SLOT_BUDGET = {"morning": 60, "afternoon": 90, "evening": 60}

        # Group planned tasks by time slot
        slots = defaultdict(list)
        for task in self.plan:
            slots[task.preferred_time].append(task)

        warnings = []

        for slot, tasks in slots.items():
            budget = SLOT_BUDGET.get(slot, 90)

            # --- 1) Same-pet overlap within this slot ---
            pet_groups = defaultdict(list)
            for task in tasks:
                pet_groups[task.pet_name].append(task)

            for pet_name, pet_tasks in pet_groups.items():
                if len(pet_tasks) > 1:
                    pet_total = sum(t.duration_minutes for t in pet_tasks)
                    if pet_total > budget:
                        names = " & ".join(t.title for t in pet_tasks)
                        warnings.append(
                            f"[Same-pet overlap] {pet_name}'s {slot} tasks "
                            f"({names}) total {pet_total} min, but the "
                            f"{slot} slot only has {budget} min."
                        )

            # --- 2) Cross-pet overlap within this slot ---
            if len(pet_groups) > 1:
                slot_total = sum(t.duration_minutes for t in tasks)
                if slot_total > budget:
                    pet_names = list(pet_groups.keys())
                    for i in range(len(pet_names)):
                        for j in range(i + 1, len(pet_names)):
                            t1 = pet_groups[pet_names[i]]
                            t2 = pet_groups[pet_names[j]]
                            combined = sum(t.duration_minutes for t in t1 + t2)
                            if combined > budget:
                                n1 = ", ".join(t.title for t in t1)
                                n2 = ", ".join(t.title for t in t2)
                                warnings.append(
                                    f"[Cross-pet overlap] {slot} slot: "
                                    f"{pet_names[i]} ({n1}) and "
                                    f"{pet_names[j]} ({n2}) total "
                                    f"{combined} min — owner can only handle "
                                    f"{budget} min in this slot."
                                )

            # --- 3) Overall slot overflow ---
            slot_total = sum(t.duration_minutes for t in tasks)
            if slot_total > budget:
                over_by = slot_total - budget
                warnings.append(
                    f"[Slot overflow] {slot} is over-scheduled by {over_by} min "
                    f"({slot_total}/{budget} min used)."
                )

        return warnings

    def explain_plan(self) -> str:
        if not self.plan:
            return "No plan generated yet. Call generate_plan() first."

        lines = [f"Daily Plan for {self.owner.name} "
                 f"({self.get_total_planned_time()}/{self.available_time} min used):"]
        lines.append("-" * 40)

        # Group tasks by time slot for display
        slot_groups = defaultdict(list)
        for task in self.plan:
            slot_groups[task.preferred_time].append(task)

        for slot in ["morning", "afternoon", "evening"]:
            if slot not in slot_groups:
                continue
            lines.append(f"\n  [{slot.upper()}]")
            for task in slot_groups[slot]:
                lines.append(
                    f"    • {task.title} ({task.pet_name}) — {task.duration_minutes} min "
                    f"(priority: {task.priority})"
                )

        remaining = self.get_remaining_time()
        if remaining > 0:
            lines.append(f"\nTime remaining: {remaining} min")

        skipped = [t for t in self.owner.get_all_tasks()
                   if t.is_due() and t not in self.plan]
        if skipped:
            names = ", ".join(t.title for t in skipped)
            lines.append(f"Skipped (not enough time): {names}")

        warnings = self.detect_conflicts()
        if warnings:
            lines.append("\nWarnings:")
            for warning in warnings:
                lines.append(f"  ⚠ {warning}")

        lines.append(f"\nReasoning: Tasks sorted by priority (high→low), then by "
                     f"time-of-day, then shortest first. Recurring tasks only appear "
                     f"when due. Tasks that don't fit within the "
                     f"{self.available_time}-minute window are skipped.")
        return "\n".join(lines)

    def compute_confidence(self, plan: list[Task], due_tasks: list[Task]) -> float:
        """Return a confidence score in [0, 1] for the generated schedule.

        Three equally-weighted components:
          - coverage:    fraction of due tasks that made it into the plan
          - utilisation: fraction of available time actually used (capped at 1)
          - conflict:    1.0 if no conflicts, reduced by 0.15 per conflict warning
        """
        if not due_tasks:
            return 0.0

        coverage = len(plan) / len(due_tasks)

        time_used = sum(t.duration_minutes for t in plan)
        utilisation = min(time_used / self.available_time, 1.0) if self.available_time > 0 else 0.0

        warnings = self.detect_conflicts()
        conflict = max(0.0, 1.0 - len(warnings) * 0.15)

        return round((coverage + utilisation + conflict) / 3, 2)

    def get_total_planned_time(self) -> int:
        return sum(task.duration_minutes for task in self.plan)

    def get_remaining_time(self) -> int:
        return self.available_time - self.get_total_planned_time()

    def complete_task(self, task: Task) -> "Task | None":
        """Mark a task complete. If it recurs, auto-create the next occurrence."""
        task.mark_complete()

        next_task = task.create_next_occurrence()
        if next_task is None:
            return None

        # Find the pet that owns this task and add the next occurrence
        for pet in self.owner.pets:
            if pet.name == task.pet_name:
                pet.add_task(next_task)
                return next_task

        return None

    def __repr__(self):
        return f"Scheduler(owner={self.owner.name!r}, plan={len(self.plan)} tasks)"
