# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Features

### Scheduling Engine

- **Multi-key sorting** — `generate_plan()` sorts tasks by priority (high first), then by time-of-day (morning before evening), then by shortest duration. The result reads like a real daily routine: urgent morning tasks first, lighter evening tasks last.
- **Greedy time-budget packing** — Tasks are added to the plan in sorted order until the owner's available minutes are full. A 30-min high-priority walk beats a 60-min low-priority grooming session when time is tight.
- **Daily / weekly / monthly recurrence** — `create_next_occurrence()` uses `timedelta` to calculate the next due date when a task is completed. Daily tasks reappear tomorrow, weekly in 7 days, monthly in 30. One-time tasks (`"once"`) produce no follow-up.
- **Frequency-aware due dates** — `is_due()` checks each task's `due_date` and completion status so future recurring tasks stay out of today's plan until they are actually due.

### Conflict Detection

- **Same-pet overlap** — Flags when one pet has multiple tasks in the same time slot whose combined duration exceeds the slot budget (e.g., a 45-min walk + 30-min bath in a 60-min evening slot).
- **Cross-pet overlap** — Flags when the owner is double-booked across pets in the same slot (e.g., walking Mochi and grooming Luna both scheduled for the morning).
- **Slot overflow** — Flags when total minutes in any slot exceed the budget, regardless of which pet owns the tasks.

### Filtering and Search

- **Predicate-based filtering** — `filter_tasks()` narrows tasks by pet name, completion status (`pending`/`done`), and/or category in any combination (e.g., "show me Mochi's pending walks").

### Streamlit UI

- **Sorted plan table** — The generated schedule displays as a numbered table ordered by time slot and priority.
- **Visual conflict warnings** — Same-pet and cross-pet overlaps render as `st.warning` banners; slot overflows render as `st.error` with actionable tips for the owner.
- **Live filtering** — Dropdowns for status, category, and pet name update a filtered task table in real time.
- **Plan explainer** — An expandable section explains the sorting and packing logic behind the schedule.

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

Run the full test suite with:

```bash
python -m pytest
```

The 29 tests cover the following areas:

| Area                    | What's tested                                                                                                                              |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **Sorting correctness** | Plan returns tasks in chronological time-slot order (morning → afternoon → evening), higher priority first, shorter duration as tiebreaker |
| **Recurrence logic**    | Completing a daily task creates a new task due tomorrow; weekly/monthly offsets are correct; one-time tasks produce no follow-up           |
| **Conflict detection**  | Same-pet overlap, cross-pet overlap, and slot overflow all produce warnings; tasks within budget produce none                              |
| **Greedy packing**      | Tasks are selected by priority until the time budget is full; exact-fit, one-over, and over-budget boundaries are verified                 |
| **Filtering**           | Combined pet + status + category filters return the correct subset; nonexistent values return empty lists                                  |
| **Edge cases**          | Pet with no tasks, owner with no pets, all tasks completed, orphaned pet names, unknown time slots, and invalid filter status              |

### Confidence Level

**★★★★☆ (4 / 5)**

The test suite thoroughly covers sorting, recurrence, conflict detection, budget boundaries, and common edge cases. The missing star reflects that the tests do not yet cover the Streamlit UI layer or end-to-end integration beyond the scheduling engine.

## Demo

<img src="PawPals.png" alt="PawPal App" width="600"/>
