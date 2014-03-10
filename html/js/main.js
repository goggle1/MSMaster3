Ext.onReady(function() {
	setTimeout(function() {
		Ext.get('loading-mask').fadeOut({
			remove : true
		});
	}, 300);

	new Ext.Viewport({
		layout: 'border',
		items: [{
			region : 'north',
			xtype : 'panel',
			title : 'MediaServer管理系统II',
			border : false
		}, {
			region : 'west',
			id : 'west_panel',
			collapsible: true,
			//collapsed : true, //默认收缩
			title : '欢迎您',
			xtype : 'treepanel',
			tools : [{
				id : 'expand',
				qtip : '展开树形菜单',
				handler : expand
			}, {
				id : 'collapse',
				qtip : '收缩菜单',
				handler : collapse
			}, {
				id : '退出',
				qtip : '退出系统',
				handler : logout
			}],
			width : 200,
			minSize: 175,
			maxSize: 400,
			ctCls : 'x-panel',
			autoScroll : true,
			split : true,
			rootVisible : false,
			loader : new Ext.tree.TreeLoader({
				dataUrl : '/tree/'
			}),
			root : new Ext.tree.AsyncTreeNode({title:'欢迎您', expanded:true})
		}, {
			region: 'center',
			id : 'main_panel',		//右侧主面板ID
			autoShow : true,
			xtype : 'tabpanel',
			animScroll : true,
			autoScroll : false,	//不出现滚动条
			enableTabScroll : true,
			border : false,
			activeTab : 0,
			items: [{
				title : '欢迎',
				align : 'center',
				html: '<table height="100%" width="100%"><tr align="center"><td><p style="font-size:36px;">欢迎登录MediaServer管理系统II<br/>0.0.1</p></td></tr></table>'
			}],
			plugins:new Ext.ux.TabCloseMenu()
		}, {
			region: 'south',
			xtype : 'panel',
			title: 'MediaServer管理系统II'
			+'<select style="margin-left:30px;" onchange="changeExtJsStyleCss(this)">'
			+'<option value="">请选择皮肤</option>'
			+'<option value="xtheme-blue.css">Default</option>'
			+'<option value="xtheme-olive.css">ExtJsx Olive</option>'
			+'<option value="xtheme-red5.css">ExtJsx Red</option>'
			+'<option value="xtheme-orange.css">ExtJsx Orange</option>'
			+'<option value="yourtheme.css">ExtJs YourTheme</option>'
			+'<option value="xtheme-access.css">ExtJs Access</option>'
			+'<option value="xtheme-gray.css">ExtJs Gray</option>'
			+'</select>'
			+'<button onclick="clearAllLocalStore();">清除本地缓存</button>',
			border: false
		}]
	});
	
	function expand(){
		Ext.getCmp('west_panel').getRootNode().expandChildNodes(true);
	    };
    
	function collapse(){
		Ext.getCmp('west_panel').getRootNode().collapseChildNodes(true);
	};
	    
	//嵌套异步请求，得到该用户的全部权限
	/*
	Base.request(
			'ext_user',
			'/authority/index.php?c=user&a=view_user_module_auth',
			'',
			function(result){
				MACROSS_GLOBAL_MODULE_AUTHS = result.data;
			},
			function(result){
				//失败不处理
			}
	);
	*/
		
	//更新用户的登录信息，并更新global.js里的MACROSS_LOGIN_USER_NAME
	/*
	Base.request(
		'main_panel',
		'/login/index.php?c=login&a=get_username',		
		'',
		function(result){
			Ext.getCmp('west_panel').setTitle("欢迎您：" + result.data);
			MSMASTER_LOGIN_USER_NAME = result.data;				
		},
		function(result){
			//失败不处理
		}
	);
	*/
	
	Ext.Ajax.request({     
       url:'/get_username/',  
       params:
       {  
       	
       },  
       success: function(resp,opts) 
       {   
			var respText = Ext.util.JSON.decode(resp.responseText);  
			Ext.getCmp('west_panel').setTitle("欢迎您：" + respText.data);
			//Ext.Msg.alert('错误', respText.name+"====="+respText.id);   
		},   
		failure: function(resp,opts) {   
		    //失败不处理
		}     
         
    });
		
		
	//获取系统配置，并更新global.js里的MACROSS_GLOBAL_CONFIG
	/*
	Base.request(
		'main_panel',
		'/system/index.php?c=config&a=view_system_config',
		'',
		function(result){
			var data = result.data;
				for(var i=0;i<data.length;i++){
					MACROSS_GLOBAL_CONFIG[data[i].type] = data[i].value;
				}
		},
		function(result){
			//失败不处理
		}
	);
	*/
		
});

