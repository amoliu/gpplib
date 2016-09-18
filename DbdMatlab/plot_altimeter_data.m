dir_list = dir('he_ha_pe_*.m');

for i = 1:length(dir_list)
    disp(sprintf('Plotting depth and altitude data for %s',dir_list(i).name));
    PlotDepthAndAltimeter(dir_list(i).name);
end

