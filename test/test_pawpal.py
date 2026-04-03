import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Pet, Task


def make_task(task_id="t1", name="Test Task"):
    return Task(
        task_id=task_id,
        name=name,
        category="walk",
        duration_minutes=20,
        priority=3,
    )


def test_mark_complete_changes_status():
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="dog", breed="Labrador", age_years=3)
    assert len(pet.tasks) == 0
    pet.add_task(make_task("t1", "Morning Walk"))
    pet.add_task(make_task("t2", "Evening Walk"))
    assert len(pet.tasks) == 2