//清楚本地缓存
function clearAllLocalStore() {
	Ext.state.Manager.getProvider( ).clearAllStore();
};

function logout() {
	Ext.MessageBox.confirm("请确认","确定要退出嘛？", function(button) {
		if(button == 'yes'){
			window.location.href = '/accounts/logout/';
		}
	});
};

function show_main() {
	Ext.getCmp("main_panel").setActiveTab(0);
}

function expand() {
	Ext.getCmp('west_panel').getRootNode().expandChildNodes(true);
};

function collapse() {
	Ext.getCmp('west_panel').getRootNode().collapseChildNodes(true);
};

ScriptLoader = function() {
	this.timeout = 30;
	this.scripts = [];
	this.disableCaching = false;
	this.loadMask = null;
};
ScriptLoader.prototype = {
	showMask: function() {
		if (!this.loadMask) {
			this.loadMask = new Ext.LoadMask(Ext.getBody());
			this.loadMask.show();
		}
	},

	hideMask: function() {
		if (this.loadMask) {
			this.loadMask.hide();
			this.loadMask = null;
		}
	},

	processSuccess: function(response) {
		this.scripts[response.argument.url] = true;		
		window.execScript ? window.execScript(response.responseText) : window.eval(response.responseText);		
		if (response.argument.options.scripts.length == 0) {
			this.hideMask();
		}
		if (typeof response.argument.callback == 'function') {
			response.argument.callback.call(response.argument.scope);
		}
	},

	processFailure: function(response) {
		this.hideMask();
		Ext.MessageBox.show({title: 'Application Error', msg: 'Script library could not be loaded.', closable: true, icon: Ext.MessageBox.ERROR, minWidth: 200});
		setTimeout(function() { Ext.MessageBox.hide(); }, 3000);
	},

	load: function(url, callback) {
		var cfg, callerScope;
		if (typeof url == 'object') { // must be config object
			cfg = url;
			url = cfg.url;
			callback = callback || cfg.callback;
			callerScope = cfg.scope;
			if (typeof cfg.timeout != 'undefined') {
				this.timeout = cfg.timeout;
			}
			if (typeof cfg.disableCaching != 'undefined') {
				this.disableCaching = cfg.disableCaching;
			}
		}
	
		if (this.scripts[url]) {
			if (typeof callback == 'function') {
				callback.call(callerScope || window);
			}
			return null;
		}
	
		this.showMask();
	
		Ext.Ajax.request({
			url: url,
			success: this.processSuccess,
			failure: this.processFailure,
			scope: this,
			timeout: (this.timeout*1000),
			disableCaching: this.disableCaching,
			argument: {
				'url': url,
				'scope': callerScope || window,
				'callback': callback,
				'options': cfg
			}
		});
	}
};
	
ScriptLoaderMgr = function() {
	this.loader = new ScriptLoader();
	
	this.load = function(o) {
		if (!Ext.isArray(o.scripts)) {
			o.scripts = [o.scripts];
		}
		
		o.url = o.scripts.shift();
		
		if (o.scripts.length == 0) {
			this.loader.load(o);
		} else {
			o.scope = this;
			this.loader.load(o, function() {
				this.load(o);
			});
		}
	};
};
ScriptMgr = new ScriptLoaderMgr();

