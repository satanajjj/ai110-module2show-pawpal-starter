import streamlit as st
from pawpal_system import Pet, Owner, Task, Scheduler, DailyPlan

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# --- Session state initialization ---
if "owner" not in st.session_state:
    st.session_state.owner = None

if "pet" not in st.session_state:
    st.session_state.pet = None

# ------------------------------------------------------------------ #
# SECTION 1 — Owner setup
# ------------------------------------------------------------------ #
st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
with col2:
    budget = st.number_input("Available minutes per day", min_value=10, max_value=480, value=90)

if st.button("Save Owner"):
    st.session_state.owner = Owner(
        name=owner_name,
        available_minutes_per_day=int(budget),
    )
    st.success(f"Owner '{owner_name}' saved ({budget} min/day).")

st.divider()

# ------------------------------------------------------------------ #
# SECTION 2 — Pet setup
# ------------------------------------------------------------------ #
st.subheader("Pet")
col1, col2, col3, col4 = st.columns(4)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "rabbit", "other"])
with col3:
    breed = st.text_input("Breed", value="Mixed")
with col4:
    age = st.number_input("Age (years)", min_value=0.0, max_value=30.0, value=3.0, step=0.5)

if st.button("Save Pet"):
    st.session_state.pet = Pet(
        name=pet_name,
        species=species,
        breed=breed,
        age_years=float(age),
    )
    st.success(f"Pet '{pet_name}' saved. Senior: {st.session_state.pet.is_senior()}")

st.divider()

# ------------------------------------------------------------------ #
# SECTION 3 — Add a Task
# ------------------------------------------------------------------ #
st.subheader("Tasks")

_PRIORITY_MAP = {"low": 1, "medium": 3, "high": 5}
col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
with col3:
    time_slot = st.selectbox("Time", ["morning", "afternoon", "evening", "any"])
with col4:
    priority_label = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add Task"):
    if st.session_state.pet is None:
        st.warning("Save a pet first before adding tasks.")
    else:
        task_id = f"t{len(st.session_state.pet.tasks) + 1}"
        new_task = Task(
            task_id=task_id,
            name=task_title,
            category="general",
            duration_minutes=int(duration),
            priority=_PRIORITY_MAP[priority_label],
            preferred_time=time_slot,
        )
        st.session_state.pet.add_task(new_task)
        st.success(f"Task '{task_title}' added to {st.session_state.pet.name}.")

if st.session_state.pet and st.session_state.pet.tasks:
    st.write(f"Tasks for **{st.session_state.pet.name}**:")
    st.table([
        {
            "Task": t.name,
            "Time": t.preferred_time,
            "Duration (min)": t.duration_minutes,
            "Priority": t.priority,
        }
        for t in st.session_state.pet.tasks
    ])
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# ------------------------------------------------------------------ #
# SECTION 4 — Generate Schedule
# ------------------------------------------------------------------ #
st.subheader("Build Schedule")

if st.button("Generate Schedule"):
    if st.session_state.owner is None:
        st.warning("Save an owner first.")
    elif st.session_state.pet is None:
        st.warning("Save a pet first.")
    elif not st.session_state.pet.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(
            owner=st.session_state.owner,
            pet=st.session_state.pet,
            tasks=st.session_state.pet.tasks,
        )
        plan = scheduler.generate_plan()

        st.success(f"Schedule for **{plan.pet_name}** — {plan.total_duration_minutes} min total")

        for slot in ("morning", "afternoon", "evening", "any"):
            slot_tasks = [t for t in plan.scheduled_tasks if t.preferred_time == slot]
            if slot_tasks:
                st.markdown(f"**{slot.capitalize()}**")
                for t in slot_tasks:
                    st.markdown(f"- {t.name} ({t.duration_minutes} min, priority {t.priority})")

        if plan.skipped_tasks:
            st.warning("Skipped (over budget): " + ", ".join(t.name for t in plan.skipped_tasks))

        if plan.reasoning:
            st.info(plan.reasoning)
