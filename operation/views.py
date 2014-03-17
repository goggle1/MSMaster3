#coding=utf-8
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response,RequestContext
import json
import models
import string
import threading
import time
import MS.views
import task.views
import room.views
import virtual_room.views

from multiprocessing import Process
import os

def get_operation_record(platform, v_type, v_name):
    records = []
    if(platform == 'mobile'):
        records = models.mobile_operation.objects.filter(type=v_type, name=v_name)
    elif(platform == 'pc'):
        records = models.pc_operation.objects.filter(type=v_type, name=v_name)
    return records


def get_operation_by_type_name(platform, v_type, v_name):
    records = []
    if(platform == 'mobile'):
        records = models.mobile_operation.objects.filter(type=v_type, name=v_name)
    elif(platform == 'pc'):
        records = models.pc_operation.objects.filter(type=v_type, name=v_name)
    return records



def get_operation_undone_by_type(platform, v_type):
    records = []
    if(platform == 'mobile'):
        records = models.mobile_operation.objects.filter(type=v_type).exclude(status=models.STATUS_DONE)
    elif(platform == 'pc'):
        records = models.pc_operation.objects.filter(type=v_type).exclude(status=models.STATUS_DONE)
    return records


def get_operation_undone_by_type_name(platform, v_type, v_name):
    records = []
    if(platform == 'mobile'):
        records = models.mobile_operation.objects.filter(type=v_type, name=v_name).exclude(status=models.STATUS_DONE)
    elif(platform == 'pc'):
        records = models.pc_operation.objects.filter(type=v_type, name=v_name).exclude(status=models.STATUS_DONE)
    return records


def create_operation_record(platform, v_type, v_name, v_user, v_dispatch_time, v_memo=''):
    record = None    
    if(platform == 'mobile'):
        record = models.mobile_operation(type=v_type, name=v_name, user=v_user, dispatch_time=v_dispatch_time, status=models.STATUS_DISPATCHED, memo=v_memo)
        record.save()
    elif(platform == 'pc'):
        record = models.pc_operation(type=v_type, name=v_name, user=v_user, dispatch_time=v_dispatch_time, status=models.STATUS_DISPATCHED, memo=v_memo)
        record.save()
    return record


def create_operation_record_by_dict(platform, operation):
    record = None    
    if(platform == 'mobile'):
        record = models.mobile_operation(type=operation['type'], name=operation['name'], user=operation['user'], dispatch_time=operation['dispatch_time'], status=models.STATUS_DISPATCHED, memo=operation['memo'])
        record.save()
    elif(platform == 'pc'):
        record = models.pc_operation(type=operation['type'], name=operation['name'], user=operation['user'], dispatch_time=operation['dispatch_time'], status=models.STATUS_DISPATCHED, memo=operation['memo'])
        record.save()
    return record



def get_operation_local(platform):
    operation_list = None
    if(platform == 'mobile'):
        operation_list = models.mobile_operation.objects.all()
    elif(platform == 'pc'):
        operation_list = models.pc_operation.objects.all()    
    return operation_list
       

def get_operation_list(request, platform):
    print 'get_operation_list'
    print request.REQUEST
    
    start = request.REQUEST['start']
    limit = request.REQUEST['limit']
    start_index = string.atoi(start)
    limit_num = string.atoi(limit)
    
    kwargs = {}
    
    v_type = ''
    if 'type' in request.REQUEST:
        v_type = request.REQUEST['type']
    if(v_type != ''):
        kwargs['type__contains'] = v_type
            
    v_name = ''
    if 'name' in request.REQUEST:
        v_name = request.REQUEST['name']
    if(v_name != ''):
        kwargs['name__contains'] = v_name
    
    v_user = ''
    if 'user' in request.REQUEST:
        v_user = request.REQUEST['user']
    if(v_user != ''):
        kwargs['user__contains'] = v_user
        
    v_status = ''
    if 'status' in request.REQUEST:
        v_status = request.REQUEST['status']
    if(v_status != ''):
        kwargs['status'] = v_status
    
    print kwargs
    
    sort = ''
    if 'sort' in request.REQUEST:
        sort  = request.REQUEST['sort']
        
    dire = ''
    if 'dir' in request.REQUEST:
        dire   = request.REQUEST['dir']
            
    order_condition = ''
    if(len(dire) > 0):
        if(dire == 'ASC'):
            order_condition += ''
        elif(dire == 'DESC'):
            order_condition += '-'
                
    if(len(sort) > 0):
        order_condition += sort
    
    operations = get_operation_local(platform)
    operations1 = operations.filter(**kwargs)
    operations2 = None
    if(len(order_condition) > 0):
        operations2 = operations1.order_by(order_condition)[start_index:start_index+limit_num]
    else:
        operations2 = operations1[start_index:start_index+limit_num]
    
    return_datas = {'success':True, 'data':[]}
    return_datas['total_count'] = operations1.count()
    for operation in operations2:
        return_datas['data'].append(operation.todict())
        
    return HttpResponse(json.dumps(return_datas))


