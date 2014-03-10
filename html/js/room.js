//room.js

var ROOM_PAGE_SIZE = 20;
var ROOM_LONG_TIMEOUT = 20;


var roomJS = function(){	
		
	var self = this;
	var room_grid = new Object();		//定义全局grid，方便其他方法中的调用
	var room_store = new Object();		//定义全局store，方便其他方法中的调用
	var plat = '';
	
	
	
	this.ext_room = function(tab_id, tab_title, param){
		var main_panel = Ext.getCmp("main_panel");
		self.plat = param;
		
		self.room_store = new Ext.data.JsonStore({
			url : '/get_room_list/' + self.plat + '/',
			root : 'data',
			totalProperty : 'total_count',
			remoteSort : true,
			pruneModifiedRecords: true, 
			fields : [
				{name: 'room_id', type: 'int'},
				'room_name',
				'is_valid',
				'ms_number',
				'task_number',
				'total_disk_space',
				'free_disk_space',
				'suggest_task_number',
				'num_dispatching',
				'num_deleting',
				//'operation_time'
				'check_time'
			]
		});

	
		var sel_mode = new Ext.grid.CheckboxSelectionModel();
		var room_mode = new Ext.grid.ColumnModel([
			new Ext.grid.RowNumberer(),
			sel_mode,
			{header : 'room_id', id : 'room_id', dataIndex : 'room_id', sortable : true},
			{header : 'room_name', id : 'room_name', dataIndex : 'room_name', sortable : true},
			{header : 'is_valid', id : 'is_valid', dataIndex : 'is_valid', sortable : true},
			{header : 'ms_number', id : 'ms_number', dataIndex : 'ms_number', sortable : true},
			{header : 'task_number', id : 'task_number', dataIndex : 'task_number', sortable : true},
			{header : 'total_disk_space', id : 'total_disk_space', dataIndex : 'total_disk_space', sortable : true, renderer : disk_size},
			{header : 'free_disk_space', id : 'free_disk_space', dataIndex : 'free_disk_space', sortable : true, renderer : disk_status},
			{header : 'suggest_task_number', id : 'suggest_task_number', dataIndex : 'suggest_task_number', sortable : true},
			{header : 'num_dispatching', id : 'num_dispatching', dataIndex : 'num_dispatching', sortable : true},
			{header : 'num_deleting', id : 'num_deleting', dataIndex : 'num_deleting', sortable : true},				
			{header : 'check_time', id : 'check_time', dataIndex : 'check_time', sortable : true, xtype: 'datecolumn', format : 'Y-m-d H:i:s', width: 200}	
		]);
	
		var room_page = new Ext.PagingToolbar({
				plugins: [new Ext.ui.plugins.SliderPageSize(), new Ext.ui.plugins.ComboPageSize({ addToItem: false, prefixText: '每页', postfixText: '条'}),new Ext.ux.ProgressBarPager()],
				//plugins: [new Ext.ui.plugins.SliderPageSize()],
	            pageSize: ROOM_PAGE_SIZE,		//每页要展现的记录数，默认从定义的全局变量获取
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
			id: 			tab_id,
			title: 			tab_title,
			iconCls: 		'tabs',
			clicksToEdit: 	2,
			autoScroll: 	true,		//内容溢出时出现滚动条
			closable: 		true,
			columnLines: 	true,		//True表示为在列分隔处显示分隔符
			collapsible: 	false,		//面板是否可收缩的
			stripeRows: 	true,		//隔行变色
			store: 			self.room_store,
			colModel: 		room_mode,
			selModel: 		sel_mode,
			loadMask: 		{ msg: '正在加载数据，请稍侯……' },
			//stateId: tab_id+'_grid'
			viewConfig : {
				forceFit:true, sortAscText:'升序',sortDescText:'降序',columnsText:'可选列'
			},
			tbar: [{
				text: '同步数据库',
				iconCls: 'sync',
				handler: self.sync_room_db
			},'-',{				
				text: '同步机房状态',				
				iconCls: 'sync',
				handler: self.sync_room_status
			},'-',{				
				text: '刷新机房列表',				
				iconCls: 'refresh',
				handler: self.refresh_room_list
			},'-',{				
				text: '机房详细状态',				
				iconCls: 'detail',
				handler: self.show_room_detail
			},'-',{				
				text: '分发热门任务',				
				iconCls: 'modify',
				handler: self.add_hot_tasks
			},'-',{				
				text: '删除冷门任务',				
				iconCls: 'modify',
				handler: self.delete_cold_tasks
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
				items:['room_id: ',{
						xtype:'textfield',
						id:'room_id',
						name:'room_id',
						width:110
					},"-",'room_name: ',{
						xtype:'textfield',
						id:'room_name',
						name:'room_name',
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
						'room_id':Ext.getCmp('room_id').getValue(),
						'room_name':Ext.getCmp('room_name').getValue()
						});
			});			
			self.room_store.load();
		};
		
		function reset_query_room(){
			//将查询条件置为空，不可以将查询条件的充值放到beforeload里
			Ext.getCmp('room_id').setValue("");
			Ext.getCmp('room_name').setValue("");
			query_room();
		};
		
		//右键触发事件
		function rightClickRowMenu(grid,rowIndex,cellIndex,e){
			e.preventDefault();  		//禁用浏览器默认的右键 ，针对某一行禁用
			if(rowIndex<0)return true;
			var record = grid.getStore().getAt(rowIndex);   //获取当前行的记录
	  		var cur_room_id = record.get('room_id');			//取得当前右键所在行的ROOM_ID
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
				t_sm.selectRow(rowIndex);			//选中某一行
				grid.getView().focusRow(rowIndex);			//获取焦点
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
		self.room_grid.addListener('contextmenu', function(e){e.preventDefault(); }); 		//禁用浏览器默认的右键 ,针对grid禁用
	
	};
	
	/*
	this.sync_room_db = function() 
	{
		Ext.Ajax.request({
			url: '/sync_room_db/' + self.plat + '/',			
			params: '',
			success: function(response) {
				Ext.MessageBox.alert('成功', response.responseText);	
			},
			failure: function(response){
				Ext.MessageBox.alert('失败', Ext.encode(response));
			}			
		});
	}
	*/
	this.sync_room_db = function() 
	{
		//避免win的重复生成
		if(Ext.get("sync_room_db_win_" + self.plat)){
			Ext.getCmp("sync_room_db_win_" + self.plat).show();
			return true;
		}
		
		var sync_room_db_form = new Ext.FormPanel({
			id: 'sync_room_db_form',
			autoWidth: true,//自动调整宽度
			url:'',
			frame:true,
			monitorValid : true,
			bodyStyle:'padding:5px 5px 0',
			labelWidth:150,
			defaults:{xtype:'textfield',width:200},
			items: [									
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
				handler: self.syncRoomDbEnd,
				formBind : true
			},{
				text: '取消',
				handler: function(){Ext.getCmp("sync_room_db_win_" + self.plat).close();}
			}]
		});
		
		var win = new Ext.Window({
			width:400,height:110,minWidth:200,minHeight:100,
			autoScroll:'auto',
			title : "同步机房数据库",
			id : "sync_room_db_win_" + self.plat,
			//renderTo: "ext_room",
			collapsible: true,
			modal:false,	//True 表示为当window显示时对其后面的一切内容进行遮罩，false表示为限制对其它UI元素的语法（默认为 false
			//所谓布局就是指容器组件中子元素的分布，排列组合方式
			layout: 'form',//layout布局方式为form
			maximizable:true,
			minimizable:false,
			items: sync_room_db_form
		}).show();
	}
	
	this.syncRoomDbEnd = function() {
		Ext.getCmp("sync_room_db_form").form.submit({
			waitMsg : '正在修改......',
			url : '/sync_room_db/' + self.plat + '/',
			method : 'post',
			timeout : 5000,//5秒超时, 
			params : '',
			success : function(form, action) {
				var result = Ext.util.JSON.decode(action.response.responseText);
				Ext.getCmp("sync_room_db_win_" + self.plat).close();
				Ext.MessageBox.alert('成功', result.data);
				//self.task_store.reload();			//重新载入数据，即根据当前页面的条件，刷新用户页面
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
	
	/*
	this.sync_room_status = function() {
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
				room_ids.push(recs[i].get('room_id'));
			}
		}
		else
		{
			return true;
		}
		//console.log(room_ids);

		Ext.Ajax.request({
			url: '/sync_room_status/' + self.plat + '/',				
			params: 'ids=' + room_ids,
			success: function(response) {
				Ext.MessageBox.alert('成功', response.responseText);	
			},
			failure: function(response){
				Ext.MessageBox.alert('失败', Ext.encode(response));
			}
			//timeout: (this.timeout*1000);
		});

	};
	*/
	
	/*
	this.sync_room_status = function() {		

		Ext.Ajax.request({
			url: '/sync_room_status/' + self.plat + '/',				
			params: '',
			success: function(response) {
				Ext.MessageBox.alert('成功', response.responseText);	
			},
			failure: function(response){
				Ext.MessageBox.alert('失败', Ext.encode(response));
			}
			//timeout: (this.timeout*1000);
		});

	};
	*/
	
	this.sync_room_status = function() 
	{
		//避免win的重复生成
		if(Ext.get("sync_room_status_win_" + self.plat)){
			Ext.getCmp("sync_room_status_win_" + self.plat).show();
			return true;
		}
		
		var sync_room_status_form = new Ext.FormPanel({
			id: 'sync_room_status_form',
			autoWidth: true,//自动调整宽度
			url:'',
			frame:true,
			monitorValid : true,
			bodyStyle:'padding:5px 5px 0',
			labelWidth:150,
			defaults:{xtype:'textfield',width:200},
			items: [									
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
				handler: self.syncRoomStatusEnd,
				formBind : true
			},{
				text: '取消',
				handler: function(){Ext.getCmp("sync_room_status_win_" + self.plat).close();}
			}]
		});
		
		var win = new Ext.Window({
			width:400,height:110,minWidth:200,minHeight:100,
			autoScroll:'auto',
			title : "同步机房状态",
			id : "sync_room_status_win_" + self.plat,
			//renderTo: "ext_room",
			collapsible: true,
			modal:false,	//True 表示为当window显示时对其后面的一切内容进行遮罩，false表示为限制对其它UI元素的语法（默认为 false
			//所谓布局就是指容器组件中子元素的分布，排列组合方式
			layout: 'form',//layout布局方式为form
			maximizable:true,
			minimizable:false,
			items: sync_room_status_form
		}).show();
	}
	
	this.syncRoomStatusEnd = function() {
		Ext.getCmp("sync_room_status_form").form.submit({
			waitMsg : '正在修改......',
			url : '/sync_room_status/' + self.plat + '/',
			method : 'post',
			timeout : 5000,//5秒超时, 
			params : '',
			success : function(form, action) {
				var result = Ext.util.JSON.decode(action.response.responseText);
				Ext.getCmp("sync_room_status_win_" + self.plat).close();
				Ext.MessageBox.alert('成功', result.data);
				//self.task_store.reload();			//重新载入数据，即根据当前页面的条件，刷新用户页面
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
	
	this.refresh_room_list = function() 
	{
		self.room_store.reload();
	};
	
	
	this.show_room_detail = function() {
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
				room_ids.push(recs[i].get('room_id'));
			}
		}
		else
		{
			return true;
		}
		//console.log(room_ids);

		Ext.Ajax.request({
			url: '/show_room_info/' + self.plat + '/',				
			params: 'ids=' + room_ids,
			success: function(response) {
				//Ext.MessageBox.alert('成功', Ext.encode(response));	
				//console.log(response.responseText);				
				var room_panel = new Ext.Panel({
				  //renderTo: 'panelDiv',
				  title: '机房状态: ' + room_ids,
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
	
	this.add_hot_tasks = function(){
		var grid = self.room_grid;
		var sm = grid.getSelectionModel();		
		if(!sm.getSelected()){
			Ext.MessageBox.alert('提示','未选中记录');
			return false;
		}		
		var record = sm.getSelections()[0];   //获取当前行的记录		
		var room_id = record.get('room_id');		
		var room_name = record.get('room_name');
		var is_valid = record.get('is_valid');
		var total_disk_space = record.get('total_disk_space');
		var free_disk_space = record.get('free_disk_space');
		var task_number = record.get('task_number');
		var suggest_task_number = record.get('suggest_task_number');		
		var num_dispatching = record.get('num_dispatching');
		var num_deleting = record.get('num_deleting');		
		var check_time = record.get('check_time');
		//避免win的重复生成
		if(Ext.get("add_hot_tasks_win_" + self.plat)){
			Ext.getCmp("add_hot_tasks_win_" + self.plat).show();
			return true;
		}
		
		var add_hot_tasks_form = new Ext.FormPanel({
			id: 'add_hot_tasks_form',
			autoWidth: true,//自动调整宽度
			url:'',
			frame:true,
			monitorValid : true,
			bodyStyle:'padding:5px 5px 0',
			labelWidth:150,
			defaults:{xtype:'textfield',width:200},
			items: [
				{fieldLabel:'room_id', 		name:'room_id', 	value: room_id, 	hidden:true},
				{fieldLabel:'room_id', 		name:'room_id', 	value: room_id, 	disabled:true},
				{fieldLabel:'room_name', 	name:'room_name', 	value: room_name, 	disabled:true},
				{fieldLabel:'total_disk_space', 	name:'total_disk_space', 	value: total_disk_space, 	disabled:true},
				{fieldLabel:'free_disk_space', 	name:'free_disk_space', 	value: free_disk_space, 	disabled:true},
				//{fieldLabel:'suggest_task_number', 	name:'suggest_task_number',	value: suggest_task_number, disabled:false},
				{fieldLabel:'suggest_task_number',	
					name: 'suggest_task_number', 
					value: suggest_task_number, 
					xtype: 'numberfield',
					minValue: 0,
					minText: '建议任务数不能小于0',
					allowBlank:false,
					blankText:'建议任务数不能为空'
				},
				{fieldLabel:'task_number', 	name:'task_number',	value: task_number, disabled:true},				
				{fieldLabel:'num_dispatching',	
					name: 'num_dispatching', 
					value: num_dispatching, 
					xtype: 'numberfield',
					minValue: 0,
					minText: '分发任务数不能小于0',
					allowBlank:false,
					blankText:'分发任务数不能为空'
				},
				{fieldLabel:'num_deleting', 	name:'num_deleting',	value: num_deleting, disabled:true},
				{fieldLabel:'check_time', 	name:'check_time', 	value: check_time, disabled:true},
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
				handler: self.addHotTasksEnd,
				formBind : true
			},{
				text: '取消',
				handler: function(){Ext.getCmp("add_hot_tasks_win_" + self.plat).close();}
			}]
		});
		
		var win = new Ext.Window({
			width:400,height:341,minWidth:200,minHeight:100,
			autoScroll:'auto',
			title : "分发热门任务",
			id : "add_hot_tasks_win_" + self.plat,
			//renderTo: "ext_room",
			collapsible: true,
			modal:false,	//True 表示为当window显示时对其后面的一切内容进行遮罩，false表示为限制对其它UI元素的语法（默认为 false
			//所谓布局就是指容器组件中子元素的分布，排列组合方式
			layout: 'form',//layout布局方式为form
			maximizable:true,
			minimizable:false,
			items: add_hot_tasks_form
		}).show();
		
		
	};
	
	this.addHotTasksEnd = function() {
		Ext.getCmp("add_hot_tasks_form").form.submit({
			waitMsg : '正在修改......',
			url : '/add_hot_tasks/' + self.plat + '/',
			method : 'post',
			timeout : 5000,//5秒超时, 
			params : '',
			success : function(form, action) {
				var result = Ext.util.JSON.decode(action.response.responseText);
				Ext.getCmp("add_hot_tasks_win_" + self.plat).close();
				Ext.MessageBox.alert('成功', result.data);
				self.room_store.reload();			//重新载入数据，即根据当前页面的条件，刷新用户页面
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
	
	this.delete_cold_tasks = function(){
		var grid = self.room_grid;
		var sm = grid.getSelectionModel();		
		if(!sm.getSelected()){
			Ext.MessageBox.alert('提示','未选中记录');
			return false;
		}		
		var record = sm.getSelections()[0];   //获取当前行的记录		
		var room_id = record.get('room_id');		
		var room_name = record.get('room_name');
		var is_valid = record.get('is_valid');
		var total_disk_space = record.get('total_disk_space');
		var free_disk_space = record.get('free_disk_space');
		var task_number = record.get('task_number');
		var suggest_task_number = record.get('suggest_task_number');		
		var num_dispatching = record.get('num_dispatching');
		var num_deleting = record.get('num_deleting');		
		var check_time = record.get('check_time');
		//避免win的重复生成
		if(Ext.get("delete_cold_tasks_win_" + self.plat)){
			Ext.getCmp("delete_cold_tasks_win_" + self.plat).show();
			return true;
		}
		
		var delete_cold_tasks_form = new Ext.FormPanel({
			id: 'delete_cold_tasks_form',
			autoWidth: true,//自动调整宽度
			url:'',
			frame:true,
			monitorValid : true,
			bodyStyle:'padding:5px 5px 0',
			labelWidth:150,
			defaults:{xtype:'textfield',width:200},
			items: [
				{fieldLabel:'room_id', 		name:'room_id', 	value: room_id, 	hidden:true},
				{fieldLabel:'room_id', 		name:'room_id', 	value: room_id, 	disabled:true},
				{fieldLabel:'room_name', 	name:'room_name', 	value: room_name, 	disabled:true},
				{fieldLabel:'total_disk_space', 	name:'total_disk_space', 	value: total_disk_space, 	disabled:true},
				{fieldLabel:'free_disk_space', 	name:'free_disk_space', 	value: free_disk_space, 	disabled:true},
				//{fieldLabel:'suggest_task_number', 	name:'suggest_task_number',	value: suggest_task_number, disabled:false},
				{fieldLabel:'suggest_task_number',	
					name: 'suggest_task_number', 
					value: suggest_task_number, 
					xtype: 'numberfield',
					minValue: 0,
					minText: '建议任务数不能小于0',
					allowBlank:false,
					blankText:'建议任务数不能为空'
				},
				{fieldLabel:'task_number', 	name:'task_number',	value: task_number, disabled:true},		
				{fieldLabel:'num_dispatching', 	name:'num_dispatching',	value: num_dispatching, disabled:true},		
				{fieldLabel:'num_deleting',	
					name: 'num_deleting', 
					value: num_deleting, 
					xtype: 'numberfield',
					minValue: 0,
					minText: '删除任务数不能小于0',
					allowBlank:false,
					blankText:'删除任务数不能为空'
				},				
				{fieldLabel:'check_time', 	name:'check_time', 	value: check_time, disabled:true},
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
				handler: self.deleteColdTasksEnd,
				formBind : true
			},{
				text: '取消',
				handler: function(){Ext.getCmp("delete_cold_tasks_win_" + self.plat).close();}
			}]
		});
		
		var win = new Ext.Window({
			width:400,height:342,minWidth:200,minHeight:100,
			autoScroll:'auto',
			title : "删除冷门任务",
			id : "delete_cold_tasks_win_" + self.plat,
			//renderTo: "ext_room",
			collapsible: true,
			modal:false,	//True 表示为当window显示时对其后面的一切内容进行遮罩，false表示为限制对其它UI元素的语法（默认为 false
			//所谓布局就是指容器组件中子元素的分布，排列组合方式
			layout: 'form',//layout布局方式为form
			maximizable:true,
			minimizable:false,
			items: delete_cold_tasks_form
		}).show();
		
		
	};
	
	this.deleteColdTasksEnd = function() {
		Ext.getCmp('delete_cold_tasks_form').form.submit({
			waitMsg : '正在修改......',
			url : '/delete_cold_tasks/' + self.plat + '/',
			method : 'post',
			timeout : 5000,//5秒超时, 
			params : '',
			success : function(form, action) {
				var result = Ext.util.JSON.decode(action.response.responseText);
				Ext.getCmp("delete_cold_tasks_win_" + self.plat).close();
				Ext.MessageBox.alert('成功', result.data);
				self.room_store.reload();			//重新载入数据，即根据当前页面的条件，刷新用户页面
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
