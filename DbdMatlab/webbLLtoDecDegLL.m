function [lat, lon] = webbLLtoDecDegLL( wLat, wLon )
    latSign = sign( wLat ); lonSign = sign( wLon );
    latDeg = floor( abs(wLat)./100.0 ); lonDeg = floor( abs(wLon)./100.0 );
    latMin = abs(wLat) - (abs(latDeg).*100.0); 
    lonMin = abs(wLon) - (abs(lonDeg).*100.0); 
    lat = latSign .* (abs(latDeg)+abs(latMin)./60.0);
    lon = lonSign .* (abs(lonDeg)+abs(lonMin)./60.0);


