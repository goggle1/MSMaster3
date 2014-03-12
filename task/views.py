#coding=utf-8
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response,RequestContext
import json
import models
import string
import time
import sys
import DB.db
#from DB.db import DB_MYSQL
#from DB.db import DB_CONFIG
#from DB.db import *
import operation.views
import config.views
import threading
import datetime
import math
from multiprocessing import Process
import urllib2
import json

def day_diff(date1, date2):
    d1 = datetime.datetime(string.atoi(date1[0:4]), string.atoi(date1[5:7]), string.atoi(date1[8:10]))
    d2 = datetime.datetime(string.atoi(date2[0:4]), string.atoi(date2[5:7]), string.atoi(date2[8:10]))
    return (d1-d2).days


def task_hits_insert(platform, hash_id, v_time, v_hits_num):
    if(platform == 'mobile'):
        hash_local = models.mobile_task_hits(hash       = hash_id,      \
                                        time            = v_time,       \
                                        hits_num        = v_hits_num    \
                                        ) 
        hash_local.save()
    elif(platform == 'pc'):
        hash_local = models.pc_task_hits(hash           = hash_id,      \
                                        time            = v_time,       \
                                        hits_num        = v_hits_num    \
                                        ) 
        hash_local.save()
        

def task_temperature_insert(platform, hash_id, v_online_time, v_is_valid, v_filesize, v0, v1, v2, v3, v4, v5, v6, v7):
    if(platform == 'mobile'):
        hash_local = models.mobile_task_temperature(hash= hash_id,          \
                                        online_time     = v_online_time,    \
                                        is_valid        = v_is_valid,       \
                                        filesize        = v_filesize,       \
                                        temperature0    = v0,               \
                                        temperature1    = v1,               \
                                        temperature2    = v2,               \
                                        temperature3    = v3,               \
                                        temperature4    = v4,               \
                                        temperature5    = v5,               \
                                        temperature6    = v6,               \
                                        temperature7    = v7               \
                                        ) 
        hash_local.save()
    elif(platform == 'pc'):
        hash_local = models.pc_task_temperature(hash= hash_id,          \
                                        online_time     = v_online_time,    \
                                        is_valid        = v_is_valid,       \
                                        filesize        = v_filesize,       \
                                        temperature0    = v0,               \
                                        temperature1    = v1,               \
                                        temperature2    = v2,               \
                                        temperature3    = v3,               \
                                        temperature4    = v4,               \
                                        temperature5    = v5,               \
                                        temperature6    = v6,               \
                                        temperature7    = v7               \
                                        ) 
        hash_local.save()
        
    

def get_tasks_local(platform):
    task_list = None
    if(platform == 'mobile'):
        task_list = models.mobile_task_temperature.objects.all()
    elif(platform == 'pc'):
        task_list = models.pc_task_temperature.objects.all()    
    return task_list

def get_tasks_hits(platform):
    task_list = None
    if(platform == 'mobile'):
        task_list = models.mobile_task_hits.objects.all()
    elif(platform == 'pc'):
        task_list = models.pc_task_hits.objects.all()    
    return task_list


def get_tasks_sql(platform):
    task_list = []
    task_dict = {}
    
    db = DB.db.DB_MYSQL()
    db.connect(DB.db.MS2_DB_CONFIG.host, DB.db.MS2_DB_CONFIG.port, DB.db.MS2_DB_CONFIG.user, DB.db.MS2_DB_CONFIG.password, DB.db.MS2_DB_CONFIG.db)
  
    sql = "SELECT hash, online_time, filesize, temperature0, PayOrFree FROM %s_task_temperature ORDER BY PayOrFree DESC, temperature0 DESC, online_time DESC" % (platform)         
    print sql
    db.execute(sql)
    
    for row in db.cur.fetchall():
        task1 = {}      
        col_num = 0  
        for r in row:
            if(col_num == 0):
                task1['hash'] = r
            elif(col_num == 1):
                task1['online_time'] = r            
            elif(col_num == 2):
                task1['filesize'] = r
            elif(col_num == 3):
                task1['temperature0'] = r
            elif(col_num == 4):
                task1['PayOrFree'] = r
            col_num += 1
        #print 'task: %s, %s, %d, %e' % (task1['hash'], str(task1['online_time']), task1['filesize'], task1['temperature0'])
        task_list.append(task1)
        task_dict[task1['hash']] = task1
    
    db.close()
        
    print 'task_list num: %d' % (len(task_list)) 
    return (task_list, task_dict)


def get_cold_tasks_rule1(platform):
    task_list = []
    
    db = DB.db.DB_MYSQL()
    db.connect(DB.db.MS_DB_CONFIG.host, DB.db.MS_DB_CONFIG.port, DB.db.MS_DB_CONFIG.user, DB.db.MS_DB_CONFIG.password, DB.db.MS_DB_CONFIG.db)
  
    sql = "SELECT hash, online_time, is_valid, filesize, hot, cold1, cold2, cold3, last_hit_time, total_hits_num FROM %s_task ORDER BY cold1 ASC, hot ASC" % (platform)         
    print sql
    db.execute(sql)
    
    for row in db.cur.fetchall():
        task1 = {}      
        col_num = 0  
        for r in row:
            if(col_num == 0):
                task1['hash'] = r
            elif(col_num == 1):
                task1['online_time'] = r
            elif(col_num == 2):
                task1['is_valid'] = r
            elif(col_num == 3):
                task1['filesize'] = r
            elif(col_num == 4):
                task1['hot'] = r
            elif(col_num == 5):
                task1['cold1'] = r
            elif(col_num == 6):
                task1['cold2'] = r
            elif(col_num == 7):
                task1['cold3'] = r
            elif(col_num == 8):
                task1['last_hit_time'] = r
            elif(col_num == 9):
                task1['total_hits_num'] = r
            col_num += 1
        task_list.append(task1)
     
    return task_list


def get_cold_tasks_rule2(platform, time_limit):
    task_list = []
    
    db = DB.db.DB_MYSQL()
    db.connect(DB.db.MS_DB_CONFIG.host, DB.db.MS_DB_CONFIG.port, DB.db.MS_DB_CONFIG.user, DB.db.MS_DB_CONFIG.password, DB.db.MS_DB_CONFIG.db)
  
    sql = "SELECT hash, online_time, is_valid, filesize, hot, cold1, cold2, cold3, last_hit_time, total_hits_num FROM %s_task where online_time < '%s' ORDER BY hot ASC" % (platform, time_limit)         
    print sql
    db.execute(sql)
    
    for row in db.cur.fetchall():
        task1 = {}      
        col_num = 0  
        for r in row:
            if(col_num == 0):
                task1['hash'] = r
            elif(col_num == 1):
                task1['online_time'] = r
            elif(col_num == 2):
                task1['is_valid'] = r
            elif(col_num == 3):
                task1['filesize'] = r
            elif(col_num == 4):
                task1['hot'] = r
            elif(col_num == 5):
                task1['cold1'] = r
            elif(col_num == 6):
                task1['cold2'] = r
            elif(col_num == 7):
                task1['cold3'] = r
            elif(col_num == 8):
                task1['last_hit_time'] = r
            elif(col_num == 9):
                task1['total_hits_num'] = r
            col_num += 1
        task_list.append(task1)
     
    return task_list


def get_tasks_by_hash(platform, hash_id):
    task_list = None
    if(platform == 'mobile'):
        task_list = models.mobile_task.objects.filter(hash=hash_id)
    elif(platform == 'pc'):
        task_list = models.pc_task.objects.filter(hash=hash_id)  
    return task_list
        

def get_task_list(request, platform):
    print 'get_task_list'
    print request.REQUEST
            
    start = request.REQUEST['start']
    limit = request.REQUEST['limit']    
    start_index = string.atoi(start)
    limit_num = string.atoi(limit)
    print '%d,%d' % (start_index, limit_num)
    
    kwargs = {}
    
    hash_id = ''
    if(request.REQUEST.has_key('hash') == True):
        hash_id = request.REQUEST['hash']
    if(hash_id != ''):
        kwargs['hash'] = hash_id
    
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
    
    tasks = get_tasks_local(platform)
    tasks1 = tasks.filter(**kwargs)
    tasks2 = None    
    if(len(order_condition) > 0):
        tasks2 = tasks1.order_by(order_condition)[start_index:start_index+limit_num]     
    else:        
        tasks2 = tasks1[start_index:start_index+limit_num]
            
    return_datas = {'success':True, 'data':[]}    
    return_datas['total_count'] = tasks1.count()
    
    for task in tasks2:        
        return_datas['data'].append(task.todict())
        
    return HttpResponse(json.dumps(return_datas))


def down_hot_tasks(request, platform):
    print 'down_hot_tasks'
    print request.REQUEST    
    task_num = request.REQUEST['task_num']
    
    tasks = get_tasks_local(platform) 
    tasks2 = tasks.order_by('-temperature0')[0:task_num]
    
    output = ''
    for task in tasks2:
        output += '%s,%s,%e\n' % (task.hash, task.online_time, task.temperature0)
            
    response = HttpResponse(output, content_type='text/comma-separated-values')
    response['Content-Disposition'] = 'attachment; filename=hot_tasks_%s_%s.csv' % (platform, task_num)
    return response


def down_cold_tasks(request, platform):
    print 'down_cold_tasks'
    print request.REQUEST  
      
    task_num = request.REQUEST['task_num']
        
    tasks = get_tasks_local(platform)  
    tasks2 = tasks.order_by('temperature0')[0:task_num]
       
    output = ''
    for task in tasks2:
        output += '%s,%s,%e\n' % (task.hash, task.online_time, task.temperature0)
    
    response = HttpResponse(output, content_type='text/comma-separated-values')
    response['Content-Disposition'] = 'attachment; filename=cold_tasks_%s_%s.csv' % (platform, task_num)
    return response


