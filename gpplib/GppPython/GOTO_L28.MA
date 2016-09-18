behavior_name=goto_list
#Mission file for MDP policy for Glider rusalka

<start:b_arg>

	b_arg: num_legs_to_run(nodim) -2 # TRAVERSE_LIST_ONCE
	b_arg: num_waypoints(nodim) 5 # 
	b_arg: start_when(enum) 0 # BAW_IMMEDIATELY
	b_arg: list_stop_when(nodim) 7 # BAW_WHEN_WPT_DIST
	b_arg: initial_wpt(nodim) -2 # CLOSEST
<end:b_arg>
<start:waypoints>
-11821.7740	3328.2908
-11820.0820	3328.2908
-11820.0820	3329.3546
-11820.0820	3330.4184
-11821.7740	3328.2908
<end:waypoints>