//通用js
//定义一些通用全局变量
var MACROSS_TIMEOUT = 50000;		//超时时长，表示50秒，有些操作如果很耗时，可以自行传入参数
var MACROSS_LONG_TIMEOUT = 1000000;	//超时时长，表示1000秒，有些操作如果很耗时
var MACROSS_TABPANEL_MAX_NUM = 10;		//打开的tabpanel的最多个数
var MACROSS_PAGE_SIZE = 20;			//全局变量，用来控制所有页面记录展现的个数，可以修改成cookie记录获取
var MACROSS_MAX_ROW = 10;			//行多选时，每次可选的记录数
var MACROSS_MS_MIN_FREE_DISK = 30;	//ms设备最小的磁盘空间，单位GB
var MACROSS_UPLOADER_IP = "127.0.0.1";		//Uploader ip
var MACROSS_UPLOADER_PORT = "9000";		//Uploader ports
var MACROSS_UPLOADER_TIMEOUT = 1000;					//Uploader timeout

var MACROSS_LOGIN_USER_NAME = "";				//登录时，需要设置当前的用户；用于后续与Uploader的交互

var MACROSS_GLOBAL_CONFIG = new Array();			//存储系统配置
var MACROSS_GLOBAL_MODULE_AUTHS = new Array(); //存储当前用户对所有模块拥有的操作权限

//使用简单的提示。想要最大化地定制一个工具提示，你可以考虑使用 Ext.Tip 或者 Ext.ToolTip。
//整个系统的提示默认都使用此tip，例如：tools 中的qtip(提示字符串)，也需要用此tip
Ext.QuickTips.init();
Ext.BLANK_IMAGE_URL = '/lib/extjs/resources/images/default/s.gif';

function $(_sId){return document.getElementById(_sId);}
// Add the additional 'advanced' VTypes，注册一个form表单的验证类型
Ext.apply(Ext.form.VTypes, {
	daterange : function(val, field) {
		var date = field.parseDate(val);
		if(!date){
		return false;
		}
		if (field.startDateField) {
			var start = Ext.getCmp(field.startDateField);
			if (!start.maxValue || (date.getTime() != start.maxValue.getTime())) {
				start.setMaxValue(date);
				start.validate();
			}
		}else if (field.endDateField) {
			var end = Ext.getCmp(field.endDateField);
			if (!end.minValue || (date.getTime() != end.minValue.getTime())) {
				end.setMinValue(date);
				end.validate();
			}
		}
		/*
		* Always return true since we're only using this vtype to set the
		* min/max allowed values (these are tested for after the vtype test)
		*/
		return true;
	},
	password:function(val,field){               //val指这里的文本框值，field指这个文本框组件
		if(field.confirmTo){                    //confirmTo是我们自定义的配置参数，一般用来保存另外的组件的id值
			var pwd=Ext.get(field.confirmTo);   //取得confirmTo的那个id的值
			return (val==pwd.getValue());
		}
		return true;
	},
	alphanumemail:function(val){	
		var regemail = /^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+((\.[a-zA-Z0-9_-]{2,3}){1,2})$/;
		var regw = /^\w+$/;
		return regemail.test(val)||regw.test(val);
	
	},
	alphanumemailText:"用户名只能是邮箱或者由数字、字母和下划线组成",
	ip:function(val) {
	   return /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/.test(val);
	},
	ipText:"请输入正确IP地址"
});



/*
* 重写getElementsByClassName方法
* 参数：classname
*/
document.getElementsByClassName = function(eleClassName){
   var getEleClass = [];//定义一个数组
   var myclass = new RegExp("\\b"+eleClassName+"\\b");//创建一个正则表达式对像
   var elem = this.getElementsByTagName("*");//获取文档里所有的元素
   for(var h=0;h<elem.length;h++){
     var classes = elem[h].className;//获取class对像
     if (myclass.test(classes)) getEleClass.push(elem[h]);//正则比较，取到想要的CLASS对像
   }
   return getEleClass;//返回数组
};

/*
* 增加一个名为 trim 的函数作为
* String 构造函数的原型对象的一个方法。
* 用正则表达式将前后空格用空字符串替代。
*/
String.prototype.trim = function(){
    return this.replace(/(^\s*)|(\s*$)/g, "");
};

