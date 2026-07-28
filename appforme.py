"""
AI Fingerprint Detector v4.0 — Unified PDF Report Build
تقرير PDF يعمل على ملفات PDF الأصلية فقط مع تظليل النقاط المشكوك بها فوق الأصل نفسه
تقرير فوق الصفحات الأصلية مع تظليل شفاف، واستبعاد محافظ للمراجع والاستشهادات من الحساب
"""
import re
import math
import collections
import io
import base64
import json
from pathlib import Path
from datetime import datetime

import streamlit as st

# ── مكتبات اختيارية ──────────────────────────────────────────────────────────
try:
    import fitz  # PyMuPDF
    FITZ_OK = True
except Exception:
    FITZ_OK = False

try:
    import docx
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.oxml.text.paragraph import CT_P
    from docx.oxml.table import CT_Tbl
    from docx.text.paragraph import Paragraph
    from docx.table import Table, _Cell
    from docx.document import Document as _Document
    DOCX_OK = True
except Exception:
    DOCX_OK = False

try:
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.colors import HexColor
    RLAB_OK = True
except Exception:
    RLAB_OK = False

try:
    from PIL import Image
    PIL_OK = True
except Exception:
    PIL_OK = False


# ══════════════════════════════════════════════════════════════════════════════
# CUSTOMER RATINGS — تخزين بسيط دائم على القرص
# ══════════════════════════════════════════════════════════════════════════════
RATINGS_FILE = Path(__file__).resolve().parent / "customer_ratings.json"


def _seed_ratings():
    """تقييمات افتراضية تظهر أول مرة قبل ورود تقييمات حقيقية."""
    return [
        {"name": "أحمد سالم", "stars": 5,
         "comment": "أداة دقيقة جدًا ووفّرت عليّ وقتًا كبيرًا في مراجعة الأبحاث.",
         "date": "2026-06-14"},
        {"name": "منى عبد الله", "stars": 4,
         "comment": "التقرير المظلل فوق ملف PDF ممتاز، أتمنى دعم صيغ أخرى مستقبلاً.",
         "date": "2026-06-20"},
        {"name": "خالد يوسف", "stars": 5,
         "comment": "التحديث الجديد حسّن سرعة التحليل بشكل ملحوظ.",
         "date": "2026-07-05"},
        {"name": "سارة إبراهيم", "stars": 4,
         "comment": "واجهة واضحة وسهلة الاستخدام، شكرًا على الجهد المبذول.",
         "date": "2026-07-14"},
        {"name": "محمد الطاهر", "stars": 5,
         "comment": "نتائج موثوقة وتقرير احترافي جاهز للطباعة مباشرة.",
         "date": "2026-07-22"},
    ]


def _load_ratings():
    try:
        if RATINGS_FILE.exists():
            data = json.loads(RATINGS_FILE.read_text(encoding="utf-8"))
            if isinstance(data, list) and data:
                return data
    except Exception:
        pass
    return _seed_ratings()


