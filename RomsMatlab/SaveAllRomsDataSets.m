% Function that saves all Roms Forecasts in a directory in small
% format so that data analysis can be done more easily.
% 
data_dir = '/home/arvind/data/roms/';
dir_cmd = sprintf('%sfcst*.mat',data_dir);
fcst_files=dir(dir_cmd);
[n,c] = size(fcst_files);

%% Create the forecasts cell-array which we will use for future processing.
%  Save this structure for future processing in a variable called
%  "all_forecasts".
forecasts={};
for i =1:n
    fileDate = sscanf(fcst_files(i).name,'fcst_%d_%d.mat');
    % Stupid date extraction since the sscanf above doesn't do it!
    yy = int32(fileDate(1)/10000);
    temp = fileDate(1) - (yy*10000);
    mm = int32(temp/100);
    dd = mod(temp,100); 
    seqNum = fileDate(2);
    % armed with the date, lets create the forecast.
    tfcst = SaveSmallRomsForecast(dd,mm,yy,seqNum,data_dir);
    % adding the date to the forecast just in case we want to do something
    % with it
    tfcst.dd = dd;
    tfcst.mm = mm;
    tfcst.yy = yy;
    %forecasts{i}=tfcst;
end
%save('all_forecasts','forecasts','-v7.3');
