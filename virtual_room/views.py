#coding=utf-8
# Create your views here.

import string
import json
import time
import models

from django.http import HttpResponse
from multiprocessing import Process

import operation.views
import room.models
import room.ms
import room.views
import task.views
import MS.views


def django_get_virtual_room(platform):
    rooms = []
    if(platform == 'mobile'):
        rooms = models.mobile_virtual_room.objects.all()
    elif(platform == 'pc'):
        rooms = models.pc_virtual_room.objects.all()
    return rooms

def django_get_rooms_in_virtual_room(platform, v_virtual_room_id):
    room_list = None
    if(platform == 'mobile'):
        room_list = room.models.mobile_room.objects.filter(virtual_room_id=v_virtual_room_id)
    elif(platform == 'pc'):
        room_list = room.models.pc_room.objects.filter(virtual_room_id=v_virtual_room_id)
    return room_list


def get_virtual_room_by_id(platform, v_id):
    records = []
    if(platform == 'mobile'):
        records = models.mobile_virtual_room.objects.filter(virtual_room_id=v_id)
    elif(platform == 'pc'):
        records = models.pc_virtual_room.objects.filter(virtual_room_id=v_id)
    return records


def add_virtual_room_by_dict(platform, room):
    record = None    
    if(platform == 'mobile'):
        record = models.mobile_virtual_room(virtual_room_id=room['virtual_room_id'], virtual_room_name=room['virtual_room_name'], is_valid=room['is_valid'], topN=room['topN'])
        record.save()
    elif(platform == 'pc'):
        record = models.pc_virtual_room(virtual_room_id=room['virtual_room_id'], virtual_room_name=room['virtual_room_name'], is_valid=room['is_valid'], topN=room['topN'])
        record.save()
    return record


def do_stat_virtual_room(platform, record):
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()
    
    virtual_rooms = django_get_virtual_room(platform)
    for virtual_room in virtual_rooms:
        print 'virtual_room_id=%d, %s' % (virtual_room.virtual_room_id, virtual_room.virtual_room_name)
        room_list = django_get_rooms_in_virtual_room(platform, virtual_room.virtual_room_id)
        virtual_room.room_number        = room_list.count()
        virtual_room.ms_number          = 0
        virtual_room.task_number        = 0
        virtual_room.total_disk_space   = 0
        virtual_room.free_disk_space    = 0
        for room in room_list:
            virtual_room.ms_number      += room.ms_number                
            virtual_room.task_number    += room.task_number
            virtual_room.total_disk_space += room.total_disk_space
            virtual_room.free_disk_space  += room.free_disk_space
        virtual_room.save()
                
    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    output = 'now: %s, ' % (end_time)
    output += 'virtual_rooms num: %d, done' % (virtual_rooms.count())
    print output
    record.end_time = end_time
    record.status = 2        
    record.memo = output
    record.save()
    
    
def do_virtual_room_add_tasks(platform, record):
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()

    str_virtual_room_id = record.name
    num_virtual_room_id = string.atoi(str_virtual_room_id)
    virtual_rooms = django_get_virtual_room(platform).filter(virtual_room_id=num_virtual_room_id)   
    if(virtual_rooms.count() == 0):
        record.status = 2
        record.memo = 'virutal_room can not be found by %d' % (num_virtual_room_id)
        record.save()
    virtual_room = virtual_rooms[0]
        
    rooms_in_virutal_room = django_get_rooms_in_virtual_room(platform, num_virtual_room_id) 
    
    room_list = []    
    for one_real_room in rooms_in_virutal_room:                
        room_id = one_real_room.room_id  
        room_topN = one_real_room.topN      
        one_room = room.views.ROOM_T(room_id, room_topN, one_real_room)
        room_list.append(one_room)
    
    rooms_topN = virtual_room.topN
    if(rooms_topN == None):
        record.status = 2
        record.memo = 'virtual_room %d topN is None' % (num_virtual_room_id)
        record.save()
    print 'virtual_room topN: %d' % (rooms_topN)
    
    file_name = '%s_%s.log' % (record.type, str_virtual_room_id)
    log_file = open(file_name, 'w')
    
    (task_list, task_dict) = task.views.get_tasks_sql(platform)    
        
    for one_room in room_list:
        ms_list = room.views.get_ms_list_in_room(platform, one_room.room_id)        
        print 'room_id: %d, ms num: %d' % (one_room.room_id, len(ms_list)) 
        for one_ms in ms_list:
            MS.views.get_ms_space(one_ms)
        log_file.write('room: %d, ms num: %d \n' % (one_room.room_id, len(ms_list)) )
        ms_group = room.ms.MS_GROUP(platform, ms_list)        
        one_room.ms_group = ms_group        
        ms_group.set_log(log_file)
        #ms_all.get_tasks()
        ms_group.get_tasks_macross() 
        ms_group.distribute_topN(task_list, one_room.topN)
        one_room.distribute_num_for_topN = ms_group.get_distribute_num()
    
    for one_room in room_list:
        one_room.init_task_num = one_room.ms_group.get_init_num()
            
    big_ms_group = None
    for one_room in room_list:
        if(big_ms_group == None):
            big_ms_group = one_room.ms_group.copy()
            big_ms_group.set_log(log_file)
        else:
            big_ms_group.combine_group(one_room.ms_group)
    if(big_ms_group == None):
        record.status = 2
        record.memo = 'virutal_room %d contains no one room' % (num_virtual_room_id)
        record.save()
    big_ms_group.distribute_ALL(task_list, rooms_topN)
        
    for one_room in room_list:
        one_room.distribute_num_for_ALL = one_room.ms_group.get_distribute_num()
        
    big_ms_group.do_dispatch()    
    big_ms_group.report_distribute_summary()
            
    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    output = 'now: %s, ' % (end_time)
    for one_room in room_list:
        temp = '[%d, %d, %d, %d, %d, %d]' % (one_room.room_id, one_room.topN, one_room.init_task_num, \
                                             one_room.distribute_num_for_topN, one_room.distribute_num_for_ALL-one_room.distribute_num_for_topN, one_room.distribute_num_for_ALL)
        print temp
        log_file.write('%s\n' % temp)
        output += temp      
    record.end_time = end_time
    record.status = 2        
    record.memo = output
    record.save()

    log_file.close() 
                    
    return True


