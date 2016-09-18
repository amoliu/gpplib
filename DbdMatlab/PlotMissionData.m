mdpD = missionData( 'R_MDP_28.mat' );
merD = missionData( 'H_MER_27.mat' );

expt1_start = mdpD.dateNumToUnixTime( datenum('2012-7-28 5:30:00') );
expt1_end = mdpD.dateNumToUnixTime(datenum('2012-7-30 18:00:00'));  %1343535910.48285;
startTime = expt1_start; finTime = expt1_end;

[sIdxMdp,fIdxMdp] = mdpD.findLimitIndices( startTime, finTime );
[sIdxMer,fIdxMer] = merD.findLimitIndices( startTime, finTime );


[mdpLat,mdpLon] = mdpD.webbLLtoDecDegLL( mdpD.mdata.data.m_lat(sIdxMdp:fIdxMdp),...
    mdpD.mdata.data.m_lon(sIdxMdp:fIdxMdp));
[merLat,merLon] = merD.webbLLtoDecDegLL(merD.mdata.data.m_lat(sIdxMer:fIdxMer),...
    merD.mdata.data.m_lon(sIdxMer:fIdxMer));

[mdpGpsLat,mdpGpsLon] = mdpD.webbLLtoDecDegLL( mdpD.mdata.data.m_gps_lat(sIdxMdp:fIdxMdp),...
    mdpD.mdata.data.m_gps_lon(sIdxMdp:fIdxMdp));
[merGpsLat,merGpsLon] = mdpD.webbLLtoDecDegLL( merD.mdata.data.m_gps_lat(sIdxMer:fIdxMer),...
    merD.mdata.data.m_gps_lon(sIdxMer:fIdxMer));

riskMap = '../RiskMaps/SCB_Sbox4.png';

r = RiskMap( riskMap );

f = figure();
imshow(r.Image);
hold on;

[x,y]=r.GetXYfromLatLon(merD.nnan(merLat),merD.nnan(merLon));
%plot(x,y,'b-','LineWidth',2.5);

% Cleanup skipped waypoint
[idx,dist] = merD.findLocationsNear( merGpsLat, merGpsLon, ...
    33.5056, -118.4355, 30 ); merGpsLat(idx)=[]; merGpsLon(idx)=[];


[merGpsLat,merGpsLon] = r.withinMap( merGpsLat, merGpsLon );
[xg,yg] = r.GetXYfromLatLon(merD.nnan(merGpsLat),merD.nnan(merGpsLon));
plot(xg,yg,'b+-','LineWidth',3.5);

[x,y]=r.GetXYfromLatLon(mdpD.nnan(mdpLat),mdpD.nnan(mdpLon));
%plot(x,y,'r-','LineWidth',2.5);

[idx,dist] = mdpD.findLocationsNear( mdpGpsLat, mdpGpsLon, ...
    33.496, -118.627, 20 ); mdpGpsLat(idx)=[]; mdpGpsLon(idx)=[];

[mdpGpsLat,mdpGpsLon] = r.withinMap( mdpGpsLat, mdpGpsLon );
[xg,yg] = r.GetXYfromLatLon(mdpD.nnan(mdpGpsLat),mdpD.nnan(mdpGpsLon));
plot(xg,yg,'rd-.','LineWidth',3.5);


startLat = mdpGpsLat(find(~isnan(mdpGpsLat),1,'first'));
startLon = mdpGpsLon(find(~isnan(mdpGpsLon),1,'first'));
[sx,sy] = r.GetXYfromLatLon( startLat, startLon );
plot( sx,sy, 'g^', 'MarkerSize', 14,'LineWidth',2.5 );

%goalLat = mdpGpsLat(find(~isnan(mdpGpsLat),1,'last'));
%goalLon = mdpGpsLon(find(~isnan(mdpGpsLon),1,'last'));
goalLat = 33.529; goalLon = -118.735;
[gx,gy] = r.GetXYfromLatLon( goalLat, goalLon );
plot( gx, gy, 'ms','MarkerSize', 14, 'LineWidth',2.5 );

[LEGH,OBJH,OUTH,OUTM] = legend('MER execution','MDP execution', 'Start', 'Goal');
set(LEGH,'FontSize',14);

