#coding=utf-8
import MS.views
import room.views
import room.ms

def hot_tasks_from_file(file_name):
    print 'hot_tasks_from_file %s' % (file_name)
    
    task_list = []
    hits_file = open(file_name, "r")
    
    line_num = 0 
    while(True): 
        line = hits_file.readline()         
        if(line == ''):
            break           
        items = line.split(' ')
        if(len(items) >= 2):
            hash_id = items[0].strip()
            hits_num = items[1].strip()
            #print '%s, %s' % (hits_num, hash_id)
            task_list.append(hash_id)
        line_num += 1        
        
    hits_file.close()   
    print '%s: line_num=%d, task_num=%d' % (file_name, line_num, len(task_list))
    return task_list


def hot_tasks_to_rooms(platform, file_name):    
    log_file = open('hot_tasks_to_rooms.log', 'w')
    log_file.write('platform=%s, file_name=%s\n' % (platform, file_name))
    
    task_list = hot_tasks_from_file(file_name)
    log_file.write('task_num=%d\n' % (len(task_list)))
    
    ms_list = MS.views.get_ms_local(platform)
    
    room_list = room.views.get_room_local(platform)
    target_room_list = room_list.filter(ms_number__gte=5)
    
    for one_room in target_room_list:
        one_room_id = one_room.room_id
        room_name = one_room.room_name
        ms_num = one_room.ms_number
        log_file.write('room_id=%d, room_name=%s, ms_num=%d\n' % (one_room_id, room_name, ms_num)) 
               
        target_ms_list = ms_list.filter(room_id=one_room_id)
        for one_ms in target_ms_list:
            log_file.write('ms_id=%d, ms_ip=%s, is_dispatch=%d\n' % (one_ms.server_id, one_ms.controll_ip, one_ms.is_dispatch)) 
        
        ms_all = room.ms.MS_GROUP(platform, target_ms_list)
        
        for one_task in task_list:
            ms_info = ms_all.dispatch_hot_task(one_task)
            if(ms_info == None):
                print 'room_id=%d, ms_num=%d, dispatch %s failure!' % (one_room_id, ms_num, one_task)
            else:
                log_file.write('hash=%s, ms=%d, %s\n' % (one_task, ms_info.db_record.server_id, ms_info.db_record.controll_ip)) 
        ms_all.do_dispatch()
    
    log_file.close()    
    return True