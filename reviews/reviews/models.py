from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


class Item(models.Model):
    name = models.CharField(max_length=20)
    item_owner = models.ForeignKey(User, models.CASCADE)
    item_description = models.CharField(max_length=100)
    rating = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )


class Comment(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    comment_owner = models.ForeignKey(User, models.CASCADE)
    text = models.CharField(max_length=200)

