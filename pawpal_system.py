class Task:
    """Represents a single pet care activity."""

    PRIORITY_MAP = {"low": 1, "medium": 2, "high": 3}

    def __init__(self, title: str, duration_minutes: int, priority: str,
                 category: str = "", frequency: str = "daily"):
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.category = category
        self.frequency = frequency
        self.completed = False

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

    def mark_complete(self):
        self.completed = True

    def mark_incomplete(self):
        self.completed = False

    def __repr__(self):
        status = "done" if self.completed else "pending"
        return f"Task({self.title!r}, {self.duration_minutes}min, {self.priority}, {status})"


class Pet:
    """Stores pet details and a list of tasks."""

    def __init__(self, name: str, species: str, age: int):
        self.name = name
        self.species = species
        self.age = age
        self.tasks: list[Task] = []

    def add_task(self, task: Task):
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
        pending = self.owner.get_all_pending_tasks()
        sorted_tasks = sorted(pending, key=lambda t: t.priority_value(), reverse=True)

        self.plan = []
        time_used = 0
        for task in sorted_tasks:
            if time_used + task.duration_minutes <= self.available_time:
                self.plan.append(task)
                time_used += task.duration_minutes

        return self.plan

    def explain_plan(self) -> str:
        if not self.plan:
            return "No plan generated yet. Call generate_plan() first."

        lines = [f"Daily Plan for {self.owner.name} "
                 f"({self.get_total_planned_time()}/{self.available_time} min used):"]
        lines.append("-" * 40)

        for i, task in enumerate(self.plan, start=1):
            lines.append(
                f"{i}. {task.title} — {task.duration_minutes} min "
                f"(priority: {task.priority})"
            )

        remaining = self.get_remaining_time()
        if remaining > 0:
            lines.append(f"\nTime remaining: {remaining} min")

        skipped = [t for t in self.owner.get_all_pending_tasks() if t not in self.plan]
        if skipped:
            names = ", ".join(t.title for t in skipped)
            lines.append(f"Skipped (not enough time): {names}")

        lines.append(f"\nReasoning: Tasks are ordered by priority (high first). "
                     f"Tasks that don't fit within the {self.available_time}-minute "
                     f"window are skipped.")
        return "\n".join(lines)

    def get_total_planned_time(self) -> int:
        return sum(task.duration_minutes for task in self.plan)

    def get_remaining_time(self) -> int:
        return self.available_time - self.get_total_planned_time()

    def complete_task(self, task: Task):
        task.mark_complete()

    def __repr__(self):
        return f"Scheduler(owner={self.owner.name!r}, plan={len(self.plan)} tasks)"
