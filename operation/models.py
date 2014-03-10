#-*-coding:utf-8-*-
from django.db import models
# Create your models here.


STATUS_DISPATCHED   = 0
STATUS_STARTED      = 1
STATUS_DONE         = 2
                
class mobile_operation(models.Model):
    # config    
    #id              = models.IntegerField(blank = False, primary_key=True, verbose_name = u"id")
    type            = models.CharField(max_length=32, verbose_name = u"type") 
    name            = models.CharField(max_length=32, verbose_name = u"name")   
    user            = models.CharField(max_length=32, verbose_name = u"user")   
    dispatch_time   = models.DateTimeField(null = True, auto_now_add = False, verbose_name = u"dispatch_time")
    status          = models.IntegerField(blank = False, null = True,  verbose_name = u"status")
    begin_time      = models.DateTimeField(null = True, auto_now_add = False, verbose_name = u"begin_time")
    end_time        = models.DateTimeField(null = True, auto_now_add = False, verbose_name = u"end_time")
    memo            = models.CharField(null = True, max_length=1024, verbose_name = u"memo")
  
    class Meta:
        db_table    = "mobile_operation"
        #User._meta.has_auto_field = True 
        #User._meta.auto_field = id  
          
    def todict(self):
        dic = {}
        dic['id'] = str(self.id)
        dic['type'] = str(self.type)
        dic['name'] = str(self.name)
        dic['user'] = str(self.user)
        dic['dispatch_time'] = str(self.dispatch_time)
        dic['status'] = str(self.status)
        dic['begin_time'] = str(self.begin_time)
        dic['end_time'] = str(self.end_time)
        dic['memo'] = str(self.memo)
        return dic
    
    
class pc_operation(models.Model):
    # config    
    #id              = models.IntegerField(blank = False, primary_key=True, verbose_name = u"id")
    type            = models.CharField(max_length=32, verbose_name = u"type") 
    name            = models.CharField(max_length=32, verbose_name = u"name")   
    user            = models.CharField(max_length=32, verbose_name = u"user")   
    dispatch_time   = models.DateTimeField(null = True, auto_now_add = False, verbose_name = u"dispatch_time")
    status          = models.IntegerField(blank = False, null = True,  verbose_name = u"status")
    begin_time      = models.DateTimeField(null = True, auto_now_add = False, verbose_name = u"begin_time")
    end_time        = models.DateTimeField(null = True, auto_now_add = False, verbose_name = u"end_time")
    memo            = models.CharField(null = True, max_length=1024, verbose_name = u"memo")
  
    class Meta:
        db_table    = "pc_operation"
        #has_auto_field = True 
        #auto_field = id  
          
    def todict(self):
        dic = {}
        dic['id'] = str(self.id)
        dic['type'] = str(self.type)
        dic['name'] = str(self.name)
        dic['user'] = str(self.user)
        dic['dispatch_time'] = str(self.dispatch_time)
        dic['status'] = str(self.status)
        dic['begin_time'] = str(self.begin_time)
        dic['end_time'] = str(self.end_time)
        dic['memo'] = str(self.memo)
        return dic
  
            