def _save_rating(entry: dict):
    ratings = _load_ratings()
    ratings.append(entry)
    try:
        RATINGS_FILE.write_text(
            json.dumps(ratings, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except Exception:
        pass  # في بيئات القراءة فقط لن يُحفظ التقييم بشكل دائم، لكن الواجهة تستمر بالعمل
    return ratings


# ══════════════════════════════════════════════════════════════════════════════
# FINGERPRINT ENGINE
# ══════════════════════════════════════════════════════════════════════════════

T1_PHRASES = [
    'it is worth noting','it is important to note','it is crucial to',
    'it is essential to','in the realm of','delve into','delve deeper',
    'let us delve','pave the way','at the heart of',
    'a multifaceted','a holistic approach','a comprehensive understanding',
    'nuanced understanding','multifaceted nature','transformative potential',
    'unprecedented','rapidly evolving landscape','ever-evolving',
    'plays a pivotal role','plays a crucial role','plays a fundamental role',
    'serves as a cornerstone','serves as a catalyst','serves as a testament',
    'serves as a foundation','in today\'s rapidly','in today\'s ever-changing',
    'foster a deeper understanding','harness the power of',
    'navigate the complexities','navigate the challenges',
    'unlock the potential','leverage the power of','reimagine the way',
    'underscore the importance','underscores the need','it is imperative',
    'first and foremost','state-of-the-art','best practices',
    'robust framework','comprehensive framework','evidence-based approach',
    'data-driven insights','key stakeholders','synergistic',
    'cutting-edge solutions','groundbreaking research',
    'innovative solutions','sustainable development',
    'this study examines','this paper examines','this paper investigates',
    'this paper addresses','this paper aims','this work examines',
    'these findings indicate','these findings suggest','these findings demonstrate',
    'these findings confirm','these findings reveal',
    'the results show a','the results demonstrate','the results indicate',
    'the results suggest','the results reveal','the results confirm',
    'the observed improvement','the observed increase','the observed decrease',
    'the observed pattern','the observed behavior','the observed trend',
    'when compared with recent','when compared to previous',
    'when compared with existing','when compared to traditional',
    'despite rapid progress','despite significant progress',
    'despite recent advances','despite considerable advances',
    'the feasibility of using','the feasibility of integrating',
    'the feasibility of applying','the feasibility of implementing',
    'instead of separating','rather than being treated',
    'rather than relying on','rather than focusing on',
    'emerges through repeated','emerges from physical',
    'emerges through sensorimotor','emerged through interaction',
    'at the same time, several limitations',
    'at the same time, some limitations',
    'future work should','future research should','future studies should',
    'future investigation should','future work could','future research could',
    'the main contribution','the key contribution','the primary contribution',
    'the central contribution','the core contribution',
    'in practical terms','in concrete terms',
    'further research is needed','additional research is needed',
    'has become increasingly important','has become increasingly prevalent',
    'has become increasingly complex','has become increasingly clear',
    'has emerged as a','has emerged as an',
    'highlights the importance of','highlights the need for',
    'highlights the potential of','highlights the significance of',
    'the paper focuses on','it investigates whether',
    'the study therefore supports','the study therefore confirms',
    'the study therefore demonstrates','the study therefore shows',
    'meaningful adaptive behavior','consistent learning pattern',
    'meaningful improvement','measurable improvement','measurable learning',
    'this makes the case','this makes it relevant','this makes the study',
    'not only.*but also','embodied intelligence','embodied learning',
    'resource-constrained','real-world constraints',
    'the present study','the present paper','the present work',
    'the proposed approach','the proposed method','the proposed framework',
    'the proposed system','the proposed model',
    # ── دفعة توسّع إضافية للحساسية العالية (إنجليزي فقط) ──────────────────────
    'it is worth mentioning','it is important to highlight','it is worth highlighting',
    'in today\'s fast-paced world','in the modern era','in the digital age',
    'holds significant potential','opens new avenues','opens up new possibilities',
    'shed light on','sheds light on','shed further light on',
    'underlying mechanism','a testament to','a paradigm shift','paradigm shift',
    'at its core','at the core of','lies at the intersection of',
    'in light of these findings','in light of the above',
    'it can be argued that','it could be argued that',
    'a growing body of','growing body of evidence','growing body of literature',
    'against this backdrop','in this rapidly changing landscape',
    'stands as a testament','stand as a testament',
    'a pressing need','an urgent need for','a critical need for',
    'significant strides','made significant strides','notable strides',
    'seamlessly integrate','seamlessly integrates','the ability to seamlessly',
    'fostering a culture of','fostering collaboration',
    'bridging the gap between','bridge the gap',
    'empowering individuals to','empower users to','empowers researchers to',
    'unlocking new possibilities','unlocking new opportunities',
    'a wealth of','a plethora of','a myriad of','myriad of',
    'in an era of','increasingly digital world','the advent of','with the advent of',
    'it goes without saying','needless to say',
    'sets the stage for','lays the groundwork for','lay the foundation for',
    'at an unprecedented rate','an unprecedented pace',
    'gained significant traction','gained considerable attention','garnered significant attention',
    'over the past few years','the intricate interplay between','intricate interplay','complex interplay',
    'reinforcing the importance','instrumental in shaping',
    'the cornerstone of','form the cornerstone','forms the backbone of','backbone of',
    'to put it simply','simply put',
    'it is no secret that','it is widely acknowledged that','widely recognized that',
    'as we navigate','as we move forward','moving forward,',
    'in essence,','essentially,','fundamentally,',
    'on a broader level','on a larger scale','in broader terms',
    'a beacon of','a driving force behind','driving force behind',
    'warrants further investigation','warrants further exploration','merits further investigation',
    'worth exploring further','deserves further attention',
    'cannot be overstated','cannot be understated',
    'in the ever-changing world of','in the fast-evolving field of',
    'in alignment with','tailored to meet','tailored specifically to','tailored approach',
    'a testament to the power of','revolutionize the way','poised to revolutionize',
    'game changer','game-changer','a holistic view of',
    'robust and reliable','robust and effective','in a world where','in an age where',
    # ── دفعة ثالثة: عبارات أكاديمية شائعة جداً في نصوص GPT ──────────────────
    'this comprehensive review','offers valuable insights into','provides valuable insights into',
    'valuable insights into','a critical component of','a vital component of',
    'plays an integral role','an integral part of','integral to the success of',
    'in order to fully understand','in order to gain a deeper understanding',
    'a deeper understanding of','a comprehensive overview of',
    'sheds new light on','offers a fresh perspective on','provides a fresh perspective on',
    'contributes to the growing body of','adds to the growing body of',
    'the findings of this study','the findings of this research',
    'according to recent studies','recent studies have shown','recent research has shown',
    'studies have consistently shown','research has consistently demonstrated',
    'it is evident that','it becomes evident that','it is clear that',
    'this highlights the need for','this underscores the need for',
    'in recent decades','over the last decade','in recent times',
    'has garnered widespread attention','has attracted considerable attention',
    'remains a significant challenge','remains a critical challenge',
    'poses a significant challenge','poses significant challenges',
    'a key factor in','a critical factor in','a determining factor in',
    'plays a significant role in shaping','a major factor contributing to',
    'in an effort to','in an attempt to','with the aim of',
    'the primary objective of this study','the main objective of this study',
    'the purpose of this study is to','this study aims to explore',
    'this research seeks to','this paper seeks to',
    'by leveraging','through the use of','by utilizing',
    'ultimately leading to','ultimately resulting in','which in turn leads to',
    'has far-reaching implications','carries significant implications',
    'a fundamental aspect of','a fundamental component of',
    'it is essential to consider','it is crucial to consider',
    'a holistic understanding of','a nuanced approach to',
    'the significance of this study lies in','underscoring its significance',
]

T2_PATTERNS = [
    r'\bthis (?:study|paper|article|research|work) (?:examines?|investigates?|explores?|addresses?|presents?|demonstrates?|aims? to|argues?|proposes?|introduces?)\b',
    r'\bthese findings (?:indicate|suggest|demonstrate|show|reveal|confirm|support|highlight|underscore)\b',
    r'\bthe (?:results?|findings?|data|evidence|analysis) (?:show|suggest|indicate|demonstrate|reveal|confirm|highlight)\b',
    r'\bthe (?:observed|noted|measured|recorded|reported) (?:improvement|increase|decrease|reduction|pattern|trend|behavior|change|difference)\b',
    r'\bthis (?:makes?|renders?) (?:the|it|this) (?:study|approach|work|finding|result|system|prototype|case|paper|contribution)\b',
    r'\bat the same time,? (?:several?|some|various|important|key|notable) (?:limitations?|challenges?|issues?|concerns?|caveats?)\b',
    r'\b(?:meaningful|measurable|clear|consistent|significant|substantial|notable) (?:improvement|learning|progress|adaptation|behavior|pattern|results?|gains?|increase|decrease)\b',
    r'\bwhen compared (?:with|to) (?:recent|previous|existing|traditional|other|prior|current|state-of-the-art)\b',
    r'\bfuture (?:work|research|studies?|investigation|directions?) (?:should|could|may|might|will|can) (?:explore|examine|investigate|test|consider|address|focus|extend|incorporate)\b',
    r'\bdespite (?:rapid|significant|recent|considerable|substantial|great|notable) (?:progress|advances?|development|growth|improvement|interest)\b',
    r'\bthe (?:feasibility|practicality|effectiveness|utility|applicability|viability) of (?:using|applying|integrating|implementing|employing|adopting)\b',
    r'\binstead of (?:separating|relying on|using|treating|employing|assuming)\b',
    r'\brather than (?:being treated|relying on|focusing on|separating|using|assuming|requiring)\b',
    r'\b(?:emerges?|emerged?) (?:from|through|via) (?:repeated?|real|physical|sensorimotor|direct|online|trial)\b',
    r'\bthis (?:approach|method|framework|system|design|setup|configuration|architecture) (?:allows?|enables?|facilitates?|supports?|provides?|offers?|ensures?)\b',
    r'\bthe (?:study|paper|experiment|research|work) (?:therefore|thus|hence|consequently) (?:supports?|confirms?|demonstrates?|shows?|suggests?|indicates?)\b',
    r'\bdespit(?:e|ing) (?:these|the|its|their|such|various) (?:challenges?|limitations?|drawbacks?|obstacles?|constraints?)\b',
    r'\bthis (?:article|paper|essay|study|work|chapter|section) (?:aims?|seeks?|explores?|examines?|discusses?|presents?|provides?|argues?|demonstrates?|shows?)\b',
    r'\ba (?:comprehensive|thorough|detailed|rigorous|systematic|careful|nuanced|in-depth) (?:analysis|examination|overview|review|investigation|evaluation|assessment|study)\b',
    r'\b(?:significant|substantial|considerable|notable|marked|profound|dramatic) (?:impact|effect|influence|improvement|shift|difference|change|reduction|increase)\b',
    r'\bthe (?:main|primary|key|central|core|fundamental|principal) (?:contribution|value|finding|advantage|limitation|challenge|goal|aim|objective|novelty) of\b',
    r'\b(?:plays?|played?) a (?:vital|crucial|key|central|pivotal|important|major|fundamental|critical|essential|significant) role in\b',
    r'\b(?:moreover|furthermore|additionally|besides),?\s+(?:the|this|its|these|such|various|several)\b',
    r'\b(?:has|have) (?:significantly|greatly|substantially|considerably|dramatically|rapidly|increasingly) (?:grown|expanded|increased|developed|improved|enhanced|advanced|transformed|evolved)\b',
    r'\b(?:is|are) characterized by (?:a|an|the|its|their)\b',
    r'\b(?:serves?|acts?) as (?:a|an|the) (?:major|key|primary|central|critical|vital|important|significant|crucial|fundamental|useful|practical)\b',
    r'\b(?:driven by|fueled by|powered by|propelled by|guided by|motivated by) (?:the|its|their|a|an)\b',
    r'\bin (?:conclusion|summary|closing|summation),?\s+(?:it is|we can|this|the|these)\b',
    r'\bit (?:is|was) (?:therefore|thus|hence|consequently) (?:demonstrated?|confirmed?|shown|established|evident|clear|argued|suggested)\b',
    r'\bthe (?:present|current|proposed|described|outlined|discussed) (?:study|work|paper|approach|method|system|framework|research)\b',
    r'\bby (?:examining|exploring|analyzing|investigating|considering|addressing|comparing|evaluating) (?:the|these|this|how|why|what|whether)\b',
    r'\bit (?:should|must|cannot|can) be (?:noted|emphasized|stressed|acknowledged|recognized|mentioned|highlighted) that\b',
    r'\bthe (?:importance|significance|relevance|role|impact|value|potential|need|necessity|utility) of (?:this|these|the|such|incorporating|using|applying)\b',
    r'\b(?:not only).{3,60}\b(?:but also|but it also|but they also|but also helps|but also provides)\b',
    r'\bthis (?:narrow(?:er)?|broad(?:er)?|simpl(?:e|er)|more (?:complex|focused|practical|realistic)) (?:focus|scope|approach|perspective|question|contribution)\b',
    r'\b(?:overall|in general|taken together|collectively),?\s+(?:the|these|this|our|the results)\b',
    r'\baddress(?:ing|es|ed)? (?:the|these|this|key|critical|important|pressing|growing|real) (?:issue|challenge|problem|concern|need|question|gap|limitation|challenge)\b',
    # ── دفعة توسّع إضافية للحساسية العالية (إنجليزي فقط) ──────────────────────
    r'\b(?:this|these) (?:findings?|results?|insights?) (?:shed|sheds|shed further) light on\b',
    r'\b(?:plays?|serves?) a (?:pivotal|instrumental|foundational) role in (?:shaping|driving|enabling|advancing)\b',
    r'\bit (?:is|remains) (?:widely|generally|commonly) (?:acknowledged|recognized|accepted|understood) that\b',
    r'\b(?:opens?|opening) (?:up )?(?:new|fresh|exciting) (?:avenues|possibilities|opportunities|horizons) for\b',
    r'\b(?:bridg(?:e|ing|es)) the gap between\b',
    r'\b(?:foster|fosters|fostering) (?:a|an) (?:deeper|greater|better) (?:understanding|awareness|appreciation) of\b',
    r'\b(?:empower|empowers|empowering) (?:individuals|users|researchers|organizations|learners) to\b',
    r'\b(?:seamlessly|effectively|effortlessly) (?:integrate|integrates|combine|combines) (?:with|into)\b',
    r'\bin (?:an|this) (?:increasingly|rapidly)\s+\w+\s+(?:world|landscape|era|environment)\b',
    r'\b(?:warrants?|merits?) (?:further|additional) (?:investigation|exploration|research|study|attention)\b',
    r'\b(?:cannot|can not) be (?:overstated|understated|overemphasized)\b',
    r'\b(?:sets?|lays?|laying) the (?:stage|groundwork|foundation) for\b',
    r'\b(?:a|an) (?:growing|increasing|expanding) body of (?:evidence|research|literature|work)\b',
    r'\b(?:gained|garnered|attracted) (?:significant|considerable|growing|increasing) (?:attention|traction|interest)\b',
    r'\b(?:poised|positioned|set) to (?:revolutionize|transform|reshape|redefine)\b',
    # ── دفعة ثالثة ──────────────────────────────────────────────────────────
    r'\b(?:offers?|provides?) (?:valuable|useful|important|critical|fresh|new) insights? into\b',
    r'\bplays? an integral (?:role|part) in\b',
    r'\bin order to (?:fully|better|fully understand|gain a (?:deeper|better)) (?:understand|understanding)\b',
    r'\b(?:contributes?|adds?) to the (?:growing|existing|current) body of (?:knowledge|literature|research)\b',
    r'\baccording to recent studies,?\b|\brecent (?:studies|research) (?:have|has) shown\b',
    r'\bstudies have consistently (?:shown|demonstrated|found)\b',
    r'\bit (?:is|becomes) evident that\b|\bit is clear that\b',
    r'\bremains? a (?:significant|critical|major|persistent) challenge\b',
    r'\bposes? (?:significant|considerable|major) challenges?\b',
    r'\ba (?:key|critical|determining|major) factor (?:in|contributing to)\b',
    r'\bin an (?:effort|attempt) to\b|\bwith the (?:aim|goal|intention) of\b',
    r'\bthe (?:primary|main) (?:objective|purpose|aim) of this (?:study|research|paper) is to\b',
    r'\bthis (?:study|research|paper) (?:aims|seeks) to (?:explore|examine|investigate)\b',
    r'\bby (?:leveraging|utilizing|harnessing) (?:the|its|their)\b',
    r'\bultimately (?:leading|resulting) (?:to|in)\b',
    r'\bhas far-reaching implications\b|\bcarries significant implications\b',
    r'\ba fundamental (?:aspect|component|part) of\b',
    r'\bit is (?:essential|crucial|important) to consider\b',
    r'\bunderscor(?:ing|es|ed) its significance\b',
]


# تجهيز النص قبل التحليل: استبعاد المراجع والاستشهادات داخل المتن
# ══════════════════════════════════════════════════════════════════════════════

_ARABIC_DIACRITICS_RE = re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]')


def _count_text_words(text: str) -> int:
    return len(re.findall(r'\b[a-zA-Z\u0600-\u06FF]+\b', text or ''))


def _normalize_reference_heading(text: str) -> str:
    """توحيد عنوان قسم المراجع قبل مطابقته."""
    s = _ARABIC_DIACRITICS_RE.sub('', text or '')
    s = s.replace('ـ', '')
    s = re.sub(r'\s+', ' ', s).strip()
    s = re.sub(r'^[\s\-–—:؛،,.()\[\]]+', '', s)
    s = re.sub(r'[\s\-–—:؛،,.()\[\]]+$', '', s)
    return s


REF_SECTION_HEADERS = re.compile(
    r'''^(?:
        (?:(?:chapter|section|appendix|الفصل|القسم)\s+)?(?:\d+(?:\.\d+)*)?\s*[:.\-–—]?\s*
    )?(?:
        references?|reference\s+list|bibliography|works\s+cited|literature\s+cited|sources?
        |المراجع(?:\s+(?:العربية|الاجنبية|الأجنبية))?
        |قائمة\s+(?:المراجع|المصادر)
        |المصادر(?:\s+والمراجع)?
        |المراجع\s+والمصادر
    )$''',
    re.I | re.X
)


def _is_reference_header(text: str) -> bool:
    """
    يكتشف عنوان قسم المراجع حتى لو سبقه رقم فصل أو تبعته نقطتان.
    لا يعتمد على وجود كلمة References داخل فقرة طويلة.
    """
    for raw_line in re.split(r'[\r\n]+', text or ''):
        line = _normalize_reference_heading(raw_line)
        if not line:
            continue
        if len(line.split()) <= 8 and REF_SECTION_HEADERS.fullmatch(line):
            return True
    return False


REF_LINE_PATTERNS = [
    r'^\s*\[\s*\d+(?:\s*[-–,]\s*\d+)*\s*\]',
    r'^\s*\d{1,4}\s*[.)]\s+',
    r'\bdoi\s*:\s*10\.\d{4,9}/\S+',
    r'\bhttps?://\S+',
    r'\b(?:ISBN|ISSN)\b',
    r'\b(?:Vol\.?|Volume)\s*\d+',
    r'\b(?:No\.?|Issue)\s*\d+',
    r'\bpp?\.\s*\d+(?:\s*[-–]\s*\d+)?',
    r'\b(?:Journal|Proceedings|Transactions|Conference|Press|Publisher)\b',
    r'\bet\s+al\.?',
]


def _reference_line_score(line: str) -> float:
    """درجة احتمالية أن السطر مدخل ببليوجرافي وليس فقرة من المتن."""
    s = re.sub(r'\s+', ' ', (line or '').strip())
    if not s:
        return 0.0

    score = 0.0
    if re.search(r'^\s*\[\s*\d+(?:\s*[-–,]\s*\d+)*\s*\]', s):
        score += 2.5
    if re.search(r'^\s*\d{1,4}\s*[.)]\s+', s):
        score += 1.8
    if re.search(r'\b(?:18|19|20)\d{2}[a-z]?\b', s, re.I):
        score += 0.8
    if re.search(r'\bdoi\s*:|doi\.org/10\.|\b10\.\d{4,9}/\S+', s, re.I):
        score += 2.2
    if re.search(r'https?://', s, re.I):
        score += 1.7
    if re.search(r'\bet\s+al\.?\b', s, re.I):
        score += 1.0
    if re.search(r'\b(?:Journal|Proceedings|Transactions|Conference|Press|Publisher|Springer|Elsevier|Wiley|IEEE|ACM)\b', s, re.I):
        score += 1.1
    if re.search(r'\b(?:Vol\.?|Volume|No\.?|Issue|pp?\.)\s*\d+', s, re.I):
        score += 1.0
    if re.search(r'\b(?:ISBN|ISSN)\b', s, re.I):
        score += 1.5
    if re.search(r'^[A-ZÀ-ÖØ-Ý][A-Za-zÀ-ÖØ-öø-ÿ\'’-]+,\s*(?:[A-Z]\.?\s*){1,4}', s):
        score += 1.2
    if re.search(r'\([12]\d{3}[a-z]?\)', s, re.I):
        score += 0.8
    if s.count(',') >= 2 and s.count('.') >= 2:
        score += 0.5
    if len(s) >= 45:
        score += 0.2
    return score


def _is_reference_line(line: str) -> bool:
    """
    تصنيف محافظ للسطر المرجعي. الأنماط القوية تكفي منفردة،
    وإلا نحتاج اجتماع أكثر من علامة ببليوجرافية لتجنب حذف متن الباحث.
    """
    s = re.sub(r'\s+', ' ', (line or '').strip())
    if not s:
        return False
    if _is_reference_header(s):
        return True
    if re.search(r'^\s*\[\s*\d+(?:\s*[-–,]\s*\d+)*\s*\]', s):
        return True
    if re.search(r'\bdoi\s*:|doi\.org/10\.|\b10\.\d{4,9}/\S+', s, re.I):
        return True
    return _reference_line_score(s) >= 2.6


_INLINE_NUMERIC_CITATION_RE = re.compile(
    r'\[(?:\s*\d+\s*(?:[-–]\s*\d+)?\s*)(?:[,;]\s*\d+\s*(?:[-–]\s*\d+)?\s*)*\]'
)
_INLINE_AUTHOR_YEAR_RE = re.compile(
    r'''\(
        (?=[^()]{0,180}\b(?:18|19|20)\d{2}[a-z]?\b)
        (?:[^()]*?[A-ZÀ-ÖØ-Ý\u0600-\u06FF][^()]*?)
        (?:18|19|20)\d{2}[a-z]?
        (?:\s*[,;]\s*[^()]*?(?:18|19|20)\d{2}[a-z]?)*
    \)''',
    re.I | re.X
)
_INLINE_YEAR_ONLY_RE = re.compile(r'\((?:18|19|20)\d{2}[a-z]?\)')
_INLINE_URL_RE = re.compile(r'https?://\S+|www\.\S+', re.I)
_INLINE_DOI_RE = re.compile(r'\b(?:doi\s*:\s*)?10\.\d{4,9}/\S+', re.I)


def _strip_inline_citations(text: str) -> str:
    """يحذف علامات الاستشهاد فقط ويُبقي الجملة العلمية نفسها للتحليل."""
    s = text or ''
    s = _INLINE_NUMERIC_CITATION_RE.sub(' ', s)
    s = _INLINE_AUTHOR_YEAR_RE.sub(' ', s)
    s = _INLINE_YEAR_ONLY_RE.sub(' ', s)
    s = _INLINE_DOI_RE.sub(' ', s)
    s = _INLINE_URL_RE.sub(' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


def _find_unheaded_reference_tail(lines) -> int | None:
    """
    إذا غاب عنوان المراجع، يبحث فقط في الجزء الأخير من المستند عن كتلة
    كثيفة من المداخل الببليوجرافية. هذا يمنع إسقاط فقرات وسط البحث.
    """
    nonempty = [(i, line.strip()) for i, line in enumerate(lines) if line.strip()]
    if len(nonempty) < 6:
        return None

    earliest_pos = max(0, int(len(nonempty) * 0.50))
    for pos in range(earliest_pos, len(nonempty)):
        window = nonempty[pos:pos + 6]
        if len(window) < 3:
            continue
        ref_hits = sum(1 for _, line in window if _is_reference_line(line))
        if ref_hits < 3:
            continue
        first_ref_offset = next(
            (j for j, (_, line) in enumerate(window) if _is_reference_line(line)),
            None
        )
        if first_ref_offset is None:
            continue
        tail = nonempty[pos + first_ref_offset:]
        density = sum(1 for _, line in tail if _is_reference_line(line)) / max(len(tail), 1)
        if density >= 0.55:
            return tail[0][0]
    return None


def _prepare_analysis_text(text: str) -> dict:
    """
    يفصل متن البحث عن قسم المراجع ويزيل الاستشهادات داخل المتن.
    يعيد إحصاءات الاستبعاد لتسهيل المراجعة والاختبار.
    """
    raw_text = text or ''
    lines = raw_text.replace('\r\n', '\n').replace('\r', '\n').split('\n')

    ref_start = None
    for idx, line in enumerate(lines):
        if _is_reference_header(line):
            ref_start = idx
            break

    if ref_start is None:
        ref_start = _find_unheaded_reference_tail(lines)

    if ref_start is None:
        main_lines = lines
        ref_lines = []
        header_found = False
    else:
        main_lines = lines[:ref_start]
        ref_lines = lines[ref_start:]
        header_found = any(_is_reference_header(line) for line in ref_lines[:3])

    main_text_raw = '\n'.join(main_lines)
    analysis_text = _strip_inline_citations(main_text_raw)
    references_text = '\n'.join(ref_lines)

    return {
        'analysis_text': analysis_text,
        'main_text_raw': main_text_raw,
        'references_text': references_text,
        'reference_section_found': ref_start is not None,
        'reference_header_found': header_found,
        'original_words': _count_text_words(raw_text),
        'analyzed_words': _count_text_words(analysis_text),
        'reference_words_excluded': _count_text_words(references_text),
        'inline_citation_words_removed': max(
            0,
            _count_text_words(main_text_raw) - _count_text_words(analysis_text)
        ),
    }


def _format_percentage(value: float, mask_low: bool = True) -> str:
    """عرض النسب من 0% إلى 20% بالشكل المطلوب: *%."""
    try:
        pct = float(value)
    except (TypeError, ValueError):
        return '*%'
    if mask_low and 0.0 <= pct <= 20.0:
        return '*%'
    return f'{pct:.0f}%'


def _format_human_percentage(ai_value: float, human_value: float) -> str:
    """لا يعرض قيمة معكوسة تكشف النسبة المخفية من 0 إلى 20."""
    try:
        ai_pct = float(ai_value)
        human_pct = float(human_value)
    except (TypeError, ValueError):
        return 'غير محدد'
    if 0.0 <= ai_pct <= 20.0:
        return 'مرتفع'
    return f'{human_pct:.0f}%'


LOW_SCORE_HIGHLIGHT_THRESHOLD = 20.0


def _highlighting_allowed(ai_percentage: float) -> bool:
    """
    يمنع التظليل نهائياً عندما تكون النتيجة معروضة بالشكل *%.
    أي نتيجة من صفر إلى 20% لا ينتج عنها أي annotation أو تظليل في PDF/DOCX.
    """
    try:
        return float(ai_percentage) > LOW_SCORE_HIGHLIGHT_THRESHOLD
    except (TypeError, ValueError):
        return False


def _collect_unique_pattern_matches(text: str, patterns) -> tuple[int, list]:
    """
    يجمع مطابقات الأنماط مع إزالة التطابقات المتداخلة التي تصف العبارة نفسها.
    هذا يمنع احتساب جملة واحدة مرتين لأن نمطين عامين التقطا الجزء نفسه.
    """
    raw_matches = []
    for pat_idx, pat in enumerate(patterns):
        try:
            for match in re.finditer(pat, text, re.I):
                start, end = match.span()
                if end > start:
                    raw_matches.append((start, end, pat_idx, pat))
        except Exception:
            continue

    raw_matches.sort(key=lambda x: (x[0], -(x[1] - x[0]), x[2]))
    unique = []
    for item in raw_matches:
        start, end, pat_idx, pat = item
        duplicate = False
        for kept in unique:
            ks, ke, _, _ = kept
            overlap = max(0, min(end, ke) - max(start, ks))
            smaller = max(1, min(end - start, ke - ks))
            if overlap / smaller >= 0.60:
                duplicate = True
                break
        if not duplicate:
            unique.append(item)

    pattern_counts = collections.Counter(item[2] for item in unique)
    matched_patterns = [
        (patterns[idx], pattern_counts[idx])
        for idx in sorted(pattern_counts)
    ]
    return len(unique), matched_patterns


# ══════════════════════════════════════════════════════════════════════════════
# FINGERPRINT ENGINE
# ══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# AI FINGERPRINT ENGINE v4.0 — HYBRID STYLOMETRY
# ─────────────────────────────────────────────────────────────────────────────

AI_ENGINE_VERSION = "4.2 High-Sensitivity Phrase Engine"

_STYLE_WORD_RE = re.compile(
    r"[A-Za-zÀ-ÖØ-öø-ÿ]+(?:['’-][A-Za-zÀ-ÖØ-öø-ÿ]+)?|"
    r"[\u0621-\u064A\u066E-\u06D3\u06FA-\u06FC]+"
)
_SENTENCE_END_RE = re.compile(r"(?<=[.!?؟])\s+|\n\s*\n+")

_STRONG_AI_MARKERS = {
    'in the realm of', 'delve into', 'delve deeper', 'let us delve',
    'pave the way', 'at the heart of', 'a multifaceted',
    'nuanced understanding', 'multifaceted nature', 'transformative potential',
    'rapidly evolving landscape', 'ever-evolving', 'serves as a testament',
    'harness the power of', 'navigate the complexities',
    'unlock the potential', 'leverage the power of', 'reimagine the way',
    'synergistic', 'cutting-edge solutions', 'groundbreaking research',
    # ── دفعة توسّع إضافية للحساسية العالية (إنجليزي فقط) ──────────────────────
    'shed light on', 'sheds light on', 'shed further light on',
    'a testament to', 'a paradigm shift', 'paradigm shift',
    'lies at the intersection of', 'stands as a testament', 'stand as a testament',
    'seamlessly integrate', 'seamlessly integrates', 'the ability to seamlessly',
    'bridging the gap between', 'bridge the gap',
    'unlocking new possibilities', 'unlocking new opportunities',
    'a wealth of', 'a plethora of', 'a myriad of', 'myriad of',
    'it goes without saying', 'needless to say',
    'gained significant traction', 'garnered significant attention',
    'the intricate interplay between', 'intricate interplay',
    'cannot be overstated', 'cannot be understated',
    'poised to revolutionize', 'game changer', 'game-changer',
    'a beacon of', 'a driving force behind',
    'offers valuable insights into', 'provides valuable insights into',
    'contributes to the growing body of', 'plays an integral role',
    'has garnered widespread attention', 'has attracted considerable attention',
    'sheds new light on', 'a comprehensive overview of',
}

_LOW_SPECIFICITY_MARKERS = {
    'this study examines', 'this paper examines', 'this paper investigates',
    'this paper addresses', 'this paper aims', 'this work examines',
    'the results demonstrate', 'the results indicate', 'the results suggest',
    'the results reveal', 'the results confirm', 'future work should',
    'future research should', 'future studies should', 'future work could',
    'future research could', 'the proposed approach', 'the proposed method',
    'the proposed framework', 'the proposed system', 'the proposed model',
    'the present study', 'the present paper', 'the present work',
    'state-of-the-art', 'best practices', 'sustainable development',
    'the findings of this study', 'the findings of this research',
    'according to recent studies', 'recent studies have shown',
    'recent research has shown', 'in recent decades', 'over the last decade',
}

_TRANSITION_PHRASES = [
    'moreover', 'furthermore', 'additionally', 'in addition', 'however',
    'therefore', 'thus', 'consequently', 'nevertheless', 'nonetheless',
    'on the other hand', 'in contrast', 'in conclusion', 'overall',
    'taken together', 'at the same time', 'in this context',
]

_STYLE_STOPWORDS = {
    'the','and','that','this','with','from','into','have','has','had','were','was',
    'are','for','of','to','in','on','by','as','an','a','or','it','its','their',
    'they','these','those','which','while','where','when','than','then','also',
    'using','used','based','study','paper','research','work','method','model',
    'system','results','result','analysis','approach','data','figure','table',
}


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def _safe_mean(values) -> float:
    vals = [float(v) for v in values if v is not None]
    return sum(vals) / len(vals) if vals else 0.0


def _safe_std(values) -> float:
    vals = [float(v) for v in values if v is not None]
    if len(vals) < 2:
        return 0.0
    mean = sum(vals) / len(vals)
    return math.sqrt(sum((v - mean) ** 2 for v in vals) / len(vals))


def _percentile(values, q: float) -> float:
    vals = sorted(float(v) for v in values)
    if not vals:
        return 0.0
    if len(vals) == 1:
        return vals[0]
    pos = _clamp(q) * (len(vals) - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return vals[lo]
    frac = pos - lo
    return vals[lo] * (1.0 - frac) + vals[hi] * frac


def _normalize_style_text(text: str) -> str:
    s = _ARABIC_DIACRITICS_RE.sub('', text or '')
    s = s.replace('ـ', '')
    s = re.sub(r'[إأآٱ]', 'ا', s)
    s = s.replace('ى', 'ي').replace('ؤ', 'و').replace('ئ', 'ي')
    s = re.sub(r'[ \t]+', ' ', s)
    return s.strip()


def _style_tokens(text: str) -> list[str]:
    return [m.group(0).lower() for m in _STYLE_WORD_RE.finditer(_normalize_style_text(text))]


def _split_analysis_sentences(text: str) -> list[str]:
    s = (text or '').replace('\r\n', '\n').replace('\r', '\n')
    # PDF extraction often inserts a newline inside a sentence.
    s = re.sub(r'(?<![.!?؟:؛])\n(?!\s*\n)', ' ', s)
    raw = _SENTENCE_END_RE.split(s)
    out = []
    for item in raw:
        item = re.sub(r'\s+', ' ', item).strip(' \t\n')
        if len(_style_tokens(item)) >= 3:
            out.append(item)
    return out


def _split_analysis_paragraphs(text: str) -> list[str]:
    raw = re.split(r'\n\s*\n+', text or '')
    paragraphs = []
    for p in raw:
        p = re.sub(r'\s+', ' ', p).strip()
        if len(_style_tokens(p)) >= 8:
            paragraphs.append(p)
    return paragraphs


def _marker_weight(phrase: str) -> float:
    p = _normalize_style_text(phrase).lower()
    if p in {_normalize_style_text(x).lower() for x in _STRONG_AI_MARKERS}:
        return 2.80
    if p in {_normalize_style_text(x).lower() for x in _LOW_SPECIFICITY_MARKERS}:
        return 0.50
    if '.*' in phrase:
        return 1.30
    return 1.25


def _collect_weighted_phrase_hits(text_lower: str) -> dict:
    weighted_hits = 0.0
    occurrence_count = 0
    hit_counter = collections.Counter()

    for phrase in T1_PHRASES:
        try:
            if '.*' in phrase:
                matches = list(re.finditer(phrase, text_lower, re.I))
            else:
                normalized_phrase = _normalize_style_text(phrase).lower()
                matches = list(re.finditer(re.escape(normalized_phrase), text_lower, re.I))
        except Exception:
            matches = []
        if not matches:
            continue
        count = len(matches)
        occurrence_count += count
        hit_counter[phrase] += count
        # Repetition matters, but sub-linearly so one template cannot dominate.
        weighted_hits += _marker_weight(phrase) * (1.0 + math.log1p(count - 1))

    ordered_hits = [p for p, _ in hit_counter.most_common()]
    return {
        'weighted_hits': weighted_hits,
        'occurrence_count': occurrence_count,
        'unique_count': len(hit_counter),
        'ordered_hits': ordered_hits,
        'counter': hit_counter,
    }


def _ngram_repetition_signal(sentences: list[str], n_values=(3, 4)) -> tuple[float, float]:
    all_ngrams = []
    for sentence in sentences:
        toks = _style_tokens(sentence)
        for n in n_values:
            if len(toks) < n:
                continue
            for i in range(len(toks) - n + 1):
                gram = tuple(toks[i:i+n])
                if all(t in _STYLE_STOPWORDS for t in gram):
                    continue
                all_ngrams.append(gram)
    if not all_ngrams:
        return 0.0, 0.0
    counts = collections.Counter(all_ngrams)
    duplicate_occurrences = sum(max(0, c - 1) for c in counts.values())
    ratio = duplicate_occurrences / max(len(all_ngrams), 1)
    signal = _clamp((ratio - 0.003) / 0.035)
    return ratio, signal


def _opener_repetition_signal(sentences: list[str]) -> tuple[float, float]:
    openers = []
    for sentence in sentences:
        toks = _style_tokens(sentence)
        if not toks:
            continue
        # Three-token openings are more informative than one-token openings.
        opener = tuple(toks[:min(3, len(toks))])
        openers.append(opener)
    if len(openers) < 4:
        return 0.0, 0.0
    counts = collections.Counter(openers)
    repeated = sum(max(0, c - 1) for c in counts.values())
    ratio = repeated / len(openers)
    return ratio, _clamp((ratio - 0.03) / 0.22)


def _transition_signal(text_lower: str, n_sents: int) -> tuple[int, int, float, float]:
    counter = collections.Counter()
    for phrase in _TRANSITION_PHRASES:
        normalized = _normalize_style_text(phrase).lower()
        cnt = len(re.findall(re.escape(normalized), text_lower, re.I))
        if cnt:
            counter[phrase] = cnt
    total = sum(counter.values())
    unique = len(counter)
    density = total / max(n_sents, 1)
    # High density with limited diversity is more formulaic than diverse use.
    diversity = unique / max(total, 1)
    signal = _clamp((density - 0.10) / 0.42)
    if total >= 3 and diversity < 0.55:
        signal = _clamp(signal + 0.15)
    return total, unique, density, signal


def _punctuation_regularity_signal(sentences: list[str]) -> tuple[float, float, int]:
    if len(sentences) < 4:
        return 0.0, 0.0, 0
    punct_chars = '.,;:!?؟،؛—()[]"“”'
    counts = [sum(s.count(ch) for ch in punct_chars) for s in sentences]
    mean = _safe_mean(counts)
    cv = (_safe_std(counts) / mean) if mean > 0 else 0.0
    types = sum(1 for ch in punct_chars if any(ch in s for s in sentences))
    regularity = _clamp((0.75 - cv) / 0.60)
    # Rich punctuation diversity is a weak counter-signal to mechanical regularity.
    if types >= 7:
        regularity *= 0.75
    return cv, regularity, types


def _lexical_smoothness_signal(tokens: list[str]) -> tuple[float, float, float]:
    if len(tokens) < 60:
        return 0.0, 0.0, 0.0
    content = [t for t in tokens if t not in _STYLE_STOPWORDS and len(t) >= 3]
    if not content:
        return 0.0, 0.0, 0.0
    counts = collections.Counter(content)
    unique = len(counts)
    hapax_ratio = sum(1 for c in counts.values() if c == 1) / max(unique, 1)
    root_ttr = unique / math.sqrt(max(2.0 * len(content), 1.0))
    # Low hapax ratio can indicate over-smoothed vocabulary, but remains weak evidence.
    smoothness = _clamp((0.58 - hapax_ratio) / 0.34)
    return hapax_ratio, root_ttr, smoothness


def _build_analysis_chunks(sentences: list[str], target_words: int = 185,
                           min_words: int = 80, max_words: int = 275,
                           overlap_sentences: int = 2) -> list[str]:
    """يبني نوافذ متداخلة كي لا تضيع الإشارة عند حدود المقاطع."""
    if not sentences:
        return []
    chunks = []
    start = 0
    n = len(sentences)
    while start < n:
        current = []
        current_words = 0
        end = start
        while end < n:
            sw = len(_style_tokens(sentences[end]))
            if current and current_words + sw > max_words:
                break
            current.append(sentences[end])
            current_words += sw
            end += 1
            if current_words >= target_words:
                break
        if current_words >= min_words or (not chunks and current_words > 0):
            chunks.append(' '.join(current))
        if end >= n:
            break
        next_start = max(start + 1, end - max(0, overlap_sentences))
        if next_start <= start:
            next_start = start + 1
        start = next_start

    # دمج ذيل قصير جداً مع آخر نافذة بدلاً من تكوين نافذة مضللة.
    if len(chunks) >= 2 and len(_style_tokens(chunks[-1])) < min_words:
        merged = chunks[-2] + ' ' + chunks[-1]
        if len(_style_tokens(merged)) <= max_words * 1.35:
            chunks[-2] = merged
            chunks.pop()
    return chunks


def _normalized_entropy(counter: collections.Counter) -> float:
    total = sum(counter.values())
    if total <= 1 or len(counter) <= 1:
        return 0.0
    entropy = -sum((c / total) * math.log(c / total, 2) for c in counter.values() if c > 0)
    return _clamp(entropy / math.log(len(counter), 2))


def _moving_ttr(tokens: list[str], window: int = 50) -> tuple[float, float]:
    """MATTR أكثر ثباتاً من TTR العادي مع اختلاف طول المستند."""
    if not tokens:
        return 0.0, 0.0
    content = [t for t in tokens if t not in _STYLE_STOPWORDS and len(t) >= 3]
    if not content:
        return 0.0, 0.0
    if len(content) <= window:
        value = len(set(content)) / len(content)
        return value, 0.0
    vals = []
    step = max(1, window // 5)
    for i in range(0, len(content) - window + 1, step):
        segment = content[i:i + window]
        vals.append(len(set(segment)) / window)
    mean = _safe_mean(vals)
    cv = _safe_std(vals) / mean if mean > 0 else 0.0
    return mean, cv


def _template_repetition_signal(sentences: list[str]) -> tuple[float, float]:
    """يرصد تكرار هياكل الجمل دون الاعتماد على الكلمات نفسها."""
    templates = []
    for sentence in sentences:
        toks = _style_tokens(sentence)
        if len(toks) < 5:
            continue
        skeleton = []
        for token in toks[:18]:
            if token in _STYLE_STOPWORDS:
                skeleton.append('F')
            elif token.isdigit():
                skeleton.append('N')
            elif len(token) <= 3:
                skeleton.append('S')
            else:
                skeleton.append('C')
        # ضغط التكرارات المتجاورة يجعل القالب أقل حساسية لطول الجملة.
        compressed = []
        for symbol in skeleton:
            if not compressed or compressed[-1] != symbol:
                compressed.append(symbol)
        templates.append(tuple(compressed[:10]))
    if len(templates) < 5:
        return 0.0, 0.0
    counts = collections.Counter(templates)
    repeated = sum(max(0, c - 1) for c in counts.values())
    ratio = repeated / len(templates)
    return ratio, _clamp((ratio - 0.05) / 0.35)


def _clause_rhythm_signal(sentences: list[str]) -> tuple[float, float, float]:
    if len(sentences) < 4:
        return 0.0, 0.0, 0.0
    clause_counts = []
    for sentence in sentences:
        count = 1 + len(re.findall(r'[,;:،؛]|\b(?:and|but|while|whereas|although|because|which|that)\b|\b(?:لكن|بينما|حيث|لان|لأن|والذي|والتي)\b', sentence, re.I))
        clause_counts.append(count)
    mean = _safe_mean(clause_counts)
    cv = _safe_std(clause_counts) / mean if mean > 0 else 0.0
    regularity = _clamp((0.72 - cv) / 0.58)
    return mean, cv, regularity


def _function_word_stability(tokens: list[str]) -> tuple[float, float]:
    """ثبات توزيع الكلمات الوظيفية بين أرباع النص؛ إشارة ضعيفة لا تعمل منفردة."""
    if len(tokens) < 120:
        return 0.0, 0.0
    vocab = sorted(_STYLE_STOPWORDS)
    boundaries = [round(i * len(tokens) / 4) for i in range(5)]
    vectors = []
    for i in range(4):
        seg = tokens[boundaries[i]:boundaries[i + 1]]
        if not seg:
            continue
        counts = collections.Counter(seg)
        denom = max(len(seg), 1)
        vectors.append([counts[w] / denom for w in vocab])
    similarities = []
    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):
            a, b = vectors[i], vectors[j]
            dot = sum(x * y for x, y in zip(a, b))
            na = math.sqrt(sum(x * x for x in a))
            nb = math.sqrt(sum(y * y for y in b))
            similarities.append(dot / (na * nb) if na and nb else 0.0)
    stability = _safe_mean(similarities)
    return stability, _clamp((stability - 0.72) / 0.25)


def _burst_regularity_signal(tokens: list[str]) -> tuple[float, float]:
    """يقيس انتظام المسافات بين تكرارات الكلمات المهمة."""
    positions = collections.defaultdict(list)
    for idx, tok in enumerate(tokens):
        if tok not in _STYLE_STOPWORDS and len(tok) >= 4:
            positions[tok].append(idx)
    cvs = []
    for pos in positions.values():
        if len(pos) < 4:
            continue
        gaps = [b - a for a, b in zip(pos, pos[1:])]
        mean = _safe_mean(gaps)
        if mean > 0:
            cvs.append(_safe_std(gaps) / mean)
    if not cvs:
        return 0.0, 0.0
    median_cv = _percentile(cvs, 0.50)
    regularity = _clamp((0.92 - median_cv) / 0.72)
    return median_cv, regularity


def _char_repetition_signal(text: str) -> tuple[float, float, float]:
    compact = re.sub(r'\s+', ' ', (text or '').lower()).strip()
    if len(compact) < 220:
        return 0.0, 0.0, 0.0
    grams = [compact[i:i + 5] for i in range(len(compact) - 4) if compact[i:i + 5].strip()]
    counts = collections.Counter(grams)
    repeated = sum(max(0, c - 1) for c in counts.values()) / max(len(grams), 1)
    entropy = _normalized_entropy(counts)
    score = _clamp((repeated - 0.18) / 0.32)
    if entropy > 0.94:
        score *= 0.75
    return repeated, entropy, score


def _compute_stylometric_features(text: str) -> dict:
    normalized = _normalize_style_text(text)
    lower = normalized.lower()
    tokens = _style_tokens(normalized)
    sentences = _split_analysis_sentences(normalized)
    paragraphs = _split_analysis_paragraphs(text)
    n_words = len(tokens)
    n_sents = len(sentences)

    phrase_data = _collect_weighted_phrase_hits(lower)
    t2_total, t2_matched = _collect_unique_pattern_matches(lower, T2_PATTERNS)

    sent_lengths = [len(_style_tokens(s)) for s in sentences]
    avg_len = _safe_mean(sent_lengths)
    sent_cv = (_safe_std(sent_lengths) / avg_len) if avg_len > 0 else 0.0
    sent_reliability = min(1.0, n_sents / 12.0)
    sentence_uniformity = _clamp((0.66 - sent_cv) / 0.48) * sent_reliability

    para_lengths = [len(_style_tokens(p)) for p in paragraphs]
    para_mean = _safe_mean(para_lengths)
    para_cv = (_safe_std(para_lengths) / para_mean) if para_mean > 0 else 0.0
    para_reliability = min(1.0, len(para_lengths) / 7.0)
    paragraph_uniformity = _clamp((0.76 - para_cv) / 0.58) * para_reliability

    ngram_ratio, ngram_signal = _ngram_repetition_signal(sentences)
    opener_ratio, opener_signal = _opener_repetition_signal(sentences)
    template_ratio, template_score = _template_repetition_signal(sentences)
    clause_mean, clause_cv, clause_score = _clause_rhythm_signal(sentences)
    transition_total, transition_unique, transition_density, transition_score = _transition_signal(lower, n_sents)
    punct_cv, punct_regularity, punct_types = _punctuation_regularity_signal(sentences)
    hapax_ratio, root_ttr, lexical_smoothness = _lexical_smoothness_signal(tokens)
    mattr, mattr_cv = _moving_ttr(tokens)
    function_stability, function_stability_score = _function_word_stability(tokens)
    burst_cv, burst_score = _burst_regularity_signal(tokens)
    char_repeat_ratio, char_entropy, char_repeat_score = _char_repetition_signal(normalized)

    self_ref = len(re.findall(
        r'\b(?:the|this)\s+(?:study|paper|article|experiment|research|work|prototype|system|approach|method|model|framework|analysis)\b',
        lower
    ))

    fw = collections.Counter(w for w in tokens if len(w) >= 5 and w not in _STYLE_STOPWORDS)
    top_kw_count = fw.most_common(1)[0][1] if fw else 0
    top_kw_word = fw.most_common(1)[0][0] if fw else ''
    top10_share = sum(c for _, c in fw.most_common(10)) / max(sum(fw.values()), 1)
    lexical_concentration = _clamp((top10_share - 0.12) / 0.28)

    phrase_density = phrase_data['weighted_hits'] / max(n_words / 100.0, 1.0)
    pattern_density = t2_total / max(n_sents, 1)
    t1_score = 1.0 - math.exp(-1.90 * phrase_density)
    t2_score = 1.0 - math.exp(-4.60 * pattern_density)

    repetition_score = (
        ngram_signal * 0.25 + opener_signal * 0.18 + template_score * 0.20 +
        burst_score * 0.12 + char_repeat_score * 0.12 + function_stability_score * 0.13
    )
    rhythm_score = (
        sentence_uniformity * 0.29 + paragraph_uniformity * 0.13 +
        clause_score * 0.20 + transition_score * 0.15 +
        punct_regularity * 0.13 + (1.0 - _clamp(mattr_cv / 0.20)) * 0.10
    )
    lexical_score = (
        lexical_smoothness * 0.42 + lexical_concentration * 0.28 +
        function_stability_score * 0.18 + char_repeat_score * 0.12
    )
    style_score = _clamp(repetition_score * 0.43 + rhythm_score * 0.39 + lexical_score * 0.18)

    struct_signal = _clamp(
        0.35 * _clamp((self_ref / max(n_sents, 1) - 0.04) / 0.14) +
        0.23 * opener_signal + 0.22 * template_score + 0.20 * paragraph_uniformity
    )
    struct_boost = min(0.07, struct_signal * 0.07)

    numeric_chars = len(re.findall(r'\d', normalized))
    quote_chars = len(re.findall(r'["“”«»]', normalized))
    parentheses = normalized.count('(') + normalized.count('[')
    numeric_density = numeric_chars / max(len(normalized), 1)
    human_complexity = _clamp(
        (0.045 if punct_types >= 7 else 0.0) +
        (0.035 if quote_chars >= 4 else 0.0) +
        (0.035 if parentheses >= max(3, n_sents // 4) else 0.0) +
        (0.025 if numeric_density >= 0.035 else 0.0) +
        (0.025 if mattr_cv >= 0.13 else 0.0), 0.0, 0.14
    )

    support_signals = [
        sentence_uniformity, paragraph_uniformity, ngram_signal, opener_signal,
        template_score, clause_score, transition_score, punct_regularity,
        lexical_smoothness, function_stability_score, burst_score, char_repeat_score,
    ]
    style_support_count = sum(v >= 0.50 for v in support_signals)
    strong_style_count = sum(v >= 0.68 for v in support_signals)
    evidence_families = (
        int(phrase_data['weighted_hits'] >= 0.75) +
        int(t2_total > 0) +
        int(repetition_score >= 0.48) +
        int(rhythm_score >= 0.52) +
        int(lexical_score >= 0.52) +
        int(struct_signal >= 0.48)
    )

    return {
        'normalized_text': normalized, 'tokens': tokens, 'sentences': sentences,
        'paragraphs': paragraphs, 'n_words': n_words, 'n_sents': n_sents,
        'avg_sent_len': avg_len, 'sent_len_cv': sent_cv,
        'sentence_uniformity': sentence_uniformity,
        'paragraph_len_cv': para_cv, 'paragraph_uniformity': paragraph_uniformity,
        'ngram_repeat_ratio': ngram_ratio, 'ngram_score': ngram_signal,
        'opener_repeat_ratio': opener_ratio, 'opener_score': opener_signal,
        'template_repeat_ratio': template_ratio, 'template_score': template_score,
        'clause_mean': clause_mean, 'clause_cv': clause_cv, 'clause_score': clause_score,
        'transition_total': transition_total, 'transition_unique': transition_unique,
        'transition_density': transition_density, 'transition_score': transition_score,
        'punctuation_cv': punct_cv, 'punctuation_score': punct_regularity,
        'punctuation_types': punct_types, 'hapax_ratio': hapax_ratio,
        'root_ttr': root_ttr, 'mattr': mattr, 'mattr_cv': mattr_cv,
        'lexical_score': _clamp(lexical_score), 'lexical_smoothness': lexical_smoothness,
        'lexical_concentration': lexical_concentration,
        'function_stability': function_stability,
        'function_stability_score': function_stability_score,
        'burst_cv': burst_cv, 'burst_score': burst_score,
        'char_repeat_ratio': char_repeat_ratio, 'char_entropy': char_entropy,
        'char_repeat_score': char_repeat_score,
        'repetition_score': _clamp(repetition_score), 'rhythm_score': _clamp(rhythm_score),
        't1_weighted_hits': phrase_data['weighted_hits'],
        't1_occurrences': phrase_data['occurrence_count'],
        't1_count': phrase_data['unique_count'], 't1_hits': phrase_data['ordered_hits'],
        't1_score': _clamp(t1_score), 't2_total': t2_total,
        't2_matched_raw': t2_matched, 't2_score': _clamp(t2_score),
        'style_score': style_score, 'struct_signal': struct_signal,
        'struct_boost': struct_boost, 'self_ref': self_ref,
        'top_kw': top_kw_word, 'top_kw_count': top_kw_count,
        'human_complexity': human_complexity,
        'style_support_count': style_support_count,
        'strong_style_count': strong_style_count,
        'evidence_families': evidence_families,
    }


def _sigmoid(x: float) -> float:
    if x >= 35:
        return 1.0
    if x <= -35:
        return 0.0
    return 1.0 / (1.0 + math.exp(-x))


def _calibrate_feature_probability(features: dict, local: bool = False) -> tuple[float, float]:
    """معايرة Ensemble متعددة الرؤوس مع بوابات تمنع الإدانة من إشارة واحدة."""
    formula_score = features['t1_score'] * 0.58 + features['t2_score'] * 0.42
    repetition = features['repetition_score']
    rhythm = features['rhythm_score']
    lexical = features['lexical_score']
    structural = features['struct_signal']

    formula_head = _sigmoid(9.4 * (formula_score - 0.16))
    repetition_head = _sigmoid(8.8 * (repetition - 0.36))
    rhythm_head = _sigmoid(8.2 * (rhythm - 0.39))
    lexical_head = _sigmoid(7.8 * (lexical - 0.41))

    heads = [formula_head, repetition_head, rhythm_head, lexical_head]
    head_median = _percentile(heads, 0.50)
    agreement = 1.0 - _clamp(_safe_std(heads) / 0.42)
    independent_support = sum(h >= 0.55 for h in heads)

    risk = (
        formula_head * 0.39 + repetition_head * 0.26 + rhythm_head * 0.21 +
        lexical_head * 0.08 + structural * 0.06
    )
    risk += min(formula_head, max(repetition_head, rhythm_head)) * 0.08
    risk += head_median * agreement * 0.05
    risk -= features['human_complexity']
    probability = _clamp(risk)

    explicit_formula = (
        features['t1_weighted_hits'] >= 0.38 or features['t2_total'] >= 2 or
        (features['t1_weighted_hits'] >= 0.16 and features['t2_total'] >= 1)
    )
    multi_style = features['style_support_count'] >= (3 if local else 2)
    strong_multi_style = features['strong_style_count'] >= (2 if local else 1)

    if not explicit_formula and not multi_style:
        probability = min(probability, 0.42 if local else 0.46)
    elif not explicit_formula and independent_support < 3:
        probability = min(probability, 0.60 if local else 0.64)
    elif features['evidence_families'] <= 1:
        probability = min(probability, 0.54 if local else 0.58)
    elif features['evidence_families'] == 2 and not (explicit_formula or strong_multi_style):
        probability = min(probability, 0.70)

    n_words = features['n_words']
    strong_short_evidence = (
        explicit_formula and features['evidence_families'] >= 2
    ) or (
        strong_multi_style and independent_support >= 3
    )
    if n_words < 35:
        probability = min(probability * (0.96 if strong_short_evidence else 0.80), 0.68)
    elif n_words < 70:
        probability = min(probability * (0.98 if strong_short_evidence else 0.90), 0.82)
    elif n_words < 130 and not local:
        probability = min(probability * (0.99 if strong_short_evidence else 0.97), 0.88)

    return _clamp(probability), formula_score


def _ai_fingerprint_score(text: str) -> dict:
    prep = _prepare_analysis_text(text)
    analyzed_text = prep['analysis_text']
    features = _compute_stylometric_features(analyzed_text)
    global_probability, formula_score = _calibrate_feature_probability(features)

    chunks = _build_analysis_chunks(features['sentences'])
    chunk_scores = []
    chunk_words = []
    for chunk in chunks:
        chunk_features = _compute_stylometric_features(chunk)
        chunk_probability, _ = _calibrate_feature_probability(chunk_features, local=True)
        chunk_scores.append(chunk_probability)
        chunk_words.append(max(chunk_features['n_words'], 1))

    if len(chunk_scores) >= 2:
        median_score = _percentile(chunk_scores, 0.50)
        q75_score = _percentile(chunk_scores, 0.75)
        q90_score = _percentile(chunk_scores, 0.90)
        top_count = max(1, int(math.ceil(len(chunk_scores) * 0.25)))
        top_mean = _safe_mean(sorted(chunk_scores, reverse=True)[:top_count])
        high_share = sum(s >= 0.62 for s in chunk_scores) / len(chunk_scores)
        medium_share = sum(s >= 0.42 for s in chunk_scores) / len(chunk_scores)
        weighted_mean = sum(s * w for s, w in zip(chunk_scores, chunk_words)) / max(sum(chunk_words), 1)
        dispersion = _safe_std(chunk_scores)

        final = (
            global_probability * 0.34 + weighted_mean * 0.20 + median_score * 0.17 +
            q75_score * 0.17 + q90_score * 0.07 + top_mean * 0.05
        )
        if high_share >= 0.45:
            final += min(0.075, (high_share - 0.45) * 0.20)
        elif high_share == 0 and medium_share < 0.30:
            final -= 0.035
        if dispersion > 0.28 and high_share < 0.35:
            final -= min(0.045, (dispersion - 0.28) * 0.18)
    else:
        median_score = q75_score = q90_score = top_mean = global_probability
        weighted_mean = global_probability
        high_share = float(global_probability >= 0.62)
        medium_share = float(global_probability >= 0.42)
        dispersion = 0.0
        final = global_probability

    if features['evidence_families'] == 0:
        final = min(final, 0.30)
    elif features['evidence_families'] == 1:
        final = min(final, 0.52)
    elif features['evidence_families'] == 2 and features['style_support_count'] < 3:
        final = min(final, 0.68)

    n_words = max(features['n_words'], 1)
    n_sents = max(features['n_sents'], 1)
    strong_document_evidence = (
        features['evidence_families'] >= 3 and
        (features['t1_score'] >= 0.68 or features['t2_score'] >= 0.52)
    ) or (
        features['style_support_count'] >= 5 and features['strong_style_count'] >= 2
    )
    if n_words < 80:
        final = min(final * (0.99 if strong_document_evidence else 0.92), 0.82)
    elif n_words < 150:
        final = min(final * (1.0 if strong_document_evidence else 0.97), 0.90)
    final = _clamp(final)

    length_factor = min(1.0, n_words / 950.0)
    chunk_factor = min(1.0, len(chunk_scores) / 6.0)
    diversity_factor = min(1.0, features['evidence_families'] / 5.0)
    agreement_factor = 1.0 - _clamp(dispersion / 0.34)
    confidence = _clamp(
        0.10 + 0.36 * length_factor + 0.18 * chunk_factor +
        0.22 * diversity_factor + 0.14 * agreement_factor,
        0.05, 0.98
    )

    if final >= 0.60:
        decision, verdict, color = 'STRONG_SIGNALS', 'مؤشرات متعددة قوية — يلزم تحقق بشري', '#c0392b'
    elif final >= 0.42:
        decision, verdict, color = 'HIGH_SIGNALS', 'مؤشرات متعددة مرتفعة — يحتاج مراجعة', '#e67e22'
    elif final >= 0.26:
        decision, verdict, color = 'MIXED', 'نمط مختلط — لا يكفي للحكم منفرداً', '#f39c12'
    elif final >= 0.12:
        decision, verdict, color = 'LIMITED_SIGNALS', 'مؤشرات محدودة أو غير متسقة', '#27ae60'
    else:
        decision, verdict, color = 'NO_CLEAR_SIGNAL', 'لا توجد مؤشرات كافية للحكم', '#2ecc71'

    percentage = round(final * 100.0, 1)
    t2_matched = [(count, pattern[:60]) for pattern, count in features['t2_matched_raw'][:8]]

    return {
        'engine_version': AI_ENGINE_VERSION,
        'score': round(final, 4),
        'raw_score_before_safety_gates': round(global_probability, 4),
        'percentage': percentage,
        'display_percentage': _format_percentage(percentage),
        'human_score': round((1.0 - final) * 100.0, 1),
        'confidence': round(confidence, 4),
        'confidence_percentage': round(confidence * 100.0, 1),
        'decision': decision, 'verdict': verdict, 'color': color,
        't1_count': features['t1_count'],
        't1_occurrences': features['t1_occurrences'],
        't1_weighted_hits': round(features['t1_weighted_hits'], 3),
        't1_score': round(features['t1_score'], 4),
        't1_hits': features['t1_hits'][:12],
        't2_total': features['t2_total'],
        't2_hit_ratio': round(features['t2_total'] / n_sents, 4),
        't2_score': round(features['t2_score'], 4), 't2_matched': t2_matched,
        'style_score': round(features['style_score'], 4),
        'avg_sent_len': round(features['avg_sent_len'], 1),
        'sent_len_cv': round(features['sent_len_cv'], 4),
        'sentence_uniformity': round(features['sentence_uniformity'], 4),
        'paragraph_uniformity': round(features['paragraph_uniformity'], 4),
        'ngram_repeat_ratio': round(features['ngram_repeat_ratio'], 4),
        'ngram_score': round(features['ngram_score'], 4),
        'opener_repeat_ratio': round(features['opener_repeat_ratio'], 4),
        'opener_score': round(features['opener_score'], 4),
        'template_repeat_ratio': round(features['template_repeat_ratio'], 4),
        'template_score': round(features['template_score'], 4),
        'clause_score': round(features['clause_score'], 4),
        'function_stability_score': round(features['function_stability_score'], 4),
        'burst_score': round(features['burst_score'], 4),
        'char_repeat_score': round(features['char_repeat_score'], 4),
        'transition_density': round(features['transition_density'], 4),
        'transition_score': round(features['transition_score'], 4),
        'lexical_hapax_ratio': round(features['hapax_ratio'], 4),
        'lexical_score': round(features['lexical_score'], 4),
        'punctuation_score': round(features['punctuation_score'], 4),
        'struct_boost': round(features['struct_boost'], 4),
        'self_ref': features['self_ref'], 'top_kw': features['top_kw'],
        'top_kw_count': features['top_kw_count'], 'n_words': n_words,
        'n_sents': n_sents, 'chunk_count': len(chunk_scores),
        'chunk_scores': [round(s * 100.0, 1) for s in chunk_scores],
        'chunk_median': round(median_score * 100.0, 1),
        'chunk_q75': round(q75_score * 100.0, 1),
        'chunk_q90': round(q90_score * 100.0, 1),
        'high_risk_chunk_share': round(high_share * 100.0, 1),
        'medium_risk_chunk_share': round(medium_share * 100.0, 1),
        'chunk_dispersion': round(dispersion, 4),
        'evidence_families': features['evidence_families'],
        'style_support_count': features['style_support_count'],
        'strong_style_count': features['strong_style_count'],
        'original_words': prep['original_words'],
        'reference_words_excluded': prep['reference_words_excluded'],
        'inline_citation_words_removed': prep['inline_citation_words_removed'],
        'reference_section_found': prep['reference_section_found'],
        'reference_header_found': prep['reference_header_found'],
        'analysis_text': analyzed_text,
        'breakdown': {
            'T1 (إشارات موزونة)': round(features['t1_score'] * 0.58 * 0.39, 4),
            'T2 (أنماط جملة)': round(features['t2_score'] * 0.42 * 0.39, 4),
            'Style (قياسات أسلوبية)': round(features['style_score'] * 0.55, 4),
            'Struct (بنية)': round(features['struct_signal'] * 0.06, 4),
        },
    }


def _score_paragraph_for_highlight(para: str) -> dict:
    """تظليل محلي محافظ: لا يعتمد على عبارة أكاديمية شائعة منفردة."""
    raw_text = (para or '').strip()
    if not raw_text or _is_reference_header(raw_text) or _is_reference_line(raw_text):
        return {
            'text': '', 'word_count': 0, 't1_count': 0, 't2_total': 0,
            'self_ref': 0, 'style_score': 0.0, 'evidence_score': 0.0,
            'density': 0.0, 'explicit_signal': False, 'signal_tier': 'none',
        }

    text = _strip_inline_citations(raw_text)
    features = _compute_stylometric_features(text)
    probability, _ = _calibrate_feature_probability(features, local=True)
    n_words = features['n_words']

    strong_formula = (
        features['t1_weighted_hits'] >= 0.60 or features['t2_total'] >= 2 or
        (features['t1_weighted_hits'] >= 0.30 and features['t2_total'] >= 1)
    )
    multi_style = (
        n_words >= 28 and features['style_support_count'] >= 3 and
        features['evidence_families'] >= 2 and probability >= 0.32
    )
    repeated_structure = (
        n_words >= 38 and features['repetition_score'] >= 0.52 and
        features['rhythm_score'] >= 0.43 and probability >= 0.34
    )
    strong_signal = strong_formula or multi_style or repeated_structure

    # ── طبقة أدلة احتياطية "خفيفة" ──────────────────────────────────────────
    # الطبقة القوية أعلاه محافظة جداً وقد لا تنطبق على أي فقرة حتى لو كانت
    # نسبة الوثيقة الكلية فوق 20%، فينتج تقرير برقم عالٍ بلا أي تظليل فعلي.
    # هذه الطبقة تُستخدم فقط كاحتياط عند اختيار فقرات للتظليل (وليست بديلاً
    # عن الطبقة القوية، بل تُستخدم بعدها وبأولوية أقل) بحيث يبقى التظليل
    # منسجماً مع النسبة المعروضة كلما كانت أعلى من 20%.
    weak_formula = (
        features['t1_weighted_hits'] >= 0.35 or features['t2_total'] >= 1 or
        (features['t1_weighted_hits'] >= 0.18 and n_words >= 18)
    )
    weak_style = (
        n_words >= 22 and features['style_support_count'] >= 2 and probability >= 0.20
    )
    weak_repeat = (
        n_words >= 26 and features['repetition_score'] >= 0.40 and probability >= 0.22
    )
    weak_signal = weak_formula or weak_style or weak_repeat

    if strong_signal:
        signal_tier = 'strong'
    elif weak_signal:
        signal_tier = 'weak'
    else:
        signal_tier = 'none'

    explicit_signal = signal_tier != 'none'

    if not explicit_signal:
        probability = 0.0
    elif signal_tier == 'weak':
        # أدلة أخف: نُبقي الاحتمال محدوداً حتى لا يُعامل كدليل قوي عند الترتيب.
        probability = min(probability, 0.34)
    elif features['t1_occurrences'] + features['t2_total'] == 1 and not (multi_style or repeated_structure):
        probability = min(probability, 0.36)

    density = probability / max(math.sqrt(max(n_words, 1)), 1.0)
    return {
        'text': text, 'word_count': n_words,
        't1_count': features['t1_count'], 't2_total': features['t2_total'],
        'self_ref': features['self_ref'],
        'style_score': round(features['style_score'], 4),
        'evidence_score': round(probability, 6),
        'signal_tier': signal_tier,
        'density': round(density, 6), 'explicit_signal': explicit_signal,
        'style_support_count': features['style_support_count'],
        'ngram_score': round(features['ngram_score'], 4),
        'opener_score': round(features['opener_score'], 4),
        'template_score': round(features['template_score'], 4),
    }


def _merge_adjacent_blocks(blocks, gap_threshold: float = 18.0):
    """
    يدمج الـ blocks النصية المتجاورة رأسياً في فقرة واحدة حقيقية.
    يعيد قائمة من الفقرات، كل فقرة = قائمة line_data مع bbox كل سطر على حدة.
    """
    text_blocks = [b for b in blocks if b.get("type", 0) == 0]
    text_blocks.sort(key=lambda b: b["bbox"][1])

    paragraphs = []

    for block in text_blocks:
        lines = block.get("lines", [])
        line_data = []
        for line in lines:
            spans = line.get("spans", [])
            txt = "".join((sp.get("text", "") or "") for sp in spans).strip()
            if txt:
                line_data.append({
                    'text':  txt,
                    'bbox':  fitz.Rect(line["bbox"]),
                    'y0':    line["bbox"][1],
                    'y1':    line["bbox"][3],
                    # نحفظ span-level data لتحديد نقطة بدء/نهاية دقيقة
                    'spans': line.get("spans", []),
                })
        if not line_data:
            continue

        if paragraphs:
            last_para = paragraphs[-1]
            last_y1   = last_para['lines'][-1]['y1']
            this_y0   = line_data[0]['y0']
            gap       = this_y0 - last_y1
            last_x0   = last_para['lines'][0]['bbox'].x0
            this_x0   = line_data[0]['bbox'].x0
            if gap <= gap_threshold and abs(last_x0 - this_x0) < 40.0:
                last_para['lines'].extend(line_data)
                last_para['full_text'] = " ".join(d['text'] for d in last_para['lines'])
                continue

        paragraphs.append({
            'lines':     line_data,
            'full_text': " ".join(d['text'] for d in line_data),
        })

    return paragraphs


def _sentence_start_x(line_data_item) -> float:
    """
    يجد الـ x الذي تبدأ منه أول جملة في السطر.
    إذا كان السطر يبدأ بحرف كبير بعد نقطة سابقة → نقطة البداية الفعلية للجملة.
    في حالات أخرى نأخذ x0 السطر كما هو.
    """
    return line_data_item['bbox'].x0


def _punct_end_x(line_data_item) -> float:
    """
    يجد الـ x الذي تنتهي عنده آخر علامة ترقيم (. أو ،) في السطر.
    نبحث في الـ spans عن آخر حرف قبل المسافات النهائية.
    إذا لم يوجد → نأخذ x1 السطر كاملاً.
    """
    txt = line_data_item['text'].rstrip()
    if not txt:
        return line_data_item['bbox'].x1
    # آخر حرف هو علامة ترقيم؟
    if re.search(r'[.،,;؟?!]\s*$', txt):
        # نأخذ x1 كاملاً (الترقيم هو الحرف الأخير)
        return line_data_item['bbox'].x1
    return line_data_item['bbox'].x1


def _build_line_rects_turnitin(chunk_lines):
    """
    يبني قائمة من المستطيلات بأسلوب Turnitin:
    - كل سطر له مستطيله المستقل (سطر تلو الآخر)
    - السطر الأول: من بداية الجملة (x0 السطر)
    - السطر الأخير: حتى آخر علامة ترقيم (x1 أو موضع الترقيم)
    - الأسطر الوسطى: من x0 إلى x1 كاملاً
    """
    rects = []
    n = len(chunk_lines)
    for i, ld in enumerate(chunk_lines):
        b = ld['bbox']
        x0 = b.x0
        x1 = b.x1
        y0 = b.y0
        y1 = b.y1

        if i == 0:
            # السطر الأول: من بداية الجملة
            x0 = _sentence_start_x(ld)
        if i == n - 1:
            # السطر الأخير: حتى الترقيم
            x1 = _punct_end_x(ld)

        rects.append(fitz.Rect(x0, y0, x1, y1))
    return rects


def _collect_page_block_candidates(page, in_refs_flag: bool):
    """
    يجمع مرشحات التظليل من متن الصفحة فقط.
    يعيد أيضاً عدد جميع كلمات المتن القابلة للتحليل، وليس كلمات المرشحات فقط.
    """
    candidates = []
    in_refs = in_refs_flag
    analyzable_words = 0

    MIN_LINES = 4
    MAX_LINES = 5
    MIN_LOCAL_EVIDENCE = 0.20        # عتبة الطبقة القوية (كما كانت)
    WEAK_LOCAL_EVIDENCE = 0.12       # عتبة احتياطية أخف، تُستخدم فقط للطبقة الخفيفة

    def _meets_local_threshold(local_res: dict) -> bool:
        tier = local_res.get('signal_tier', 'none')
        if tier == 'strong':
            return local_res['evidence_score'] >= MIN_LOCAL_EVIDENCE
        if tier == 'weak':
            return local_res['evidence_score'] >= WEAK_LOCAL_EVIDENCE
        return False

    try:
        page_dict = page.get_text("dict")
        raw_blocks = page_dict.get("blocks", [])
    except Exception:
        raw_blocks = []

    paragraphs = _merge_adjacent_blocks(raw_blocks)

    for para in paragraphs:
        original_lines = para['lines']
        if not original_lines:
            continue

        # قد يندمج عنوان المراجع مع block سابق أو لاحق؛ نعالج ما قبله فقط.
        header_idx = next(
            (i for i, ld in enumerate(original_lines) if _is_reference_header(ld.get('text', ''))),
            None
        )
        set_refs_after = header_idx is not None

        if in_refs:
            continue

        if header_idx == 0:
            in_refs = True
            continue
        elif header_idx is not None:
            line_data = original_lines[:header_idx]
        else:
            line_data = original_lines

        btext = " ".join(d['text'] for d in line_data).strip()
        if not btext:
            if set_refs_after:
                in_refs = True
            continue

        if _is_reference_line(btext):
            if set_refs_after:
                in_refs = True
            continue

        clean_btext = _strip_inline_citations(btext)
        analyzable_words += _count_text_words(clean_btext)
        total_lines = len(line_data)

        if total_lines < MIN_LINES:
            local = _score_paragraph_for_highlight(btext)
            if local['word_count'] < 4 or not _meets_local_threshold(local):
                if set_refs_after:
                    in_refs = True
                continue

            line_rects = _build_line_rects_turnitin(line_data)
            combined = line_rects[0]
            for r in line_rects[1:]:
                combined = combined | r
            candidates.append({
                'rects': line_rects,
                'rect': combined,
                'text': btext,
                'word_count': local['word_count'],
                'score': local['evidence_score'],
                'density': local['density'],
                'tier': local.get('signal_tier', 'none'),
                't1_count': local['t1_count'],
                't2_total': local['t2_total'],
                'self_ref': local['self_ref'],
                'explicit_signal': local['explicit_signal'],
                'line_count': total_lines,
            })
            if set_refs_after:
                in_refs = True
            continue

        best_candidate = None
        for end_i in range(MIN_LINES - 1, total_lines):
            end_text = line_data[end_i]['text'].rstrip()
            ends_with_punct = bool(re.search(r'[.،,;؟?!]\s*$', end_text))

            for chunk_len in range(MIN_LINES, MAX_LINES + 1):
                start_i = end_i - chunk_len + 1
                if start_i < 0:
                    continue
                chunk_lines = line_data[start_i:end_i + 1]
                chunk_text = " ".join(d['text'] for d in chunk_lines)
                local = _score_paragraph_for_highlight(chunk_text)

                if local['word_count'] < 4 or not _meets_local_threshold(local):
                    continue

                line_rects = _build_line_rects_turnitin(chunk_lines)
                combined = line_rects[0]
                for r in line_rects[1:]:
                    combined = combined | r

                tier = local.get('signal_tier', 'none')
                score_val = local['evidence_score'] * (1.08 if ends_with_punct else 1.0)
                tier_rank = 1 if tier == 'strong' else 0
                best_rank = (
                    (1 if best_candidate['tier'] == 'strong' else 0, best_candidate['score'])
                    if best_candidate is not None else None
                )
                if best_candidate is None or (tier_rank, score_val) > best_rank:
                    best_candidate = {
                        'rects': line_rects,
                        'rect': combined,
                        'text': chunk_text,
                        'word_count': local['word_count'],
                        'score': score_val,
                        'density': local['density'],
                        'tier': tier,
                        't1_count': local['t1_count'],
                        't2_total': local['t2_total'],
                        'self_ref': local['self_ref'],
                        'explicit_signal': local['explicit_signal'],
                        'line_count': len(chunk_lines),
                    }

        if best_candidate is not None:
            candidates.append(best_candidate)

        if set_refs_after:
            in_refs = True

    return candidates, in_refs, analyzable_words


def _select_highlight_plan(orig_doc, target_pct: float):
    """
    يختار فقط الفقرات ذات الدليل الصريح، ويحسب النسبة من جميع كلمات المتن.
    إذا لم توجد أدلة كافية فلن يملأ النسبة قسراً بفقرات عادية.
    """
    pages_candidates = []
    in_refs_global = False
    total_words = 0

    for page_idx in range(len(orig_doc)):
        page = orig_doc[page_idx]
        candidates, in_refs_global, page_words = _collect_page_block_candidates(
            page, in_refs_global
        )
        total_words += page_words
        for item in candidates:
            item['page_idx'] = page_idx
        pages_candidates.extend(candidates)

    total_words = max(total_words, 1)

    # النسبة المخفية *% (0–20%) لا يُسمح معها بأي تظليل مطلقاً.
    if not _highlighting_allowed(target_pct):
        return {
            'plan_by_page': {},
            'total_words': total_words,
            'target_words': 0,
            'covered_words': 0,
            'achieved_pct': 0.0,
            'selected_blocks': 0,
            'available_candidate_words': sum(i['word_count'] for i in pages_candidates),
            'suppressed_low_score': True,
        }

    target_words = int(round(
        total_words * max(0.0, min(100.0, target_pct)) / 100.0
    ))

    ranked = sorted(
        pages_candidates,
        key=lambda x: (
            1 if x.get('tier') == 'strong' else 0,
            x['density'], x['score'], x['t1_count'] + x['t2_total'], -x['word_count']
        ),
        reverse=True
    )

    selected = []
    covered_words = 0
    for item in ranked:
        if target_words > 0 and covered_words >= target_words:
            break
        selected.append(item)
        covered_words += item['word_count']

    plan_by_page = {}
    for item in selected:
        plan_by_page.setdefault(item['page_idx'], []).extend(
            item.get('rects') or [item['rect']]
        )

    achieved_pct = round((covered_words / total_words) * 100.0, 1)

    return {
        'plan_by_page': plan_by_page,
        'total_words': total_words,
        'target_words': target_words,
        'covered_words': covered_words,
        'achieved_pct': achieved_pct,
        'selected_blocks': len(selected),
        'available_candidate_words': sum(i['word_count'] for i in ranked),
        'suppressed_low_score': False,
    }


def generate_report_pdf_from_original(original_pdf_bytes: bytes,
                                       text: str,
                                       doc_name: str = "Document") -> bytes:
    """
    يستخدم ملف PDF الأصلي مباشرة:
    - يحتفظ بكل صفحة كما هي (نص + صور + جداول + تنسيق)
    - يُضيف تظليل أصفر/برتقالي شفاف فوق الفقرات المشبوهة كاملة فقط
    - يجعل مجموع كلمات الفقرات المظللة قريباً من نسبة AI النهائية من كلمات الملف (بدون المراجع)
    - وحدة التظليل هي الفقرة كاملة بكل أسطرها، وليس جزءاً من الجملة أو بعض الأسطر
    - لا يُظلّل قسم المراجع
    - يُضيف صفحة غلاف احترافية في البداية
    - يُضيف صفحة ملخص في النهاية
    - إذا كانت النتيجة *% (0–20%) يُنشئ التقرير بلا أي تظليل نهائياً
    """
    if not FITZ_OK or not RLAB_OK:
        return b""

    result = _ai_fingerprint_score(text)
    pct    = result['percentage']
    today  = datetime.now().strftime("%Y-%m-%d  %H:%M")

    try:
        orig_doc = fitz.open(stream=original_pdf_bytes, filetype="pdf")
    except Exception:
        return b""

    highlight_plan = _select_highlight_plan(orig_doc, pct)
    result['highlight_target_words'] = highlight_plan['target_words']
    result['highlight_covered_words'] = highlight_plan['covered_words']
    result['highlight_total_words'] = highlight_plan['total_words']
    result['highlight_achieved_pct'] = highlight_plan['achieved_pct']
    result['highlight_selected_blocks'] = highlight_plan['selected_blocks']
    result['highlight_suppressed_low_score'] = highlight_plan.get('suppressed_low_score', False)

    cover_buf = io.BytesIO()
    W_pt, H_pt = A4
    cv = rl_canvas.Canvas(cover_buf, pagesize=A4)
    _draw_cover_rl(cv, W_pt, H_pt, result, doc_name, today)
    cv.save()
    cover_buf.seek(0)

    cover_doc = fitz.open(stream=cover_buf.read(), filetype="pdf")

    out_doc = fitz.open()
    out_doc.insert_pdf(cover_doc)

    for page_idx in range(len(orig_doc)):
        out_doc.insert_pdf(orig_doc, from_page=page_idx, to_page=page_idx)
        new_page = out_doc[-1]

        highlights = highlight_plan['plan_by_page'].get(page_idx, [])
        for line_rect in highlights:
            # كل line_rect هو مستطيل سطر مستقل → annotation منفصل (أسلوب Turnitin)
            annot = new_page.add_highlight_annot(line_rect)
            annot.set_colors(stroke=[0.0, 0.75, 1.0])   # أزرق سماوي
            annot.set_opacity(0.40)
            annot.update()

        _stamp_page_header(new_page, page_idx + 1, len(orig_doc), pct, result['color'])

    summary_buf = io.BytesIO()
    cv2 = rl_canvas.Canvas(summary_buf, pagesize=A4)
    _draw_summary_page(cv2, W_pt, H_pt, result, doc_name, today)
    cv2.save()
    summary_buf.seek(0)
    summary_doc = fitz.open(stream=summary_buf.read(), filetype="pdf")
    out_doc.insert_pdf(summary_doc)

    out_buf = io.BytesIO()
    out_doc.save(out_buf, garbage=4, deflate=True)
    orig_doc.close()
    cover_doc.close()
    summary_doc.close()
    out_doc.close()
    return out_buf.getvalue()


def _stamp_page_header(page, page_num: int, total_pages: int, pct: float, col_hex: str):
    """يُضيف شريط معلومات خفي في أعلى كل صفحة"""
    pw = page.rect.width
    ph = page.rect.height

    # شريط علوي شفاف
    strip_rect = fitz.Rect(0, 0, pw, 18)
    page.draw_rect(strip_rect, color=None, fill=(0.04, 0.08, 0.16), fill_opacity=0.82)

    # نص على اليسار
    page.insert_text(
        (6, 13), f"AI Fingerprint Detector  |  AI Score: {_format_percentage(pct)}",
        fontsize=6.5, color=(0.7, 0.85, 1.0)
    )
    # رقم الصفحة على اليمين
    page.insert_text(
        (pw - 55, 13), f"Page {page_num}/{total_pages}",
        fontsize=6.5, color=(0.7, 0.85, 1.0)
    )


def _draw_cover_rl(c, W, H, result, doc_name, doc_date):
    """صفحة الغلاف الاحترافية"""
    pct = result['percentage']

    score_colors = {
        '#c0392b': (0.75, 0.22, 0.17),
        '#e67e22': (0.90, 0.49, 0.13),
        '#f39c12': (0.95, 0.61, 0.07),
        '#27ae60': (0.15, 0.68, 0.38),
        '#2ecc71': (0.18, 0.80, 0.44),
    }
    score_color_rl = score_colors.get(result['color'], (0.75, 0.22, 0.17))

    # خلفية داكنة
    c.setFillColor(HexColor('#060d1a'))
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # زخارف دائرية
    for (cx, cy, r, cr, ca) in [
        (W*0.1, H*0.88, 200, '#00bcd4', 0.05),
        (W*0.9, H*0.12, 170, '#f4a300', 0.04),
        (W*0.78, H*0.70, 120, '#7c3aed', 0.035),
    ]:
        rgb = tuple(int(cr[i:i+2], 16)/255 for i in (1, 3, 5))
        c.setFillColorRGB(*rgb, alpha=ca)
        c.circle(cx, cy, r, fill=1, stroke=0)

    # شبكة نقاط خفيفة
    c.setFillColorRGB(0.2, 0.5, 0.7, alpha=0.08)
    for gx in range(0, int(W), 30):
        for gy in range(0, int(H), 30):
            c.circle(gx, gy, 1.0, fill=1, stroke=0)

    # شرائط علوية
    for i, (col, th) in enumerate([('#00bcd4', 7), ('#f4a300', 4), ('#7c3aed', 2)]):
        offset = sum(t for _, t in [('#00bcd4', 7), ('#f4a300', 4), ('#7c3aed', 2)][:i])
        c.setFillColor(HexColor(col))
        c.rect(0, H - offset - th, W, th, fill=1, stroke=0)

    # شعار دائري
    lcx, lcy = W/2, H - 105
    c.setFillColorRGB(0.0, 0.74, 0.83, alpha=0.12)
    c.circle(lcx, lcy, 52, fill=1, stroke=0)
    c.setFillColor(HexColor('#00bcd4'))
    c.circle(lcx, lcy, 38, fill=1, stroke=0)
    c.setFillColor(HexColor('#060d1a'))
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(lcx, lcy - 7, "AI")

    # عنوان
    c.setFillColor(HexColor('#ffffff'))
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(W/2, H - 170, "AI Fingerprint Detector")
    c.setFillColor(HexColor('#7fb3c8'))
    c.setFont("Helvetica", 11)
    c.drawCentredString(W/2, H - 190, "Academic AI-Style Signal Report")

    # فاصل
    c.setStrokeColor(HexColor('#1e3a5f'))
    c.setLineWidth(0.8)
    c.line(60, H - 210, W - 60, H - 210)

    # دائرة النتيجة
    cx, cy = W/2, H - 340
    c.setFillColorRGB(0.06, 0.10, 0.18, alpha=1.0)
    c.circle(cx, cy, 78, fill=1, stroke=0)
    c.setStrokeColorRGB(*score_color_rl)
    c.setLineWidth(4)
    c.circle(cx, cy, 78, fill=0, stroke=1)
    c.setFillColorRGB(*score_color_rl)
    c.setFont("Helvetica-Bold", 46)
    c.drawCentredString(cx, cy - 16, _format_percentage(pct))
    c.setFillColor(HexColor('#aaaaaa'))
    c.setFont("Helvetica", 9)
    c.drawCentredString(cx, cy + 30, "AI-Style Signal Score")

    # الحكم
    c.setFillColorRGB(*score_color_rl)
    c.setFont("Helvetica-Bold", 17)
    c.drawCentredString(W/2, H - 466, result['verdict'])
    c.setFillColor(HexColor('#7fb3c8'))
    c.setFont("Helvetica", 10)
    c.drawCentredString(W/2, H - 484,
        f"Human: {_format_human_percentage(pct, result['human_score'])}    |    AI: {_format_percentage(pct)}")

    # شريط اللون
    bx, by = 55, H - 538
    bw, bh = W - 110, 18
    for sc, s0, s1 in [
        ('#2ecc71', 0.0, 0.22), ('#27ae60', 0.22, 0.42),
        ('#f39c12', 0.42, 0.62), ('#e67e22', 0.62, 0.80),
        ('#c0392b', 0.80, 1.00),
    ]:
        sx = bx + bw * s0
        sw = bw * (s1 - s0) - 1
        c.setFillColor(HexColor(sc))
        c.roundRect(sx, by, sw, bh, 3, fill=1, stroke=0)

    ind_x = bx + bw * (pct / 100.0)
    c.setFillColor(HexColor('#ffffff'))
    c.setStrokeColor(HexColor('#000000'))
    c.setLineWidth(1.0)
    p = c.beginPath()
    p.moveTo(ind_x, by - 2)
    p.lineTo(ind_x - 6, by - 13)
    p.lineTo(ind_x + 6, by - 13)
    p.close()
    c.drawPath(p, fill=1, stroke=1)

    # صناديق الإحصائيات
    sy = H - 628
    sw_each = (W - 110) / 4
    for i, (lbl, val, vc) in enumerate([
        ("الكلمات",   f"{result['n_words']:,}", '#00bcd4'),
        ("الجمل",     f"{result['n_sents']}",   '#7c3aed'),
        ("T1 إشارات", f"{result['t1_count']}",  '#f4a300'),
        ("T2 أنماط",  f"{result['t2_total']}",  '#e74c3c'),
    ]):
        bx2 = 55 + i * sw_each
        c.setFillColor(HexColor('#0b1829'))
        c.roundRect(bx2 + 3, sy - 32, sw_each - 6, 52, 7, fill=1, stroke=0)
        c.setStrokeColor(HexColor(vc))
        c.setLineWidth(0.8)
        c.roundRect(bx2 + 3, sy - 32, sw_each - 6, 52, 7, fill=0, stroke=1)
        c.setFillColor(HexColor(vc))
        c.setFont("Helvetica-Bold", 17)
        c.drawCentredString(bx2 + sw_each/2, sy + 4, val)
        c.setFillColor(HexColor('#888888'))
        c.setFont("Helvetica", 8)
        c.drawCentredString(bx2 + sw_each/2, sy - 20, lbl)

    # معلومات المستند
    iy = H - 708
    c.setFillColor(HexColor('#0b1829'))
    c.roundRect(55, iy - 18, W - 110, 52, 8, fill=1, stroke=0)
    c.setStrokeColor(HexColor('#1e3a5f'))
    c.setLineWidth(0.5)
    c.roundRect(55, iy - 18, W - 110, 52, 8, fill=0, stroke=1)
    c.setFillColor(HexColor('#aaaaaa'))
    c.setFont("Helvetica", 8.5)
    c.drawString(70, iy + 20, f"Document: {doc_name[:55]}")
    c.drawString(70, iy + 7,  f"Analysis Date: {doc_date}")
    h_pct = result.get('highlight_achieved_pct')
    if result.get('highlight_suppressed_low_score'):
        c.drawString(70, iy - 6, "Engine: AI Fingerprint v4.0  |  No highlighting for masked score *%")
    elif h_pct is not None:
        c.drawString(70, iy - 6,  f"Engine: AI Fingerprint v4.0  |  Highlighted coverage: {_format_percentage(h_pct, mask_low=False)}")
    else:
        c.drawString(70, iy - 6,  "Engine: AI Fingerprint v4.0  |  Original format preserved")

    # شريط أسفل
    c.setFillColor(HexColor('#060d1a'))
    c.rect(0, 0, W, 26, fill=1, stroke=0)
    c.setFillColor(HexColor('#00bcd4'))
    c.rect(0, 25, W, 1.5, fill=1, stroke=0)
    c.setFillColor(HexColor('#555'))
    c.setFont("Helvetica", 7)
    c.drawCentredString(W/2, 8,
        "AI Fingerprint Detector  •  Confidential Analysis Report  •  Academic & Research Use Only")


def _draw_summary_page(c, W, H, result, doc_name, doc_date):
    """صفحة ملخص الإشارات"""
    c.setFillColor(HexColor('#f8fbff'))
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # رأس
    c.setFillColor(HexColor('#060d1a'))
    c.rect(0, H - 40, W, 40, fill=1, stroke=0)
    c.setFillColor(HexColor('#00bcd4'))
    c.rect(0, H - 41, W, 1.5, fill=1, stroke=0)
    c.setFillColor(HexColor('#aaaaaa'))
    c.setFont("Helvetica", 8)
    c.drawString(18, H - 24, "AI Fingerprint Detector")
    c.drawRightString(W - 18, H - 24, f"Summary  |  AI Score: {_format_percentage(result['percentage'])}")

    y = H - 70
    c.setFillColor(HexColor('#00bcd4'))
    c.setFont("Helvetica-Bold", 14)
    c.drawString(52, y, "Detected Style Signals Summary")
    y -= 8
    c.setStrokeColor(HexColor('#1e3a5f'))
    c.setLineWidth(0.8)
    c.line(52, y, W - 52, y)
    y -= 20

    # سياسة التظليل
    low_score_no_highlight = bool(result.get("highlight_suppressed_low_score")) or not _highlighting_allowed(result.get('percentage', 0))
    if low_score_no_highlight:
        c.setFillColor(HexColor('#e8f5e9'))
        c.roundRect(52, y - 5, W - 104, 22, 4, fill=1, stroke=0)
        c.setStrokeColor(HexColor('#27ae60'))
        c.setLineWidth(0.6)
        c.roundRect(52, y - 5, W - 104, 22, 4, fill=0, stroke=1)
        c.setFillColor(HexColor('#1b5e20'))
        c.setFont("Helvetica-Bold", 9)
        c.drawString(58, y + 6, "No highlighting applied: masked score *% (0–20%).")
        y -= 30
    else:
        c.setFillColor(HexColor('#fff9c4'))
        c.roundRect(52, y - 4, 14, 12, 2, fill=1, stroke=0)
        c.setStrokeColor(HexColor('#f4a300'))
        c.setLineWidth(0.5)
        c.roundRect(52, y - 4, 14, 12, 2, fill=0, stroke=1)
        c.setFillColor(HexColor('#555'))
        c.setFont("Helvetica", 9)
        c.drawString(70, y + 4, "Highlighted text = selected suspicious lines; references are excluded.")
        y -= 22

        # نسبة التغطية الفعلية للتظليل
        h_pct = result.get("highlight_achieved_pct")
        h_cov = result.get("highlight_covered_words")
        h_tot = result.get("highlight_total_words")
        if h_pct is not None and h_cov is not None and h_tot is not None:
            c.setFillColor(HexColor('#0b1829'))
            c.roundRect(52, y - 5, W - 104, 18, 4, fill=1, stroke=0)
            c.setFillColor(HexColor('#00bcd4'))
            c.setFont("Helvetica-Bold", 9)
            c.drawString(58, y + 5, f"Highlighted coverage (non-references): {_format_percentage(h_pct, mask_low=False)}  |  {h_cov:,} / {h_tot:,} words")
            y -= 26

    # عبارات T1
    if result['t1_hits']:
        c.setFillColor(HexColor('#e67e22'))
        c.setFont("Helvetica-Bold", 11)
        c.drawString(52, y, f"T1 Phrases Detected ({result['t1_count']} hits):")
        y -= 16

        col_idx = 0
        col_w = (W - 110) / 2
        col_x = 52

        for hit in result['t1_hits']:
            if y < 60:
                break
            tag_w = min(len(hit) * 5.5 + 14, col_w - 8)
            c.setFillColor(HexColor('#fff3e0'))
            c.roundRect(col_x, y - 3, tag_w, 14, 4, fill=1, stroke=0)
            c.setStrokeColor(HexColor('#e65100'))
            c.setLineWidth(0.4)
            c.roundRect(col_x, y - 3, tag_w, 14, 4, fill=0, stroke=1)
            c.setFillColor(HexColor('#bf360c'))
            c.setFont("Helvetica", 8)
            c.drawString(col_x + 5, y + 4, hit[:45])
            col_idx += 1
            if col_idx % 2 == 0:
                col_x = 52
                y -= 22
            else:
                col_x = 52 + col_w

        y -= 28

    # أنماط T2
    if result['t2_matched'] and y > 100:
        c.setFillColor(HexColor('#3498db'))
        c.setFont("Helvetica-Bold", 11)
        c.drawString(52, y, f"T2 Patterns Detected ({result['t2_total']} matches):")
        y -= 16

        for cnt, pat in result['t2_matched'][:6]:
            if y < 60:
                break
            c.setFillColor(HexColor('#0b1829'))
            c.roundRect(52, y - 3, W - 110, 14, 3, fill=1, stroke=0)
            c.setFillColor(HexColor('#00bcd4'))
            c.setFont("Helvetica-Bold", 8)
            c.drawString(58, y + 4, f"×{cnt}")
            c.setFillColor(HexColor('#aaaaaa'))
            c.setFont("Helvetica", 7.5)
            c.drawString(78, y + 4, pat[:75])
            y -= 20

    # ذيل
    c.setFillColor(HexColor('#060d1a'))
    c.rect(0, 0, W, 26, fill=1, stroke=0)
    c.setFillColor(HexColor('#f4a300'))
    c.rect(0, 25, W, 1, fill=1, stroke=0)
    c.setFillColor(HexColor('#555'))
    c.setFont("Helvetica", 7)
    c.drawCentredString(W/2, 8, "AI Fingerprint Detector — Confidential Analysis Report")


def _para_is_suspicious(para: str) -> bool:
    """
    يحدد إذا كانت الفقرة مشبوهة (AI) بناءً على نفس منهجية التظليل الأصلية.
    يُستخدم في تقرير DOCX/النص المباشر فقط.
    """
    local = _score_paragraph_for_highlight(para)
    tier = local.get('signal_tier', 'none')
    if tier == 'strong':
        return local['evidence_score'] >= 0.20
    if tier == 'weak':
        return local['evidence_score'] >= 0.12
    return False


def generate_report_pdf_text_only(text: str, doc_name: str = "Document") -> bytes:
    """
    نسخة احتياطية: عندما لا يكون هناك ملف PDF أصلي.
    تُنشئ تقريراً نصياً مع تظليل الفقرات المشبوهة.
    المراجع لا تُظلَّل.
    """
    if not RLAB_OK:
        return b""

    buf    = io.BytesIO()
    result = _ai_fingerprint_score(text)
    pct    = result['percentage']
    col_h  = result['color']
    allow_highlighting = _highlighting_allowed(pct)
    result['highlight_suppressed_low_score'] = not allow_highlighting
    result['highlight_target_words'] = 0 if not allow_highlighting else None
    result['highlight_covered_words'] = 0 if not allow_highlighting else None
    result['highlight_total_words'] = result.get('n_words', 0)
    result['highlight_achieved_pct'] = 0.0 if not allow_highlighting else None
    result['highlight_selected_blocks'] = 0 if not allow_highlighting else None
    today  = datetime.now().strftime("%Y-%m-%d  %H:%M")

    W, H   = A4
    ML, MR = 52, 52
    MT, MB = 45, 40
    TW     = W - ML - MR
    LH     = 13.5
    PS     = 9.0

    c = rl_canvas.Canvas(buf, pagesize=A4)

    # غلاف
    _draw_cover_rl(c, W, H, result, doc_name, today)
    c.showPage()

    # صفحات المحتوى
    page_num = 2
    y = H - MT - 36

    # رأس الصفحة
    _rl_page_header(c, W, H, page_num, doc_name, pct)

    # legend
    c.setFillColor(HexColor('#00bcd4'))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(ML, y, "Document Content Analysis")
    y -= 7
    c.setStrokeColor(HexColor('#1e3a5f'))
    c.setLineWidth(0.7)
    c.line(ML, y, W - MR, y)
    y -= 18

    lx = ML
    for lcol, border, ltxt in [
        ('#fff9c4', '#f4a300', '   AI-Suspicious (orange highlight)'),
        ('#f8fafc', '#dce8f5', '   Normal / Human text'),
        ('#f3e5f5', '#c897d8', '   References — not analyzed'),
    ]:
        c.setFillColor(HexColor(lcol))
        c.roundRect(lx, y - 3, 14, 10, 2, fill=1, stroke=0)
        c.setStrokeColor(HexColor(border))
        c.setLineWidth(0.4)
        c.roundRect(lx, y - 3, 14, 10, 2, fill=0, stroke=1)
        c.setFillColor(HexColor('#333333'))
        c.setFont("Helvetica", 8)
        c.drawString(lx + 17, y + 3, ltxt)
        lx += 158
    y -= 22

    # فقرات النص
    paras_raw = [p.strip() for p in text.split('\n') if p.strip()]
    in_refs = False
    para_groups = []
    for para in paras_raw:
        if _is_reference_header(para):
            in_refs = True
        is_ref  = in_refs or _is_reference_line(para)
        is_susp = allow_highlighting and (not is_ref) and _para_is_suspicious(para)
        para_groups.append((para, is_susp, is_ref))

    def new_page_rl():
        nonlocal page_num, y
        _rl_page_footer(c, W, page_num)
        c.showPage()
        page_num += 1
        y = H - MT - 40
        _rl_page_header(c, W, H, page_num, doc_name, pct)

    def draw_para_rl(txt, is_susp, is_ref):
        nonlocal y

        if is_ref:
            bg, border, tc, fn, fs = '#f3e5f5', '#c897d8', '#6a1b9a', "Helvetica-Oblique", 9.0
        elif is_susp:
            bg, border, tc, fn, fs = '#fff9c4', '#f4a300', '#5d3a00', "Helvetica", 10.5
        else:
            bg, border, tc, fn, fs = '#f8fafc', '#dce8f5', '#1a1a2a', "Helvetica", 10.5

        avg_char_w = fs * 0.52
        max_c = max(10, int(TW / avg_char_w))
        words_ = txt.split()
        lines  = []
        cur    = ""
        for w in words_:
            test = (cur + " " + w).strip()
            if len(test) <= max_c:
                cur = test
            else:
                if cur: lines.append(cur)
                cur = w
        if cur: lines.append(cur)

        bh = len(lines) * LH + 8

        if y - bh < MB + 26:
            new_page_rl()

        # خلفية
        c.setFillColor(HexColor(bg))
        c.roundRect(ML - 5, y - bh + 4, TW + 10, bh + 2, 4, fill=1, stroke=0)
        if not is_ref:
            c.setStrokeColor(HexColor(border))
            c.setLineWidth(0.3)
            c.roundRect(ML - 5, y - bh + 4, TW + 10, bh + 2, 4, fill=0, stroke=1)

        # شريط جانبي للمشبوه — مثل تظليل Turnitin
        if is_susp:
            c.setFillColor(HexColor('#f4a300'))
            c.rect(ML - 5, y - bh + 4, 4, bh + 2, fill=1, stroke=0)

        # النص
        c.setFillColor(HexColor(tc))
        c.setFont(fn, fs)
        ty = y
        for line in lines:
            if ty < MB + 26:
                new_page_rl()
                ty = y
            c.drawString(ML + 6, ty, line)
            ty -= LH

        # علامة AI
        if is_susp:
            tag_y = y + 1
            c.setFillColor(HexColor('#f4a300'))
            c.roundRect(W - MR - 28, tag_y - 1, 28, 12, 3, fill=1, stroke=0)
            c.setFillColor(HexColor('#ffffff'))
            c.setFont("Helvetica-Bold", 6.5)
            c.drawCentredString(W - MR - 14, tag_y + 4, "AI ✓")

        y = ty - PS

    for pt, ps_, pr in para_groups:
        draw_para_rl(pt, ps_, pr)

    # صفحة ملخص
    _rl_page_footer(c, W, page_num)
    c.showPage()
    page_num += 1
    _draw_summary_page(c, W, H, result, doc_name, today)
    c.save()
    return buf.getvalue()


def _rl_page_header(c, W, H, page_num, doc_name, pct):
    c.setFillColor(HexColor('#060d1a'))
    c.rect(0, H - 30, W, 30, fill=1, stroke=0)
    c.setFillColor(HexColor('#00bcd4'))
    c.rect(0, H - 31, W, 1.5, fill=1, stroke=0)
    c.setFillColor(HexColor('#aaaaaa'))
    c.setFont("Helvetica", 7.5)
    c.drawString(18, H - 19, "AI Fingerprint Detector")
    c.drawCentredString(W/2, H - 19, doc_name[:42])
    c.drawRightString(W - 18, H - 19, f"AI: {_format_percentage(pct)}  |  p.{page_num}")


def _rl_page_footer(c, W, page_num):
    c.setFillColor(HexColor('#060d1a'))
    c.rect(0, 0, W, 24, fill=1, stroke=0)
    c.setFillColor(HexColor('#f4a300'))
    c.rect(0, 23, W, 1, fill=1, stroke=0)
    c.setFillColor(HexColor('#555'))
    c.setFont("Helvetica", 7)
    c.drawCentredString(W/2, 7, f"Page {page_num}  —  AI Fingerprint Detector  —  Confidential")


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS: قراءة الملفات
# ══════════════════════════════════════════════════════════════════════════════

def extract_text_from_pdf(file_bytes: bytes) -> str:
    if not FITZ_OK: return ""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        return "\n".join(page.get_text() for page in doc)
    except Exception:
        return ""


def extract_text_from_docx(file_bytes: bytes) -> str:
    if not DOCX_OK:
        return ""
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        return "\n".join(
            p.text for p in _iter_docx_paragraphs(doc) if (p.text or "").strip()
        )
    except Exception:
        return ""



def _iter_docx_paragraphs(container):
    """
    يمر على فقرات Word والجداول بترتيب ظهورها الحقيقي في المستند.
    هذا يمنع انتقال حالة "داخل المراجع" إلى أجزاء سابقة بسبب ترتيب غير صحيح.
    """
    try:
        if isinstance(container, _Document):
            parent_element = container.element.body
            parent = container
        elif isinstance(container, _Cell):
            parent_element = container._tc
            parent = container
        else:
            for p in getattr(container, "paragraphs", []):
                yield p
            return

        for child in parent_element.iterchildren():
            if isinstance(child, CT_P):
                yield Paragraph(child, parent)
            elif isinstance(child, CT_Tbl):
                table = Table(child, parent)
                seen_cells = set()
                for row in table.rows:
                    for cell in row.cells:
                        # الخلايا المدمجة قد تظهر أكثر من مرة؛ لا نكرر نصها.
                        # احتفظ بعنصر XML نفسه، لا بـ id رقمي قد تعيد بايثون استخدامه
                        # أثناء إنشاء wrappers للخلايا؛ إعادة استخدام id كانت تُسقط خلايا صحيحة.
                        cell_key = cell._tc
                        if cell_key in seen_cells:
                            continue
                        seen_cells.add(cell_key)
                        yield from _iter_docx_paragraphs(cell)
    except Exception:
        return


def _set_run_docx_shading(run, fill: str = "9FE2FF"):
    """
    يضيف تظليل خلفية حقيقي على run داخل DOCX
    للحفاظ على النص الأصلي وتنسيقه بالكامل.
    """
    try:
        r_pr = run._r.get_or_add_rPr()
        shd = r_pr.find(qn("w:shd"))
        if shd is None:
            shd = OxmlElement("w:shd")
            r_pr.append(shd)
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), fill)
    except Exception:
        pass


def generate_highlighted_docx_bytes(docx_bytes: bytes,
                                    text: str = "",
                                    doc_name: str = "Document") -> bytes:
    """
    يطبّق نفس مبدأ PDF لكن مباشرة على ملف Word الأصلي:
    - لا يعيد كتابة التقرير كنص جديد
    - يحتفظ بالتنسيق والجداول والأشكال كما هي
    - يظلل الفقرات المشبوهة داخل DOCX نفسه
    - يستثني قسم المراجع من التظليل
    """
    if not DOCX_OK:
        return b""

    # احتياطياً: إذا كانت النتيجة *% نعيد ملف Word الأصلي بلا أي تعديل.
    if text and not _highlighting_allowed(_ai_fingerprint_score(text).get('percentage', 0)):
        return docx_bytes

    try:
        doc = docx.Document(io.BytesIO(docx_bytes))
    except Exception:
        return b""

    in_refs = False
    highlighted = 0

    try:
        for para in _iter_docx_paragraphs(doc):
            para_text = (para.text or "").strip()
            if not para_text:
                continue

            if _is_reference_header(para_text):
                in_refs = True

            is_ref = in_refs or _is_reference_line(para_text)
            is_susp = (not is_ref) and _para_is_suspicious(para_text)

            if not is_susp:
                continue

            # نطبّق التظليل على كل run موجود للحفاظ على تنسيق كل جزء كما هو
            non_empty_run_found = False
            for run in para.runs:
                if (run.text or "").strip():
                    _set_run_docx_shading(run, fill="9FE2FF")
                    non_empty_run_found = True

            # إذا كانت الفقرة بلا runs واضحة، ننشئ run أخيراً بدون المساس بالمحتوى
            if not non_empty_run_found and para_text:
                run = para.add_run("")
                _set_run_docx_shading(run, fill="9FE2FF")

            highlighted += 1
    except Exception:
        return b""

    out = io.BytesIO()
    try:
        doc.save(out)
        return out.getvalue()
    except Exception:
        return b""



_DOCX_CONVERSION_DIAGNOSTIC = {
    "ok": False,
    "engine": "",
    "message": "لم تبدأ محاولة التحويل بعد.",
    "details": "",
}


def _set_docx_conversion_diagnostic(ok: bool, engine: str, message: str, details: str = "") -> None:
    """يحفظ آخر حالة تحويل Word حتى تعرض الواجهة سبب النجاح أو الفشل الحقيقي."""
    global _DOCX_CONVERSION_DIAGNOSTIC
    _DOCX_CONVERSION_DIAGNOSTIC = {
        "ok": bool(ok),
        "engine": str(engine or ""),
        "message": str(message or ""),
        "details": str(details or "")[:5000],
    }


def get_last_docx_conversion_diagnostic() -> dict:
    """يعيد نسخة آمنة من آخر تشخيص لتحويل Word إلى PDF."""
    return dict(_DOCX_CONVERSION_DIAGNOSTIC)


def convert_docx_to_pdf_bytes(docx_bytes: bytes) -> bytes:
    """
    يحوّل DOCX إلى PDF مع الحفاظ على تخطيط المستند قدر الإمكان.

    ترتيب المحركات:
    1) Microsoft Word عبر docx2pdf على Windows/macOS.
    2) Microsoft Word COM على Windows.
    3) LibreOffice Writer على Linux وStreamlit Community Cloud.

    ملاحظة نشر مهمة:
    - requirements.txt يثبت مكتبات Python فقط.
    - على Streamlit Community Cloud يجب تثبيت LibreOffice كاعتماد نظام
      من خلال packages.txt في جذر المستودع.
    """
    import os
    import platform
    import shutil
    import socket
    import subprocess
    import tempfile
    from pathlib import Path

    _set_docx_conversion_diagnostic(False, "", "بدأت محاولة تحويل Word إلى PDF.")

    if not docx_bytes or len(docx_bytes) < 100:
        _set_docx_conversion_diagnostic(
            False,
            "input",
            "ملف Word فارغ أو غير صالح.",
        )
        return b""

    def _read_valid_pdf(pdf_path: str) -> bytes:
        try:
            if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 100:
                with open(pdf_path, "rb") as f:
                    data = f.read()
                if data.startswith(b"%PDF"):
                    return data
        except Exception:
            pass
        return b""

    with tempfile.TemporaryDirectory(prefix="ai_detector_docx_") as tmpdir:
        docx_path = os.path.join(tmpdir, "input.docx")
        expected_pdf_path = os.path.join(tmpdir, "input.pdf")
        with open(docx_path, "wb") as f:
            f.write(docx_bytes)

        system_name = platform.system()
        errors = []

        # المسار الأدق على الأجهزة التي تحتوي Microsoft Word.
        if system_name in {"Windows", "Darwin"}:
            try:
                from docx2pdf import convert as docx2pdf_convert

                docx2pdf_convert(docx_path, expected_pdf_path)
                data = _read_valid_pdf(expected_pdf_path)
                if data:
                    _set_docx_conversion_diagnostic(
                        True,
                        "Microsoft Word / docx2pdf",
                        "تم تصدير Word إلى PDF بواسطة Microsoft Word.",
                    )
                    return data
                errors.append("docx2pdf انتهى دون إنشاء PDF صالح.")
            except Exception as exc:
                errors.append(f"docx2pdf: {type(exc).__name__}: {exc}")

        # Word COM على Windows.
        if os.name == "nt":
            word_app = None
            word_doc = None
            pythoncom_initialized = False
            try:
                import pythoncom
                import win32com.client

                pythoncom.CoInitialize()
                pythoncom_initialized = True
                word_app = win32com.client.DispatchEx("Word.Application")
                word_app.Visible = False
                word_app.DisplayAlerts = 0
                word_doc = word_app.Documents.Open(
                    os.path.abspath(docx_path),
                    ConfirmConversions=False,
                    ReadOnly=True,
                    AddToRecentFiles=False,
                )
                word_doc.ExportAsFixedFormat(
                    OutputFileName=os.path.abspath(expected_pdf_path),
                    ExportFormat=17,
                    OpenAfterExport=False,
                    OptimizeFor=0,
                    Range=0,
                    Item=0,
                    IncludeDocProps=True,
                    KeepIRM=True,
                    CreateBookmarks=1,
                    DocStructureTags=True,
                    BitmapMissingFonts=True,
                    UseISO19005_1=False,
                )
                data = _read_valid_pdf(expected_pdf_path)
                if data:
                    _set_docx_conversion_diagnostic(
                        True,
                        "Microsoft Word COM",
                        "تم تصدير Word إلى PDF بواسطة Microsoft Word.",
                    )
                    return data
                errors.append("Word COM انتهى دون إنشاء PDF صالح.")
            except Exception as exc:
                errors.append(f"Word COM: {type(exc).__name__}: {exc}")
            finally:
                try:
                    if word_doc is not None:
                        word_doc.Close(False)
                except Exception:
                    pass
                try:
                    if word_app is not None:
                        word_app.Quit()
                except Exception:
                    pass
                if pythoncom_initialized:
                    try:
                        pythoncom.CoUninitialize()
                    except Exception:
                        pass

        # LibreOffice: المحرك المطلوب على Streamlit Community Cloud/Linux.
        env = os.environ.copy()
        env["TMPDIR"] = tmpdir
        env["HOME"] = tmpdir
        env["XDG_RUNTIME_DIR"] = tmpdir
        env["SAL_USE_VCLPLUGIN"] = "svp"
        env.setdefault("LANG", "C.UTF-8")
        env.setdefault("LC_ALL", "C.UTF-8")

        # حل احتياطي لبيئات Linux المقيدة التي تمنع AF_UNIX.
        af_unix = getattr(socket, "AF_UNIX", None)
        if af_unix is not None and os.name != "nt":
            try:
                sock = socket.socket(af_unix, socket.SOCK_STREAM)
                sock.close()
            except OSError:
                shim_path = "/tmp/lo_socket_shim.so"
                if os.path.exists(shim_path):
                    env["LD_PRELOAD"] = shim_path

        candidates = [shutil.which("soffice"), shutil.which("libreoffice")]
        if os.name == "nt":
            candidates.extend([
                r"C:\Program Files\LibreOffice\program\soffice.exe",
                r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
            ])
        elif system_name == "Darwin":
            candidates.append("/Applications/LibreOffice.app/Contents/MacOS/soffice")
        else:
            candidates.extend([
                "/usr/bin/soffice",
                "/usr/bin/libreoffice",
                "/usr/local/bin/soffice",
                "/usr/local/bin/libreoffice",
            ])

        soffice_bin = next((c for c in candidates if c and os.path.exists(c)), None)
        if not soffice_bin:
            details = "\n".join(errors)
            _set_docx_conversion_diagnostic(
                False,
                "LibreOffice",
                "LibreOffice غير مثبت في بيئة الاستضافة. أضف ملف packages.txt إلى جذر مستودع GitHub ثم أعد تشغيل التطبيق.",
                details,
            )
            return b""

        # تأكد أن الملف التنفيذي يعمل، وهذا يعطي رسالة أوضح من فشل صامت.
        try:
            version_proc = subprocess.run(
                [soffice_bin, "--version"],
                env=env,
                capture_output=True,
                timeout=30,
                text=True,
            )
            version_text = (version_proc.stdout or version_proc.stderr or "").strip()
            if version_proc.returncode != 0:
                errors.append(
                    f"LibreOffice --version returncode={version_proc.returncode}: {version_text}"
                )
        except Exception as exc:
            version_text = ""
            errors.append(f"LibreOffice version check: {type(exc).__name__}: {exc}")

        profile_dir = Path(tmpdir, "lo_profile")
        profile_dir.mkdir(parents=True, exist_ok=True)
        cmd = [
            soffice_bin,
            f"-env:UserInstallation={profile_dir.as_uri()}",
            "--headless",
            "--invisible",
            "--nologo",
            "--nodefault",
            "--nolockcheck",
            "--norestore",
            "--nofirststartwizard",
            "--convert-to", "pdf:writer_pdf_Export",
            "--outdir", tmpdir,
            docx_path,
        ]

        try:
            proc = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                timeout=240,
                text=True,
            )
        except subprocess.TimeoutExpired as exc:
            _set_docx_conversion_diagnostic(
                False,
                "LibreOffice",
                "انتهت مهلة تحويل Word إلى PDF داخل بيئة الاستضافة.",
                f"timeout={exc.timeout}; errors={' | '.join(errors)}",
            )
            return b""
        except Exception as exc:
            _set_docx_conversion_diagnostic(
                False,
                "LibreOffice",
                "تعذر تشغيل LibreOffice داخل بيئة الاستضافة.",
                f"{type(exc).__name__}: {exc}\n" + "\n".join(errors),
            )
            return b""

        # LibreOffice قد يعيد تسمية الملف؛ لذلك نبحث عن أي PDF ناتج.
        pdf_candidates = [Path(expected_pdf_path)] + sorted(Path(tmpdir).glob("*.pdf"))
        for candidate in pdf_candidates:
            data = _read_valid_pdf(str(candidate))
            if data:
                details = "\n".join(
                    part for part in [
                        version_text,
                        (proc.stdout or "").strip(),
                        (proc.stderr or "").strip(),
                    ] if part
                )
                _set_docx_conversion_diagnostic(
                    True,
                    "LibreOffice Writer",
                    "تم تصدير Word إلى PDF بواسطة LibreOffice Writer.",
                    details,
                )
                return data

        details = "\n".join(
            part for part in [
                f"returncode={proc.returncode}",
                (proc.stdout or "").strip(),
                (proc.stderr or "").strip(),
                "\n".join(errors),
            ] if part
        )
        _set_docx_conversion_diagnostic(
            False,
            "LibreOffice",
            "عمل LibreOffice لكنه لم يُنشئ ملف PDF صالحًا.",
            details,
        )
        return b""


def _build_logo_data_uri() -> str:
    svg = """<svg xmlns='http://www.w3.org/2000/svg' width='220' height='220' viewBox='0 0 220 220'>
      <defs>
        <linearGradient id='lg1' x1='0%' y1='0%' x2='100%' y2='100%'>
          <stop offset='0%' stop-color='#08150f'/>
          <stop offset='100%' stop-color='#0d3324'/>
        </linearGradient>
        <linearGradient id='lg2' x1='0%' y1='0%' x2='100%' y2='100%'>
          <stop offset='0%' stop-color='#22e5a8'/>
          <stop offset='50%' stop-color='#ffb703'/>
          <stop offset='100%' stop-color='#ff6b4a'/>
        </linearGradient>
        <linearGradient id='lg3' x1='0%' y1='0%' x2='100%' y2='100%'>
          <stop offset='0%' stop-color='#22e5a8' stop-opacity='0.3'/>
          <stop offset='100%' stop-color='#ffb703' stop-opacity='0.1'/>
        </linearGradient>
        <filter id='glow'>
          <feGaussianBlur stdDeviation='3' result='coloredBlur'/>
          <feMerge><feMergeNode in='coloredBlur'/><feMergeNode in='SourceGraphic'/></feMerge>
        </filter>
      </defs>
      <!-- خلفية -->
      <rect x='0' y='0' width='220' height='220' rx='44' fill='url(#lg1)'/>
      <!-- حلقات توهج خلفية -->
      <circle cx='110' cy='110' r='90' fill='none' stroke='url(#lg2)' stroke-width='0.5' opacity='0.2'/>
      <circle cx='110' cy='110' r='72' fill='none' stroke='url(#lg2)' stroke-width='0.5' opacity='0.3'/>
      <!-- شبكة نقاط خفية -->
      <g opacity='0.12' fill='#22e5a8'>
        <circle cx='40' cy='40' r='1.5'/><circle cx='70' cy='40' r='1.5'/><circle cx='100' cy='40' r='1.5'/>
        <circle cx='130' cy='40' r='1.5'/><circle cx='160' cy='40' r='1.5'/><circle cx='180' cy='40' r='1.5'/>
        <circle cx='40' cy='70' r='1.5'/><circle cx='180' cy='70' r='1.5'/>
        <circle cx='40' cy='180' r='1.5'/><circle cx='70' cy='180' r='1.5'/><circle cx='130' cy='180' r='1.5'/>
        <circle cx='160' cy='180' r='1.5'/><circle cx='180' cy='180' r='1.5'/>
      </g>
      <!-- دائرة رئيسية متوهجة -->
      <circle cx='110' cy='105' r='52' fill='url(#lg3)' filter='url(#glow)'/>
      <circle cx='110' cy='105' r='44' fill='none' stroke='url(#lg2)' stroke-width='2.5' opacity='0.9'/>
      <!-- خطوط بصمة إصبع -->
      <g fill='none' stroke='url(#lg2)' stroke-linecap='round' opacity='0.7'>
        <path d='M90 105 Q110 88 130 105 Q110 122 90 105' stroke-width='2'/>
        <path d='M83 105 Q110 80 137 105 Q110 130 83 105' stroke-width='1.5'/>
        <path d='M76 105 Q110 72 144 105 Q110 138 76 105' stroke-width='1.2'/>
        <path d='M70 105 Q110 65 150 105 Q110 145 70 105' stroke-width='1'/>
      </g>
      <!-- نقطة مركزية -->
      <circle cx='110' cy='105' r='6' fill='#22e5a8' filter='url(#glow)'/>
      <circle cx='110' cy='105' r='3' fill='#ffffff'/>
      <!-- خطوط ماسحة رادار -->
      <line x1='110' y1='105' x2='110' y2='65' stroke='#22e5a8' stroke-width='1.5' opacity='0.6'/>
      <line x1='110' y1='105' x2='140' y2='80' stroke='#ffb703' stroke-width='1' opacity='0.5'/>
      <!-- نص AI -->
      <text x='110' y='168' text-anchor='middle' font-size='13' font-family='Arial Black,Arial' font-weight='900'
            letter-spacing='4' fill='url(#lg2)' opacity='0.9'>AI·FP</text>
      <!-- إطار خارجي فاخر -->
      <rect x='3' y='3' width='214' height='214' rx='42' fill='none' stroke='url(#lg2)' stroke-width='1.5' opacity='0.4'/>
    </svg>"""
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")


logo_data_uri = _build_logo_data_uri()

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Space+Grotesk:wght@400;600;700&display=swap');

* {{ box-sizing: border-box; }}

body,
[data-testid="stAppViewContainer"],
[data-testid="stVerticalBlock"],
.main {{
    direction: rtl;
    font-family: 'Cairo', 'Segoe UI', Tahoma, sans-serif;
}}

pre, code, .stat-num, .layer-val, .ltr {{
    direction: ltr !important;
    text-align: left !important;
    font-family: 'Space Grotesk', 'Courier New', monospace;
}}

[data-testid="stAppViewContainer"] {{
    background:
        radial-gradient(ellipse 80% 60% at 10% 0%, rgba(34,229,168,0.07) 0%, transparent 60%),
        radial-gradient(ellipse 60% 70% at 90% 100%, rgba(255,183,3,0.09) 0%, transparent 60%),
        radial-gradient(ellipse 50% 50% at 50% 50%, rgba(255,107,74,0.04) 0%, transparent 70%),
        linear-gradient(160deg, #071410 0%, #0a1f18 40%, #10190f 100%);
    min-height: 100vh;
}}

[data-testid="stHeader"] {{
    background: rgba(7,9,26,0.85) !important;
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(34,229,168,0.12);
}}

.main .block-container {{
    max-width: 980px;
    padding-top: 2rem;
    padding-bottom: 4rem;
    padding-right: 1.4rem;
    padding-left: 1.4rem;
}}

.hero-card {{
    background: linear-gradient(145deg, rgba(13,16,42,0.95), rgba(10,14,35,0.98));
    border: 1px solid rgba(34,229,168,0.18);
    border-radius: 28px;
    padding: 1.8rem 2rem 1.5rem;
    box-shadow: 0 0 0 1px rgba(255,183,3,0.08) inset, 0 30px 80px rgba(0,0,0,0.5);
    margin-bottom: 1.4rem;
    position: relative;
    overflow: hidden;
}}

.hero-card::before {{
    content: '';
    position: absolute;
    top: -80px; right: -80px;
    width: 260px; height: 260px;
    background: radial-gradient(circle, rgba(34,229,168,0.07), transparent 70%);
    pointer-events: none;
}}

.hero-card::after {{
    content: '';
    position: absolute;
    bottom: -60px; left: -60px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(255,183,3,0.06), transparent 70%);
    pointer-events: none;
}}

.hero-card-topbar {{
    position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #22e5a8, #ffb703, #ff6b4a, #22e5a8);
    background-size: 200% 100%;
    animation: shimmer 4s linear infinite;
    border-radius: 28px 28px 0 0;
}}

@keyframes shimmer {{
    0%   {{ background-position: 0% 0%; }}
    100% {{ background-position: 200% 0%; }}
}}

.hero-grid {{
    display: grid;
    grid-template-columns: 110px 1fr;
    gap: 1.4rem;
    align-items: center;
    direction: rtl;
}}

.hero-logo {{
    width: 100px; height: 100px;
    border-radius: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(145deg, #0b1f16, #08150f);
    border: 1px solid rgba(34,229,168,0.25);
    box-shadow: 0 0 30px rgba(34,229,168,0.15), 0 10px 30px rgba(0,0,0,0.4);
    overflow: hidden;
    flex-shrink: 0;
}}

.hero-logo img {{
    width: 92px; height: 92px;
    object-fit: contain;
}}

.hero-text {{ text-align: right; }}

.hero-title {{
    font-size: 2.1rem;
    font-weight: 900;
    background: linear-gradient(135deg, #22e5a8 0%, #ffb703 50%, #ff6b4a 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 0.45rem;
    letter-spacing: -0.5px;
    direction: ltr;
    text-align: left;
}}

.hero-subtitle {{
    color: rgba(180,200,240,0.75);
    font-size: 0.93rem;
    line-height: 1.9;
    direction: rtl;
    text-align: right;
}}

.hero-badges {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 1rem;
    justify-content: flex-end;
    direction: rtl;
}}

.hero-badge {{
    background: rgba(34,229,168,0.07);
    border: 1px solid rgba(34,229,168,0.18);
    color: #7be8c4;
    border-radius: 999px;
    padding: 0.3rem 0.85rem;
    font-size: 0.78rem;
    font-weight: 700;
    white-space: nowrap;
    transition: all 0.2s;
}}

.features-wrap {{
    background: rgba(10,14,35,0.85);
    border: 1px solid rgba(255,183,3,0.15);
    border-radius: 24px;
    padding: 1.4rem;
    box-shadow: 0 20px 50px rgba(0,0,0,0.3);
    margin-bottom: 0.6rem;
    position: relative;
    overflow: hidden;
}}

.features-wrap::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, rgba(255,183,3,0.6), transparent);
}}