//封装ExtJs里的Ajax
var MESSAGE_HEAD_OK = true;
var MESSAGE_HEAD_ERROR = false;
var Base = new Object();
var Bases = function(){	
	var self = this;
	
	this.request = function(_id,_url,_params, onSuccess,onError,onFailure,_timeout,_method){
		_method = (_method == 'get')?'get':'post';
		_timeout = (_timeout)?_timeout:MACROSS_TIMEOUT;
		if(Ext.get(_id) && Ext.getCmp(_id).getEl()){
			Ext.getCmp(_id).getEl().mask('loading......','x-mask-loading');
		}
		Ext.Ajax.request({
						url: _url,
						method: _method,
						timeout: _timeout,
						params: _params,
						callback: function(option,success,response){
							if(Ext.get(_id) && Ext.getCmp(_id).getEl()){
								Ext.getCmp(_id).getEl().unmask();
							}
							try{
								var msg = Ext.util.JSON.decode(response.responseText);
								if(!msg)throw "response is empty";
							}catch(e){
								if(onFailure) onFailure(response);
									else self.ajaxFail(response);
								return;
							}
					    	if(msg.success == MESSAGE_HEAD_OK){
					    		onSuccess(msg);
					    		return;
					    	}
					    	if(msg.success == MESSAGE_HEAD_ERROR){
					    		if(msg.data == 'SESSION TIMEOUT!'){
					    			Ext.Msg.alert('Warning',"登录超时，请重新登录！");
									location.href = "/";	//如果登录session超时，需要重新登录
					    			return;
					    		}
								if(onError) onError(msg);
									else self.ajaxError(msg);
								return;
					    	}
				    		self.ajaxFail();
						}
					});
	};
	
	this.ajaxFail = function(response){
		Ext.Msg.alert('Error','Server error, please try later.');
	};
	
	this.ajaxError = function(msg){
		Ext.Msg.alert("Error" , msg.data);
	};
	
	this.getParameterByUrl = function(url, item){//获取指定连接中的参数值
		var sValue=url.match(new RegExp("[\?\&]"+item+"=([^\&]*)(\&?)","i"));
		return sValue?sValue[1]:sValue;
	};

	this.getParameter = function(name){//获取当前链接中的某个参数值
	    var search = document.location.search;
	    var pattern = new RegExp("[?&]"+name+"\=([^&]+)", "g");
	    var matcher = pattern.exec(search);
	    var items = null;
	    if(null != matcher){
	        items = decodeURIComponent(matcher[1]);
	    }
	    return items;
	};
	
	this.dealTime = function(time){		
		var cur_time = time.split(" ");
		return cur_time[0];
	};
	
	this.isEmpty = function(str){// 检测字符串是否为空，空返回true
	   return ((str.trim().length == 0)||(str == null));
	};
	
	this.dealFileSize = function(size,unit){
		var n = 0;
		var i = 0;
		unit = (unit)?unit:'B';
		size = parseInt(size);		//作为字符串使用，toFixed会异常
		var iec = new Array("B","KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB");
		for(var j=0;j<iec.length;j++){
			if(iec[j] == unit.toUpperCase()){
				n = j;
				break;
			}
		}
		while ((size/1024)>1){
			size=size/1024;
			i++;
		}
		return size.toFixed(2) + iec[i+n];
	};
	
	this.validateIp = function (ip){	//验证是否为ip地址，正确返回true，检查比较严格，第一位不能为0
	    if(ip=="")return false;
	    var nums = ip.split('.');
	    if(nums.length != 4)return false;
	    var stat = 0;
	    for(i=0;i<4;i++){
	        if(!self.isNonNegativeInt(nums[i]) || self.isfirst0(nums[i]))return false;
	        var n = parseInt(nums[i]);
	        if(i==0 && n==0)return false;
	        if(n ==255)stat +=1;
			if(n<0 ||n>255)return false;
		}
		if(stat ==4)return false;
		return true;
	};
	
	this.isfirst0 = function (t){
		return ((t.slice(0,1) == 0) && t.length>1);
	};
	
	this.isNonNegativeInt = function (i){
		return (i.search("^[0-9]+$")==0);
	};
	
	this.getCheckBoxValue = function(name){
		var checkbox_arr = document.getElementsByName(name+"[]");
		if(0 == checkbox_arr.length)return;
		var num=0;
		var check_value=[];
		for(i=0;i<checkbox_arr.length;i++){
			if(checkbox_arr[i].checked){
				num++;
				check_value.push(checkbox_arr[i].value);
			}
		}
		return check_value;
	};
	
	this.dealObjectStateIcon = function(value){
		if(value == 1){
			return '<img src="/img/yes.gif">';
		}else{
			return '<img src="/img/no.gif">';
		}
	};
	
	this.sleep = function(func){
		if (func == null){
			return ;
		}
		var reg= /[\n\r]/g;
		var funcStr = func.toString().replace(reg,''); //替换回车和换行符
		reg = /.+?sleep.+?return;/;
		funcStr = '{' + funcStr.replace(reg,'');    //去掉函数test，return之前的代码
		return funcStr;
	};
	
	this.nl2br = function(str){
		var re = /\n/g;
	    var s = str.replace(re, "<br/>");
	    return s;
	};
	
	this.br2nl = function(str) {
	    var re = /(<br\/>|<br>|<BR>|<BR\/>)/g;   
	    var s = str.replace(re, "\n");
	    return s;
	};
	
	this.br2space = function(str){
	    var re = /(<br\/>|<br>|<BR>|<BR\/>)/g;   
	    var s = str.replace(re, "");
	    return s;
	};
	
	this.isInteger = function(str){ /*验证正整数 正确返回true*/
	    if(str.match(/^[0-9]\d*$/))
	       return true;
	    return false;
	};
	
	this.encode = function(string){
		return encodeURIComponent(string);
	};
	
	this.decode = function(string){
		return decodeURIComponent(string);
	};
	//处理毫秒级的文件时长
	this.dealMillitimelength = function(value){
		if(!value) return '';
		var hour = parseInt(value / 3600000);
		var minute = parseInt((value % 3600000) / 60000);
		var second = parseInt(((value % 3600000) % 60000)/1000);
		var millisecond  = ((value % 3600000) % 60000)%1000;
		return (hour<10?'0'+hour:hour)+':'+(minute<10?'0'+minute:minute)+':'+(second<10?'0'+second:second)+'.'+(millisecond);
	}
	//处理秒级的文件时长
	this.dealTimelength = function(value){
		if(!value) return '';
		var hour = parseInt(value / 3600);
		var minute = parseInt((value % 3600) / 60);
		var second = (value % 3600) % 60;
		return (hour<10?'0'+hour:hour)+':'+(minute<10?'0'+minute:minute)+':'+(second<10?'0'+second:second);
	}
	
	//格式化显示耗时,盘点模块
	this.formatConsumeTime = function(value){
		if(value === 0)return "00:00:00";
		if(value === '') return '无';
		if(value == '异常') return value;
		var hour = parseInt(value / 3600);
		var minute = parseInt((value % 3600) / 60);
		var second = (value % 3600) % 60;
		return (hour<10?'0'+hour:hour)+':'+(minute<10?'0'+minute:minute)+':'+(second<10?'0'+second:second);
	};
};
var Base = new Bases();


