from .models import Tasks, UserTasks

def assign_hidden_tasks(user_profile):
    # Map user profile attributes to task demographic keys
    demographic_mapping = {
        'is_expat': 'EXPAT',
        'is_student': 'STUDENT',
        'is_sports_traveler': 'SPORTS',
        'is_festival_traveler': 'FESTIVAL',
    }

    # Pre-fetch all tasks to minimize database hits.
    hidden_tasks = Tasks.objects.filter(is_hidden=True)

    # Iterate over the demographic mapping
    for profile_attr, task_demographic in demographic_mapping.items():
        if getattr(user_profile, profile_attr, False):
            # Retrieve tasks for the demographic
            demographic_tasks = hidden_tasks.filter(target_demographic=task_demographic)
            # Create user tasks if they don't exist
            for task in demographic_tasks:
                UserTasks.objects.get_or_create(user=user_profile.user, task=task)