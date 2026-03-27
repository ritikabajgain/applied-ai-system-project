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

## Smarter Scheduling

Beyond the basic priority-first planner, PawPal+ includes four algorithmic improvements:

- **Multi-key sorting** — `generate_plan()` sorts tasks by priority (high first), then by time-of-day (morning before evening), then by shortest duration. This produces a schedule that reads like a real daily routine instead of a flat priority list.
- **Predicate-based filtering** — `filter_tasks()` lets you narrow tasks by pet name, completion status, and/or category in any combination (e.g., "show me Mochi's pending walks").
- **Recurring task auto-creation** — When a daily, weekly, or monthly task is marked complete, `create_next_occurrence()` uses `timedelta` to calculate the next due date and automatically adds a new task instance to the pet. One-time tasks (`"once"`) produce no follow-up.
- **Lightweight conflict detection** — `detect_conflicts()` groups planned tasks by time slot and checks three conditions: same-pet overlap (one pet has too many tasks in a slot), cross-pet overlap (the owner is double-booked across pets), and total slot overflow. Conflicts are returned as warning strings — the program never crashes.

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