def show_operation_list(request, platform):  
    output = ''
    ids = request.REQUEST['ids']    
    id_list = ids.split(',')
    operations = get_operation_local(platform)
    
    for the_id in id_list:
        operation_list = operations.filter(id=the_id)
        title = '<h1>id: %s</h1>' % (the_id)
        output += title  
        for operation in operation_list:
            output += '%s,%s,%s,%s,%s,%s,%s,%s<br>' \
            % (str(operation.id), str(operation.type), str(operation.name), str(operation.dispatch_time), \
               str(operation.status), str(operation.begin_time), str(operation.end_time), str(operation.memo))        
        
    return HttpResponse(output)


def do_operation(platform, operation):
        result = False
        if(operation.status == models.STATUS_DONE):
            return True
        if(operation.type == 'sync_hash_db'):
            if(operation.memo == '~'):
                result = task.views.do_sync_all_sql(platform, operation)
            else:
                result = task.views.do_sync_partial(platform, operation)
        elif(operation.type == 'sync_pay_medias'):
            result = task.views.do_sync_pay_medias(platform, operation)
        elif(operation.type == 'upload_hits_num'):
            result = task.views.do_upload(platform, operation)
        elif(operation.type == 'calc_hot_mean_hits_num'):
            result = task.views.do_calc_hot_mean_hits_num(platform, operation)
        elif(operation.type == 'calc_temperature'):
            result = task.views.do_calc_temperature(platform, operation)
        elif(operation.type == 'evaluate_temperature'):
            result = task.views.do_evaluate_temperature(platform, operation)
        elif(operation.type == 'sync_ms_db'):
            result = MS.views.do_sync_ms_db(platform, operation)
        elif(operation.type == 'sync_ms_status'):
            result = MS.views.do_sync_ms_status(platform, operation)
        elif(operation.type == 'sync_room_db'):
            result = room.views.do_sync_room_db(platform, operation)
        elif(operation.type == 'sync_room_status'):
            result = room.views.do_sync_room_status(platform, operation)
        elif(operation.type == 'stat_virtual_room'):
            result = virtual_room.views.do_stat_virtual_room(platform, operation)
        elif(operation.type == 'delete_cold_tasks'):
            result = room.views.do_delete_cold_tasks(platform, operation)  
        elif(operation.type == 'add_hot_tasks'):
            result = room.views.do_add_hot_tasks(platform, operation)
        elif(operation.type == 'virtual_room_add_tasks'):
            result = virtual_room.views.do_virtual_room_add_tasks(platform, operation)
        elif(operation.type == 'virtual_room_delete_tasks'):
            result = virtual_room.views.do_virtual_room_delete_tasks(platform, operation)
        elif(operation.type == 'auto_distribute_tasks'):
            result = room.views.do_auto_distribute_tasks(platform, operation)
        elif(operation.type == 'auto_delete_tasks'):
            result = room.views.do_auto_delete_tasks(platform, operation)
        elif(operation.type == 'ms_delete_cold_tasks'):
            result = MS.views.ms_do_delete_cold_tasks(platform, operation)
        elif(operation.type == 'ms_add_hot_tasks'):
            result = MS.views.ms_do_add_hot_tasks(platform, operation)      
        else:
            print 'unknown operation type: %s' % (operation.type)
            
        return result
    

def do_operation_list(platform, operation_list):   
    for operation in operation_list:
        p = Process(target=do_operation, args=(platform, operation))
        p.start()
        p.join()
        
        
#g_thread = None
g_thread_mobile = None
g_thread_pc = None
class Thread_JOBS(threading.Thread):
    #platform = ''
    #operation_list = []
    
    def __init__(self, v_platform, operation_list):
        super(Thread_JOBS, self).__init__()        
        self.platform = v_platform
        self.operation_list = operation_list
               
            
    def run(self):        
        do_operation_list(self.platform, self.operation_list)  
        #global g_thread
        global g_thread_mobile
        global g_thread_pc
        if(self.platform == 'mobile'):
            g_thread_mobile = None
        elif(self.platform == 'pc'):
            g_thread_pc = None



