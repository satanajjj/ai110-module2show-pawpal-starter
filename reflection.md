# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial UML design centered around five classes connected through a clear data-flow: owner and pet info flow into a scheduler, which produces a daily plan made up of tasks.

- **`Owner`** — holds the pet owner's profile and constraints: their name, total available minutes per day, preferred time slots (morning/evening), and any free-text notes. It is a pure data container with two helper methods for retrieving the time budget and checking time-slot preferences.

- **`Pet`** — stores pet-specific information (name, species, breed, age, special needs) that may influence which tasks are appropriate. Includes `is_senior()` and `has_need()` to make pet-aware decisions easier elsewhere.

- **`Task`** — represents a single care activity. Holds the task's name, category (walk/feed/meds/grooming/enrichment), duration, priority (1–5), preferred time of day, and recurrence flag. Methods like `is_high_priority()` and `fits_in()` encapsulate task-level decisions so the scheduler doesn't repeat that logic inline.

- **`Scheduler`** — the only "smart" class. Takes an `Owner`, a `Pet`, and a list of `Task` objects and produces a `DailyPlan`. Internal helper methods handle sorting by priority, filtering to the time budget, assigning morning/afternoon/evening slots, and generating a plain-English explanation of the plan.

- **`DailyPlan`** — the output of a scheduling run. Stores the ordered list of scheduled tasks, the list of skipped tasks, total duration, and the reasoning string. Provides a `summary()` method for the UI and `get_tasks_by_time()` for rendering tasks grouped by time slot.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
