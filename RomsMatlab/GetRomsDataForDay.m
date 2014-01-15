function GetRomsDataForDay( yy,mm,dd, data_dir )
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here
    addpath('/usr/local/bin/');
    data_dir = '/Volumes/data/roms5/'

    [X,t_s_indx,t_e_indx,lat_s_indx,lat_e_indx,lon_s_indx,lon_e_indx,d_s_indx,zd_e_indx] = GetDownloadIndices(yy,mm,dd);
    
    % Save each day in the forecast separately...
    
    t_e_indx = 72;
    timeSteps = 24;
    for i = 0:floor(t_e_indx/timeSteps)
       %url_str = PlotROMSCurrents(yy,mm,dd);
       t_s_indx_i = i*timeSteps;
       t_e_indx_i= ((i+1)*timeSteps)-1;
       if t_e_indx_i>t_e_indx
          t_e_indx_i = t_e_indx;
       end
       try
       	  %t_s_indx = 0; t_e_indx = 2; d_s_indx = 0; zd_e_indx = 11;
       	  lat_s_indx = 30; lat_e_indx = 110; lon_s_indx = 290; %lon_e_indx = 350;
          temp_forecast=DownloadForecast(yy,mm,dd,t_s_indx_i,t_e_indx_i,d_s_indx,zd_e_indx,lat_s_indx,lat_e_indx,lon_s_indx,lon_e_indx);
          fileName = sprintf('%s/fcst_%04d%02d%02d_%d',data_dir,yy,mm,dd,i);
          save(fileName,'temp_forecast');
          tfcst = SaveSmallRomsForecast(dd,mm,yy,i,data_dir);
       catch Error
          continue;
       end
    end
end
