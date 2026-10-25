from forkcast.simulation import apply_scenario,reset_scenario
def test_scenario_does_not_mutate_original():
 d={"options":[{"name":"A"}]}; out=apply_scenario(d,{"budget":500}); assert "scenario_assumptions" not in d and out["scenario_assumptions"]["budget"]==500
def test_reset_returns_copy():
 d={"title":"x"}; out,sc=reset_scenario(d); out["title"]="y"; assert d["title"]=="x" and sc["growth"]==30
