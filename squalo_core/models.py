from django.db import models

from django.contrib.auth.models import User

from django.utils.text import slugify

class Dataspace(models.Model):
	owner = models.ForeignKey(User, related_name="dataspaces")
	name = models.CharField(max_length=100)
	sqlite_file = models.FileField()

	geo = models.BooleanField(default=False)
	def __str__(self):
		return self.name

class Model(models.Model):
	dataspace = models.ForeignKey(Dataspace, related_name="models")
	name = models.CharField(max_length=255)

	internal=models.BooleanField(default=False)

	def __str__(self):
		return self.name

class Field(models.Model):
	model = models.ForeignKey(Model, related_name='fields')
	name = models.CharField(max_length=255)

	geo = models.BooleanField(default=False)

	def __str__(self):
		return self.name