def one_virtual_room_simulate_add(platform, one_virtual_room):        
    rooms_in_virutal_room = django_get_rooms_in_virtual_room(platform, one_virtual_room.virtual_room_id) 
    
    room_list = []    
    for one_real_room in rooms_in_virutal_room:                
        room_id = one_real_room.room_id  
        room_topN = one_real_room.topN      
        one_room = room.views.ROOM_T(room_id, room_topN, one_real_room)
        room_list.append(one_room)
    
    rooms_topN = one_virtual_room.topN
    if(rooms_topN == None):
        print 'virtual_room %d topN is None' % (one_virtual_room.virtual_room_id)
        return False
    
    file_name = '%s_%d.log' % ('virtual_room_simulate_add', one_virtual_room.virtual_room_id)
    log_file = open(file_name, 'w')
    
    print 'virtual_room: %d, topN: %d' % (one_virtual_room.virtual_room_id, rooms_topN)
    log_file.write('virtual_room: %d, topN: %d\n' % (one_virtual_room.virtual_room_id, rooms_topN))
    
    total_init_num = 0
    total_distribute_num_for_topN   = 0
    total_distribute_num_for_ALL    = 0
    
    (task_list, task_dict) = task.views.get_tasks_sql(platform)    
        
    for one_room in room_list:
        ms_list = room.views.get_ms_list_in_room(platform, one_room.room_id)        
        print 'room_id: %d, ms num: %d' % (one_room.room_id, len(ms_list)) 
        for one_ms in ms_list:
            MS.views.get_ms_space(one_ms)
        log_file.write('room: %d, ms num: %d \n' % (one_room.room_id, len(ms_list)) )
        ms_group = room.ms.MS_GROUP(platform, ms_list)        
        one_room.ms_group = ms_group        
        ms_group.set_log(log_file)
        #ms_all.get_tasks()
        ms_group.get_tasks_macross() 
        ms_group.distribute_topN(task_list, one_room.topN)
        one_room.distribute_num_for_topN = ms_group.get_distribute_num()
        total_distribute_num_for_topN += one_room.distribute_num_for_topN
    
    for one_room in room_list:
        one_room.init_task_num = one_room.ms_group.get_init_num()
        total_init_num += one_room.init_task_num
            
    big_ms_group = None
    for one_room in room_list:
        if(big_ms_group == None):
            big_ms_group = one_room.ms_group.copy()
            big_ms_group.set_log(log_file)
        else:
            big_ms_group.combine_group(one_room.ms_group)
    if(big_ms_group == None):
        print 'virutal_room %d contains no one room' % (one_virtual_room.virtual_room_id)
        log_file.write('virutal_room %d contains no one room\n' % (one_virtual_room.virtual_room_id))
        return False
    big_ms_group.distribute_ALL(task_list, rooms_topN)
        
    for one_room in room_list:
        one_room.distribute_num_for_ALL = one_room.ms_group.get_distribute_num()
        total_distribute_num_for_ALL += one_room.distribute_num_for_ALL
        
    #big_ms_group.do_dispatch()    
    big_ms_group.report_distribute_summary()
    
    for one_room in room_list:
        distribute_num_diff = one_room.distribute_num_for_ALL - one_room.distribute_num_for_topN
        one_room.real_room.add_m = one_room.distribute_num_for_topN
        one_room.real_room.add_N = distribute_num_diff
        one_room.real_room.add_mN = one_room.distribute_num_for_ALL
        one_room.real_room.save()
        print 'room: %d[%s] %d, %d, %d, %d, %d' % (one_room.real_room.room_id, one_room.real_room.room_name, one_room.topN, one_room.init_task_num, \
                                                   one_room.real_room.add_m, one_room.real_room.add_N, one_room.real_room.add_mN)
        log_file.write('room: %d[%s] %d, %d, %d, %d, %d\n' % (one_room.real_room.room_id, one_room.real_room.room_name, one_room.topN, one_room.init_task_num, \
                                                              one_room.real_room.add_m, one_room.real_room.add_N, one_room.real_room.add_mN))
   
    total_distribute_num_diff = total_distribute_num_for_ALL - total_distribute_num_for_topN
    one_virtual_room.add_m = total_distribute_num_for_topN
    one_virtual_room.add_N = total_distribute_num_diff
    one_virtual_room.add_mN = total_distribute_num_for_ALL
    one_virtual_room.save()
    print 'virtual_room: %d[%s] %d, %d, %d, %d, %d' % (one_virtual_room.virtual_room_id, one_virtual_room.virtual_room_name, one_virtual_room.topN, total_init_num, \
                                                       one_virtual_room.add_m, one_virtual_room.add_N, one_virtual_room.add_mN)
    log_file.write('virtual_room: %d[%s] %d, %d, %d, %d, %d\n' % (one_virtual_room.virtual_room_id, one_virtual_room.virtual_room_name, one_virtual_room.topN, total_init_num, \
                                                       one_virtual_room.add_m, one_virtual_room.add_N, one_virtual_room.add_mN))
             
    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    output = 'now: %s, end' % (end_time)    
    print output
    log_file.write('%s\n' % output)
    
    log_file.close()
    return True

    
