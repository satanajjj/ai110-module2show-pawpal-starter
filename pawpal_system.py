from dataclasses import dataclass, field
from datetime import date, timedelta


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
        return need in self.special_needs


@dataclass
class Owner:
    name: str
    available_minutes_per_day: int
    preferred_times: list[str] = field(default_factory=list)  # e.g. ["morning", "evening"]
    notes: str = ""

    def get_time_budget(self) -> int:
        """Return the owner's total available minutes per day."""
        return self.available_minutes_per_day

    def prefers_time(self, slot: str) -> bool:
        """Return True if the given time slot matches the owner's preferred times."""
        return slot in self.preferred_times


@dataclass
class Task:
    task_id: str
    name: str
    category: str          # walk / feed / meds / grooming / enrichment
    duration_minutes: int
    priority: int          # 1 (low) to 5 (critical)
    preferred_time: str = "any"   # morning / afternoon / evening / any
    start_time: str = "00:00"     # scheduled start time in "HH:MM" format
    is_recurring: bool = True
    recurrence: str | None = None  # "daily", "weekly", or None for one-time tasks
    due_date: date = field(default_factory=date.today)
    notes: str = ""
    completed: bool = False

    def mark_complete(self) -> "Task | None":
        """Mark this task as completed and return the next occurrence, if any.

        Returns:
            A new Task scheduled for the next due date if this task recurs,
            or None if it is a one-time task.
        """
        self.completed = True
        return self.next_occurrence()

    def next_occurrence(self) -> "Task | None":
        """Return a fresh, incomplete copy of this task due on the next recurrence date.

        Uses timedelta to advance the due_date:
          - "daily"  → due_date + 1 day
          - "weekly" → due_date + 7 days
          - None     → returns None (task does not repeat)
        """
        _RECURRENCE_DAYS = {"daily": 1, "weekly": 7}
        days = _RECURRENCE_DAYS.get(self.recurrence)
        if days is None:
            return None
        return Task(
            task_id=f"{self.task_id}_next",
            name=self.name,
            category=self.category,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            preferred_time=self.preferred_time,
            start_time=self.start_time,
            is_recurring=self.is_recurring,
            recurrence=self.recurrence,
            due_date=self.due_date + timedelta(days=days),
            notes=self.notes,
            completed=False,
        )

    def is_high_priority(self) -> bool:
        """Return True if priority is 4 or higher."""
        return self.priority >= 4

    def fits_in(self, remaining_minutes: int) -> bool:
        """Return True if this task's duration fits within the remaining time budget."""
        return self.duration_minutes <= remaining_minutes

    def __repr__(self) -> str:
        """Return a human-readable string describing the task."""
        status = "done" if self.completed else "pending"
        return f"[{self.task_id}] {self.name} ({self.category}, {self.duration_minutes}min, priority={self.priority}, {status})"


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

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted by start_time in ascending order.

        Uses a lambda that converts each task's 'HH:MM' start_time string into
        a comparable tuple of ints (hours, minutes), so '08:30' < '13:00'.
        """
        return sorted(
            tasks,
            key=lambda t: tuple(int(part) for part in t.start_time.split(":")),
        )

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

    _SLOT_BASE_MINUTES = {"morning": 7 * 60, "afternoon": 13 * 60, "evening": 18 * 60, "any": 9 * 60}

    def _assign_time_slots(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by time slot (morning → afternoon → evening → any), preserving priority within each slot.

        For tasks whose start_time is still the default '00:00', assign sequential
        start times within each slot starting from the slot's base time.
        """
        ordered = sorted(tasks, key=lambda t: (self._SLOT_ORDER.get(t.preferred_time, 3), -t.priority))
        slot_cursor: dict[str, int] = {}
        for task in ordered:
            if task.start_time == "00:00":
                base = self._SLOT_BASE_MINUTES.get(task.preferred_time, 9 * 60)
                cursor = slot_cursor.get(task.preferred_time, base)
                task.start_time = f"{cursor // 60:02d}:{cursor % 60:02d}"
                slot_cursor[task.preferred_time] = cursor + task.duration_minutes
        return ordered

    def complete_task(self, task: Task) -> Task | None:
        """Mark a task complete and, if it recurs, add the next occurrence to this scheduler.

        Returns the newly created next Task, or None for one-time tasks.
        """
        next_task = task.mark_complete()
        if next_task is not None:
            self.tasks.append(next_task)
            self.pet.add_task(next_task)
        return next_task

    def _explain_reasoning(self, included: list[Task], skipped: list[Task]) -> str:
        """Build and return a human-readable explanation of why tasks were included or skipped."""
        lines = [f"Scheduled {len(included)} task(s), skipped {len(skipped)}."]
        for task in included:
            lines.append(f"  + {task.name} (priority={task.priority}, {task.duration_minutes}min)")
        for task in skipped:
            lines.append(f"  - {task.name} skipped: exceeds remaining time budget")
        return "\n".join(lines)

    def detect_conflicts(self) -> list[tuple[Task, Task]]:
        """Return pairs of scheduled tasks whose time windows overlap.

        A conflict exists when two tasks share the same preferred_time slot and
        their HH:MM start times plus durations overlap.
        """
        conflicts = []
        tasks = [t for t in self.tasks if not t.completed]
        for i, a in enumerate(tasks):
            for b in tasks[i + 1:]:
                a_start = sum(int(x) * m for x, m in zip(a.start_time.split(":"), (60, 1)))
                b_start = sum(int(x) * m for x, m in zip(b.start_time.split(":"), (60, 1)))
                a_end = a_start + a.duration_minutes
                b_end = b_start + b.duration_minutes
                if a_start < b_end and b_start < a_end:
                    conflicts.append((a, b))
        return conflicts


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
        lines = [
            f"Plan for {self.pet_name}",
            f"  Total scheduled: {self.total_duration_minutes} min across {len(self.scheduled_tasks)} task(s)",
        ]
        if self.skipped_tasks:
            lines.append(f"  Skipped: {', '.join(t.name for t in self.skipped_tasks)}")
        lines.append(f"  Reasoning:\n{self.reasoning}")
        return "\n".join(lines)

    def get_tasks_by_time(self, slot: str) -> list[Task]:
        """Return scheduled tasks that match the given time slot."""
        return [t for t in self.scheduled_tasks if t.preferred_time == slot]

    def filter_tasks(
        self,
        *,
        completed: bool | None = None,
        pet_name: str | None = None,
    ) -> list[Task]:
        """Return scheduled tasks filtered by completion status and/or pet name.

        Args:
            completed: If True, return only completed tasks. If False, return
                       only incomplete tasks. If None, skip this filter.
            pet_name:  If provided, return only tasks belonging to that pet.
                       If None, skip this filter.

        Examples:
            plan.filter_tasks(completed=False)              # all pending tasks
            plan.filter_tasks(pet_name="Mochi")             # all of Mochi's tasks
            plan.filter_tasks(completed=True, pet_name="Mochi")  # Mochi's done tasks
        """
        tasks = self.scheduled_tasks
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        if pet_name is not None:
            tasks = [t for t in tasks if self.pet_name.lower() == pet_name.lower()]
        return tasks
