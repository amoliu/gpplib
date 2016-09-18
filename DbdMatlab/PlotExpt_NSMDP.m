mdpD = missionData( 'NS_MDP_28.mat' );

expt1_start = mdpD.dateNumToUnixTime( datenum('2013-8-14 7:10:00') );
expt1_end = mdpD.dateNumToUnixTime(datenum('2013-8-17 2:30:00'));  %1343535910.48285;
startTime = expt1_start; finTime = expt1_end;

[sIdxMdp,fIdxMdp] = mdpD.findLimitIndices( startTime, finTime );


[mdpLat,mdpLon] = mdpD.webbLLtoDecDegLL( mdpD.mdata.data.m_lat(sIdxMdp:fIdxMdp),...
    mdpD.mdata.data.m_lon(sIdxMdp:fIdxMdp));

[mdpGpsLat,mdpGpsLon] = mdpD.webbLLtoDecDegLL( mdpD.mdata.data.m_gps_lat(sIdxMdp:fIdxMdp),...
    mdpD.mdata.data.m_gps_lon(sIdxMdp:fIdxMdp));

riskMap = '../RiskMaps/SCB_Sbox4.png';

r = RiskMap( riskMap );

f = figure();
imshow(r.Image);
hold on;

[x,y]=r.GetXYfromLatLon(mdpD.nnan(mdpLat),mdpD.nnan(mdpLon));
%plot(x,y,'r-','LineWidth',2.5);

[mdpGpsLat,mdpGpsLon] = r.withinMap( mdpGpsLat, mdpGpsLon );
[xg,yg] = r.GetXYfromLatLon(mdpD.nnan(mdpGpsLat),mdpD.nnan(mdpGpsLon));
plot(xg,yg,'rd-','LineWidth',3.5);

% Start: 3326.589, -11820.968
startLat = 33 + 26.589/60; startLon = -( 118 + 20.968/60 );
[sx,sy] = r.GetXYfromLatLon( startLat, startLon );
plot( sx,sy, 'b^', 'MarkerSize', 14,'LineWidth',2.5 );

% Goal : 3332.494, -11836.914
goalLat = 33 + 32.494/60; goalLon = -( 118 + 36.914/60);
[gx,gy] = r.GetXYfromLatLon( goalLat, goalLon );
plot( gx, gy, 'ks','MarkerSize', 14, 'LineWidth',2.5 );

[LEGH,OBJH,OUTH,OUTM] = legend('MDP execution', 'Start', 'Goal');
set(LEGH,'FontSize',14);

