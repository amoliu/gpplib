behavior_name=yo

# Auto-generated YO11.MA file, created by GPPLIB at 2012-07-15 03:21:50.035773  (c) Arvind Pereira.

<start:b_arg>

	b_arg: c_target_altitude(m) -1 # Altitude to aim for. (when climbing we are usually aiming for -1)
	b_arg: c_pitch_value(X) 0.4538 # Climb Angle: 26.000000 deg
	b_arg: d_target_altitude(m) 4 # Altitude to aim for. (How much higher above the bottom.)
	b_arg: args_from_file(enum) 10 # >= 0 enables reading from mafiles/surfac<N>.ma
	b_arg: c_target_depth(m) 25 # Depth to aim for when at the top of the Yo. (30m max for shallow water glider)
	b_arg: d_use_pitch(enum) 3 #  1:battpos  2:setonce  3:servo
	b_arg: d_target_depth(m) 90 # Depth to aim for. (98m max for shallow water glider)
	b_arg: end_action(enum) 2 #  0-quit, 2 resume
	b_arg: d_pitch_value(X) -0.4538 # Dive Angle: -26.000000 deg
	b_arg: num_half_cycles_to_do(nodim) -1 # Number of dive/climbs to perform
					# <0 is infinite, i.e. never finishes
	b_arg: start_when(enum) 2 # BAW_PITCH_IDLE
	b_arg: c_use_pitch(enum) 3 #  1:battpos  2:setonce  3:servo
<end:b_arg>

