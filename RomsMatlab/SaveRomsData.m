% This script should be used to download ROMS forecasts from the JPL ROMS data server for Southern California.
% Modify the sYear, eYear, sMonth and eMonth accordingly.
% 
% Author: Arvind Pereira
sYear=2012; eYear=2012;
daysInMonths=[31 28 31 30 31 30 31 31 30 31 30 31];
addpath('/usr/local/bin/');

for yy = sYear:eYear
    if mod(yy,4)==0
        daysInMonths(2) = 29;
    end
    sMonth = 7; eMonth = 7;
    forecast = cell(sum(daysInMonths(sMonth:eMonth)),1);
    for mm =sMonth:eMonth
        for dd = 1:daysInMonths(mm)
            [X,t_s_indx,t_e_indx,lat_s_indx,lat_e_indx,lon_s_indx,lon_e_indx,d_s_indx,zd_e_indx] = GetDownloadIndices(yy,mm,dd);
            % Save each day in the forecast separately...
            for i = 0:floor(t_e_indx/24)
                %url_str = PlotROMSCurrents(yy,mm,dd);
                    t_s_indx_i = i*24;
                    t_e_indx_i= ((i+1)*24)-1;
                    if t_e_indx_i>t_e_indx
                        t_e_indx_i = t_e_indx;
                    end
                try    
                    temp_forecast=DownloadForecast(yy,mm,dd,t_s_indx_i,t_e_indx_i);
                    fileName = sprintf('fcst_%04d%02d%02d_%d',yy,mm,dd,i);
                    save(fileName,'temp_forecast');
                catch Error
                    continue;
                    %temp_forecast=DownloadForecast(yy,mm,dd,0,17);
                end
                    

            end
            %forecast{i}=DownloadForecast(yy,mm,dd); 
        end
    end
end