def get_tasks_macross_mobile(begin_date, end_date):
    task_list = []
    sql = ""
    
    #reload(sys)
    #sys.setdefaultencoding('utf8')
    where_condition = ''
    if(len(begin_date) > 0):
        begin_time = '%s-%s-%s 00:00:00' % (begin_date[0:4], begin_date[4:6], begin_date[6:8])
        where_condition += " where create_time >= '%s'" % (begin_time)
    if(len(end_date) > 0):
        end_time = '%s-%s-%s 00:00:00' % (end_date[0:4], end_date[4:6], end_date[6:8])
        where_condition += " and create_time < '%s'" % (end_time)
    
    db = DB.db.DB_MYSQL()
    db.connect(DB.db.DB_CONFIG.host, DB.db.DB_CONFIG.port, DB.db.DB_CONFIG.user, DB.db.DB_CONFIG.password, DB.db.DB_CONFIG.db)
        
    #sql = "select dat_hash, create_time, filesize from fs_mobile_dat where state!='dismissed' " + where_condition           
    sql = "select dat_hash, create_time, filesize from fs_mobile_dat" + where_condition
    print sql
    db.execute(sql)
    
    for row in db.cur.fetchall():
        task1 = {}      
        col_num = 0  
        for r in row:
            if(col_num == 0):
                task1['hash'] = r
            elif(col_num == 1):
                task1['online_time'] = r
            elif(col_num == 2):
                task1['filesize'] = r
            col_num += 1
        task_list.append(task1)
    print 'task_list num: %d' % (len(task_list))
    
    sql = "select video_hash, create_time, filesize from fs_video_dat" + where_condition           
    print sql
    db.execute(sql)
    
    for row in db.cur.fetchall():
        task1 = {}      
        col_num = 0  
        for r in row:
            if(col_num == 0):
                task1['hash'] = r
            elif(col_num == 1):
                task1['online_time'] = r
            elif(col_num == 2):
                task1['filesize'] = r
            col_num += 1
        task_list.append(task1)
    print 'task_list num: %d' % (len(task_list))
    
    db.close()  
     
    return task_list


def get_tasks_macross_pc(begin_date, end_date):
    task_list = []
    sql = ""
    
    where_condition = ''
    if(len(begin_date) > 0):
        begin_time = '%s-%s-%s 00:00:00' % (begin_date[0:4], begin_date[4:6], begin_date[6:8])
        where_condition += " where fs_task.create_time >= '%s'" % (begin_time)
    if(len(end_date) > 0):
        end_time = '%s-%s-%s 00:00:00' % (end_date[0:4], end_date[4:6], end_date[6:8])
        where_condition += " and fs_task.create_time < '%s'" % (end_time)
    
    db = DB.db.DB_MYSQL()
    db.connect(DB.db.DB_CONFIG.host, DB.db.DB_CONFIG.port, DB.db.DB_CONFIG.user, DB.db.DB_CONFIG.password, DB.db.DB_CONFIG.db)
    
    #where_condition = " and fs_task.task_hash='92A20D164F8D5F18F2433E9CB39703E2A381EDDC'"
    #sql = "select task_hash, create_time from fs_task where state!='dismissed' " + where_condition
    #sql = "select t.task_hash, t.create_time, d.file_size from fs_task t, fs_dat_file d where t.task_hash=d.hashid and t.state!='dismissed' " + where_condition
    sql = "select fs_task.task_hash, fs_task.create_time, fs_dat_file.file_size from fs_task LEFT JOIN fs_dat_file ON fs_task.task_hash=fs_dat_file.hashid" + where_condition              
    print sql
    db.execute(sql)
    
    for row in db.cur.fetchall():
        task1 = {}      
        col_num = 0  
        for r in row:
            if(col_num == 0):
                task1['hash'] = r
            elif(col_num == 1):
                task1['online_time'] = r
            elif(col_num == 2):
                task1['filesize'] = r
            col_num += 1
        task_list.append(task1)
    
    db.close()  
     
    return task_list


def add_tasks_local(platform, task_list):    
    table = '%s_task_temperature' % (platform)
    
    db = DB.db.DB_MYSQL()
    db.connect(DB.db.MS2_DB_CONFIG.host, DB.db.MS2_DB_CONFIG.port, DB.db.MS2_DB_CONFIG.user, DB.db.MS2_DB_CONFIG.password, DB.db.MS2_DB_CONFIG.db)

    sql = 'SELECT count(*) FROM %s' % (table)
    print sql
    db.execute(sql)
    num_1 = 0    
    for row in db.cur.fetchall():        
        for r in row:
            num_1 = r
            break
        break
    
    print 'INSERT INTO %s' % (table)
    for task in task_list:  
        if(task['filesize'] == None):
            task['filesize'] = 0      
        sql = 'INSERT INTO %s(hash, online_time, is_valid, filesize, temperature0, \
        temperature1, temperature2, temperature3, temperature4, temperature5, temperature6, temperature7) \
        VALUES("%s", "%s", 2, %s, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0) \
        ON DUPLICATE KEY UPDATE is_valid=2' % (table, task['hash'], task['online_time'], task['filesize'])              
        print sql
        db.execute(sql)
    
    sql = 'SELECT count(*) FROM %s' % (table)
    print sql
    db.execute(sql)
    num_2 = 0    
    for row in db.cur.fetchall():        
        for r in row:
            num_2 = r
            break
        break
    
    num_insert = num_2 - num_1
    
    sql = 'DELETE FROM %s WHERE is_valid!=2' % (table)
    print sql
    db.execute(sql)
    
    sql = 'SELECT count(*) FROM %s' % (table)
    print sql
    db.execute(sql)
    num_3 = 0    
    for row in db.cur.fetchall():        
        for r in row:
            num_3 = r
            break
        break
    
    num_delete = num_2 - num_3
    
    sql = 'UPDATE %s SET is_valid=1' % (table)
    print sql
    db.execute(sql)
        
    db.close()  
     
    return (num_1, num_insert, 0, num_delete)


def get_tasks_macross(platform, begin_date, end_date):
    task_list = None
    if(platform == 'mobile'):
        task_list = get_tasks_macross_mobile(begin_date, end_date)
    elif(platform == 'pc'):        
        task_list = get_tasks_macross_pc(begin_date, end_date)
        
    return task_list


def task_list_find(task_list, hashid):
    for task in task_list:
        if(task.hash == hashid):
            return task
    return None



def show_task_list(request, platform):  
    output = ''
    hashs = request.REQUEST['hashs']    
    hash_list = hashs.split(',')
    
    #reload(sys)
    #sys.setdefaultencoding('utf8')
    
    db = DB.db.DB_MYSQL()
    #db.connect("192.168.8.101", 3317, "public", "funshion", "macross")
    db.connect(DB.db.DB_CONFIG.host, DB.db.DB_CONFIG.port, DB.db.DB_CONFIG.user, DB.db.DB_CONFIG.password, DB.db.DB_CONFIG.db)
    if(platform == 'mobile'):
        sql = 'select dat_hash, cid, serialid, media_id, dat_name from fs_mobile_dat where dat_hash='
    elif(platform == 'pc'):
        sql = 'select a.hashid, a.dat_id, a.serialid, b.media_id, a.dat_name from fs_dat_file a, fs_media_serials b where a.serialid=b.serialid and a.hashid='    
        
    for hashid in hash_list:
        title = '<h1>hash: %s</h1>' % (hashid)
        output += title          
        sql_where = sql + '"%s"'%(hashid)
        db.execute(sql_where)
        
        task_list = []
        for row in db.cur.fetchall():
            task = {}      
            col_num = 0  
            for r in row:
                if(col_num == 0):
                    task['hash'] = r
                elif(col_num == 1):
                    task['cid'] = r
                elif(col_num == 2):
                    task['serialid'] = r
                elif(col_num == 3):
                    task['media_id'] = r
                elif(col_num == 4):
                    task['dat_name'] = r
                col_num += 1
            task_list.append(task)   
        
        for task in task_list:
            output += '%s,%s,%s,%s,%s\n' % (task['hash'], task['cid'], task['serialid'], task['media_id'], task['dat_name']) 
      
    db.close()  
      
    return HttpResponse(output)


def upload_sub_hits_num(platform, previous_day):
    num_insert2 = 0
    num_update2 = 0
    # check if uploaded
    #     true: sub it,
    #     false: do nothing.
    operation_list = operation.views.get_operation_by_type_name(platform, 'upload_hits_num', previous_day)
    if(len(operation_list) <= 0):
        print 'sub_hits_num %s not uploaded' % (previous_day)
        return (True, num_insert2, num_update2)
        
    upload_file = ""
    if(platform == 'mobile'):
        upload_file = DB.db.HITS_FILE.template_mobile % (previous_day)
    elif(platform == 'pc'):
        upload_file = DB.db.HITS_FILE.template_pc % (previous_day)
    print 'sub_hits_num %s' % (upload_file)
       
    line_num = 0
    try:
        hits_file = open(upload_file, "r")
    except:            
        return (False, num_insert2, num_update2)
        
    hash_list_local = get_tasks_local(platform)  
        
    content = hits_file.readlines()
    for line in content:
        items = line.split(' ')
        if(len(items) >= 2):
            hits_num = items[0].strip()
            hash_id = items[1].strip()
            #print '%s, %s' % (hits_num, hash_id)
            task_list = hash_list_local.filter(hash=hash_id)
            if(len(task_list) > 0):
                #print '%s, %s [update -]' % (hits_num, hash_id)
                hash_local = task_list[0]
                if(hash_local.hot > string.atoi(hits_num)): 
                    hash_local.hot -= string.atoi(hits_num)
                else:
                    hash_local.hot = 0                    
                hash_local.save()
                num_update2 += 1
            else:
                print '%s, %s [insert -]' % (hits_num, hash_id)
                num_insert2 += 1
        line_num += 1
        if(line_num % 100 == 0):
            print 'file=%s, line_num=%d' % (upload_file, line_num)
    hits_file.close()
    print 'sub_hits_num line_num=%d, num_insert2=%d, num_update2=%d' % (line_num, num_insert2, num_update2)        
    return (True, num_insert2, num_update2)
    