.features-title {{
    font-weight: 900;
    color: #cdf0e0;
    margin-bottom: 1rem;
    font-size: 1rem;
    text-align: right;
}}

.features-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.85rem;
}}

.feature-card {{
    background: rgba(15,20,50,0.7);
    border: 1px solid rgba(34,229,168,0.10);
    border-radius: 18px;
    padding: 1.1rem;
    transition: transform 0.25s, box-shadow 0.25s, border-color 0.25s;
    text-align: right;
    position: relative;
    overflow: hidden;
}}

.feature-card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 16px 40px rgba(0,0,0,0.4), 0 0 20px rgba(34,229,168,0.07);
    border-color: rgba(34,229,168,0.22);
}}

.feature-icon {{
    width: 40px; height: 40px;
    border-radius: 12px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, rgba(34,229,168,0.15), rgba(255,183,3,0.15));
    border: 1px solid rgba(34,229,168,0.15);
    font-size: 1.15rem;
    margin-bottom: 0.55rem;
}}

.feature-card strong {{
    display: block;
    color: #d9f5e6;
    margin-bottom: 0.3rem;
    font-size: 0.92rem;
    font-weight: 800;
}}

.feature-card span {{
    color: rgba(140,165,210,0.7);
    font-size: 0.82rem;
    line-height: 1.75;
}}

