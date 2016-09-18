classdef missionData
    properties %(GetAccess=private)
        mdata
    end
    properties (Dependent)
    end
    
    methods
        function obj = missionData( missionName )
            obj.mdata = load( missionName );
        end
        
        function [sIdx,fIdx] = findLimitIndices(obj,startTime,endTime)
            sIdx = find( obj.mdata.data.m_present_time >= startTime,1,'first');
            fIdx = find( obj.mdata.data.m_present_time <= endTime,1, 'last' );
        end
        
        function [filtData] = nnan( obj, data )
            filtData = data( ~isnan( data ) );
        end
        
        function [unixTime] = dateNumToUnixTime( obj, dateNumTime )
            unixTime = (dateNumTime-repmat(datenum('1970-1-1 00:00:00'), ...
            size(dateNumTime))).*repmat(24*3600.0,size(dateNumTime));
        end
        
        function [dateNumTime] = unixTimeToDateNum( obj, unixTime )
            dateNumTime = repmat(datenum('1970-1-1 00:00:00'),size( unixTime ))+ ...
            unixTime./repmat(24*3600.0,size(unixTime));
        end
        
        function [idx,dist]= findLocationsNear( obj, lat, lon, slat, slon, num )
            X = [ lat lon ];
            ns=createns( X, 'nsmethod', 'kdtree', 'Distance', 'euclidean' );
            [idx,dist]=knnsearch(ns,[slat slon],'k',num);
        end
        
        function [lat, lon] = webbLLtoDecDegLL( obj, wLat, wLon )
            latSign = sign( wLat ); lonSign = sign( wLon );
            latDeg = floor( abs(wLat)./100.0 ); lonDeg = floor( abs(wLon)./100.0 );
            latMin = abs(wLat) - (abs(latDeg).*100.0); 
            lonMin = abs(wLon) - (abs(lonDeg).*100.0); 
            lat = latSign .* (abs(latDeg)+abs(latMin)./60.0);
            lon = lonSign .* (abs(lonDeg)+abs(lonMin)./60.0);
        end
    end
end