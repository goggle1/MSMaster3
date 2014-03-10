#-*-coding:utf-8-*-
from django.db import models

# Create your models here.
class mobile_room(models.Model):
    # config
    room_id             = models.IntegerField(blank = False, primary_key=True, verbose_name = u"room_id")
    room_name           = models.CharField(max_length=64, verbose_name = u"room_name")
    # status 
    is_valid            = models.IntegerField(blank = False, verbose_name = u"is_valid")
    ms_number           = models.IntegerField(blank = False, null = True, verbose_name = u"ms_number")   
    task_number         = models.IntegerField(blank = False, null = True, verbose_name = u"task_number")   
    total_disk_space    = models.BigIntegerField(blank = False, null = True, verbose_name = u"total_disk_space")
    free_disk_space     = models.BigIntegerField(blank = False, null = True, verbose_name = u"free_disk_space")
    suggest_task_number = models.IntegerField(blank = False, null = True, verbose_name = u"suggest_task_number")
    num_dispatching     = models.IntegerField(blank = False, null = True,  verbose_name = u"num_dispatching") 
    num_deleting        = models.IntegerField(blank = False, null = True,  verbose_name = u"num_deleting")    
    check_time          = models.DateTimeField(auto_now_add=True, null = True, verbose_name = u"check_time")
    
    def todict(self):
        dic = {}
        dic['room_id'] = str(self.room_id)
        dic['room_name'] = str(self.room_name)
        dic['is_valid'] = str(self.is_valid)
        dic['ms_number'] = str(self.ms_number)
        dic['task_number'] = str(self.task_number)
        dic['total_disk_space'] = str(self.total_disk_space)
        dic['free_disk_space'] = str(self.free_disk_space)
        dic['suggest_task_number'] = str(self.suggest_task_number)
        dic['num_dispatching'] = str(self.num_dispatching)
        dic['num_deleting'] = str(self.num_deleting)
        dic['check_time'] = str(self.check_time)
        return dic
    
    class Meta:
        db_table    = "mobile_room" 

        
class pc_room(models.Model):
    # config
    room_id       = models.IntegerField(blank = False, primary_key=True, verbose_name = u"room_id")
    room_name     = models.CharField(max_length=64, verbose_name = u"room_name")
    # status 
    is_valid            = models.IntegerField(blank = False, verbose_name = u"is_valid")
    ms_number           = models.IntegerField(blank = False, null = True, verbose_name = u"ms_number")   
    task_number         = models.IntegerField(blank = False, null = True, verbose_name = u"task_number")   
    total_disk_space    = models.BigIntegerField(blank = False, null = True, verbose_name = u"total_disk_space")
    free_disk_space     = models.BigIntegerField(blank = False, null = True, verbose_name = u"free_disk_space")
    suggest_task_number = models.IntegerField(blank = False, null = True, verbose_name = u"suggest_task_number")
    num_dispatching     = models.IntegerField(blank = False, null = True,  verbose_name = u"num_dispatching") 
    num_deleting        = models.IntegerField(blank = False, null = True,  verbose_name = u"num_deleting")    
    check_time          = models.DateTimeField(auto_now_add=True, null = True, verbose_name = u"check_time")
    
    def todict(self):
        dic = {}
        dic['room_id'] = str(self.room_id)
        dic['room_name'] = str(self.room_name)
        dic['is_valid'] = str(self.is_valid)
        dic['ms_number'] = str(self.ms_number)
        dic['task_number'] = str(self.task_number)
        dic['total_disk_space'] = str(self.total_disk_space)
        dic['free_disk_space'] = str(self.free_disk_space)
        dic['suggest_task_number'] = str(self.suggest_task_number)
        dic['num_dispatching'] = str(self.num_dispatching)
        dic['num_deleting'] = str(self.num_deleting)
        dic['check_time'] = str(self.check_time)
        return dic
    
    class Meta:
        db_table    = "pc_room" 


