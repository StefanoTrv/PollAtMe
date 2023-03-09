from __future__ import unicode_literals
import string
from django.db import migrations, models
import random



def add_mapping_old_polls(apps, schema_editor):
    Poll = apps.get_model("polls", "Poll")
    Mapping = apps.get_model("polls", "Mapping")


    for _poll in Poll.objects.all():
        if Mapping.objects.filter(poll=_poll).count() == 0:
           new_code = generate_code(Mapping)
           Mapping(
               poll = _poll,
               code = new_code
           ).save()

def generate_code(mapping):

    while True:
        new_code = ''.join(random.choices(
            string.ascii_uppercase +
            string.ascii_lowercase +
            string.digits,
                k=6))
            
            #se il codice non è ancora stato utilizzato lo ritorniamo
        if not mapping.objects.filter(code=new_code).count() > 0:
            return new_code



class Migration(migrations.Migration):
    dependencies = [
        ("polls", "0010_merge_20230306_1702"),
    ]

    operations = [
        migrations.RunPython(add_mapping_old_polls),
    ]
