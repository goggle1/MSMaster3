//virtual_room.js

var ROOM_PAGE_SIZE = 20;
var ROOM_LONG_TIMEOUT = 20;


var virtual_roomJS = function(){    
        
    var self = this;
    var room_grid = new Object();       //定义全局grid，方便其他方法中的调用
    var room_store = new Object();      //定义全局store，方便其他方法中的调用
    var plat = '';
    var plat_ = '';    
    
    this.ext_virtual_room = function(tab_id, tab_title, param){
        var main_panel = Ext.getCmp("main_panel");
        self.plat = param;
        self.plat_ = self.plat + '_';
        
        self.room_store = new Ext.data.JsonStore({
            url : '/get_virtual_room_list/' + self.plat + '/',
            root : 'data',
            totalProperty : 'total_count',
            remoteSort : true,
            pruneModifiedRecords: true, 
            fields : [
                {name: 'virtual_room_id', type: 'int'},
                'virtual_room_name',
                'is_valid',
                'room_number',
                'ms_number',
                'task_number',
                'total_disk_space',
                'free_disk_space',
                'topN',
                'add_m',
                'add_N',
                'add_mN',
                'keep_m',
                'keep_N',
                'keep_mN',
                'delete_mN',
                'percent_50k',
                'percent_100k',
                'percent_200k'
            ]
        });

    
        var sel_mode = new Ext.grid.CheckboxSelectionModel();
        var room_mode = new Ext.grid.ColumnModel([
            new Ext.grid.RowNumberer(),
            sel_mode,
            {header : 'virtual_room_id', id : 'virtual_room_id', dataIndex : 'virtual_room_id', sortable : true},
            {header : 'virtual_room_name', id : 'virtual_room_name', dataIndex : 'virtual_room_name', sortable : true},
            {header : 'is_valid', id : 'is_valid', dataIndex : 'is_valid', sortable : true},
            {header : 'room_number', id : 'room_number', dataIndex : 'room_number', sortable : true},
            {header : 'ms_number', id : 'ms_number', dataIndex : 'ms_number', sortable : true},
            {header : 'task_number', id : 'task_number', dataIndex : 'task_number', sortable : true},
            {header : 'total_disk_space', id : 'total_disk_space', dataIndex : 'total_disk_space', sortable : true, renderer : disk_size},
            {header : 'free_disk_space', id : 'free_disk_space', dataIndex : 'free_disk_space', sortable : true, renderer : disk_status},
            {header : 'topN', id : 'topN', dataIndex : 'topN', sortable : true},
            {header : 'add_m', id : 'add_m', dataIndex : 'add_m', sortable : true, hidden : true},
            {header : 'add_N', id : 'add_N', dataIndex : 'add_N', sortable : true, hidden : true}, 
            {header : 'add_mN', id : 'add_mN', dataIndex : 'add_mN', sortable : true},
            {header : 'keep_m', id : 'keep_m', dataIndex : 'keep_m', sortable : true, hidden : true},
            {header : 'keep_N', id : 'keep_N', dataIndex : 'keep_N', sortable : true, hidden : true},
            {header : 'keep_mN', id : 'keep_mN', dataIndex : 'keep_mN', sortable : true},
            {header : 'delete_mN', id : 'delete_mN', dataIndex : 'delete_mN', sortable : true},
            {header : 'percent_50k', id : 'percent_50k', dataIndex : 'percent_50k', sortable : true},
            {header : 'percent_100k', id : 'percent_100k', dataIndex : 'percent_100k', sortable : true},
            {header : 'percent_200k', id : 'percent_200k', dataIndex : 'percent_200k', sortable : true, width: 200}
        ]);
    
        var room_page = new Ext.PagingToolbar({
                plugins: [new Ext.ui.plugins.SliderPageSize(), new Ext.ui.plugins.ComboPageSize({ addToItem: false, prefixText: '每页', postfixText: '条'}),new Ext.ux.ProgressBarPager()],
                //plugins: [new Ext.ui.plugins.SliderPageSize()],
                pageSize: ROOM_PAGE_SIZE,       //每页要展现的记录数，默认从定义的全局变量获取
                store: self.room_store,
                displayInfo: true,
                displayMsg: ' 显示第{0}条 到 {1}条记录， 共 {2}条',
                emptyMsg: "没有记录",
                prevText: "上一页",
                nextText: "下一页",
                refreshText: "刷新",
                lastText: "最后页",
                firstText: "第一页",
                beforePageText: "当前页",
                afterPageText: "共{0}页"
        });
        
        self.room_grid = new Ext.grid.EditorGridPanel({
            id:             tab_id,
            title:          tab_title,
            iconCls:        'tabs',
            clicksToEdit:   2,
            autoScroll:     true,       //内容溢出时出现滚动条
            closable:       true,
            columnLines:    true,       //True表示为在列分隔处显示分隔符
            collapsible:    false,      //面板是否可收缩的
            stripeRows:     true,       //隔行变色
            store:          self.room_store,
            colModel:       room_mode,
            selModel:       sel_mode,
            loadMask:       { msg: '正在加载数据，请稍侯……' },
            //stateId: tab_id+'_grid'
            viewConfig : {
                forceFit:true, sortAscText:'升序',sortDescText:'降序',columnsText:'可选列'
            },
            tbar: [{
                text: '新增',
                iconCls: 'add',
                handler: self.add_virtual_room
            },'-',{
                text: '修改',
                iconCls: 'modify',
                handler: self.modify_virtual_room
            },'-',{
                text: '删除',
                iconCls: 'del',
                handler: self.delete_virtual_room
            },'-',{             
                text: '统计汇总',               
                iconCls: 'sync',
                handler: self.stat_virtual_room
            },'-',{             
                text: '分发预算',               
                iconCls: 'sync',
                handler: self.virtual_room_simulate_add
            },'-',{             
                text: '删除预算',               
                iconCls: 'sync',
                handler: self.virtual_room_simulate_delete
            },'-',{             
                text: '最热占比计算',               
                iconCls: 'sync',
                handler: self.virtual_room_percent_topN
            },'-',{             
                text: '刷新列表',               
                iconCls: 'refresh',
                handler: self.refresh_virtual_room_list
            },'-',{             
                text: '详细状态',               
                iconCls: 'detail',
                handler: self.show_virtual_room_detail
            },'-',{             
                text: '分发任务',               
                iconCls: 'modify',
                handler: self.virtual_room_add_tasks
            },'-',{             
                text: '删除任务',               
                iconCls: 'modify',
                handler: self.virtual_room_delete_tasks
            }],
            listeners:{'render':createTbar},
            bbar: room_page
        });
    
        self.room_store.load({params:{start:0,limit:ROOM_PAGE_SIZE}});
        
        main_panel.add(self.room_grid);
        main_panel.setActiveTab(self.room_grid);
        
        function disk_size(value)
        {
            var i = 0;
            var n = 3;
            var iec = Array("B","KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB");
            while ((value/1024)>1)
            {
                value=value/1024;
                i++;
            }
            return (Math.round(value)+iec[i+n]);
        }
        
        function disk_status(value, metadata, record)
        {
            //var task_number = record.get('task_number');
            //var total_task_num = record.get('total_task_num');
            //if(task_number != total_task_num) metadata.css = 'bgred';
            
            if(value < 2000) 
            {
                metadata.css = 'bgred';
            }   
            
            var i = 0;
            var n = 3;
            var iec = Array("B","KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB");            
            while ((value/1024)>1){
                value=value/1024;
                i++;
            }
            //return value; 
            return (Math.round(value)+iec[i+n]);                    
        }
        
        //生成顶部工具条
        function createTbar(){
            var listener = {specialkey:function(field, e){if(e.getKey()==Ext.EventObject.ENTER){query_room();}}};
            var oneTbar = new Ext.Toolbar({
                items:['virtual_room_id: ',{
                        xtype:'textfield',
                        id: self.plat_+'virtual_room_id',
                        name:'virtual_room_id',
                        width:110
                    },"-",'virtual_room_name: ',{
                        xtype:'textfield',
                        id: self.plat_+'virtual_room_name',
                        name:'virtual_room_name',
                        width:110
                    },"-",{
                        text:'搜索',
                        iconCls: 'search',
                        handler: query_room
                    },"-",{
                        text:'重置',
                        iconCls: 'reset',
                        handler: reset_query_room
                    }]
            });
            oneTbar.render(self.room_grid.tbar);
        }
        
        
        function query_room(){          
            self.room_store.on('beforeload', function(obj) {
                Ext.apply(obj.baseParams,{
                        'start':0,
                        'limit':room_page.pageSize,
                        'virtual_room_id':Ext.getCmp(self.plat_+'virtual_room_id').getValue(),
                        'virtual_room_name':Ext.getCmp(self.plat_+'virtual_room_name').getValue()
                        });
            });         
            self.room_store.load();
        };
        
        function reset_query_room(){
            //将查询条件置为空，不可以将查询条件的充值放到beforeload里
            Ext.getCmp(self.plat_+'virtual_room_id').setValue("");
            Ext.getCmp(self.plat_+'virtual_room_name').setValue("");
            query_room();
        };
        
        //右键触发事件
        function rightClickRowMenu(grid,rowIndex,cellIndex,e){
            e.preventDefault();         //禁用浏览器默认的右键 ，针对某一行禁用
            if(rowIndex<0)return true;
            var record = grid.getStore().getAt(rowIndex);   //获取当前行的记录
            var cur_room_id = record.get('room_id');            //取得当前右键所在行的ROOM_ID
            var t_sm = grid.getSelectionModel();
            //此处为多选行，如果没有选择任意一行时，需要对右键当前行进行选中设置,如果当前右键所在行不在选择的行中，则移除所有选择的行，选择当前行，
            var room_id_arr = [];
            if(t_sm.getSelected()){
                var recs=t_sm.getSelections(); // 把所有选中项放入数组
                for(var i=0;i<recs.length;i++){
                    room_id_arr.push(recs[i].get("room_id"));
                }
            }
            var param_id = "";
            if(room_id_arr.indexOf(cur_room_id) < 0){
                //如果当前右键所在行不在选择的行中，则移除所有选择的行，选择当前行，
                //没有选择任意一行时,使用右键时，需要设置选中当前行
                t_sm.clearSelections();
                t_sm.selectRow(rowIndex);           //选中某一行
                grid.getView().focusRow(rowIndex);          //获取焦点
                param_id = cur_room_id;
            }else{
                param_id = room_id_arr.join(',');
            }
            //如果存在右键菜单，则需要清除右键里的所有菜单项item
            if(Ext.get('room_right_menu')){
                Ext.getCmp('room_right_menu').removeAll();
            }
                        
            //动态生成右键
            var menu_items = [];
            var auth_detail = {text:'机房详细状态',iconCls:'detail',handler:self.show_room_detail};
            //var auth_modify = {text:'修改任务信息',iconCls:'modify',handler:self.modifyTaskInfo};
            var auth_refresh = {text:'刷新机房列表',iconCls:'refresh',handler:self.refresh_room_list};
            menu_items.push(auth_detail);
            //menu_items.push(auth_modify);
            menu_items.push(auth_refresh);
            var rightMenu = new Ext.menu.Menu({
                            id:'room_right_menu',
                            items: menu_items
                        });
            //定位。显示右键菜单
            if(e.getXY()[0]==0||e.getXY()[1]==0)
                rightMenu.show(grid.getView().getCell(rowIndex,cellIndex));
            else
                rightMenu.showAt(e.getXY());
        }
        // 给控件添加右键菜单触发事件(rowcontextmenu)
        self.room_grid.addListener('cellcontextmenu', rightClickRowMenu);
        self.room_grid.addListener('contextmenu', function(e){e.preventDefault(); });       //禁用浏览器默认的右键 ,针对grid禁用
    
    };
    
     /**
     *通用JS 同步ajax调用 返回json Object
     * 
     * @param {}
     *            urlStr
     * @param {}
     *            paramsStr 为字符串键值对形式“key=value&key2=value2”
     * @return {} 返回json Object
     */
    function ajaxSyncCall(urlStr, paramsStr) {
        var obj;
        var value;
        if (window.ActiveXObject) {
            obj = new ActiveXObject('Microsoft.XMLHTTP');
        } else if (window.XMLHttpRequest) {
            obj = new XMLHttpRequest();
        }
        obj.open('POST', urlStr, false);
        obj.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        obj.send(paramsStr);
        var result = Ext.util.JSON.decode(obj.responseText);
        return result;
    }

    this.add_virtual_room = function() 
    {
        //避免win的重复生成
        if(Ext.get("add_virtual_room_win_" + self.plat)){
            Ext.getCmp("add_virtual_room_win_" + self.plat).show();
            return true;
        }
        
        var topN = 100000;      
        var virtual_room_id = 0;
        
        /*
        Ext.Ajax.request({
                url: 'get_max_virtual_room_id/'+self.plat+'/',
                scope:this,     
                sync:true,
                headers: {
                    'userHeader': 'userMsg'
                },
                params: { a: 10, b: 20 },
                method: 'GET',
                success: function (response, options) {
                    //Ext.MessageBox.alert('成功', '从服务端获取结果: ' + response.responseText); 
                    var result = Ext.util.JSON.decode(response.responseText);
                    virtual_room_id = parseInt(result.data); 
                    Ext.MessageBox.alert('成功', '从服务端获取结果: ' + virtual_room_id); 
                },
                failure: function (response, options) {
                    Ext.MessageBox.alert('失败', '请求超时或网络故障,错误编号：' + response.status);
                }
            });
          */
            
       	var result = ajaxSyncCall('get_max_virtual_room_id/'+self.plat+'/', '')  
       	virtual_room_id = parseInt(result.data);        
        //Ext.MessageBox.alert('ok', 'virtual_room_id: ' + virtual_room_id); 
        virtual_room_id += 1
                
        var add_virtual_room_form = new Ext.FormPanel({
            id: self.plat_+'add_virtual_room_form',
            autoWidth: true,//自动调整宽度
            url:'',
            frame:true,
            monitorValid : true,
            bodyStyle:'padding:5px 5px 0',
            labelWidth:150,
            defaults:{xtype:'textfield',width:200},
            items: [                                    
                {fieldLabel:'virtual_room_id',  
                    name: 'virtual_room_id', 
                    value: virtual_room_id, 
                    xtype: 'numberfield',
                    minValue: 0,
                    minText: 'id不能小于0',
                    allowBlank:false,
                    blankText:'id不能为空'
                },
                {fieldLabel:'virtual_room_name',    
                    name: 'virtual_room_name', 
                    value: 'input name', 
                    xtype: 'textfield',                                     
                    allowBlank:false,
                    blankText:'name不能为空'
                },
                {fieldLabel:'is_valid', 
                    name: 'is_valid', 
                    value: '1', 
                    xtype: 'numberfield',
                    minValue: 0,
                    minText: '或者为1，或者为0',
                    allowBlank:false,
                    blankText:'或者为1，或者为0'
                },
                {fieldLabel:'topN', 
                    name: 'topN', 
                    value: topN, 
                    xtype: 'numberfield',
                    minValue: 1,
                    minText: 'topN不能小于等于0',
                    allowBlank:false,
                    blankText:'topN不能为空'
                },
            ],
            buttons: [{
                text: '确定',
                handler: self.addVirtualRoomEnd,
                formBind : true
            },{
                text: '取消',
                handler: function(){Ext.getCmp("add_virtual_room_win_" + self.plat).close();}
            }]
        });
        
        var win = new Ext.Window({
            width:400,height:190,minWidth:200,minHeight:100,
            autoScroll:'auto',
            title : "新增虚拟机房",
            id : "add_virtual_room_win_" + self.plat,
            //renderTo: "ext_room",
            collapsible: true,
            modal:false,    //True 表示为当window显示时对其后面的一切内容进行遮罩，false表示为限制对其它UI元素的语法（默认为 false
            //所谓布局就是指容器组件中子元素的分布，排列组合方式
            layout: 'form',//layout布局方式为form
            maximizable:true,
            minimizable:false,
            items: add_virtual_room_form
        }).show();
    }
    
    this.addVirtualRoomEnd = function() {
        Ext.getCmp(self.plat_+"add_virtual_room_form").form.submit({
            waitMsg : '正在修改......',
            url : '/add_virtual_room/' + self.plat + '/',
            method : 'post',
            timeout : 5000,//5秒超时, 
            params : '',
            success : function(form, action) {
                var result = Ext.util.JSON.decode(action.response.responseText);
                Ext.getCmp("add_virtual_room_win_" + self.plat).close();
                Ext.MessageBox.alert('成功', result.data);
                //self.task_store.reload();         //重新载入数据，即根据当前页面的条件，刷新用户页面
            },
            failure : function(form, action) {
                alert('失败:' + action.response.responseText);
                if(typeof(action.response) == 'undefined'){
                    Ext.MessageBox.alert('警告','添加失败，请重新添加！');
                } else {
                    var result = Ext.util.JSON.decode(action.response.responseText);
                    if(action.failureType == Ext.form.Action.SERVER_INVALID){
                        Ext.MessageBox.alert('警告', result.data);
                    }else{
                        Ext.MessageBox.alert('警告','表单填写异常，请重新填写！');
                    }
                }
            }
        });
    };
    
    this.modify_virtual_room = function() 
    {
        var grid = self.room_grid;
        var sm = grid.getSelectionModel();      
        if(!sm.getSelected()){
            Ext.MessageBox.alert('提示','未选中记录');
            return false;
        }       
        var record = sm.getSelections()[0];   //获取当前行的记录        
        var virtual_room_id = record.get('virtual_room_id');        
        var virtual_room_name = record.get('virtual_room_name');
        var is_valid = record.get('is_valid');      
        var topN = record.get('topN');
        
        //避免win的重复生成
        if(Ext.get("modify_virtual_room_win_" + self.plat)){
            Ext.getCmp("modify_virtual_room_win_" + self.plat).show();
            return true;
        }
                
        var modify_virtual_room_form = new Ext.FormPanel({
            id: self.plat_+'modify_virtual_room_form',
            autoWidth: true,//自动调整宽度
            url:'',
            frame:true,
            monitorValid : true,
            bodyStyle:'padding:5px 5px 0',
            labelWidth:150,
            defaults:{xtype:'textfield',width:200},
            items: [                                    
                {fieldLabel:'virtual_room_id',  
                    name: 'virtual_room_id', 
                    value: virtual_room_id, 
                    xtype: 'numberfield',
                    minValue: 0,
                    minText: 'id不能小于0',
                    allowBlank:false,
                    blankText:'id不能为空'
                },
                {fieldLabel:'virtual_room_name',    
                    name: 'virtual_room_name', 
                    value: virtual_room_name, 
                    xtype: 'textfield',                                     
                    allowBlank:false,
                    blankText:'name不能为空'
                },
                {fieldLabel:'is_valid', 
                    name: 'is_valid', 
                    value: is_valid, 
                    xtype: 'numberfield',
                    minValue: 0,
                    minText: '或者为1，或者为0',
                    allowBlank:false,
                    blankText:'或者为1，或者为0'
                },
                {fieldLabel:'topN', 
                    name: 'topN', 
                    value: topN, 
                    xtype: 'numberfield',
                    minValue: 1,
                    minText: 'topN不能小于等于0',
                    allowBlank:false,
                    blankText:'topN不能为空'
                },
            ],
            buttons: [{
                text: '确定',
                handler: self.modifyVirtualRoomEnd,
                formBind : true
            },{
                text: '取消',
                handler: function(){Ext.getCmp("modify_virtual_room_win_" + self.plat).close();}
            }]
        });
        
        var win = new Ext.Window({
            width:400,height:190,minWidth:200,minHeight:100,
            autoScroll:'auto',
            title : "修改虚拟机房",
            id : "modify_virtual_room_win_" + self.plat,
            //renderTo: "ext_room",
            collapsible: true,
            modal:false,    //True 表示为当window显示时对其后面的一切内容进行遮罩，false表示为限制对其它UI元素的语法（默认为 false
            //所谓布局就是指容器组件中子元素的分布，排列组合方式
            layout: 'form',//layout布局方式为form
            maximizable:true,
            minimizable:false,
            items: modify_virtual_room_form
        }).show();
    }
    
    this.modifyVirtualRoomEnd = function() {
        Ext.getCmp(self.plat_+"modify_virtual_room_form").form.submit({
            waitMsg : '正在修改......',
            url : '/modify_virtual_room/' + self.plat + '/',
            method : 'post',
            timeout : 5000,//5秒超时, 
            params : '',
            success : function(form, action) {
                var result = Ext.util.JSON.decode(action.response.responseText);
                Ext.getCmp("modify_virtual_room_win_" + self.plat).close();
                Ext.MessageBox.alert('成功', result.data);
                //self.task_store.reload();         //重新载入数据，即根据当前页面的条件，刷新用户页面
            },
            failure : function(form, action) {
                alert('失败:' + action.response.responseText);
                if(typeof(action.response) == 'undefined'){
                    Ext.MessageBox.alert('警告','添加失败，请重新添加！');
                } else {
                    var result = Ext.util.JSON.decode(action.response.responseText);
                    if(action.failureType == Ext.form.Action.SERVER_INVALID){
                        Ext.MessageBox.alert('警告', result.data);
                    }else{
                        Ext.MessageBox.alert('警告','表单填写异常，请重新填写！');
                    }
                }
            }
        });
    };
    
    
    this.delete_virtual_room = function() 
    {
        var grid = self.room_grid;
        var sm = grid.getSelectionModel();      
        if(!sm.getSelected()){
            Ext.MessageBox.alert('提示','未选中记录');
            return false;
        }       
        var record = sm.getSelections()[0];   //获取当前行的记录        
        var virtual_room_id = record.get('virtual_room_id');        
        var virtual_room_name = record.get('virtual_room_name');
        var is_valid = record.get('is_valid');      
        var topN = record.get('topN');
        
        //避免win的重复生成
        if(Ext.get("delete_virtual_room_win_" + self.plat)){
            Ext.getCmp("delete_virtual_room_win_" + self.plat).show();
            return true;
        }
                
        var delete_virtual_room_form = new Ext.FormPanel({
            id: self.plat_+'delete_virtual_room_form',
            autoWidth: true,//自动调整宽度
            url:'',
            frame:true,
            monitorValid : true,
            bodyStyle:'padding:5px 5px 0',
            labelWidth:150,
            defaults:{xtype:'textfield',width:200},
            items: [                                    
                {fieldLabel:'virtual_room_id',  
                    name: 'virtual_room_id', 
                    value: virtual_room_id, 
                    xtype: 'numberfield',
                    minValue: 0,
                    minText: 'id不能小于0',
                    allowBlank:false,
                    blankText:'id不能为空'
                },
                {fieldLabel:'virtual_room_name',    
                    name: 'virtual_room_name', 
                    value: virtual_room_name, 
                    xtype: 'textfield',                                     
                    allowBlank:false,
                    blankText:'name不能为空'
                },
                {fieldLabel:'is_valid', 
                    name: 'is_valid', 
                    value: is_valid, 
                    xtype: 'numberfield',
                    minValue: 0,
                    minText: '或者为1，或者为0',
                    allowBlank:false,
                    blankText:'或者为1，或者为0'
                },
                {fieldLabel:'topN', 
                    name: 'topN', 
                    value: topN, 
                    xtype: 'numberfield',
                    minValue: 1,
                    minText: 'topN不能小于等于0',
                    allowBlank:false,
                    blankText:'topN不能为空'
                },
            ],
            buttons: [{
                text: '确定',
                handler: self.deleteVirtualRoomEnd,
                formBind : true
            },{
                text: '取消',
                handler: function(){Ext.getCmp("delete_virtual_room_win_" + self.plat).close();}
            }]
        });
        
        var win = new Ext.Window({
            width:400,height:190,minWidth:200,minHeight:100,
            autoScroll:'auto',
            title : "删除虚拟机房",
            id : "delete_virtual_room_win_" + self.plat,
            //renderTo: "ext_room",
            collapsible: true,
            modal:false,    //True 表示为当window显示时对其后面的一切内容进行遮罩，false表示为限制对其它UI元素的语法（默认为 false
            //所谓布局就是指容器组件中子元素的分布，排列组合方式
            layout: 'form',//layout布局方式为form
            maximizable:true,
            minimizable:false,
            items: delete_virtual_room_form
        }).show();
    }
    
    this.deleteVirtualRoomEnd = function() {
        Ext.getCmp(self.plat_+"delete_virtual_room_form").form.submit({
            waitMsg : '正在修改......',
            url : '/delete_virtual_room/' + self.plat + '/',
            method : 'post',
            timeout : 5000,//5秒超时, 
            params : '',
            success : function(form, action) {
                var result = Ext.util.JSON.decode(action.response.responseText);
                Ext.getCmp("delete_virtual_room_win_" + self.plat).close();
                Ext.MessageBox.alert('成功', result.data);
                //self.task_store.reload();         //重新载入数据，即根据当前页面的条件，刷新用户页面
            },
            failure : function(form, action) {
                alert('失败:' + action.response.responseText);
                if(typeof(action.response) == 'undefined'){
                    Ext.MessageBox.alert('警告','添加失败，请重新添加！');
                } else {
                    var result = Ext.util.JSON.decode(action.response.responseText);
                    if(action.failureType == Ext.form.Action.SERVER_INVALID){
                        Ext.MessageBox.alert('警告', result.data);
                    }else{
                        Ext.MessageBox.alert('警告','表单填写异常，请重新填写！');
                    }
                }
            }
        });
    };
    
    this.stat_virtual_room = function() 
    {
        //避免win的重复生成
        if(Ext.get("stat_virtual_room_win_" + self.plat)){
            Ext.getCmp("stat_virtual_room_win_" + self.plat).show();
            return true;
        }
        
        var grid = self.room_grid;
        var t_sm = grid.getSelectionModel();
        var virtual_room_ids = []
        var recs = t_sm.getSelections();
        for (var i = 0; i < recs.length; i++) 
        {
            virtual_room_ids.push(recs[i].get('virtual_room_id'));
        }
        
        var stat_virtual_room_form = new Ext.FormPanel({
            id: self.plat_+'stat_virtual_room_form',
            autoWidth: true,//自动调整宽度
            url:'',
            frame:true,
            monitorValid : true,
            bodyStyle:'padding:5px 5px 0',
            labelWidth:150,
            defaults:{xtype:'textfield',width:200},
            items: [   
            	{fieldLabel:'ids',      name:'ids',     value: virtual_room_ids,     hidden:true},
                {fieldLabel:'ids',      name:'ids',     value: virtual_room_ids,     disabled:true},                                 
                {
                    xtype:'checkbox',
                    id: 'start_now',
                    name: 'start_now',
                    //align:'left',
                    fieldLabel:'是否立即执行',
                    checked: false
                }   
            ],
            buttons: [{
                text: '确定',
                handler: self.statVirtualRoomEnd,
                formBind : true
            },{
                text: '取消',
                handler: function(){Ext.getCmp("stat_virtual_room_win_" + self.plat).close();}
            }]
        });
        
        var win = new Ext.Window({
            width:400,height:135,minWidth:200,minHeight:100,
            autoScroll:'auto',
            title : "统计汇总，汇总虚拟机房内信息",
            id : "stat_virtual_room_win_" + self.plat,
            //renderTo: "ext_room",
            collapsible: true,
            modal:false,    //True 表示为当window显示时对其后面的一切内容进行遮罩，false表示为限制对其它UI元素的语法（默认为 false
            //所谓布局就是指容器组件中子元素的分布，排列组合方式
            layout: 'form',//layout布局方式为form
            maximizable:true,
            minimizable:false,
            items: stat_virtual_room_form
        }).show();
    }
    
    this.statVirtualRoomEnd = function() {
        Ext.getCmp(self.plat_+"stat_virtual_room_form").form.submit({
            waitMsg : '正在修改......',
            url : '/stat_virtual_room/' + self.plat + '/',
            method : 'post',
            timeout : 5000,//5秒超时, 
            params : '',
            success : function(form, action) {
                var result = Ext.util.JSON.decode(action.response.responseText);
                Ext.getCmp("stat_virtual_room_win_" + self.plat).close();
                Ext.MessageBox.alert('成功', result.data);
                //self.task_store.reload();         //重新载入数据，即根据当前页面的条件，刷新用户页面
            },
            failure : function(form, action) {
                alert('失败:' + action.response.responseText);
                if(typeof(action.response) == 'undefined'){
                    Ext.MessageBox.alert('警告','添加失败，请重新添加！');
                } else {
                    var result = Ext.util.JSON.decode(action.response.responseText);
                    if(action.failureType == Ext.form.Action.SERVER_INVALID){
                        Ext.MessageBox.alert('警告', result.data);
                    }else{
                        Ext.MessageBox.alert('警告','表单填写异常，请重新填写！');
                    }
                }
            }
        });
    };
        
    this.virtual_room_simulate_add = function() 
    {
        //避免win的重复生成
        if(Ext.get("virtual_room_simulate_add_win_" + self.plat)){
            Ext.getCmp("virtual_room_simulate_add_win_" + self.plat).show();
            return true;
        }
        
        var grid = self.room_grid;
        var t_sm = grid.getSelectionModel();
        var virtual_room_ids = []
        var recs = t_sm.getSelections();
        for (var i = 0; i < recs.length; i++) 
        {
            virtual_room_ids.push(recs[i].get('virtual_room_id'));
        }
        
        var virtual_room_simulate_add_form = new Ext.FormPanel({
            id: self.plat_+'virtual_room_simulate_add_form',
            autoWidth: true,//自动调整宽度
            url:'',
            frame:true,
            monitorValid : true,
            bodyStyle:'padding:5px 5px 0',
            labelWidth:150,
            defaults:{xtype:'textfield',width:200},
            items: [ 
            	{fieldLabel:'ids',      name:'ids',     value: virtual_room_ids,     hidden:true},
                {fieldLabel:'ids',      name:'ids',     value: virtual_room_ids,     disabled:true},                                   
                {
                    xtype:'checkbox',
                    id: 'start_now',
                    name: 'start_now',
                    //align:'left',
                    fieldLabel:'是否立即执行',
                    checked: false
                }   
            ],
            buttons: [{
                text: '确定',
                handler: self.virtualRoomSimulateAddEnd,
                formBind : true
            },{
                text: '取消',
                handler: function(){Ext.getCmp("virtual_room_simulate_add_win_" + self.plat).close();}
            }]
        });
        
        var win = new Ext.Window({
            width:400,height:135,minWidth:200,minHeight:100,
            autoScroll:'auto',
            title : "分发预算，只计算，并不分发",
            id : "virtual_room_simulate_add_win_" + self.plat,
            //renderTo: "ext_room",
            collapsible: true,
            modal:false,    //True 表示为当window显示时对其后面的一切内容进行遮罩，false表示为限制对其它UI元素的语法（默认为 false
            //所谓布局就是指容器组件中子元素的分布，排列组合方式
            layout: 'form',//layout布局方式为form
            maximizable:true,
            minimizable:false,
            items: virtual_room_simulate_add_form
        }).show();
    }
    
    this.virtualRoomSimulateAddEnd = function() {
        Ext.getCmp(self.plat_+"virtual_room_simulate_add_form").form.submit({
            waitMsg : '正在修改......',
            url : '/virtual_room_simulate_add/' + self.plat + '/',
            method : 'post',
            timeout : 5000,//5秒超时, 
            params : '',
            success : function(form, action) {
                var result = Ext.util.JSON.decode(action.response.responseText);
                Ext.getCmp("virtual_room_simulate_add_win_" + self.plat).close();
                Ext.MessageBox.alert('成功', result.data);
                //self.task_store.reload();         //重新载入数据，即根据当前页面的条件，刷新用户页面
            },
            failure : function(form, action) {
                alert('失败:' + action.response.responseText);
                if(typeof(action.response) == 'undefined'){
                    Ext.MessageBox.alert('警告','添加失败，请重新添加！');
                } else {
                    var result = Ext.util.JSON.decode(action.response.responseText);
                    if(action.failureType == Ext.form.Action.SERVER_INVALID){
                        Ext.MessageBox.alert('警告', result.data);
                    }else{
                        Ext.MessageBox.alert('警告','表单填写异常，请重新填写！');
                    }
                }
            }
        });
    };
    
    this.virtual_room_simulate_delete = function() 
    {
        //避免win的重复生成
        if(Ext.get("virtual_room_simulate_delete_win_" + self.plat)){
            Ext.getCmp("virtual_room_simulate_delete_win_" + self.plat).show();
            return true;
        }
        
        var grid = self.room_grid;
        var t_sm = grid.getSelectionModel();
        var virtual_room_ids = []
        var recs = t_sm.getSelections();
        for (var i = 0; i < recs.length; i++) 
        {
            virtual_room_ids.push(recs[i].get('virtual_room_id'));
        }
        
        var virtual_room_simulate_delete_form = new Ext.FormPanel({
            id: self.plat_+'virtual_room_simulate_delete_form',
            autoWidth: true,//自动调整宽度
            url:'',
            frame:true,
            monitorValid : true,
            bodyStyle:'padding:5px 5px 0',
            labelWidth:150,
            defaults:{xtype:'textfield',width:200},
            items: [ 
            	{fieldLabel:'ids',      name:'ids',     value: virtual_room_ids,     hidden:true},
                {fieldLabel:'ids',      name:'ids',     value: virtual_room_ids,     disabled:true},                                        
                {
                    xtype:'checkbox',
                    id: 'start_now',
                    name: 'start_now',
                    //align:'left',
                    fieldLabel:'是否立即执行',
                    checked: false
                }   
            ],
            buttons: [{
                text: '确定',
                handler: self.virtualRoomSimulateDeleteEnd,
                formBind : true
            },{
                text: '取消',
                handler: function(){Ext.getCmp("virtual_room_simulate_delete_win_" + self.plat).close();}
            }]
        });
        
        var win = new Ext.Window({
            width:400,height:135,minWidth:200,minHeight:100,
            autoScroll:'auto',
            title : "删除预算，只计算，并不删除",
            id : "virtual_room_simulate_delete_win_" + self.plat,
            //renderTo: "ext_room",
            collapsible: true,
            modal:false,    //True 表示为当window显示时对其后面的一切内容进行遮罩，false表示为限制对其它UI元素的语法（默认为 false
            //所谓布局就是指容器组件中子元素的分布，排列组合方式
            layout: 'form',//layout布局方式为form
            maximizable:true,
            minimizable:false,
            items: virtual_room_simulate_delete_form
        }).show();
    }
    
    this.virtualRoomSimulateDeleteEnd = function() {
        Ext.getCmp(self.plat_+"virtual_room_simulate_delete_form").form.submit({
            waitMsg : '正在修改......',
            url : '/virtual_room_simulate_delete/' + self.plat + '/',
            method : 'post',
            timeout : 5000,//5秒超时, 
            params : '',
            success : function(form, action) {
                var result = Ext.util.JSON.decode(action.response.responseText);
                Ext.getCmp("virtual_room_simulate_delete_win_" + self.plat).close();
                Ext.MessageBox.alert('成功', result.data);
                //self.task_store.reload();         //重新载入数据，即根据当前页面的条件，刷新用户页面
            },
            failure : function(form, action) {
                alert('失败:' + action.response.responseText);
                if(typeof(action.response) == 'undefined'){
                    Ext.MessageBox.alert('警告','添加失败，请重新添加！');
                } else {
                    var result = Ext.util.JSON.decode(action.response.responseText);
                    if(action.failureType == Ext.form.Action.SERVER_INVALID){
                        Ext.MessageBox.alert('警告', result.data);
                    }else{
                        Ext.MessageBox.alert('警告','表单填写异常，请重新填写！');
                    }
                }
            }
        });
    };
    
    this.virtual_room_percent_topN = function() 
    {
        //避免win的重复生成
        if(Ext.get("virtual_room_percent_topN_win_" + self.plat)){
            Ext.getCmp("virtual_room_percent_topN_win_" + self.plat).show();
            return true;
        }
        
        var grid = self.room_grid;
        var t_sm = grid.getSelectionModel();
        var virtual_room_ids = []
        var recs = t_sm.getSelections();
        for (var i = 0; i < recs.length; i++) 
        {
            virtual_room_ids.push(recs[i].get('virtual_room_id'));
        }
        
        var virtual_room_percent_topN_form = new Ext.FormPanel({
            id: self.plat_+'virtual_room_percent_topN_form',
            autoWidth: true,//自动调整宽度
            url:'',
            frame:true,
            monitorValid : true,
            bodyStyle:'padding:5px 5px 0',
            labelWidth:150,
            defaults:{xtype:'textfield',width:200},
            items: [ 
            	{fieldLabel:'ids',      name:'ids',     value: virtual_room_ids,     hidden:true},
                {fieldLabel:'ids',      name:'ids',     value: virtual_room_ids,     disabled:true},                                    
                {
                    xtype:'checkbox',
                    id: 'start_now',
                    name: 'start_now',
                    //align:'left',
                    fieldLabel:'是否立即执行',
                    checked: false
                }   
            ],
            buttons: [{
                text: '确定',
                handler: self.virtualRoomPercentTopNEnd,
                formBind : true
            },{
                text: '取消',
                handler: function(){Ext.getCmp("virtual_room_percent_topN_win_" + self.plat).close();}
            }]
        });
        
        var win = new Ext.Window({
            width:400,height:135,minWidth:200,minHeight:100,
            autoScroll:'auto',
            title : "最热占比计算，top5万，top10万，top20万",
            id : "virtual_room_percent_topN_win_" + self.plat,
            //renderTo: "ext_room",
            collapsible: true,
            modal:false,    //True 表示为当window显示时对其后面的一切内容进行遮罩，false表示为限制对其它UI元素的语法（默认为 false
            //所谓布局就是指容器组件中子元素的分布，排列组合方式
            layout: 'form',//layout布局方式为form
            maximizable:true,
            minimizable:false,
            items: virtual_room_percent_topN_form
        }).show();
    }
    
    this.virtualRoomPercentTopNEnd = function() {
        Ext.getCmp(self.plat_+"virtual_room_percent_topN_form").form.submit({
            waitMsg : '正在修改......',
            url : '/virtual_room_percent_topN/' + self.plat + '/',
            method : 'post',
            timeout : 5000,//5秒超时, 
            params : '',
            success : function(form, action) {
                var result = Ext.util.JSON.decode(action.response.responseText);
                Ext.getCmp("virtual_room_percent_topN_win_" + self.plat).close();
                Ext.MessageBox.alert('成功', result.data);
                //self.task_store.reload();         //重新载入数据，即根据当前页面的条件，刷新用户页面
            },
            failure : function(form, action) {
                alert('失败:' + action.response.responseText);
                if(typeof(action.response) == 'undefined'){
                    Ext.MessageBox.alert('警告','添加失败，请重新添加！');
                } else {
                    var result = Ext.util.JSON.decode(action.response.responseText);
                    if(action.failureType == Ext.form.Action.SERVER_INVALID){
                        Ext.MessageBox.alert('警告', result.data);
                    }else{
                        Ext.MessageBox.alert('警告','表单填写异常，请重新填写！');
                    }
                }
            }
        });
    };
    
    
    this.refresh_virtual_room_list = function() 
    {
        self.room_store.reload();
    };
    
    
    this.show_virtual_room_detail = function() {
        var grid = self.room_grid;
        var t_sm = grid.getSelectionModel();

        //此处为多选行，如果没有选中任意一行时，需要对右键当前行进行选中设置
        //如果右键当前行不在选中的行中，则移除所选的行，选择当前行
        var room_ids = []
        if (t_sm.getSelected()) 
        {
            var recs = t_sm.getSelections();
            for (var i = 0; i < recs.length; i++) 
            {
                room_ids.push(recs[i].get('virtual_room_id'));
            }
        }
        else
        {
            return true;
        }
        //console.log(room_ids);

        Ext.Ajax.request({
            url: '/show_virtual_room_detail/' + self.plat + '/',                
            params: 'ids=' + room_ids,
            success: function(response) {
                //Ext.MessageBox.alert('成功', Ext.encode(response)); 
                //console.log(response.responseText);               
                var room_panel = new Ext.Panel({
                  //renderTo: 'panelDiv',
                  title: '虚拟机房状态: ' + room_ids,
                  iconCls : 'tabs',
                  closable : true,
                  autoScroll: true,
                  items:[{
                    html: response.responseText
                  }]
                });
                var main_panel = Ext.getCmp("main_panel");
                main_panel.add(room_panel);
                main_panel.setActiveTab(room_panel);        
                
            },
            failure: function(response){
                Ext.MessageBox.alert('失败', Ext.encode(response));
            }
            //timeout: (this.timeout*1000);
        });

    };
    
    this.virtual_room_add_tasks = function(){
        var grid = self.room_grid;
        var sm = grid.getSelectionModel();      
        if(!sm.getSelected()){
            Ext.MessageBox.alert('提示','未选中记录');
            return false;
        }       
        var record = sm.getSelections()[0];   //获取当前行的记录        
        var virtual_room_id = record.get('virtual_room_id');        
        var virtual_room_name = record.get('virtual_room_name');
        var topN = record.get('topN');              
        //避免win的重复生成
        if(Ext.get("virtual_room_add_tasks_win_" + self.plat)){
            Ext.getCmp("virtual_room_add_tasks_win_" + self.plat).show();
            return true;
        }
        
        var virtual_room_add_tasks_form = new Ext.FormPanel({
            id: self.plat_+'virtual_room_add_tasks_form',
            autoWidth: true,//自动调整宽度
            url:'',
            frame:true,
            monitorValid : true,
            bodyStyle:'padding:5px 5px 0',
            labelWidth:150,
            defaults:{xtype:'textfield',width:200},
            items: [
                {fieldLabel:'virtual_room_id',      name:'virtual_room_id',     value: virtual_room_id,     hidden:true},
                {fieldLabel:'virtual_room_id',      name:'virtual_room_id',     value: virtual_room_id,     disabled:true},
                {fieldLabel:'virtual_room_name',    name:'virtual_room_name',   value: virtual_room_name,   disabled:true},             
                {fieldLabel:'topN',     name:'topN',    value: topN, disabled:true},                
                {
                    xtype:'checkbox',
                    id: 'start_now',
                    name: 'start_now',
                    //align:'left',
                    fieldLabel:'是否立即执行',
                    checked: false
                }   
            ],
            buttons: [{
                text: '确定',
                handler: self.virtualRoomAddTasksEnd,
                formBind : true
            },{
                text: '取消',
                handler: function(){Ext.getCmp("virtual_room_add_tasks_win_" + self.plat).close();}
            }]
        });
        
        var win = new Ext.Window({
            width:400,height:190,minWidth:200,minHeight:100,
            autoScroll:'auto',
            title : "虚拟机房分发任务",
            id : "virtual_room_add_tasks_win_" + self.plat,
            //renderTo: "ext_room",
            collapsible: true,
            modal:false,    //True 表示为当window显示时对其后面的一切内容进行遮罩，false表示为限制对其它UI元素的语法（默认为 false
            //所谓布局就是指容器组件中子元素的分布，排列组合方式
            layout: 'form',//layout布局方式为form
            maximizable:true,
            minimizable:false,
            items: virtual_room_add_tasks_form
        }).show();
        
        
    };
    
    this.virtualRoomAddTasksEnd = function() {
        Ext.getCmp(self.plat_+"virtual_room_add_tasks_form").form.submit({
            waitMsg : '正在修改......',
            url : '/virtual_room_add_tasks/' + self.plat + '/',
            method : 'post',
            timeout : 5000,//5秒超时, 
            params : '',
            success : function(form, action) {
                var result = Ext.util.JSON.decode(action.response.responseText);
                Ext.getCmp("virtual_room_add_tasks_win_" + self.plat).close();
                Ext.MessageBox.alert('成功', result.data);
                self.room_store.reload();           //重新载入数据，即根据当前页面的条件，刷新用户页面
            },
            failure : function(form, action) {
                alert('失败:' + action.response.responseText);
                if(typeof(action.response) == 'undefined'){
                    Ext.MessageBox.alert('警告','添加失败，请重新添加！');
                } else {
                    var result = Ext.util.JSON.decode(action.response.responseText);
                    if(action.failureType == Ext.form.Action.SERVER_INVALID){
                        Ext.MessageBox.alert('警告', result.data);
                    }else{
                        Ext.MessageBox.alert('警告','表单填写异常，请重新填写！');
                    }
                }
            }
        });
    };
    
    this.virtual_room_delete_tasks = function(){
        var grid = self.room_grid;
        var sm = grid.getSelectionModel();      
        if(!sm.getSelected()){
            Ext.MessageBox.alert('提示','未选中记录');
            return false;
        }       
        var record = sm.getSelections()[0];   //获取当前行的记录        
        var virtual_room_id = record.get('virtual_room_id');        
        var virtual_room_name = record.get('virtual_room_name');
        var topN = record.get('topN');
        //避免win的重复生成
        if(Ext.get("virtual_room_delete_tasks_win_" + self.plat)){
            Ext.getCmp("virtual_room_delete_tasks_win_" + self.plat).show();
            return true;
        }
        
        var virtual_room_delete_tasks_form = new Ext.FormPanel({
            id: self.plat_+'virtual_room_delete_tasks_form',
            autoWidth: true,//自动调整宽度
            url:'',
            frame:true,
            monitorValid : true,
            bodyStyle:'padding:5px 5px 0',
            labelWidth:150,
            defaults:{xtype:'textfield',width:200},
            items: [
                {fieldLabel:'virtual_room_id',      name:'virtual_room_id',     value: virtual_room_id,     hidden:true},
                {fieldLabel:'virtual_room_id',      name:'virtual_room_id',     value: virtual_room_id,     disabled:true},
                {fieldLabel:'virtual_room_name',    name:'virtual_room_name',   value: virtual_room_name,   disabled:true},         
                {fieldLabel:'topN',     name:'topN',    value: topN, disabled:true},
                {
                    xtype:'checkbox',
                    id: 'start_now',
                    name: 'start_now',
                    //align:'left',
                    fieldLabel:'是否立即执行',
                    checked: false
                }   
            ],
            buttons: [{
                text: '确定',
                handler: self.virtualRoomDeleteTasksEnd,
                formBind : true
            },{
                text: '取消',
                handler: function(){Ext.getCmp("virtual_room_delete_tasks_win_" + self.plat).close();}
            }]
        });
        
        var win = new Ext.Window({
            width:400,height:190,minWidth:200,minHeight:100,
            autoScroll:'auto',
            title : "虚拟机房删除任务",
            id : "virtual_room_delete_tasks_win_" + self.plat,
            //renderTo: "ext_room",
            collapsible: true,
            modal:false,    //True 表示为当window显示时对其后面的一切内容进行遮罩，false表示为限制对其它UI元素的语法（默认为 false
            //所谓布局就是指容器组件中子元素的分布，排列组合方式
            layout: 'form',//layout布局方式为form
            maximizable:true,
            minimizable:false,
            items: virtual_room_delete_tasks_form
        }).show();
        
        
    };
    
    this.virtualRoomDeleteTasksEnd = function() {
        Ext.getCmp(self.plat_+'virtual_room_delete_tasks_form').form.submit({
            waitMsg : '正在修改......',
            url : '/virtual_room_delete_tasks/' + self.plat + '/',
            method : 'post',
            timeout : 5000,//5秒超时, 
            params : '',
            success : function(form, action) {
                var result = Ext.util.JSON.decode(action.response.responseText);
                Ext.getCmp("virtual_room_delete_tasks_win_" + self.plat).close();
                Ext.MessageBox.alert('成功', result.data);
                self.room_store.reload();           //重新载入数据，即根据当前页面的条件，刷新用户页面
            },
            failure : function(form, action) {
                alert('失败:' + action.response.responseText);
                if(typeof(action.response) == 'undefined'){
                    Ext.MessageBox.alert('警告','添加失败，请重新添加！');
                } else {
                    var result = Ext.util.JSON.decode(action.response.responseText);
                    if(action.failureType == Ext.form.Action.SERVER_INVALID){
                        Ext.MessageBox.alert('警告', result.data);
                    }else{
                        Ext.MessageBox.alert('警告','表单填写异常，请重新填写！');
                    }
                }
            }
        });
    };
    
    
};

//Room = new roomJS();
