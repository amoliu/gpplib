% Create an object of type risk-map initializing it with the appropriate image file. Then simply use GetXYfromLatLon to get the x,y locations. And risk from x,y returned.
classdef RiskMap
    properties (GetAccess=private)
        I    % Image
        width
        height
        colors
   end
    properties (Constant)
        %n = 34.1333; s = 33.25; e=-117.7; w=-118.8; % Real map
        n=33.6; s=33.25; e=-118.236; w=-118.8;     % Virtual map
    end
    properties (Dependent)
        Image
    end
    methods
        function obj = RiskMap( imapName )
            obj.I = imread( imapName );
            [obj.height,obj.width,obj.colors] = size(obj.I);
        end
        
        function [x,y]=GetXYfromLatLon(obj,lat,lon)
           lon2x = obj.width/abs(obj.e-obj.w);
           lat2y = obj.height/abs(obj.n-obj.s);
            
           x = (lon-repmat(obj.w,size(lon)))*lon2x;
           y = obj.height-(lat-repmat(obj.s,size(lat)))*lat2y;
        end
        
        function [lat,lon]=GetLatLonfromXY( obj, x,y )
           x2lon = abs(obj.e-obj.w)/obj.width;
           y2lat = abs(obj.n-obj.s)/obj.height;
           
           lon = repmat(obj.w,size(x))+ x.*repmat(x2lon,size(x));
           lat = repmat(obj.s,size(y))+ y.*repmat(y2lat,size(y));
        end
        
        function [inlat,inlon]=withinMap( obj,lat,lon ) 
            outN = find(lat>obj.n);
            outS = find(lat<obj.s);
            outW = find(lon<obj.w);
            outE = find(lon>obj.e);
            inlat = lat; inlon = lon;
            inlat(outN) = []; inlon(outN) = [];
            inlat(outS) = []; inlon(outS) = [];
            inlat(outE) = []; inlon(outE) = [];
            inlat(outW) = []; inlon(outW) = [];
        end
        
        function Image = get.Image(obj)
            Image = obj.I;
        end
    end
end