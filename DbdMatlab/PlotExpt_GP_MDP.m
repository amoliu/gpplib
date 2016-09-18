mdpD = missionData( 'R_GPMDP_28.mat' );

expt1_start = mdpD.dateNumToUnixTime( datenum('2012-8-18 10:50:00') );
expt1_end = mdpD.dateNumToUnixTime(datenum('2012-8-20 10:30:00'));  %1343535910.48285;
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

% Start: 3331.063, -11820.310
startLat = 33 + 31.063/60; startLon = -( 118 + 20.310/60 );
[sx,sy] = r.GetXYfromLatLon( startLat, startLon );
plot( sx,sy, 'b^', 'MarkerSize', 14,'LineWidth',2.5 );

[mdpGpsLat,mdpGpsLon] = r.withinMap( mdpGpsLat, mdpGpsLon );
[xg,yg] = r.GetXYfromLatLon(mdpD.nnan(mdpGpsLat),mdpD.nnan(mdpGpsLon));
xg = vertcat( sx, xg ); yg = vertcat( sy, yg );
plot(xg,yg,'rd-','LineWidth',3.5);



% Goal : 3330.150, -11843.898
goalLat = 33 + 30.150/60; goalLon = -( 118 + 43.898/60);
[gx,gy] = r.GetXYfromLatLon( goalLat, goalLon );
plot( gx, gy, 'ks','MarkerSize', 14, 'LineWidth',2.5 );

[LEGH,OBJH,OUTH,OUTM] = legend('Start', 'MDP execution',  'Goal');
set(LEGH,'FontSize',14);

