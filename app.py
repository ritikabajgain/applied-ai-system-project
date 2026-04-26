import streamlit as st
from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler
from ai_engine import AIEngine
from retriever import PetCareRetriever

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ── Custom CSS: light pet-friendly theme + animations ───────────

st.markdown("""
<style>
/* ── Bouncing paw header animation ─────────────────────────── */
@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50%      { transform: translateY(-8px); }
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes wiggle {
    0%, 100% { transform: rotate(0deg); }
    25%      { transform: rotate(-5deg); }
    75%      { transform: rotate(5deg); }
}
@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50%      { transform: scale(1.05); }
}

/* Header banner */
.paw-header {
    text-align: center;
    padding: 1.5rem 1rem;
    background: linear-gradient(135deg, #FFF0E0 0%, #FFE0CC 50%, #FFD6E0 100%);
    border-radius: 16px;
    margin-bottom: 1.5rem;
    animation: fadeInUp 0.6s ease-out;
    border: 2px solid #FFD0B0;
}
.paw-header h1 {
    margin: 0;
    font-size: 2.4rem;
    color: #3D2C2C;
}
.paw-header .paw-icon {
    font-size: 2.8rem;
    display: inline-block;
    animation: bounce 1.5s ease-in-out infinite;
}
.paw-header p {
    margin: 0.3rem 0 0 0;
    color: #7A5C5C;
    font-size: 1.05rem;
}

/* Section headers with pet emojis */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.6rem 0;
    animation: fadeInUp 0.5s ease-out;
}
.section-header .emoji {
    font-size: 1.5rem;
    display: inline-block;
    animation: wiggle 2s ease-in-out infinite;
}

/* Styled cards for pet overview */
.pet-card {
    background: linear-gradient(135deg, #FFFFFF, #FFF5EB);
    border: 2px solid #FFD0B0;
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 0.8rem;
    animation: fadeInUp 0.4s ease-out;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.pet-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(255, 107, 107, 0.15);
}

/* Softer buttons */
.stButton > button {
    border-radius: 20px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: scale(1.03) !important;
    box-shadow: 0 3px 10px rgba(255, 107, 107, 0.25) !important;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px 10px 0 0 !important;
    font-weight: 600 !important;
}

/* Table styling */
.stTable {
    animation: fadeInUp 0.4s ease-out;
}

/* Metrics pulse on hover */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #FFFFFF, #FFF8F0);
    border: 1px solid #FFE0CC;
    border-radius: 10px;
    padding: 0.8rem;
    transition: transform 0.2s ease;
}
[data-testid="stMetric"]:hover {
    animation: pulse 0.6s ease-in-out;
}

/* Divider color */
hr {
    border-color: #FFD0B0 !important;
}

/* Success/warning/error animations */
.stAlert {
    animation: fadeInUp 0.4s ease-out;
    border-radius: 10px !important;
}

/* Footer paw prints */
.paw-footer {
    text-align: center;
    padding: 1rem;
    margin-top: 2rem;
    color: #C4A48A;
    font-size: 1.3rem;
    letter-spacing: 0.4rem;
    animation: fadeInUp 0.6s ease-out;
}
</style>
""", unsafe_allow_html=True)

# ── Animated header ─────────────────────────────────────────────

st.markdown("""
<div class="paw-header">
    <div><span class="paw-icon">🐾</span></div>
    <h1>PawPal+</h1>
    <p>Your happy pet care planner - schedule, sort & stay on track!</p>
</div>
""", unsafe_allow_html=True)

# ── Session state initialisation ────────────────────────────────

if "pets" not in st.session_state:
    st.session_state.pets = []
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# ═══════════════════════════════════════════════════════════════
# SETUP — Owner + Pets  (always visible, compact)
# ═══════════════════════════════════════════════════════════════

st.markdown('<div class="section-header"><span class="emoji">🏠</span><h3>Setup</h3></div>', unsafe_allow_html=True)

owner_name = st.text_input("Owner name", value="Jordan")
time_available = st.number_input(
    "Available time (minutes)", min_value=10, max_value=480, value=120
)

