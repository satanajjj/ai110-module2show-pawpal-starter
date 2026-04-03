import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import timedelta
from pawpal_system import Pet, Owner, Task, Scheduler, DailyPlan


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


def test_task_next_occurrence_rules():
    task = Task(task_id="t1", name="Feed", category="feed", duration_minutes=10, priority=5, recurrence="daily")
    next_task = task.next_occurrence()
    assert next_task is not None
    assert next_task.due_date == task.due_date + timedelta(days=1)
    assert next_task.completed is False
    assert next_task.task_id == "t1_next"

    task.recurrence = "weekly"
    next_week_task = task.next_occurrence()
    assert next_week_task.due_date == task.due_date + timedelta(days=7)

    task.recurrence = None
    assert task.next_occurrence() is None


def test_scheduler_sort_slot_and_budget():
    owner = Owner(name="Alex", available_minutes_per_day=30)
    pet = Pet(name="Mochi", species="cat", breed="Siamese", age_years=2)
    tasks = [
        Task(task_id="t1", name="Groom", category="grooming", duration_minutes=15, priority=3, preferred_time="afternoon"),
        Task(task_id="t2", name="Walk", category="walk", duration_minutes=20, priority=5, preferred_time="morning"),
        Task(task_id="t3", name="Play", category="enrichment", duration_minutes=10, priority=4, preferred_time="any"),
    ]
    scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks.copy())

    plan = scheduler.generate_plan()
    assert plan.pet_name == "Mochi"
    assert plan.total_duration_minutes == 30
    assert [t.task_id for t in plan.scheduled_tasks] == ["t2", "t3"]
    assert [t.task_id for t in plan.skipped_tasks] == ["t1"]

    # verify slot ordering uses morning->afternoon->evening->any
    ordered = scheduler._assign_time_slots(tasks)
    assert [t.task_id for t in ordered] == ["t2", "t1", "t3"]


def test_scheduler_detect_conflicts():
    owner = Owner(name="Sam", available_minutes_per_day=120)
    pet = Pet(name="Puffy", species="rabbit", breed="Lionhead", age_years=4)

    overlap_a = Task(task_id="a", name="Task A", category="feed", duration_minutes=30, priority=2, preferred_time="morning", start_time="09:00")
    overlap_b = Task(task_id="b", name="Task B", category="walk", duration_minutes=30, priority=2, preferred_time="morning", start_time="09:15")
    adjacent = Task(task_id="c", name="Task C", category="meds", duration_minutes=30, priority=2, preferred_time="morning", start_time="09:30")

    scheduler = Scheduler(owner=owner, pet=pet, tasks=[overlap_a, overlap_b, adjacent])
    conflicts = scheduler.detect_conflicts()

    assert (overlap_a, overlap_b) in conflicts or (overlap_b, overlap_a) in conflicts
    assert (overlap_b, adjacent) in conflicts or (adjacent, overlap_b) in conflicts
    assert all(pair[0] != pair[1] for pair in conflicts)
    assert len(conflicts) >= 1


# ── Sorting Correctness ───────────────────────────────────────────────────────

def test_sort_by_time_chronological_order():
    """sort_by_time returns tasks in ascending HH:MM order."""
    owner = Owner(name="Alex", available_minutes_per_day=120)
    pet = Pet(name="Mochi", species="cat", breed="Siamese", age_years=2)
    tasks = [
        Task(task_id="t3", name="Evening Feed",   category="feed", duration_minutes=10, priority=3, start_time="18:00"),
        Task(task_id="t1", name="Morning Walk",   category="walk", duration_minutes=20, priority=3, start_time="08:00"),
        Task(task_id="t2", name="Afternoon Meds", category="meds", duration_minutes=5,  priority=3, start_time="13:30"),
    ]
    scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks)
    result = scheduler.sort_by_time(tasks)
    assert [t.task_id for t in result] == ["t1", "t2", "t3"]


