from __future__ import unicode_literals
from django.db import models

import common.constant as c
import json

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

    task_id = models.AutoField(primary_key = True)
    proc_id = models.CharField(max_length = 100, blank = True)
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
    status = models.PositiveSmallIntegerField(default = 0)
    eps1_val = models.FloatField(default = float(c.EPSILON_1))
    eps1_level = models.PositiveSmallIntegerField(default = 1)

    class Meta:
        ordering = ('start_time',)


class Job(models.Model):
    dp_id = models.AutoField(primary_key = True)
    proc_id = models.CharField(max_length = 100, blank = True)
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

class UtilityMeasure(models.Model):
    analysis_id = models.AutoField(primary_key = True)
    task_ids = models.CharField(blank = True, max_length = 30)
    proc_id = models.CharField(max_length = 100, blank = True)
    ml_config = models.TextField(blank = True)
    ml_measure = models.TextField(blank = True)
    ml_result = models.TextField(blank = True)
    user_queries = models.TextField(blank = True)
    query_results = models.TextField(blank = True)
    status = models.PositiveSmallIntegerField(default = 0)
    start_time = models.DateTimeField(auto_now_add = True)
    end_time = models.DateTimeField(null = True)

    def settask_ids(self, value):
        self.task_ids = json.dumps(value)

    def setml_config(self, value):
        self.ml_config = json.dumps(value)

    def setml_measure(self, value):
        self.ml_measure = json.dumps(value)

    def setml_result(self, value):
        self.ml_result = json.dumps(value)

    def setuser_queries(self, value):
        self.user_queries = json.dumps(value)

    def setquery_results(self, value):
        self.query_results = json.dumps(value)

    def gettask_ids(self):
        return json.loads(self.task_ids)

    def getml_config(self):
        return json.loads(self.ml_config)

    def getml_measure(self):
        return json.loads(self.ml_measure)

    def getml_result(self):
        return json.loads(self.ml_result)

    def getuser_queries(self):
        return json.loads(self.user_queries)

    def getquery_results(self):
        return json.loads(self.query_results)