with st.expander("Manage Pets"):
    pcol1, pcol2, pcol3 = st.columns(3)
    with pcol1:
        new_pet_name = st.text_input("Pet name", value="Mochi")
    with pcol2:
        new_pet_species = st.selectbox("Species", ["dog", "cat", "other"])
    with pcol3:
        new_pet_age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)

    if st.button("🐶 Add pet"):
        if any(p["name"] == new_pet_name for p in st.session_state.pets):
            st.warning(f"A pet named **{new_pet_name}** already exists.")
        else:
            st.session_state.pets.append(
                {"name": new_pet_name, "species": new_pet_species, "age": new_pet_age}
            )
            st.rerun()

    if st.session_state.pets:
        st.table(st.session_state.pets)
    else:
        st.info("No pets yet. Add one above.")

# ── Rebuild backend objects from session state ──────────────────

owner = Owner(owner_name, time_available)

pet_objects = {}
for p in st.session_state.pets:
    pet_obj = Pet(p["name"], p["species"], p["age"])
    owner.add_pet(pet_obj)
    pet_objects[p["name"]] = pet_obj

task_objects = []
for t in st.session_state.tasks:
    task_obj = Task(
        t["title"], t["duration"], t["priority"],
        category=t["category"], frequency=t["frequency"],
        preferred_time=t["time_slot"],
    )
    if t["completed"]:
        task_obj.mark_complete()
    if t["pet"] in pet_objects:
        pet_objects[t["pet"]].add_task(task_obj)
    task_objects.append(task_obj)

scheduler = Scheduler(owner)

# ═══════════════════════════════════════════════════════════════
# MANAGE TASKS — single expander with tabs inside
# ═══════════════════════════════════════════════════════════════

st.divider()
st.markdown('<div class="section-header"><span class="emoji">📋</span><h3>Manage Tasks</h3></div>', unsafe_allow_html=True)

if not st.session_state.pets:
    st.info("Add a pet first, then you can manage tasks.")