def test_sort_by_time_same_hour_different_minutes():
    """sort_by_time correctly orders tasks within the same hour."""
    owner = Owner(name="Alex", available_minutes_per_day=120)
    pet = Pet(name="Mochi", species="cat", breed="Siamese", age_years=2)
    tasks = [
        Task(task_id="late",  name="Late",  category="walk", duration_minutes=10, priority=3, start_time="09:45"),
        Task(task_id="early", name="Early", category="walk", duration_minutes=10, priority=3, start_time="09:05"),
    ]
    scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks)
    result = scheduler.sort_by_time(tasks)
    assert result[0].task_id == "early"
    assert result[1].task_id == "late"


# ── Recurrence Logic ──────────────────────────────────────────────────────────

def test_mark_complete_daily_creates_next_day_task():
    """Completing a daily task via Scheduler adds a new task due the following day."""
    owner = Owner(name="Alex", available_minutes_per_day=120)
    pet = Pet(name="Mochi", species="cat", breed="Siamese", age_years=2)
    task = Task(task_id="feed1", name="Feed", category="feed",
                duration_minutes=10, priority=5, recurrence="daily")
    scheduler = Scheduler(owner=owner, pet=pet, tasks=[task])

    next_task = scheduler.complete_task(task)

    assert task.completed is True
    assert next_task is not None
    assert next_task.due_date == task.due_date + timedelta(days=1)
    assert next_task.completed is False
    assert next_task in scheduler.tasks


def test_mark_complete_one_time_returns_none():
    """Completing a non-recurring task returns None and does not grow the task list."""
    owner = Owner(name="Alex", available_minutes_per_day=120)
    pet = Pet(name="Mochi", species="cat", breed="Siamese", age_years=2)
    task = Task(task_id="vet1", name="Vet Visit", category="meds",
                duration_minutes=60, priority=5, recurrence=None, is_recurring=False)
    scheduler = Scheduler(owner=owner, pet=pet, tasks=[task])

    next_task = scheduler.complete_task(task)

    assert task.completed is True
    assert next_task is None
    assert len(scheduler.tasks) == 1


# ── Conflict Detection ────────────────────────────────────────────────────────

def test_detect_conflicts_exact_same_start_time():
    """Two tasks starting at the same time are always a conflict."""
    owner = Owner(name="Sam", available_minutes_per_day=120)
    pet = Pet(name="Puffy", species="rabbit", breed="Lionhead", age_years=4)
    task_a = Task(task_id="a", name="Walk",  category="walk",     duration_minutes=30, priority=3, start_time="09:00")
    task_b = Task(task_id="b", name="Groom", category="grooming", duration_minutes=20, priority=3, start_time="09:00")
    scheduler = Scheduler(owner=owner, pet=pet, tasks=[task_a, task_b])

    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
    assert (task_a, task_b) in conflicts or (task_b, task_a) in conflicts


def test_detect_conflicts_no_overlap():
    """Back-to-back tasks (one ends exactly when the next starts) are not conflicts."""
    owner = Owner(name="Sam", available_minutes_per_day=120)
    pet = Pet(name="Puffy", species="rabbit", breed="Lionhead", age_years=4)
    task_a = Task(task_id="a", name="Walk", category="walk", duration_minutes=30, priority=3, start_time="09:00")
    task_b = Task(task_id="b", name="Feed", category="feed", duration_minutes=20, priority=3, start_time="09:30")
    scheduler = Scheduler(owner=owner, pet=pet, tasks=[task_a, task_b])

    conflicts = scheduler.detect_conflicts()

    assert conflicts == []


# ── Existing tests ────────────────────────────────────────────────────────────

def test_dailyplan_filter_and_get_tasks_by_time():
    plan = DailyPlan(date="2026-04-03", pet_name="Mochi", scheduled_tasks=[
        Task(task_id="t2", name="Walk", category="walk", duration_minutes=20, priority=5, preferred_time="morning"),
        Task(task_id="t3", name="Play", category="enrichment", duration_minutes=10, priority=4, preferred_time="evening"),
    ], skipped_tasks=[], reasoning="")

    assert plan.total_duration_minutes == 30
    assert len(plan.get_tasks_by_time("morning")) == 1
    assert len(plan.get_tasks_by_time("afternoon")) == 0
    assert plan.filter_tasks(completed=False) == plan.scheduled_tasks
