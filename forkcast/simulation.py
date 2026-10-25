from copy import deepcopy
def apply_scenario(decision:dict,scenario:dict)->dict:
    result=deepcopy(decision); result["scenario_assumptions"]=deepcopy(scenario); return result
def reset_scenario(original:dict,defaults:dict|None=None)->tuple[dict,dict]:
    return deepcopy(original),deepcopy(defaults or {"growth":30,"risk_tolerance":50,"cost_overrun":0,"time_delay":0})
