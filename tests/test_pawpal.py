
from pawpal_system import Task, Pet


def test_task_completion():
    """Verify that mark_complete() updates task status."""
    task = Task(
        name="Feeding",
        description="Feed the cat",
        duration=10
    )

    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_task_addition():
    """Verify that adding a task increases the pet's task count."""
    pet = Pet(
        name="Buddy",
        species="Dog",
        breed="Golden Retriever",
        age=4
    )

    task = Task(
        name="Morning Walk",
        description="Walk around the neighborhood",
        duration=30
    )

    initial_count = len(pet.tasks)

    pet.add_task(task)

    assert len(pet.tasks) == initial_count + 1
