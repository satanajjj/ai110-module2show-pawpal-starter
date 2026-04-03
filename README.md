# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

<a href="/course_images/ai110/pawpal_demo.png" target="_blank"><img src='/course_images/ai110/pawpal_demo.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## Features

- Priority-first task sorting (high → low, duration tie-break)
- Time-slot assignment with ordered slots: `morning`, `afternoon`, `evening`, `any`
- Schedule generation includes budget filtering (greedy inclusion then skipped tasks)
- Conflict detection for overlapping task time windows (`start_time` + duration)
- Recurring task support (`daily`, `weekly`) with `next_occurrence()` rollout
- Senior age check per species (`dog`, `cat`, `rabbit`, default other)
- Reasoning output describing included/skipped tasks and total scheduled minutes


## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Testing PawPal+

Run: `python -m pytest`

This test suite covers:

- Task recurrence and next occurrence logic (`daily`/`weekly`/one-time)
- Scheduler sorting by priority and duration
- Time-slot assignment order (morning → afternoon → evening → any)
- Budget filtering (including and skipping tasks correctly)
- Conflict detection for overlapping task time windows
- `DailyPlan` task filtering and duration aggregation

Confidence Level: ⭐⭐⭐⭐⭐ (5/5) based on successful test suite execution.

