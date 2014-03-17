#coding=utf-8
import time
import urllib
import urllib2
import hashlib
import random
import datetime
import string

import DB.db

def day_diff(date1, date2):
    d1 = datetime.datetime(string.atoi(date1[0:4]), string.atoi(date1[5:7]), string.atoi(date1[8:10]))
    d2 = datetime.datetime(string.atoi(date2[0:4]), string.atoi(date2[5:7]), string.atoi(date2[8:10]))
    return (d1-d2).days


class MS_INFO:
    
    def __init__(self, v_platform, v_db_record):        
        self.platform = None
        self.db_record = None
        #self.task_list = []
        self.task_dict = {}
        self.add_list = []
        self.delete_dict = {}
        self.keep_dict = {}
        self.will_be_full = False
        self.disk_can_be_used = 0L        
        self.add_filesize = 0L        
        self.init_task_num = 0
        self.distribute_num_for_topN = 0
        self.distribute_num_for_ALL = 0
        self.keep_num_for_topN = 0
        self.keep_num_for_ALL = 0
        self.num_should_be_deleted = 0
        self.num_actual_be_deleted = 0
        self.platform = v_platform
        self.db_record = v_db_record
        
        
class MS_GROUP:
    MACROSS_IP = '192.168.160.128'
    MACROSS_PORT = 80
    #MACROSS_IP = 'macross.funshion.com'
    #MACROSS_PORT = 27777
    BATCH_NUM = 2000
    
    def __init__(self, v_platform, v_ms_list = None, v_ms_id_list = None):
        self.log_file = None
        
        self.in_ms_list = v_ms_list
        self.ms_list = []
        self.ms_list_allowed_add = []
        self.ms_list_allowed_delete = []
        self.ms_id_list = []
        self.round_robin_index = 0
        
        self.platform = v_platform
        
        if(v_ms_list != None):
            for ms in v_ms_list:
                ms_info = MS_INFO(v_platform, ms)
                self.ms_list.append(ms_info)
            
        if(v_ms_id_list != None):
            for ms_id in v_ms_id_list:
                self.ms_id_list.append(ms_id)
                #find_availiable_ms(ms_id)
                for ms_info in self.ms_list:
                    if(ms_info.db_record.server_id == ms_id):
                        self.ms_list_allowed_delete.append(ms_info)
                        if(ms_info.db_record.is_dispatch == 1):
                            self.ms_list_allowed_add.append(ms_info)
        else:
            for ms_info in self.ms_list:
                self.ms_list_allowed_delete.append(ms_info)
                if(ms_info.db_record.is_dispatch == 1):
                    self.ms_list_allowed_add.append(ms_info)
                   
    
    def get_tasks(self):
        for one in self.ms_list:
            print '%s get tasks begin' % (one.db_record.controll_ip)
            #file_name = 'enum_task_%s.log' % (one.db_record.controll_ip)
            #log_file = open(file_name, 'w')
            try:        
                url = 'http://%s:%d/macross?cmd=enumtask' % (one.db_record.controll_ip, one.db_record.controll_port)
                print url
                #log_file.write('\nstep1: \n%s' % (url))
                req = urllib2.Request(url)
                response = urllib2.urlopen(req)
                output = response.read()
                #print output
                #log_file.write('\nstep2: \n%s' % (output))
                #return=ok
                #result=骑呢大状（国语版）-第16集-PAD:fsp:0:0:100:00001C597A755CF0D6A19D7F675C927047FF267E:1|国家地理之伟大工程巡礼系列-超级潜艇-HDPAD:fsp:0:0:100:00009D980AC62CE44ECFB4C22C735CF3EDA8267C:1|
                lines = output.split('\n')
                if(len(lines)>=2):
                    line_1 = lines[0].strip()
                    line_2 = lines[1].strip()
                    if(line_1 == 'return=ok'):
                        #fields = line_2.split('=')
                        prefix_len = len('result=')                        
                        field2 = line_2[prefix_len:]
                        #log_file.write('\nstep3: \n%s' % (field2))
                        values = field2.split('|')
                        for value in values:
                            #log_file.write('\nstep4: \n%s' % (value))
                            items = value.split(':')
                            if(len(items) >= 7):
                                #one.task_list.append(items[5])
                                one.task_dict[items[5]] = '1'
                                #log_file.write('\nstep5: \n%s' % (items[5]))
                                #print '%s append task %s' % (one.db_record.controll_ip, items[5])
            except:
                print '%s get tasks error' % (one.db_record.controll_ip)
            #print '%s get tasks end, %d' % (one.db_record.controll_ip, len(one.task_list))    
            print '%s get tasks end, %d' % (one.db_record.controll_ip, len(one.task_dict))
            #log_file.write('\nstep6: tasks_num=%d\n' % (len(one.task_dict)))
            #log_file.close()
        return True
    
    
    def get_tasks_macross_mobile(self):               
        db = DB.db.DB_MYSQL()
        #db.connect("192.168.8.101", 3317, "public", "funshion", "macross")
        db.connect(DB.db.DB_CONFIG.host, DB.db.DB_CONFIG.port, DB.db.DB_CONFIG.user, DB.db.DB_CONFIG.password, DB.db.DB_CONFIG.db)        
        
        for one in self.ms_list:
            print '%d, %s get tasks begin' % (one.db_record.server_id, one.db_record.controll_ip)
            
            sql = "SELECT d.dat_hash, d.create_time, d.filesize FROM fs_mobile_dat d, fs_mobile_ms_dat m WHERE d.dat_id = m.dat_id AND m.server_id=%d" % (one.db_record.server_id)                
            print sql
            db.execute(sql)      
            #print type(db.cur)  
            #print type(db.cur.fetchall())
            for row in db.cur.fetchall():
                col_num = 0
                one_task = {}
                for r in row:
                    if(col_num == 0):
                        #print str(r)
                        one_task['hash'] = r
                    elif(col_num == 1):
                        #print str(r)
                        one_task['online_time'] = r
                    elif(col_num == 2):
                        #print str(r)
                        one_task['filesize'] = r                                
                    col_num += 1  
                one.task_dict[one_task['hash']] = one_task 
                
            sql = "SELECT video_hash, create_time, filesize FROM fs_video_dat where server_id=%d" % (one.db_record.server_id)                
            print sql
            db.execute(sql)      
            #print type(db.cur)  
            #print type(db.cur.fetchall())
            for row in db.cur.fetchall():
                col_num = 0
                one_task = {}
                for r in row:
                    if(col_num == 0):
                        one_task['hash'] = r
                    elif(col_num == 1):
                        one_task['online_time'] = r
                    elif(col_num == 2):
                        one_task['filesize'] = r                                
                    col_num += 1  
                one.task_dict[one_task['hash']] = one_task
                
            one.init_task_num = len(one.task_dict)            
            print '%d, %s get tasks end, task_number=%d' % (one.db_record.server_id, one.db_record.controll_ip, len(one.task_dict)) 
            if(self.log_file != None):
                self.log_file.write('%d, %s get tasks end, task_number=%d\n' % (one.db_record.server_id, one.db_record.controll_ip, len(one.task_dict)))
        db.close()  
        #del db
        return True
    
    
    def get_tasks_macross_pc(self):               
        db = DB.db.DB_MYSQL()
        #db.connect("192.168.8.101", 3317, "public", "funshion", "macross")
        db.connect(DB.db.DB_CONFIG.host, DB.db.DB_CONFIG.port, DB.db.DB_CONFIG.user, DB.db.DB_CONFIG.password, DB.db.DB_CONFIG.db)        
        
        for one in self.ms_list:
            print '%d, %s get tasks begin' % (one.db_record.server_id, one.db_record.controll_ip)
            sql = "SELECT t.task_hash, t.create_time FROM fs_task t, fs_ms_task m WHERE t.task_id = m.task_id AND m.server_id=%d" % (one.db_record.server_id)    
            print sql
            db.execute(sql)      
            #print type(db.cur)  
            #print type(db.cur.fetchall())
            for row in db.cur.fetchall():
                col_num = 0
                one_task = {}
                for r in row:
                    if(col_num == 0):
                        one_task['hash'] = r
                    elif(col_num == 1):
                        one_task['online_time'] = r
                    elif(col_num == 2):
                        one_task['filesize'] = r                                 
                    col_num += 1  
                one.task_dict[one_task['hash']] = one_task
            one.init_task_num = len(one.task_dict)
            print '%d, %s get tasks end, task_number=%d' % (one.db_record.server_id, one.db_record.controll_ip, len(one.task_dict)) 
            if(self.log_file != None):
                self.log_file.write('%d, %s get tasks end, task_number=%d\n' % (one.db_record.server_id, one.db_record.controll_ip, len(one.task_dict)))
        db.close()  
        #del db
        return True
    
    
    def get_tasks_macross(self):               
        if(self.platform == 'mobile'):
            return self.get_tasks_macross_mobile()
        elif(self.platform == 'pc'):
            return self.get_tasks_macross_pc()
        return None   
            
            
            
    def get_tasks_num(self):
        total_num = 0
        for one in self.ms_list:
            total_num += len(one.task_dict)
        return total_num
            
            
    def find_ms_by_task(self, task_hash):
        for one in self.ms_list:
            if(one.task_dict.has_key(task_hash)):
                return one            
        return None
    
    
    def find_ms_list_by_task(self, task_hash):
        ms_list = []
        for one in self.ms_list:
            if ((one.keep_dict.has_key(task_hash)==False) and (one.task_dict.has_key(task_hash)==True)):
                ms_list.append(one)            
        return ms_list
    
    
    def find_task_is_keeped(self, task_hash):
        for one in self.ms_list:
            if (one.keep_dict.has_key(task_hash)==True):
                return True            
        return False
            
        
    def dispatch_hot_task(self, task_hash):   
        if(len(self.ms_list_allowed_add) == 0):
            return None
        ms_info = self.ms_list_allowed_add[self.round_robin_index]            
        ms_info.add_list.append(task_hash)
        self.round_robin_index = self.round_robin_index + 1
        if(self.round_robin_index >= len(self.ms_list_allowed_add)):
                self.round_robin_index = self.round_robin_index % len(self.ms_list_allowed_add)
        return ms_info
    
    
    def distribute_task(self, task_hash, task_size):   
        if(len(self.ms_list_allowed_add) == 0):
            return None
        
        if(task_size > 4*1024*1024*1024):
            task_size = 4*1024*1024*1024
        
        USAGE_RATIO = 90.0/100
        FREE_RATIO = 1.0 - USAGE_RATIO
        total_free_disk_space = 0L
        for ms_info in self.ms_list_allowed_add:
            if(ms_info.will_be_full == True):
                continue
            ms_total_disk_space = ms_info.db_record.total_disk_space*1024*1024*1024
            ms_free_disk_space = ms_info.db_record.free_disk_space*1024*1024*1024
            if(ms_free_disk_space <= ms_total_disk_space * FREE_RATIO):
                ms_info.will_be_full = True
                continue
            ms_free_disk_left = ms_free_disk_space - ms_info.add_filesize
            if(ms_free_disk_left <= ms_total_disk_space * FREE_RATIO):
                ms_info.will_be_full = True
                continue
            ms_can_be_used_disk = ms_free_disk_left - ms_total_disk_space * FREE_RATIO
            ms_info.disk_can_be_used = ms_can_be_used_disk
            total_free_disk_space += ms_can_be_used_disk
            
        random_value = random.random()
        total_free_disk_pos = total_free_disk_space * random_value
        #print 'total_free_disk_space=%ld, total_free_disk_pos=%ld' % (total_free_disk_space, total_free_disk_pos) 
        if(self.log_file != None):
                self.log_file.write('total_free_disk_space=%ld, total_free_disk_pos=%ld \n' % (total_free_disk_space, total_free_disk_pos) )
        temp_free_disk_space = 0L
        for ms_info in self.ms_list_allowed_add: 
            if(ms_info.will_be_full == True):
                continue
            # find the proper position firstly
            if(total_free_disk_pos >= temp_free_disk_space and total_free_disk_pos <= (temp_free_disk_space + ms_info.disk_can_be_used)):
                '''
                if(task_size >= ms_info.disk_can_be_used):
                    # move to next
                    temp_free_disk_space += ms_info.disk_can_be_used
                    continue
                '''
                ms_info.add_list.append(task_hash)
                ms_info.task_dict[task_hash] = '1'
                ms_info.add_filesize += task_size
                return ms_info
            temp_free_disk_space += ms_info.disk_can_be_used
        
        return None
        
    
    def ms_is_allowed_delete(self, one_ms):
        for ms_info in self.ms_list_allowed_delete:
            if(ms_info.db_record.server_id == one_ms.db_record.server_id):
                return True
        return False
    
        
    def delete_cold_task(self, one_ms, task_hash):
        if(self.ms_is_allowed_delete(one_ms) == False):
            return False
        
        if task_hash in one_ms.delete_dict:
            return False
        else:
            #print '%d, %s delete task %s' % (one_ms.db_record.server_id, one_ms.db_record.controll_ip, task_hash)
            one_ms.delete_dict[task_hash] = '1'
            return True
    
    
    '''
    http://MacrossAddress[:MacrossPort]/api/?cli=ms&cmd=report_hot_task
            提交方式：POST
            参数说明：
            $server_id：设备id
            $priority：处理的优先级权重,范围1~10，默认为1
            $ctime：当前时间戳，单位：秒
            $t：热门任务的hashid hashid,hashid,hashid[,hashid,……],hashid统一使用大写
            $sign：验证码；sign=md5(msreport_hot_task$server_id$priority$ctime$t$key),sign统一为小写
    '''
    def dispatch_batch(self, one, batch_list):
        cmd = 'report_hot_task'
        server_id = one.db_record.server_id
        priority = 1
        ctime = int(time.time())        
        t = ''
        key = ''
        sign = ''  
        
        num = 0
        for task_hash in batch_list:
            if(num > 0):
                t += ','
            t += task_hash
            num += 1
            
        src = ''
        src += cmd
        src += str(server_id)
        src += str(priority)
        src += str(ctime)
        src += t
        src += key
        sign = hashlib.md5(src).hexdigest().lower()
        
        values = {}
        values['server_id'] = str(server_id)
        values['priority']  = str(priority)
        values['ctime']     = str(ctime)
        values['t']         = t
        values['sign']      = sign
                
        url = 'http://%s:%d/api/?cli=ms&cmd=report_hot_task' % (self.MACROSS_IP, self.MACROSS_PORT)
        #print 'ms_id=%d, ms_ip=%s, task_num=%d, url=%s' % (one.db_record.server_id, one.db_record.controll_ip, num, url)
        if(self.log_file != None):
            self.log_file.write('ms_id=%d, ms_ip=%s, task_num=%d, url=%s\n' % (one.db_record.server_id, one.db_record.controll_ip, num, url))
        
        data = urllib.urlencode(values)
        #print data
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        the_page = response.read()        
        #print the_page        
        
        return True        
        
        
    def dispatch_to_ms(self, one):
        num = 0
        batch_list = []
        for task_hash in one.add_list:
            batch_list.append(task_hash)
            num += 1 
            if(num>=self.BATCH_NUM):
                self.dispatch_batch(one, batch_list)                
                num = 0
                batch_list = []
        
        if(num > 0):
            self.dispatch_batch(one, batch_list)
               
        return True
        
    
    def do_dispatch(self):        
        for one in self.ms_list_allowed_add:
            self.dispatch_to_ms(one)
        return True
    
    
    '''
    http://MacrossAddress[:MacrossPort]/api/?cli=ms&cmd=report_cold_task
            提交方式：POST
            参数说明：
            $server_id：设备id
            $priority：处理的优先级权重,范围1~10，默认为1
            $ctime：当前时间戳，单位：秒
            $t：热门任务的hashid hashid,hashid,hashid[,hashid,……],hashid统一使用大写
            $sign：验证码；sign=md5(msreport_cold_task$server_id$priority$ctime$t$key),sign统一为小写
    '''
    def delete_batch(self, one, batch_list):
        cmd = 'report_cold_task'
        server_id = one.db_record.server_id
        priority = 1
        ctime = int(time.time())        
        t = ''
        key = ''
        sign = ''  
        
        num = 0
        for task_hash in batch_list:
            if(num > 0):
                t += ','
            t += task_hash
            num += 1
            
        src = ''
        src += cmd
        src += str(server_id)
        src += str(priority)
        src += str(ctime)
        src += t
        src += key
        sign = hashlib.md5(src).hexdigest().lower()
        
        values = {}
        values['server_id'] = str(server_id)
        values['priority']  = str(priority)
        values['ctime']     = str(ctime)
        values['t']         = t
        values['sign']      = sign
                
        url = 'http://%s:%d/api/?cli=ms&cmd=report_cold_task' % (self.MACROSS_IP, self.MACROSS_PORT)        
        #print 'ms_id=%d, ms_ip=%s, task_num=%d, url=%s' % (one.db_record.server_id, one.db_record.controll_ip, num, url)
        if(self.log_file != None):
            self.log_file.write('ms_id=%d, ms_ip=%s, task_num=%d, url=%s\n' % (one.db_record.server_id, one.db_record.controll_ip, num, url))
        
        data = urllib.urlencode(values)
        #print data
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        the_page = response.read()
        #print the_page
        
        return True        
    
    
    def delete_from_ms(self, one):
        num = 0
        batch_list = []
        for (task_hash, value) in one.delete_dict.items():
            batch_list.append(task_hash)
            num += 1 
            if(num>=self.BATCH_NUM):
                self.delete_batch(one, batch_list)                
                num = 0
                batch_list = []
        
        if(num > 0):
            self.delete_batch(one, batch_list)
               
        return True
    
    
    def do_delete(self):        
        for one in self.ms_list_allowed_delete:
            self.delete_from_ms(one)
        return True
    
    
    def get_cur_ms(self):
        one = self.ms_list[self.round_robin_index]
        return one
    
    
    def copy(self):
        one_group = MS_GROUP(self.platform)
        one_group.ms_list = self.ms_list[:]
        one_group.ms_list_allowed_add = self.ms_list_allowed_add[:]
        one_group.ms_list_allowed_delete = self.ms_list_allowed_delete[:]
        return one_group
    
    
    def combine_group(self, ms_group):
        self.ms_list.extend(ms_group.ms_list)
        self.ms_list_allowed_add.extend(ms_group.ms_list_allowed_add)
        self.ms_list_allowed_delete.extend(ms_group.ms_list_allowed_delete)
        self.ms_id_list.extend(ms_group.ms_id_list)
        self.round_robin_index = 0
        return True
    
    
    def distribute_topN(self, task_list, topN):
        print 'distribute_topN'
        if(self.log_file != None):
            self.log_file.write('distribute_topN\n' )
        task_num = 0
        for one_task in task_list:
            one_ms = self.find_ms_by_task(one_task['hash'])
            if(one_ms == None):
                one_ms = self.distribute_task(one_task['hash'], one_task['filesize'])
                if(one_ms != None):
                    #print '%d: %s[%e][%d] distribute to %s' % (task_num, one_task['hash'], one_task['temperature0'], one_task['filesize'], one_ms.db_record.controll_ip) 
                    if(self.log_file != None):
                        self.log_file.write('%d: %s[%e][%d][%s] distribute to %s \n' % (task_num, one_task['hash'], one_task['temperature0'], one_task['filesize'], str(one_task['PayOrFree']), one_ms.db_record.controll_ip))
                else:
                    #print '%d: %s[%e][%d] can not be distributed!' % (task_num, one_task['hash'], one_task['temperature0'], one_task['filesize']) 
                    if(self.log_file != None):
                        self.log_file.write('%d: %s[%e][%d][%s] can not be distributed!\n' % (task_num, one_task['hash'], one_task['temperature0'], one_task['filesize'], str(one_task['PayOrFree'])))
            else:
                #print '%d: %s[%e][%d] exist in %s' % (task_num, one_task['hash'], one_task['temperature0'], one_task['filesize'], one_ms.db_record.controll_ip)   
                if(self.log_file != None):
                        self.log_file.write('%d: %s[%e][%d][%s] exist in %s\n' % (task_num, one_task['hash'], one_task['temperature0'], one_task['filesize'], str(one_task['PayOrFree']), one_ms.db_record.controll_ip) )         
            task_num += 1
            if(task_num >= topN):
                break
        for one_ms in self.ms_list_allowed_add:
            one_ms.distribute_num_for_topN = len(one_ms.add_list) 
        return True


    def distribute_ALL(self, task_list, topN):
        print 'distribute_ALL'
        if(self.log_file != None):
            self.log_file.write('distribute_ALL\n' )
        task_num = 0
        for one_task in task_list:
            one_ms = self.find_ms_by_task(one_task['hash'])
            if(one_ms == None):
                one_ms = self.distribute_task(one_task['hash'], one_task['filesize'])
                if(one_ms != None):
                    #print '%d: %s[%e][%d] distribute to %s' % (task_num, one_task['hash'], one_task['temperature0'], one_task['filesize'], one_ms.db_record.controll_ip) 
                    if(self.log_file != None):
                        self.log_file.write('%d: %s[%e][%d][%s] distribute to %s \n' % (task_num, one_task['hash'], one_task['temperature0'], one_task['filesize'], str(one_task['PayOrFree']), one_ms.db_record.controll_ip))
                else:
                    #print '%d: %s[%e][%d] can not be distributed!' % (task_num, one_task['hash'], one_task['temperature0'], one_task['filesize']) 
                    if(self.log_file != None):
                        self.log_file.write('%d: %s[%e][%d][%s] can not be distributed!\n' % (task_num, one_task['hash'], one_task['temperature0'], one_task['filesize'], str(one_task['PayOrFree'])))
            else:
                #print '%d: %s[%e][%d] exist in %s' % (task_num, one_task['hash'], one_task['temperature0'], one_task['filesize'], one_ms.db_record.controll_ip)   
                if(self.log_file != None):
                        self.log_file.write('%d: %s[%e][%d][%s] exist in %s\n' % (task_num, one_task['hash'], one_task['temperature0'], one_task['filesize'], str(one_task['PayOrFree']), one_ms.db_record.controll_ip) )         
            task_num += 1 
            if(task_num >= topN):
                break
        for one_ms in self.ms_list_allowed_add:
            one_ms.distribute_num_for_ALL = len(one_ms.add_list)        
        return True
        
    
    def find_ms_max_space(self, ms_list):
        ms_found = None
        base_free_ratio = 0.0
        for one_ms in ms_list:
            if(one_ms.db_record.total_disk_space <= 0):
                continue
            free_ratio = float(one_ms.db_record.free_disk_space) / float(one_ms.db_record.total_disk_space)
            if(free_ratio > base_free_ratio):
                base_free_ratio = free_ratio
                ms_found = one_ms
        return ms_found
    
    
    def choose_keep_unique(self, ms_list, task_hash):
        ms_list_num = len(ms_list)
        if(ms_list_num == 0):
            return False
        elif(ms_list_num == 1):            
            ms_list[0].keep_dict[task_hash] = '1'
        else:
            ms_found = self.find_ms_max_space(ms_list)
            if(ms_found != None):
                ms_found.keep_dict[task_hash] = '1'                
                if(self.log_file != None):
                    self.log_file.write('choose %s, %s, %d, %d\n' % (ms_found.db_record.server_name, ms_found.db_record.controll_ip, ms_found.db_record.total_disk_space, ms_found.db_record.free_disk_space))
        return True
        
        
    def keep_topN(self, task_list, topN):
        print 'keep_topN'
        if(self.log_file != None):
            self.log_file.write('keep_topN begin\n')
        task_num = 0
        for one_task in task_list:
            ms_list = self.find_ms_list_by_task(one_task['hash'])
            ms_list_num = len(ms_list)
            if(ms_list_num<=0):
                if(self.log_file != None):
                    self.log_file.write('%d: %s [%s][%e][%s] not found\n' % (task_num, one_task['hash'], one_task['online_time'], one_task['temperature0'], str(one_task['PayOrFree'])))
            else:                
                if(self.log_file != None):
                    self.log_file.write('%d: %s [%s][%e][%s] found %d, choose_keep_unique\n' % (task_num, one_task['hash'], one_task['online_time'], one_task['temperature0'], str(one_task['PayOrFree']), ms_list_num))
                    for one_ms in ms_list:
                        self.log_file.write('%s, %s, %d, %d\n' % (one_ms.db_record.server_name, one_ms.db_record.controll_ip, one_ms.db_record.total_disk_space, one_ms.db_record.free_disk_space))
                self.choose_keep_unique(ms_list, one_task['hash'])  
            task_num += 1    
            if(task_num>=topN):            
                break 
        for one_ms in self.ms_list_allowed_delete:
            one_ms.keep_num_for_topN = len(one_ms.keep_dict)
            print '%s, %s, keep_num_for_topN=%d' % (one_ms.db_record.server_name, one_ms.db_record.controll_ip, one_ms.keep_num_for_topN) 
            if(self.log_file != None):
                self.log_file.write('%s, %s, keep_num_for_topN=%d\n' % (one_ms.db_record.server_name, one_ms.db_record.controll_ip, one_ms.keep_num_for_topN))
        if(self.log_file != None):
            self.log_file.write('keep_topN end\n')
                   
        return True
    
    
    def keep_ALL(self, task_list, topN):
        print 'keep_ALL'
        if(self.log_file != None):
            self.log_file.write('keep_ALL begin\n')
        task_num = 0
        for one_task in task_list:
            if(self.find_task_is_keeped(one_task['hash']) == True):  
                if(self.log_file != None):
                    self.log_file.write('%d: %s [%s][%e][%s] have keeped\n' % (task_num, one_task['hash'], one_task['online_time'], one_task['temperature0'], str(one_task['PayOrFree'])))
            else:
                ms_list = self.find_ms_list_by_task(one_task['hash'])
                ms_list_num = len(ms_list)
                if(ms_list_num<=0):
                    if(self.log_file != None):
                        self.log_file.write('%d: %s [%s][%e][%s] not found\n' % (task_num, one_task['hash'], one_task['online_time'], one_task['temperature0'], str(one_task['PayOrFree'])))
                else:                
                    if(self.log_file != None):
                        self.log_file.write('%d: %s [%s][%e][%s] found %d, choose_keep_unique\n' % (task_num, one_task['hash'], one_task['online_time'], one_task['temperature0'], str(one_task['PayOrFree']), ms_list_num))
                        for one_ms in ms_list:
                            self.log_file.write('%s, %s, %d, %d\n' % (one_ms.db_record.server_name, one_ms.db_record.controll_ip, one_ms.db_record.total_disk_space, one_ms.db_record.free_disk_space))
                    self.choose_keep_unique(ms_list, one_task['hash'])  
            task_num += 1    
            if(task_num>=topN):            
                break 
        for one_ms in self.ms_list_allowed_delete:
            one_ms.keep_num_for_ALL = len(one_ms.keep_dict) 
            print '%s, %s, keep_num_for_ALL=%d' % (one_ms.db_record.server_name, one_ms.db_record.controll_ip, one_ms.keep_num_for_ALL)
            if(self.log_file != None):
                self.log_file.write('%s, %s, keep_num_for_ALL=%d\n' % (one_ms.db_record.server_name, one_ms.db_record.controll_ip, one_ms.keep_num_for_ALL))
        if(self.log_file != None):
            self.log_file.write('keep_ALL end\n')
                   
        return True
        
             
    def delete_complement(self, task_dict):
        if(self.log_file != None):
            self.log_file.write('ms_list: %d, ms_list_allowed_delete: %d \n' % (len(self.ms_list), len(self.ms_list_allowed_delete)))
            
        now_time = time.localtime(time.time())        
        today = time.strftime("%Y-%m-%d", now_time)
        
        DAYS_PROTECTED = 7
    
        for one_ms in self.ms_list_allowed_delete:  
            one_ms.num_should_be_deleted = len(one_ms.task_dict) - len(one_ms.keep_dict)
            if(self.log_file != None):
                self.log_file.write('%s, %s, task_dict: %d, keep_dict: %d, delete_dict: %d \n' % (one_ms.db_record.server_name, one_ms.db_record.controll_ip, len(one_ms.task_dict), len(one_ms.keep_dict), len(one_ms.delete_dict)))         
            for (key, value) in one_ms.task_dict.items():
                if(one_ms.keep_dict.has_key(key) == False):
                    one_ms.delete_dict[key] = value                    
                    if(task_dict.has_key(key)):
                        one_task = task_dict[key]
                        task_online_time = one_task['online_time'].strftime("%Y-%m-%d")
                        if(day_diff(today, task_online_time) <= DAYS_PROTECTED):
                            del one_ms.delete_dict[key]
                            if(self.log_file != None):
                                self.log_file.write('%s [%s][%s] not keeped, within %d days\n' % (key, one_task['online_time'], one_task['temperature0'], DAYS_PROTECTED))
                        else:
                            if(self.log_file != None):
                                self.log_file.write('%s [%s][%s] not keeped, which will be deleted\n' % (key, one_task['online_time'], one_task['temperature0']))                                
                    else:
                        task_online_time =value['online_time'].strftime("%Y-%m-%d")
                        if(day_diff(today, task_online_time) <= DAYS_PROTECTED):
                            del one_ms.delete_dict[key]
                            if(self.log_file != None):
                                self.log_file.write('%s [%s][%s] not keeped, within %d days\n' % (key, value['online_time'], 'unknown', DAYS_PROTECTED))                                
                        else:
                            if(self.log_file != None):
                                self.log_file.write('%s [%s][%s] not keeped, which will be deleted\n' % (key, value['online_time'], 'unknown'))                                
            one_ms.num_actual_be_deleted = len(one_ms.delete_dict)
            if(self.log_file != None):
                self.log_file.write('%s, %s, task_dict: %d, keep_dict: %d, delete_dict: %d,  num_should_be_deleted: %d, num_actual_be_deleted: %d\n' % \
                                    (one_ms.db_record.server_name, one_ms.db_record.controll_ip, len(one_ms.task_dict), len(one_ms.keep_dict), len(one_ms.delete_dict), \
                                     one_ms.num_should_be_deleted, one_ms.num_actual_be_deleted) \
                                    ) 
        return True    
    
    
    def get_distribute_num(self):
        total_num = 0
        for one_ms in self.ms_list:
            total_num += len(one_ms.add_list)
        return total_num
    
    
    def get_keep_num(self):
        total_num = 0
        for one_ms in self.ms_list:
            total_num += len(one_ms.keep_dict)
        return total_num
    
    
    def get_init_num(self):
        total_num = 0
        for one_ms in self.ms_list:
            total_num += one_ms.init_task_num
        return total_num
    
    
    def set_log(self, log_file):
        self.log_file = log_file
        return True
        
    def report_distribute_summary(self):        
        for one_ms in self.ms_list_allowed_add:
            distribute_num_diff = one_ms.distribute_num_for_ALL - one_ms.distribute_num_for_topN
            print '%s[%s], %s, %d, %d, %d, %d' % (one_ms.db_record.server_name, one_ms.db_record.room_name, one_ms.db_record.controll_ip, one_ms.init_task_num, \
                                                  one_ms.distribute_num_for_topN, distribute_num_diff, one_ms.distribute_num_for_ALL)
            if(self.log_file != None):
                self.log_file.write('%s[%s], %s, %d, %d, %d, %d\n' % (one_ms.db_record.server_name, one_ms.db_record.room_name, one_ms.db_record.controll_ip, one_ms.init_task_num, \
                                                                      one_ms.distribute_num_for_topN, distribute_num_diff, one_ms.distribute_num_for_ALL))
        return True
    
    
    def report_delete_summary(self):        
        for one_ms in self.ms_list_allowed_delete:
            keep_num_diff = one_ms.keep_num_for_ALL - one_ms.keep_num_for_topN
            print '%s[%s], %s, %d, %d, %d, %d, %d, %d' % (one_ms.db_record.server_name, one_ms.db_record.room_name, one_ms.db_record.controll_ip, one_ms.init_task_num, \
                                                  one_ms.keep_num_for_topN, keep_num_diff, one_ms.keep_num_for_ALL, one_ms.num_should_be_deleted, one_ms.num_actual_be_deleted)
            if(self.log_file != None):
                self.log_file.write('%s[%s], %s, %d, %d, %d, %d, %d, %d\n' % (one_ms.db_record.server_name, one_ms.db_record.room_name, one_ms.db_record.controll_ip, one_ms.init_task_num, \
                                                  one_ms.keep_num_for_topN, keep_num_diff, one_ms.keep_num_for_ALL, one_ms.num_should_be_deleted, one_ms.num_actual_be_deleted))
        return True