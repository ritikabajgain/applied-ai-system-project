class Owner:
    """Represents a pet owner with their preferences and availability."""

    def __init__(self, name: str, time_available: int, preferences: list[str] = None):
        self.name = name
        self.time_available = time_available
        self.preferences = preferences if preferences is not None else []

    def add_preference(self, preference: str):
        pass

    def set_available_time(self, minutes: int):
        pass


class Pet:
    """Represents a pet with basic info and a reference to its owner."""

    def __init__(self, name: str, species: str, age: int, owner: Owner):
        self.name = name
        self.species = species
        self.age = age
        self.owner = owner

    def get_info(self) -> dict:
        pass


class Task:
    """Represents a pet care task with duration and priority."""

    def __init__(self, title: str, duration_minutes: int, priority: str, category: str = ""):
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.category = category

    def edit(self, title: str, duration_minutes: int, priority: str):
        pass

    def priority_value(self) -> int:
        pass


class Schedule:
    """Generates and manages a daily care plan for a pet."""

    def __init__(self, pet: Pet, available_time: int):
        self.pet = pet
        self.tasks: list[Task] = []
        self.total_time = 0
        self.available_time = available_time

    def add_task(self, task: Task):
        pass

    def remove_task(self, task: Task):
        pass

    def generate_plan(self) -> list[Task]:
        pass

    def explain_plan(self) -> str:
        pass

    def get_remaining_time(self) -> int:
        pass