.section-card {{
    background: rgba(10,14,35,0.88);
    border: 1px solid rgba(34,229,168,0.14);
    border-radius: 24px;
    padding: 1.4rem;
    box-shadow: 0 20px 50px rgba(0,0,0,0.3);
    position: relative;
}}

.section-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, rgba(34,229,168,0.5), transparent);
    border-radius: 24px 24px 0 0;
}}

.meter-wrap {{
    background: rgba(10,14,35,0.9);
    border: 1px solid rgba(34,229,168,0.15);
    border-radius: 24px;
    padding: 2.4rem 2rem 2rem;
    margin: 1.5rem 0;
    text-align: center;
    box-shadow: 0 30px 70px rgba(0,0,0,0.4);
    position: relative;
    overflow: hidden;
}}

.meter-wrap::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, rgba(34,229,168,0.6), rgba(255,183,3,0.6), transparent);
}}

.meter-pct {{
    font-size: 5.5rem;
    font-weight: 900;
    line-height: 1;
    letter-spacing: -4px;
    font-family: 'Space Grotesk', sans-serif;
    direction: ltr;
    display: block;
}}

.meter-label {{
    font-size: 1.2rem;
    margin-top: 0.6rem;
    font-weight: 800;
    direction: rtl;
}}

.meter-human {{
    font-size: 0.9rem;
    color: rgba(140,165,210,0.65);
    margin-top: 0.5rem;
    direction: rtl;
    font-family: 'Space Grotesk', sans-serif;
}}