def do_virtual_room_simulate_add(platform, record):
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()

    virtual_rooms = django_get_virtual_room(platform)
    for one_virtual_room in virtual_rooms:
        one_virtual_room_simulate_add(platform, one_virtual_room)
        
    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    output = 'now: %s, ' % (end_time)     
    record.end_time = end_time
    record.status = 2        
    record.memo = output
    record.save()
                    
    return True


def do_virtual_room_delete_tasks(platform, record):
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()

    str_virtual_room_id = record.name
    num_virtual_room_id = string.atoi(str_virtual_room_id)
    virtual_rooms = django_get_virtual_room(platform).filter(virtual_room_id=num_virtual_room_id)   
    if(virtual_rooms.count() == 0):
        record.status = 2
        record.memo = 'virutal_room can not be found by %d' % (num_virtual_room_id)
        record.save()
    virtual_room = virtual_rooms[0]
        
    rooms_in_virutal_room = django_get_rooms_in_virtual_room(platform, num_virtual_room_id) 
    
    room_list = []    
    for one_real_room in rooms_in_virutal_room:                
        room_id = one_real_room.room_id  
        room_topN = one_real_room.topN      
        one_room = room.views.ROOM_T(room_id, room_topN, one_real_room)
        room_list.append(one_room)
    
    rooms_topN = virtual_room.topN
    if(rooms_topN == None):
        record.status = 2
        record.memo = 'virtual_room %d topN is None' % (num_virtual_room_id)
        record.save()
    print 'virtual_room topN: %d' % (rooms_topN)
    
    file_name = '%s_%s.log' % (record.type, str_virtual_room_id)
    log_file = open(file_name, 'w')
    
    (task_list, task_dict) = task.views.get_tasks_sql(platform)    
        
    for one_room in room_list:
        ms_list = room.views.get_ms_list_in_room(platform, one_room.room_id)
        print 'room_id: %d, ms num: %d' % (one_room.room_id, len(ms_list)) 
        for one_ms in ms_list:
            MS.views.get_ms_space(one_ms)
        log_file.write('room: %d, ms num: %d \n' % (one_room.room_id, len(ms_list)) )
        ms_group = room.ms.MS_GROUP(platform, ms_list)        
        one_room.ms_group = ms_group        
        ms_group.set_log(log_file)
        #ms_all.get_tasks()
        ms_group.get_tasks_macross() 
        ms_group.keep_topN(task_list, one_room.topN)
        one_room.keep_num_for_topN = ms_group.get_keep_num()
    
    for one_room in room_list:
        one_room.init_task_num = one_room.ms_group.get_init_num()
            
    big_ms_group = None
    for one_room in room_list:
        if(big_ms_group == None):
            big_ms_group = one_room.ms_group.copy()
            big_ms_group.set_log(log_file)
        else:
            big_ms_group.combine_group(one_room.ms_group)
    if(big_ms_group == None):
        record.status = 2
        record.memo = 'virtual_room %d contains no room' % (num_virtual_room_id)
        record.save()
    big_ms_group.keep_ALL(task_list, rooms_topN)
        
    for one_room in room_list:
        one_room.keep_num_for_ALL = one_room.ms_group.get_keep_num()
        
    big_ms_group.delete_complement(task_dict)
    big_ms_group.do_delete()    
    big_ms_group.report_delete_summary()
            
    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    output = 'now: %s, ' % (end_time)
    for one_room in room_list:
        keep_num_diff = one_room.keep_num_for_ALL - one_room.keep_num_for_topN
        delete_num = one_room.init_task_num - one_room.keep_num_for_ALL
        temp = '[%d, %d, %d, %d, %d, %d, %d]' % (one_room.room_id, one_room.topN, one_room.init_task_num, \
                                             one_room.keep_num_for_topN, keep_num_diff, one_room.keep_num_for_ALL, delete_num)
        print temp
        log_file.write('%s\n' % temp)
        output += temp      
    record.end_time = end_time
    record.status = 2        
    record.memo = output
    record.save()

    log_file.close() 
                    
    return True


