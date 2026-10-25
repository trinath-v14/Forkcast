from forkcast.validation import validate_decision
def test_invalid_input(): assert len(validate_decision({}))>=3
def test_valid_input(): assert validate_decision({"title":"A","description":"B","options":[{"name":"one"},{"name":"two"}]})==[]
def test_negative_limit():
 d={"title":"A","description":"B","options":[{"name":"one"},{"name":"two"}],"budget_limit":-1}; assert any("negative" in x for x in validate_decision(d))
