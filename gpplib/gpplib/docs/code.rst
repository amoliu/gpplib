Glider Path Planning Library
****************************

Welcome to the documentation of the Glider Path Planning Library. 
Please refer to GPP_in_CPP_ for details on the C++ path-planning documentation.

.. _GPP_IN_CPP: ../../html/index.html

	GenGliderModelUsingRoms
	=======================
	
	This class is the glue for the gpplib and contains basic features shared across all the other parts
	of gpplib.
	
	.. automodule:: gpplib.GenGliderModelUsingRoms
	
	.. autoclass:: GliderModel
	    :members: SimulateDive, OpenSfcstFile, GetObs, GetRisk, ObsDetLatLon, GetRomsData, LatLonToRomsXY, PlotNewRiskMapFig, PlotCurrentField, InitSim, SimulateDive_R
	
	
	
	MDP Class -- for Minimum Risk Planning in Currents
	==================================================
	
	This class is useful in running a 'MDP'_ planner instance.
	
	.. automodule:: gpplib.MDP_class
	
	.. autoclass:: MDP
	    :members: __init__, GetTransitionModelFromShelf, GetRomsData, SetGoalAndInitTerminalStates, GetUtilityForStateTransition, CalculateTransUtilities, doValueIteration, DisplayPolicy, GetPolicyTreeForMDP, GetPolicyAtCurrentNode, GetRiskFromXY, SimulateAndPlotMDP_PolicyExecution, InitMDP_Simulation, SimulateAndPlotMDP_PolicyExecution_R
	    
	An Example of its use can be found in gpplib/GppPython/debugMDP.py listed below:
	    
	.. literalinclude:: ../../GppPython/debugMDP.py
	    
	
	Replanner -- for Minimum (Expected) Risk Planning in Currents
	=============================================================
	
	This class is useful to run a 'Replanner'_ instance.
	
	.. automodule:: gpplib.Replanner
	
	.. autoclass:: Replanner
	    :members: __init__, GetTransitionModelFromShelf, GetRomsData, GetExpRisk, CreateExpRiskGraph, CreateMinRiskGraph, GetShortestPathMST, GetPathXYfromPathList, BackTrackNxPath, BackTrackPath, PlotMRpaths, GetPolicyNxMR, GetPolicyMR, GetRiskFromXY, SimulateAndPlotMR_PolicyExecution
	
	An example of its use can be found in gpplib/GppPython/debugReplanner.py listed below:
	
	.. literalinclude:: ../../GppPython/debugReplanner.py

	
	SA_MDP Class -- for Minimum Risk Planning in Currents
	==================================================
	
	This class is useful in running a 'SA_MDP'_ planner instance.
	
	.. automodule:: gpplib.StateActionMDP
	
	.. autoclass:: SA_MDP
	    :members: __init__, BuildTransitionGraph, GetRewardForStateAction, GetUtilityForStateTransition, GetXYfromNodeStr, GetNodesFromEdgeStr, GetTransitionModelFromShelf, GetRomsData, SetGoalAndInitTerminalStates, GetUtilityForStateTransition, CalculateTransUtilities, doValueIteration, DisplayPolicy, GetPolicyTreeForMDP, GetPolicyAtCurrentNode, GetRiskFromXY, SimulateAndPlotMDP_PolicyExecution, InitMDP_Simulation, SimulateAndPlotMDP_PolicyExecution_R
	    
	An Example of its use can be found in gpplib/GppPython/debugSA_MDP.py listed below:
	    
	.. literalinclude:: ../../GppPython/debugSA_MDP.py
	
	
	SA_Replanner -- for Minimum (Expected) Risk Planning in Currents
	=============================================================
	
	This class is useful to run a 'SA_Replanner'_ instance.
	
	.. automodule:: gpplib.SA_Replanner
	
	.. autoclass:: SA_Replanner
	    :members: __init__, GetTransitionModelFromShelf, GetRomsData, GetExpRisk, CreateExpRiskGraph, CreateMinRiskGraph, GetShortestPathMST, GetPathXYfromPathList, BackTrackNxPath, BackTrackPath, PlotMRpaths, GetPolicyNxMR, GetPolicyMR, GetRiskFromXY, SimulateAndPlotMR_PolicyExecution
	
	An example of its use can be found in gpplib/GppPython/debugSA_Replanner.py listed below:
	
	.. literalinclude:: ../../GppPython/debugSA_Replanner.py