//operation.js

var OPERATION_PAGE_SIZE = 20;

var operationJS = function(){
    var self = this;
    var operation_grid = new Object();      //定义全局grid，方便其他方法中的调用
    var operation_store = new Object();     //定义全局store，方便其他方法中的调用
    var plat = '';
    var plat_ = '';
            
    this.ext_operation = function(tab_id, tab_title, param){
        var main_panel = Ext.getCmp("main_panel");
        self.plat = param;
        self.plat_ = self.plat + '_';
                    
        self.operation_store = new Ext.data.JsonStore({
            url: '/get_operation_list/' + self.plat + '/',          
            root: 'data',
            totalProperty: 'total_count',
            remoteSort: true,
            pruneModifiedRecords: true,         //必须为true，这样重新reload数据时，会将脏数据清除
            fields : [
                {name: 'id', type: 'int'},
                'type',
                'name',
                'user',
                'dispatch_time',
                'status',
                'begin_time',
                'end_time',             
                'memo'
            ],
            /*
            sorters: [{
                //排序字段。
                property: 'id',
                //排序类型，默认为 ASC
                direction: 'DESC'
            }]
            */
            sortInfo: {field: "id", direction: "desc"}
        });
                    
        var sel_mode = new Ext.grid.CheckboxSelectionModel();
        var operation_mode = new Ext.grid.ColumnModel([
            new Ext.grid.RowNumberer({ header: "序号", width: 40, align: 'center' }),
            sel_mode,
            {header : 'id', id : 'id', dataIndex : 'id', sortable : true},
            {header : 'type', id : 'type', dataIndex : 'type', sortable : true},
            {header : 'name', id : 'name', dataIndex : 'name', sortable : true},
            {header : 'user', id : 'user', dataIndex : 'user', sortable : true},
            {header : 'dispatch_time', id : 'dispatch_time', dataIndex : 'dispatch_time', sortable : true},
            {header : 'status', id : 'status', dataIndex : 'status', sortable : true, renderer: operation_status},
            {header : 'begin_time', id : 'begin_time', dataIndex : 'begin_time', sortable : true},
            {header : 'end_time', id : 'end_time', dataIndex : 'end_time', sortable : true},
            {header : 'memo', id : 'memo', dataIndex : 'memo', sortable : true, width: 320}
        ]);
        
        
        var operation_page = new Ext.PagingToolbar({
                plugins: [new Ext.ui.plugins.SliderPageSize(), new Ext.ui.plugins.ComboPageSize({ addToItem: false, prefixText: '每页', postfixText: '条'}),new Ext.ux.ProgressBarPager()],
                //plugins: [new Ext.ui.plugins.SliderPageSize()],
                pageSize: OPERATION_PAGE_SIZE,      //每页要展现的记录数，默认从定义的全局变量获取
                store: self.operation_store,
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
        
        self.operation_grid = new Ext.grid.EditorGridPanel({
            id:             tab_id,
            title:          tab_title,
            iconCls:        'tabs',
            clicksToEdit:   2,
            autoScroll:     true,       //内容溢出时出现滚动条
            closable:       true,
            columnLines:    true,       //True表示为在列分隔处显示分隔符
            collapsible:    false,      //面板是否可收缩的
            stripeRows:     true,       //隔行变色
            store:          self.operation_store,
            colModel:       operation_mode,
            selModel:       sel_mode,
            loadMask:       { msg: '正在加载数据，请稍侯……' },
            //stateId: tab_id+'_grid'
            viewConfig : {
                forceFit:true, sortAscText:'升序',sortDescText:'降序',columnsText:'可选列'
            },
            tbar: [{
                //id: 'refresh_operation_list',
                text: '刷新操作列表',             
                iconCls: 'refresh',
                handler: self.refresh_operation_list
            },'-',{
            	//id: 'delete_wrong_operation',
                text: '删除错误操作',
                iconCls: 'del',
                handler: self.delete_wrong_operation
            },'-',{
                //id: 'do_selected_operations',
                text: '执行选中操作',             
                iconCls: 'confirm',
                handler: self.do_selected_operations
            },'-',{
                //id: 'do_all_operations',
                text: '执行全部操作',             
                iconCls: 'check',
                handler: self.do_all_operations
            },'-',{
                //id: 'show_operation_detail',
                text: '操作详细信息',             
                iconCls: 'detail',
                handler: self.show_operation_detail
            }],
            listeners:{'render':createTbar},
            bbar: operation_page
        });
        
        self.operation_store.load({params:{start:0,limit:OPERATION_PAGE_SIZE}});
        
        main_panel.add(self.operation_grid);
        main_panel.setActiveTab(self.operation_grid);           
    
        
        function operation_status(value,metadata,record) {
            switch(value) {
                case "0": 
                    metadata.css = 'bgyellow';
                    return '0:dispatched'; 
                    break;
                case "1": 
                    metadata.css = 'bggreen';
                    return '1:doing'; 
                    break;
                case "2": 
                    //metadata.css = 'bggreen';
                    return '2:done'; 
                    break;
                default:
                    return '<span class="black">' + value  + '</span>';
            }
        }
        
        //生成顶部工具条
        function createTbar(){
            var listener = {specialkey:function(field, e){if(e.getKey()==Ext.EventObject.ENTER){query_operation();}}};
            var oneTbar = new Ext.Toolbar({
                items:['type: ',{
                        xtype:'textfield',
                        id: self.plat_+'type',
                        name:'type',
                        width:110
                    },"-",
                    'name: ',{
                        xtype:'textfield',
                        id: self.plat_+'name',
                        name:'name',
                        width:110
                    },"-",
                    'user: ',{
                        xtype:'textfield',
                        id: self.plat_+'user',
                        name:'user',
                        width:110
                    },"-",
                    'status: ',{
                        xtype:'textfield',
                        id: self.plat_+'status',
                        name:'status',
                        width:110
                    },"-",{                    	
                        text:'搜索',
                        iconCls: 'search',
                        handler: query_operation
                    },"-",{                    	
                        text:'重置',
                        iconCls: 'reset',
                        handler: reset_query_operation
                    }]
            });
            oneTbar.render(self.operation_grid.tbar);
        }
        
        
        function query_operation(){         
            self.operation_store.on('beforeload', function(obj) {
                Ext.apply(obj.baseParams,{
                        'start':0,
                        'limit':operation_page.pageSize,
                        'type':Ext.getCmp(self.plat_+'type').getValue(),
                        'name':Ext.getCmp(self.plat_+'name').getValue(),
                        'user':Ext.getCmp(self.plat_+'user').getValue(),
                        'status':Ext.getCmp(self.plat_+'status').getValue()
                        });
            });         
            self.operation_store.load();
        };
        
        function reset_query_operation(){
            //将查询条件置为空，不可以将查询条件的充值放到beforeload里         
            Ext.getCmp(self.plat_+'type').setValue("");
            Ext.getCmp(self.plat_+'name').setValue("");
            Ext.getCmp(self.plat_+'user').setValue("");
            Ext.getCmp(self.plat_+'status').setValue("");
            query_operation();
        };

        //右键触发事件
        function rightClickRowMenu(grid, rowIndex, cellIndex, e) {
            e.preventDefault();//禁用浏览器默认的右键，针对某一行禁用
            if (rowIndex < 0)
                return true;
            var record = grid.getStore().getAt(rowIndex);//获取当前行的纪录
            var operation_id = record.get('id');

            var t_sm = grid.getSelectionModel();

            //此处为多选行，如果没有选中任意一行时，需要对右键当前行进行选中设置
            //如果右键当前行不在选中的行中，则移除所选的行，选择当前行
            var operation_id_arr = []
            if (t_sm.getSelected()) {
                var recs = t_sm.getSelections();
                for (var i = 0; i < recs.length; i++) {
                    operation_id_arr.push(recs[i].get('id'));
                }
            }
            var param_id = '';
            if (operation_id_arr.indexOf(operation_id) < 0) {
                //当前行没有选中
                t_sm.clearSelections();
                t_sm.selectRow(rowIndex);
                grid.getView().focusRow(rowIndex);
                param_id = operation_id;
            } else {
                param_id = operation_id_arr.join(',');
            }

            //如果存在右键菜单，清楚菜单里的所有项
            if (Ext.get('operation_right_menu')) {
                Ext.getCmp('operation_right_menu').removeAll();
            }
            //动态生成右键
            var menu_items = [];
            var auth_detail = {text:'操作详细状态',iconCls:'detail',handler:self.show_operation_detail};
            //var auth_modify = {text:'修改任务信息',iconCls:'modify',handler:self.modifyTaskInfo};
            var auth_refresh = {text:'刷新操作列表',iconCls:'refresh',handler:self.refresh_operation_list};
            menu_items.push(auth_detail);
            //menu_items.push(auth_modify);
            menu_items.push(auth_refresh);
            var rightMenu = new Ext.menu.Menu({
                            id:'operation_right_menu',
                            items: menu_items
                        });
            //定位。显示右键菜单
            if(e.getXY()[0]==0||e.getXY()[1]==0)
                rightMenu.show(grid.getView().getCell(rowIndex,cellIndex));
            else
                rightMenu.showAt(e.getXY());
        }
        
        //给控键添加右键菜单触发事件
        self.operation_grid.addListener('cellcontextmenu', rightClickRowMenu);
        self.operation_grid.addListener('contextmenu', function(e){e.preventDefault(); })//禁用浏览器默认的右键，针对grid禁用
        
        
    };
            
    this.refresh_operation_list = function() 
    {       
        self.operation_store.reload();
    }
    
    this.delete_wrong_operation = function() 
    {
        var grid = self.operation_grid;
        var t_sm = grid.getSelectionModel();      
        if(!t_sm.getSelected()){
            Ext.MessageBox.alert('提示','未选中记录');
            return false;
        } 
        
        var operation_ids = []
        if (t_sm.getSelected()) 
        {
            var recs = t_sm.getSelections();
            for (var i = 0; i < recs.length; i++) 
            {
                operation_ids.push(recs[i].get('id'));
            }
        }
        else
        {
            return;
        }
        
        //避免win的重复生成
        if(Ext.get("delete_wrong_operation_win_" + self.plat)){
            Ext.getCmp("delete_wrong_operation_win_" + self.plat).show();
            return true;
        }
                
        var delete_wrong_operation_form = new Ext.FormPanel({
            id: self.plat_+'delete_wrong_operation_form',
            autoWidth: true,//自动调整宽度
            url:'',
            frame:true,
            monitorValid : true,
            bodyStyle:'padding:5px 5px 0',
            labelWidth:150,
            defaults:{xtype:'textfield',width:200},
            items: [                                
            	{fieldLabel:'ids',      name:'ids',     value: operation_ids,     hidden:true},   
                {fieldLabel:'ids',      name:'ids',     value: operation_ids,     disabled:true}
            ],
            buttons: [{
                text: '确定',
                handler: self.deleteWrongOperationEnd,
                formBind : true
            },{
                text: '取消',
                handler: function(){Ext.getCmp("delete_wrong_operation_win_" + self.plat).close();}
            }]
        });
        
        var win = new Ext.Window({
            width:400,height:110,minWidth:200,minHeight:100,
            autoScroll:'auto',
            title : "删除错误操作",
            id : "delete_wrong_operation_win_" + self.plat,
            //renderTo: "ext_room",
            collapsible: true,
            modal:false,    //True 表示为当window显示时对其后面的一切内容进行遮罩，false表示为限制对其它UI元素的语法（默认为 false
            //所谓布局就是指容器组件中子元素的分布，排列组合方式
            layout: 'form',//layout布局方式为form
            maximizable:true,
            minimizable:false,
            items: delete_wrong_operation_form
        }).show();
    }
    
    this.deleteWrongOperationEnd = function() {
        Ext.getCmp(self.plat_+"delete_wrong_operation_form").form.submit({
            waitMsg : '正在修改......',
            url : '/delete_wrong_operation/' + self.plat + '/',
            method : 'post',
            timeout : 5000,//5秒超时, 
            params : '',
            success : function(form, action) {
                var result = Ext.util.JSON.decode(action.response.responseText);
                Ext.getCmp("delete_wrong_operation_win_" + self.plat).close();
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
    
    
    this.do_selected_operations = function() {
        var grid = self.operation_grid;
        var t_sm = grid.getSelectionModel();

        //此处为多选行，如果没有选中任意一行时，需要对右键当前行进行选中设置
        //如果右键当前行不在选中的行中，则移除所选的行，选择当前行
        var operation_ids = []
        if (t_sm.getSelected()) 
        {
            var recs = t_sm.getSelections();
            for (var i = 0; i < recs.length; i++) 
            {
                operation_ids.push(recs[i].get('id'));
            }
        }
        else
        {
            return;
        }
        //console.log(ms_ips);

        Ext.Ajax.request({
            url: '/do_selected_operations/' + self.plat + '/',              
            params: 'ids=' + operation_ids,
            success: function(response) {
                Ext.MessageBox.alert('成功', response.responseText);                      
                
            },
            failure: function(response){
                Ext.MessageBox.alert('失败', response.responseText);
            }
            //timeout: (this.timeout*1000);
        });

    };
    
    this.do_all_operations = function() {
        
        Ext.Ajax.request({
            url: '/do_all_operations/' + self.plat + '/',               
            params: '',
            success: function(response) {
                Ext.MessageBox.alert('成功', response.responseText);                      
                
            },
            failure: function(response){
                Ext.MessageBox.alert('失败', response.responseText);
            }
            //timeout: (this.timeout*1000);
        });

    };

    this.show_operation_detail = function() {
        var grid = self.operation_grid;
        var t_sm = grid.getSelectionModel();

        //此处为多选行，如果没有选中任意一行时，需要对右键当前行进行选中设置
        //如果右键当前行不在选中的行中，则移除所选的行，选择当前行
        var operation_ids = []
        if (t_sm.getSelected()) 
        {
            var recs = t_sm.getSelections();
            for (var i = 0; i < recs.length; i++) 
            {
                operation_ids.push(recs[i].get('id'));
            }
        }
        else
        {
            return;
        }
        //console.log(ms_ips);

        Ext.Ajax.request({
            url: '/show_operation_info/' + self.plat + '/',             
            params: 'ids=' + operation_ids,
            success: function(response) {
                //Ext.MessageBox.alert('成功', Ext.encode(response)); 
                //console.log(response.responseText);               
                var ms_panel = new Ext.Panel({
                  //renderTo: 'panelDiv',
                  title: '操作状态: ' + operation_ids,
                  iconCls : 'tabs',
                  closable : true,
                  autoScroll: true,
                  items:[{
                    html: response.responseText
                  }]
                });
                var main_panel = Ext.getCmp("main_panel");
                main_panel.add(ms_panel);
                main_panel.setActiveTab(ms_panel);      
                
            },
            failure: function(response){
                Ext.MessageBox.alert('失败', Ext.encode(response));
            }
            //timeout: (this.timeout*1000);
        });

    };
    
};

//Operation = new operationJS();
