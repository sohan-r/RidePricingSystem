from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import PricingConfig
import math

class CalculatePriceAPIView(APIView):
    def post(self, request):
        """
        Expected JSON:
        {
            "day_of_week": "MON",
            "total_distance_km": 5.0,
            "ride_time_minutes": 90,
            "waiting_time_minutes": 10
        }
        """
        data = request.data
        day = data.get('day_of_week')
        try:
            total_distance = float(data.get('total_distance_km', 0))
            ride_time = int(data.get('ride_time_minutes', 0))
            waiting_time = int(data.get('waiting_time_minutes', 0))
        except (ValueError, TypeError):
            return Response({"error": "Invalid numeric values."}, status=status.HTTP_400_BAD_REQUEST)

        if not day or total_distance < 0 or ride_time < 0 or waiting_time < 0:
            return Response({"error": "Invalid input parameters."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch pricing config
        try:
            config = PricingConfig.objects.filter(day_of_week=day, is_active=True).latest('updated_at')
        except PricingConfig.DoesNotExist:
            return Response({"error": "No active pricing config found for the day."}, status=status.HTTP_404_NOT_FOUND)

        # Distance price calculation
        base_km = config.base_distance_km
        dbp = float(config.distance_base_price)
        dap = float(config.distance_additional_price)
        additional_distance = max(0, total_distance - base_km)
        distance_price = dbp + (additional_distance * dap)

        # Time multiplier selection
        tmf = 1.0
        time_multipliers = config.time_multipliers.all().order_by('min_minutes')
        for tier in time_multipliers:
            if tier.min_minutes <= ride_time <= tier.max_minutes:
                tmf = tier.multiplier
                break
        else:
            last_tier = time_multipliers.last()
            if last_tier:
                tmf = last_tier.multiplier

        time_charge = ride_time * tmf

        # Waiting charge
        waiting_charge = 0.0
        if waiting_time > config.waiting_free_minutes:
            extra_wait = waiting_time - config.waiting_free_minutes
            chargeable_units = math.ceil(extra_wait / config.waiting_unit_minutes)
            waiting_charge = chargeable_units * float(config.waiting_charge_per_unit)

        # Final price calculation
        total_price = round(distance_price + time_charge + waiting_charge, 2)

        return Response({
            "total_price": total_price,
            "details": {
                "distance_price": round(distance_price, 2),
                "time_charge": round(time_charge, 2),
                "waiting_charge": round(waiting_charge, 2),
            }
        })