def one_virtual_room_simulate_delete(platform, one_virtual_room):
    rooms_in_virutal_room = django_get_rooms_in_virtual_room(platform, one_virtual_room.virtual_room_id) 
    
    room_list = []    
    for one_real_room in rooms_in_virutal_room:                
        room_id = one_real_room.room_id  
        room_topN = one_real_room.topN      
        one_room = room.views.ROOM_T(room_id, room_topN, one_real_room)
        room_list.append(one_room)
    
    rooms_topN = one_virtual_room.topN
    if(rooms_topN == None):
        print 'virtual_room %d topN is None' % (one_virtual_room.virtual_room_id)
        return False
    
    file_name = '%s_%d.log' % ('virtual_room_simulate_delete', one_virtual_room.virtual_room_id)
    log_file = open(file_name, 'w')
    
    print 'virtual_room: %d, topN: %d' % (one_virtual_room.virtual_room_id, rooms_topN)
    log_file.write('virtual_room: %d, topN: %d\n' % (one_virtual_room.virtual_room_id, rooms_topN))
    
    total_init_num = 0
    total_keep_num_for_topN = 0
    total_keep_num_for_ALL = 0
    
    (task_list, task_dict) = task.views.get_tasks_sql(platform)    
        
    for one_room in room_list:
        ms_list = room.views.get_ms_list_in_room(platform, one_room.room_id)
        print 'room_id: %d, ms num: %d' % (one_room.room_id, len(ms_list)) 
        for one_ms in ms_list:
            MS.views.get_ms_space(one_ms)
        log_file.write('room: %d, ms num: %d \n' % (one_room.room_id, len(ms_list)) )
        ms_group = room.ms.MS_GROUP(platform, ms_list)        
        one_room.ms_group = ms_group        
        ms_group.set_log(log_file)
        #ms_all.get_tasks()
        ms_group.get_tasks_macross() 
        ms_group.keep_topN(task_list, one_room.topN)
        one_room.keep_num_for_topN = ms_group.get_keep_num()
        total_keep_num_for_topN += one_room.keep_num_for_topN
    
    for one_room in room_list:
        one_room.init_task_num = one_room.ms_group.get_init_num()
        total_init_num += one_room.init_task_num
            
    big_ms_group = None
    for one_room in room_list:
        if(big_ms_group == None):
            big_ms_group = one_room.ms_group.copy()
            big_ms_group.set_log(log_file)
        else:
            big_ms_group.combine_group(one_room.ms_group)
    if(big_ms_group == None):
        print 'virtual_room %d contains no room' % (one_virtual_room.virtual_room_id)
        log_file.write('virtual_room %d contains no room\n' % (one_virtual_room.virtual_room_id))
        return False
    big_ms_group.keep_ALL(task_list, rooms_topN)
        
    for one_room in room_list:
        one_room.keep_num_for_ALL = one_room.ms_group.get_keep_num()
        total_keep_num_for_ALL += one_room.keep_num_for_ALL
        
    big_ms_group.delete_complement(task_dict)
    #big_ms_group.do_delete()    
    big_ms_group.report_delete_summary()
    
    for one_room in room_list:
        keep_num_diff = one_room.keep_num_for_ALL - one_room.keep_num_for_topN
        delete_num = one_room.init_task_num - one_room.keep_num_for_ALL
        one_room.real_room.keep_m = one_room.keep_num_for_topN
        one_room.real_room.keep_N = keep_num_diff
        one_room.real_room.keep_mN = one_room.keep_num_for_ALL
        one_room.real_room.delete_mN = delete_num        
        one_room.real_room.save()
        print 'room: %d[%s], %d, %d, %d, %d, %d, %d' % (one_room.room_id, one_room.real_room.room_name, one_room.topN, one_room.init_task_num, \
                                             one_room.keep_num_for_topN, keep_num_diff, one_room.keep_num_for_ALL, delete_num)        
        log_file.write('room: %d[%s], %d, %d, %d, %d, %d, %d\n' % (one_room.room_id, one_room.real_room.room_name, one_room.topN, one_room.init_task_num, \
                                             one_room.keep_num_for_topN, keep_num_diff, one_room.keep_num_for_ALL, delete_num))
              
    total_keep_num_diff = total_keep_num_for_ALL - total_keep_num_for_topN
    one_virtual_room.keep_m = total_keep_num_for_topN
    one_virtual_room.keep_N = total_keep_num_diff
    one_virtual_room.keep_mN = total_keep_num_for_ALL
    one_virtual_room.delete_mN = total_init_num - total_keep_num_for_ALL
    one_virtual_room.save()
    print 'virtual_room: %d[%s] %d, %d, %d, %d, %d' % (one_virtual_room.virtual_room_id, one_virtual_room.virtual_room_name, one_virtual_room.topN, total_init_num, \
                                                       one_virtual_room.add_m, one_virtual_room.add_N, one_virtual_room.add_mN)
    log_file.write('virtual_room: %d[%s] %d, %d, %d, %d, %d\n' % (one_virtual_room.virtual_room_id, one_virtual_room.virtual_room_name, one_virtual_room.topN, total_init_num, \
                                                       one_virtual_room.add_m, one_virtual_room.add_N, one_virtual_room.add_mN))
    
    log_file.close() 
    
    return True


def do_virtual_room_simulate_delete(platform, record):
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()
    
    virtual_rooms = django_get_virtual_room(platform)
    for one_virtual_room in virtual_rooms:
        one_virtual_room_simulate_delete(platform, one_virtual_room)
            
    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    output = 'now: %s end' % (end_time)    
    record.end_time = end_time
    record.status = 2        
    record.memo = output
    record.save()
                    
    return True


