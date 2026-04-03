from pawpal_system import Pet, Owner, Task, Scheduler

# --- Owner ---
owner = Owner(
    name="Alex",
    available_minutes_per_day=90,
    preferred_times=["morning", "evening"],
)

# --- Pets ---
buddy = Pet(
    name="Buddy",
    species="dog",
    breed="Labrador",
    age_years=8,
    special_needs=["joint supplement"],
)

luna = Pet(
    name="Luna",
    species="cat",
    breed="Siamese",
    age_years=4,
    special_needs=[],
)

# --- Tasks per pet ---
# Tasks added out of order (not sorted by time or priority) to demonstrate sorting
buddy_tasks = [
    Task(
        task_id="b4",
        name="Grooming Brush",
        category="grooming",
        duration_minutes=20,
        priority=2,
        preferred_time="afternoon",
        start_time="14:00",
    ),
    Task(
        task_id="b3",
        name="Evening Walk",
        category="walk",
        duration_minutes=30,
        priority=4,
        preferred_time="evening",
        start_time="18:00",
    ),
    Task(
        task_id="b2",
        name="Joint Supplement",
        category="meds",
        duration_minutes=5,
        priority=4,
        preferred_time="morning",
        start_time="08:00",
    ),
    Task(
        task_id="b1",
        name="Morning Walk",
        category="walk",
        duration_minutes=30,
        priority=5,
        preferred_time="morning",
        start_time="07:00",
    ),
]

# Tasks added out of order (not sorted by time or priority) to demonstrate sorting
luna_tasks = [
    Task(
        task_id="l3",
        name="Dinner",
        category="feed",
        duration_minutes=10,
        priority=5,
        preferred_time="evening",
        start_time="18:00",
    ),
    Task(
        task_id="l2",
        name="Interactive Play",
        category="enrichment",
        duration_minutes=15,
        priority=3,
        preferred_time="afternoon",
        start_time="13:00",
    ),
    Task(
        task_id="l1",
        name="Breakfast",
        category="feed",
        duration_minutes=10,
        priority=5,
        preferred_time="morning",
        start_time="07:30",
    ),
]

# --- Generate plans ---
buddy_scheduler = Scheduler(owner=owner, pet=buddy, tasks=buddy_tasks)
luna_scheduler = Scheduler(owner=owner, pet=luna, tasks=luna_tasks)

buddy_plan = buddy_scheduler.generate_plan()
luna_plan = luna_scheduler.generate_plan()


# --- Display helper ---
def print_pet_schedule(plan, scheduler):
    print(f"  {plan.pet_name}  ({plan.total_duration_minutes} min total)")
    sorted_tasks = scheduler.sort_by_time(plan.scheduled_tasks)
    for slot in ("morning", "afternoon", "evening", "any"):
        slot_tasks = [t for t in sorted_tasks if t.preferred_time == slot]
        if slot_tasks:
            print(f"    [{slot.capitalize()}]")
            for task in slot_tasks:
                print(f"      - {task.start_time}  {task.name} ({task.duration_minutes} min)")
    if plan.skipped_tasks:
        skipped_names = ", ".join(t.name for t in plan.skipped_tasks)
        print(f"    Skipped (over budget): {skipped_names}")


# --- Today's Schedule ---
print("=" * 40)
print("        TODAY'S SCHEDULE")
print(f"        Owner: {owner.name}")
print("=" * 40)

for plan, scheduler in ((buddy_plan, buddy_scheduler), (luna_plan, luna_scheduler)):
    print()
    print_pet_schedule(plan, scheduler)

print()
print("=" * 40)
