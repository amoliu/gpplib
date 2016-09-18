% noElectronicsData=LoadCurrentDraw( 'data/NoElectronics.log' );
% withElectronicsData=LoadCurrentDraw('data/WithElectronics.log');
% withElectronics15Data=LoadCurrentDraw('data/WithElectronics15mi.log');
% withElectronics8hr=LoadCurrentDraw('data/WithElectronics8hr.log');
load 'data/withElectronics8hr';
load 'data/workspace.mat';

subplot(5,1,1); plot((noElectronicsData(:,2)-noElectronicsData(1,2))./3600,noElectronicsData(:,3));
%hold on;
subplot(5,1,2); plot((withElectronicsData(:,2)-withElectronicsData(1,2))./3600,withElectronicsData(:,3),'r');

subplot(5,1,3); plot((withElectronics15Data(:,2)-withElectronics15Data(1,2))./3600,withElectronics15Data(:,3),'g');

WithElect15mean = mean( withElectronicsData(:,3) );
WithElect15std = std( withElectronicsData(:,3) );

outLiers = find( (withElectronics15Data(:,3)-WithElect15mean)>3*WithElect15std);
outLiersRemoved=withElectronics15Data;
outLiersRemoved(outLiers,:)=[];
subplot(5,1,4); plot((outLiersRemoved(:,2)-outLiersRemoved(1,2))./3600,outLiersRemoved(:,3),'c');
subplot(5,1,5); plot((withElectronics8hr(:,2)-withElectronics8hr(1,2))./3600,withElectronics8hr(:,3),'m');



figure;
% Let us try to figure match this up with the data

load 'data/PVCATCC.mi.mat'

plot((noElectronicsData(:,2))./3600,noElectronicsData(:,3),'c');
hold on;
plot((data.m_present_time)./3600,data.m_air_pump,'r+');
plot((data.m_present_time)./3600,data.m_iridium_on,'b+');
plot((data.m_present_time)./3600,data.m_console_on,'g*');
plot((data.m_present_time)./3600,data.m_is_ballast_pump_moving,'y.');
plot((data.m_present_time)./3600,data.m_science_on,'m+');
legend('Current','Apump','Irid','Fwave','Bpump','Sci');
plot((withElectronicsData(:,2))./3600,withElectronicsData(:,3),'r');
plot((withElectronics15Data(:,2))./3600,withElectronics15Data(:,3),'g');
plot(withElectronics8hr(:,2)./3600,withElectronics8hr(:,3),'m');

%plot((data.m_present_time-withElectronicsData(1,2))./3600,data.m_air_pump,'r+');
% plot((data.m_present_time-noElectronicsData(1,2))./3600,data.m_air_pump,'r+');
% plot((data.m_present_time-noElectronicsData(1,2))./3600,data.m_air_pump,'r+');
% plot((data.m_present_time-noElectronicsData(1,2))./3600,data.m_air_pump,'r+');
% 
% 
