#-*-coding:utf-8-*-
from django.db import models

class mobile_config(models.Model):
    alpha           = models.FloatField(blank = False, null = False,  verbose_name = u"alpha")
    mean_hits       = models.BigIntegerField(blank = False, null = False,  verbose_name = u"mean_hits")
    
    class Meta:
        db_table        = "mobile_config"        


class pc_config(models.Model):
    alpha           = models.FloatField(blank = False, null = False,  verbose_name = u"alpha")
    mean_hits       = models.BigIntegerField(blank = False, null = False,  verbose_name = u"mean_hits")
    
    class Meta:
        db_table        = "pc_config" 