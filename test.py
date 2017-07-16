import sys, os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tpobot.settings")
django.setup()

from bot.models import Company
c = Company.objects.get(company_name='asfd')
print(c.what_has_changed())

print(c.x)
c.x = 3
c.save()