def one_virtual_room_percent_topN(platform, one_virtual_room):
    rooms_in_virutal_room = django_get_rooms_in_virtual_room(platform, one_virtual_room.virtual_room_id) 
    
    room_list = []    
    for one_real_room in rooms_in_virutal_room:                
        room_id = one_real_room.room_id  
        room_topN = one_real_room.topN      
        one_room = room.views.ROOM_T(room_id, room_topN, one_real_room)
        room_list.append(one_room)
    
    file_name = '%s_%d.log' % ('one_virtual_room_percent_topN', one_virtual_room.virtual_room_id)
    log_file = open(file_name, 'w')
    
    print 'virtual_room: %d[%s]' % (one_virtual_room.virtual_room_id, one_virtual_room.virtual_room_name)
    log_file.write('virtual_room: %d[%s]\n' % (one_virtual_room.virtual_room_id, one_virtual_room.virtual_room_name))
    
    topN1 = 50000
    topN2 = 100000
    topN3 = 200000
    
    (task_list, task_dict) = task.views.get_tasks_sql(platform)    
        
    for one_room in room_list:
        ms_list = room.views.get_ms_list_in_room(platform, one_room.room_id)
        print 'room_id: %d, ms num: %d' % (one_room.room_id, len(ms_list)) 
        log_file.write('room: %d, ms num: %d \n' % (one_room.room_id, len(ms_list)) )
        ms_group = room.ms.MS_GROUP(platform, ms_list)        
        one_room.ms_group = ms_group        
        ms_group.set_log(log_file)
        #ms_all.get_tasks()
        ms_group.get_tasks_macross() 
        # todo:
        ms_group.percent_topNNN_for_ms(task_list)
        ms_group.percent_topNNN_for_group(task_list)
        one_room.real_room.percent_50k  = 100.0*float(ms_group.find_num_topN_50k)/float(topN1)
        one_room.real_room.percent_100k = 100.0*float(ms_group.find_num_topN_100k)/float(topN2)
        one_room.real_room.percent_200k = 100.0*float(ms_group.find_num_topN_200k)/float(topN3)
        one_room.real_room.save()
        print 'room: %d[%s] %f, %f, %f' % (one_room.real_room.room_id, one_room.real_room.room_name, \
                                                       one_room.real_room.percent_50k, one_room.real_room.percent_100k, one_room.real_room.percent_200k)
        log_file.write('room: %d[%s] %f, %f, %f\n' % (one_room.real_room.room_id, one_room.real_room.room_name, \
                                                       one_room.real_room.percent_50k, one_room.real_room.percent_100k, one_room.real_room.percent_200k))
              
    big_ms_group = None
    for one_room in room_list:
        if(big_ms_group == None):
            big_ms_group = one_room.ms_group.copy()
            big_ms_group.set_log(log_file)
        else:
            big_ms_group.combine_group(one_room.ms_group)
    if(big_ms_group == None):
        print 'virtual_room %d contains no room' % (one_virtual_room.virtual_room_id)
        log_file.write('virtual_room %d contains no room\n' % (one_virtual_room.virtual_room_id))
        return False
    big_ms_group.percent_topNNN_for_group(task_list)
    one_virtual_room.percent_50k  = 100.0*float(ms_group.find_num_topN_50k)/float(topN1)
    one_virtual_room.percent_100k = 100.0*float(ms_group.find_num_topN_100k)/float(topN2)
    one_virtual_room.percent_200k = 100.0*float(ms_group.find_num_topN_200k)/float(topN3)
    one_virtual_room.save()   
    print  'virtual_room: %d[%s] %f, %f, %f' % (one_virtual_room.virtual_room_id, one_virtual_room.virtual_room_name, \
                                                       one_virtual_room.percent_50k, one_virtual_room.percent_100k, one_virtual_room.percent_200k)
    log_file.write('virtual_room: %d[%s] %f, %f, %f\n' % (one_virtual_room.virtual_room_id, one_virtual_room.virtual_room_name, \
                                                       one_virtual_room.percent_50k, one_virtual_room.percent_100k, one_virtual_room.percent_200k))
    
    log_file.close() 
    
    return True


def do_virtual_room_percent_topN(platform, record):
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()
    
    virtual_rooms = django_get_virtual_room(platform)
    for one_virtual_room in virtual_rooms:
        one_virtual_room_percent_topN(platform, one_virtual_room)               
            
    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    output = 'now: %s end' % (end_time)    
    record.end_time = end_time
    record.status = 2        
    record.memo = output
    record.save()
                    
    return True


def add_virtual_room(request, platform):
    print 'add_virtual_room'
    print request.REQUEST
    #{u'virtual_room_id': u'0', u'virtual_room_name': u'input name', u'is_valid': u'1', u'topN': u'100000'}
    virtual_room_id     = string.atoi(request.REQUEST['virtual_room_id'])
    virtual_room_name   = request.REQUEST['virtual_room_name']
    is_valid            = string.atoi(request.REQUEST['is_valid'])
    topN                = string.atoi(request.REQUEST['topN'])
    
    return_datas = {}
    output = ''
    records = get_virtual_room_by_id(platform, virtual_room_id)
    if(len(records) > 0):          
        for record in records:
            output += 'exist, id=%d, name=%s, valid=%d, topN=%d' % (record.virtual_room_id, record.virtual_room_name, record.is_valid, record.topN)
        return_datas['success'] = False
        return_datas['data'] = output
        return HttpResponse(json.dumps(return_datas))
    
    one_room = {}
    one_room['virtual_room_id']     = virtual_room_id
    one_room['virtual_room_name']   = virtual_room_name
    one_room['is_valid']            = is_valid
    one_room['topN']                = topN
        
    record = add_virtual_room_by_dict(platform, one_room)
    if(record == None):
        output += 'add failure'
        return_datas['success'] = False
        return_datas['data'] = output
        return HttpResponse(json.dumps(return_datas)) 
        
    output += 'add success, id=%d, name=%s, valid=%d, topN=%d' % (record.virtual_room_id, record.virtual_room_name, record.is_valid, record.topN)
    return_datas['success'] = True
    return_datas['data'] = output        
    return HttpResponse(json.dumps(return_datas))


