/**
 * 自定义下拉树，支持初始化值时自动定位树节点。
 */
Ext.ux.ComboBoxTree = Ext.extend(Ext.form.ComboBox, {
	//树的配置项
	dataUrl: null, //获取树所有节点的url
	//通过id获取某个节点的id全路径的url，返回值的格式应该是：parentId1/parentId2/parentId3/../节点id
	//如果不设置这个值，下拉树不会自动定位节点并在初始化时显示文本
	nodePathUrl: null,
	loader: null,
	root: {},
	rootVisible: false,
	//树的选择模式
	rootSelectable: false, //根节点是否可选，默认为false
	folderSelectable: true, //目录是否可选，默认为true
	leafSelectable: true, //叶子是否可选，默认为true
	showFullPath: false, //是否显示全路径
	rootValue: undefined, //根节点的值（通常根节点的取值与普通节点的取值不一样，如果一样则不需要设置此值）
	//原combo类的配置项
	store: new Ext.data.SimpleStore({fields:[],data:[[]]}),
	mode: 'local',
	triggerAction: 'all',
	editable: false,
	forceSelection: true,
	tree: null, //树控件，在expand方法中初始化
	//private: 用于防止combo收缩，在树的事件中控制此属性值
	preventCollapse: false,
	
	initComponent: function(){
		this.treeId = Ext.id();
		this.height = this.height || 200;
		this.tpl = String.format('<tpl for="."><div id="{0}" style="height:{1}px"></div></tpl>', this.treeId, this.height);
		Ext.ux.ComboBoxTree.superclass.initComponent.call(this);
	},
	setValue: function(value){
		var comboTree = this;
		if (!value || value==0){//页面上获取的value为空时其对应值为0
			this.doSetValue(null);
		}
		else if (Ext.isObject(value)){ //点击树节点时的选择
			this.doSetValue(value);
		}
		else{ //只是设置一个值，从后台获取这个值的路径，并在树中选中这个节点
			var url = this.nodePathUrl;
			if (!url){
				this.doSetValue({id: value});
				return;
			}
			if (!this.tree) this.initTree();

			Base.request(
			'',
			url,
			'announce_node_id='+value,
			function(result){
				result = result.data;
				path = '/' + comboTree.root.id + (result.indexOf('/') == 0 ? '' : '/') + result;
				comboTree.tree.selectPath(path, 'id', function(success, node){
					comboTree.doSetValue(success ? node : null);
				});
			});
		}
    },
    //private:设置值，参数value应该是一个对象
    doSetValue: function(value){
    	var id = value ? value.id : '';
    	var text = value ? value.text : '';
    	if (value && value.attributes){ //是树节点
    		var isRootNode = (value == this.tree.root);
    		if (isRootNode && Ext.isDefined(this.rootValue)){
    			id = this.rootValue;
    		}
            if (this.showFullPath){
            	text = isRootNode ? '/' : value.getPath('text').replace('/' + this.tree.root.text, '');
            }
    	}
		this.value = id;
		if(this.hiddenField) this.hiddenField.value = id; //设置表单域
		this.lastSelectionText = text;
        this.fireEvent('select', this, value);
        Ext.form.ComboBox.superclass.setValue.call(this, text);
    },
    selectPath: function(path){
    	this.tree.selectPath(path);
    },
    getValue : function(){
    	return Ext.isDefined(this.value) ? this.value : ''; 
    },
    //取得树开节点的属性值
	getNodeValue: function(){
		return this.tree ? this.tree.getSelectionModel().getSelectedNode() : null;
		//return node ? node.attributes : null;
	},
	//通过树节点的ID获取节点对象
	getNodeById: function(id){
		return this.tree ? this.tree.getNodeById(id) : null;
		//return node ? node.attributes : null;
	},
	getText: function(){
		return this.lastSelectionText || '';
	},
    //private: 根据preventCollapse属性判断是否要收缩
	collapse: function(){
		if (this.preventCollapse){
			this.preventCollapse = false;
			return;
		}
		Ext.ux.ComboBoxTree.superclass.collapse.call(this);
	},
	//private:
	expand : function(){
		Ext.ux.ComboBoxTree.superclass.expand.call(this);
		if (!this.tree){
			this.initTree();
		}
    },
    //private:
    destroy: function(){
    	if (this.tree && this.tree.rendered) this.tree.destroy();
    	Ext.form.ComboBox.superclass.destroy.call(this);
    },
    //private
    initTree: function(){
    	if (!this.list){ //必须先初始化列表，在一开始就设置了combotree的值时尤其重要
			this.initList();
    	}
    	//设置this.preventCollapse=true，防止combo收缩
    	var enableCollapse = function(){this.preventCollapse = false;};
    	//设置this.preventCollapse=false，允许combo收缩
    	var disableCollapse = function(){this.preventCollapse = true;};
    	var combo = this;
    	this.tree = new Ext.tree.TreePanel({
    		renderTo: this.treeId,
    		useArrows: false,
    	    autoScroll: true,
    	    height: this.height,  //fix IE
    	    animate: true,
    	    enableDD: false,
    	    containerScroll: true,
    	    border: false,
			dataUrl: this.dataUrl,
			tbar: [{text:'清空',xtype:'button',iconCls:'reset',handler:function(){combo.setValue(null);}}],
			loader: this.loader,
			root: this.root,
			rootVisible: this.rootVisible,
			listeners: {
	        	click: function(node){
	        		disableCollapse();
		        	if (node == this.tree.root){ //选中根节点
		        		if (!this.rootSelectable) return;
		        	}
		        	else if (!node.isLeaf()){ //选中目录节点
		        		if (!this.folderSelectable) return;
		        	}
		        	else{ //选中叶子节点
		        		if (!this.leafSelectable) return;
		        	}
		        	//先选择节点，再设置value，让getNodeValue方法在select事件中取到正确的值
		        	node.select();
		        	this.setValue(node);
		        	enableCollapse();
	        	},
	        	//展开和收缩节点时防止combo收缩
	        	beforeexpandnode: disableCollapse,
	        	beforecollapsenode: disableCollapse,
	        	beforeload: disableCollapse,
	        	//节点加载和展开后允许combo收缩
	        	load: enableCollapse,
	        	expandnode: enableCollapse,
	        	scope: this
			}
    	});
    }
});
Ext.reg('combotree', Ext.ux.ComboBoxTree);