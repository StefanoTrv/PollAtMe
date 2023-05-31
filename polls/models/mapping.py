import string
import random

from django.db import models

from .poll import Poll


class Mapping(models.Model):
    poll = models.OneToOneField(Poll, on_delete=models.CASCADE)
    code = models.CharField(unique=True, blank=True, max_length=50)
    
    def __str__(self) -> str:
        return self.code
    
    @staticmethod
    def generate_code():

        while True:
            new_code = ''.join(random.choices(
                string.ascii_uppercase +
                string.ascii_lowercase +
                string.digits,
                k=6))
            
            #we return the code if yet it isn't been used
            if not Mapping.objects.filter(code=new_code).count() > 0:
                return new_code


        
