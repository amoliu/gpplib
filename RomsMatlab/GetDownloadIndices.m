% [X,t_s_indx,t_e_indx,lat_s_indx,lat_e_indx,lon_s_indx,lon_e_indx,d_s_indx,d_e_indx] = GetDownloadIndices(yy,mm,dd)
%
% Gets the download indices for the ROMS data from the data headers.
function [X,t_s_indx,t_e_indx,lat_s_indx,lat_e_indx,lon_s_indx,lon_e_indx,d_s_indx,d_e_indx] = GetDownloadIndices(yy,mm,dd)
        
        server_str= 'http://west.rssoffice.com:8080/thredds/dodsC/pacific/CA3km-forecast/CA';
        %server_str= 'http://ourocean.jpl.nasa.gov:8080/thredds/dodsC/las';
        ldap_header_url = sprintf('%s/ca_subCA_fcst_%04d%02d%02d03.nc',server_str,yy,mm,dd);
        try
            X = loaddap('-A',ldap_header_url);
            t_s_indx = 0; t_e_indx = X.time.DODS_ML_Size-1;
            lat_s_indx = 0; 
            lat_e_indx = X.lat.DODS_ML_Size-1;
            lon_s_indx = 0; 
            lon_e_indx = X.lon.DODS_ML_Size-1;
            d_s_indx = 0; 
            d_e_indx = X.depth.DODS_ML_Size-1;
        catch Error
            disp('Error getting Indices! The file does NOT exist!');
            X=[];
            t_s_indx = 0;
            t_e_indx = 0;
            lat_s_indx = 0;
            lon_s_indx = 0;
            lat_e_indx = 0;
            lon_e_indx = 0;
            d_s_indx = 0;
            d_e_indx = 0;
            %rethrow(Error);
        end
    end
