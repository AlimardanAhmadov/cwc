from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Profile
import datetime

User = get_user_model()


class ProfileTestCase(TestCase):
    def setUp(self):
        start_time = datetime.datetime.now()
        profiles = []
        batch_size = 500
        for i in range(10000):
            user = User.objects.create(username=f"UserName{i}", email=f"user@gmail.com{i}")
            profile = Profile()
            profile.user = user
            profile.full_name = str(i)
            profile.about = f"code{i}"
            profile.phone_number = f"code{i}"
            profiles.append(profile)
        Profile.objects.bulk_create(profiles, batch_size)

        end_time = datetime.datetime.now()
        print(f" Created in {end_time - start_time}")

    def test_lookup(self):
        start_time = datetime.datetime.now()
        for i in range(50000, 51000):
            Profile.objects.filter(user=1)

        end_time = datetime.datetime.now()
        print(f"Looked up in {end_time - start_time}")
        