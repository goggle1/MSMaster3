#-*-coding:utf-8-*-
from django.db import models

# Create your models here.
class mobile_virtual_room(models.Model):
    # config
    virtual_room_id     = models.IntegerField(blank = False, primary_key=True, verbose_name = u"virtual_room_id")
    virtual_room_name   = models.CharField(max_length=64, verbose_name = u"virtual_room_name")
    # status 
    is_valid            = models.IntegerField(blank = False, verbose_name = u"is_valid")
    room_number         = models.IntegerField(blank = False, null = True, verbose_name = u"room_number")   
    ms_number           = models.IntegerField(blank = False, null = True, verbose_name = u"ms_number")   
    task_number         = models.IntegerField(blank = False, null = True, verbose_name = u"task_number")   
    total_disk_space    = models.BigIntegerField(blank = False, null = True, verbose_name = u"total_disk_space")
    free_disk_space     = models.BigIntegerField(blank = False, null = True, verbose_name = u"free_disk_space")
    topN                = models.IntegerField(blank = False, null = True, verbose_name = u"topN")
    
    def todict(self):
        dic = {}
        dic['virtual_room_id'] = str(self.virtual_room_id)
        dic['virtual_room_name'] = str(self.virtual_room_name)
        dic['is_valid'] = str(self.is_valid)
        dic['room_number'] = str(self.room_number)
        dic['ms_number'] = str(self.ms_number)
        dic['task_number'] = str(self.task_number)
        dic['total_disk_space'] = str(self.total_disk_space)
        dic['free_disk_space'] = str(self.free_disk_space)
        dic['topN'] = str(self.topN)
        return dic
    
    class Meta:
        db_table    = "mobile_virtual_room" 

        
class pc_virtual_room(models.Model):
    # config
    virtual_room_id     = models.IntegerField(blank = False, primary_key=True, verbose_name = u"virtual_room_id")
    virtual_room_name   = models.CharField(max_length=64, verbose_name = u"virtual_room_name")
    # status 
    is_valid            = models.IntegerField(blank = False, verbose_name = u"is_valid")
    room_number         = models.IntegerField(blank = False, null = True, verbose_name = u"room_number")   
    ms_number           = models.IntegerField(blank = False, null = True, verbose_name = u"ms_number")   
    task_number         = models.IntegerField(blank = False, null = True, verbose_name = u"task_number")   
    total_disk_space    = models.BigIntegerField(blank = False, null = True, verbose_name = u"total_disk_space")
    free_disk_space     = models.BigIntegerField(blank = False, null = True, verbose_name = u"free_disk_space")
    topN                = models.IntegerField(blank = False, null = True, verbose_name = u"topN")
    
    def todict(self):
        dic = {}
        dic['virtual_room_id'] = str(self.virtual_room_id)
        dic['virtual_room_name'] = str(self.virtual_room_name)
        dic['is_valid'] = str(self.is_valid)
        dic['room_number'] = str(self.room_number)
        dic['ms_number'] = str(self.ms_number)
        dic['task_number'] = str(self.task_number)
        dic['total_disk_space'] = str(self.total_disk_space)
        dic['free_disk_space'] = str(self.free_disk_space)
        dic['topN'] = str(self.topN)
        return dic
    
    class Meta:
        db_table    = "pc_virtual_room" 