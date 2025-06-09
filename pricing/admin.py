from django.contrib import admin
from .models import PricingConfig, TimeMultiplierTier

class TimeMultiplierTierInline(admin.TabularInline):
    model = TimeMultiplierTier
    extra = 1

@admin.register(PricingConfig)
class PricingConfigAdmin(admin.ModelAdmin):
    inlines = [TimeMultiplierTierInline]
