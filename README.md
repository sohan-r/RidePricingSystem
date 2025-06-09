# Ride Pricing System
A Django REST API for calculating ride prices based on configurable pricing rules.  
It supports base pricing, time multipliers, and waiting charges per day of the week.


## 🔧 Features
- Configurable distance and waiting time charges
- Time multiplier tiers based on ride duration
- API endpoint to calculate total ride cost
- Admin interface to manage pricing configurations


## 🏗️ Build & Run Instructions

1. Clone the repository:
git remote add origin https://github.com/sohan-r/RidePricingSystem.git

2. Set up Virtual Environment
python -m venv env
env\Scripts\activate       # On Windows
or
source env/bin/activate    # On macOS/Linux

3. Install Requirements
pip install -r requirements.txt

4. Run Migrations:

python manage.py makemigrations
python manage.py migrate

5. Create Superuser:
 
python manage.py createsuperuser

6. Run the Development Server:

python manage.py runserver
Now visit http://127.0.0.1:8000/admin/ to manage pricing configs, and
http://127.0.0.1:8000/pricing/api/calculate-price/ for the API.

📬 API Usage:

POST /calculate-price/:

Example:
Request Body:
json
{
  "day_of_week": "MON",
  "total_distance_km": 5.0,
  "ride_time_minutes": 90,
  "waiting_time_minutes": 10
}

Response:
json
{
  "total_price": 140.0,
  "details": {
    "distance_price": 90.0,
    "time_charge": 50.0,
    "waiting_charge": 0.0
  }
}

🧪 Run Tests:

python manage.py test

🗂️ Tech Stack

Python 3.x
Django
Django REST Framework
SQLite (default)
