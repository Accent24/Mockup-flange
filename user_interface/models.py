from django.db import models
from django.shortcuts import reverse
from django.urls import reverse_lazy


# Create your models here.
class MainFunction(models.Model):
    name = models.CharField(blank=False, max_length=200)
    view_name = models.CharField(blank=False, max_length=200)


    def __str__(self):
        return self.name


    def get_absolute_url(self):
        return reverse('FillFormView', kwargs={'pk': self.pk})


class FillForm(models.Model):
    date_time = models.DateTimeField(auto_now=True)
    report_number = models.CharField(max_length=200, blank=False, verbose_name='Report number')
    employee_id = models.IntegerField(verbose_name='Employee ID')
    employee_name = models.CharField(max_length=200, blank=False, verbose_name='Employee name')
    job_number = models.CharField(max_length=200, blank=True, verbose_name='Job number')
    wo_number = models.CharField(max_length=200, blank=True, verbose_name='Work order number')
    steel_temperature = models.IntegerField(blank=False, verbose_name='Steel temperature')
    fabrication_stage = models.CharField(max_length=200, blank=False, verbose_name='Fabrication stage')
    file_path = models.CharField(max_length=250, blank=False)
    station_name = models.CharField(max_length=250, blank=False)


    def __str__(self):
        name = '{0} - {1} - {2}'.format(self.station_name, self.report_number, self.date_time)
        return name


    def get_absolute_url(self):
        return reverse(self.station_name, kwargs={'form_pk': self.pk})