def modify_virtual_room(request, platform):
    print 'modify_virtual_room'
    print request.REQUEST
    #{u'virtual_room_id': u'0', u'virtual_room_name': u'input name', u'is_valid': u'1', u'topN': u'100000'}
    virtual_room_id     = string.atoi(request.REQUEST['virtual_room_id'])
    virtual_room_name   = request.REQUEST['virtual_room_name']
    is_valid            = string.atoi(request.REQUEST['is_valid'])
    topN                = string.atoi(request.REQUEST['topN'])
    
    return_datas = {}
    output = ''
    records = get_virtual_room_by_id(platform, virtual_room_id)
    if(len(records) == 0):          
        output += 'non-exist, id=%d' % (virtual_room_id)
        return_datas['success'] = False
        return_datas['data'] = output
        return HttpResponse(json.dumps(return_datas))
   
    record = records[0]
    record.virtual_room_id     = virtual_room_id
    record.virtual_room_name   = virtual_room_name
    record.is_valid            = is_valid
    record.topN                = topN    
    record.save()
    
    room_list = django_get_rooms_in_virtual_room(platform, virtual_room_id)
    for one_room in room_list:
        one_room.virtual_room_id = virtual_room_id
        one_room.virtual_room_name = virtual_room_name
        one_room.save()
        
    output += 'modify success, id=%d, name=%s, valid=%d, topN=%d' % (record.virtual_room_id, record.virtual_room_name, record.is_valid, record.topN)
    return_datas['success'] = True
    return_datas['data'] = output        
    return HttpResponse(json.dumps(return_datas))


def delete_virtual_room(request, platform):
    print 'delete_virtual_room'
    print request.REQUEST
    #{u'virtual_room_id': u'0', u'virtual_room_name': u'input name', u'is_valid': u'1', u'topN': u'100000'}
    virtual_room_id     = string.atoi(request.REQUEST['virtual_room_id'])
    virtual_room_name   = request.REQUEST['virtual_room_name']
    is_valid            = string.atoi(request.REQUEST['is_valid'])
    topN                = string.atoi(request.REQUEST['topN'])
    
    return_datas = {}
    output = ''
    records = get_virtual_room_by_id(platform, virtual_room_id)
    if(len(records) == 0):          
        output += 'non-exist, id=%d' % (virtual_room_id)
        return_datas['success'] = False
        return_datas['data'] = output
        return HttpResponse(json.dumps(return_datas))
    
    record = records[0] 
    record.delete()
    
    room_list = django_get_rooms_in_virtual_room(platform, virtual_room_id)
    for one_room in room_list:
        one_room.virtual_room_id = -1
        one_room.virtual_room_name = 'NotExist'
        one_room.save()
        
    output += 'delete success, id=%d, name=%s, valid=%d, topN=%d' % (virtual_room_id, virtual_room_name, is_valid, topN)
    return_datas['success'] = True
    return_datas['data'] = output        
    return HttpResponse(json.dumps(return_datas))


def stat_virtual_room(request, platform):
    print 'stat_virtual_room'
    print request.REQUEST    
    
    start_now = False
    if 'start_now' in request.REQUEST:
        if(request.REQUEST['start_now'] == 'on'):
            start_now = True
    
    now_time = time.localtime(time.time())
    today = time.strftime("%Y-%m-%d", now_time)
    dispatch_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    
     
    operation1 = {}
    operation1['type'] = 'stat_virtual_room'
    operation1['name'] = today
    operation1['user'] = request.user.username
    operation1['dispatch_time'] = dispatch_time
    operation1['memo'] = ''
            
    return_datas = {}
    output = ''
    records = operation.views.get_operation_undone_by_type(platform, operation1['type'])
    if(len(records) > 0):          
        for record in records:
            output += 'operation exist, id=%d, type=%s, name=%s, dispatch_time=%s, status=%d' % (record.id, record.type, record.name, record.dispatch_time, record.status)
        return_datas['success'] = False
        return_datas['data'] = output
        return HttpResponse(json.dumps(return_datas))
   
    record = operation.views.create_operation_record_by_dict(platform, operation1)
    if(record == None):
        output += 'operation create failure'
        return_datas['success'] = False
        return_datas['data'] = output
        return HttpResponse(json.dumps(return_datas)) 
        
    output += 'operation add, id=%d, type=%s, name=%s, dispatch_time=%s, status=%d' % (record.id, record.type, record.name, record.dispatch_time, record.status)
    return_datas['success'] = True
    return_datas['data'] = output
        
    if(start_now == True):
        # start process
        p = Process(target=do_stat_virtual_room, args=(platform, record))
        p.start()
    
    str_datas = json.dumps(return_datas)
    response = HttpResponse(str_datas, mimetype='application/json;charset=UTF-8')
    response['Content-Length'] = len(str_datas)
    return response

        
def get_virtual_room_list(request, platform):
    print 'get_virtual_room_list'
    print request.REQUEST
        
    start = '0'
    if 'start' in request.REQUEST:
        start = request.REQUEST['start']
    limit = '100'
    if 'limit' in request.REQUEST:
        limit = request.REQUEST['limit']
    start_index = string.atoi(start)
    limit_num = string.atoi(limit)
    
    kwargs = {}
    
    v_virtual_room_id = ''
    if 'virtual_room_id' in request.REQUEST:
        v_virtual_room_id = request.REQUEST['virtual_room_id']
    if(v_virtual_room_id != ''):
        kwargs['virtual_room_id'] = v_virtual_room_id
        
    v_virtual_room_name = ''
    if 'virtual_room_name' in request.REQUEST:
        v_virtual_room_name = request.REQUEST['virtual_room_name']
    if(v_virtual_room_name != ''):
        kwargs['virtual_room_name__contains'] = v_virtual_room_name
    
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
    
    rooms = django_get_virtual_room(platform)
    rooms1 = rooms.filter(**kwargs)
    rooms2 = None
    if(len(order_condition) > 0):
        rooms2 = rooms1.order_by(order_condition)[start_index:start_index+limit_num]
    else:
        rooms2 = rooms1[start_index:start_index+limit_num]
    
    return_datas = {'success':True, 'data':[]}
    return_datas['total_count'] = rooms1.count()
    for room in rooms2:
        return_datas['data'].append(room.todict())
        
    return HttpResponse(json.dumps(return_datas))


