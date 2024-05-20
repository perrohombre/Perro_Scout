from django.db import models

class League(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'leagues'

class Club(models.Model):
    name = models.CharField(max_length=255)
    league = models.ForeignKey(League, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'clubs'

class Player(models.Model):
    name = models.CharField(max_length=255)
    position = models.CharField(max_length=255, null=True, blank=True)
    nationality = models.CharField(max_length=255, null=True, blank=True)
    born = models.IntegerField(null=True, blank=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'players'

class Season(models.Model):
    season = models.CharField(max_length=255)

    class Meta:
        db_table = 'seasons'

# Dodaj pozostałe modele analogicznie...
