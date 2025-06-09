from django.test import TestCase
from pricing.models import PricingConfig, TimeMultiplierTier
from django.contrib.auth.models import User

class PricingCalculationTest(TestCase):
    def setUp(self):
        # Create test pricing config for Monday
        self.config = PricingConfig.objects.create(
            day_of_week="MON",
            is_active=True,
            distance_base_price=90,       # base price up to base_distance_km
            base_distance_km=3.5,
            distance_additional_price=30, # per km beyond base_distance_km
            waiting_charge_per_unit=5,    # charge per waiting unit
            waiting_unit_minutes=3,       # waiting unit length in minutes
            waiting_free_minutes=3,       # free waiting minutes
        )

        # Create TimeMultiplierTier linked to this config
        TimeMultiplierTier.objects.create(
            pricing_config=self.config,
            min_minutes=0,
            max_minutes=60,
            multiplier=1
        )
        TimeMultiplierTier.objects.create(
            pricing_config=self.config,
            min_minutes=61,
            max_minutes=120,
            multiplier=1.25
        )
        TimeMultiplierTier.objects.create(
            pricing_config=self.config,
            min_minutes=121,
            max_minutes=180,
            multiplier=2.2
        )

    def test_base_price_only(self):
        # No additional distance, waiting, or multiplier > 1
        km = 3.0
        ride_time = 50
        waiting = 2

        base_price = self.config.distance_base_price  # 90
        additional_charge = 0
        time_multiplier = 1  # under 60 mins
        waiting_charge = 0

        subtotal = base_price + additional_charge
        total_price = subtotal * time_multiplier + waiting_charge

        self.assertAlmostEqual(total_price, 90)

    def test_with_additional_distance(self):
        # Additional 2 km beyond base distance (5.5 - 3.5)
        km = 5.5
        ride_time = 50
        waiting = 2

        base_price = self.config.distance_base_price  # 90
        additional_km = km - self.config.base_distance_km  # 2.0
        additional_charge = additional_km * self.config.distance_additional_price  # 60
        time_multiplier = 1
        waiting_charge = 0

        subtotal = base_price + additional_charge
        total_price = subtotal * time_multiplier + waiting_charge

        self.assertAlmostEqual(total_price, 150)

    def test_with_time_multiplier(self):
        km = 5.5
        ride_time = 75  # falls in 61-120 mins bracket -> multiplier 1.25
        waiting = 2

        base_price = self.config.distance_base_price  # 90
        additional_km = km - self.config.base_distance_km  # 2.0
        additional_charge = additional_km * self.config.distance_additional_price  # 60
        subtotal = base_price + additional_charge  # 150

        # Find multiplier based on ride_time
        multiplier_tier = TimeMultiplierTier.objects.filter(
            pricing_config=self.config,
            min_minutes__lte=ride_time,
            max_minutes__gte=ride_time
        ).first()
        time_multiplier = multiplier_tier.multiplier if multiplier_tier else 1

        total_price = subtotal * time_multiplier

        self.assertAlmostEqual(total_price, 187.5)

    def test_with_waiting_charge(self):
        km = 3.0
        ride_time = 50
        waiting = 9  # 6 minutes beyond free waiting (3 min free)

        base_price = self.config.distance_base_price  # 90
        additional_charge = 0

        free_wait = self.config.waiting_free_minutes  # 3
        waiting_time_chargeable = max(0, waiting - free_wait)  # 6
        unit = self.config.waiting_unit_minutes  # 3
        units = (waiting_time_chargeable + unit - 1) // unit  # ceiling division = 2
        waiting_charge = units * self.config.waiting_charge_per_unit  # 10

        subtotal = base_price + additional_charge
        total_price = subtotal + waiting_charge

        self.assertAlmostEqual(total_price, 100)

    def test_full_combination(self):
        km = 6.5
        ride_time = 125  # falls in 121-180 mins bracket -> multiplier 2.2
        waiting = 10     # 7 min chargeable waiting (10-3)

        base_price = self.config.distance_base_price  # 90
        additional_km = km - self.config.base_distance_km  # 3.0
        additional_charge = additional_km * self.config.distance_additional_price  # 90
        subtotal = base_price + additional_charge  # 180

        # Get multiplier for ride_time
        multiplier_tier = TimeMultiplierTier.objects.filter(
            pricing_config=self.config,
            min_minutes__lte=ride_time,
            max_minutes__gte=ride_time
        ).first()
        time_multiplier = multiplier_tier.multiplier if multiplier_tier else 1

        time_charge = subtotal * (time_multiplier - 1)  # 180 * 1.2 = 216

        free_wait = self.config.waiting_free_minutes  # 3
        waiting_time_chargeable = max(0, waiting - free_wait)  # 7
        unit = self.config.waiting_unit_minutes  # 3
        units = (waiting_time_chargeable + unit - 1) // unit  # ceiling div = 3 units
        waiting_charge = units * self.config.waiting_charge_per_unit  # 15

        total_price = subtotal + time_charge + waiting_charge  # 180 + 216 + 15 = 411

        self.assertAlmostEqual(total_price, 411)
