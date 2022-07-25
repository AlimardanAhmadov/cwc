from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Coach
import datetime

User = get_user_model()


class CoachTestCase(TestCase):
    def setUp(self):
        start_time = datetime.datetime.now()
        coaches = []
        batch_size = 500
        for i in range(10000):
            user = User.objects.create(username=f"UserName{i}", email=f"user@gmail.com{i}")
            coach = Coach()
            coach.user = user
            coach.full_name = str(i)
            coach.location = f"code{i}"
            coach.location = f"code{i}"
            coach.address = f"code{i}"
            coach.timing = f"code{i}"
            coach.category = f"code{i}"
            coach.available_days = f"code{i}"
            coach.phone_number = f"code{i}"
            coach.phone_number = f"code{i}"
            coaches.append(coach)
        Coach.objects.bulk_create(coaches, batch_size)

        end_time = datetime.datetime.now()
        print(f" Created in {end_time - start_time}")

    def test_lookup(self):
        start_time = datetime.datetime.now()
        for i in range(50000, 51000):
            Coach.objects.filter(location=f"code0{i%2}")

        end_time = datetime.datetime.now()
        print(f"Looked up in {end_time - start_time}")