.bar-track {{
    background: rgba(255,255,255,0.06);
    border-radius: 999px;
    height: 14px;
    margin: 1.5rem 0;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.04);
}}

.bar-fill {{
    height: 100%;
    border-radius: 999px;
    transition: width 0.8s cubic-bezier(.4, 0, .2, 1);
}}

.layer-card {{
    background: rgba(12,17,45,0.85);
    border: 1px solid rgba(34,229,168,0.10);
    border-radius: 16px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.75rem;
    direction: rtl;
    text-align: right;
    transition: border-color 0.2s;
    overflow: hidden;
}}

.layer-card:hover {{
    border-color: rgba(34,229,168,0.22);
}}

.layer-title {{
    font-weight: 800;
    font-size: 0.9rem;
    color: #bfe8d4;
    direction: rtl;
    display: inline-block;
}}

.layer-val {{
    float: left;
    font-weight: 900;
    font-size: 0.92rem;
    direction: ltr !important;
    text-align: left !important;
    font-family: 'Space Grotesk', monospace;
}}

.layer-bar {{
    clear: both;
    height: 8px;
    background: rgba(255,255,255,0.06);
    border-radius: 999px;
    margin-top: 0.75rem;
    overflow: hidden;
}}

.layer-bar-fill {{
    height: 100%;
    border-radius: 999px;
}}

