classdef netcdfvar < handle
    % Helper netcdfobj.m
    %
    %
    % Aslak Grinsted 2009
    properties(SetAccess=private) %setting not supported yet.
        name= '';
        id = [];
        val=[];
        xtype = [];
        atts = [];
        parent = [];
    end
    properties(SetAccess=public)
        value;
    end
    

    methods
        function obj = netcdfvar(parent,id) 
            obj.parent=parent;
            obj.id=id;
            [name, xtype, dimids, numatts] = netcdf.inqVar(obj.parent.ncid,id); %get all meta data
            obj.xtype=xtype;
            %obj.name.struct('id',ii-1,'xtype',xtype,'dimids',dimids,'getValue',@()netcdf.getVar(ncid,ii-1));
            obj.name=name;
            obj.atts=netcdfnamedlist(numatts);
            for jj=1:numatts
               obj.atts.listdata{jj}=netcdfatt(obj,jj-1);
            end
        end
        
        function value=get.value(obj)
            if isempty(obj.val)
                obj.val= netcdf.getVar(obj.parent.ncid,obj.id);
            end
            value=obj.val;
        end

        function set.value(obj,val)
            obj.val=val;
            netcdf.putVar(obj.parent.ncid,obj.id,obj.val);
        end
        
        
        function prettydisp(obj)
            
            disp(obj.name)
        end
        
    end
    

end
