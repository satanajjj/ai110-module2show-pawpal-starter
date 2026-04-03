classDiagram
    class Owner {
        +String name
        +int available_minutes_per_day
        +list preferred_times
        +String notes
        +get_time_budget() int
        +prefers_time(slot: str) bool
    }

    class Pet {
        +String name
        +String species
        +String breed
        +float age_years
        +list special_needs
        +list tasks
        +add_task(task: Task) void
        +is_senior() bool
        +has_need(need: str) bool
    }

    class Task {
        +String task_id
        +String name
        +String category
        +int duration_minutes
        +int priority
        +String preferred_time
        +String start_time
        +bool is_recurring
        +String recurrence
        +Date due_date
        +String notes
        +bool completed
        +mark_complete() Task | None
        +next_occurrence() Task | None
        +is_high_priority() bool
        +fits_in(remaining_minutes: int) bool
        +__repr__() str
    }

    class Scheduler {
        +Owner owner
        +Pet pet
        +list tasks
        +generate_plan() DailyPlan
        -_sort_by_priority(tasks) list
        -_filter_by_budget(tasks, budget) list
        -_assign_time_slots(tasks) list
        -_explain_reasoning(included, excluded) str
    }

    class DailyPlan {
        +String date
        +list scheduled_tasks
        +list skipped_tasks
        +int total_duration_minutes
        +String reasoning
        +summary() str
        +get_tasks_by_time(slot: str) list
    }

    Owner "1" --> "1" Pet : owns
    Scheduler "1" --> "1" Owner : uses
    Scheduler "1" --> "1" Pet : uses
    Scheduler "1" --> "many" Task : schedules
    Scheduler "1" --> "1" DailyPlan : produces
    DailyPlan "1" --> "many" Task : contains
