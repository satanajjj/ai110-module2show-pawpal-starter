from dataclasses import dataclass, field


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age_years: float
    special_needs: list[str] = field(default_factory=list)
    tasks: list = field(default_factory=list)

    def add_task(self, task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    # Fix 6: senior threshold is species-dependent
    _SENIOR_AGE = {"dog": 7, "cat": 10, "rabbit": 6}

    def is_senior(self) -> bool:
        """Return True if the pet has reached the senior age for its species."""
        threshold = self._SENIOR_AGE.get(self.species.lower(), 8)
        return self.age_years >= threshold

    def has_need(self, need: str) -> bool:
        """Return True if the given special need is in the pet's special_needs list."""
        pass


@dataclass
class Owner:
    name: str
    available_minutes_per_day: int
    preferred_times: list[str] = field(default_factory=list)  # e.g. ["morning", "evening"]
    notes: str = ""

    def get_time_budget(self) -> int:
        """Return the owner's total available minutes per day."""
        pass

    def prefers_time(self, slot: str) -> bool:
        """Return True if the given time slot matches the owner's preferred times."""
        pass


@dataclass
class Task:
    task_id: str
    name: str
    category: str          # walk / feed / meds / grooming / enrichment
    duration_minutes: int
    priority: int          # 1 (low) to 5 (critical)
    preferred_time: str = "any"   # morning / afternoon / evening / any
    is_recurring: bool = True
    notes: str = ""
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def is_high_priority(self) -> bool:
        """Return True if priority is 4 or higher."""
        pass

    def fits_in(self, remaining_minutes: int) -> bool:
        """Return True if this task's duration fits within the remaining time budget."""
        pass

    def __repr__(self) -> str:
        """Return a human-readable string describing the task."""
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet, tasks: list[Task]):
        """Initialize the scheduler with an owner, a pet, and a list of tasks."""
        self.owner = owner
        self.pet = pet
        self.tasks = tasks

    # Fix 4: slot order constant used by both _assign_time_slots and generate_plan
    _SLOT_ORDER = {"morning": 0, "afternoon": 1, "evening": 2, "any": 3}

    def generate_plan(self) -> "DailyPlan":
        """Main entry point. Sort, assign time slots, filter by budget, and return a DailyPlan."""
        # Fix 4: assign slots before filtering so time-constrained tasks are visible
        sorted_tasks = self._sort_by_priority(self.tasks)
        slotted = self._assign_time_slots(sorted_tasks)
        # Fix 1: pass owner's time budget explicitly
        budget = self.owner.get_time_budget()
        included, skipped = self._filter_by_budget(slotted, budget)
        reasoning = self._explain_reasoning(included, skipped)
        # Fix 2: pass pet_name so DailyPlan can reference it in display
        return DailyPlan(
            date="",
            pet_name=self.pet.name,
            scheduled_tasks=included,
            skipped_tasks=skipped,
            reasoning=reasoning,
        )

    def _sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted by priority descending, then duration ascending to break ties."""
        # Fix 3: secondary sort on duration so tie-breaking is deterministic
        return sorted(tasks, key=lambda t: (-t.priority, t.duration_minutes))

    def _filter_by_budget(self, tasks: list[Task], budget: int) -> tuple[list[Task], list[Task]]:
        """Greedily include tasks that fit within the budget; return (included, skipped)."""
        included, skipped = [], []
        remaining = budget
        for task in tasks:
            if task.fits_in(remaining):
                included.append(task)
                remaining -= task.duration_minutes
            else:
                skipped.append(task)
        return included, skipped

    def _assign_time_slots(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by time slot (morning → afternoon → evening → any), preserving priority within each slot."""
        return sorted(tasks, key=lambda t: (self._SLOT_ORDER.get(t.preferred_time, 3), -t.priority))

    def _explain_reasoning(self, included: list[Task], skipped: list[Task]) -> str:
        """Build and return a human-readable explanation of why tasks were included or skipped."""
        pass


@dataclass
class DailyPlan:
    date: str
    pet_name: str                  # Fix 2: store pet name for display
    scheduled_tasks: list[Task]
    skipped_tasks: list[Task]
    reasoning: str

    @property
    def total_duration_minutes(self) -> int:
        """Return the sum of duration_minutes for all scheduled tasks."""
        return sum(t.duration_minutes for t in self.scheduled_tasks)

    def summary(self) -> str:
        """Return a formatted overview of the plan suitable for display in the UI."""
        pass

    def get_tasks_by_time(self, slot: str) -> list[Task]:
        """Return scheduled tasks that match the given time slot."""
        pass
