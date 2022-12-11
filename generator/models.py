from django.db import models


#
# Model to hold randomized game data.
# Holds ID, game settings, and game configuration.
#
class Game(models.Model):
    share_id = models.CharField(max_length=15)
    settings = models.BinaryField()
    race_seed = models.BooleanField(default=False)
    configuration = models.BinaryField()
    creation_date = models.DateTimeField(auto_now=True)
    seed_nonce = models.CharField(max_length=15, blank=True, default='')

