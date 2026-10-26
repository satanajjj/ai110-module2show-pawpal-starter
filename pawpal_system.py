
from dataclasses import dataclass, field
from typing import List


@dataclass
class Task:
    name: str
    description: str
    duration: int
    priority: int = 3
    preferred_time: str = "Anytime"
    frequency: str = "Daily"
    completed: bool = False

    def is_high_priority(self) -> bool:
        return self.priority >= 4

    def fits_in(self, minutes: int) -> bool:
        return self.duration <= minutes

    def mark_complete(self) -> None:
        self.completed = True


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    special_needs: List[str] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def get_tasks(self) -> List[Task]:
        return self.tasks

    def is_senior(self) -> bool:
        return self.age >= 7

    def has_need(self, need: str) -> bool:
        return need in self.special_needs


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferred_time_slots: List[str] = field(default_factory=list)
    notes: str = ""
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def get_time_budget(self) -> int:
        return self.available_minutes

    def prefers_time_slot(self, slot: str) -> bool:
        return slot in self.preferred_time_slots

    def get_all_tasks(self) -> List[tuple[Pet, Task]]:
        all_tasks = []

        for pet in self.pets:
            for task in pet.get_tasks():
                all_tasks.append((pet, task))

        return all_tasks


@dataclass
class DailyPlan:
    scheduled_tasks: List[tuple[Pet, Task]] = field(
        default_factory=list
    )
    skipped_tasks: List[tuple[Pet, Task]] = field(
        default_factory=list
    )
    total_duration: int = 0
    reasoning: str = ""

    def summary(self) -> str:
        return (
            f"Scheduled {len(self.scheduled_tasks)} tasks "
            f"({self.total_duration} minutes). "
            f"Skipped {len(self.skipped_tasks)} tasks."
        )

    def get_tasks_by_time(
        self, slot: str
    ) -> List[tuple[Pet, Task]]:
        return [
            (pet, task)
            for pet, task in self.scheduled_tasks
            if task.preferred_time == slot
        ]


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def generate_plan(self) -> DailyPlan:
        all_tasks = self.owner.get_all_tasks()

        pending_tasks = [
            (pet, task)
            for pet, task in all_tasks
            if not task.completed
        ]

        sorted_tasks = sorted(
            pending_tasks,
            key=lambda item: (
                -item[1].priority,
                item[1].duration
            )
        )

        plan = DailyPlan()
        remaining = self.owner.get_time_budget()

        for pet, task in sorted_tasks:
            if task.fits_in(remaining):
                plan.scheduled_tasks.append((pet, task))
                plan.total_duration += task.duration
                remaining -= task.duration
            else:
                plan.skipped_tasks.append((pet, task))

        plan.reasoning = (
            "Tasks were organized by priority and duration. "
            "Completed tasks were excluded, and activities "
            "that exceeded the available time were skipped."
        )

        return plan
