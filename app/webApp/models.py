from django.db import models


class Book(models.Model):
    Name = models.CharField(max_length=100)
    # Number = models.BigIntegerField(blank=True, null=True, default=0)
    ISBN = models.BigIntegerField(blank=True, default=0)
    def __str__(self):
        return self.Name + str(self.ISBN)


# class Movies(models.Model):
#     file = models.FileField(upload_to='documents/', None=True)
#     image = models.ImageField(upload_to='images/', None=True)