.hit-tag {{
    display: inline-block;
    background: rgba(255,107,107,0.08);
    border: 1px solid rgba(255,107,107,0.22);
    border-radius: 8px;
    padding: 4px 12px;
    margin: 3px;
    font-size: 0.77rem;
    font-family: 'Space Grotesk', 'Courier New', monospace;
    color: #ff9999;
    direction: ltr !important;
    text-align: left !important;
    transition: background 0.2s;
}}

.stat-row {{
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin: 1rem 0;
    direction: rtl;
}}

.stat-box {{
    flex: 1;
    min-width: 95px;
    background: rgba(12,17,45,0.85);
    border: 1px solid rgba(34,229,168,0.12);
    border-radius: 16px;
    padding: 0.9rem 0.8rem;
    text-align: center;
    transition: transform 0.2s, border-color 0.2s;
}}

.stat-box:hover {{
    transform: translateY(-2px);
    border-color: rgba(34,229,168,0.28);
}}

.stat-num {{
    font-size: 1.5rem;
    font-weight: 900;
    color: #22e5a8;
    direction: ltr !important;
    text-align: center !important;
    font-family: 'Space Grotesk', sans-serif;
    display: block;
}}

.stat-lbl {{
    font-size: 0.7rem;
    color: rgba(140,165,210,0.6);
    margin-top: 0.25rem;
    direction: rtl;
}}

