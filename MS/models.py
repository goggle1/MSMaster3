#-*-coding:utf-8-*-
from django.db import models
# Create your models here.

class mobile_ms(models.Model):
    # config
    server_id       = models.IntegerField(blank = False, primary_key=True, verbose_name = u"server_id")
    server_name     = models.CharField(max_length=32, verbose_name = u"server_name")   
    server_ip       = models.IPAddressField(verbose_name = u"server_ip")
    server_port     = models.IntegerField(blank = False, verbose_name = u"server_port")
    controll_ip     = models.IPAddressField(verbose_name = u"controll_ip")
    controll_port   = models.IntegerField(blank = False, verbose_name = u"controll_port")    
    room_id         = models.IntegerField(blank = False, null = True, verbose_name = u"room_id")
    room_name       = models.CharField(null = True, max_length=32, verbose_name = u"room_name")
    server_version  = models.CharField(null = True, max_length=32, verbose_name = u"server_version")
    protocol_version= models.CharField(null = True, max_length=32, verbose_name = u"protocol_version")        
    identity_file   = models.CharField(null = True, max_length=32, verbose_name = u"identity_file")
    password        = models.CharField(null = True, max_length=32, verbose_name = u"password")    
    # status 
    is_valid        = models.IntegerField(blank = False, null = True, verbose_name = u"is_valid") 
    is_dispatch     = models.IntegerField(blank = False, null = True, verbose_name = u"is_dispatch") 
    is_pause        = models.IntegerField(blank = False, null = True, verbose_name = u"is_pause")
    task_number     = models.IntegerField(blank = False, null = True, verbose_name = u"task_number")    
    server_status1  = models.IntegerField(blank = False, null = True, verbose_name = u"server_status1")
    server_status2  = models.IntegerField(blank = False, null = True, verbose_name = u"server_status2")
    server_status3  = models.IntegerField(blank = False, null = True, verbose_name = u"server_status3")
    server_status4  = models.IntegerField(blank = False, null = True, verbose_name = u"server_status4")
    total_disk_space= models.BigIntegerField(blank = False, null = True, verbose_name = u"total_disk_space")
    free_disk_space = models.BigIntegerField(blank = False, null = True, verbose_name = u"free_disk_space")
    check_time      = models.DateTimeField(auto_now_add=True, null = True, verbose_name = u"check_time")
  
    class Meta:
        db_table    = "mobile_ms" 
        
    def __unicode__(self):
        return "%s,%s,%s" % (str(self.server_id), str(self.server_name), str(self.server_ip))
          
    def todict(self):
        dic = {}
        dic['server_id'] = str(self.server_id)
        dic['server_name'] = str(self.server_name)
        dic['server_ip'] = str(self.server_ip)
        dic['server_port'] = str(self.server_port)
        dic['controll_ip'] = str(self.controll_ip)
        dic['controll_port'] = str(self.controll_port)
        dic['room_id'] = str(self.room_id)
        dic['room_name'] = str(self.room_name)
        dic['server_version'] = str(self.server_version)
        dic['protocol_version'] = str(self.protocol_version)
        dic['identity_file'] = str(self.identity_file)
        dic['password'] = str(self.password)
        dic['is_valid'] = str(self.is_valid)
        dic['is_dispatch'] = str(self.is_dispatch)
        dic['is_pause']    = str(self.is_pause)
        dic['task_number'] = str(self.task_number)
        dic['server_status1'] = str(self.server_status1)
        dic['server_status2'] = str(self.server_status2)
        dic['server_status3'] = str(self.server_status3)
        dic['server_status4'] = str(self.server_status4)
        dic['total_disk_space'] = str(self.total_disk_space)
        dic['free_disk_space'] = str(self.free_disk_space)
        dic['check_time'] = str(self.check_time)
        return dic
  
            
class pc_ms(models.Model):
    # config
    server_id       = models.IntegerField(blank = False, primary_key=True, verbose_name = u"server_id")
    server_name     = models.CharField(max_length=32, verbose_name = u"server_name")   
    server_ip       = models.IPAddressField(verbose_name = u"server_ip")
    server_port     = models.IntegerField(blank = False, verbose_name = u"server_port")
    controll_ip     = models.IPAddressField(verbose_name = u"controll_ip")
    controll_port   = models.IntegerField(blank = False, verbose_name = u"controll_port")    
    room_id         = models.IntegerField(blank = False, null = True, verbose_name = u"room_id")
    room_name       = models.CharField(null = True, max_length=32, verbose_name = u"room_name")
    server_version  = models.CharField(null = True, max_length=32, verbose_name = u"server_version")
    protocol_version= models.CharField(null = True, max_length=32, verbose_name = u"protocol_version")        
    identity_file   = models.CharField(null = True, max_length=32, verbose_name = u"identity_file")
    password        = models.CharField(null = True, max_length=32, verbose_name = u"password")    
    # status 
    is_valid        = models.IntegerField(blank = False, null = True, verbose_name = u"is_valid") 
    is_dispatch     = models.IntegerField(blank = False, null = True, verbose_name = u"is_dispatch") 
    is_pause        = models.IntegerField(blank = False, null = True, verbose_name = u"is_pause")
    task_number     = models.IntegerField(blank = False, null = True, verbose_name = u"task_number")    
    server_status1  = models.IntegerField(blank = False, null = True, verbose_name = u"server_status1")
    server_status2  = models.IntegerField(blank = False, null = True, verbose_name = u"server_status2")
    server_status3  = models.IntegerField(blank = False, null = True, verbose_name = u"server_status3")
    server_status4  = models.IntegerField(blank = False, null = True, verbose_name = u"server_status4")
    total_disk_space= models.BigIntegerField(blank = False, null = True, verbose_name = u"total_disk_space")
    free_disk_space = models.BigIntegerField(blank = False, null = True, verbose_name = u"free_disk_space")
    check_time      = models.DateTimeField(auto_now_add=True, null = True, verbose_name = u"check_time")
    
    class Meta:
        db_table    = "pc_ms" 
        
    def __unicode__(self):
        return "%s,%s,%s" % (str(self.server_id), str(self.server_name), str(self.server_ip))
        
    def todict(self):
        dic = {}
        dic['server_id'] = str(self.server_id)
        dic['server_name'] = str(self.server_name)
        dic['server_ip'] = str(self.server_ip)
        dic['server_port'] = str(self.server_port)
        dic['controll_ip'] = str(self.controll_ip)
        dic['controll_port'] = str(self.controll_port)
        dic['room_id'] = str(self.room_id)
        dic['room_name'] = str(self.room_name)
        dic['server_version'] = str(self.server_version)
        dic['protocol_version'] = str(self.protocol_version)
        dic['identity_file'] = str(self.identity_file)
        dic['password'] = str(self.password)
        dic['is_valid'] = str(self.is_valid)
        dic['is_dispatch'] = str(self.is_dispatch)
        dic['is_pause']    = str(self.is_pause)
        dic['task_number'] = str(self.task_number)
        dic['server_status1'] = str(self.server_status1)
        dic['server_status2'] = str(self.server_status2)
        dic['server_status3'] = str(self.server_status3)
        dic['server_status4'] = str(self.server_status4)
        dic['total_disk_space'] = str(self.total_disk_space)
        dic['free_disk_space'] = str(self.free_disk_space)
        dic['check_time'] = str(self.check_time)
        return dic


