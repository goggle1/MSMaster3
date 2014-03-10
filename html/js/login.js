//登录js
Ext.onReady(function()
{
	var win=new LoginWindow();
	win.show();
	//页面加载特效
	setTimeout(function() {
				Ext.get('loading-mask').fadeOut( {
					remove : true
				});
			}, 300);

	 var map = new Ext.KeyMap("username", {
	     key: 13, // 或者是 Ext.EventObject.ENTER
	     fn: function(){Ext.getCmp("password").focus()}
	 });
	 var map = new Ext.KeyMap("password", {
	     key: 13, // 或者是 Ext.EventObject.ENTER
	     fn: win.login
	 });
}
);

LoginWindow = new Ext.extend(Ext.Window,{
	title: 'MediaServer管理系统——MSMaster 0.0.1',
	width: 300,height: 150,minWidth:300,minHeight:150,
    autoScroll:'auto',
	collapsible : true,		//表示登录框可收缩
	closable : false,
	buttonAlign : 'center',
	createFormPanel : function(){
		return new Ext.FormPanel({
			bodyStyle : 'padding-top:6px',
			id : 'login_form',
			defaultType : 'textfield',
			labelAlign : 'right',
			labelWidth : 55,
			labelPad : 0,
			frame : true,
			monitorValid : true,
			defaults : {
				allowBlank : false,
				width : 158
			},
			items : [{
					cls : 'user', 	//样式
					id : 'username',
					name : 'username',
					minLength : 5,
					fieldLabel : '帐号',
					allowBlank : false,
					//vtype:'alphanumemail',
					blankText : '用户名不能为空',
					minLengthText : '用户名不能少于5'
				}, {
					cls : 'key',	//样式
					id : 'password',
					name : 'password',
					minLength : 6,
					fieldLabel : '密码',
					allowBlank : false,
					blankText : '密码不能为空',
					minLengthText : '密码长度最少为6位',
					inputType : 'password'
				}],
			buttons : [{
					text : "登录",
					handler : this.login,
					formBind : true
				},{
					text : "重置",
					handler : this.reset
				}]
				
		});
	},
	login : function(){
			if(!Ext.getDom('username').value){
				Ext.MessageBox.alert('警告','用户名不能为空！');
				return false;
			}
			if(!Ext.getDom('password').value){
				Ext.MessageBox.alert('警告','密码不能为空！');
				return false;
			}
			Ext.getCmp('login_form').form.submit({
					waitMsg : '正在登录......',
					// url : '/login/index.php?c=login&a=login&so=end',
					url : '/accounts/login/',
					method : 'post',
					// 如果有表单以外的其它参数，可以加在这里。我这里暂时为空，也可以将下面这句省略   
				  	params : '',
				  	timeout : 5,//5秒超时, 
					success : function(form, action) {
						Ext.MessageBox.alert('成功','成功登录！');
						//window.location.href = '/index.php';
						window.location.href = '/';
					},
					failure : function(form, action) {
						Ext.getDom('password').value = "";
						if(typeof(action.response) == 'undefined'){
							Ext.MessageBox.alert('警告','登录失败，请重新登录！');
						}else{
							var result = Ext.util.JSON.decode(action.response.responseText);
							if(action.failureType == Ext.form.Action.SERVER_INVALID){
								Ext.MessageBox.alert('警告', result.data);
							}else{
								Ext.MessageBox.alert('警告','网络异常，请稍后重试！');
							}
						}
					}
				});
	},
	reset : function(){
		Ext.getCmp('login_form').form.reset();//重置
	},
	initComponent : function(){
        LoginWindow.superclass.initComponent.call(this);       
        this.fp = this.createFormPanel();
        this.add(this.fp);
	}
});