else:
    # Show the task summary table above the tabs (always visible)
    if st.session_state.tasks:
        st.table(
            [
                {
                    "Pet": t["pet"],
                    "Task": t["title"],
                    "Duration": f'{t["duration"]} min',
                    "Priority": t["priority"].capitalize(),
                    "Category": t["category"],
                    "Slot": t["time_slot"].capitalize(),
                    "Freq": t["frequency"].capitalize(),
                    "Status": "Done" if t["completed"] else "Pending",
                }
                for t in st.session_state.tasks
            ]
        )

    tab_add, tab_complete, tab_edit, tab_remove = st.tabs(
        ["➕ Add Task", "✅ Mark Complete", "✏️ Edit Task", "🗑️ Remove Task"]
    )

    pet_names = [p["name"] for p in st.session_state.pets]

    # ── Tab 1: Add Task ─────────────────────────────────────────
    with tab_add:
        acol1, acol2 = st.columns(2)
        with acol1:
            task_pet = st.selectbox("Assign to pet", pet_names, key="add_pet")
            task_title = st.text_input("Task title", value="Morning walk")
            task_category = st.selectbox(
                "Category", ["walk", "feeding", "grooming", "enrichment", "medical", "other"]
            )
        with acol2:
            task_duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
            task_priority = st.selectbox("Priority", ["high", "medium", "low"])
            task_frequency = st.selectbox("Frequency", ["daily", "weekly", "biweekly", "monthly", "once"])

        task_time_slot = st.selectbox("Preferred time of day", ["morning", "afternoon", "evening"])

        if st.button("➕ Add task"):
            st.session_state.tasks.append(
                {
                    "pet": task_pet,
                    "title": task_title,
                    "duration": int(task_duration),
                    "priority": task_priority,
                    "category": task_category,
                    "frequency": task_frequency,
                    "time_slot": task_time_slot,
                    "completed": False,
                }
            )
            st.rerun()

    # ── Tab 2: Mark Complete / Incomplete ────────────────────────
    with tab_complete:
        if not st.session_state.tasks:
            st.info("No tasks yet.")
        else:
            st.caption("Completing a recurring task automatically creates the next occurrence.")

            pending_indices = [i for i, t in enumerate(st.session_state.tasks) if not t["completed"]]
            done_indices = [i for i, t in enumerate(st.session_state.tasks) if t["completed"]]

            ccol1, ccol2 = st.columns(2)

            with ccol1:
                st.markdown("**Complete a task**")
                if pending_indices:
                    pending_labels = [
                        f'{st.session_state.tasks[i]["title"]} ({st.session_state.tasks[i]["pet"]})'
                        for i in pending_indices
                    ]
                    selected_complete = st.selectbox("Select task", pending_labels, key="sel_complete")
                    if st.button("✅ Mark complete"):
                        idx = pending_indices[pending_labels.index(selected_complete)]
                        t = st.session_state.tasks[idx]
                        t["completed"] = True

                        if t["frequency"] != "once":
                            freq_days = {"daily": 1, "weekly": 7, "biweekly": 14, "monthly": 30}
                            interval = freq_days.get(t["frequency"], 1)
                            st.session_state.tasks.append(
                                {
                                    "pet": t["pet"],
                                    "title": t["title"],
                                    "duration": t["duration"],
                                    "priority": t["priority"],
                                    "category": t["category"],
                                    "frequency": t["frequency"],
                                    "time_slot": t["time_slot"],
                                    "completed": False,
                                }
                            )
                            st.toast(
                                f"Next **{t['title']}** created for "
                                f"{(date.today() + timedelta(days=interval)).strftime('%b %d')}."
                            )
                        st.rerun()
                else:
                    st.info("No pending tasks.")

            with ccol2:
                st.markdown("**Undo a completion**")
                if done_indices:
                    done_labels = [
                        f'{st.session_state.tasks[i]["title"]} ({st.session_state.tasks[i]["pet"]})'
                        for i in done_indices
                    ]
                    selected_undo = st.selectbox("Select task", done_labels, key="sel_undo")
                    if st.button("↩️ Mark incomplete"):
                        idx = done_indices[done_labels.index(selected_undo)]
                        st.session_state.tasks[idx]["completed"] = False
                        st.rerun()
                else:
                    st.info("No completed tasks.")

    # ── Tab 3: Edit Task ────────────────────────────────────────
    with tab_edit:
        if not st.session_state.tasks:
            st.info("No tasks to edit.")
        else:
            edit_labels = [
                f'{t["title"]} ({t["pet"]})' for t in st.session_state.tasks
            ]
            selected_edit = st.selectbox("Select task to edit", edit_labels, key="sel_edit")
            edit_idx = edit_labels.index(selected_edit)
            current = st.session_state.tasks[edit_idx]

            ecol1, ecol2, ecol3 = st.columns(3)
            with ecol1:
                new_title = st.text_input("New title", value=current["title"], key="edit_title")
            with ecol2:
                new_duration = st.number_input(
                    "New duration (min)", min_value=1, max_value=240,
                    value=current["duration"], key="edit_dur",
                )
            with ecol3:
                pri_options = ["high", "medium", "low"]
                new_priority = st.selectbox(
                    "New priority", pri_options,
                    index=pri_options.index(current["priority"]), key="edit_pri",
                )

            if st.button("💾 Save edit"):
                st.session_state.tasks[edit_idx]["title"] = new_title
                st.session_state.tasks[edit_idx]["duration"] = int(new_duration)
                st.session_state.tasks[edit_idx]["priority"] = new_priority
                st.rerun()

    # ── Tab 4: Remove Task ──────────────────────────────────────
    with tab_remove:
        if not st.session_state.tasks:
            st.info("No tasks to remove.")
        else:
            remove_labels = [
                f'{t["title"]} ({t["pet"]})' for t in st.session_state.tasks
            ]
            selected_remove = st.selectbox("Select task to remove", remove_labels, key="sel_remove")
            if st.button("🗑️ Remove task"):
                remove_idx = remove_labels.index(selected_remove)
                st.session_state.tasks.pop(remove_idx)
                st.rerun()