def upload_add_hits_num_sql(platform, hits_date):
    num_insert = 0
    num_update = 0
    
    upload_file = ""
    if(platform == 'mobile'):        
        upload_file = DB.db.HITS_FILE.template_mobile % (hits_date)
    elif(platform == 'pc'):
        upload_file = DB.db.HITS_FILE.template_pc % (hits_date)
    print 'add_hits_num %s' % (upload_file)
       
    hits_time = '%s-%s-%s 12:00:00' % (hits_date[0:4], hits_date[4:6], hits_date[6:8])  
    
    try:
        hits_file = open(upload_file, "r")
    except:            
        return (False, num_insert, num_update)
    
    table = '%s_task_hits' % (platform)
    
    db = DB.db.DB_MYSQL()
    db.connect(DB.db.MS2_DB_CONFIG.host, DB.db.MS2_DB_CONFIG.port, DB.db.MS2_DB_CONFIG.user, DB.db.MS2_DB_CONFIG.password, DB.db.MS2_DB_CONFIG.db)
    
    line_num = 0 
    while(True): 
        line = hits_file.readline()
        if(line == ''):
            break           
        items = line.split(' ')
        if(len(items) >= 2):
            hits_num = items[0].strip()
            hash_id = items[1].strip()
            v_hits_num = string.atoi(hits_num)
            #sql = 'INSERT ignore INTO %s(hash, time, hits_num) VALUES("%s", "%s", %d)' % (table, hash_id, hits_time, v_hits_num)  
            sql = 'INSERT INTO %s(hash, time, hits_num) VALUES("%s", "%s", %d) ON DUPLICATE KEY UPDATE hits_num=hits_num+%d' % (table, hash_id, hits_time, v_hits_num, v_hits_num) 
            print sql
            db.execute(sql)
            num_insert += 1
        line_num += 1
        if(line_num % 100 == 0):
            print 'file=%s, line_num=%d' % (upload_file, line_num)
        
    hits_file.close() 
    
    print 'add_hits_num line_num=%d, num_insert=%d, num_update=%d' % (line_num, num_insert, num_update)            
    return (True, num_insert, num_update)

    
def upload_add_hits_num_django(platform, hits_date):
    num_insert = 0
    num_update = 0
    
    upload_file = ""
    if(platform == 'mobile'):        
        upload_file = DB.db.HITS_FILE.template_mobile % (hits_date)
    elif(platform == 'pc'):
        upload_file = DB.db.HITS_FILE.template_pc % (hits_date)
    print 'add_hits_num %s' % (upload_file)
       
    hits_time = '%s-%s-%s 12:00:00' % (hits_date[0:4], hits_date[4:6], hits_date[6:8])  
    
    try:
        hits_file = open(upload_file, "r")
    except:            
        return (False, num_insert, num_update)
    
    # method 1    
    hash_list_local = get_tasks_local(platform)
    
    line_num = 0 
    while(True): 
        line = ''        
        try:      
            line = hits_file.readline()
        except:            
            break 
        if(line == ''):
            break           
        items = line.split(' ')
        if(len(items) >= 2):
            hits_num = items[0].strip()
            hash_id = items[1].strip()            
            #print '%s, %s [insert +]' % (hits_num, hash_id)
            v_hits_num = string.atoi(hits_num)            
            task_hits_insert(platform, hash_id, hits_time, v_hits_num)
            num_insert += 1
        line_num += 1
        if(line_num % 100 == 0):
            print 'file=%s, line_num=%d' % (upload_file, line_num)
        
    hits_file.close() 
    
    print 'add_hits_num line_num=%d, num_insert=%d, num_update=%d' % (line_num, num_insert, num_update)            
    return (True, num_insert, num_update)


