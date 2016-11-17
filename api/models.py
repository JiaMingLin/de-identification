from __future__ import unicode_literals

from django.db import models
import common.constant as c

# Create your models here.

"""
De-Identification Task Entity
    Task ID
    Task Name
    Data Path
    Selected Attributes
    Junction Tree
    Dependency Graph
    Task Create Time
    Task End Time
    Task Status
"""
class Task(models.Model):

    TASK_STATUS = (
        (0, 'WAITTING'),
        (1, 'FINISH'),
        (2, 'ERROR'),
    )
    task_id = models.CharField(primary_key = True)
    task_name = models.CharField(max_length = 100, blank = False)
    data_path = models.CharField(max_length = 300, blank = False)
    selected_attrs = models.TextField(blank = False)
    jtree_strct = models.TextField(max_length = 500, blank = True)
    opted_cluster = models.TextField(max_length = 500, blank = True)
    white_list = models.TextField(blank = True)
    dep_graph = models.TextField(blank = True)
    valbin_map = models.TextField(blank = True)
    domain = models.TextField(blank = True)
    start_time = models.DateTimeField(auto_now_add = True)
    end_time = models.DateTimeField(null = True)
    status = models.PositiveSmallIntegerField(default = 0, choices=TASK_STATUS)
    eps1_val = models.FloatField(default = float(c.EPSILON_1))
    eps1_level = models.PositiveSmallIntegerField(default = 1)

    class Meta:
        ordering = ('start_time',)


class Job(models.Model):
    dp_id = models.CharField(primary_key = True)
    task_id = models.ForeignKey(Task, on_delete=models.CASCADE)
    privacy_level = models.PositiveSmallIntegerField(default = 0)
    epsilon = models.FloatField()
    status = models.PositiveSmallIntegerField(default = 0)
    exp_round = models.PositiveSmallIntegerField(default = 0)
    min_freq = models.FloatField(default = 0.)
    synthetic_path = models.CharField(max_length = 300, blank = True)
    statistics_err = models.TextField(blank = True)
    log_path = models.CharField(max_length = 300, blank = True)
    start_time = models.DateTimeField(auto_now_add = True)
    end_time = models.DateTimeField(null = True)

    class Meta:
        ordering = ('start_time',)
