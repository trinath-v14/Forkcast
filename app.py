from __future__ import annotations
import json
import streamlit as st
import pandas as pd
import plotly.express as px
from forkcast.scenarios import SAMPLE_SCENARIOS
from forkcast.validation import validate_decision
from forkcast.scoring import analyze_decision
from forkcast.simulation import apply_scenario
from forkcast.recommendations import build_recommendation
from forkcast.gemini_client import generate_analysis, OllamaError
from components.visualizations import render_path_map

st.set_page_config(page_title="Forkcast — Decision Intelligence", page_icon="⑂", layout="wide", initial_sidebar_state="collapsed")
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --bg:#090b0a; --panel:#121613; --panel2:#171d18; --line:#2b342c; --silver:#aeb8af; --white:#f4f5ef; --lime:#d2ff4d; --muted:#8e9a90; }
.stApp { background:radial-gradient(ellipse at 76% 0%, rgba(159,197,87,.08), transparent 31%), var(--bg); color:var(--white); font-family:'Manrope',sans-serif; }
.block-container { max-width:1320px; padding-top:1.25rem; padding-bottom:4rem; }
[data-testid="stSidebar"], [data-testid="collapsedControl"] {display:none !important;}
header[data-testid="stHeader"] {background:rgba(9,11,10,.7);}
h1,h2,h3,h4 { letter-spacing:-.045em !important; color:var(--white) !important; }
h1 {font-weight:800 !important;}
p, li {line-height:1.68;}
.eyebrow {font-family:'DM Mono',monospace;font-size:.68rem;letter-spacing:.16em;color:var(--lime);text-transform:uppercase;}
.brandbar {display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:.65rem 0 1.1rem;border-bottom:1px solid var(--line);margin-bottom:1rem;}
.brandmark {display:flex;align-items:center;gap:.72rem;font-size:1.03rem;font-weight:800;letter-spacing:.16em;color:var(--white);}
.brandglyph {display:inline-flex;width:34px;height:34px;align-items:center;justify-content:center;border:1px solid #53633a;border-radius:11px;background:linear-gradient(135deg,rgba(210,255,77,.18),rgba(210,255,77,.02));color:var(--lime);font-size:1.15rem;}
.statuspill {display:inline-flex;align-items:center;gap:.45rem;padding:.42rem .7rem;border:1px solid var(--line);border-radius:999px;color:#b6c1b6;font-size:.73rem;letter-spacing:.04em;}
.statusdot {display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--lime);box-shadow:0 0 10px rgba(210,255,77,.6);}
.hero {position:relative;overflow:hidden;padding:3.2rem 2.5rem 2.4rem;border:1px solid #303a30;border-radius:26px;background:linear-gradient(115deg,rgba(24,31,25,.96),rgba(12,15,13,.96) 58%,rgba(24,32,18,.72));margin:1.4rem 0 1.6rem;box-shadow:0 24px 80px rgba(0,0,0,.22);}
.hero:after {content:'';position:absolute;width:390px;height:390px;right:-90px;top:-175px;border:1px solid rgba(210,255,77,.16);border-radius:50%;box-shadow:0 0 0 35px rgba(210,255,77,.025),0 0 0 75px rgba(210,255,77,.018),inset 0 0 70px rgba(210,255,77,.035);pointer-events:none;}
.hero-title {font-size:clamp(2.7rem,6.3vw,5.4rem);font-weight:800;line-height:.98;letter-spacing:-.075em;margin:.75rem 0 1.05rem;max-width:800px;}
.hero-copy {max-width:620px;color:#b9c2b9;font-size:1rem;line-height:1.8;}
.panel {background:linear-gradient(145deg,rgba(255,255,255,.045),rgba(255,255,255,.012));border:1px solid var(--line);border-radius:19px;padding:1.25rem 1.35rem;margin:.35rem 0 1rem;transition:border-color .2s ease,transform .2s ease,background .2s ease;}
.panel:hover {border-color:#526342;background:linear-gradient(145deg,rgba(210,255,77,.055),rgba(255,255,255,.012));transform:translateY(-2px);}
.entryshell {padding:1.45rem;border:1px solid #344033;border-radius:22px;background:linear-gradient(145deg,#151b16,#0d100e);box-shadow:0 20px 60px rgba(0,0,0,.22);}
.muted {color:var(--muted);font-size:.88rem;}
.sectionhead {display:flex;align-items:center;justify-content:space-between;gap:1rem;margin:.5rem 0 1rem;}
div.stButton > button[kind="primary"], div.stFormSubmitButton > button[kind="primary"] {background:var(--lime);color:#11150c;border:0;font-weight:800;border-radius:12px;min-height:3rem;box-shadow:0 6px 24px rgba(210,255,77,.10);transition:transform .18s ease,box-shadow .18s ease;}
div.stButton > button[kind="primary"]:hover, div.stFormSubmitButton > button[kind="primary"]:hover {background:#ddff79;color:#11150c;transform:translateY(-1px);box-shadow:0 10px 30px rgba(210,255,77,.17);}
div.stButton > button {border-radius:12px;border:1px solid #3c483d;background:#151a16;color:#e8eee6;min-height:2.65rem;transition:border-color .18s ease,background .18s ease;}
div.stButton > button:hover {border-color:#8fa75d;background:#1b241b;color:white;}
div[data-testid="stMetric"] {background:#141915;border:1px solid #303a30;padding:1rem;border-radius:15px;}
[data-testid="stProgressBar"] > div > div {background:var(--lime) !important;}
hr {border-color:var(--line);}
label, .stMarkdown p {color:#dbe2da;}
[data-testid="stWidgetLabel"] p {color:#c8d1c8;}
input, textarea, [data-baseweb="select"] > div {background:#0d110e !important;border-color:#344034 !important;border-radius:12px !important;color:#f4f5ef !important;}
.stTextInput input, .stTextArea textarea {padding:.9rem 1rem;}
[data-testid="stRadio"] > div {gap:.38rem;}
[data-testid="stRadio"] label {border:1px solid #293229;border-radius:999px;padding:.42rem .82rem;background:#101411;transition:all .18s ease;}
[data-testid="stRadio"] label:has(input:checked) {background:#d2ff4d !important;border-color:#d2ff4d !important;color:#11150c !important;}
[data-testid="stRadio"] label:has(input:checked) p {color:#11150c !important;font-weight:800;}
[data-testid="stDataFrame"] {border:1px solid var(--line);border-radius:14px;overflow:hidden;}
[data-testid="stExpander"] {border:1px solid var(--line);border-radius:14px;background:rgba(255,255,255,.018);}
[data-testid="stAlert"] {border-radius:14px;}
[data-testid="stPlotlyChart"] {border:1px solid #283128;border-radius:16px;padding:.3rem;background:rgba(255,255,255,.01);}
@media (max-width:700px) {.block-container{padding-top:.7rem}.hero{padding:2rem 1.25rem}.hero-title{font-size:2.7rem}.brandbar{align-items:flex-start}.statuspill{font-size:.65rem}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)
DEFAULT_SCENARIO={"budget":1000.0,"time":10.0,"growth":30,"risk_tolerance":50,"cost_overrun":0,"time_delay":0}
PAGES=["Home","Decision Entry","Three-Lens Analysis","Options Comparison","What-If Simulator","Alternative Futures","Next Move","Decision History"]
NAV_LABELS={"Home":"Overview","Decision Entry":"New decision","Three-Lens Analysis":"Three lenses","Options Comparison":"Compare","What-If Simulator":"What-if","Alternative Futures":"Futures","Next Move":"Recommendation","Decision History":"History"}
for key,default in [("decision",None),("saved",[]),("original",None),("view","Home"),("scenario",dict(DEFAULT_SCENARIO)),("ollama_status",None),("ollama_config",{"api_key":"","model":"gemini-2.5-flash"})]:
    if key not in st.session_state: st.session_state[key]=default

# A compact top navigation replaces the old left-hand sidebar entirely.
head_left, head_right = st.columns([1.25, 1], vertical_alignment="center")
with head_left:
    st.markdown('<div class="brandmark"><span class="brandglyph">⑂</span> FORKCAST <span style="color:#d2ff4d">/</span> <span style="font-size:.68rem;letter-spacing:.09em;color:#8e9a90;font-weight:500">DECISION INTELLIGENCE</span></div>', unsafe_allow_html=True)
with head_right:
    active_label = "AI READY" if st.session_state.get("decision", None) else "GEMINI AI"
    st.markdown(f'<div style="display:flex;justify-content:flex-end"><span class="statuspill"><span class="statusdot"></span>{active_label}</span></div>', unsafe_allow_html=True)
st.markdown('<div style="height:1px;background:linear-gradient(90deg,#354033,rgba(53,64,51,.1));margin:.85rem 0 1rem"></div>',unsafe_allow_html=True)
current_view=st.session_state.view if st.session_state.view in PAGES else "Home"
if "top_navigation" not in st.session_state:
    st.session_state.top_navigation = current_view

def _sync_navigation():
    st.session_state.view = st.session_state.top_navigation

nav=st.radio("Main navigation",PAGES,format_func=lambda x:NAV_LABELS[x],horizontal=True,index=PAGES.index(current_view),label_visibility="collapsed",key="top_navigation",on_change=_sync_navigation)
page=st.session_state.view
with st.expander("Gemini API settings", expanded=False):
    st.caption("Use your Google Gemini API key. It is held in this app session only; do not share it in chat or commit it to GitHub.")
    gemini_key=st.text_input("Gemini API key", type="password", value=st.session_state.ollama_config.get("api_key", ""), help="Get a key from Google AI Studio.")
    gemini_model=st.text_input("Gemini model", value=st.session_state.ollama_config.get("model", "gemini-2.5-flash"), help="Default: gemini-2.5-flash")
    st.session_state.ollama_config={"api_key":gemini_key.strip(),"model":gemini_model.strip() or "gemini-2.5-flash"}

def load_sample(name):
    d=json.loads(json.dumps(SAMPLE_SCENARIOS[name]))
    d["generated_by"]="Illustrative built-in sample"
    d["analysis_meta"]={"mode":"sample","notice":"Illustrative sample; no Ollama generation was used."}
    st.session_state.decision=d; st.session_state.original=json.loads(json.dumps(d))
    st.session_state.scenario={"budget":float(d.get("budget_limit") or 1000),"time":float(d.get("time_limit") or 10),"growth":30,"risk_tolerance":50,"cost_overrun":0,"time_delay":0}
    st.session_state.view="Three-Lens Analysis"

def set_decision(d):
    errors=validate_decision(d)
    if errors:
        for e in errors: st.error(e)
        return False
    st.session_state.decision=d; st.session_state.original=json.loads(json.dumps(d))
    st.session_state.scenario={"budget":float(d.get("budget_limit") or 1000),"time":float(d.get("time_limit") or 10),"growth":30,"risk_tolerance":50,"cost_overrun":0,"time_delay":0}
    st.session_state.view="Three-Lens Analysis"
    return True

def render_entry():
    st.markdown('<div class="eyebrow">START HERE / ONE INPUT</div>',unsafe_allow_html=True)
    st.markdown('<div style="max-width:780px;margin:.7rem 0 1.2rem"><div class="hero-title" style="font-size:clamp(2.4rem,5vw,4.2rem)">A decision is a starting point.<br><span style="color:#d2ff4d">Not a questionnaire.</span></div><div class="hero-copy">Tell Forkcast what you are deciding. Your local AI will generate the possible paths, explore three perspectives, and help you see the trade-offs.</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="entryshell">',unsafe_allow_html=True)
    with st.form("decision_prompt_form"):
        st.markdown('<div class="eyebrow">YOUR DECISION</div>',unsafe_allow_html=True)
        title=st.text_area("What are you trying to decide?",placeholder="Should I focus on C++ or Python first?",height=105,label_visibility="collapsed",max_chars=700)
        with st.expander("Add context (optional)"):
            context=st.text_area("Anything else Forkcast should know?",placeholder="Your goals, constraints, or situation — only if it helps.",height=100,label_visibility="collapsed",max_chars=1800)
        st.markdown('<div class="muted">No mandatory dates, budgets, locations, or setup questions. Forkcast will make reasonable assumptions and call them out.</div>',unsafe_allow_html=True)
        st.write("")
        submit=st.form_submit_button("✦  Reveal my options",type="primary",use_container_width=True)
    st.markdown('</div>',unsafe_allow_html=True)
    if submit:
        if not title.strip():
            st.error("Add your decision above to begin.")
        else:
            with st.spinner("Exploring possible paths with Gemini…"):
                try:
                    generated=generate_analysis(title.strip(),context.strip(),st.session_state.ollama_config)
                    d=generated
                    d["title"]=title.strip()
                    d["description"]=generated.get("description") or title.strip()
                    d["context"]=context.strip()
                    d["generated_by"]="Google Gemini"
                    d["analysis_meta"]={"mode":"gemini","model":st.session_state.ollama_config["model"],"notice":"Qualitative analysis is generated by Google Gemini. Numeric rankings are calculated separately by deterministic Python code."}
                    if set_decision(d):
                        st.success("Your decision paths are ready.")
                        st.rerun()
                except OllamaError as e:
                    st.error(str(e))
                    st.info("Check your Gemini API key, model name, internet connection, and API quota. You can also load a built-in sample from Overview to preview Forkcast.")
                except Exception as e:
                    st.error(f"Forkcast could not finish this analysis: {type(e).__name__}: {e}")
                    st.info("Try a smaller, clearer decision statement, or check that your Ollama model is running and has enough memory. You can still open any sample to test the interface.")

if page=="Home":
    st.markdown('<div class="hero"><div class="eyebrow">A CALMER WAY TO MAKE HARD CHOICES</div><div class="hero-title">See the paths.<br>Understand the trade-offs<span style="color:#d2ff4d">.</span></div><div class="hero-copy">One decision in. A clearer view of what could happen next. Forkcast uses Gemini AI to explore alternatives, stress-test assumptions, and turn uncertainty into a practical next move.</div></div>',unsafe_allow_html=True)
    left,right=st.columns([1.08,.92],gap="large",vertical_alignment="center")
    with left:
        st.markdown('<div class="eyebrow">YOUR NEXT MOVE STARTS HERE</div>',unsafe_allow_html=True)
        st.markdown("### No forms to fill. No options to invent.")
        st.write("Enter your decision once. Forkcast builds the alternatives and compares them through practical fit, risk and resilience, and future growth.")
        if st.button("Start with my decision  ↗",type="primary",use_container_width=True):
            st.session_state.view="Decision Entry"; st.rerun()
        st.markdown('<div class="muted" style="margin-top:.8rem">Powered by Google Gemini · Transparent Python scoring</div>',unsafe_allow_html=True)
    with right:
        st.markdown('<div class="panel"><div class="eyebrow">THE FORKCAST METHOD</div><h3 style="margin-top:.8rem">From question to clarity.</h3><div style="display:flex;gap:1rem;padding:.75rem 0;border-bottom:1px solid #2b342c"><span style="color:#d2ff4d;font-family:monospace">01</span><div><b>Reveal possibilities</b><div class="muted">AI generates distinct options and assumptions.</div></div></div><div style="display:flex;gap:1rem;padding:.75rem 0;border-bottom:1px solid #2b342c"><span style="color:#d2ff4d;font-family:monospace">02</span><div><b>Explore three lenses</b><div class="muted">Practical fit, risk, and future growth.</div></div></div><div style="display:flex;gap:1rem;padding:.75rem 0;border-bottom:1px solid #2b342c"><span style="color:#d2ff4d;font-family:monospace">03</span><div><b>Test what-if scenarios</b><div class="muted">See how changed assumptions affect rankings.</div></div></div><div style="display:flex;gap:1rem;padding:.75rem 0"><span style="color:#d2ff4d;font-family:monospace">04</span><div><b>Choose a next move</b><div class="muted">A recommendation with reasons and caveats.</div></div></div></div>',unsafe_allow_html=True)
    st.markdown('<div class="sectionhead"><div><div class="eyebrow">TAKE A LOOK AROUND</div><h3 style="margin:.3rem 0">Explore a sample decision</h3></div><div class="muted">Demo mode · no AI connection required</div></div>',unsafe_allow_html=True)
    cols=st.columns(3,gap="medium")
    for col,(name,data) in zip(cols,SAMPLE_SCENARIOS.items()):
        with col:
            st.markdown(f'<div class="panel" style="min-height:160px"><div class="eyebrow">ILLUSTRATIVE SCENARIO</div><h4 style="margin:.7rem 0">{data["title"]}</h4><p class="muted">{data["description"]}</p></div>',unsafe_allow_html=True)
            if st.button("Explore sample ↗",key=f"sample_{name}",use_container_width=True):
                load_sample(name); st.rerun()
elif page=="Decision Entry":
    render_entry()
elif page=="Decision History":
    st.markdown('<div class="eyebrow">SESSION ARCHIVE</div>',unsafe_allow_html=True); st.title("Decision history")
    st.caption("History is stored in this session only; it may not survive a new session or server restart.")
    if st.session_state.decision and st.button("Save current decision",type="primary"):
        st.session_state.saved.append(json.loads(json.dumps(st.session_state.decision))); st.success("Saved to this session.")
    for i,d in enumerate(reversed(st.session_state.saved)):
        with st.container(border=True):
            st.markdown(f"**{d.get('title','Untitled')}**")
            st.caption(d.get("description",""))
            if st.button("Load",key=f"history_{i}"):
                st.session_state.decision=json.loads(json.dumps(d)); st.session_state.original=json.loads(json.dumps(d)); st.session_state.view="Three-Lens Analysis"; st.rerun()
    if not st.session_state.saved: st.info("No saved decisions yet.")
elif not st.session_state.decision:
    st.markdown('<div class="hero"><div class="eyebrow">YOUR WORKSPACE</div><div class="hero-title" style="font-size:3.4rem">Every path starts<br>with one question.</div><div class="hero-copy">Start a new decision or explore a sample scenario.</div></div>',unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        if st.button("Enter a decision →",type="primary",use_container_width=True): st.session_state.view="Decision Entry"; st.rerun()
    with c2:
        sample=st.selectbox("Sample",list(SAMPLE_SCENARIOS),format_func=lambda k:SAMPLE_SCENARIOS[k]["title"])
        if st.button("Load selected sample",use_container_width=True): load_sample(sample); st.rerun()
else:
    d=st.session_state.decision
    scenario=st.session_state.scenario
    scored_decision=apply_scenario(d,scenario)
    results=analyze_decision(scored_decision,scenario)
    rec=build_recommendation(scored_decision,results)
    meta=d.get("analysis_meta",{})
    st.markdown(f'<div class="eyebrow">YOUR DECISION / {NAV_LABELS.get(page,page).upper()}</div>',unsafe_allow_html=True)
    st.title(d.get("title","Untitled"))
    st.caption(d.get("description",""))
    if meta.get("notice"): st.info(meta["notice"])
    if page=="Three-Lens Analysis":
        st.markdown("### Three perspectives. One clearer picture.")
        weights={}
        cols=st.columns(3)
        for col,(key,label,default) in zip(cols,[("practical","Practical Fit",40),("risk","Risk & Resilience",30),("growth","Future Growth",30)]):
            weights[key]=col.slider(label+" weight",0,100,int(d.get("weights",{}).get(key,default)),5,key=f"weight_{key}")
        d["weights"]=weights
        results=analyze_decision(d,scenario)
        for option in results:
            with st.container(border=True):
                st.markdown(f"#### {option['name']}")
                metrics=st.columns(4)
                metrics[0].metric("Overall fit",f"{option['overall']:.0f}/100")
                metrics[1].metric("Practical",f"{option['lenses']['practical']['score']:.0f}")
                metrics[2].metric("Risk & resilience",f"{option['lenses']['risk']['score']:.0f}")
                metrics[3].metric("Future growth",f"{option['lenses']['growth']['score']:.0f}")
                st.write(option.get("description",""))
                for key in ("practical","risk","growth"):
                    lens=option["lenses"][key]
                    st.markdown(f"**{lens['label']}** · {lens['score']:.0f}/100")
                    st.progress(int(lens["score"]))
                    st.write(lens["explanation"])
                    st.caption("Advantages: "+", ".join(lens["advantages"])+" · Concerns: "+", ".join(lens["concerns"]))
                    st.caption("Could improve if: "+lens["improvement"])
                st.markdown("**Pros:** "+", ".join(option["pros"]))
                st.markdown("**Cons:** "+", ".join(option["cons"]))
                if option["violations"]: st.error("Constraint flags: "+"; ".join(option["violations"]))
                if option["uncertainties"]: st.info("Unknowns: "+"; ".join(option["uncertainties"]))
    elif page=="Options Comparison":
        df=pd.DataFrame([{"Option":r["name"],"Overall":r["overall"],"Practical Fit":r["lenses"]["practical"]["score"],"Risk & Resilience":r["lenses"]["risk"]["score"],"Future Growth":r["lenses"]["growth"]["score"],"Cost":r["cost"],"Time":r["time"],"Constraint flags":len(r["violations"])} for r in results])
        st.markdown("### Side-by-side scorecard"); st.dataframe(df,hide_index=True,use_container_width=True)
        chart=px.bar(df,x="Option",y=["Practical Fit","Risk & Resilience","Future Growth"],barmode="group",range_y=[0,100],template="plotly_dark",color_discrete_sequence=["#C8FF32","#BFC5C0","#6f7770"])
        chart.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",legend_title_text="",margin=dict(l=5,r=5,t=25,b=5))
        st.plotly_chart(chart,use_container_width=True)
        for r in results:
            with st.expander(f"{r['name']} — pros & cons"):
                st.write("**Pros:** "+", ".join(r["pros"])); st.write("**Cons:** "+", ".join(r["cons"]))
                st.write("**Expected benefit:** "+(r.get("benefit") or "Not specified"))
                st.write("**Major uncertainty:** "+", ".join(r["uncertainties"] or ["Not specified"]))
                if r["violations"]: st.error("Constraint violations: "+", ".join(r["violations"]))
    elif page=="What-If Simulator":
        st.markdown("### Change the conditions. Watch the ranking move.")
        st.caption("Sensitivity estimates from stated assumptions—not predictions.")
        sc=st.session_state.scenario
        c1,c2=st.columns(2)
        sc["budget"]=c1.slider("Available budget",0,100000,int(min(100000,sc.get("budget",1000))),500)
        sc["time"]=c2.slider("Available time (units / week)",0,80,int(min(80,sc.get("time",10))),1)
        sc["growth"]=st.slider("Importance of long-term growth",0,100,int(sc.get("growth",30)),5)
        sc["risk_tolerance"]=st.slider("Risk tolerance",0,100,int(sc.get("risk_tolerance",50)),5)
        sc["cost_overrun"]=st.slider("Potential cost overrun (%)",0,100,int(sc.get("cost_overrun",0)),5)
        sc["time_delay"]=st.slider("Potential time delay (%)",0,100,int(sc.get("time_delay",0)),5)
        if st.button("Reset scenario assumptions"):
            st.session_state.scenario=dict(DEFAULT_SCENARIO); st.rerun()
        results=analyze_decision(apply_scenario(d,sc),sc)
        st.dataframe(pd.DataFrame([{"Rank":i+1,"Option":r["name"],"Score":r["overall"]} for i,r in enumerate(results)]),hide_index=True,use_container_width=True)
        chart=px.bar(pd.DataFrame([{"Option":r["name"],"Score":r["overall"]} for r in results]),x="Option",y="Score",range_y=[0,100],template="plotly_dark",color="Score",color_continuous_scale=["#777d77","#C8FF32"])
        chart.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",coloraxis_showscale=False)
        st.plotly_chart(chart,use_container_width=True)
        st.info("Assumptions: "+", ".join(f"{k.replace('_',' ')} = {v}" for k,v in sc.items()))
    elif page=="Alternative Futures":
        st.markdown("### Plausible paths, not predictions.")
        render_path_map(["Decision"]+[r["name"] for r in results])
        futures=d.get("alternative_futures",[])
        for i,r in enumerate(results):
            f=futures[i] if i<len(futures) else {}
            with st.container(border=True):
                st.markdown(f"#### Path {i+1} · {r['name']}")
                c1,c2=st.columns(2)
                c1.markdown("**Favorable outcome**"); c1.write(f.get("favorable") or f"If it works well: {r.get('benefit') or 'the intended benefit is achieved'}.")
                c2.markdown("**Possible downside**"); c2.write(f.get("downside") or r.get("concern") or "A key assumption may not hold.")
                st.write("**Major uncertainty:** "+str(f.get("uncertainty") or (r["uncertainties"][0] if r["uncertainties"] else "Actual outcomes may differ.")))
                st.write("**Early indicator:** "+str(f.get("early_indicator") or "Progress toward the stated benefit is visible during the first review period."))
                st.write("**Warning sign:** "+str(f.get("warning_sign") or "Cost or time rises without corresponding progress."))
                st.write("**Fallback:** "+str(f.get("fallback") or "Time-box the trial and reassess if the warning sign persists."))
        if d.get("assumptions"):
            st.markdown("### Assumptions to validate")
            for a in d["assumptions"]: st.write(f"- {a}")
    elif page=="Next Move":
        st.markdown(f'<div class="panel"><div class="eyebrow">BEST FIT UNDER CURRENT PRIORITIES</div><h2>{rec["winner"]}</h2><h3>{rec["score"]:.0f}/100</h3><p>{rec["summary"]}</p></div>',unsafe_allow_html=True)
        for label,key in [("Strongest advantage","advantage"),("Main trade-off","tradeoff"),("Key uncertainty","uncertainty"),("When another option could be preferable","switch_condition"),("Recommended immediate action","next_step")]:
            st.markdown(f"**{label}**"); st.write(rec[key])
        st.markdown("**Verify before committing**"); st.write(d.get("verify_before_committing") or "Confirm key estimates and validate important facts independently.")
        st.markdown("**Low-commitment test**"); st.write(d.get("low_commitment_test") or "Run a small, time-boxed trial with one observable success measure.")
        st.markdown("**Reassess if**"); st.write(d.get("reassess_if") or "The key assumption fails, a constraint is violated, or new evidence changes your priorities.")
        if rec.get("close"): st.warning("The leading options are close. Small changes in assumptions could change the ranking.")
        if rec.get("violations"): st.error("The top-scoring option has constraint flags. Review these before acting.")
        st.caption("Forkcast supports your judgment; it does not predict outcomes or make the decision for you.")
        md=f"# Forkcast Decision Report\n\n## {d['title']}\n\n{d.get('description','')}\n\n## Recommendation\n\n{rec['winner']} — {rec['score']:.1f}/100\n\n{rec['summary']}\n\n## Scores\n\n"+"\n".join(f"- {r['name']}: {r['overall']:.1f}/100" for r in results)
        st.download_button("Export report (Markdown)",md,"forkcast-report.md","text/markdown",type="primary")
        st.download_button("Export raw data (JSON)",json.dumps({"decision":d,"analysis":results,"recommendation":rec,"scenario":scenario},indent=2),"forkcast-report.json","application/json")
    st.divider()
    if st.button("＋ Start a new decision", type="primary"):
        st.session_state.decision=None
        st.session_state.original=None
        st.session_state.view="Decision Entry"
        st.rerun()
    if st.button("Edit decision input"):
        st.session_state.view="Decision Entry"; st.rerun()
    if st.button("Save to session history"):
        st.session_state.saved.append(json.loads(json.dumps(d))); st.success("Saved for this session.")
