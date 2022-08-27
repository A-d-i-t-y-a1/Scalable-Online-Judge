from django.db import models

# Create your models here.
class Problems(models.Model):
    name = models.CharField(max_length=20)
    statement = models.CharField(max_length=500)
    def __str__(self):
        return self.name

class Solution(models.Model):
    problem = models.ForeignKey(Problems, on_delete=models.CASCADE)
    code = models.CharField(max_length=5000)
    verdict = models.CharField(max_length=50)
    sub_time = models.DateTimeField('date submitted')
    def __str__(self):
        return str(self.sub_time)

class TestCases(models.Model):
    problem = models.ForeignKey(Problems, on_delete=models.CASCADE)
    input = models.CharField(max_length=1000)
    output = models.CharField(max_length=1000)
    def __str__(self):
        return self.input