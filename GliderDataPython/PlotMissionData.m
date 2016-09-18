mdpD = missionData( 'R_MDP_28.mat' );
merD = missionData( 'H_MER_27.mat' );

expt1_start = mdpD.dateNumToUnixTime( datenum('2012-7-28 5:30:00') );
expt1_end = mdpD.dateNumToUnixTime(datenum('2012-7-30 20:00:00'));  %1343535910.48285;
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

riskMap = '../RiskMaps/SCB_Sbox3.png';

r = RiskMap( riskMap );

f = figure();
imshow(r.Image);
hold on;

[x,y]=r.GetXYfromLatLon(merD.nnan(merLat),merD.nnan(merLon));
%plot(x,y,'b-','LineWidth',2.5);

[merGpsLat,merGpsLon] = r.withinMap( merGpsLat, merGpsLon );
[xg,yg] = r.GetXYfromLatLon(merD.nnan(merGpsLat),merD.nnan(merGpsLon));
plot(xg,yg,'b-.','LineWidth',2.5);

[x,y]=r.GetXYfromLatLon(mdpD.nnan(mdpLat),mdpD.nnan(mdpLon));
%plot(x,y,'r-','LineWidth',2.5);

[mdpGpsLat,mdpGpsLon] = r.withinMap( mdpGpsLat, mdpGpsLon );
[xg,yg] = r.GetXYfromLatLon(mdpD.nnan(mdpGpsLat),mdpD.nnan(mdpGpsLon));
plot(xg,yg,'r--','LineWidth',2.5);



[LEGH,OBJH,OUTH,OUTM] = legend('MER execution','MDP execution','Location','West');
