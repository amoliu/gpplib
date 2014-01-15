% [forecast]=SaveSmallRomsForecast(dd,mm,yy,varargin)
%
% Data is assumed to be stored in a directory under the name:
% fcst_yyyymmdd.mat
%
% Arguments: dd,mm,yy (self-explanatory - day, month, year)
% Optional arguments:
% data_dir (in quotes). (Defaults to: '.')
% latN,latS,lonE,lonW (Defaults to: 34.1333, 33.25, -117.7, -118.8)
% Saves the result in: sfcst_yymmdd.mat.
% 
% Returns: forecast.
%
function [forecast]=SaveSmallRomsForecast(dd,mm,yy,seqNum,varargin)
    % First setup defaults:
    data_dir = '.';
    file_prefix = 'fcst_';
    file_postfix= '.mat';
    
    % Arvind's papers use:
    % lat range: 33.25 - 34.1333.
    % lon range: -118.8 to -117.7
    latN = 34.1333; latS = 33.25;
    lonW = -118.8;  lonE = -117.7;
    
    latN = 34.0; latS = 33.0;
    lonW = -118.9; lonE = -117.6;
    
    maxDepth = 100;

    if nargin>4, data_dir = varargin{1}; end
    if nargin>5, latN = varargin{2}; end
    if nargin>6, latS = varargin{3}; end
    if nargin>7, lonE = varargin{4}; end
    if nargin>8, lonW = varargin{5}; end
    if nargin>9, maxDepth = varargin{6}; end
    
    
    
    if dd<=0 || dd>31, disp('Error in field for dd.'); return; end
    if mm<=0 || mm>12, disp('Error in field for mm.'); return;  end
    if yy<2011 || yy> 2015, disp('Error in field for yy.'); return; end
    
    fileName = sprintf('%s/%s%04d%02d%02d_%d%s',data_dir,file_prefix,yy,mm,dd,seqNum,file_postfix);
    fileName = strrep( fileName,'//','/');
    disp(fileName);
    
    try
        load(fileName);
    catch Error
        disp('File not found');
        throw(Error);
    end
    
    % Now that we have the data, let us look for the ranges of lat,lon in
    % it.
    fix_lon = false;
    if temp_forecast.lon(1)>180
	temp_forecast.lon = temp_forecast.lon-360;
	fix_lon = true
    end
    lat1 = find( temp_forecast.lat<= latS,1,'last' );
    lat2 = find( temp_forecast.lat>= latN,1,'first');
    lon2 = find( temp_forecast.lon<= lonE,1,'last' );
    lon1 = find( temp_forecast.lon>= lonW,1,'first');
    
    % Armed with the indices we are interested in, let us save the data.
    maxDepth = find( temp_forecast.depth >= maxDepth, 1, 'first' );
    U=temp_forecast.u.u;
    V=temp_forecast.v.v;
    U=permute(U,[4,3,1,2]);
    V=permute(V,[4,3,1,2]);
    
    a=find(abs(U(:,:,:,:))>10);
    U(a)=nan;

    b=find(abs(V(:,:,:,:))>10);
    V(b)=nan;
    
    forecast = temp_forecast;
    forecast.lon = temp_forecast.lon(lon1:lon2);
    forecast.lat = temp_forecast.lat(lat1:lat2);
    forecast.time = temp_forecast.time;
    forecast.depth = temp_forecast.depth(1:maxDepth);
    forecast.u.time = temp_forecast.u.time;
    forecast.v.time = temp_forecast.v.time;
    forecast.u.depth = temp_forecast.u.depth(1:maxDepth);
    forecast.v.depth = temp_forecast.v.depth(1:maxDepth);
    forecast.u.lat = temp_forecast.u.lat(lat1:lat2);
    forecast.v.lat = temp_forecast.v.lat(lat1:lat2);
    if fix_lon==true
        forecast.u.lon = temp_forecast.u.lon(lon1:lon2)-360;
        forecast.v.lon = temp_forecast.v.lon(lon1:lon2)-360;
    else
        forecast.u.lon = temp_forecast.u.lon(lon1:lon2);
        forecast.v.lon = temp_forecast.v.lon(lon1:lon2);
    end
    forecast.u.u = U(:,1:maxDepth,lat1:lat2,lon1:lon2);
    forecast.v.v = V(:,1:maxDepth,lat1:lat2,lon1:lon2);
    
    %forecast = rmfield( forecast,{'w','zeta','salt','temp'});
    forecast = rmfield( forecast,{'zeta','salt','temp'});
    
    sfcst_fileName = sprintf('%s/sfcst_%04d%02d%02d_%d',data_dir,yy,mm,dd,seqNum);
    save(sfcst_fileName,'forecast');
    
    
    
    
    
    