def show_virtual_room_detail(request, platform):  
    output = ''
    ids = request.REQUEST['ids']    
    id_list = ids.split(',')
    for virtual_room_id in id_list:                         
        room_list = django_get_rooms_in_virtual_room(platform, virtual_room_id)
        title = '<h1>id: %s, room_num: %d</h1>' % (virtual_room_id, room_list.count())
        output += title        
        for room in room_list:
            output += '%s,%s,%s,%s,%s,%s,%s<br>' \
            % (str(room.room_id), str(room.room_name), str(room.ms_number), str(room.task_number), \
               str(room.total_disk_space), str(room.free_disk_space), str(room.topN))
    return HttpResponse(output)


def virtual_room_add_tasks(request, platform):
    print 'virtual_room_add_tasks'
    print request.REQUEST    
    
    virtual_room_id = request.REQUEST['virtual_room_id']
    
    start_now = False
    if 'start_now' in request.REQUEST:
        if(request.REQUEST['start_now'] == 'on'):
            start_now = True
        
    now_time = time.localtime(time.time())    
    dispatch_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)    
     
    operation1 = {}
    operation1['type'] = 'virtual_room_add_tasks'
    operation1['name'] = virtual_room_id
    operation1['user'] = request.user.username
    operation1['dispatch_time'] = dispatch_time
    operation1['memo'] = ''
            
    return_datas = {}
    output = ''
    records = operation.views.get_operation_undone_by_type_name(platform, operation1['type'], operation1['name'])
    if(len(records) > 0):          
        for record in records:
            output += 'operation exist, id=%d, type=%s, name=%s, dispatch_time=%s, status=%d' % (record.id, record.type, record.name, record.dispatch_time, record.status)
        return_datas['success'] = False
        return_datas['data'] = output
        return HttpResponse(json.dumps(return_datas))
   
    record = operation.views.create_operation_record_by_dict(platform, operation1)
    if(record == None):
        output += 'operation create failure'
        return_datas['success'] = False
        return_datas['data'] = output
        return HttpResponse(json.dumps(return_datas)) 
        
    output += 'operation add, id=%d, type=%s, name=%s, dispatch_time=%s, status=%d' % (record.id, record.type, record.name, record.dispatch_time, record.status)
    return_datas['success'] = True
    return_datas['data'] = output
        
    if(start_now == True):
        # start process
        p = Process(target=do_virtual_room_add_tasks, args=(platform, record))
        p.start()
    
    str_datas = json.dumps(return_datas)
    response = HttpResponse(str_datas, mimetype='application/json;charset=UTF-8')
    response['Content-Length'] = len(str_datas)
    return response



def virtual_room_delete_tasks(request, platform):
    print 'virtual_room_delete_tasks'
    print request.REQUEST    
    
    virtual_room_id = request.REQUEST['virtual_room_id']
    
    start_now = False
    if 'start_now' in request.REQUEST:
        if(request.REQUEST['start_now'] == 'on'):
            start_now = True
        
    now_time = time.localtime(time.time())    
    dispatch_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)    
     
    operation1 = {}
    operation1['type'] = 'virtual_room_delete_tasks'
    operation1['name'] = virtual_room_id
    operation1['user'] = request.user.username
    operation1['dispatch_time'] = dispatch_time
    operation1['memo'] = ''
            
    return_datas = {}
    output = ''
    records = operation.views.get_operation_undone_by_type_name(platform, operation1['type'], operation1['name'])
    if(len(records) > 0):          
        for record in records:
            output += 'operation exist, id=%d, type=%s, name=%s, dispatch_time=%s, status=%d' % (record.id, record.type, record.name, record.dispatch_time, record.status)
        return_datas['success'] = False
        return_datas['data'] = output
        return HttpResponse(json.dumps(return_datas))
   
    record = operation.views.create_operation_record_by_dict(platform, operation1)
    if(record == None):
        output += 'operation create failure'
        return_datas['success'] = False
        return_datas['data'] = output
        return HttpResponse(json.dumps(return_datas)) 
        
    output += 'operation add, id=%d, type=%s, name=%s, dispatch_time=%s, status=%d' % (record.id, record.type, record.name, record.dispatch_time, record.status)
    return_datas['success'] = True
    return_datas['data'] = output
        
    if(start_now == True):
        # start process
        p = Process(target=do_virtual_room_delete_tasks, args=(platform, record))
        p.start()
    
    str_datas = json.dumps(return_datas)
    response = HttpResponse(str_datas, mimetype='application/json;charset=UTF-8')
    response['Content-Length'] = len(str_datas)
    return response


def virtual_room_simulate_add(request, platform):
    print 'virtual_room_simulate_add'
    print request.REQUEST    
    
    #virtual_room_id = request.REQUEST['virtual_room_id']
    
    start_now = False
    if 'start_now' in request.REQUEST:
        if(request.REQUEST['start_now'] == 'on'):
            start_now = True
        
    now_time = time.localtime(time.time())    
    dispatch_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)    
     
    operation1 = {}
    operation1['type'] = 'virtual_room_simulate_add'
    operation1['name'] = 'ALL'
    operation1['user'] = request.user.username
    operation1['dispatch_time'] = dispatch_time
    operation1['memo'] = ''
            
    return_datas = {}
    output = ''
    records = operation.views.get_operation_undone_by_type_name(platform, operation1['type'], operation1['name'])
    if(len(records) > 0):          
        for record in records:
            output += 'operation exist, id=%d, type=%s, name=%s, dispatch_time=%s, status=%d' % (record.id, record.type, record.name, record.dispatch_time, record.status)
        return_datas['success'] = False
        return_datas['data'] = output
        return HttpResponse(json.dumps(return_datas))
   
    record = operation.views.create_operation_record_by_dict(platform, operation1)
    if(record == None):
        output += 'operation create failure'
        return_datas['success'] = False
        return_datas['data'] = output
        return HttpResponse(json.dumps(return_datas)) 
        
    output += 'operation add, id=%d, type=%s, name=%s, dispatch_time=%s, status=%d' % (record.id, record.type, record.name, record.dispatch_time, record.status)
    return_datas['success'] = True
    return_datas['data'] = output
        
    if(start_now == True):
        # start process
        p = Process(target=do_virtual_room_simulate_add, args=(platform, record))
        p.start()
    
    str_datas = json.dumps(return_datas)
    response = HttpResponse(str_datas, mimetype='application/json;charset=UTF-8')
    response['Content-Length'] = len(str_datas)
    return response