/*	ScriptMgr.load({
	scripts: ['/static/js/task.js'],
	callback: function() {
	}
});*/

//需要对是否为首页和退出模块。两个模块需要单独处理
function index_main(action_method, title_name, param) {
	if (action_method ==  'main_page') {
		show_main();
		return true;
	}
	if (action_method == 'logout'){
		logout();
		return true;
	}
	
	ext_action_method = 'ext_'+action_method;
	tab_id = ext_action_method + '_' + param;
	if (Ext.get(tab_id)) {
		Ext.getCmp('main_panel').setActiveTab(Ext.getCmp(tab_id));
		return true;
	}

	//从数据库获取配置的值
	/*var config_type = 'ajax_common_tabpanel_num';
	var config_value = (typeof MACROSS_GLOBAL_CONFIG[config_type])=='undefined' ? MACROSS_TABPANEL_MAX_NUM : MACROSS_GLOBAL_CONFIG[config_type];
	if(Ext.getCmp('main_panel').items.length > config_value){
		Ext.Msg.alert('警告',"最多只能同时打开"+config_value+"个应用界面");
		return true;
	}

	var main_panel = Ext.getCmp("main_panel");
	main_panel.add({
	    title : title_name,
			id : ext_action_method,
	    iconCls : 'tabs',
	    closable : true,
	}).show();
	*/
	ScriptMgr.load({
		scripts: ['/static/js/'+action_method+'.js'],
		callback: function() {
			//参数分别为tab_id,tab_title
			strLen = action_method.length; 
			tmpChar = action_method.substring(0,1).toUpperCase();
			postString = action_method.substring(1,strLen);
			my_object = tmpChar + postString + '_' + param;
			var _new = my_object + '= new ' + action_method + 'JS()';
			eval(_new);
			var _method = (my_object + "." + ext_action_method);			
			eval(_method)(tab_id, title_name, param);
		}
	});
	//调用对应的方法，进行页面的初始化，JS的名称需要固定
	//1、先检查对应的JS是否引入，如果没有引入，引入对应的JS。如果页面里已存在则不操作
	//2、调用对应的方法，展现页面，并初始化页面里的数据
	/*
	var url = '/js/'+action_method+'.js';
	var oldScript =document.getElementById(url);
	if(oldScript){
		document.getElementsByTagName("head")[0].removeChild(oldScript);
	}
	var script =document.createElement("script");
	script.setAttribute("type", "text/javascript");
	script.setAttribute("src",url);
	script.setAttribute("id", url);
	document.getElementsByTagName("head")[0].appendChild(script);
	*/
}

/*//嵌套异步请求，得到该用户的全部权限
Base.request(
	'ext_user',
	'/authority/index.php?c=user&a=view_user_module_auth',
	'',
	function(result){
		MACROSS_GLOBAL_MODULE_AUTHS = result.data;
	},
	function(result){
		//失败不处理
	}
);

//更新用户的登录信息，并更新global.js里的MACROSS_LOGIN_USER_NAME
Base.request(
	'main_panel',
	'/login/index.php?c=login&a=get_username',
	'',
	function(result){
		Ext.getCmp('west_panel').setTitle("欢迎您：" + result.data);
		MACROSS_LOGIN_USER_NAME = result.data;				
	},
	function(result){
		//失败不处理
	}
);


//获取系统配置，并更新global.js里的MACROSS_GLOBAL_CONFIG
Base.request(
	'main_panel',
	'/system/index.php?c=config&a=view_system_config',
	'',
	function(result){
		var data = result.data;
		for (var i=0;i<data.length;i++) {
			MACROSS_GLOBAL_CONFIG[data[i].type] = data[i].value;
		}
	},
	function(result){
		//失败不处理
	}
);*/
