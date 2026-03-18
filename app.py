"""
Semi Turnitin v35 — Streamlit Web App
AI Content Detector — Fingerprint-Driven Detection
"""
import sys, os, io, re, types, traceback
import streamlit as st

st.set_page_config(
    page_title="Semi Turnitin v35",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Inject stubs for desktop modules ─────────────────────────────
for _m in ["tkinter","tkinter.ttk","tkinter.filedialog",
           "tkinter.messagebox","tkinter.scrolledtext"]:
    if _m not in sys.modules:
        sys.modules[_m] = types.ModuleType(_m)

import multiprocessing as _mp
_mp.freeze_support = lambda: None

# ── Load Engine ───────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading engine...")
def get_engine():
    import importlib.util, pathlib
    p = pathlib.Path(__file__).parent / "semi_turnitin_v35.py"
    if not p.exists():
        return None
    spec = importlib.util.spec_from_file_location("st35", p)
    mod  = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except (SystemExit, Exception):
        pass
    return getattr(mod, "AIDetectionEngine", None)()

# ── CSS ───────────────────────────────────────────────────────────
st.markdown("""<style>
[data-testid="stAppViewContainer"]{background:#0e0e12}
[data-testid="stHeader"]{background:#0e0e12}
.block-container{padding-top:1.4rem}
.score-card{background:#1a1a24;border-radius:14px;padding:22px 16px;
            text-align:center;border:1px solid #2a2a38;margin-bottom:10px}
.score-num{font-size:54px;font-weight:800;line-height:1}
.score-sub{font-size:13px;color:#888;margin-top:5px}
.score-vd {font-size:15px;font-weight:600;margin-top:6px}
.pill{display:inline-block;background:#1e1e2e;border:1px solid #2a2a38;
      border-radius:20px;padding:3px 12px;font-size:12px;color:#aaa;margin:2px}
.pill b{color:#eee}
.sh{font-size:13px;font-weight:700;color:#00c8dc;
    border-left:3px solid #00c8dc;padding-left:8px;margin:14px 0 8px}
.fp-row{display:flex;align-items:center;gap:8px;padding:4px 0;
        border-bottom:1px solid #1a1a2e;font-size:12px}
.fp-lbl{flex:1;color:#ccc}
.fp-bg{width:100px;background:#222230;border-radius:4px;
       height:8px;overflow:hidden;flex-shrink:0}
.fp-fill{height:100%;border-radius:4px}
.fp-pct{min-width:34px;text-align:right;color:#888;font-family:monospace}
</style>""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:12px;margin-bottom:18px">
  <span style="font-size:32px">🔍</span>
  <div>
    <div style="font-size:22px;font-weight:800;color:#fff">
      Semi Turnitin <span style="color:#00c8dc">v35</span>
    </div>
    <div style="font-size:12px;color:#555">
      Fingerprint-Driven AI Content Detector · English & Arabic
    </div>
  </div>
</div>""", unsafe_allow_html=True)

L, R = st.columns([1,1], gap="large")

# ═══════════════════════════════════════════════════════════════════
# LEFT — Input
# ═══════════════════════════════════════════════════════════════════
with L:
    st.markdown('<div class="sh">📝 Input Text</div>', unsafe_allow_html=True)

    up = st.file_uploader("Upload file", type=["txt","pdf","docx"],
                          label_visibility="collapsed")
    ft = ""
    if up:
        raw = up.read()
        try:
            if up.name.endswith(".txt"):
                ft = raw.decode("utf-8", errors="replace")
            elif up.name.endswith(".pdf"):
                try:
                    import pdfplumber
                    with pdfplumber.open(io.BytesIO(raw)) as pdf:
                        ft = "\n".join(p.extract_text() or "" for p in pdf.pages)
                except Exception:
                    st.warning("PDF reading failed — paste text manually.")
            elif up.name.endswith(".docx"):
                try:
                    import docx as _dx
                    ft = "\n".join(p.text for p in _dx.Document(io.BytesIO(raw)).paragraphs)
                except Exception:
                    st.warning("DOCX reading failed — paste text manually.")
            if ft.strip():
                st.success(f"✅ {up.name} — {len(ft.split())} words")
        except Exception as e:
            st.warning(f"Error: {e}")

    txt = st.text_area("Text", value=ft, height=300,
                       placeholder="Paste English or Arabic text (min 80 words)...",
                       label_visibility="collapsed")

    wc = len(txt.split()) if txt.strip() else 0
    c1,c2,c3 = st.columns([3,1,1])
    with c1: run = st.button("▶  Analyze", type="primary", use_container_width=True)
    with c2: st.metric("Words", wc)
    with c3: st.metric("Sents", len(re.findall(r'[.!?؟]+', txt)))

# ═══════════════════════════════════════════════════════════════════
# RIGHT — Results
# ═══════════════════════════════════════════════════════════════════
with R:
    st.markdown('<div class="sh">📊 Results</div>', unsafe_allow_html=True)

    if not run:
        st.markdown("""<div style="text-align:center;padding:70px 20px;color:#333">
          <div style="font-size:36px">🔬</div>
          <div style="margin-top:8px;font-size:13px">Enter text and click Analyze</div>
        </div>""", unsafe_allow_html=True)
    elif wc < 50:
        st.warning("⚠️ Too short — enter at least 50 words.")
    else:
        with st.spinner("Analyzing..."):
            try:
                eng = get_engine()
                if eng is None:
                    st.error("Engine not found.")
                    st.stop()

                res  = eng.analyze(txt)
                sc   = res.get("percentage", 0)
                shu  = 100 - sc
                risk = res.get("risk_level","")
                vd   = res.get("verdict","")
                ext  = res.get("extended",{})
                inds = res.get("indicators",{})
                fp   = ext.get("fingerprint_score",0)
                fpd  = ext.get("fp_details",{})

                # color
                if   sc>=85: clr,ico,lbl="#ff3333","🔴","AI — Confirmed"
                elif sc>=70: clr,ico,lbl="#ff7700","🟠","AI — High Probability"
                elif sc>=50: clr,ico,lbl="#ffcc00","🟡","Mixed — Review Needed"
                elif sc>=25: clr,ico,lbl="#3399ff","🔵","Likely Human"
                else:        clr,ico,lbl="#33ff88","🟢","Human — Confirmed"

                # Score cards
                ca,cb_=st.columns(2)
                with ca:
                    st.markdown(f"""<div class="score-card">
                      <div class="score-num" style="color:{clr}">{sc:.1f}%</div>
                      <div class="score-vd">{ico} {lbl}</div>
                      <div class="score-sub">AI Content · Risk: {risk}</div>
                    </div>""", unsafe_allow_html=True)
                with cb_:
                    st.markdown(f"""<div class="score-card">
                      <div class="score-num" style="color:#33ff88">{shu:.1f}%</div>
                      <div class="score-vd">👤 Human Written</div>
                      <div class="score-sub">{vd}</div>
                    </div>""", unsafe_allow_html=True)

                # Gauge
                st.markdown(f"""
                <div style="background:linear-gradient(90deg,#33ff88 0%,
                  #ffcc00 50%,#ff3333 100%);border-radius:6px;height:10px;
                  margin:6px 0;position:relative">
                  <div style="position:absolute;left:{sc:.0f}%;top:-4px;
                    transform:translateX(-50%);font-size:18px">▼</div>
                </div>""", unsafe_allow_html=True)

                # Pills
                st.markdown(f"""
                <div style="margin:8px 0">
                  <span class="pill">🔬 FP <b>{fp*100:.1f}%</b></span>
                  <span class="pill">📝 <b>{res.get('word_count',0)}</b> words</span>
                  <span class="pill">🤖 AI words <b>{res.get('ai_words_count',0)}</b></span>
                  <span class="pill">📄 AI sents <b>{res.get('ai_sentence_pct',0):.0f}%</b></span>
                </div>""", unsafe_allow_html=True)

                # Tabs
                t1,t2,t3 = st.tabs(["🔬 Fingerprints","📊 Indicators","📄 Paragraphs"])

                # ── Tab 1: Fingerprints ───────────────────────────────────
                with t1:
                    FLB = {
                        'fp_en_phrases': "GPT English Phrases",
                        'fp_cliches':    "Closing Clichés",
                        'fp_simple_gpt': "Simple GPT Style",
                        'fp_structure':  "AI Sentence Structures",
                        'fp_vocab':      "AI Vocabulary",
                        'fp_format_sig': "Markdown Formatting",
                        'fp_t2_patterns':"GPT Sentence Patterns",
                        'fp_ar_phrases': "Arabic GPT Phrases",
                        'fp_triplets':   "Triple Enumerations",
                        'fp_uniformity': "Uniform Sentence Length",
                        'fp_pairs':      "Elegant Word Pairs",
                        'fp_no_data':    "No Numbers/Data",
                        'fp_no_personal':"No Personal Pronouns",
                    }
                    ai_fps = sorted(
                        [(v,FLB.get(k,k)) for k,v in fpd.items() if v>=0.12],
                        reverse=True)

                    st.markdown('<div class="sh">📌 AI Fingerprints</div>',
                                unsafe_allow_html=True)
                    for val,lbl in ai_fps[:12]:
                        pct = int(val*100)
                        c2  = ("#ff3333" if val>=0.65 else
                               "#ff7700" if val>=0.40 else "#ffcc00")
                        st.markdown(f"""<div class="fp-row">
                          <span style="color:{c2};font-size:9px;min-width:26px">
                            {"★★★" if val>=0.65 else "★★" if val>=0.40 else "★"}</span>
                          <span class="fp-lbl">{lbl}</span>
                          <div class="fp-bg">
                            <div class="fp-fill" style="width:{pct}%;background:{c2}"></div>
                          </div>
                          <span class="fp-pct">{pct}%</span>
                        </div>""", unsafe_allow_html=True)

                    if not ai_fps:
                        st.caption("⚪ No significant AI fingerprints detected.")

                    # Human
                    h_fps = []
                    if fpd.get('fp_no_data',0)<-0.05: h_fps.append((abs(fpd['fp_no_data']),"Real Numbers & Data"))
                    if fpd.get('fp_no_personal',0)<-0.05: h_fps.append((abs(fpd['fp_no_personal']),"Personal Pronouns"))
                    if ext.get("human_error_score",0)>=0.15: h_fps.append((ext["human_error_score"],"Human Writing Errors"))
                    if ext.get("english_human_score",0)>=0.20: h_fps.append((ext["english_human_score"],"Natural Human Writing"))
                    if ext.get("deep_human_score",0)>=0.20: h_fps.append((ext["deep_human_score"],"Deep Stylometric Signature"))
                    if ext.get("citation_bonus",0)>=0.20: h_fps.append((ext["citation_bonus"],"Academic Citations"))
                    h_fps.sort(reverse=True)

                    if h_fps:
                        st.markdown('<div class="sh">🛡 Human Fingerprints</div>',
                                    unsafe_allow_html=True)
                        for val,lbl in h_fps:
                            pct=int(val*100)
                            st.markdown(f"""<div class="fp-row">
                              <span style="color:#33ff88;font-size:9px;min-width:26px">🛡</span>
                              <span class="fp-lbl" style="color:#33ff88">{lbl}</span>
                              <div class="fp-bg"><div class="fp-fill"
                                style="width:{pct}%;background:#33ff88"></div></div>
                              <span class="fp-pct" style="color:#33ff88">{pct}%</span>
                            </div>""", unsafe_allow_html=True)

                    # Why
                    st.markdown('<div class="sh">💡 Why this score?</div>',
                                unsafe_allow_html=True)
                    ns = sum(1 for v,_ in ai_fps if v>=0.55)
                    if fp>=0.75:
                        why = f"**{ns} strong fingerprints** → high AI probability. Strongest: *{ai_fps[0][1] if ai_fps else '—'}* ({ai_fps[0][0]*100:.0f}%)." if ai_fps else f"High fingerprint score ({fp*100:.0f}%)"
                    elif fp>=0.50: why = f"{ns} strong fingerprints." + (" Partially offset by human signals." if h_fps else "")
                    elif fp>=0.25: why = "Partial AI fingerprints + human patterns."
                    else: why = "No significant AI fingerprints — appears human-written."
                    if res.get('word_count',0)<150: why += f" ⚠️ Short text ({res['word_count']} words)."
                    st.markdown(why)

                    # Weights
                    ga=ext.get("layer_a_v20",0); gb=ext.get("layer_b_ml",0); gc=ext.get("layer_c_heuristic",0)
                    for lbl2,wgt,val2 in [("🔬 Fingerprints",35,fp*100),("🔵 Engine B",30,gb*100),("🟢 Engine A",20,ga*100),("⚪ Engine C",15,gc*100)]:
                        st.markdown(f"""<div style="display:flex;align-items:center;
                          gap:8px;margin:3px 0;font-size:11px">
                          <span style="min-width:130px;color:#bbb">{lbl2} ({wgt}%)</span>
                          <div style="flex:1;background:#1e1e2e;border-radius:3px;height:6px;overflow:hidden">
                            <div style="width:{min(val2,100):.0f}%;height:100%;
                              background:#00c8dc;border-radius:3px"></div></div>
                          <span style="color:#fff;font-family:monospace;
                            min-width:38px;text-align:right">{val2:.1f}%</span>
                        </div>""", unsafe_allow_html=True)

                # ── Tab 2: All Indicators ─────────────────────────────────
                with t2:
                    for nm,val in inds.items():
                        bw=int(min(val,1.0)*100)
                        c3=("#ff3333" if val>=0.70 else "#ff7700" if val>=0.50 else "#33ff88" if val<=0.30 else "#888")
                        st.markdown(f"""<div style="display:flex;align-items:center;
                          gap:8px;margin:2px 0;font-size:11px">
                          <span style="min-width:190px;color:#bbb;white-space:nowrap;
                            overflow:hidden;text-overflow:ellipsis">{nm[:34]}</span>
                          <div style="flex:1;background:#1e1e2e;border-radius:3px;
                            height:6px;overflow:hidden">
                            <div style="width:{bw}%;height:100%;background:{c3};
                              border-radius:3px"></div></div>
                          <span style="color:{c3};font-family:monospace;
                            min-width:36px;text-align:right">{val*100:.1f}%</span>
                        </div>""", unsafe_allow_html=True)
                    cf=res.get("confidence",{})
                    if cf:
                        st.divider()
                        st.markdown(f'<span class="pill">🎯 Confidence: <b>{cf.get("label","—")}</b></span>'
                                    f'<span class="pill">📏 Range: <b>{cf.get("range_low",0):.1f}—{cf.get("range_high",0):.1f}%</b></span>',
                                    unsafe_allow_html=True)

                # ── Tab 3: Paragraphs ─────────────────────────────────────
                with t3:
                    paras = ext.get("paragraph_results",[])
                    if paras:
                        st.caption(f"Paragraphs: {ext.get('total_para',0)} | AI: {ext.get('ai_para_count',0)} | Max: {ext.get('max_para_score',0)*100:.1f}%")
                        for p in paras:
                            pct2=p.get('pct',0)
                            pc=("#ff3333" if pct2>=70 else "#ff7700" if pct2>=50 else "#ffcc00" if pct2>=30 else "#33ff88")
                            st.markdown(f"""<div style="background:#1a1a24;border-radius:8px;
                              padding:10px 12px;margin:5px 0;border-left:3px solid {pc}">
                              <div style="display:flex;justify-content:space-between">
                                <span style="color:#666;font-size:11px">Para {p.get('index','')} — {p.get('verdict','')}</span>
                                <span style="color:{pc};font-weight:700">{pct2:.1f}%</span></div>
                              <div style="background:#222;border-radius:3px;height:4px;
                                margin:5px 0;overflow:hidden">
                                <div style="width:{pct2}%;height:100%;background:{pc}"></div></div>
                              <div style="font-size:11px;color:#666;font-style:italic">
                                "{p.get('preview','')[:70]}..."</div>
                            </div>""", unsafe_allow_html=True)
                    else:
                        st.caption("Paragraph analysis needs longer text.")

            except Exception as e:
                st.error(f"Error: {e}")
                with st.expander("Details"):
                    st.code(traceback.format_exc())

st.markdown("""<div style="text-align:center;color:#2a2a38;font-size:11px;
  margin-top:30px;padding-top:16px;border-top:1px solid #1a1a2e">
  Semi Turnitin v35 · Fingerprint-Driven AI Detection · English & Arabic
</div>""", unsafe_allow_html=True)
