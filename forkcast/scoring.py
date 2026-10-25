from __future__ import annotations
from .models import number
def _clamp(x): return max(0.0,min(100.0,float(x)))
def _cost_score(cost,budget):
    if budget is None or budget<=0: return 65.0 if cost<=0 else 60.0
    return _clamp(100-max(0,cost-budget)/max(budget,1)*100-cost/max(budget,1)*25)
def _time_score(time,limit):
    if limit is None or limit<=0: return 65.0 if time<=0 else 60.0
    return _clamp(100-max(0,time-limit)/max(limit,1)*100-time/max(limit,1)*20)
def _risk_score(opt,scenario):
    risk=number(opt.get("risk"),45); probability=number(opt.get("success_probability"),65)
    reversibility=20 if opt.get("reversible",True) else 0
    tolerance=number(scenario.get("risk_tolerance"),50)
    return _clamp(70+(probability-65)*.55-(risk-45)*.55+reversibility+(tolerance-50)*.15)
def analyze_decision(decision:dict,scenario:dict|None=None)->list[dict]:
    scenario=scenario or {}; options=decision.get("options",[]) if isinstance(decision,dict) else []
    budget=scenario.get("budget",decision.get("budget_limit")); limit=scenario.get("time",decision.get("time_limit"))
    weights=decision.get("weights",{"practical":40,"risk":30,"growth":30})
    w={k:max(0,number(weights.get(k),default)) for k,default in [("practical",40),("risk",30),("growth",30)]}
    total=sum(w.values()) or 100; w={k:v/total for k,v in w.items()}
    gi=number(scenario.get("growth"),30); output=[]
    for opt in options:
        cost=number(opt.get("cost")); time=number(opt.get("time"))
        cost*=1+number(scenario.get("cost_overrun"))/100; time*=1+number(scenario.get("time_delay"))/100
        practical=_clamp(_cost_score(cost,budget)*.48+_time_score(time,limit)*.32+(75 if opt.get("description") else 55)*.20)
        risk=_risk_score(opt,scenario); growth=_clamp(number(opt.get("learning"),65)*.45+number(opt.get("growth",65))*.55)
        eg=w["growth"]*(.5+gi/100); ep=w["practical"]*(1.25-gi/200); denom=eg+ep+w["risk"] or 1
        overall=_clamp((practical*ep+risk*w["risk"]+growth*eg)/denom)
        violations=[]
        if decision.get("budget_limit") and cost>number(decision["budget_limit"]): violations.append(f"Estimated cost {cost:g} exceeds stated budget {decision['budget_limit']:g}.")
        if decision.get("time_limit") and time>number(decision["time_limit"]): violations.append(f"Estimated time {time:g} exceeds stated time limit {decision['time_limit']:g}.")
        uncertainties=[]
        for key,label in [("benefit","Expected benefit"),("concern","Major concern"),("description","Option details")]:
            if not opt.get(key): uncertainties.append(f"{label} is not specified.")
        lenses={
        "practical":{"label":"Practical Fit","score":practical,"explanation":f"Uses the estimated cost ({cost:g}) and time ({time:g}) against current limits. Missing limits use neutral defaults.","advantages":[f"Estimated cost: {cost:g}",f"Estimated time: {time:g}"],"concerns":[opt.get("practical_concern") or "Feasibility depends on estimate accuracy"],"improvement":"Reduce scope or validate cost/time estimates."},
        "risk":{"label":"Risk & Resilience","score":risk,"explanation":f"Combines the model-suggested risk rating, success estimate, reversibility, and risk-tolerance setting. These are estimates, not measured probabilities.","advantages":[opt.get("risk_advantage") or "A bounded trial may limit downside"],"concerns":[opt.get("concern") or "Primary concern needs investigation"],"improvement":"Define a fallback and test the riskiest assumption."},
        "growth":{"label":"Future Growth","score":growth,"explanation":"Combines illustrative learning and future-usefulness ratings proposed by the local model.","advantages":[opt.get("benefit") or "Benefit needs validation"],"concerns":[opt.get("growth_concern") or "Long-term usefulness is uncertain"],"improvement":"Set a measurable learning or opportunity milestone."}}
        output.append({"name":str(opt.get("name","Unnamed option")),"description":str(opt.get("description","")),"cost":cost,"time":time,"benefit":str(opt.get("benefit","")),"concern":str(opt.get("concern","")),"overall":round(overall,2),"lenses":lenses,"violations":violations,"uncertainties":uncertainties,"pros":opt.get("pros") or [str(opt.get("benefit") or "Benefit needs validation")],"cons":opt.get("cons") or [str(opt.get("concern") or "Concern needs investigation")]})
    output.sort(key=lambda x:x["overall"],reverse=True)
    return output