def virtual_room_simulate_delete(request, platform):
    print 'virtual_room_simulate_delete'
    print request.REQUEST    
    
    #virtual_room_id = request.REQUEST['virtual_room_id']
    
    start_now = False
    if 'start_now' in request.REQUEST:
        if(request.REQUEST['start_now'] == 'on'):
            start_now = True
        
    now_time = time.localtime(time.time())    
    dispatch_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)    
     
    operation1 = {}
    operation1['type'] = 'virtual_room_simulate_delete'
    operation1['name'] = 'ALL'
    operation1['user'] = request.user.username
    operation1['dispatch_time'] = dispatch_time
    operation1['memo'] = ''
            
    return_datas = {}
    output = ''
    records = operation.views.get_operation_undone_by_type_name(platform, operation1['type'], operation1['name'])
    if(len(records) > 0):          
        for record in records:
            output += 'operation exist, id=%d, type=%s, name=%s, dispatch_time=%s, status=%d' % (record.id, record.type, record.name, record.dispatch_time, record.status)
        return_datas['success'] = False
        return_datas['data'] = output
        return HttpResponse(json.dumps(return_datas))
   
    record = operation.views.create_operation_record_by_dict(platform, operation1)
    if(record == None):
        output += 'operation create failure'
        return_datas['success'] = False
        return_datas['data'] = output
        return HttpResponse(json.dumps(return_datas)) 
        
    output += 'operation add, id=%d, type=%s, name=%s, dispatch_time=%s, status=%d' % (record.id, record.type, record.name, record.dispatch_time, record.status)
    return_datas['success'] = True
    return_datas['data'] = output
        
    if(start_now == True):
        # start process
        p = Process(target=do_virtual_room_simulate_delete, args=(platform, record))
        p.start()
    
    str_datas = json.dumps(return_datas)
    response = HttpResponse(str_datas, mimetype='application/json;charset=UTF-8')
    response['Content-Length'] = len(str_datas)
    return response


def virtual_room_percent_topN(request, platform):
    print 'virtual_room_percent_topN'
    print request.REQUEST    
    
    #virtual_room_id = request.REQUEST['virtual_room_id']
    
    start_now = False
    if 'start_now' in request.REQUEST:
        if(request.REQUEST['start_now'] == 'on'):
            start_now = True
        
    now_time = time.localtime(time.time())    
    dispatch_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)    
     
    operation1 = {}
    operation1['type'] = 'virtual_room_percent_topN'
    operation1['name'] = 'ALL'
    operation1['user'] = request.user.username
    operation1['dispatch_time'] = dispatch_time
    operation1['memo'] = ''
            
    return_datas = {}
    output = ''
    records = operation.views.get_operation_undone_by_type_name(platform, operation1['type'], operation1['name'])
    if(len(records) > 0):          
        for record in records:
            output += 'operation exist, id=%d, type=%s, name=%s, dispatch_time=%s, status=%d' % (record.id, record.type, record.name, record.dispatch_time, record.status)
        return_datas['success'] = False
        return_datas['data'] = output
        return HttpResponse(json.dumps(return_datas))
   
    record = operation.views.create_operation_record_by_dict(platform, operation1)
    if(record == None):
        output += 'operation create failure'
        return_datas['success'] = False
        return_datas['data'] = output
        return HttpResponse(json.dumps(return_datas)) 
        
    output += 'operation add, id=%d, type=%s, name=%s, dispatch_time=%s, status=%d' % (record.id, record.type, record.name, record.dispatch_time, record.status)
    return_datas['success'] = True
    return_datas['data'] = output
        
    if(start_now == True):
        # start process
        p = Process(target=do_virtual_room_percent_topN, args=(platform, record))
        p.start()
    
    str_datas = json.dumps(return_datas)
    response = HttpResponse(str_datas, mimetype='application/json;charset=UTF-8')
    response['Content-Length'] = len(str_datas)
    return response


def get_max_virtual_room_id(request, platform):
    print 'get_max_virtual_room_id'
    print request.REQUEST
    
    max_virtual_room_id = 0
    
    virtual_rooms = django_get_virtual_room(platform)
    virtual_rooms2 = virtual_rooms.order_by('-virtual_room_id')
    if(virtual_rooms2.count() == 0):
        max_virtual_room_id = 0
    else:
        virtual_room = virtual_rooms2[0]
        max_virtual_room_id = virtual_room.virtual_room_id
    
    return_datas = {}
    return_datas['success'] = True
    return_datas['data'] = str(max_virtual_room_id)
    
    str_datas = json.dumps(return_datas)
    response = HttpResponse(str_datas, mimetype='application/json;charset=UTF-8')
    response['Content-Length'] = len(str_datas)
    return response
    
