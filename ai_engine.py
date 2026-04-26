from collections import defaultdict


class AIEngine:
    """Generates natural-language insights for tasks and schedules."""

    _CATEGORY_IMPORTANCE = {
        "walk":        "Regular walks keep energy levels balanced and support joint health.",
        "feeding":     "Consistent feeding times regulate digestion and prevent anxiety.",
        "grooming":    "Grooming prevents matting, skin issues, and keeps your pet comfortable.",
        "enrichment":  "Mental stimulation reduces boredom and destructive behaviour.",
        "medical":     "Medical care catches problems early and maintains long-term wellbeing.",
        "other":       "Routine care reinforces trust and strengthens your bond.",
    }

    _PRIORITY_PHRASES = {
        "high":   "This is a high-priority task that should not be skipped today.",
        "medium": "This is a moderately important task worth fitting in when possible.",
        "low":    "This is a low-priority task — helpful, but flexible if time is tight.",
    }

    _SLOT_PHRASES = {
        "morning":   "Starting it in the morning sets a positive tone for the rest of the day.",
        "afternoon": "The afternoon slot gives your pet midday activity and attention.",
        "evening":   "An evening slot helps your pet wind down and settle for the night.",
    }

    def explain_task(self, task) -> str:
        """Return a 1–2 sentence user-friendly explanation for a single task."""
        importance = self._CATEGORY_IMPORTANCE.get(
            task.category, "This task contributes to your pet's overall wellbeing."
        )
        slot_note = self._SLOT_PHRASES.get(task.preferred_time, "")
        return f"{importance} {slot_note}".strip()

    def explain_schedule(self, plan) -> str:
        """Return a short paragraph explaining how the schedule was built."""
        if not plan:
            return "No tasks were scheduled."

        total_min = sum(t.duration_minutes for t in plan)
        pet_names = sorted({t.pet_name for t in plan})
        pets_str = ", ".join(pet_names) if pet_names else "your pet"

        high = [t for t in plan if t.priority == "high"]
        medium = [t for t in plan if t.priority == "medium"]
        low = [t for t in plan if t.priority == "low"]

        priority_parts = []
        if high:
            priority_parts.append(
                f"{len(high)} high-priority task(s) ({', '.join(t.title for t in high)})"
            )
        if medium:
            priority_parts.append(f"{len(medium)} medium-priority task(s)")
        if low:
            priority_parts.append(f"{len(low)} low-priority task(s)")

        priority_sentence = (
            "Tasks were ranked by urgency: " + ", then ".join(priority_parts) + "."
            if priority_parts else ""
        )

        slot_groups = defaultdict(list)
        for t in plan:
            slot_groups[t.preferred_time].append(t)

        slot_parts = []
        for slot in ["morning", "afternoon", "evening"]:
            if slot in slot_groups:
                slot_parts.append(
                    f"{len(slot_groups[slot])} task(s) in the {slot}"
                )
        time_sentence = (
            "Time constraints shaped the order: " + ", ".join(slot_parts) + f", "
            f"totalling {total_min} minutes across {len(pet_names)} pet(s) ({pets_str})."
            if slot_parts else ""
        )

        return f"{priority_sentence} {time_sentence}".strip()