# ═══════════════════════════════════════════════════════════════
# FILTER TASKS  (Scheduler.filter_tasks)
# ═══════════════════════════════════════════════════════════════

st.divider()
st.markdown('<div class="section-header"><span class="emoji">🔍</span><h3>Filter Tasks</h3></div>', unsafe_allow_html=True)

if st.session_state.tasks:
    pet_filter_options = ["all"] + [p["name"] for p in st.session_state.pets]

    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        filter_pet = st.selectbox("Pet", pet_filter_options, key="filter_pet")
    with fcol2:
        filter_status = st.selectbox("Status", ["all", "pending", "done"], key="filter_status")
    with fcol3:
        filter_category = st.selectbox(
            "Category",
            ["all", "walk", "feeding", "grooming", "enrichment", "medical", "other"],
            key="filter_cat",
        )

    filtered = scheduler.filter_tasks(
        pet_name=filter_pet if filter_pet != "all" else None,
        status=filter_status if filter_status != "all" else None,
        category=filter_category if filter_category != "all" else None,
    )

    if filtered:
        st.table(
            [
                {
                    "Pet": t.pet_name,
                    "Task": t.title,
                    "Duration": f"{t.duration_minutes} min",
                    "Priority": t.priority.capitalize(),
                    "Category": t.category,
                    "Slot": t.preferred_time.capitalize(),
                    "Status": "Done" if t.completed else "Pending",
                }
                for t in filtered
            ]
        )
    else:
        st.info("No tasks match the current filters.")
else:
    st.info("Add tasks to use filtering.")

# ═══════════════════════════════════════════════════════════════
# BUILD SCHEDULE  (generate_plan, detect_conflicts, explain_plan)
# ═══════════════════════════════════════════════════════════════

st.divider()
st.markdown('<div class="section-header"><span class="emoji">📅</span><h3>Build Schedule</h3></div>', unsafe_allow_html=True)
st.caption("Generates a priority-sorted schedule that fits within your available time.")

if st.button("🗓️ Generate schedule"):
    all_tasks = owner.get_all_tasks()
    due_tasks = [t for t in all_tasks if t.is_due()]

    if not due_tasks:
        st.warning("No due tasks to schedule. Add tasks or check that they aren't all completed.")
    else:
        plan = scheduler.generate_plan()

        if not plan:
            st.warning("No tasks could fit within the available time. Try increasing your available minutes.")
        else:
            st.balloons()
            total = scheduler.get_total_planned_time()
            remaining = scheduler.get_remaining_time()
            st.success(
                f"Schedule ready — **{len(plan)} task(s)** across "
                f"**{len({t.pet_name for t in plan})} pet(s)**, "
                f"**{total}/{scheduler.available_time} min** used, "
                f"**{remaining} min** remaining."
            )

            confidence = scheduler.compute_confidence(plan, due_tasks)
            st.metric(
                label="🤖 AI Confidence Score",
                value=f"{confidence:.2f}",
                help="Coverage of due tasks + time utilisation + absence of conflicts, averaged to a 0–1 score.",
            )

            st.markdown("#### Daily Plan (sorted: priority > time slot > duration)")
            st.table(
                [
                    {
                        "#": i,
                        "Slot": t.preferred_time.capitalize(),
                        "Task": t.title,
                        "Pet": t.pet_name,
                        "Duration": f"{t.duration_minutes} min",
                        "Priority": t.priority.capitalize(),
                        "Frequency": t.frequency.capitalize(),
                    }
                    for i, t in enumerate(plan, 1)
                ]
            )

            skipped = [t for t in due_tasks if t not in plan]
            if skipped:
                st.markdown("#### Skipped Tasks")
                st.caption("Due today but didn't fit in the time budget.")
                st.table(
                    [
                        {
                            "Task": t.title,
                            "Pet": t.pet_name,
                            "Duration": f"{t.duration_minutes} min",
                            "Priority": t.priority.capitalize(),
                        }
                        for t in skipped
                    ]
                )

            warnings = scheduler.detect_conflicts()
            if warnings:
                st.markdown("#### Schedule Warnings")
                for w in warnings:
                    if "[Same-pet overlap]" in w:
                        st.warning(f"🐾 **Same-pet overlap** — {w.split('] ', 1)[1]}")
                    elif "[Cross-pet overlap]" in w:
                        st.warning(f"🙌 **Cross-pet overlap** — {w.split('] ', 1)[1]}")
                    elif "[Slot overflow]" in w:
                        st.error(f"⏰ **Slot overflow** — {w.split('] ', 1)[1]}")
                    else:
                        st.warning(w)
                st.info(
                    "**Tip:** Try moving a task to a different time slot, "
                    "shortening its duration, or increasing your available time."
                )
            else:
                st.success("No scheduling conflicts detected.")

            with st.expander("How was this plan built?"):
                st.markdown(
                    "Tasks are sorted by **priority** (high first), then by "
                    "**time of day** (morning before evening), then **shortest first**. "
                    "The scheduler packs tasks greedily until the time budget is "
                    "full. Recurring tasks only appear when due."
                )

            st.divider()
            st.markdown('<div class="section-header"><span class="emoji">🧠</span><h3>AI Insights</h3></div>', unsafe_allow_html=True)

            ai = AIEngine()
            for task in plan:
                st.markdown(f"**{task.title}** *(for {task.pet_name})*")
                st.caption(ai.explain_task(task))

            with st.expander("Why was this schedule built this way?"):
                st.markdown(ai.explain_schedule(plan))

