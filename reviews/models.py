from django.db import models
from django.db.models.signals import post_save
from django.db.models import Sum

from user.models import Profile
from coach.models import Coach



class Review(models.Model):
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(Profile, on_delete=models.CASCADE)
    review_summary = models.TextField()
    review_description = models.TextField()
    rating = models.DecimalField(max_digits = 5,decimal_places = 1, null=True, blank=True)
    created = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ('created',)
        indexes = [models.Index(fields=['coach', 'reviewer', ])]

    def __str__(self):
        return self.review_summary


    @staticmethod
    def post_save(sender, **kwargs):
        instance = kwargs.get('instance')
        created = kwargs.get('created')

        if created:
            instance_coach = instance.coach
            # total score
            total_score = Review.objects.filter(coach=instance.coach).aggregate(Sum('rating'))['rating__sum']
            # total reviews
            total_reviews = Review.objects.filter(coach=instance.coach).count()

            # calculating average score
            instance_coach.rating = total_score / total_reviews
            instance_coach.save()


post_save.connect(Review.post_save, sender=Review)