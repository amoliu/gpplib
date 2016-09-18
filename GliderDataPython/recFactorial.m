function n=recFactorial( N )
    if N==0
        n = 1;
    else
        n = N* recFactorial(N-1);
    end
end

