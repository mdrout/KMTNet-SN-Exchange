from django.db import models
import numpy as np

class Field(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)


class Quadrant(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)


class Classification(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)


class Candidate(models.Model):
    id = models.AutoField(primary_key=True)
    ra = models.FloatField()
    dec = models.FloatField()
    field_id = models.ForeignKey(Field, on_delete=models.CASCADE)
    quadrant_id = models.ForeignKey(Quadrant, on_delete=models.CASCADE)
    classification = models.ForeignKey(Classification, on_delete=models.CASCADE)

    def is_same_target(self, ra, dec):
        ra1_rad, dec1_rad = np.deg2rad([self.ra, self.dec])
        ra2_rad, dec2_rad = np.deg2rad([ra, dec])
        distance_rad = np.arccos(np.sin(dec1_rad) * np.sin(dec2_rad) + np.cos(dec1_rad) * np.cos(dec2_rad) * np.cos(ra2_rad - ra1_rad))
        return np.rad2deg(distance_rad) < (1.0 / 3600.0)

