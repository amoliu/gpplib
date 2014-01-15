function forecast=DownloadForecast(yy,mm,dd,varargin)
%  forecast=DownloadForecast(yy,mm,dd,varargin)
%  
%  Optional arguments are:
%  t_s_indx, t_e_indx -> Start and End indices for time.
%  d_s_indx, d_e_indx -> Start and End indices for depth.
%  lat_s_indx, lat_e_indx -> Start and End indices for latitude.
%  lon_s_indx, lon_e_indx -> Start and End indices for longitude.
%  
%  By default all the data is attempted to be downloaded.
%  Unfortunately, this will not work, since JPL restricts the maximum data download file size.
%  Use the script SaveRomsData.m to issue the appropriate calls to this function
%  so that the data gets downloaded properly.
%  
%  Earlier, indices for data were within SCB (Arvind's planner).
%     t_s_indx=0; t_e_indx=23; d_s_indx=1; d_e_indx=11;
%     lat_s_indx=37; lat_e_indx=82; lon_s_indx=118; lon_e_indx=180;
%
%  Author: Arvind A de Menezes Pereira
%  
    
    %server_str= 'http://ourocean.jpl.nasa.gov:8080/thredds/dodsC/las';
    server_str= 'http://west.rssoffice.com:8080/thredds/dodsC/pacific/CA3km-forecast/CA';
% Indices for all the data.
   %t_s_indx=0; t_e_indx=23; d_s_indx=0; d_e_indx=23;
   %lat_s_indx=0; lat_e_indx=110; lon_s_indx=0; lon_e_indx=210;
   try
    [X,t_s_indx,t_e_indx,lat_s_indx,lat_e_indx,lon_s_indx,lon_e_indx,d_s_indx,d_e_indx] = GetDownloadIndices(yy,mm,dd);
   catch Error
      throw(Error);
   end
   r = 98; c = 103;
   % r=52; c=49;
   %r=21; c=20;
   % t_s_indx=0; t_e_indx=23; d_s_indx=1; d_e_indx=11;
   % lat_s_indx=38; lat_e_indx=81; lon_s_indx=120; lon_e_indx=175;
    
    % Arvind's papers use:
    % lat range: 33.25 - 34.1333.
    % lon range: -118.8 to -117.7
    if nargin>3, t_s_indx = varargin{1}; end
    if nargin>4, t_e_indx = varargin{2}; end
    if nargin>5, d_s_indx = varargin{3}; end
    if nargin>6, d_e_indx = varargin{4}; end
    if nargin>7, lat_s_indx = varargin{5}; end
    if nargin>8, lat_e_indx = varargin{6}; end
    if nargin>9, lon_s_indx = varargin{7}; end
    if nargin>10, lon_e_indx = varargin{8}; end
    if nargin>11, r = varargin{9}; end
    if nargin>12, c = varargin{10}; end
    
    if yy<2008 or yy>2015, yy = 2015; end
    if mm<1 or mm>12, mm = 1; end
    if dd<1 or dd>12, dd = 12; end
    
    %addpath('/Users/arvind/Documents/code/Matlab_Libraries/');
    
    try
        ldap_url = GetLDAPUrl(server_str,yy,mm,dd,t_s_indx,t_e_indx,lat_s_indx,lat_e_indx,lon_s_indx,lon_e_indx,d_s_indx,d_e_indx);
        disp(ldap_url)
        forecast=loaddap(ldap_url);
    catch Error % We might have made a mistake. Grab what we can!
        %[X,t_s_indx,t_e_indx,lat_s_indx,lat_e_indx,lon_s_indx,lon_e_indx,d_s_indx,d_e_indx] = GetDownloadIndices(yy,mm,dd);
        %ldap_url = GetLDAPUrl(server_str,yy,mm,dd,t_s_indx,t_e_indx,lat_s_indx,lat_e_indx,lon_s_indx,lon_e_indx,d_s_indx,d_e_indx);
        %disp(ldap_url)
        %forecast = loaddap(ldap_url);
        forecast = [];
        disp('Error Getting Data!!!');
        throw(Error);
    end
    
    
    

%    function ldap_url2 = GetLDAPUrl(server_str,yy,mm,dd,t_s_indx,t_e_indx,lat_s_indx,lat_e_indx,lon_s_indx,lon_e_indx,d_s_indx,d_e_indx)
%        ldap_url2 = sprintf('%s/ca_subCA_fcst_%04d%02d%02d03.nc?time[%d:1:%d],depth[%d:1:%d],lat[%d:1:%d],lon[%d:1:%d],temp[%d:1:%d][%d:1:%d][%d:1:%d][%d:1:%d],salt[%d:1:%d][%d:1:%d][%d:1:%d][%d:1:%d],u[%d:1:%d][%d:1:%d][%d:1:%d][%d:1:%d],v[%d:1:%d][%d:1:%d][%d:1:%d][%d:1:%d],w[%d:1:%d][%d:1:%d][%d:1:%d][%d:1:%d],zeta[%d:1:%d][%d:1:%d][%d:1:%d]',...
%            server_str,yy,mm,dd, t_s_indx, t_e_indx, d_s_indx, d_e_indx, ...
%            lat_s_indx,lat_e_indx, lon_s_indx, lon_e_indx, ...
%            t_s_indx, t_e_indx, d_s_indx, d_e_indx, ...
%            lat_s_indx,lat_e_indx, lon_s_indx, lon_e_indx, ...
%            t_s_indx, t_e_indx, d_s_indx, d_e_indx, ...
%            lat_s_indx,lat_e_indx, lon_s_indx, lon_e_indx, ...
%            t_s_indx, t_e_indx, d_s_indx, d_e_indx, ...
%            lat_s_indx,lat_e_indx, lon_s_indx, lon_e_indx, ...
%            t_s_indx, t_e_indx, d_s_indx, d_e_indx, ...
%            lat_s_indx,lat_e_indx, lon_s_indx, lon_e_indx, ...
%            t_s_indx, t_e_indx, d_s_indx, d_e_indx, ...
%            lat_s_indx,lat_e_indx, lon_s_indx, lon_e_indx, ...
%            t_s_indx, t_e_indx, ...
%            lat_s_indx,lat_e_indx, lon_s_indx, lon_e_indx);
%            
%    end
    
    function ldap_url2 = GetLDAPUrl(server_str,yy,mm,dd,t_s_indx,t_e_indx,lat_s_indx,lat_e_indx,lon_s_indx,lon_e_indx,d_s_indx,d_e_indx)
        ldap_url2 = sprintf('%s/ca_subCA_fcst_%04d%02d%02d03.nc?time[%d:1:%d],depth[%d:1:%d],lat[%d:1:%d],lon[%d:1:%d],temp[%d:1:%d][%d:1:%d][%d:1:%d][%d:1:%d],salt[%d:1:%d][%d:1:%d][%d:1:%d][%d:1:%d],u[%d:1:%d][%d:1:%d][%d:1:%d][%d:1:%d],v[%d:1:%d][%d:1:%d][%d:1:%d][%d:1:%d],zeta[%d:1:%d][%d:1:%d][%d:1:%d]',...
            server_str,yy,mm,dd, t_s_indx, t_e_indx, d_s_indx, d_e_indx, ...
            lat_s_indx,lat_e_indx, lon_s_indx, lon_e_indx, ...
            t_s_indx, t_e_indx, d_s_indx, d_e_indx, ...
            lat_s_indx,lat_e_indx, lon_s_indx, lon_e_indx, ...
            t_s_indx, t_e_indx, d_s_indx, d_e_indx, ...
            lat_s_indx,lat_e_indx, lon_s_indx, lon_e_indx, ...
            t_s_indx, t_e_indx, d_s_indx, d_e_indx, ...
            lat_s_indx,lat_e_indx, lon_s_indx, lon_e_indx, ...
            t_s_indx, t_e_indx, d_s_indx, d_e_indx, ...
            lat_s_indx,lat_e_indx, lon_s_indx, lon_e_indx, ...
            t_s_indx, t_e_indx, ...
            lat_s_indx,lat_e_indx, lon_s_indx, lon_e_indx);
    end
    
    
end
