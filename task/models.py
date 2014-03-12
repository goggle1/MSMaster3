#-*-coding:utf-8-*-
from django.db import models

class mobile_task_hits(models.Model):
    hash            = models.CharField(max_length = 40, null = False, primary_key=True, verbose_name = u"hash")
    time            = models.DateTimeField(blank = False, null = False, auto_now_add = False, verbose_name = u"time")
    hits_num        = models.BigIntegerField(blank = False, null = False,  verbose_name = u"hits_num") 
    #primary         = ('hash', 'time')
    
    class Meta:
        db_table        = "mobile_task_hits"
        #unique_together = ('hash', 'time') 
        
    def __unicode__(self):  
        return '%s, %s'%(self.hash, self.time.strftime("%Y-%m-%d %H:%M:%S"))
    

class mobile_task_temperature(models.Model):
    hash            = models.CharField(max_length = 40, primary_key = True, verbose_name = u"hash")
    online_time     = models.DateTimeField(null = True, auto_now_add = False, verbose_name = u"online_time")
    is_valid        = models.IntegerField(blank = False, null = True,  verbose_name = u"is_valid")
    filesize        = models.BigIntegerField(blank = False, null = True,  verbose_name = u"filesize")
    temperature0    = models.FloatField(blank = False, null = True,  verbose_name = u"temperature0")
    temperature1    = models.FloatField(blank = False, null = True,  verbose_name = u"temperature1")
    temperature2    = models.FloatField(blank = False, null = True,  verbose_name = u"temperature2")
    temperature3    = models.FloatField(blank = False, null = True,  verbose_name = u"temperature3")    
    temperature4    = models.FloatField(blank = False, null = True,  verbose_name = u"temperature4")
    temperature5    = models.FloatField(blank = False, null = True,  verbose_name = u"temperature5")
    temperature6    = models.FloatField(blank = False, null = True,  verbose_name = u"temperature6") 
    temperature7    = models.FloatField(blank = False, null = True,  verbose_name = u"temperature7")
    PayOrFree       = models.SmallIntegerField(blank = False, null = True,  verbose_name = u"PayOrFree")
    mediaId         = models.IntegerField(blank = False, null = True,  verbose_name = u"mediaId")  
    mediaName       = models.CharField(max_length = 256, blank = False, null = True,  verbose_name = u"mediaName")   
    payStartTime    = models.DateTimeField(null = True, auto_now_add = False, verbose_name = u"payStartTime")
    payEndTime      = models.DateTimeField(null = True, auto_now_add = False, verbose_name = u"payEndTime")
    
    class Meta:
        db_table    = "mobile_task_temperature"
        
    def __unicode__(self):  
        return '%s'%(self.hash)
        
    def todict(self):
        dic = {}
        dic['hash']             = str(self.hash)        
        dic['online_time']      = self.online_time.strftime("%Y-%m-%d %H:%M:%S")
        dic['is_valid']         = str(self.is_valid)
        dic['filesize']         = str(self.filesize)
        dic['temperature0']     = str(self.temperature0)
        dic['temperature1']     = str(self.temperature1)
        dic['temperature2']     = str(self.temperature2)
        dic['temperature3']     = str(self.temperature3)
        dic['temperature4']     = str(self.temperature4)
        dic['temperature5']     = str(self.temperature5)
        dic['temperature6']     = str(self.temperature6)
        dic['temperature7']     = str(self.temperature7)
        dic['PayOrFree']        = str(self.PayOrFree)
        dic['mediaId']          = str(self.mediaId)
        dic['mediaName']        = str(self.mediaName)
        #dic['payStartTime']     = self.payStartTime.strftime("%Y-%m-%d %H:%M:%S")    
        #dic['payEndTime']       = self.payEndTime.strftime("%Y-%m-%d %H:%M:%S")
        dic['payStartTime']     = str(self.payStartTime)
        dic['payEndTime']       = str(self.payEndTime)
        return dic
        

class pc_task_hits(models.Model):
    hash            = models.CharField(max_length = 40, null = False, primary_key=True, verbose_name = u"hash")
    time            = models.DateTimeField(blank = False, null = False, auto_now_add = False, verbose_name = u"time")
    hits_num        = models.BigIntegerField(blank = False, null = False,  verbose_name = u"hits_num") 
    #primary         = ('hash', 'time')
    
    class Meta:
        db_table        = "pc_task_hits"
        #unique_together = ('hash', 'time') 
        
    def __unicode__(self):  
        return '%s, %s'%(self.hash, self.time.strftime("%Y-%m-%d %H:%M:%S"))
    

class pc_task_temperature(models.Model):
    hash            = models.CharField(max_length = 40, primary_key = True, verbose_name = u"hash")
    online_time     = models.DateTimeField(null = True, auto_now_add = False, verbose_name = u"online_time")
    is_valid        = models.IntegerField(blank = False, null = True,  verbose_name = u"is_valid")
    filesize        = models.BigIntegerField(blank = False, null = True,  verbose_name = u"filesize")
    temperature0    = models.FloatField(blank = False, null = True,  verbose_name = u"temperature0")
    temperature1    = models.FloatField(blank = False, null = True,  verbose_name = u"temperature1")
    temperature2    = models.FloatField(blank = False, null = True,  verbose_name = u"temperature2")
    temperature3    = models.FloatField(blank = False, null = True,  verbose_name = u"temperature3")    
    temperature4    = models.FloatField(blank = False, null = True,  verbose_name = u"temperature4")
    temperature5    = models.FloatField(blank = False, null = True,  verbose_name = u"temperature5")
    temperature6    = models.FloatField(blank = False, null = True,  verbose_name = u"temperature6") 
    temperature7    = models.FloatField(blank = False, null = True,  verbose_name = u"temperature7")
    PayOrFree       = models.SmallIntegerField(blank = False, null = True,  verbose_name = u"PayOrFree")
    mediaId         = models.IntegerField(blank = False, null = True,  verbose_name = u"mediaId")  
    mediaName       = models.CharField(max_length = 256, blank = False, null = True,  verbose_name = u"mediaName")   
    payStartTime    = models.DateTimeField(null = True, auto_now_add = False, verbose_name = u"payStartTime")
    payEndTime      = models.DateTimeField(null = True, auto_now_add = False, verbose_name = u"payEndTime")
    
    class Meta:
        db_table    = "pc_task_temperature"
        
    def __unicode__(self):  
        return '%s'%(self.hash)
        
    def todict(self):
        dic = {}
        dic['hash']             = str(self.hash)        
        dic['online_time']      = self.online_time.strftime("%Y-%m-%d %H:%M:%S")
        dic['is_valid']         = str(self.is_valid)
        dic['filesize']         = str(self.filesize)
        dic['temperature0']     = str(self.temperature0)
        dic['temperature1']     = str(self.temperature1)
        dic['temperature2']     = str(self.temperature2)
        dic['temperature3']     = str(self.temperature3)
        dic['temperature4']     = str(self.temperature4)
        dic['temperature5']     = str(self.temperature5)
        dic['temperature6']     = str(self.temperature6)
        dic['temperature7']     = str(self.temperature7)
        dic['PayOrFree']        = str(self.PayOrFree)
        dic['mediaId']          = str(self.mediaId)
        dic['mediaName']        = str(self.mediaName)      
        #dic['payStartTime']     = self.payStartTime.strftime("%Y-%m-%d %H:%M:%S")    
        #dic['payEndTime']       = self.payEndTime.strftime("%Y-%m-%d %H:%M:%S")
        dic['payStartTime']     = str(self.payStartTime)
        dic['payEndTime']       = str(self.payEndTime)
        return dic
        