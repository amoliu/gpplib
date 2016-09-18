behavior_name=surface
# surface-20deg.ma
#
# FOR MAY 17 OCSD effluent diversion (no changes from May 9 Test)
#
# climb to surface with ballast pump full out
#                       pitch servo'ed to 26 degrees
# Hand Written
# 08-Apr-02 tc@DinkumSoftware.com Initial
# 01-Feb-03 tc@DinkumSoftware.com Renamed surfac20.ma
# 03-Mar-03 kniewiad@webbresearch.com Renamed surfac30.ma for Buzzards Bay Trials
# 09-Apr-03 kniewiad@webbresearch.com Adjusted for Ashumet. Pitch to 26 deg
#
# LOOK FOR $$$ TO SEE CHANGES W.R.T. ORIGINAL 
#
#
<start:b_arg>
    # arguments for climb_to
    b_arg: c_use_bpump(enum)      2
    b_arg: c_bpump_value(X)  1000.0

    b_arg: c_use_pitch(enum)      3   # 1:battpos  2:setonce  3:servo
                                      #   in         rad        rad, >0 climb
    b_arg: c_pitch_value(X)     0.4528     # 26 deg

<end:b_arg>

