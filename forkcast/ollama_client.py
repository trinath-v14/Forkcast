"""Minimal Ollama client using the Python standard library only."""
from __future__ import annotations
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from socket import timeout as SocketTimeout

class OllamaError(RuntimeError):
    """A user-safe local model connectivity or response error."""

SYSTEM_PROMPT = """You are Forkcast, a careful decision-analysis assistant. Return ONLY valid JSON, no markdown.
Generate useful alternatives and qualitative analysis from the user's decision and optional context. Do not claim certainty. Do not invent facts about the user. Mark assumptions explicitly. First, identify the exact subject/domain and the user's intended decision from their words. Keep every option tightly grounded in that subject. Do NOT switch to a generic career, productivity, or business framework unless that is actually what the user asked about. If the input is ambiguous, state a brief assumption and still provide useful, subject-specific paths. The description must restate the user's real decision, not a generic paraphrase. Generate exactly THREE meaningfully different options/perspectives, not three rewordings of the same idea. Each option must name a concrete path relevant to the user's decision and explain why it fits this exact question. Do not invent personal facts or silently assume a country, deadline, budget, or timeframe. Return this schema:
{
 "description":"brief restatement",
 "priorities":["priority"],
 "horizon":"Immediate|Short term|Medium term|Long term",
 "budget_limit":null,
 "time_limit":null,
 "constraints":"known constraints or 'Not specified'",
 "weights":{"practical":40,"risk":30,"growth":30},
 "assumptions":["assumption to validate"],
 "options":[
  {"name":"option name","description":"what it means","cost":0,"time":0,
   "benefit":"expected benefit","concern":"main concern",
   "pros":["pro"],"cons":["con"],
   "learning":70,"growth":70,"risk":40,"success_probability":60,
   "reversible":true,"practical_concern":"feasibility concern",
   "risk_advantage":"resilience advantage","growth_concern":"growth caveat",
   "switch_condition":"condition that makes another option better"}
 ],
 "alternative_futures":[
  {"favorable":"plausible favorable outcome","downside":"plausible downside",
   "uncertainty":"major unknown","early_indicator":"signal it is working",
   "warning_sign":"early warning","fallback":"fallback plan"}
 ],
 "recommended_next_step":"one practical next step",
 "verify_before_committing":"facts to verify",
 "low_commitment_test":"small test",
 "reassess_if":"when to reassess"
}
For unknown cost/time use 0 and mention missing estimates in assumptions. Scores/risk/probability are illustrative estimates on 0-100 scales. Keep costs in a consistent unit if user supplied one; otherwise use 0 and explain in assumptions. Return between two and five options. Each alternative_futures entry should correspond to the option at the same index. Keep recommendations proportionate, practical, and clear about uncertainty."""

def generate_analysis(title: str, context: str, config: dict, timeout: int=120) -> dict:
    base=str(config.get("url","http://localhost:11434")).rstrip("/")
    model=str(config.get("model","llama3.2")).strip()
    if not model: raise OllamaError("Enter an Ollama model name in the sidebar settings.")
    payload={"model":model,"stream":False,"format":"json","messages":[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":f"User's exact decision: {title}\nOptional context: {context or 'Not provided'}\nBefore drafting, infer the core subject and intent from the exact decision text. Make all three options specific to that subject. Avoid generic filler. Return the complete JSON schema."}],"options":{"temperature":0.3}}
    req=Request(base+"/api/chat",data=json.dumps(payload).encode("utf-8"),headers={"Content-Type":"application/json"},method="POST")
    try:
        with urlopen(req,timeout=timeout) as response:
            body=json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        detail=e.read().decode("utf-8",errors="replace")[:300]
        if e.code==404:
            raise OllamaError(f"Ollama returned 404. Check that the model '{model}' is installed (`ollama pull {model}`) and that the configured URL is correct.") from e
        raise OllamaError(f"Ollama returned HTTP {e.code}: {detail or 'No details supplied.'}") from e
    except (URLError,ConnectionError,SocketTimeout,TimeoutError,OSError) as e:
        raise OllamaError(f"Cannot reach Ollama at {base}. Start the Ollama application/service, verify the URL, and confirm a model is installed. Details: {e}") from e
    try:
        content=body["message"]["content"]
        data=json.loads(content)
    except (KeyError,TypeError,ValueError) as e:
        raise OllamaError("The selected model did not return valid JSON. Try a model that supports structured JSON output, or retry the analysis.") from e
    options=data.get("options")
    if not isinstance(options,list) or len(options) < 2:
        raise OllamaError("The model response did not contain 2–5 valid options. Try again with a more specific decision sentence.")
    if len(options) > 3:
        options = options[:3]
    for i,opt in enumerate(options,1):
        if not isinstance(opt,dict) or not str(opt.get("name","")).strip():
            raise OllamaError(f"The model response has an invalid name for option {i}. Try again.")
        opt.setdefault("pros",[]); opt.setdefault("cons",[])
        for key,default in [("cost",0),("time",0),("learning",65),("growth",65),("risk",45),("success_probability",65)]:
            try: opt[key]=float(opt.get(key,default) or 0)
            except (ValueError,TypeError): opt[key]=float(default)
        opt["reversible"]=bool(opt.get("reversible",True))
    data["options"]=options
    data.setdefault("priorities",["Practicality","Risk","Long-term usefulness"])
    data.setdefault("weights",{"practical":40,"risk":30,"growth":30})
    data.setdefault("assumptions",["Generated estimates should be verified."])
    data.setdefault("alternative_futures",[])
    for key in ("budget_limit", "time_limit"):
        value=data.get(key)
        if value is not None:
            try:
                value=float(value)
                data[key]=value if value >= 0 else None
            except (TypeError, ValueError):
                data[key]=None
    if not isinstance(data.get("weights"), dict):
        data["weights"]={"practical":40,"risk":30,"growth":30}
    else:
        for key, default in (("practical",40),("risk",30),("growth",30)):
            try:
                data["weights"][key]=max(0.0,min(100.0,float(data["weights"].get(key,default))))
            except (TypeError,ValueError):
                data["weights"][key]=default
    for key in ("assumptions","priorities"):
        if not isinstance(data.get(key),list):
            data[key]=[]
        data[key]=[str(item)[:500] for item in data[key][:12]]
    if not isinstance(data.get("alternative_futures"),list):
        data["alternative_futures"]=[]
    data["alternative_futures"]=[
        item for item in data["alternative_futures"][:5] if isinstance(item,dict)
    ]
    data["alternative_futures"] += [{}] * (len(options)-len(data["alternative_futures"]))
    return data
