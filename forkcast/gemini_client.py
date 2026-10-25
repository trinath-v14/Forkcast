"""Gemini REST API client using Python stdlib; API key stays in session memory."""
from __future__ import annotations
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from socket import timeout as SocketTimeout
from .ollama_client import SYSTEM_PROMPT, OllamaError

def generate_analysis(title: str, context: str, config: dict, timeout: int=90) -> dict:
    api_key=str(config.get("api_key", "")).strip()
    model=str(config.get("model", "gemini-2.5-flash")).strip() or "gemini-2.5-flash"
    if not api_key:
        raise OllamaError("Enter your Gemini API key in the Gemini connection settings. The key is used only for this session and is not saved to the project files.")
    prompt=f"{SYSTEM_PROMPT}\n\nUser's exact decision: {title}\nOptional context: {context or 'Not provided'}\nInfer the core subject and intent from the exact wording. Make all three options specific to that subject. Return the complete JSON schema only."
    payload={"system_instruction":{"parts":[{"text":"You are Forkcast. Return valid JSON only, matching the requested schema. Be specific to the user's decision."}]},"contents":[{"role":"user","parts":[{"text":prompt}]}],"generationConfig":{"responseMimeType":"application/json","temperature":0.3}}
    url=f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    req=Request(url,data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"},method="POST")
    try:
        with urlopen(req,timeout=timeout) as response: body=json.loads(response.read().decode())
    except HTTPError as e:
        detail=e.read().decode(errors="replace")[:500]
        if e.code in (400,401,403): raise OllamaError(f"Gemini API rejected the request (HTTP {e.code}). Check the API key, enabled Gemini API, model name, and quota. Details: {detail}") from e
        raise OllamaError(f"Gemini API returned HTTP {e.code}: {detail}") from e
    except (URLError,ConnectionError,SocketTimeout,TimeoutError,OSError) as e:
        raise OllamaError(f"Could not reach Gemini API. Check your internet connection. Details: {e}") from e
    try:
        content=body["candidates"][0]["content"]["parts"][0]["text"]
        data=json.loads(content)
    except (KeyError,IndexError,TypeError,ValueError) as e:
        raise OllamaError("Gemini did not return the expected JSON analysis. Try again.") from e
    options=data.get("options")
    if not isinstance(options,list) or len(options)<3: raise OllamaError("Gemini returned fewer than three usable options. Please retry the analysis.")
    data["options"]=options[:3]
    for i,opt in enumerate(data["options"],1):
        if not isinstance(opt,dict) or not str(opt.get("name","")).strip(): raise OllamaError(f"Gemini returned an invalid option {i}. Please retry.")
        opt.setdefault("pros",[]); opt.setdefault("cons",[])
        for k,default in [("cost",0),("time",0),("learning",65),("growth",65),("risk",45),("success_probability",65)]:
            try: opt[k]=float(opt.get(k,default) or 0)
            except (ValueError,TypeError): opt[k]=float(default)
        opt["reversible"]=bool(opt.get("reversible",True))
    data.setdefault("description",title); data.setdefault("priorities",["Practicality","Risk","Long-term usefulness"])
    data.setdefault("weights",{"practical":40,"risk":30,"growth":30}); data.setdefault("assumptions",["Generated estimates should be verified."])
    if not isinstance(data.get("weights"),dict): data["weights"]={"practical":40,"risk":30,"growth":30}
    for k in ("budget_limit","time_limit"):
        if data.get(k) is not None:
            try: data[k]=max(0,float(data[k]))
            except (TypeError,ValueError): data[k]=None
    for k in ("assumptions","priorities"):
        if not isinstance(data.get(k),list): data[k]=[]
        data[k]=[str(x)[:500] for x in data[k][:12]]
    futures=data.get("alternative_futures",[])
    if not isinstance(futures,list): futures=[]
    data["alternative_futures"]=(futures[:3]+[{}]*3)[:3]
    return data