# ═══════════════════════════════════════════════════════════════
# PET OVERVIEW  (Pet.get_info)
# ═══════════════════════════════════════════════════════════════

st.divider()
st.markdown('<div class="section-header"><span class="emoji">🐕</span><h3>Pet Overview</h3></div>', unsafe_allow_html=True)

if st.session_state.pets:
    for p_name, p_obj in pet_objects.items():
        with st.expander(f"{p_obj.name} ({p_obj.species}, {p_obj.age} yrs)"):
            info = p_obj.get_info()
            icol1, icol2, icol3 = st.columns(3)
            icol1.metric("Total tasks", info["total_tasks"])
            icol2.metric("Pending", info["pending_tasks"])
            icol3.metric("Completed", info["total_tasks"] - info["pending_tasks"])

            pet_tasks = [t for t in st.session_state.tasks if t["pet"] == p_name]
            if pet_tasks:
                st.table(
                    [
                        {
                            "Task": t["title"],
                            "Duration": f'{t["duration"]} min',
                            "Priority": t["priority"].capitalize(),
                            "Slot": t["time_slot"].capitalize(),
                            "Status": "Done" if t["completed"] else "Pending",
                        }
                        for t in pet_tasks
                    ]
                )
else:
    st.info("Add pets above to see their overview here.")

# ═══════════════════════════════════════════════════════════════
# ASK PAWPAL AI  (RAG — keyword retrieval over pet_knowledge.json)
# ═══════════════════════════════════════════════════════════════

st.divider()
st.markdown('<div class="section-header"><span class="emoji">🐾</span><h3>Ask PawPal AI</h3></div>', unsafe_allow_html=True)
st.caption("Ask anything about pet care — feeding, walking, grooming, enrichment, and more.")

rag_query = st.text_input("Your question", placeholder="e.g. How often should I brush my dog?", key="rag_query")

if rag_query.strip():
    retriever = PetCareRetriever()
    results = retriever.retrieve(rag_query)
    if results:
        for tip in results:
            st.info(tip["tip"])
    else:
        st.warning("No matching tips found. Try rephrasing your question (e.g. 'dog walk', 'cat grooming', 'feeding schedule').")

# ── Footer ──────────────────────────────────────────────────────

st.markdown("""
<div class="paw-footer">
    🐾 &bull; 🐾 &bull; 🐾 &bull; 🐾 &bull; 🐾
    <br>
    <span style="font-size: 0.8rem; letter-spacing: normal;">
        Made with love for happy pets everywhere
    </span>
</div>
""", unsafe_allow_html=True)
