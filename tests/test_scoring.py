from forkcast.scoring import analyze_decision
from forkcast.recommendations import build_recommendation
def decision():
 return {"title":"test","description":"desc","budget_limit":100,"time_limit":5,"weights":{"practical":40,"risk":30,"growth":30},"options":[{"name":"A","description":"d","cost":10,"time":2,"benefit":"learn","concern":"time","learning":90,"growth":80,"risk":20,"success_probability":80,"reversible":True},{"name":"B","description":"d","cost":200,"time":9,"benefit":"other","concern":"cost","learning":50,"growth":50,"risk":80,"success_probability":40,"reversible":False}]}
def test_scores_bounded_and_ranked():
 r=analyze_decision(decision()); assert len(r)==2 and r[0]["overall"]>=r[1]["overall"]; assert all(0<=x["overall"]<=100 for x in r)
def test_zero_weights_fall_back_safely():
 d=decision(); d["weights"]={"practical":0,"risk":0,"growth":0}; assert len(analyze_decision(d))==2
def test_constraint_violation():
 r=analyze_decision(decision()); assert any("exceeds" in x for x in r[1]["violations"])
def test_missing_optional_fields():
 d=decision(); d["options"][0].pop("benefit"); d["options"][0].pop("concern"); assert analyze_decision(d)[0]["uncertainties"]
def test_recommendation():
 r=analyze_decision(decision()); assert build_recommendation(decision(),r)["winner"]==r[0]["name"]
def test_ties_handled():
 d=decision(); d["options"][1]=dict(d["options"][0],name="A twin"); assert len(analyze_decision(d))==2