div[data-testid="stTabs"] {{
    direction: rtl;
}}

div[data-testid="stTabs"] button[role="tab"] {{
    border-radius: 12px !important;
    background: rgba(12,17,45,0.8) !important;
    border: 1px solid rgba(34,229,168,0.12) !important;
    color: rgba(140,180,220,0.8) !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    font-family: 'Cairo', sans-serif !important;
}}

div[data-testid="stTabs"] button[aria-selected="true"] {{
    background: linear-gradient(135deg, rgba(34,229,168,0.15), rgba(255,183,3,0.15)) !important;
    color: #22e5a8 !important;
    border-color: rgba(34,229,168,0.3) !important;
}}

div[data-testid="stTextArea"] textarea {{
    background: rgba(7,9,26,0.8) !important;
    border-radius: 16px !important;
    border: 1.5px solid rgba(34,229,168,0.15) !important;
    color: #d9f5e6 !important;
    direction: rtl;
    text-align: right;
    font-size: 0.95rem !important;
    font-family: 'Cairo', sans-serif !important;
}}

div[data-testid="stTextArea"] textarea::placeholder {{
    text-align: right;
    color: rgba(100,130,180,0.45) !important;
}}

div[data-testid="stFileUploader"] section {{
    background: rgba(7,9,26,0.6) !important;
    border-radius: 16px !important;
    border: 1.5px dashed rgba(34,229,168,0.2) !important;
    color: rgba(140,180,220,0.7) !important;
}}

.stButton > button,
.stDownloadButton > button {{
    border: none !important;
    border-radius: 14px !important;
    font-size: 0.97rem !important;
    font-weight: 800 !important;
    padding: 0.78rem 1.5rem !important;
    width: 100% !important;
    transition: all 0.25s cubic-bezier(.4, 0, .2, 1);
    font-family: 'Cairo', sans-serif !important;
}}

.stButton > button[kind="primary"],
.stDownloadButton > button {{
    background: linear-gradient(135deg, #22e5a8, #ffb703) !important;
    color: white !important;
    box-shadow: 0 8px 25px rgba(34,229,168,0.25), 0 4px 10px rgba(0,0,0,0.3) !important;
}}

.stButton > button[kind="primary"]:hover,
.stDownloadButton > button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 14px 35px rgba(34,229,168,0.35), 0 6px 15px rgba(0,0,0,0.3) !important;
}}

.stButton > button:not([kind="primary"]) {{
    background: rgba(12,17,45,0.85) !important;
    color: rgba(140,180,220,0.85) !important;
    border: 1.5px solid rgba(34,229,168,0.18) !important;
}}

.stButton > button:not([kind="primary"]):hover {{
    background: rgba(34,229,168,0.08) !important;
    border-color: rgba(34,229,168,0.35) !important;
    color: #22e5a8 !important;
    transform: translateY(-1px);
}}

.stAlert,
div[data-testid="stAlert"] {{
    border-radius: 14px !important;
    direction: rtl !important;
    text-align: right !important;
}}

div[data-testid="stAlert"] {{
    background: rgba(34,229,168,0.06) !important;
    border: 1px solid rgba(34,229,168,0.18) !important;
}}

div[data-testid="stAlert"] p {{
    direction: rtl !important;
    text-align: right !important;
    color: rgba(140,200,240,0.85) !important;
}}

h3 {{
    text-align: right !important;
    direction: rtl !important;
    color: #7fd9ae !important;
    font-weight: 800 !important;
    margin: 1.2rem 0 0.6rem !important;
    font-family: 'Cairo', sans-serif !important;
}}

hr {{
    border: none !important;
    border-top: 1px solid rgba(34,229,168,0.12) !important;
    margin: 1.5rem 0 !important;
}}

.info-note {{
    text-align: center;
    font-size: 0.8rem;
    color: rgba(140,165,210,0.5);
    margin-top: 0.5rem;
    direction: rtl;
}}

code {{
    background: rgba(34,229,168,0.08) !important;
    border: 1px solid rgba(34,229,168,0.15) !important;
    color: #22e5a8 !important;
    border-radius: 6px !important;
    padding: 2px 6px !important;
    direction: ltr !important;
    text-align: left !important;
    font-family: 'Space Grotesk', 'Courier New', monospace !important;
}}

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {{
    color: rgba(160,185,225,0.85);
    direction: rtl;
    text-align: right;
    line-height: 1.85;
}}

[data-testid="stMarkdownContainer"] strong {{
    color: #d9f5e6;
    font-weight: 800;
}}

[data-testid="stSuccess"] {{
    background: rgba(0,200,100,0.08) !important;
    border-color: rgba(0,200,100,0.2) !important;
    border-radius: 14px !important;
    direction: rtl !important;
    text-align: right !important;
}}

[data-testid="stError"] {{
    background: rgba(255,80,80,0.08) !important;
    border-color: rgba(255,80,80,0.2) !important;
    border-radius: 14px !important;
    direction: rtl !important;
    text-align: right !important;
}}

[data-testid="stWarning"] {{
    background: rgba(255,170,0,0.08) !important;
    border-color: rgba(255,170,0,0.2) !important;
    border-radius: 14px !important;
    direction: rtl !important;
    text-align: right !important;
}}

/* ── لافتة التحديثات المتحركة ─────────────────────────────────────────── */
.update-banner {{
    position: relative;
    overflow: hidden;
    border-radius: 16px;
    background: linear-gradient(90deg, rgba(34,229,168,0.16), rgba(255,183,3,0.16), rgba(255,107,74,0.16));
    border: 1px solid rgba(34,229,168,0.3);
    box-shadow: 0 10px 30px rgba(0,0,0,0.35);
    padding: 0.65rem 0;
    margin-bottom: 1.4rem;
}}

.update-banner-track {{
    display: flex;
    width: max-content;
    white-space: nowrap;
    animation: marquee-scroll 22s linear infinite;
}}

.update-banner:hover .update-banner-track {{
    animation-play-state: paused;
}}

.update-banner-track span {{
    display: inline-block;
    padding: 0 2.2rem;
    font-weight: 800;
    font-size: 0.95rem;
    font-family: 'Cairo', sans-serif;
    color: #eafff4;
    direction: rtl;
}}

