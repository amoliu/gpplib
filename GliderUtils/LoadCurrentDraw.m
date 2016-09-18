function data=LoadCurrentDraw( logFile )
    fid= fopen(logFile,'r');
    pat = '([0-9\.]+), ([a-zA-Z0-9: ]+), (\+[0-9\.]+) A DC';
    addpath 'umtConv' -end;
    
    data=[];
    while ~feof( fid )
        tLine=fgets( fid, 200 );
        m = regexp( tLine, pat,'tokens' );
        if ~isempty(m)
            utc = str2num(m{1}{1});
            n  = unixTimeToDateNum( utc );
            amps = str2num(m{1}{3});
            %disp(sprintf('%f,%f,%f\n',n,utc,volt));
            data = vertcat(data,[n utc amps]);
        end
    end
    fclose( fid );