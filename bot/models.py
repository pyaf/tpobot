from django.db import models
from django.core.validators import URLValidator
import logging


class Company(models.Model):
    company_name = models.CharField(max_length=150, unique=True)
    updated_at = models.CharField(max_length=150, null=True, blank=True)
    company_profile = models.CharField(max_length=150, null=True, blank=True)
    purpose = models.CharField(max_length=150, null=True, blank=True)
    x = models.CharField(max_length=50, null=True, blank=True)
    xii = models.CharField(max_length=50, null=True, blank=True)
    cgpa = models.CharField(max_length=50, null=True, blank=True)
    course = models.CharField(max_length=50, null=True, blank=True)
    department = models.CharField(max_length=250, null=True, blank=True)
    a_backlog = models.CharField(max_length=50, null=True, blank=True)
    t_backlog = models.CharField(max_length=50, null=True, blank=True)
    ppt_date = models.CharField(max_length=50, null=True, blank=True)
    exam_date = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)#willingness status
    branch_issue_dead = models.CharField(max_length=100, null=True, blank=True)
    willingness_dead = models.CharField(max_length=100, null=True, blank=True)
    btech_ctc = models.CharField(max_length=100, null=True, blank=True)
    idd_imd_ctc = models.CharField(max_length=100, null=True, blank=True)
    jd = models.TextField(validators=[URLValidator()], null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s" %(self.company_name)



    def get_value(self, field):
        value = self.__dict__.get(field)
        return '' if value is None else value

    def update(self, data_dict):
        changed_fields = []
        for field in data_dict:
            if self.get_value(field) != data_dict[field]:
                setattr(self, field, data_dict[field])
                changed_fields.append(field)
        self.save()
        return changed_fields


    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        # imp_fields=[]

class User(models.Model):
    psid = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    profile_pic = models.TextField(validators=[URLValidator()], null=True, blank=True)
    gender = models.CharField(max_length=100, null=True, blank=True)
    course = models.CharField(max_length=50, null=True, blank=True)
    department = models.CharField(max_length=25, null=True, blank=True)
    profile_completed = models.BooleanField(default=False)
    valid = models.BooleanField(default=True)
    subscribed = models.BooleanField(default=True)

    def __str__(self):
        return "%s %s" %(self.first_name, self.last_name)


'''
The exception is CharFields and TextFields, which in Django are never saved as
 NULL. Blank values are stored in the DB as an empty string ('').
'''
