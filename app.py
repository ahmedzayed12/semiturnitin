"""
Semi Turnitin v35 — Streamlit Web App
AI Content Detector — Fingerprint-Driven Detection
"""
import sys, os, io, re, types, traceback
import streamlit as st

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Semi Turnitin v35",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Inject tkinter stubs so engine imports without crashing ──────────────────
for _mod in ["tkinter","tkinter.ttk","tkinter.filedialog",
             "tkinter.messagebox","tkinter.scrolledtext"]:
    if _mod not in sys.modules:
        sys.modules[_mod] = types.ModuleType(_mod)

import multiprocessing
multiprocessing.freeze_support = lambda: None

# ─── Load Engine (cached) ─────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading detection engine...")
def get_engine():
    import importlib.util, pathlib
    path = pathlib.Path(__file__).parent / "semi_turnitin_v35.py"
    spec = importlib.util.spec_from_file_location("semi_turnitin_v35", path)
    mod  = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except SystemExit:
        pass
    except Exception as e:
        st.error(f"Engine load error: {e}")
        return None
    return mod.AIDetectionEngine()

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Dark theme */
[data-testid="stAppViewContainer"] { background:#0e0e12; }
[data-testid="stHeader"]           { background:#0e0e12; }
section[data-testid="stSidebar"]   { background:#13131a; }
.block-container { padding-top:1.5rem; }

/* Score cards */
.score-card {
    background: #1a1a24;
    border-radius: 16px;
    padding: 28px 20px 20px;
    text-align: center;
    border: 1px solid #2a2a38;
    margin-bottom: 12px;
}
.score-num   { font-size: 58px; font-weight: 800; line-height: 1; }
.score-label { font-size: 13px; color: #888; margin-top: 6px; }
.score-verd  { font-size: 16px; font-weight: 600; margin-top: 8px; }

/* Gauge bar */
.gauge-wrap { background:#222230; border-radius:8px; height:16px;
              overflow:hidden; margin:10px 0; }
.gauge-fill { height:100%; border-radius:8px; transition:width .4s; }

/* Fingerprint rows */
.fp-row { display:flex; align-items:center; gap:10px;
          padding:5px 0; border-bottom:1px solid #1e1e2e; }
.fp-stars { font-size:10px; min-width:30px; }
.fp-label { flex:1; font-size:13px; color:#ccc; }
.fp-bar-bg { width:110px; background:#222230; border-radius:5px;
             height:10px; overflow:hidden; flex-shrink:0; }
.fp-bar    { height:100%; border-radius:5px; }
.fp-pct    { min-width:36px; text-align:right; font-size:12px;
             color:#999; font-family:monospace; }

/* Section headers */
.sec-hdr { font-size:14px; font-weight:700; color:#00c8dc;
           border-left:3px solid #00c8dc; padding-left:10px;
           margin:18px 0 10px; }

/* Metric pill */
.pill { display:inline-block; background:#1e1e2e; border:1px solid #2a2a38;
        border-radius:20px; padding:4px 14px; font-size:12px;
        color:#aaa; margin:3px; }
.pill b { color:#eee; }

/* Risk badge */
.badge { display:inline-block; border-radius:6px; padding:3px 12px;
         font-size:12px; font-weight:700; }

/* Indicator table */
.ind-table { width:100%; border-collapse:collapse; font-size:12px; }
.ind-table tr { border-bottom:1px solid #1e1e2e; }
.ind-table td { padding:5px 8px; color:#bbb; }
.ind-table td:last-child { text-align:right; color:#fff; font-family:monospace; }
</style>
""", unsafe_allow_html=True)


# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:14px;margin-bottom:20px">
  <span style="font-size:36px">🔍</span>
  <div>
    <div style="font-size:24px;font-weight:800;color:#fff">Semi Turnitin <span style="color:#00c8dc">v35</span></div>
    <div style="font-size:13px;color:#666">Fingerprint-Driven AI Content Detector · English & Arabic</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── Layout ───────────────────────────────────────────────────────────────────
left, right = st.columns([1, 1], gap="large")

# ══════════════════════════════════════════════════════════════════════════════
# LEFT PANEL — Input
# ══════════════════════════════════════════════════════════════════════════════
with left:
    st.markdown('<div class="sec-hdr">📝 Input Text</div>', unsafe_allow_html=True)

    # File upload
    uploaded = st.file_uploader(
        "Upload file (optional)",
        type=["txt", "pdf", "docx"],
        label_visibility="collapsed",
    )

    file_text = ""
    if uploaded:
        try:
            if uploaded.name.endswith(".txt"):
                file_text = uploaded.read().decode("utf-8", errors="replace")
            elif uploaded.name.endswith(".pdf"):
                import fitz
                doc = fitz.open(stream=uploaded.read(), filetype="pdf")
                file_text = "\n".join(p.get_text() for p in doc)
            elif uploaded.name.endswith(".docx"):
                import docx as _docx
                doc = _docx.Document(io.BytesIO(uploaded.read()))
                file_text = "\n".join(p.text for p in doc.paragraphs)
            st.success(f"✅ {uploaded.name} — {len(file_text.split())} words loaded")
        except Exception as e:
            st.warning(f"File read error: {e}")

    text = st.text_area(
        "Paste text",
        value=file_text,
        height=300,
        placeholder="Paste English or Arabic text here (min 80 words)...",
        label_visibility="collapsed",
    )

    wc = len(text.split()) if text.strip() else 0
    sc_count = len(re.findall(r'[.!?؟]+', text)) if text.strip() else 0

    ca, cb_, cc = st.columns([3, 1, 1])
    with ca:
        run = st.button("▶  Analyze Text", type="primary", use_container_width=True)
    with cb_:
        st.metric("Words", wc)
    with cc:
        st.metric("Sents", sc_count)

# ══════════════════════════════════════════════════════════════════════════════
# RIGHT PANEL — Results
# ══════════════════════════════════════════════════════════════════════════════
with right:
    st.markdown('<div class="sec-hdr">📊 Analysis Results</div>', unsafe_allow_html=True)

    if not run:
        st.markdown("""
        <div style="text-align:center;padding:80px 20px;color:#444">
          <div style="font-size:40px">🔬</div>
          <div style="margin-top:10px;font-size:14px">Enter text and click Analyze</div>
        </div>""", unsafe_allow_html=True)

    elif wc < 50:
        st.warning("⚠️ Text too short — please enter at least 50 words.")

    else:
        with st.spinner("Analyzing fingerprints..."):
            try:
                engine = get_engine()
                if engine is None:
                    st.error("Engine failed to load.")
                    st.stop()

                res  = engine.analyze(text)
                sc   = res.get("percentage", 0)
                schu = 100.0 - sc
                risk = res.get("risk_level", "")
                verd = res.get("verdict", "")
                ext  = res.get("extended", {})
                inds = res.get("indicators", {})
                fp   = ext.get("fingerprint_score", 0)
                fpd  = ext.get("fp_details", {})

                # ── Color scheme ──────────────────────────────────────────────
                if   sc >= 85: clr, icon, label = "#ff3333", "🔴", "AI — Confirmed"
                elif sc >= 70: clr, icon, label = "#ff7700", "🟠", "AI — High Probability"
                elif sc >= 50: clr, icon, label = "#ffcc00", "🟡", "Mixed — Review"
                elif sc >= 25: clr, icon, label = "#3399ff", "🔵", "Likely Human"
                else:          clr, icon, label = "#33ff88", "🟢", "Human — Confirmed"

                badge_bg = {"CRITICAL":"#5c0000","HIGH":"#4a2000",
                            "MEDIUM":"#3d3300","LOW":"#00224d","MINIMAL":"#00391a"}
                badge_clr = {"CRITICAL":"#ff4444","HIGH":"#ff8800",
                             "MEDIUM":"#ffcc00","LOW":"#44aaff","MINIMAL":"#44ff88"}

                # ── Score cards ───────────────────────────────────────────────
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"""
                    <div class="score-card">
                      <div class="score-num" style="color:{clr}">{sc:.1f}%</div>
                      <div class="score-verd">{icon} {label}</div>
                      <div class="score-label">AI-Generated Content</div>
                      <div style="margin-top:10px">
                        <span class="badge" style="background:{badge_bg.get(risk,'#222')};
                              color:{badge_clr.get(risk,'#aaa')}">{risk}</span>
                      </div>
                    </div>""", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""
                    <div class="score-card">
                      <div class="score-num" style="color:#33ff88">{schu:.1f}%</div>
                      <div class="score-verd">👤 Human Written</div>
                      <div class="score-label">Human-Authored Content</div>
                      <div style="margin-top:10px">
                        <span class="badge" style="background:#00391a;color:#44ff88">
                          {verd}
                        </span>
                      </div>
                    </div>""", unsafe_allow_html=True)

                # ── Main gauge ────────────────────────────────────────────────
                gw = int(sc)
                st.markdown(f"""
                <div style="margin:4px 0 2px">
                  <span style="font-size:11px;color:#555">0%</span>
                  <span style="float:right;font-size:11px;color:#555">100% AI</span>
                </div>
                <div class="gauge-wrap">
                  <div class="gauge-fill" style="width:{gw}%;
                    background:linear-gradient(90deg,#33ff88,#ffcc00,#ff3333)"></div>
                </div>""", unsafe_allow_html=True)

                # ── Quick stats ───────────────────────────────────────────────
                st.markdown(f"""
                <div style="margin:10px 0">
                  <span class="pill">🔬 Fingerprint <b>{fp*100:.1f}%</b></span>
                  <span class="pill">📝 Words <b>{res.get('word_count',0)}</b></span>
                  <span class="pill">📄 Sentences <b>{res.get('sentence_count',0)}</b></span>
                  <span class="pill">🤖 AI Words <b>{res.get('ai_words_count',0)}</b></span>
                  <span class="pill">📊 AI Sents <b>{res.get('ai_sentence_pct',0):.0f}%</b></span>
                </div>""", unsafe_allow_html=True)

                # ═══════════════════════════════════════════════════════════════
                # TABS
                # ═══════════════════════════════════════════════════════════════
                tab_fp, tab_inds, tab_para = st.tabs(
                    ["🔬 Fingerprint Diagnosis", "📊 All Indicators", "📄 Paragraph Analysis"]
                )

                # ── TAB 1: Fingerprint Diagnosis ──────────────────────────────
                with tab_fp:
                    FP_LABELS = {
                        'fp_en_phrases':  "GPT English Phrases (T1)",
                        'fp_cliches':     "Closing Clichés & Stock Phrases",
                        'fp_simple_gpt':  "Simple/School GPT Style",
                        'fp_structure':   "AI Sentence Structures",
                        'fp_vocab':       "AI Vocabulary",
                        'fp_format_sig':  "Markdown Formatting (**,##,bullets)",
                        'fp_t2_patterns': "AI Sentence Patterns (T2)",
                        'fp_ar_phrases':  "Arabic GPT Phrases",
                        'fp_format':      "Direct Format Markers",
                        'fp_triplets':    "Triple Enumerations (X, Y, and Z)",
                        'fp_uniformity':  "Uniform Sentence Length (CV<0.30)",
                        'fp_pairs':       "Elegant Word Pairs",
                        'fp_no_data':     "No Numbers / No Data",
                        'fp_no_personal': "No Personal Pronouns",
                    }

                    # AI fingerprints
                    ai_fps = [(v, FP_LABELS.get(k,k), k)
                              for k,v in fpd.items() if v >= 0.12]
                    ai_fps.sort(reverse=True)

                    st.markdown('<div class="sec-hdr">📌 AI Fingerprints — raised the score</div>',
                                unsafe_allow_html=True)

                    if ai_fps:
                        rows_html = ""
                        for val, lbl, key in ai_fps[:12]:
                            pct  = int(val*100)
                            w    = pct
                            c    = ("#ff3333" if val>=0.65 else
                                    "#ff7700" if val>=0.40 else "#ffcc00")
                            st = ("★★★" if val>=0.65 else
                                  "★★ " if val>=0.40 else "★  ")
                            rows_html += f"""
                            <div class="fp-row">
                              <span class="fp-stars" style="color:{c}">{st}</span>
                              <span class="fp-label">{lbl}</span>
                              <div class="fp-bar-bg">
                                <div class="fp-bar" style="width:{w}%;background:{c}"></div>
                              </div>
                              <span class="fp-pct">{pct}%</span>
                            </div>"""
                        st_html = rows_html   # rename to avoid collision
                    else:
                        st_html = '<div style="color:#555;padding:12px">⚪ No significant AI fingerprints</div>'

                    # Human fingerprints
                    h_fps = []
                    ndata = fpd.get('fp_no_data', 0)
                    npers = fpd.get('fp_no_personal', 0)
                    if ndata < -0.05: h_fps.append((abs(ndata), "Real Numbers & Data Found"))
                    if npers < -0.05: h_fps.append((abs(npers), "Personal Pronouns (I/my/honestly)"))
                    he = ext.get("human_error_score",0)
                    eh = ext.get("english_human_score",0)
                    dh = ext.get("deep_human_score",0)
                    ci = ext.get("citation_bonus",0)
                    if he >= 0.15: h_fps.append((he, "Human Writing Errors"))
                    if eh >= 0.20:
                        sigs = ext.get("en_human_signals",[])
                        h_fps.append((eh, f"Natural Human Writing [{sigs[0][:20] if sigs else ''}]"))
                    if dh >= 0.20: h_fps.append((dh, "Deep Stylometric Signature"))
                    if ci >= 0.20: h_fps.append((ci, "Academic Citations Found"))
                    h_fps.sort(reverse=True)

                    h_html = ""
                    if h_fps:
                        for val, lbl in h_fps:
                            pct = int(val*100)
                            h_html += f"""
                            <div class="fp-row">
                              <span class="fp-stars" style="color:#33ff88">🛡</span>
                              <span class="fp-label" style="color:#33ff88">{lbl}</span>
                              <div class="fp-bar-bg">
                                <div class="fp-bar" style="width:{pct}%;background:#33ff88"></div>
                              </div>
                              <span class="fp-pct" style="color:#33ff88">{pct}%</span>
                            </div>"""

                    import streamlit.components.v1 as components
                    components.html(f"""
                    <style>
                    .fp-row{{display:flex;align-items:center;gap:10px;
                             padding:5px 0;border-bottom:1px solid #1e1e2e;}}
                    .fp-stars{{font-size:10px;min-width:30px;}}
                    .fp-label{{flex:1;font-size:13px;color:#ccc;}}
                    .fp-bar-bg{{width:110px;background:#222230;border-radius:5px;
                               height:10px;overflow:hidden;flex-shrink:0;}}
                    .fp-bar{{height:100%;border-radius:5px;}}
                    .fp-pct{{min-width:36px;text-align:right;font-size:12px;
                             color:#999;font-family:monospace;}}
                    .sec{{font-size:13px;font-weight:700;color:#00c8dc;
                          border-left:3px solid #00c8dc;padding-left:8px;
                          margin:14px 0 8px;}}
                    body{{background:#0e0e12;}}
                    </style>
                    <div class="sec">📌 AI Fingerprints</div>
                    {st_html}
                    {'<div class="sec">🛡 Human Fingerprints</div>' + h_html if h_html else ''}
                    """, height=max(60 + len(ai_fps)*34 + len(h_fps)*34, 120))

                    # Why this score
                    st.markdown('<div class="sec-hdr">💡 Why this score?</div>',
                                unsafe_allow_html=True)
                    n_str = sum(1 for v,_,_ in ai_fps if v>=0.55)
                    n_med = sum(1 for v,_,_ in ai_fps if v>=0.35)
                    if fp >= 0.75:
                        why = (f"**{n_str} strong AI fingerprints** accumulated. "
                               f"Strongest: *{ai_fps[0][1] if ai_fps else '—'}* "
                               f"({ai_fps[0][0]*100:.0f}% confidence)." if ai_fps else
                               f"**High fingerprint score ({fp*100:.0f}%)**")
                    elif fp >= 0.50:
                        why = (f"{n_str} strong + {n_med-n_str} medium fingerprints. "
                               + ("Partially offset by human signals." if h_fps else ""))
                    elif fp >= 0.25:
                        why = "Partial AI fingerprints mixed with natural human writing."
                    else:
                        why = ("No significant AI fingerprints detected — text appears human-written. "
                               + (f"Human signals: {h_fps[0][1]}." if h_fps else ""))
                    if res.get("word_count",0) < 150:
                        why += f" ⚠️ Short text ({res['word_count']} words) — result is approximate."
                    st.markdown(why)

                    # Weight breakdown
                    ga = ext.get("layer_a_v20",0)
                    gb = ext.get("layer_b_ml",0)
                    gc = ext.get("layer_c_heuristic",0)
                    st.markdown("**Score composition:**")
                    for lbl, wgt, val in [
                        ("🔬 Fingerprints",     35, fp*100),
                        ("🔵 Engine B (LLR+NB)",30, gb*100),
                        ("🟢 Engine A (Semantic)",20, ga*100),
                        ("⚪ Engine C (Classic)",15, gc*100),
                    ]:
                        st.markdown(f"""
                        <div style="display:flex;align-items:center;gap:8px;
                                    margin:3px 0;font-size:12px;">
                          <span style="min-width:170px;color:#bbb">{lbl} ({wgt}%)</span>
                          <div style="flex:1;background:#222230;border-radius:4px;
                                      height:8px;overflow:hidden">
                            <div style="width:{min(val,100):.0f}%;height:100%;
                                        background:#00c8dc;border-radius:4px"></div>
                          </div>
                          <span style="color:#fff;font-family:monospace;
                                       min-width:40px;text-align:right">{val:.1f}%</span>
                        </div>""", unsafe_allow_html=True)

                # ── TAB 2: All Indicators ─────────────────────────────────────
                with tab_inds:
                    st.markdown('<div class="sec-hdr">📊 All Detection Indicators</div>',
                                unsafe_allow_html=True)
                    for name, val in inds.items():
                        bar_w = int(min(val,1.0)*100)
                        c2 = ("#ff3333" if val>=0.70 else
                              "#ff7700" if val>=0.50 else
                              "#33ff88" if val<=0.30 else "#888")
                        st.markdown(f"""
                        <div style="display:flex;align-items:center;gap:8px;
                                    margin:3px 0;font-size:11px">
                          <span style="min-width:200px;color:#bbb;
                                       white-space:nowrap;overflow:hidden;
                                       text-overflow:ellipsis">{name[:35]}</span>
                          <div style="flex:1;background:#1e1e2e;border-radius:3px;
                                      height:7px;overflow:hidden">
                            <div style="width:{bar_w}%;height:100%;
                                        background:{c2};border-radius:3px"></div>
                          </div>
                          <span style="color:{c2};font-family:monospace;
                                       min-width:38px;text-align:right">{val*100:.1f}%</span>
                        </div>""", unsafe_allow_html=True)

                    conf = res.get("confidence",{})
                    if conf:
                        st.divider()
                        st.markdown(f"""
                        <span class="pill">🎯 Confidence: <b>{conf.get('label','—')}</b></span>
                        <span class="pill">📏 Range: <b>{conf.get('range_low',0):.1f}% — {conf.get('range_high',0):.1f}%</b></span>
                        """, unsafe_allow_html=True)

                # ── TAB 3: Paragraph Analysis ─────────────────────────────────
                with tab_para:
                    paras = ext.get("paragraph_results", [])
                    if paras:
                        st.markdown('<div class="sec-hdr">📄 Paragraph-by-Paragraph</div>',
                                    unsafe_allow_html=True)
                        st.caption(f"Total: {ext.get('total_para',0)} paragraphs | "
                                   f"AI confirmed: {ext.get('ai_para_count',0)} | "
                                   f"Max: {ext.get('max_para_score',0)*100:.1f}%")
                        for p in paras:
                            pct  = p.get('pct', 0)
                            pc   = ("#ff3333" if pct>=70 else
                                    "#ff7700" if pct>=50 else
                                    "#ffcc00" if pct>=30 else "#33ff88")
                            prev = p.get('preview','')[:80]
                            st.markdown(f"""
                            <div style="background:#1a1a24;border-radius:8px;
                                        padding:10px 14px;margin:6px 0;
                                        border-left:3px solid {pc}">
                              <div style="display:flex;justify-content:space-between;
                                          align-items:center">
                                <span style="color:#888;font-size:11px">
                                  Paragraph {p.get('index','')} — {p.get('verdict','')}
                                </span>
                                <span style="color:{pc};font-weight:700;
                                             font-size:16px">{pct:.1f}%</span>
                              </div>
                              <div style="margin-top:6px;
                                          background:#222230;border-radius:4px;
                                          height:6px;overflow:hidden">
                                <div style="width:{pct}%;height:100%;
                                            background:{pc};border-radius:4px"></div>
                              </div>
                              <div style="margin-top:8px;font-size:12px;color:#999;
                                          font-style:italic">"{prev}..."</div>
                            </div>""", unsafe_allow_html=True)
                    else:
                        st.info("Paragraph analysis requires longer text.")

            except Exception as e:
                st.error(f"Analysis error: {e}")
                with st.expander("Error details"):
                    st.code(traceback.format_exc())

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;color:#333;font-size:11px;margin-top:40px;
            padding-top:20px;border-top:1px solid #1e1e2e">
  Semi Turnitin v35 · Fingerprint-Driven AI Content Detection · English & Arabic
</div>""", unsafe_allow_html=True)
