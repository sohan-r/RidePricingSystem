from django.db import models

DAYS_OF_WEEK = [
    ("MON", "Monday"),
    ("TUE", "Tuesday"),
    ("WED", "Wednesday"),
    ("THU", "Thursday"),
    ("FRI", "Friday"),
    ("SAT", "Saturday"),
    ("SUN", "Sunday"),
]

class PricingConfig(models.Model):
    day_of_week = models.CharField(max_length=3, choices=DAYS_OF_WEEK)
    is_active = models.BooleanField(default=False)
    distance_base_price = models.FloatField()
    base_distance_km = models.FloatField()
    distance_additional_price = models.FloatField()
    waiting_charge_per_unit = models.FloatField()
    waiting_unit_minutes = models.IntegerField()
    waiting_free_minutes = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return f"{self.day_of_week} - Active: {self.is_active}"

class TimeMultiplierTier(models.Model):
    pricing_config = models.ForeignKey(
        PricingConfig, 
        on_delete=models.CASCADE,
        related_name="time_multipliers"  
    )
    min_minutes = models.IntegerField()
    max_minutes = models.IntegerField()
    multiplier = models.FloatField()

    def __str__(self):
        return f"{self.min_minutes}-{self.max_minutes} mins: {self.multiplier}x"