def operation_type_int(v_type):
    result = 0
    type_dict = {   'sync_hash_db':1,               \
                    'sync_pay_medias':2,            \
                    'upload_hits_num':3,            \
                    'calc_hot_mean_hits_num':4,     \
                    'calc_temperature':5,           \
                    'sync_ms_db':6,                 \
                    'sync_ms_status':7,             \
                    'sync_room_db':8,               \
                    'sync_room_status':9,           \
                    'stat_virtual_room':10,         \
                    'delete_cold_tasks':11,         \
                    'add_hot_tasks':12,             \
                    'auto_distribute_tasks':13,     \
                    'auto_delete_tasks':14,         \
                    'virtual_room_add_tasks':15,    \
                    'virtual_room_delete_tasks':16, \
                    'evaluate_temperature':17       \
                }
    if(type_dict.has_key(v_type) == True):
        result = type_dict[v_type]        
    return result

            
def operation_cmp(op1, op2):
    type1 = operation_type_int(op1.type)
    type2 = operation_type_int(op2.type)
    
    if(type1 == type2):
        return cmp(op1.name, op2.name)
    else:
        if(type1<type2):
            return -1
        else:
            return 1            

    
def do_selected_operations(request, platform):  
    output = ''
    operation_list = []
    operations = get_operation_local(platform)
    
    ids = request.REQUEST['ids']    
    id_list = ids.split(',')
    for the_id in id_list:
        op_list = operations.filter(id=the_id)
        operation_list.extend(op_list)
    
    print 'before:'
    for op in operation_list:
        print '%s %s' % (op.type, op.name)
    operation_list.sort(operation_cmp)
    print 'after:'
    for op in operation_list:
        print '%s %s' % (op.type, op.name)
    
    #global g_thread
    global g_thread_mobile
    global g_thread_pc    
    if(platform == 'mobile'):
        if(g_thread_mobile == None):
            g_thread_mobile = Thread_JOBS(platform, operation_list)            
            g_thread_mobile.start() 
            #g_thread_mobile = Process(target=do_operation_list, args=(platform, operation_list))            
            #g_thread_mobile.start()       
            output += 'do '  
            for operation in operation_list:      
                output += '%s,' % (str(operation.id))
        else:
            output += 'Thread_JOBS has started!'
    elif(platform == 'pc'):
        if(g_thread_pc == None):
            output += 'do '  
            for operation in operation_list:      
                output += '%s,' % (str(operation.id))
            print "%s begin [@%d]" % (output, os.getpid())
            g_thread_pc = Thread_JOBS(platform, operation_list)            
            g_thread_pc.start()
            #g_thread_pc = Process(target=do_operation_list, args=(platform, operation_list))            
            #g_thread_pc.start()    
        else:
            output += 'Thread_JOBS has started!'           
        
    print "%s end [@%d]" % (output, os.getpid())
    response = HttpResponse(output, mimetype='text/plain')
    response['Content-Length'] = len(output)
    return response


def do_all_operations(request, platform):  
    output = ''
    operation_list = []
    operations = get_operation_local(platform)    
    #temp_list = operations.filter(status=models.STATUS_DISPATCHED)
    temp_list = operations.exclude(status=models.STATUS_DONE)
    operation_list.extend(temp_list)
    
    print 'before:'
    for op in operation_list:
        print '%s %s' % (op.type, op.name)
    operation_list.sort(operation_cmp)
    print 'after:'
    for op in operation_list:
        print '%s %s' % (op.type, op.name)
    
    #global g_thread
    global g_thread_mobile
    global g_thread_pc    
    if(platform == 'mobile'):
        if(g_thread_mobile == None):
            g_thread_mobile = Thread_JOBS(platform, operation_list)            
            g_thread_mobile.start() 
            #g_thread_mobile = Process(target=do_operation_list, args=(platform, operation_list))            
            #g_thread_mobile.start()       
            output += 'do '  
            for operation in operation_list:      
                output += '%s,' % (str(operation.id))
        else:
            output += 'Thread_JOBS has started!'
    elif(platform == 'pc'):
        if(g_thread_pc == None):
            g_thread_pc = Thread_JOBS(platform, operation_list)            
            g_thread_pc.start()
            #g_thread_pc = Process(target=do_operation_list, args=(platform, operation_list))            
            #g_thread_pc.start()     
            output += 'do '  
            for operation in operation_list:      
                output += '%s,' % (str(operation.id))
        else:
            output += 'Thread_JOBS has started!'
            
    response = HttpResponse(output, mimetype='text/plain')
    response['Content-Length'] = len(output)
    return response    

