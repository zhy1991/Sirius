#-*- coding: UTF-8 -*-

from __future__ import unicode_literals

from django.db import models

class vm_snap(models.Model):
        image_name = models.CharField(max_length=30)
        vm_id = models.CharField(max_length=100)
        parent_name = models.CharField(max_length=30,null=True)
        image_id = models.CharField(max_length=100)
        status = models.IntegerField()
        time = models.DateTimeField()