var UploaderBase = new Object();
uploaderBaseJs = function(){
	var self = this;
	var request_status = 0;
	var _callback = "";
	var _object_id = "";
	
	this.scriptUploaderRequest = function(object_id,_params,_method){
		self._object_id = object_id;
		self._callback = _method;
		if(Ext.get(self._object_id)){
			Ext.getCmp(self._object_id).getEl().mask('loading......','x-mask-loading');
		}
		self.request_status = 0;
		var uploader_ip = MACROSS_UPLOADER_IP;
		var uploader_port = MACROSS_UPLOADER_PORT;
		var _url = "http://"+uploader_ip+":"+uploader_port+"/mgmt/";
		self.request_status = 0;
		//为_params追加一个user_name参数
		_params['user_name'] = MACROSS_LOGIN_USER_NAME;
		_params['_time'] = new Date();		//增加随机数，防止IE等浏览器针对相同请求不在发送
		Ext.ux.JSONP.request({
			url: _url,
			timeout:MACROSS_UPLOADER_TIMEOUT,
            params:_params,
			failure:self.loadUploaderFailure
		});
	};
	
	this.scriptUploaderResponse = function(return_str){
		self.request_status = 1;		//需要将请求状态置为1
		if(Ext.get(self._object_id)){
		//	Ext.getCmp(self._object_id).getEl().unmask();		//为了防止对uploader频繁操作，此处不进行操作。在loadUploaderFailure中进行
		}
		eval(self._callback)(return_str);
	};
	
	this.loadUploaderFailure = function(){
		if(Ext.get(self._object_id)){
			Ext.getCmp(self._object_id).getEl().unmask();
		}
		if(self.request_status == 0){
			Ext.MessageBox.show({title: '警告',msg:"与Uploader连接失败，请检查Uploader是否启动",buttons: Ext.MessageBox.OK,icon: Ext.MessageBox.WARNING});
		}
	};
	
	this.dealUploaderReturnData = function(result){
		var ret_arr = result.split(';');
		var pre_result = [];
		pre_result['return'] = "error";
		pre_result['result'] = "";
		if(ret_arr[0]){
			var status_arr = ret_arr[0].split('=');
			pre_result['return'] = (status_arr[1])?status_arr[1]:"error";
		}
		if(ret_arr[1]){
			var reason_arr = ret_arr[1].split('=');
			pre_result['result'] = (reason_arr[1])?reason_arr[1]:"";
		}
		return pre_result;
	};
};

