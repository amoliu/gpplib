function PlotDepthAndAltimeter(fileName)
    % Pick out a few thing from the filename. (Not very useful, huh?)
    %m=regexp(dir_list(1).name,'([a-zA-Z\_]+)([0-9]+)_([0-9]+)_([0-9]+)_([0-9]+)_dbd.m','tokens');
    
    % Run the mat-file given by this name.
    eval(strrep(fileName,'.m',''));
    
    if exist('m_present_time')
        % Plot the data with respect to time
        figure; hold off;

        subplot(2,1,1);
        % Start of with a depth/altimeter plot.
        plot((data(:,m_present_time)-start)./3600,-data(:,m_depth),'b.-'); 
        hold on; plot((data(:,m_present_time)-start)./3600,-data(:,m_raw_altitude),'g*');
        legend('depth in m','raw altitude in m');
        xlabel('time in hrs'); ylabel('meter');
        % Plot the altimeter voltage.
        hold off; 
        subplot(2,1,2);
        plot((data(:,m_present_time)-start)./3600,data(:,m_altimeter_voltage),'m*-'); legend('altimeter Volt');
        xlabel('time in hrs'); ylabel('Volt');

        title(sprintf('Plot of data from %s',strrep(fileName,'_','-')));
        % Save the figure.
        print( gcf,'-dpng', strrep(fileName,'.m','.png') );
    end