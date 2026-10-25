import json
from unittest.mock import patch
from urllib.error import URLError, HTTPError
import pytest
from forkcast.ollama_client import generate_analysis, OllamaError

def config(): return {"url":"http://localhost:11434","model":"llama3.2"}
def mock_response(data):
    class R:
        def __enter__(self): return self
        def __exit__(self,*args): pass
        def read(self): return json.dumps(data).encode()
    return R()
def valid_payload():
    return {"message":{"content":json.dumps({"options":[{"name":"A"},{"name":"B"}],"assumptions":[]})}}
def test_generate_analysis_parses_json_and_defaults_fields():
    with patch("forkcast.ollama_client.urlopen",return_value=mock_response(valid_payload())):
        d=generate_analysis("test decision","",config())
    assert len(d["options"])==2 and d["options"][0]["cost"]==0
    assert "weights" in d
def test_connection_error_is_helpful():
    with patch("forkcast.ollama_client.urlopen",side_effect=URLError("offline")):
        with pytest.raises(OllamaError,match="Cannot reach Ollama"): generate_analysis("test","",config())
def test_invalid_json_is_handled():
    with patch("forkcast.ollama_client.urlopen",return_value=mock_response({"message":{"content":"not json"}})):
        with pytest.raises(OllamaError,match="valid JSON"): generate_analysis("test","",config())
def test_missing_options_rejected():
    with patch("forkcast.ollama_client.urlopen",return_value=mock_response({"message":{"content":json.dumps({"options":[{"name":"only"}]})}})):
        with pytest.raises(OllamaError,match="2–5 valid options"): generate_analysis("test","",config())
