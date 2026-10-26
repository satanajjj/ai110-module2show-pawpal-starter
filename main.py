
from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    owner = Owner(
        name="Alex",
        available_minutes=90,
        preferred_time_slots=["Morning", "Evening"]
    )

    dog = Pet(
        name="Buddy",
        species="Dog",
        breed="Golden Retriever",
        age=4
    )

    cat = Pet(
        name="Luna",
        species="Cat",
        breed="Siamese",
        age=3
    )

    dog.add_task(Task(
        name="Morning Walk",
        description="Walk around the neighborhood",
        duration=30,
        priority=5,
        preferred_time="Morning"
    ))

    dog.add_task(Task(
        name="Grooming",
        description="Brush fur",
        duration=25,
        priority=2,
        preferred_time="Evening"
    ))

    cat.add_task(Task(
        name="Feeding",
        description="Serve breakfast",
        duration=10,
        priority=5,
        preferred_time="Morning"
    ))

    cat.add_task(Task(
        name="Playtime",
        description="Interactive toy session",
        duration=20,
        priority=3,
        preferred_time="Evening"
    ))

    scheduler = Scheduler(owner)

    owner.add_pet(dog)
    owner.add_pet(cat)

    plan = scheduler.generate_plan()

    print("\n🐾 PAWPAL+ — TODAY'S SCHEDULE")
    print("=" * 40)
    print(f"Owner: {owner.name}")
    print(f"Available Time: {owner.available_minutes} min")
    print("-" * 40)

    for pet, task in plan.scheduled_tasks:
        print(f"\n🐾 {pet.name} ({pet.species})")
        print(f"   Task: {task.name}")
        print(f"   Time: {task.preferred_time}")
        print(f"   Duration: {task.duration} min")
        print(f"   Priority: {task.priority}/5")

    print("\n" + "-" * 40)
    print(plan.summary())

    if plan.skipped_tasks:
        print("\nSkipped Tasks:")
        for pet, task in plan.skipped_tasks:
            print(f"  - {pet.name}: {task.name}")

    print("\nReasoning:")
    print(plan.reasoning)


if __name__ == "__main__":
    main()