var UploaderBase = new uploaderBaseJs();

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

var Tip = new Object();
var Tips = function(){
	var _o = this;
	var IE = navigator.userAgent.indexOf('MSIE') > -1 ? true : false;
	var Opera = navigator.userAgent.indexOf('Opera') > -1 ? true : false;
	var IE7 = navigator.userAgent.indexOf('MSIE 7') > -1 ? true : false;
	var Safari = navigator.userAgent.indexOf('safari') > -1 ? true : false;
	var Firefox = navigator.userAgent.indexOf('Firefox') > -1 ? true : false;
	var Mozilla = (typeof document.implementation != 'undefined') && (typeof document.implementation.createDocument != 'undefined') && (typeof HTMLDocument != 'undefined');

	var _t = '';
	var _submit_value = '';
	this.sure = -1;
	this.eventIndex = -1;
	this.divIndex = 0;
	this.delObj = new Object();
	this.getElementsByClassName = function(ele, className){
		if(document.all){var children = ele.all;}else{var children = ele.getElementsByTagName('*');}
		var elements = new Array();
		for (var i = 0; i < children.length; i++){
			var child = children[i];
			var classNames = child.className.split(' ');
			for (var j = 0; j < classNames.length; j++) {
				if (classNames[j].trim() == className) {
					elements[elements.length] = child;
					break;
				}
			}
		}
		return elements;
	};
	this.evalscript = function(s){
		if(s.indexOf('<script') == -1) return s;
		var p = /<script[^\>]*?src=\"([^\>]*?)\"[^\>]*?(reload=\"1\")?(?:charset=\"([\w\-]+?)\")?><\/script>/ig;
		var arr = new Array();
		while(arr = p.exec(s)) appendscript(arr[1], '', arr[2], arr[3]);
		p = /<script (?!src)[^\>]*?( reload=\"1\")?>([^\x00]+?)<\/script>/ig;
		while(arr = p.exec(s)) appendscript('', arr[2], arr[1]);
		return s;
	};
	this.encode = function(string){return encodeURIComponent(string);};
	this.getFile = function(url){var index = url.lastIndexOf('/');return url.substr(index+1);};
	this.evaljson = function(resp){var json; try{eval("json = " + resp);}catch(e){var l = resp.indexOf('{'); var r = resp.lastIndexOf('}'); eval("json = " + resp.substr(l, r-l+1));};return json;};
	this.preloadImg = function(arr){var imgs= new Array();for(var i=0;i<arr.length;i++){imgs[i]=new Image();imgs[i].src=arr[i];}};
	this.backIframeDis = function(){if(!IE) return false; var shield = document.createElement("DIV");shield.id = "iframeTop" ;shield.style.position = "absolute";shield.style.left = "0px";shield.style.top = "0px";shield.style.width = "100%";shield.style.height = document.body.clientHeight + 'px';shield.style.zIndex = "499";shield.style.opacity = 0;shield.style.filter = "alpha(opacity=0)";document.body.appendChild(shield);shield.innerHTML= '<iframe src="about:blank" frameBorder=0 scrolling=no style="width:100%;height:100%;"></iframe>';};
	this.backGroundDis = function(){var shield = document.createElement("DIV");shield.id = "shield";shield.style.position = "absolute";shield.style.left = "0px";shield.style.top = "0px";shield.style.width = "100%";shield.style.height = document.body.clientHeight + 'px';shield.style.background = "#000000";shield.style.textAlign = "center";shield.style.zIndex = "500";shield.style.filter = "alpha(opacity=50)";shield.style.opacity = 0.5;document.body.appendChild(shield);};
	this.backGroundDisColor = function(_s,_e){var _opac = parseFloat($('shield').style.opacity);if(_opac >= _e) return true;_opac = _opac+0.05;$('shield').style.filter = "alpha(opacity="+(_opac*100)+")";$('shield').style.opacity = _opac;this._t = setTimeout(function(){_o.backGroundDisColor(_s,_e);}, 50);};
	this.backGroundDisClose = function(){if($('shield') != null){clearTimeout(this._t);document.body.removeChild($('shield'));};if($('iframeTop')!= null){$('iframeTop').removeChild($('iframeTop').getElementsByTagName('iframe')[0]);document.body.removeChild($('iframeTop'));};};
	this.getElementsByName = function(name, tag){var _o = document.getElementsByName(name);if(_o.length > 0) return _o;var temp = [];tag = tag || 'DIV';var _o = document.getElementsByTagName(tag.toUpperCase());for(var i=0;i<_o.length;i++){if(_o[i].getAttribute('name') == name){temp[temp.length] = _o[i];}};return temp;};
	this.closeDoDiv = function(){if($('dialog-advanced') == null) return false;document.body.removeChild($('dialog-advanced'));window.onscroll=null;window.onresize=null;_o.backGroundDisClose();return false;};
	this.closeDiv = function(){Tip.closeDoDiv();return false;};
	this.bgChangeColor = function(_id, _type, fun){var fun = fun || null;this.obj = typeof(_id)=='object' ? _id : $(_id);this._type = _type || 'up';this.start = this._type == 'up' ? 0 : 1;this.end = this._type == 'up' ? 1 : 0;if(this.obj == null) return false;this.obj.style.background = 'yellow';this.obj.style.filter = "alpha(opacity="+(this.start*100)+")";this.obj.style.opacity = this.start;this.stat = 0;var _t = this;this.timer = window.setTimeout(function(){_t.change(fun);},1);this.getStep = function(op){return op <= 0.15 ? 0.05 : 0.2;};this.change = function(fun){var op = parseFloat(this.obj.style.opacity);var step = _t.getStep(op);if(_t._type == 'up'){if(op<=_t.end){this.obj.style.opacity = op + step;this.obj.style.filter = "alpha(opacity="+(op+step)*100+")";window.setTimeout(function(){_t.change(fun);},25);}else{clearTimeout(_t.timer);fun();}}else{if(op>=_t.end){this.obj.style.opacity = op - step;this.obj.style.filter = "alpha(opacity="+(op-step)*100+")";window.setTimeout(function(){_t.change(fun);},25);}else{clearTimeout(_t.timer);fun();}}};};
	this.GoOn = function(ind,title){var obj=window.eventList[ind];window.eventList[ind]=null;if(_o.sure == -1) _o.makeSure(obj,title);else{if(_o.sure==1){$('delSureTitle').parentNode.innerHTML='<img src="img/loading.gif" />数据处理中,请等待';$('make_sure_act').className='hidden';}else{document.body.removeChild($('delMakeSure'));}; if(obj.NextStep) obj.NextStep();else obj();_o.sure = -1;_o.delObj.style.zIndex = _o.divIndex;}};
	this.removeSure = function(){$('delMakeSure')!=null && document.body.removeChild($('delMakeSure'));};
	this.disableSubmit = function(){
		if($('dialog-submit') == null) return false;
		this._submit_value = $('dialog-submit').value;
		$('dialog-submit').value = "数据提交中……";
		$('dialog-submit').disabled = 'disabled';
	};
	this.enableSubmit = function(){
		if($('dialog-submit') == null) return false;
		$('dialog-submit').value = this._submit_value;
		$('dialog-submit').disabled = false;
	};
	this.message = function(title, message){
		_o.dialog(title, message);
		$('dialog-submit').className = $('dialog-submit').className.replace('hidden','').trim() + ' hidden';
		$('dialog-cancel').value = "关闭";
	};
	this.alert = function(title, message){
		_o.dialog(title, message);
		_o.setOk(false);
	};
	this.setOk = function(_type,_value, _function){
		if($('dialog-submit') == null) return false;
		var obj = $('dialog-submit');
		if(_type == true){
			obj.className = obj.className.replace('hidden','').trim();
		}else{
			obj.className = obj.className.replace('hidden','').trim() + ' hidden';
		}
		if(_value) $('dialog-submit').value = _value;
		if(_function) $('dialog-submit').onclick = _function;
	};
	this.dialog = function(title, message){
		if($('dialog-advanced') != null) _o.closeDoDiv();
		_o.backGroundDis();
		_o.backIframeDis();
		var _html = "<div class='hd' id='dialog-title'><h3>"+title+"</h3></div><div class='bd' id='dialog-content'>"+message+"</div><div class='ft' id='dialog-ft'><input type='button' id='dialog-submit' class='f-button' value='确定'/><input type='button' id='dialog-cancel' onclick='return Tip.closeDiv()' class='f-button' value='取消'/><div class='dialog-close'><a href='#' onclick='return Tip.closeDiv()'>关闭</a></div></div><div class='underlay' id='dialog-underlay' style='width:500px;height:120px;'></div>";
		var _div = document.createElement('DIV');
		_div.className = 'dialog-advanced';
		_div.id = 'dialog-advanced';
		_div.innerHTML = _html;
		_div.style.top = 180 + document.documentElement.scrollTop + 'px';
		_div.style.left = 280 + document.documentElement.scrollLeft + 'px';
		document.body.appendChild(_div);
		this.listen();
	};
	this.listen = function(){
		if($('dialog-advanced') == null) return false;
		var extend = (IE && IE7) ? 15 : 0;
		$('dialog-underlay').style.width = ($('dialog-advanced').offsetWidth + extend).toString() + 'px';
		$('dialog-underlay').style.height = ($('dialog-advanced').offsetHeight + extend).toString() + 'px';
		setTimeout(_o.listen, 200);
	};
	this.showResult = function(title, url,parameter)
	{
		_o.alert(title,'<p class="loading">数据加载中，请等待......</p>');
		_o.showResultAjax(url,parameter);
	};
	this.showResultAjax = function(url,parameter)
	{
		Base.request('',url,parameter,
			function(msg){
				message=msg.data;
				if($('dialog-content') == null) return false;
				$('dialog-content').innerHTML = message;
				_o.evalscript('dialog-content');
			},
			function(msg){
				alert(msg.data);
				_o.closeDiv();
			}
		);
	};
	
	this.showResultSmall = function(title, message){
		_o.dialogSmall(title, message);
	};
	this.dialogSmall = function(title, message){
		if($('dialog-advanced') != null) _o.closeDoDiv();
		_o.backGroundDis();
		_o.backIframeDis();
		var _html = "<div class='hd' id='dialog-title'><h3>"+title+"</h3></div><div class='bd' id='dialog-content'>"+message+"</div><div class='ft' id='dialog-ft'><input type='button' id='dialog-submit' class='f-button' value='确定'/><input type='button' id='dialog-cancel' onclick='return Tip.closeDiv()' class='f-button' value='取消'/><div class='dialog-close'><a href='#' onclick='return Tip.closeDiv()'>关闭</a></div></div><div class='underlay' id='dialog-underlay' style='width:200px;height:120px;'></div>";
		var _div = document.createElement('DIV');
		_div.className = 'dialog-advanced';
		_div.id = 'dialog-advanced';
		_div.innerHTML = _html;
		_div.style.top = 180 + document.documentElement.scrollTop + 'px';
		_div.style.left = 280 + document.documentElement.scrollLeft + 'px';
		_div.style.width = 300+"px";
		document.body.appendChild(_div);
		this.listen();
	};
};
var Tip = new Tips();