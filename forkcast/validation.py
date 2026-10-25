from typing import Any
def validate_decision(decision: dict[str,Any])->list[str]:
    errors=[]
    if not isinstance(decision,dict): return ["Decision must be a valid object."]
    if not str(decision.get("title","")).strip(): errors.append("Add a title for your decision.")
    if not str(decision.get("description","")).strip(): errors.append("Describe the decision in a sentence or two.")
    options=decision.get("options",[])
    if not isinstance(options,list) or not 2<=len(options)<=5: errors.append("Add between two and five options.")
    else:
        for i,opt in enumerate(options,1):
            if not isinstance(opt,dict) or not str(opt.get("name","")).strip(): errors.append(f"Give option {i} a name.")
    for key in ("budget_limit","time_limit"):
        value=decision.get(key)
        if value is not None:
            try:
                if float(value)<0: errors.append(f"{key.replace('_',' ').title()} cannot be negative.")
            except (TypeError,ValueError): errors.append(f"{key.replace('_',' ').title()} must be a number.")
    return errors
