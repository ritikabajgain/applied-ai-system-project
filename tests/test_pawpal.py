from pawpal_system import Pet, Task


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