.update-banner-track span b {{
    background: linear-gradient(135deg, #22e5a8, #ffb703);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

@keyframes marquee-scroll {{
    0%   {{ transform: translateX(0%); }}
    100% {{ transform: translateX(-50%); }}
}}

/* ── تقييمات العملاء ───────────────────────────────────────────────────── */
.ratings-summary {{
    text-align: center;
    padding: 0.4rem 0 1rem;
}}

.ratings-avg {{
    font-size: 3rem;
    font-weight: 900;
    line-height: 1;
    font-family: 'Space Grotesk', sans-serif;
    background: linear-gradient(135deg, #22e5a8, #ffb703);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    direction: ltr;
}}

.ratings-stars-big {{
    font-size: 1.6rem;
    letter-spacing: 4px;
    color: #ffb703;
    margin-top: 0.3rem;
    direction: ltr;
}}

.ratings-count {{
    font-size: 0.82rem;
    color: rgba(160,220,195,0.65);
    margin-top: 0.3rem;
    direction: rtl;
}}

.review-item {{
    background: rgba(12,45,32,0.55);
    border: 1px solid rgba(34,229,168,0.14);
    border-radius: 14px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.6rem;
    direction: rtl;
    text-align: right;
}}

.review-head {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.25rem;
}}

.review-name {{
    font-weight: 800;
    color: #d9f5e6;
    font-size: 0.88rem;
}}

.review-stars {{
    color: #ffb703;
    font-size: 0.95rem;
    letter-spacing: 2px;
    direction: ltr;
}}

.review-comment {{
    color: rgba(190,225,210,0.8);
    font-size: 0.85rem;
    line-height: 1.7;
}}

.review-date {{
    color: rgba(150,190,175,0.45);
    font-size: 0.72rem;
    margin-top: 0.3rem;
    direction: ltr;
    text-align: left;
}}

.rate-prompt {{
    font-weight: 800;
    color: #cdf0e0;
    margin: 0.6rem 0 0.4rem;
    text-align: right;
    direction: rtl;
}}

@media (max-width: 720px) {{
    .hero-grid, .features-grid {{
        grid-template-columns: 1fr;
    }}
    .hero-logo {{
        margin: 0 auto;
    }}
    .hero-title {{
        font-size: 1.6rem;
        text-align: right;
    }}
}}
</style>
""", unsafe_allow_html=True)


# ── Hero Section ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-card">
    <div class="hero-card-topbar"></div>
    <div class="hero-grid">
        <div class="hero-logo">
            <img src="{logo_data_uri}" alt="AI Fingerprint Detector">
        </div>
        <div class="hero-text">
            <div class="hero-title">AI Fingerprint Detector</div>
            <div class="hero-subtitle">
                أداة متقدمة لكشف بصمات الذكاء الاصطناعي في النصوص الأكاديمية،
                مع تقرير مُظلَّل يعمل على ملفات PDF و Word مع الحفاظ التام على التنسيق والجداول والأشكال.
            </div>
            <div class="hero-badges">
                <span class="hero-badge">🎯 تظليل دقيق على الملف الأصلي</span>
                <span class="hero-badge">📄 PDF و Word (تنسيق كامل)</span>
                <span class="hero-badge">🚫 المراجع خارج التظليل</span>
                <span class="hero-badge">⚖️ مراجعة محافظة تقلل الإيجابيات الكاذبة</span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── لافتة تحديثات متحركة ─────────────────────────────────────────────────────
_banner_msg = (
    "🎉 <b>تحديث جديد!</b> تم رفع مستوى الخدمة وتحسين دقة الفحص وسرعة توليد التقارير "
    "&nbsp;•&nbsp; ⚡ أداء أسرع في تحليل الملفات الكبيرة "
    "&nbsp;•&nbsp; 🛡️ حماية أدق للمراجع من التظليل "
    "&nbsp;•&nbsp; ⭐ يسعدنا معرفة رأيك في التحديث الجديد"
)
st.markdown(f"""
<div class="update-banner">
    <div class="update-banner-track">
        <span>{_banner_msg}</span>
        <span>{_banner_msg}</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ── تقييمات العملاء ───────────────────────────────────────────────────────────
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown("### ⭐ تقييمات العملاء")

_ratings_data = _load_ratings()
_avg_rating   = sum(r["stars"] for r in _ratings_data) / len(_ratings_data) if _ratings_data else 0.0
_full_stars   = int(round(_avg_rating))
_stars_disp   = "★" * _full_stars + "☆" * (5 - _full_stars)

st.markdown(f"""
<div class="ratings-summary">
    <span class="ratings-avg">{_avg_rating:.1f}</span>
    <div class="ratings-stars-big">{_stars_disp}</div>
    <div class="ratings-count">بناءً على {len(_ratings_data)} تقييم من عملائنا</div>
</div>
""", unsafe_allow_html=True)

with st.expander("💬 اطّلع على آراء العملاء"):
    for _r in reversed(_ratings_data[-10:]):
        _stxt = "★" * _r["stars"] + "☆" * (5 - _r["stars"])
        _comment = _r.get("comment") or ""
        st.markdown(f"""
        <div class="review-item">
            <div class="review-head">
                <span class="review-name">{_r.get('name', 'عميل')}</span>
                <span class="review-stars">{_stxt}</span>
            </div>
            {f'<div class="review-comment">{_comment}</div>' if _comment else ''}
            <div class="review-date">{_r.get('date', '')}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="rate-prompt">قيّم تجربتك معنا:</div>', unsafe_allow_html=True)
_new_stars = st.feedback("stars", key="rating_feedback")

_rc1, _rc2 = st.columns([2, 2])
with _rc1:
    _reviewer_name = st.text_input(
        "اسمك (اختياري)", key="reviewer_name",
        label_visibility="collapsed", placeholder="اسمك (اختياري)",
    )
with _rc2:
    _reviewer_comment = st.text_input(
        "تعليقك (اختياري)", key="reviewer_comment",
        label_visibility="collapsed", placeholder="تعليقك (اختياري)",
    )

if st.button("إرسال التقييم", use_container_width=True):
    if _new_stars is None:
        st.warning("الرجاء اختيار عدد النجوم أولاً.")
    else:
        _save_rating({
            "name": (_reviewer_name or "").strip() or "عميل",
            "stars": int(_new_stars) + 1,
            "comment": (_reviewer_comment or "").strip(),
            "date": datetime.now().strftime("%Y-%m-%d"),
        })
        st.success("✅ شكراً على تقييمك! تم إضافته إلى آراء العملاء.")
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)


# ── Features ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="features-wrap">
    <div class="features-title">ماذا يُقدّم البرنامج؟</div>
    <div class="features-grid">
        <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <strong>فحص دقيق بطبقتين</strong>
            <span>تحليل إشارات T1 وأنماط T2 مع منع احتساب الإشارة نفسها مرتين وتقييم الأسلوب والبنية.</span>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📑</div>
            <strong>التقرير المظلل: PDF و Word (تنسيق كامل)</strong>
            <span>عند رفع PDF يتم التظليل فوق الصفحات الأصلية مباشرة. وعند رفع DOCX يتم تصدير الملف الأصلي أولاً إلى PDF بواسطة Microsoft Word عند توفره، ثم يُنشأ عليه التقرير نفسه تماماً مع الحفاظ على الجداول والصور والأشكال والتنسيق.</span>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🚫</div>
            <strong>المراجع محمية من التظليل</strong>
            <span>يستبعد قسم المراجع والاستشهادات الرقمية والمؤلف–السنة من الحساب، ولا يطبّق على قسم المراجع أي تظليل.</span>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <strong>إحصاءات تفصيلية وغلاف احترافي</strong>
            <span>صفحة غلاف فنية + إحصاءات + صفحة ملخص الإشارات المكتشفة في نهاية التقرير.</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Input Section ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-card">', unsafe_allow_html=True)

st.markdown("### رفع الملف للفحص")
st.info("📌 ارفع ملف PDF أو Word (DOCX). ملف Word يُصدَّر أولاً إلى PDF من الأصل دون تعديل، ثم يُطبَّق عليه تقرير PDF نفسه. عند ظهور *% لا يتم تظليل أي نص نهائياً.")

input_text         = ""
uploaded_name      = "Document"
original_pdf_bytes = None
original_docx_bytes = None

uploaded = st.file_uploader(
    "ارفع ملف PDF أو Word:",
    type=["pdf", "docx"],
    key="file_upload",
)

if uploaded:
    uploaded_name = uploaded.name
    raw = uploaded.read()
    ext = uploaded.name.lower().rsplit(".", 1)[-1]

    if ext == "pdf":
        original_pdf_bytes = raw
        input_text = extract_text_from_pdf(raw)
        if input_text:
            st.success(f"✅ تم استخراج النص من ملف PDF ({len(input_text.split()):,} كلمة)")
        else:
            st.error("تعذّر استخراج النص من ملف PDF. تأكد من أن الملف قابل للقراءة وأن PyMuPDF مثبتة.")
    elif ext == "docx":
        original_docx_bytes = raw
        input_text = extract_text_from_docx(raw)
        if input_text:
            st.success(f"✅ تم استخراج النص من ملف Word ({len(input_text.split()):,} كلمة)")
            with st.spinner("جارٍ تصدير ملف Word الأصلي إلى PDF مع الحفاظ على التنسيق والجداول والصور والأشكال..."):
                converted_pdf = convert_docx_to_pdf_bytes(raw)
                conversion_diag = get_last_docx_conversion_diagnostic()
            if converted_pdf:
                original_pdf_bytes = converted_pdf
                engine_name = conversion_diag.get("engine") or "محرك التحويل"
                st.info(
                    f"✅ تم تصدير Word الأصلي إلى PDF بواسطة {engine_name} دون أي تعديل مسبق. "
                    "سيُنشأ التقرير عليه بنفس غلاف وتظليل وملخص تقرير PDF تماماً."
                )
            else:
                st.error(
                    "تعذّر تحويل Word إلى PDF داخل بيئة الاستضافة، ولذلك لا يمكن إنشاء تقرير "
                    "مطابق لتقرير PDF مع الحفاظ على الجداول والصور والتنسيق."
                )
                st.warning(
                    conversion_diag.get("message")
                    or "على Streamlit Community Cloud أضف LibreOffice إلى packages.txt، وليس requirements.txt فقط."
                )
                details = (conversion_diag.get("details") or "").strip()
                if details:
                    with st.expander("التفاصيل الفنية للتحويل"):
                        st.code(details)
        else:
            st.error("تعذّر استخراج النص من ملف Word. تأكد من تثبيت python-docx.")


# ── Buttons ───────────────────────────────────────────────────────────────────
col_btn, col_clear = st.columns([3, 1])
with col_btn:
    analyze_btn = st.button("🔍 فحص الآن", use_container_width=True, type="primary")
with col_clear:
    if st.button("🗑️ مسح", use_container_width=True):
        st.session_state.pop("last_result", None)
        st.session_state.pop("last_text", None)
        st.session_state.pop("last_name", None)
        st.session_state.pop("last_pdf_bytes", None)
        st.session_state.pop("last_docx_bytes", None)
        st.rerun()

if analyze_btn and input_text and input_text.strip():
    with st.spinner("جارٍ الفحص..."):
        result = _ai_fingerprint_score(input_text.strip())
    st.session_state["last_result"]     = result
    st.session_state["last_text"]       = input_text.strip()
    st.session_state["last_name"]       = uploaded_name
    st.session_state["last_pdf_bytes"]  = original_pdf_bytes   # PDF أصلي أو PDF مُصدَّر من Word الأصلي
    st.session_state["last_docx_bytes"] = original_docx_bytes

st.markdown('</div>', unsafe_allow_html=True)


# ── Results ───────────────────────────────────────────────────────────────────
if "last_result" in st.session_state:
    st.markdown("### نتيجة التحليل")
    r   = st.session_state["last_result"]
    pct = r["percentage"]
    clr = r["color"]
    pct_label = r.get("display_percentage", _format_percentage(pct))
    human_label = _format_human_percentage(pct, r["human_score"])

    # Meter
    st.markdown(f"""
    <div class="meter-wrap">
        <div class="meter-pct" style="color:{clr}">{pct_label}</div>
        <div class="meter-label" style="color:{clr}">{r['verdict']}</div>
        <div class="meter-human">بشري: {human_label}</div>
        <div class="bar-track">
            <div class="bar-fill" style="width:{pct}%;background:{clr}"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.caption(
        f"المحرك {r.get('engine_version', '4.0')}: تحليل مقطعي متعدد المؤشرات يجمع القوالب اللغوية، "
        "وتجانس أطوال الجمل، والتكرار النصي، وبدايات الجمل، والانتقالات، والتنوع المعجمي. "
        "النتيجة مؤشر للمراجعة وليست إثباتاً قاطعاً أو بديلاً عن التحقق البشري."
    )
    if r.get("reference_words_excluded", 0) > 0:
        st.success(
            f"✅ تم استبعاد {r['reference_words_excluded']:,} كلمة من قسم المراجع "
            f"و{r.get('inline_citation_words_removed', 0):,} كلمة من علامات الاستشهاد داخل المتن قبل الحساب."
        )
    elif not r.get("reference_section_found", False):
        st.info("ℹ️ لم يُكتشف قسم مراجع مستقل. تم مع ذلك حذف الاستشهادات المضمنة التي أمكن التعرف عليها.")

    # Stats
    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-box"><div class="stat-num">{r['n_words']:,}</div><div class="stat-lbl">كلمة محللة</div></div>
        <div class="stat-box"><div class="stat-num">{r['n_sents']}</div><div class="stat-lbl">جملة</div></div>
        <div class="stat-box"><div class="stat-num">{r['avg_sent_len']}</div><div class="stat-lbl">كلمة/جملة</div></div>
        <div class="stat-box"><div class="stat-num">{r['t1_count']}</div><div class="stat-lbl">عبارة T1</div></div>
        <div class="stat-box"><div class="stat-num">{r['t2_total']}</div><div class="stat-lbl">نمط T2</div></div>
        <div class="stat-box"><div class="stat-num">{r['reference_words_excluded']:,}</div><div class="stat-lbl">كلمة مراجع مستبعدة</div></div>
        <div class="stat-box"><div class="stat-num">{r['confidence_percentage']:.0f}%</div><div class="stat-lbl">كفاية الأدلة</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-box"><div class="stat-num">{r.get('chunk_count', 1)}</div><div class="stat-lbl">مقاطع تحليلية</div></div>
        <div class="stat-box"><div class="stat-num">{r.get('sent_len_cv', 0):.2f}</div><div class="stat-lbl">تذبذب طول الجمل</div></div>
        <div class="stat-box"><div class="stat-num">{r.get('ngram_repeat_ratio', 0)*100:.1f}%</div><div class="stat-lbl">تكرار العبارات</div></div>
        <div class="stat-box"><div class="stat-num">{r.get('opener_repeat_ratio', 0)*100:.1f}%</div><div class="stat-lbl">تكرار بدايات الجمل</div></div>
        <div class="stat-box"><div class="stat-num">{r.get('high_risk_chunk_share', 0):.0f}%</div><div class="stat-lbl">مقاطع مرتفعة الإشارة</div></div>
        <div class="stat-box"><div class="stat-num">{r.get('evidence_families', 0)}</div><div class="stat-lbl">عائلات أدلة مستقلة</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Layers
    st.markdown("### تفصيل الطبقات")
    for title, raw_val, lcolor in [
        ("T1 — عبارات موزونة وصيغ جاهزة", r["t1_score"],    "#e74c3c"),
        ("T2 — أنماط تركيبية متكررة",   r["t2_score"],    "#e67e22"),
        ("Style — القياسات الأسلوبية المتقدمة", r["style_score"], "#3498db"),
        ("Struct — انتظام البنية", min(r["struct_boost"] * 10, 1.0), "#9b59b6"),
    ]:
        bar_pct = int(raw_val * 100)
        st.markdown(f"""
        <div class="layer-card">
            <span class="layer-title">{title}</span>
            <span class="layer-val" style="color:{lcolor}">{raw_val:.3f}</span>
            <div class="layer-bar">
                <div class="layer-bar-fill" style="width:{bar_pct}%;background:{lcolor}"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # T1 Hits
    if r["t1_hits"]:
        st.markdown("### 🎯 عبارات T1 المكتشفة")
        tags = "".join(f'<span class="hit-tag">{h}</span>' for h in r["t1_hits"])
        st.markdown(f'<div style="line-height:2.4;direction:rtl">{tags}</div>', unsafe_allow_html=True)

    # T2
    if r["t2_matched"]:
        st.markdown("### 🔎 أنماط T2 المكتشفة")
        for cnt, pat in r["t2_matched"]:
            st.markdown(
                f'<span class="hit-tag">×{cnt}</span> <code style="font-size:.8rem;direction:ltr">{pat}</code>',
                unsafe_allow_html=True
            )

    # Top keyword
    if r["top_kw"]:
        st.markdown(
            f"**الكلمة الأكثر تكراراً:** `{r['top_kw']}` "
            f"× {r['top_kw_count']} من {r['n_words']:,} كلمة "
            f"({r['top_kw_count']/r['n_words']*100:.2f}%)"
        )

    st.divider()

    # ── PDF / DOCX Report Download ─────────────────────────────────────────────
    if RLAB_OK:
        st.markdown("### 📥 تحميل التقرير الكامل")

        saved_text                 = st.session_state.get("last_text", "")
        saved_name                 = st.session_state.get("last_name", "Document")
        saved_pdf_bytes            = st.session_state.get("last_pdf_bytes", None)
        saved_docx_bytes           = st.session_state.get("last_docx_bytes", None)

        if saved_text and saved_pdf_bytes:
            # ── تقرير واحد موحد: PDF أصلي أو PDF مُصدَّر من Word الأصلي ───
            is_converted_docx = saved_docx_bytes is not None
            label_spinner = (
                "جارٍ توليد تقرير PDF الموحد من ملف Word المُصدَّر مع الحفاظ على تخطيطه..."
                if is_converted_docx
                else "جارٍ توليد التقرير من ملف PDF الأصلي..."
            )
            with st.spinner(label_spinner):
                pdf_bytes = generate_report_pdf_from_original(
                    saved_pdf_bytes, saved_text, saved_name
                )
            if pdf_bytes:
                report_filename = f"AI_Report_{saved_name.replace('.', '_')}.pdf"
                btn_label = (
                    "⬇️  تحميل تقرير Word بصيغة PDF (مطابق لمسار تقرير PDF)"
                    if is_converted_docx
                    else "⬇️  تحميل التقرير المظلل من PDF الأصلي"
                )
                st.download_button(
                    label=btn_label,
                    data=pdf_bytes,
                    file_name=report_filename,
                    mime="application/pdf",
                    use_container_width=True,
                )

                no_highlight_note = (
                    " · بدون أي تظليل لأن النتيجة *%"
                    if not _highlighting_allowed(r.get('percentage', 0))
                    else " · تظليل أزرق سماوي فوق المقاطع المختارة"
                )
                info_detail = (
                    "✅ تقرير Word خرج عبر نفس مسار تقرير PDF: غلاف احترافي · صفحات Word بعد تصديرها كما هي "
                    "بجداولها وصورها وأشكالها ورؤوسها وتذييلاتها · المراجع مستبعدة · صفحة ملخص"
                    + no_highlight_note
                    if is_converted_docx
                    else
                    "✅ التقرير يحتوي على: صفحة غلاف · الصفحات الأصلية كما هي · المراجع بدون تظليل · ملخص الإشارات"
                    + no_highlight_note
                )
                st.markdown(
                    f"<div class='info-note'>{info_detail}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.warning("تعذّر توليد التقرير. تأكد من تثبيت PyMuPDF و reportlab.")

        elif saved_text and saved_docx_bytes:
            # ── حل أخير فقط إذا تعذرت كل مسارات الحفاظ على الأصل ────────────
            with st.spinner("جارٍ توليد التقرير النصي الاحتياطي..."):
                pdf_bytes = generate_report_pdf_text_only(saved_text, saved_name)
            if pdf_bytes:
                report_filename = f"AI_Report_{saved_name.replace('.', '_')}.pdf"
                st.download_button(
                    label="⬇️  تحميل التقرير النصي الاحتياطي",
                    data=pdf_bytes,
                    file_name=report_filename,
                    mime="application/pdf",
                    use_container_width=True,
                )
                st.markdown(
                    "<div class='info-note'>"
                    "⚠️ هذا المسار احتياطي فقط عند تعذّر الحفاظ على الأصل."
                    "</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.warning("تعذّر توليد التقرير. تأكد من تثبيت reportlab.")
    else:
        st.info("💡 لتفعيل تصدير PDF: `pip install reportlab`")

    st.markdown(
        f"<div style='text-align:center;font-size:.82rem;opacity:.5;direction:ltr'>"
        f"Displayed score: {pct_label} | Decision: {r['decision']} | Evidence sufficiency: {r['confidence_percentage']:.0f}%"
        f"</div>",
        unsafe_allow_html=True,
    )

elif analyze_btn and not (input_text and input_text.strip()):
    st.warning("الرجاء رفع ملف PDF أو Word أولاً.")
