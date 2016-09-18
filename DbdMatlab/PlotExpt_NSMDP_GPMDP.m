mdpD = missionData( 'NS_MDP_28.mat' );

expt1_start = mdpD.dateNumToUnixTime( datenum('2013-8-14 7:10:00') );
expt1_end = mdpD.dateNumToUnixTime(datenum('2013-8-17 2:30:00'));  %1343535910.48285;
startTime = expt1_start; finTime = expt1_end;

[sIdxMdp,fIdxMdp] = mdpD.findLimitIndices( startTime, finTime );


[mdpLat,mdpLon] = mdpD.webbLLtoDecDegLL( mdpD.mdata.data.m_lat(sIdxMdp:fIdxMdp),...
    mdpD.mdata.data.m_lon(sIdxMdp:fIdxMdp));

[mdpGpsLat,mdpGpsLon] = mdpD.webbLLtoDecDegLL( mdpD.mdata.data.m_gps_lat(sIdxMdp:fIdxMdp),...
    mdpD.mdata.data.m_gps_lon(sIdxMdp:fIdxMdp));

% GPMDP section
mdpD2 = missionData( 'R_GPMDP_28.mat' );

expt1_start2 = mdpD2.dateNumToUnixTime( datenum('2012-8-18 10:50:00') );
expt1_end2 = mdpD2.dateNumToUnixTime(datenum('2012-8-20 10:30:00'));  %1343535910.48285;
startTime2 = expt1_start2; finTime2 = expt1_end2;

[sIdxMdp2,fIdxMdp2] = mdpD2.findLimitIndices( startTime2, finTime2 );


[mdpLat2,mdpLon2] = mdpD2.webbLLtoDecDegLL( mdpD2.mdata.data.m_lat(sIdxMdp2:fIdxMdp2),...
    mdpD2.mdata.data.m_lon(sIdxMdp2:fIdxMdp2));

[mdpGpsLat2,mdpGpsLon2] = mdpD2.webbLLtoDecDegLL( mdpD2.mdata.data.m_gps_lat(sIdxMdp2:fIdxMdp2),...
    mdpD2.mdata.data.m_gps_lon(sIdxMdp2:fIdxMdp2));

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

[LEGH,OBJH,OUTH,OUTM] = legend('NS-GPMDP execution', 'NS-GPMDP Start', 'NS-GPMDP Goal');
set(LEGH,'FontSize',14);

%% GPMDP section
[x2,y2]=r.GetXYfromLatLon(mdpD2.nnan(mdpLat2),mdpD2.nnan(mdpLon2));
%plot(x,y,'r-','LineWidth',2.5);

% Start: 3331.063, -11820.310
startLat2 = 33 + 31.063/60; startLon2 = -( 118 + 20.310/60 );
[sx2,sy2] = r.GetXYfromLatLon( startLat2, startLon2 );
plot( sx2,sy2, 'g^', 'MarkerSize', 14,'LineWidth',2.5 );

[mdpGpsLat2,mdpGpsLon2] = r.withinMap( mdpGpsLat2, mdpGpsLon2 );
[xg2,yg2] = r.GetXYfromLatLon(mdpD2.nnan(mdpGpsLat2),mdpD2.nnan(mdpGpsLon2));
xg2 = vertcat( sx2, xg2 ); yg2 = vertcat( sy2, yg2 );
plot(xg2,yg2,'bd-','LineWidth',3.5);



% Goal : 3330.150, -11843.898
goalLat = 33 + 30.150/60; goalLon = -( 118 + 43.898/60);
[gx,gy] = r.GetXYfromLatLon( goalLat, goalLon );
plot( gx, gy, 'ro','MarkerSize', 14, 'LineWidth',2.5 );

[LEGH,OBJH,OUTH,OUTM] = legend('NS-GPMDP execution', 'NS-GPMDP Start', 'NS-GPMDP Goal','GPMDP Start', 'GPMDP execution',  'GPMDP Goal');
set(LEGH,'FontSize',14);




