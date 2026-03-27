from pawpal_system import Owner, Pet, Task, Scheduler

# Create an owner with 90 minutes available
owner = Owner("Jordan", time_available=90)

# Create two pets and register them with the owner
mochi = Pet("Mochi", species="dog", age=3)
owner.add_pet(mochi)

luna = Pet("Luna", species="cat", age=5)
owner.add_pet(luna)

# Add tasks to Mochi
mochi.add_task(Task("Morning walk", duration_minutes=30, priority="high", category="walk"))
mochi.add_task(Task("Brush fur", duration_minutes=15, priority="low", category="grooming"))

# Add tasks to Luna
luna.add_task(Task("Feed Luna", duration_minutes=10, priority="high", category="feeding"))
luna.add_task(Task("Play with feather toy", duration_minutes=20, priority="medium", category="enrichment"))
luna.add_task(Task("Administer flea meds", duration_minutes=5, priority="high", category="meds"))

# Generate and print the schedule
scheduler = Scheduler(owner)
scheduler.generate_plan()
print(scheduler.explain_plan())
