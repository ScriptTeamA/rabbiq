from .models import TimeEntry
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse


class KPI():
    def __init__(self):
        self.DECAY_FACTOR = 0.95
        self.BONUS_THRESHOLD = 60
        self.BONUS_PERCENTAGE = 0.05

    def calculate_performance_rating(self,user):
        total_hours = 0
        total_rating = 0

        time_entries = TimeEntry.objects.filter(user=user).order_by('-end_time')
        if time_entries.exists():
            last_activity_time = time_entries.first().end_time
            days_since_last_activity = (timezone.now() - last_activity_time).days
        else:
            days_since_last_activity = None

        for entry in time_entries:
            hours_worked = (entry.end_time - entry.start_time).total_seconds() / 3600
            total_hours += hours_worked
            total_rating += float(entry.task.wage_per_hour) * hours_worked

        if total_hours > 0:
            average_performance = total_rating / total_hours
        else:
            average_performance = 0

        # Apply time decay to the rating based on days since last activity
        if days_since_last_activity is not None:
            decay_factor = self.DECAY_FACTOR ** days_since_last_activity
            average_performance *= decay_factor

        # Limit the rating to a maximum of 100
        average_performance = min(average_performance, 100)

        return round(average_performance,2)

    def calculate_performance_comments(self,user):
        average_performance = self.calculate_performance_rating(user)
        comments = ''

        if average_performance >= 80:
            comments = 'Great job! You are performing excellently.'
        elif average_performance >= 60:
            comments = 'Good job! Keep up the good work.'
        else:
            comments = 'You can improve your performance.'

        return comments
    
    def calculate_bonus(self, user):
        # Calculate the performance rating
        performance_rating = self.calculate_performance_rating(user)

        # Calculate the bonus amount based on the performance rating
        if performance_rating >= self.BONUS_THRESHOLD:
            bonus = performance_rating * self.BONUS_PERCENTAGE
        else:
            bonus = 0

        return bonus

    def apply_bonus_to_wage(self, user):
        # Retrieve the user's wage
        wage = user.wage

        # Calculate the bonus amount
        bonus = self.calculate_bonus(user)

        # Increase the wage by the bonus amount
        wage_with_bonus = wage + bonus

        return wage_with_bonus