function GetNCToSfcts( dd,mm,yy )
%UNTITLED2 Summary of this function goes here
%   Detailed explanation goes here

    % First setup defaults:
    data_dir = '.';
    file_prefix = 'ca_subCA_fcst_';
    file_postfix= '.nc';
    seqNum = 3;
    
    % Arvind's papers use:
    % lat range: 33.25 - 34.1333.
    % lon range: -118.8 to -117.7
    %latN = 34.1333; latS = 33.25;
    %lonW = -118.8;  lonE = -117.7;
    
    latN = 34.0; latS = 33.0;
    lonW = -118.9; lonE = -117.6;
    
    maxDepth = 100;
    
    %load data
    data = netcdfobj(sprintf('%s/%s%04d%02d%02d%02d%s',data_dir,file_prefix,yy,mm,dd,seqNum,file_postfix));
    
    % Now that we have the data, let us look for the ranges of lat,lon in
    % it.
    %data.vars.lon.value = data.vars.lon.value-360;
    lat1 = find( data.vars.lat.value<= latS,1,'last' );
    lat2 = find( data.vars.lat.value>= latN,1,'first');
    lon2 = find( data.vars.lon.value-360<= lonE,1,'last' );
    lon1 = find( data.vars.lon.value-360>= lonW,1,'first');
    
    % Armed with the indices we are interested in, let us save the data.
    maxDepth = find( data.vars.depth.value >= maxDepth, 1, 'first' );
    U=data.vars.u.value;
    V=data.vars.v.value;
    U=permute(U,[4,3,1,2]);
    V=permute(V,[4,3,1,2]);
    
    a=find(abs(U(:,:,:,:))>10);
    U(a)=nan;

    b=find(abs(V(:,:,:,:))>10);
    V(b)=nan;
    
    forecast = {};
    forecast.lon = data.vars.lon.value(lon1:lon2)-360;
    forecast.lat = data.vars.lat.value(lat1:lat2);
    forecast.time = data.vars.time.value;
    forecast.depth = data.vars.depth.value(1:maxDepth);
    forecast.u.time = data.vars.time.value;
    forecast.v.time = data.vars.time.value;
    forecast.u.depth = data.vars.depth.value(1:maxDepth);
    forecast.v.depth = data.vars.depth.value(1:maxDepth);
    forecast.u.lat = data.vars.lat.value(lat1:lat2);
    forecast.v.lat = data.vars.lat.value(lat1:lat2);
    forecast.u.lon = data.vars.lon.value(lon1:lon2)-360;
    forecast.v.lon = data.vars.lon.value(lon1:lon2)-360;
    forecast.u.u = U(:,1:maxDepth,lon1:lon2,lat1:lat2);
    forecast.v.v = V(:,1:maxDepth,lon1:lon2,lat1:lat2);
    
    %forecast = rmfield( forecast,{'w','zeta','salt','temp'});
    
    t_e_indx = 72;
    tForecast = forecast;
    for i=0:floor(t_e_indx/24)
        t_s_indx_i = i*24+1;
        t_e_indx_i = ((i+1)*24);
        if t_e_indx_i>t_e_indx
            t_e_indx_i = t_e_indx;
        end
        seqNum = i;
        forecast.time = forecast.time(t_s_indx_i:t_e_indx_i);
        forecast.u.time = forecast.u.time(t_s_indx_i:t_e_indx_i);
        forecast.v.time = forecast.v.time(t_s_indx_i:t_e_indx_i);
        forecast.u.u = forecast.u.u(t_s_indx_i:t_e_indx_i,:,:,:);
        forecast.v.v = forecast.v.v(t_s_indx_i:t_e_indx_i,:,:,:);
	% ---- Looks like we need to permute the u, v axes here ----
	forecast.u.u = permute( forecast.u.u,[1,2,4,3]);
	forecast.v.v = permute( forecast.v.v,[1,2,4,3]);
        
        sfcst_fileName = sprintf('%s/sfcst_%04d%02d%02d_%d',data_dir,yy,mm,dd,seqNum);
        save(sfcst_fileName,'forecast');
        
        forecast = tForecast;
    end
end