def do_calc_temperature_normal_sql(platform, record):
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    print 'begin@ %s' % (begin_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()
    
    str_time = time.strftime("%Y-%m-%d 00:00:00", now_time)   
    
    day_delta = 1
    previous_date = datetime.datetime(string.atoi(str_time[0:4]), string.atoi(str_time[5:7]), string.atoi(str_time[8:10]), 0, 0, 0) - datetime.timedelta(days=day_delta)
    previous_day = '%04d-%02d-%02d 00:00:00' % (previous_date.year, previous_date.month, previous_date.day)
    week_day = previous_date.weekday()    
    previous_week_day = week_day - 1
    if(previous_week_day < 0):
        previous_week_day = 6
    print 'weekday: %d, previous_weekday: %d' % (week_day, previous_week_day)
    
    v_config = config.views.get_config(platform)
    ALPHA = v_config.alpha
    MEAN_HITS_NUM = v_config.mean_hits
    
    table_temperature = '%s_task_temperature' % (platform)
    table_hits = '%s_task_hits' % (platform)
    
    db = DB.db.DB_MYSQL()
    db.connect(DB.db.MS2_DB_CONFIG.host, DB.db.MS2_DB_CONFIG.port, DB.db.MS2_DB_CONFIG.user, DB.db.MS2_DB_CONFIG.password, DB.db.MS2_DB_CONFIG.db)
    
    sql1 = 'SELECT hash, online_time, temperature0 FROM %s' % (table_temperature)
    print sql1
    db.execute(sql1)
    
    num_calc = 0 
    query_set_1 = db.cur.fetchall()
    for row1 in query_set_1:
        task1 = {} 
        r1_index = 0
        for r1 in row1:
            if(r1_index == 0):
                task1['hash'] = r1
            elif(r1_index == 1):
                task1['online_time'] = r1
            elif(r1_index == 2):
                task1['temperature0'] = r1
            r1_index += 1
        print '%s, %s, %e' % (task1['hash'], task1['online_time'], task1['temperature0'])
        
        task_temperature = 0.0
        
        sql2 = 'SELECT hash, time, hits_num FROM %s WHERE hash="%s" and time>="%s"' % (table_hits, task1['hash'], previous_day)
        print sql2
        db.execute(sql2)
        query_set_2 = db.cur.fetchall()
        hits_days_num = 0
        for row2 in query_set_2:
            hits_days_num += 1
            hits = {}            
            r2_index = 0       
            for r2 in row2:
                if(r2_index == 0):
                    hits['hash'] = r2
                elif(r2_index == 1):
                    hits['time'] = r2
                elif(r2_index == 2):
                    hits['hits_num'] = r2
                r2_index += 1
            print '%s, %s, %d' % (hits['hash'], hits['time'], hits['hits_num'])
            diff_days_num = day_diff(previous_day, hits['time'].strftime("%Y-%m-%d %H:%M:%S"))
            if(diff_days_num < 0):
                diff_days_num = 0
            hits_num = hits['hits_num']
            online_days_num = day_diff(task1['online_time'].strftime("%Y-%m-%d %H:%M:%S"), hits['time'].strftime("%Y-%m-%d %H:%M:%S"))
            if(online_days_num == 0):
                hits_num += MEAN_HITS_NUM
            task_temperature = task_temperature + hits_num*(ALPHA**diff_days_num)
            
        if(hits_days_num == 0):            
            diff_days_num = day_diff(previous_day, task1['online_time'].strftime("%Y-%m-%d %H:%M:%S"))
            if(diff_days_num < 0):                
                diff_days_num = 0
            if(diff_days_num == 0):
                task_temperature = task_temperature + MEAN_HITS_NUM*(ALPHA**diff_days_num)
        
        task_temperature = task1['temperature0'] * ALPHA + task_temperature;
        sql3 = 'UPDATE %s SET temperature0=%e, temperature%d=%e WHERE hash="%s"' % (table_temperature, task_temperature, week_day+1, task_temperature, task1['hash'])
        print sql3
        db.execute(sql3)        
        print '%s, %e' % (task1['hash'], task_temperature)        
        num_calc += 1
        
    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    print 'end@ %s' % (end_time)
    output = 'now: %s, ' % (end_time)
    output += 'num_calc: %d, ' % (num_calc)
    print output
    record.end_time = end_time
    record.status = 2                
    record.memo = output
    record.save()
    return True 



def do_calc_temperature_normal_django(platform, record):
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    print 'begin@ %s' % (begin_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()
    
    str_time = time.strftime("%Y-%m-%d 00:00:00", now_time)   
    
    day_delta = 1
    previous_date = datetime.datetime(string.atoi(str_time[0:4]), string.atoi(str_time[5:7]), string.atoi(str_time[8:10]), 0, 0, 0) - datetime.timedelta(days=day_delta)
    previous_day = '%04d-%02d-%02d 00:00:00' % (previous_date.year, previous_date.month, previous_date.day)
    week_day = previous_date.weekday()    
    previous_week_day = week_day - 1
    if(previous_week_day < 0):
        previous_week_day = 6
    print 'weekday: %d, previous_weekday: %d' % (week_day, previous_week_day)
    
    hash_list_local = get_tasks_local(platform)  
    tasks_hits_list = get_tasks_hits(platform)

    v_config = config.views.get_config(platform)
    ALPHA = v_config.alpha
    MEAN_HITS_NUM = v_config.mean_hits
    
    num_calc = 0 
    print 'hash_list_local count %d' % (hash_list_local.count())
    for task in hash_list_local:
        hits_list = tasks_hits_list.filter(hash=task.hash, time__gte=previous_date)
        task_temperature = 0.0
        if(hits_list.count() > 0):
            for hits in hits_list:
                days_num = day_diff(previous_day, str(hits.time))
                if(days_num < 0):
                    days_num = 0
                task_temperature = task_temperature + hits.hits_num*(ALPHA**days_num)
        else:
            online_time = task.online_time.strftime("%Y-%m-%d %H:%M:%S")
            days_num = day_diff(previous_day, online_time)
            if(days_num < 0):
                days_num = 0
            if(days_num == 0):
                task_temperature = MEAN_HITS_NUM
            else:
                task_temperature = 0.0
        
        task.__dict__['temperature%d'%(week_day+1)] = task.__dict__['temperature%d'%(previous_week_day+1)] * ALPHA + task_temperature 
        task.temperature0 = task.__dict__['temperature%d'%(week_day+1)]
        print '%s, %e' % (task.hash, task.temperature0)
        task.save()
        num_calc += 1        
    
    #hash_list_local.update(temperature0=temperature1)
        
    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    print 'end@ %s' % (end_time)
    output = 'now: %s, ' % (end_time)
    output += 'num_calc: %d, ' % (num_calc)
    print output
    record.end_time = end_time
    record.status = 2                
    record.memo = output
    record.save()
    return True 

def do_calc_temperature_renew_sql(platform, record):
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    print 'begin@ %s' % (begin_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()
    
    str_time = time.strftime("%Y-%m-%d 00:00:00", now_time)   
    
    day_delta = 1
    previous_date = datetime.datetime(string.atoi(str_time[0:4]), string.atoi(str_time[5:7]), string.atoi(str_time[8:10]), 0, 0, 0) - datetime.timedelta(days=day_delta)
    previous_day = '%04d-%02d-%02d 00:00:00' % (previous_date.year, previous_date.month, previous_date.day)
    week_day = previous_date.weekday()    
    previous_week_day = week_day - 1
    if(previous_week_day < 0):
        previous_week_day = 6
    print 'weekday: %d, previous_weekday: %d' % (week_day, previous_week_day)
    
    v_config = config.views.get_config(platform)
    ALPHA = v_config.alpha
    MEAN_HITS_NUM = v_config.mean_hits
    
    table_temperature = '%s_task_temperature' % (platform)
    table_hits = '%s_task_hits' % (platform)
    
    db = DB.db.DB_MYSQL()
    db.connect(DB.db.MS2_DB_CONFIG.host, DB.db.MS2_DB_CONFIG.port, DB.db.MS2_DB_CONFIG.user, DB.db.MS2_DB_CONFIG.password, DB.db.MS2_DB_CONFIG.db)
    
    sql1 = 'SELECT hash, online_time FROM %s' % (table_temperature)
    print sql1
    db.execute(sql1)
    
    num_calc = 0 
    query_set_1 = db.cur.fetchall()
    for row1 in query_set_1:
        task1 = {} 
        r1_index = 0
        for r1 in row1:
            if(r1_index == 0):
                task1['hash'] = r1
            elif(r1_index == 1):
                task1['online_time'] = r1
            r1_index += 1
        print '%s, %s' % (task1['hash'], task1['online_time'])
        
        task_temperature = 0.0
        
        sql2 = 'SELECT hash, time, hits_num FROM %s WHERE hash="%s"' % (table_hits, task1['hash'])
        print sql2
        db.execute(sql2)
        query_set_2 = db.cur.fetchall()
        online_day_have_hits = False
        hits_days_num = 0
        for row2 in query_set_2:
            hits_days_num += 1
            hits = {}            
            r2_index = 0       
            for r2 in row2:
                if(r2_index == 0):
                    hits['hash'] = r2
                elif(r2_index == 1):
                    hits['time'] = r2
                elif(r2_index == 2):
                    hits['hits_num'] = r2
                r2_index += 1
            print '%s, %s, %d' % (hits['hash'], hits['time'], hits['hits_num'])
            diff_days_num = day_diff(previous_day, hits['time'].strftime("%Y-%m-%d %H:%M:%S"))
            if(diff_days_num < 0):
                diff_days_num = 0
            online_days_num = day_diff(task1['online_time'].strftime("%Y-%m-%d %H:%M:%S"), hits['time'].strftime("%Y-%m-%d %H:%M:%S"))
            hits_num = hits['hits_num']
            if(online_days_num == 0):
                online_day_have_hits = True
                hits_num += MEAN_HITS_NUM
            task_temperature = task_temperature + hits_num*(ALPHA**diff_days_num)
            
        #if(hits_days_num == 0):  
        if(online_day_have_hits == False):          
            diff_days_num = day_diff(previous_day, task1['online_time'].strftime("%Y-%m-%d %H:%M:%S"))
            if(diff_days_num < 0):
                diff_days_num = 0
            task_temperature = task_temperature + MEAN_HITS_NUM*(ALPHA**diff_days_num)
        
        sql3 = 'UPDATE %s SET temperature0=%e, temperature%d=%e WHERE hash="%s"' % (table_temperature, task_temperature, week_day+1, task_temperature, task1['hash'])
        print sql3
        db.execute(sql3)        
        print '%s, %e' % (task1['hash'], task_temperature)        
        num_calc += 1
        
    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    print 'end@ %s' % (end_time)
    output = 'mode: renew, '
    output += 'now: %s, ' % (end_time)
    output += 'num_calc: %d, ' % (num_calc)
    print output
    record.end_time = end_time
    record.status = 2                
    record.memo = output
    record.save()
    return True 


def do_calc_temperature_renew_django(platform, record):
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    print 'begin@ %s' % (begin_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()
    
    str_time = time.strftime("%Y-%m-%d 00:00:00", now_time)   
    
    day_delta = 1
    previous_date = datetime.datetime(string.atoi(str_time[0:4]), string.atoi(str_time[5:7]), string.atoi(str_time[8:10]), 0, 0, 0) - datetime.timedelta(days=day_delta)
    previous_day = '%04d-%02d-%02d 00:00:00' % (previous_date.year, previous_date.month, previous_date.day)
    week_day = previous_date.weekday()    
    previous_week_day = week_day - 1
    if(previous_week_day < 0):
        previous_week_day = 6
    print 'weekday: %d, previous_weekday: %d' % (week_day, previous_week_day)
    
    hash_list_local = get_tasks_local(platform)  
    tasks_hits_list = get_tasks_hits(platform)

    v_config = config.views.get_config(platform)
    ALPHA = v_config.alpha
    MEAN_HITS_NUM = v_config.mean_hits
    
    num_calc = 0 
    print 'hash_list_local count %d' % (hash_list_local.count())
    for task in hash_list_local:
        hits_list = tasks_hits_list.filter(hash=task.hash)
        task_temperature = 0.0
        if(hits_list.count() > 0):
            for hits in hits_list:
                days_num = day_diff(previous_day, str(hits.time))
                if(days_num < 0):
                    days_num = 0
                task_temperature = task_temperature + hits.hits_num*(ALPHA**days_num)
        else:
            online_time = task.online_time.strftime("%Y-%m-%d %H:%M:%S")
            days_num = day_diff(previous_day, online_time)
            if(days_num < 0):
                days_num = 0
            task_temperature = task_temperature + MEAN_HITS_NUM*(ALPHA**days_num)
            
        task.__dict__['temperature%d'%(week_day+1)] = task_temperature 
        task.temperature0 = task_temperature
        print '%s, %e' % (task.hash, task.temperature0)
        task.save()
        num_calc += 1        
        
    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    print 'end@ %s' % (end_time)
    output = 'now: %s, ' % (end_time)
    output += 'num_calc: %d, ' % (num_calc)
    print output
    record.end_time = end_time
    record.status = 2                
    record.memo = output
    record.save()
    return True 

'''
def do_calc_temperature(platform, record):
    result = False
    memo = record.memo
    if(memo == ''):
        #result = do_calc_temperature_normal_django(platform, record)
        result = do_calc_temperature_normal_sql(platform, record)
    elif(memo == 'renew'):
        result = do_calc_temperature_renew_sql(platform, record)
        #result = do_calc_temperature_renew_django(platform, record)
    else:
        result = False
    return result
'''


def calc_week_temperature(db, table_hits, hash_id, begin_time):
    str_date = begin_time    
    day_delta = 7*8
    week_begin = datetime.datetime(string.atoi(str_date[0:4]), string.atoi(str_date[4:6]), string.atoi(str_date[6:8]), 0, 0, 0) - datetime.timedelta(days=day_delta)
    day_delta = 1
    week_end  = datetime.datetime(string.atoi(str_date[0:4]), string.atoi(str_date[4:6]), string.atoi(str_date[6:8]), 0, 0, 0) - datetime.timedelta(days=day_delta)
    
    DAY_WEEK_BEGIN = '%04d-%02d-%02d' % (week_begin.year, week_begin.month, week_begin.day)
    DAY_WEEK_END   = '%04d-%02d-%02d' % (week_end.year, week_end.month, week_end.day)    
    #print DAY_WEEK_BEGIN
    #print DAY_WEEK_END
    sql2 = 'SELECT hash, time, hits_num FROM %s WHERE hash="%s" and time>="%s 00:00:00" and time<="%s 23:59:59" ' % (table_hits, hash_id, DAY_WEEK_BEGIN, DAY_WEEK_END)
    #print sql2
    db.execute(sql2)
    query_set_2 = db.cur.fetchall()
    
    hits_array = [0]*56 
    for row2 in query_set_2:
        hits = {}            
        r2_index = 0       
        for r2 in row2:
            if(r2_index == 0):
                hits['hash'] = r2
            elif(r2_index == 1):
                hits['time'] = r2
            elif(r2_index == 2):
                hits['hits_num'] = r2
            r2_index += 1
        #print '%s, %s, %d' % (hits['hash'], hits['time'], hits['hits_num'])
        str_date=hits['time'].strftime("%Y-%m-%d %H:%M:%S")
        #print str_date
        day_index = day_diff(str_date, DAY_WEEK_BEGIN)
        hits_array[day_index] = hits['hits_num']        
        
    find_first_not_zero = False
    hash_temperature = 0.0
    for week_index in range(0, 8):
        reverse_week_index = 7 - week_index
        hash_week_hits_num = 0
        week_hits_day_num = 7
        for day_index in range(0, 7):
            if(find_first_not_zero == False):
                if(hits_array[week_index*7+day_index] != 0):
                    find_first_not_zero = True
                    week_hits_day_num = 7 - day_index
            hash_week_hits_num += hits_array[week_index*7+day_index]
        hash_week_mean_hits_num = float(hash_week_hits_num) / week_hits_day_num
        #print '%d / %d = %f' % (hash_week_hits_num, week_hits_day_num, hash_week_mean_hits_num)
        hash_temperature +=   hash_week_mean_hits_num/(100000000**reverse_week_index)
    
    return hash_temperature


#def do_calc_temperature_week(platform, record):
def do_calc_temperature(platform, record):
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    print 'begin@ %s' % (begin_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()
    
    str_date = record.name    
    the_date = datetime.datetime(string.atoi(str_date[0:4]), string.atoi(str_date[4:6]), string.atoi(str_date[6:8]), 0, 0, 0)    
    week_day = the_date.weekday()
    print 'week_day: %d' % (week_day)
    
    table_temperature = '%s_task_temperature' % (platform)
    table_hits = '%s_task_hits' % (platform)
    
    db = DB.db.DB_MYSQL()
    db.connect(DB.db.MS2_DB_CONFIG.host, DB.db.MS2_DB_CONFIG.port, DB.db.MS2_DB_CONFIG.user, DB.db.MS2_DB_CONFIG.password, DB.db.MS2_DB_CONFIG.db)
    
    sql1 = 'SELECT hash, online_time FROM %s' % (table_temperature)
    print sql1
    db.execute(sql1)
 
    tasks_num = 0    
    query_set_1 = db.cur.fetchall()
    for row1 in query_set_1:
        task1 = {} 
        r1_index = 0
        for r1 in row1:
            if(r1_index == 0):
                task1['hash'] = r1
            elif(r1_index == 1):
                task1['online_time'] = r1
            r1_index += 1
        #print '%s, %s' % (task1['hash'], task1['online_time'])
                
        tasks_num = tasks_num + 1
                
        total_temperature = calc_week_temperature(db, table_hits, task1['hash'], str_date)
          
        sql3 = 'UPDATE %s SET temperature0=%e, temperature%d=%e WHERE hash="%s"' % (table_temperature, total_temperature, week_day+1, total_temperature, task1['hash'])
        #print sql3
        db.execute(sql3)        
        print '%d, %s, %e' % (tasks_num, task1['hash'], total_temperature)
    
    db.close()
    
    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    print 'end@ %s' % (end_time)
    output = 'now: %s, ' % (end_time)    
    output += 'tasks_num: %d' % (tasks_num)
    print output
    record.end_time = end_time
    record.status = 2                
    record.memo = output
    record.save()
    return True


def do_calc_hot_mean_hits_num(platform, record):
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    print 'begin@ %s' % (begin_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()
    
    str_date = record.name   
    str_day_begin = '%s-%s-%s 00:00:00' % (str_date[0:4], str_date[4:6], str_date[6:8]) 
    str_day_end   = '%s-%s-%s 23:59:59' % (str_date[0:4], str_date[4:6], str_date[6:8]) 
    print str_day_begin
    print str_day_end        
    
    tasks_hits_list = get_tasks_hits(platform)
    hot_list = tasks_hits_list.filter(time__gte=str_day_begin, time__lte=str_day_end).order_by('-hits_num')
    total_list_num = hot_list.count()
    hot_list_num = total_list_num/5
    
    total_hits_num = 0
    hot_list_index = 0
    for hot_task in hot_list:
        print 'hot_list_index: %d, hits_num:%d, hash: %s' % (hot_list_index, hot_task.hits_num, hot_task.hash)
        total_hits_num = total_hits_num + hot_task.hits_num
        hot_list_index = hot_list_index + 1
        if(hot_list_index>=hot_list_num):
            break
    
    mean_hits_num = 0
    if(hot_list_num > 0):
        mean_hits_num = total_hits_num/hot_list_num
    
    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    print 'end@ %s' % (end_time)
    output = 'now: %s, ' % (end_time)
    output += 'hot_list_num: %d[%d], ' % (hot_list_num, total_list_num)
    output += 'total_hits_num: %d, mean_hits_num: %d' % (total_hits_num, mean_hits_num)
    print output
    record.end_time = end_time
    record.status = 2                
    record.memo = output
    record.save()
    return True 


def do_evaluate_temperature_day(platform, record):
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    print 'begin@ %s' % (begin_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()
    
    str_date = record.memo    
    day_delta = 1
    previous_date = datetime.datetime(string.atoi(str_date[0:4]), string.atoi(str_date[4:6]), string.atoi(str_date[6:8]), 0, 0, 0) - datetime.timedelta(days=day_delta)
    
    DAY_1 = '%04d-%02d-%02d' % (previous_date.year, previous_date.month, previous_date.day)
    DAY_2 = '%s-%s-%s' % (str_date[0:4], str_date[4:6], str_date[6:8])
    print DAY_1
    print DAY_2
    
    total_hits_num1 = 0.0
    total_hits_num2 = 0.0
    total_hits_diff_square = 0.0
    
    table_temperature = '%s_task_temperature' % (platform)
    table_hits = '%s_task_hits' % (platform)
    
    db = DB.db.DB_MYSQL()
    db.connect(DB.db.MS2_DB_CONFIG.host, DB.db.MS2_DB_CONFIG.port, DB.db.MS2_DB_CONFIG.user, DB.db.MS2_DB_CONFIG.password, DB.db.MS2_DB_CONFIG.db)
    
    sql1 = 'SELECT hash, online_time FROM %s' % (table_temperature)
    print sql1
    db.execute(sql1)
 
    tasks_num = 0
    evaluate_num = 0
    query_set_1 = db.cur.fetchall()
    for row1 in query_set_1:
        task1 = {} 
        r1_index = 0
        for r1 in row1:
            if(r1_index == 0):
                task1['hash'] = r1
            elif(r1_index == 1):
                task1['online_time'] = r1
            r1_index += 1
        #print '%s, %s' % (task1['hash'], task1['online_time'])
                
        tasks_num = tasks_num + 1
        sql2 = 'SELECT hash, time, hits_num FROM %s WHERE hash="%s" and time>="%s 00:00:00" and time<="%s 23:59:59" ' % (table_hits, task1['hash'], DAY_1, DAY_1)
        #print sql2
        db.execute(sql2)
        query_set_2 = db.cur.fetchall()
        hash_total_hits_num1 = 0        
        hash_hits_days_num1 = 0
        for row2 in query_set_2:
            hash_hits_days_num1 += 1
            hits = {}            
            r2_index = 0       
            for r2 in row2:
                if(r2_index == 0):
                    hits['hash'] = r2
                elif(r2_index == 1):
                    hits['time'] = r2
                elif(r2_index == 2):
                    hits['hits_num'] = r2
                r2_index += 1
            #print '%s, %s, %d' % (hits['hash'], hits['time'], hits['hits_num'])
            hash_total_hits_num1 = hash_total_hits_num1 + hits['hits_num']
        
        mean_hits_num1 = 0
        if(hash_hits_days_num1>0):
            mean_hits_num1 = hash_total_hits_num1/hash_hits_days_num1
        else:
            continue
        evaluate_num = evaluate_num + 1
        
        sql2 = 'SELECT hash, time, hits_num FROM %s WHERE hash="%s" and time>="%s 00:00:00" and time<="%s 23:59:59" ' % (table_hits, task1['hash'], DAY_2, DAY_2)
        #print sql2
        db.execute(sql2)
        query_set_2 = db.cur.fetchall()
        hash_total_hits_num2 = 0        
        hash_hits_days_num2 = 0
        for row2 in query_set_2:
            hash_hits_days_num2 += 1
            hits = {}            
            r2_index = 0       
            for r2 in row2:
                if(r2_index == 0):
                    hits['hash'] = r2
                elif(r2_index == 1):
                    hits['time'] = r2
                elif(r2_index == 2):
                    hits['hits_num'] = r2
                r2_index += 1
            #print '%s, %s, %d' % (hits['hash'], hits['time'], hits['hits_num'])
            hash_total_hits_num2 = hash_total_hits_num2 + hits['hits_num']
        
        mean_hits_num2 = 0
        if(hash_hits_days_num2>0):
            mean_hits_num2 = hash_total_hits_num2/hash_hits_days_num2
        
        total_hits_num1 = total_hits_num1 + mean_hits_num1
        total_hits_num2 = total_hits_num2 + mean_hits_num2
        hits_num_diff = mean_hits_num2 - mean_hits_num1
        hits_num_square = hits_num_diff * hits_num_diff
        total_hits_diff_square = total_hits_diff_square + hits_num_square        
        print '%d: %s, %s, %d-%d=%d, square=%d, total_square=%f, total_hits_num1=%f, total_hits_num1=%f' \
        % (evaluate_num, task1['hash'], task1['online_time'], mean_hits_num2, mean_hits_num1, hits_num_diff, hits_num_square, total_hits_diff_square, total_hits_num1, total_hits_num2)
        
    MSE = math.sqrt(total_hits_diff_square / evaluate_num);
    mean_hits1 = total_hits_num1/evaluate_num
    mean_hits2 = total_hits_num2/evaluate_num
    
    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    print 'end@ %s' % (end_time)
    output = 'now: %s, ' % (end_time)
    output += 'DAY_1: %s, DAY_2: %s, ' % (DAY_1, DAY_2)
    output += 'tasks_num: %d, evaluate_num: %d, ' % (tasks_num, evaluate_num)
    output += 'total_hits1: %f, mean_hits1: %f, ' % (total_hits_num1, mean_hits1)
    output += 'total_hits2: %f, mean_hits2: %f, ' % (total_hits_num2, mean_hits2)
    output += 'total_square: %f, MSE(mean square error): %f' % (total_hits_diff_square, MSE)
    print output
    record.end_time = end_time
    record.status = 2                
    record.memo = output
    record.save()
    return True

# evaluate temperature by week
def do_evaluate_temperature(platform, record):
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    print 'begin@ %s' % (begin_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()
    
    str_date = record.memo    
    day_delta = 7
    week_begin = datetime.datetime(string.atoi(str_date[0:4]), string.atoi(str_date[4:6]), string.atoi(str_date[6:8]), 0, 0, 0) - datetime.timedelta(days=day_delta)
    day_delta = 1
    week_end  = datetime.datetime(string.atoi(str_date[0:4]), string.atoi(str_date[4:6]), string.atoi(str_date[6:8]), 0, 0, 0) - datetime.timedelta(days=day_delta)
    
    DAY_WEEK_BEGIN = '%04d-%02d-%02d' % (week_begin.year, week_begin.month, week_begin.day)
    DAY_WEEK_END   = '%04d-%02d-%02d' % (week_end.year, week_end.month, week_end.day)
    DAY_PREDICT = '%s-%s-%s' % (str_date[0:4], str_date[4:6], str_date[6:8])
    print DAY_WEEK_BEGIN
    print DAY_WEEK_END
    print DAY_PREDICT
    
    total_hits_num1 = 0.0
    total_hits_num2 = 0.0
    total_hits_diff_square = 0.0
    
    table_temperature = '%s_task_temperature' % (platform)
    table_hits = '%s_task_hits' % (platform)
    
    db = DB.db.DB_MYSQL()
    db.connect(DB.db.MS2_DB_CONFIG.host, DB.db.MS2_DB_CONFIG.port, DB.db.MS2_DB_CONFIG.user, DB.db.MS2_DB_CONFIG.password, DB.db.MS2_DB_CONFIG.db)
    
    sql1 = 'SELECT hash, online_time FROM %s' % (table_temperature)
    print sql1
    db.execute(sql1)
 
    tasks_num = 0
    evaluate_num = 0
    query_set_1 = db.cur.fetchall()
    for row1 in query_set_1:
        task1 = {} 
        r1_index = 0
        for r1 in row1:
            if(r1_index == 0):
                task1['hash'] = r1
            elif(r1_index == 1):
                task1['online_time'] = r1
            r1_index += 1
        #print '%s, %s' % (task1['hash'], task1['online_time'])
                
        tasks_num = tasks_num + 1
        sql2 = 'SELECT hash, time, hits_num FROM %s WHERE hash="%s" and time>="%s 00:00:00" and time<="%s 23:59:59" ' % (table_hits, task1['hash'], DAY_WEEK_BEGIN, DAY_WEEK_END)
        #print sql2
        db.execute(sql2)
        query_set_2 = db.cur.fetchall()
        hash_total_hits_num1 = 0        
        hash_hits_days_num1 = 0
        
        hits_array = [0]*7 
        for row2 in query_set_2:
            hash_hits_days_num1 += 1
            hits = {}            
            r2_index = 0       
            for r2 in row2:
                if(r2_index == 0):
                    hits['hash'] = r2
                elif(r2_index == 1):
                    hits['time'] = r2
                elif(r2_index == 2):
                    hits['hits_num'] = r2
                r2_index += 1
            #print '%s, %s, %d' % (hits['hash'], hits['time'], hits['hits_num'])
            str_date=hits['time'].strftime("%Y-%m-%d %H:%M:%S")
            #print str_date
            day_index = day_diff(str_date, DAY_WEEK_BEGIN)
            hits_array[day_index] = hits['hits_num']
            hash_total_hits_num1 = hash_total_hits_num1 + hits['hits_num']
        
        hash_hits_days_num1 = 0
        for index in range(0, 7):
            if(hits_array[index] != 0):
                hash_hits_days_num1 = 7 - index
                break    
        
        mean_hits_num1 = 0
        if(hash_hits_days_num1>0):
            mean_hits_num1 = hash_total_hits_num1/hash_hits_days_num1
        else:
            continue
        evaluate_num = evaluate_num + 1
        
        sql2 = 'SELECT hash, time, hits_num FROM %s WHERE hash="%s" and time>="%s 00:00:00" and time<="%s 23:59:59" ' % (table_hits, task1['hash'], DAY_PREDICT, DAY_PREDICT)
        #print sql2
        db.execute(sql2)
        query_set_2 = db.cur.fetchall()
        hash_total_hits_num2 = 0        
        hash_hits_days_num2 = 0
        for row2 in query_set_2:
            hash_hits_days_num2 += 1
            hits = {}            
            r2_index = 0       
            for r2 in row2:
                if(r2_index == 0):
                    hits['hash'] = r2
                elif(r2_index == 1):
                    hits['time'] = r2
                elif(r2_index == 2):
                    hits['hits_num'] = r2
                r2_index += 1
            #print '%s, %s, %d' % (hits['hash'], hits['time'], hits['hits_num'])
            hash_total_hits_num2 = hash_total_hits_num2 + hits['hits_num']
        
        mean_hits_num2 = 0
        if(hash_hits_days_num2>0):
            mean_hits_num2 = hash_total_hits_num2/hash_hits_days_num2
        
        total_hits_num1 = total_hits_num1 + mean_hits_num1
        total_hits_num2 = total_hits_num2 + mean_hits_num2
        hits_num_diff = mean_hits_num2 - mean_hits_num1
        hits_num_square = hits_num_diff * hits_num_diff
        total_hits_diff_square = total_hits_diff_square + hits_num_square        
        print '%d: %s, %s, %d-%d=%d, square=%d, total_square=%f, total_hits_num1=%f, total_hits_num1=%f' \
        % (evaluate_num, task1['hash'], task1['online_time'], mean_hits_num2, mean_hits_num1, hits_num_diff, hits_num_square, total_hits_diff_square, total_hits_num1, total_hits_num2)
        
    MSE = math.sqrt(total_hits_diff_square / evaluate_num);
    mean_hits1 = total_hits_num1/evaluate_num
    mean_hits2 = total_hits_num2/evaluate_num
    
    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    print 'end@ %s' % (end_time)
    output = 'now: %s, ' % (end_time)
    output += 'DAY_WEEK_BEGIN: %s, DAY_WEEK_END: %s, DAY_PREDICT: %s, ' % (DAY_WEEK_BEGIN, DAY_WEEK_END, DAY_PREDICT)
    output += 'tasks_num: %d, evaluate_num: %d, ' % (tasks_num, evaluate_num)
    output += 'total_hits1: %f, mean_hits1: %f, ' % (total_hits_num1, mean_hits1)
    output += 'total_hits2: %f, mean_hits2: %f, ' % (total_hits_num2, mean_hits2)
    output += 'total_square: %f, MSE(mean square error): %f' % (total_hits_diff_square, MSE)
    print output
    record.end_time = end_time
    record.status = 2                
    record.memo = output
    record.save()
    return True


def do_evaluate_temperature_django(platform, record):
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    print 'begin@ %s' % (begin_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()
    
    str_date = '20140211'   
    str_day_begin = '%s-%s-%s 00:00:00' % (str_date[0:4], str_date[4:6], str_date[6:8]) 
    str_day_end   = '%s-%s-%s 23:59:59' % (str_date[0:4], str_date[4:6], str_date[6:8]) 
    print str_day_begin
    print str_day_end        
    
    tasks_hits_list = get_tasks_hits(platform)
    hot_list = tasks_hits_list.filter(time__gte=str_day_begin, time__lte=str_day_end).order_by('-hits_num')
    total_list_num = hot_list.count()
    print 'total_list_num: %d' % (total_list_num)
    
    str_date2 = '20140212'   
    str_day_begin2 = '%s-%s-%s 00:00:00' % (str_date2[0:4], str_date2[4:6], str_date2[6:8]) 
    str_day_end2   = '%s-%s-%s 23:59:59' % (str_date2[0:4], str_date2[4:6], str_date2[6:8]) 
    print str_day_begin2
    print str_day_end2
        
    hot_list2 = tasks_hits_list.filter(time__gte=str_day_begin2, time__lte=str_day_end2).order_by('-hits_num')
    total_list_num2 = hot_list2.count()
    print 'total_list_num2: %d' % (total_list_num2)
        
    hot_list_index = 0
    total_evaluate_num = 0
    total_evaluate_value = 0.0
    for hot_task in hot_list:
        print 'hot_list_index: %d, hits_num:%d, hash: %s' % (hot_list_index, hot_task.hits_num, hot_task.hash)
        hot_list_index = hot_list_index + 1
        hot_task2 = hot_list2.filter(hash=hot_task.hash)
        hits_num2 = 0
        hot_task2_count = hot_task2.count() 
        if(hot_task2_count <= 0):
            hits_num2 = 0
        elif(hot_task2_count >= 2):
            print 'hash: %s, count()=%d ?' % (hot_task.hash, hot_task2_count)
            hits_num2 = hot_task2[0].hits_num
        else:
            hits_num2 = hot_task2[0].hits_num         
        hits_diff = hits_num2 - hot_task.hits_num
        total_evaluate_num = total_evaluate_num + 1
        total_evaluate_value = total_evaluate_value + hits_diff * hits_diff
    
    MSE = 0.0
    if(total_evaluate_num > 0):
        MSE = math.sqrt(total_evaluate_value/total_evaluate_num)
    
    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    print 'end@ %s' % (end_time)
    output = 'now: %s, ' % (end_time)
    output += 'total_list_num: %d, total_evaluate_num: %d, MSE(mean square error): %f' % (total_list_num, total_evaluate_num, MSE)
    print output
    record.end_time = end_time
    record.status = 2                
    record.memo = output
    record.save()
    return True

            
def do_upload(platform, record):
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    print 'begin@ %s' % (begin_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()
    
    hits_date = record.name
    (result, num_insert, num_update) = upload_add_hits_num_sql(platform, hits_date)
    if(result == False):
        now_time = time.localtime(time.time())        
        end_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
        output = 'now: %s, ' % (end_time)
        output += 'error@add_hits_num %s' % (hits_date)            
        print output            
        record.end_time = end_time
        record.status = 2
        record.memo = output
        record.save()
        return False
    
    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    print 'end@ %s' % (end_time)
    output = 'now: %s, ' % (end_time)
    output += 'num_insert: %d, ' % (num_insert)
    output += 'num_update: %d, ' % (num_update)
    print output
    record.end_time = end_time
    record.status = 2 
    record.memo = output
    record.save()
    return True
        

def get_pay_media_list():
    #http://nami.funshion.com/nami/service/paid-media-list                
    url = 'http://nami.funshion.com/nami/service/paid-media-list'    
    #data = urllib.urlencode(values)
    #print data
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    the_page = response.read()
    #print the_page
    
    medias = json.loads(the_page)
    return medias


def get_hash_list_by_medias(media_list):
    task_list = []
    
    db = DB.db.DB_MYSQL()    
    db.connect(DB.db.DB_CONFIG.host, DB.db.DB_CONFIG.port, DB.db.DB_CONFIG.user, DB.db.DB_CONFIG.password, DB.db.DB_CONFIG.db)
    
    for media in media_list:
        sql = 'select s.media_id, s.serialid, d.hashid from fs_media_serials as s, fs_dat_file as d where s.media_id=%d and s.serialid=d.serialid' % (media['mediaId'])
        print sql
        db.execute(sql)    
        for row in db.cur.fetchall():
            task = {}    
            task['mediaId']     = media['mediaId']  
            task['mediaName']   = media['mediaName'] 
            task['payStartTime']= media['payStartTime'] 
            task['payEndTime']  = media['payEndTime'] 
            task['inDB']        = False
            col_num = 0  
            for r in row:
                if(col_num == 0):
                    task['media_id'] = r
                elif(col_num == 1):
                    task['serialid'] = r
                elif(col_num == 2):
                    task['hashid'] = r
                col_num += 1
            task_list.append(task) 
            
    db.close()
    return task_list
        
            
def do_sync_pay_medias(platform, record):    
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    print 'begin@%s' % (begin_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()
    
    media_list  = get_pay_media_list()
    task_list   = get_hash_list_by_medias(media_list)
 
    db = DB.db.DB_MYSQL()    
    db.connect(DB.db.MS2_DB_CONFIG.host, DB.db.MS2_DB_CONFIG.port, DB.db.MS2_DB_CONFIG.user, DB.db.MS2_DB_CONFIG.password, DB.db.MS2_DB_CONFIG.db)
    
    #sql = 'update %s_task_temperature set PayOrFree=0 where PayOrFree=1' % (platform)
    #print sql
    #db.execute(sql)
    
    for task in task_list:
        sql = 'update %s_task_temperature set PayOrFree=1, mediaId=%d, mediaName="%s", payStartTime="%s", payEndTime="%s" where hash="%s"' % \
            (platform, task['mediaId'], task['mediaName'], task['payStartTime'], task['payEndTime'], task['hashid'])
        print sql
        db.execute(sql)
    db.close()   
    
    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    output = 'now: %s, ' % (end_time)
    output += 'media_list: %d, ' % (len(media_list))
    output += 'task_list: %d' % (len(task_list))
    print output
    record.end_time = end_time
    record.status = 2
    record.memo = output
    record.save()
    
    return True
    
    
    
def do_sync_all_sql(platform, record):    
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    print 'begin@%s' % (begin_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()
    
    begin_date = ''
    end_date = ''
        
    hash_list_macross = get_tasks_macross(platform, begin_date, end_date)
    num_macross = hash_list_macross.__len__()
    print 'num_macross=%d' % (num_macross)
    
    (num_local, num_insert, num_update, num_delete) = add_tasks_local(platform, hash_list_macross)    
    
    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    output = 'now: %s, ' % (end_time)
    output += 'num_macross: %d, ' % (num_macross)
    output += 'num_local: %d, ' % (num_local)
    output += 'num_insert: %d, ' % (num_insert)
    output += 'num_update: %d, ' % (num_update)
    output += 'num_delete: %d' % (num_delete)
    print output
    record.end_time = end_time
    record.status = 2
    record.memo = output
    record.save()
    return True

        
def do_sync_all_django(platform, record):    
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    print 'begin@%s' % (begin_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()
    
    begin_date = ''
    end_date = ''
        
    hash_list_macross = get_tasks_macross(platform, begin_date, end_date)
    num_macross = hash_list_macross.__len__()
    print 'num_macross=%d' % (num_macross)
    
    hash_list_local = get_tasks_local(platform)
    num_local = hash_list_local.count()
    print 'num_local=%d' % (num_local)
    
    num_insert = 0
    num_update = 0
    num_delete = 0
    
    #if(len(date_range) <= 0):
    #    for hash_local in hash_list_local:
    #        hash_local.is_valid = 0
    
    for hash_macross in hash_list_macross:   
        hash_id = hash_macross['hash']     
        online_time = hash_macross['online_time']        
        filesize = hash_macross['filesize']
        print '%s, %s' % (hash_macross['hash'], online_time)
        hash_list = hash_list_local.filter(hash=hash_id)
        if(len(hash_list) <= 0):
            print 'insert'
            is_valid = 2
            task_temperature_insert(platform, hash_id, online_time, is_valid, filesize, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)  
            num_insert += 1    
        else:      
            print 'update' 
            hash_list[0].online_time = online_time
            hash_list[0].is_valid = 2
            hash_list[0].filesize = filesize            
            hash_list[0].save()       
            num_update += 1
    
    hash_list_delete = hash_list_local.filter(is_valid=1)
    num_delete = hash_list_delete.count()
    hash_list_delete.delete()  
    
    get_tasks_local(platform).update(is_valid=1)
    
    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    output = 'now: %s, ' % (end_time)
    output += 'num_macross: %d, ' % (num_macross)
    output += 'num_local: %d, ' % (num_local)
    output += 'num_insert: %d, ' % (num_insert)
    output += 'num_update: %d, ' % (num_update)
    output += 'num_delete: %d' % (num_delete)
    print output
    record.end_time = end_time
    record.status = 2
    record.memo = output
    record.save()
    return True
    
            
def do_sync_partial(platform, record):    
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    print 'begin@%s' % (begin_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()
    
    begin_date = ''
    end_date = ''
    
    date_range = record.memo
    if(len(date_range) > 0):
        parts = date_range.split('~')
        begin_date = parts[0] 
        end_date = parts[1]
    
    hash_list_macross = get_tasks_macross(platform, begin_date, end_date)
    num_macross = hash_list_macross.__len__()
    print 'num_macross=%d' % (num_macross)
    
    hash_list_local = get_tasks_local(platform)
    num_local = hash_list_local.count()
    print 'num_local=%d' % (num_local)
    
    num_insert = 0
    num_update = 0
    num_delete = 0
    
    for hash_macross in hash_list_macross:   
        hash_id = hash_macross['hash']
        online_time = hash_macross['online_time']
        filesize = hash_macross['filesize']
        print '%s, %s' % (hash_id, online_time)
        hash_list = hash_list_local.filter(hash=hash_id)
        if(len(hash_list) <= 0):
            print 'insert'
            is_valid = 1
            task_temperature_insert(platform, hash_id, online_time, is_valid, filesize, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)  
            num_insert += 1 
        else:      
            print 'update'
            hash_list[0].online_time = online_time
            hash_list[0].is_valid = 1
            hash_list[0].filesize = filesize            
            hash_list[0].save()       
            num_update += 1
    
    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    output = 'now: %s, ' % (end_time)
    output += 'num_macross: %d, ' % (num_macross)
    output += 'num_local: %d, ' % (num_local)
    output += 'num_insert: %d, ' % (num_insert)
    output += 'num_update: %d, ' % (num_update)
    output += 'num_delete: %d' % (num_delete)
    print output
    record.end_time = end_time
    record.status = 2
    record.memo = output
    record.save()
    return True    

            
def do_uploads(platform, record_list):
    for record in record_list:            
        do_upload(platform, record)
           

    
def do_sync(platform, record): 
    result = False       
    if(record.memo == '~'):
        result = do_sync_all_sql(platform, record)
    else:
        result = do_sync_partial(platform, record)
    return result
        

def add_record_sync_pay_medias(platform, record_list, operation1):
    records = operation.views.get_operation_undone_by_type(platform, operation1['type'])
    if(len(records) == 0):
        record = operation.views.create_operation_record_by_dict(platform, operation1)
        if(record != None):
            record_list.append(record)
        else:
            return False
    else:
        return False
    
    
def add_record_sync_hash_db(platform, record_list, operation1):
    records = operation.views.get_operation_undone_by_type(platform, operation1['type'])
    if(len(records) == 0):
        record = operation.views.create_operation_record_by_dict(platform, operation1)
        if(record != None):
            record_list.append(record)
        else:
            return False
    else:
        return False
       

def sync_pay_medias(request, platform):    
    print 'sync_pay_medias'  
    print request.REQUEST  
    
    start_now = False
    if 'start_now' in request.REQUEST:
        if(request.REQUEST['start_now'] == 'on'):
            start_now = True
    
    now_time = time.localtime(time.time())
    today = time.strftime("%Y-%m-%d", now_time)
    dispatch_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    
    operation = {}
    operation['type'] = 'sync_pay_medias'
    operation['name'] = today
    operation['user'] = request.user.username
    operation['dispatch_time'] = dispatch_time
    operation['memo'] = ''
    
    return_datas = {}
    
    record_list = []
    result = add_record_sync_hash_db(platform, record_list, operation)
    if(result == False):
        return_datas['success'] = False
        return_datas['data'] = 'sync_pay_medias operation add error, maybe exist.'
        return HttpResponse(json.dumps(return_datas))
    
    if(start_now == True):
        # start process
        p = Process(target=do_sync_pay_medias, args=(platform, record_list[0]))
        p.start()
        
    return_datas['success'] = True
    return_datas['data'] = 'sync_pay_medias operation add success'
    
    str_datas = json.dumps(return_datas)
    response = HttpResponse(str_datas, mimetype='application/json;charset=UTF-8')
    response['Content-Length'] = len(str_datas)
    return response

            
def sync_hash_db(request, platform):    
    print 'sync_hash_db'  
    print request.REQUEST    
    #{u'start_now': u'on', u'begin_date': u'20130922', u'end_date': u'20130923'}
    #{u'begin_date': u'', u'end_date': u''}
    
    start_now = False
    if 'start_now' in request.REQUEST:
        if(request.REQUEST['start_now'] == 'on'):
            start_now = True
    
    now_time = time.localtime(time.time())
    today = time.strftime("%Y-%m-%d", now_time)
    dispatch_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
       
    begin_date = ''
    end_date = ''
    if 'begin_date' in request.REQUEST:
        begin_date = request.REQUEST['begin_date']
    if 'end_date' in request.REQUEST:
        end_date = request.REQUEST['end_date']
    
    operation = {}
    operation['type'] = 'sync_hash_db'
    operation['name'] = today
    operation['user'] = request.user.username
    operation['dispatch_time'] = dispatch_time
    operation['memo'] = '%s~%s' % (begin_date, end_date)
    
    return_datas = {}
    
    record_list = []
    result = add_record_sync_hash_db(platform, record_list, operation)
    if(result == False):
        return_datas['success'] = False
        return_datas['data'] = 'sync_hash_db operation add error, maybe exist.'
        return HttpResponse(json.dumps(return_datas))
    
    if(start_now == True):
        # start process
        p = Process(target=do_sync, args=(platform, record_list[0]))
        p.start()
        
    return_datas['success'] = True
    return_datas['data'] = 'sync_hash_db operation add success'
    
    str_datas = json.dumps(return_datas)
    response = HttpResponse(str_datas, mimetype='application/json;charset=UTF-8')
    response['Content-Length'] = len(str_datas)
    return response


def operations_add_record_by_name(platform, record_list, operation1):
    records = operation.views.get_operation_by_type_name(platform, operation1['type'], operation1['name'])
    if(len(records) == 0):
        record = operation.views.create_operation_record_by_dict(platform, operation1)
        if(record != None):
            record_list.append(record)
        else:
            return False
    else:
        return False
    
    

def add_record_upload_hits_num(platform, record_list, operation1):
    records = operation.views.get_operation_by_type_name(platform, operation1['type'], operation1['name'])
    if(len(records) == 0):
        record = operation.views.create_operation_record_by_dict(platform, operation1)
        if(record != None):
            record_list.append(record)
        else:
            return False
    else:
        return False    
    
    

def upload_hits_num(request, platform):
    print 'upload_hits_num'  
    print request.REQUEST
    #{u'start_now': u'on', u'begin_date': u'20130922', u'end_date': u'20130923'}
    #{u'begin_date': u'', u'end_date': u''}
    start_now = False
    if 'start_now' in request.REQUEST:
        if(request.REQUEST['start_now'] == 'on'):
            start_now = True
    
    begin_date = request.REQUEST['begin_date']
    print begin_date    
    
    end_date = request.REQUEST['end_date']
    print end_date
        
    now_time = time.localtime(time.time())
    #today = time.strftime("%Y-%m-%d", now_time)
    dispatch_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    
    begin_day = None
    return_datas = {}
    if(len(begin_date) >= 8):
        begin_day = datetime.date(string.atoi(begin_date[0:4]), string.atoi(begin_date[4:6]), string.atoi(begin_date[6:8])) 
    else:
        return_datas['success'] = False
        return_datas['data'] = 'begin_date %s error' % (begin_date)  
        return HttpResponse(json.dumps(return_datas))
    
    end_day = begin_day      
    if(len(end_date) >= 8):
        end_day = datetime.date(string.atoi(end_date[0:4]), string.atoi(end_date[4:6]), string.atoi(end_date[6:8])) 
       
    record_list = []
    
    operation = {}
    operation['type'] = 'upload_hits_num'
    operation['name'] = ''
    operation['user'] = request.user.username
    operation['dispatch_time'] = dispatch_time
    operation['memo'] = ''
    
    day_num = 0
    operation['name'] = '%04d%02d%02d' % (begin_day.year, begin_day.month, begin_day.day)
    result = add_record_upload_hits_num(platform, record_list, operation)
    if(result == False):
        return_datas['success'] = False
        return_datas['data'] = 'date %s error' % (operation['name'])  
        return HttpResponse(json.dumps(return_datas))
    day_num += 1    
    while(True):
        d1 = begin_day
        delta = datetime.timedelta(days=day_num)
        d2 = d1 + delta
        if(d2 >= end_day):
            break
        else:
            operation['name'] = '%04d%02d%02d' % (d2.year, d2.month, d2.day)
            result = add_record_upload_hits_num(platform, record_list, operation)
            if(result == False):
                return_datas['success'] = False
                return_datas['data'] = 'date %s error' % (operation['name'])  
                return HttpResponse(json.dumps(return_datas))
        day_num += 1 
            
    if(start_now == True):
        # start thread.
        #t = Thread_UPLOAD(platform, record_list)            
        #t.start()
        # start process
        p = Process(target=do_uploads, args=(platform, record_list))
        p.start()
        
    return_datas['success'] = True
    return_datas['data'] = 'day_num %d' % (day_num)  
    
    str_datas = json.dumps(return_datas)
    response = HttpResponse(str_datas, mimetype='application/json;charset=UTF-8')
    response['Content-Length'] = len(str_datas)
    return response
        
        
def add_record_one_operation(platform, record_list, operation1):
    records = operation.views.get_operation_undone_by_type(platform, operation1['type'])
    if(len(records) == 0):
        record = operation.views.create_operation_record_by_dict(platform, operation1)
        if(record != None):
            record_list.append(record)
        else:
            return False
    else:
        return False
    
    
def add_record_calc_hot_mean_hits_num(platform, record_list, operation1):
    records = operation.views.get_operation_undone_by_type(platform, operation1['type'])
    if(len(records) == 0):
        record = operation.views.create_operation_record_by_dict(platform, operation1)
        if(record != None):
            record_list.append(record)
        else:
            return False
    else:
        return False
    
    
def calc_temperature(request, platform):
    print 'calc_temperature'
    print request.REQUEST
    #{u'start_now': u'on', u'begin_date': u'20130922', u'end_date': u'20130923'}
    #{u'begin_date': u'', u'end_date': u''}    
    start_now = False    
    if 'start_now' in request.REQUEST:
        if(request.REQUEST['start_now'] == 'on'):
            start_now = True
    
    now_time = time.localtime(time.time())
    
    str_date = time.strftime("%Y%m%d", now_time)
    if 'date' in request.REQUEST:
        str_date = request.REQUEST['date']    
    print str_date
    
    dispatch_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
                
    operation = {}
    operation['type'] = 'calc_temperature'
    operation['name'] = str_date
    operation['user'] = request.user.username
    operation['dispatch_time'] = dispatch_time    
    operation['memo'] = ''
    
    return_datas = {}
    
    record_list = []
    result = operations_add_record_by_name(platform, record_list, operation)
    if(result == False):
        return_datas['success'] = False
        return_datas['data'] = 'calc_temperature operation add error, [%s] maybe exist.' % (str_date)
        return HttpResponse(json.dumps(return_datas))
    
    if(start_now == True):        
        p = Process(target=do_calc_temperature, args=(platform, record_list[0]))        
        p.start()
        
    return_datas['success'] = True
    return_datas['data'] = 'calc_temperature operation add success'
    
    str_datas = json.dumps(return_datas)
    response = HttpResponse(str_datas, mimetype='application/json;charset=UTF-8')
    response['Content-Length'] = len(str_datas)
    return response


def evaluate_temperature(request, platform):
    print 'evaluate_temperature'
    print request.REQUEST
    #{u'start_now': u'on', u'begin_date': u'20130922', u'end_date': u'20130923'}
    #{u'begin_date': u'', u'end_date': u''}
    
    start_now = False    
    if 'start_now' in request.REQUEST:
        if(request.REQUEST['start_now'] == 'on'):
            start_now = True
    
    begin_date = request.REQUEST['date']
    print begin_date
    
    now_time = time.localtime(time.time())
    today = time.strftime("%Y-%m-%d", now_time)
    dispatch_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    
    memo = begin_date
        
    operation1 = {}
    operation1['type'] = 'evaluate_temperature'
    operation1['name'] = today
    operation1['user'] = request.user.username
    operation1['dispatch_time'] = dispatch_time    
    operation1['memo'] = memo
    
    return_datas = {}
    
    record_list = []
    #result = add_record_one_operation(platform, record_list, operation1)
    #if(result == False):
    #    return_datas['success'] = False
    #    return_datas['data'] = 'evaluate_temperature operation add error, maybe exist.'
    #    return HttpResponse(json.dumps(return_datas))
    record = operation.views.create_operation_record_by_dict(platform, operation1)
    record_list.append(record)    
    
    if(start_now == True):
        # start thread.
        #t = Thread_COLD(platform, record_list[0])            
        #t.start()
        # start process
        p = Process(target=do_evaluate_temperature, args=(platform, record_list[0]))
        p.start()
        
    return_datas['success'] = True
    return_datas['data'] = 'evaluate_temperature operation add success'
    
    str_datas = json.dumps(return_datas)
    response = HttpResponse(str_datas, mimetype='application/json;charset=UTF-8')
    response['Content-Length'] = len(str_datas)
    return response


def get_parameters(request, platform):
    print 'get_parameters'
    print request.REQUEST
    
    v_config = config.views.get_config(platform)
    
    return_datas = {}
    return_datas['success'] = True
    return_datas['alpha'] = '%f' % (v_config.alpha)
    return_datas['mean_hits'] = '%d' % (v_config.mean_hits)
    
    str_datas = json.dumps(return_datas)
    response = HttpResponse(str_datas, mimetype='application/json;charset=UTF-8')
    response['Content-Length'] = len(str_datas)
    return response


def set_parameters(request, platform):
    print 'set_parameters'
    print request.REQUEST
    
    v_config = config.views.get_config(platform)
    v_config.alpha = string.atof(request.REQUEST['alpha'])
    v_config.mean_hits = string.atoi(request.REQUEST['mean_hits'])
    v_config.save()
    
    return_datas = {}
    return_datas['success'] = True
    return_datas['data'] = 'set_parameters success'
    
    str_datas = json.dumps(return_datas)
    response = HttpResponse(str_datas, mimetype='application/json;charset=UTF-8')
    response['Content-Length'] = len(str_datas)
    return response
    

def calc_hot_mean_hits_num(request, platform):
    print 'calc_hot_mean_hits_num'  
    print request.REQUEST
    #{u'start_now': u'on', u'date': u'20130922'}
    start_now = False
    if 'start_now' in request.REQUEST:
        if(request.REQUEST['start_now'] == 'on'):
            start_now = True
    
    begin_date = request.REQUEST['date']
    print begin_date    
        
    now_time = time.localtime(time.time())
    #today = time.strftime("%Y-%m-%d", now_time)
    dispatch_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
    
    begin_day = None
    return_datas = {}
    if(len(begin_date) >= 8):
        begin_day = datetime.date(string.atoi(begin_date[0:4]), string.atoi(begin_date[4:6]), string.atoi(begin_date[6:8])) 
    else:
        return_datas['success'] = False
        return_datas['data'] = 'date %s error' % (begin_date)  
        return HttpResponse(json.dumps(return_datas))
        
    record_list = []
    
    operation = {}
    operation['type'] = 'calc_hot_mean_hits_num'
    operation['name'] = ''
    operation['user'] = request.user.username
    operation['dispatch_time'] = dispatch_time
    operation['memo'] = ''
        
    operation['name'] = '%04d%02d%02d' % (begin_day.year, begin_day.month, begin_day.day)
    result = add_record_calc_hot_mean_hits_num(platform, record_list, operation)
    if(result == False):
        return_datas['success'] = False
        return_datas['data'] = 'date %s error' % (operation['name'])  
        return HttpResponse(json.dumps(return_datas))    
            
    if(start_now == True):
        # start thread.
        #t = Thread_UPLOAD(platform, record_list)            
        #t.start()
        # start process
        p = Process(target=do_calc_hot_mean_hits_num, args=(platform, record_list[0]))
        p.start()
        
    return_datas['success'] = True
    return_datas['data'] = 'day_num %d' % (1)  
    
    str_datas = json.dumps(return_datas)
    response = HttpResponse(str_datas, mimetype='application/json;charset=UTF-8')
    response['Content-Length'] = len(str_datas)
    return response
        
   
def test_insert(request, platform):
    print 'test_insert'
    #2014-01-07 16:00:00+00:00
    print datetime.datetime.now()
    record = models.mobile_task_hits(hash='1234', time='2014-01-08 00:00:00', hits_num=789)
    record.save()
    response = HttpResponse('test_insert done!')
    return response

def test_select(request, platform):
    print 'test_select'
    records = models.mobile_task_hits.objects.all()
    for record in records:
        print record
    response = HttpResponse('test_select done!')
    return response