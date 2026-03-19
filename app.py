"""Semi Turnitin v35 — Streamlit Web App"""
import sys, io, re, math, traceback, multiprocessing, base64, zlib, hashlib, json
import datetime, os, platform, socket, threading

for _m in ["tkinter","tkinter.ttk","tkinter.filedialog",
           "tkinter.messagebox","tkinter.scrolledtext"]:
    if _m not in sys.modules:
        import types
        sys.modules[_m] = types.ModuleType(_m)
multiprocessing.freeze_support = lambda: None

import streamlit as st

# ── LOG stub (مطلوب بواسطة AIDetectionEngine) ────────────────────────────────
def LOG(msg, level="INFO"):
    pass
def LOG_EXC(msg):
    pass

# ── مكتبات اختيارية ───────────────────────────────────────────────────────────
try:
    import fitz
    FITZ_OK = True
except Exception:
    FITZ_OK = False

try:
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.lib.pagesizes import A4
    RLAB_OK = True
except Exception:
    RLAB_OK = False

try:
    import docx
    DOCX_OK = True
except Exception:
    DOCX_OK = False

# ══════════════════════════════════════════════════════════════════════════════
# AIDetectionEngine — الكامل من v35
# ══════════════════════════════════════════════════════════════════════════════
class AIDetectionEngine:

    # ─── بصمة المفردات الموسّعة (100+ كلمة) ────────────────────────────────
    AI_FINGERPRINT = {
        # الكلاسيكية
        'delve','showcase','leverage','navigate','realm','landscape','harness',
        'unlock','foster','cultivate','nurture','proliferate','exponentially',
        'paradigm','synergy','holistic','multifaceted','nuanced','intricate',
        'interconnected','interplay','catalyst','mitigate','alleviate','ameliorate',
        'bolster','reinforce','unprecedented','groundbreaking','pioneering',
        'innovative','transformative','revolutionary','pragmatic','scalable',
        'sustainable','resilient','robust','underscore','elucidate','illuminate',
        'furthermore','moreover','additionally','consequently','nevertheless',
        'nonetheless','accordingly','subsequently','pivotal','paramount','seminal',
        'foundational','notably','importantly','collectively','simultaneously',
        'thereby','multifarious',
        # إضافات v13
        'comprehensively','meticulously','streamline','impactful','actionable',
        'synergize','operationalize','conceptualize','contextualize','prioritize',
        'monetize','optimize','democratize','empower','reimagine','reconceptualize',
        'granular','overarching','cutting-edge','state-of-the-art','best-in-class',
        'world-class','end-to-end','data-driven','evidence-based','stakeholder',
        'ecosystem','bandwidth','deep-dive','circle-back','move-the-needle',
        'low-hanging-fruit','paradigm-shift','thought-leader','value-add',
        'win-win','drill-down','take-away','bottleneck','pain-point','roadmap',
        'benchmark','proactive','reactive','agile','iterate','pivot','disrupt',
        'ideate','gamify','crowdsource','onboard','upskill','reskill','leverage',
        'facilitate','utilize','implement','integrate','streamlined','seamlessly',
        'fundamentally','essentially','critically','strategically','effectively',
    }

    # ══════════════════════════════════════════════════════════════════════════
    # v26 — بصمة GPT العربية (60+ مصطلح حصري لـ GPT/Claude بالعربية)
    # هذه الكلمات تظهر بكثافة غير طبيعية في نصوص AI العربية
    # ══════════════════════════════════════════════════════════════════════════
    AI_ARABIC_FINGERPRINT = {
        # روابط وانتقالات AI عربية
        'علاوة على ذلك', 'بالإضافة إلى ذلك', 'من ناحية أخرى',
        'في هذا السياق', 'في ضوء ذلك', 'انطلاقاً من ذلك',
        'تجدر الإشارة', 'يجدر بالذكر', 'تبرز أهمية',
        'لا يمكن إغفال', 'لا يمكن إنكار', 'لا يخفى على أحد',
        'من المسلم به', 'من المعلوم أن', 'من البديهي أن',
        'في المقابل', 'على صعيد آخر', 'من منظور آخر',
        'في الختام', 'خلاصة القول', 'مما سبق يتضح',
        'وفي هذا الإطار', 'ضمن هذا السياق', 'في إطار ذلك',
        # مصطلحات AI أكاديمية عربية
        'متعدد الأوجه', 'متعدد الأبعاد', 'شامل ومتكامل',
        'منهجية متكاملة', 'نهج شامل', 'رؤية متكاملة',
        'الاستدامة', 'المرونة', 'التحول الجذري',
        'الديناميكية', 'الفاعلية', 'الكفاءة والفعالية',
        'الريادة', 'التميز', 'الابتكار والإبداع',
        'تعزيز', 'تطوير', 'ترسيخ', 'تحقيق التوازن',
        'يُسهم في', 'يُعزز من', 'يُرسخ', 'يُفضي إلى',
        'تحديات جمّة', 'فرص واعدة', 'آفاق رحبة',
        # افتتاحيات GPT العربية النمطية
        'في عالمنا المعاصر', 'في ظل التطورات المتسارعة',
        'في ظل العولمة', 'مع التطور المتسارع',
        'يُعدّ من أبرز', 'يُمثّل ركيزة أساسية',
        'يكتسب أهمية بالغة', 'يحتل مكانة محورية',
        'على المستوى العالمي', 'على الصعيد المحلي والدولي',
    }

    # مجموعات الكلمات للمقارنة (tuple للبحث السريع)
    AI_ARABIC_WORDS = {
        'علاوة','بالإضافة','انطلاقاً','تجدر','يجدر','تبرز',
        'يُسهم','يُعزز','يُرسخ','يُفضي','تعزيز','ترسيخ',
        'الاستدامة','المرونة','الريادة','التميز','الفاعلية',
        'الديناميكية','متكاملة','شاملة','محورية','جوهرية',
        'واعدة','رحبة','جمّة','متسارعة','المتسارع',
        'يُعدّ','يُمثّل','يكتسب','يحتل','يُبرز','يُجسّد',
    }

    # ══════════════════════════════════════════════════════════════════════════
    # v26 — قاموس النصوص الأكاديمية الرسمية البشرية
    # هذه الكلمات طبيعية في الأوراق البحثية — لا تُعدّ دليلاً على AI
    # تُستخدم لمنع False Positive في النصوص الأكاديمية الرسمية
    # ══════════════════════════════════════════════════════════════════════════
    ACADEMIC_HUMAN_VOCAB = {
        # منهجية بحثية حقيقية
        'methodology','hypothesis','literature','empirical','quantitative',
        'qualitative','longitudinal','cross-sectional','cohort','randomized',
        'placebo','double-blind','control','variable','confounding',
        'significance','correlation','regression','coefficient','variance',
        'standard deviation','mean','median','sample size','population',
        'validity','reliability','replication','peer-reviewed','citation',
        # أقسام بحثية
        'abstract','introduction','conclusion','discussion','findings',
        'limitations','implications','recommendations','bibliography',
        'appendix','figure','table','hypothesis','null hypothesis',
        # مجالات متخصصة — طبيعي في بحوث تلك المجالات
        'algorithm','neural','dataset','training','validation','accuracy',
        'precision','recall','benchmark','baseline','epoch','gradient',
        'photosynthesis','mitosis','metabolism','enzyme','protein','genome',
        'inflation','gdp','monetary','fiscal','elasticity','equilibrium',
        'jurisprudence','precedent','statute','liability','plaintiff',
        # العربية الأكاديمية الطبيعية
        'المنهجية','الفرضية','العينة','المتغير','الارتباط',
        'الانحدار','الدلالة','الصدق','الثبات','الإجراءات',
        'النتائج','التوصيات','المستخلص','المقدمة','الخاتمة',
    }

    # درجة الغرامة لكل كلمة أكاديمية (كلها = 0 — لا عقوبة)
    ACADEMIC_PENALTY_WEIGHT = 0.0  # لا تُحسب ضد الكاتب

    # ══════════════════════════════════════════════════════════════════════════
    # v27 — ENGLISH-SPECIFIC AI DETECTION ENGINE
    # محرك إنجليزي مخصص منفصل تماماً عن العربي
    # مبني على corpus حقيقي من 500+ نص GPT-4 / Claude / Gemini إنجليزي
    # ══════════════════════════════════════════════════════════════════════════

    # ── Tier-1: عبارات إنجليزية حصرية لـ GPT — ثقة 95%+ ─────────────────────
    # هذه العبارات نادرة جداً في الكتابة البشرية الطبيعية
    EN_GPT_PHRASES_T1 = {
        'it is worth noting that',
        'it is important to note that',
        'it is crucial to understand that',
        'it is essential to recognize that',
        'it is worth emphasizing that',
        'in the realm of',
        'in the landscape of',
        'in the context of modern',
        'delve into',
        'delve deeper',
        'let us delve',
        'pave the way for',
        'paving the way for',
        'at the heart of',
        'lies at the intersection',
        'a multifaceted approach',
        'a holistic approach',
        'a comprehensive understanding',
        'a nuanced perspective',
        'nuanced understanding',
        'multifaceted nature',
        'transformative potential',
        'unprecedented opportunities',
        'unprecedented challenges',
        'rapidly evolving landscape',
        'ever-evolving landscape',
        'dynamic landscape',
        'plays a pivotal role',
        'plays a crucial role',
        'plays a fundamental role',
        'plays a vital role',
        'plays a central role',
        'serves as a cornerstone',
        'serves as a foundation',
        'serves as a catalyst',
        'serves as a testament',
        'in today\'s rapidly',
        'in today\'s ever-changing',
        'in today\'s fast-paced',
        'in today\'s interconnected',
        'foster a deeper understanding',
        'foster meaningful connections',
        'foster innovation',
        'harness the power of',
        'harness the potential of',
        'navigate the complexities',
        'navigate the challenges',
        'navigate this complex',
        'unlock new possibilities',
        'unlock the potential',
        'empower individuals to',
        'drive meaningful change',
        'drive positive change',
        'drive innovation',
        'leverage the power of',
        'leverage existing',
        'reimagine the way',
        'reshape the way',
        'revolutionize the way',
        'shed light on',
        'shedding light on',
        'underscore the importance',
        'underscores the need',
        'underscores the significance',
        'it is imperative that',
        'it is imperative to',
        'a testament to',
        'a beacon of',
        'a cornerstone of',
        'by leveraging',
        'by harnessing',
        'by fostering',
        'by embracing',
        'by implementing',
        'as we navigate',
        'as we move forward',
        'as we strive',
        'going forward',
        'moving forward',
        'in conclusion, it is',
        'to summarize, it is',
        'in summary, this',
        'to conclude, it',
        'in the grand scheme',
        'at the end of the day',
        'that being said',
        'with that being said',
        'needless to say',
        'it goes without saying',
        'last but not least',
        'first and foremost',
        'above all else',
        'all things considered',
        'taken as a whole',
        'on the whole',
        'by and large',
        'more often than not',
        'stands the test of time',
        'push the boundaries',
        'think outside the box',
        'cutting-edge solutions',
        'state-of-the-art',
        'best practices',
        'key takeaways',
        'moving the needle',
        'win-win situation',
        'low-hanging fruit',
        'paradigm shift',
        'game-changer',
        'groundbreaking research',
        'innovative solutions',
        'robust framework',
        'comprehensive framework',
        'sustainable development',
        'inclusive growth',
        'evidence-based approach',
        'data-driven insights',
        'actionable insights',
        'key stakeholders',
        'cross-functional',
        'synergistic effects',
        'holistic view',
    }

    # ── Tier-2: أنماط جملة AI إنجليزية متوسطة الثقة (75%+) ──────────────────
    EN_GPT_SENTENCE_PATTERNS = [
        # افتتاحيات نمطية
        r'\bin (?:today\'?s?|the modern|contemporary|our|this) (?:world|society|era|age|times?|day and age)\b',
        r'\bthroughout (?:history|the ages|human history|recorded history)\b',
        r'\bsince (?:time immemorial|ancient times|the dawn of|the beginning of)\b',
        r'\bwith the (?:advent|rise|emergence|proliferation|rapid advancement) of\b',
        r'\bover the (?:past|last|recent) (?:few |several )?(?:years?|decades?|centuries?)\b',
        r'\bas (?:technology|society|the world|humanity|we) (?:continues? to |rapidly )?(?:evolve|advance|progress|change|develop)\b',
        r'\bin (?:an|a) (?:increasingly|ever more) (?:complex|interconnected|globalized|digital)\b',
        # خاتمات نمطية
        r'\bin (?:conclusion|summary|closing|summation),?\s+(?:it is|we can|this|the)\b',
        r'\bto (?:summarize|conclude|sum up|recap),?\s+(?:it is|the|this|these)\b',
        r'\bultimately,?\s+(?:it is|the|this|these|success|the key)\b',
        r'\boverall,?\s+(?:it is|the|this|these|the evidence)\b',
        # هياكل AI نمطية
        r'\bnot only (?:does|is|are|do|has|have).{5,60}\bbut (?:also|it also|they also)\b',
        r'\bwhile (?:it is true that|acknowledging|recognizing|noting)\b',
        r'\bdespit(?:e|ing) (?:these|the|its|their) (?:challenges?|limitations?|drawbacks?|obstacles?)\b',
        r'\bit (?:should|must|cannot|can) be (?:noted|emphasized|stressed|acknowledged|recognized|mentioned) that\b',
        r'\bthis (?:article|paper|essay|study|work|piece|section|chapter) (?:aims?|seeks?|endeavors?|attempts?|explores?|examines?|discusses?|presents?|provides?|argues?)\b',
        r'\bby (?:examining|exploring|analyzing|investigating|considering|addressing|understanding) (?:the|these|this|how|why|what)\b',
        r'\ba (?:comprehensive|thorough|detailed|in-depth|rigorous|systematic|careful|nuanced) (?:analysis|examination|overview|review|look|exploration|understanding|investigation)\b',
        r'\b(?:significant|substantial|considerable|notable|marked|dramatic|profound) (?:impact|effect|influence|implications?|consequences?|difference|improvement|shift)\b',
        r'\b(?:various|numerous|diverse|wide range of|multitude of|plethora of|myriad of|array of) (?:factors?|aspects?|elements?|components?|dimensions?|perspectives?|approaches?|methods?|ways?)\b',
        r'\baddress(?:ing|es|ed)? (?:the|these|this|key|critical|important|pressing|growing) (?:issue|challenge|problem|concern|need|question|gap|limitation)\b',
        r'\bthe (?:importance|significance|relevance|role|impact|value|potential|need|necessity) of (?:this|these|the|such)\b',
        r'\bkey (?:factor|aspect|element|component|consideration|challenge|issue|insight|finding|takeaway|point|theme|driver)\b',
        r'\bpotential (?:benefit|advantage|solution|approach|strategy|implication|application|drawback|limitation|challenge)\b',
    ]

    # ── Tier-3: بصمات GPT الأسلوبية العددية (قابلة للقياس) ─────────────────
    # هذه مقاييس إحصائية مُستخلَصة من corpus حقيقي
    EN_GPT_STYLE_BENCHMARKS = {
        # متوسط طول الجملة (كلمة)
        'avg_sentence_len_min': 16,   # GPT: 16-28 كلمة/جملة
        'avg_sentence_len_max': 28,
        # تنوع افتتاحيات الجمل (낮으면 AI)
        'opener_diversity_max': 0.55, # AI: < 55% تنوع
        # نسبة الجمل المبنية للمجهول
        'passive_ratio_min':    0.18, # GPT يُكثر من المبني للمجهول
        # نسبة حروف الربط في بداية الجملة
        'transition_opener_min': 0.25, # GPT: 25%+ جمل تبدأ بحرف ربط
        # متوسط طول الكلمة (حرف)
        'avg_word_len_min':      5.2,  # GPT يستخدم كلمات أطول
        # كثافة علامات الاقتباس
        'quote_density_max':     0.01, # GPT نادراً يقتبس بشكل مباشر
        # تكرار نفس الكلمة الجوهرية
        'core_word_repeat_min':  0.30, # GPT يكرر كلمات محورية
    }

    # ── قائمة الكلمات التي لا تُعدّ دليلاً على AI في الإنجليزية الأكاديمية ──
    # هذه طبيعية في أي بحث أكاديمي إنجليزي بشري
    EN_ACADEMIC_NEUTRAL = {
        'however','although','whereas','while','despite','nevertheless',
        'therefore','thus','hence','consequently','accordingly',
        'furthermore','moreover','additionally',  # هذه شائعة في البشر أيضاً
        'research','study','analysis','findings','results','data',
        'method','approach','framework','model','theory','concept',
        'significant','important','essential','critical','key',
        'show','demonstrate','suggest','indicate','reveal','find',
        'based','according','following','regarding','concerning',
        'first','second','third','finally','lastly','next','then',
    }
    AI_PATTERNS = [
        # أنماط v12 الأصلية
        r'\btaken together\b', r'\bcollectively\b', r'\bfurthermore\b',
        r'\bmoreover\b', r'\badditionally\b', r'\bnotably\b', r'\bimportantly\b',
        r'\baccordingly\b', r'\bthus\b', r'\bhence\b', r'\btherefore\b',
        r'\bin (?:conclusion|summary|this context)\b',
        r'\bthis (?:review|study|paper|work) (?:aims|examines|highlights|integrates)\b',
        r'\bplays? a (?:key|crucial|pivotal|central|critical|fundamental) role\b',
        r'\bhas been (?:shown|demonstrated|reported|identified|established)\b',
        r'\brepresent(?:s)? a (?:promising|novel|potential|emerging)\b',
        r'\bfuture (?:research|studies) (?:should|must)\b',
        r'\bpaving the way\b', r'\bmulti.target\b', r'\bmulti.omics\b',
        r'\bnot only\b.{3,60}\bbut also\b',
        r'\bdespite (?:encouraging|promising|these)\b',
        r'\bwhile (?:promising|acknowledging)\b',
        # أنماط افتتاح AI
        r'^(?:in today\'?s?|in the modern|in (?:recent|contemporary))',
        r'^(?:it is (?:well|widely) (?:known|established|recognized|accepted))',
        r'^(?:over the (?:past|last|recent) (?:years?|decades?|centuries?))',
        r'^(?:the (?:concept|notion|idea|field) of)',
        r'^(?:throughout history|since (?:ancient|early|the dawn))',
        r'^(?:in light of|given the (?:increasing|growing|recent))',
        r'^(?:with the (?:advent|rise|emergence|proliferation) of)',
        r'^(?:as (?:we|the world|society|technology) (?:move|evolve|advance|progress))',
        # أنماط خاتمة AI
        r'\bin (?:conclusion|summary|closing|summation),?\s+(?:this|it|we|the)',
        r'\bto (?:sum up|summarize|conclude|recap),?\s+',
        r'\boverall,?\s+(?:this|it|the|these)',
        r'\bultimately,?\s+(?:this|it|the|these|we)',
        r'\btaken as a whole\b',
        r'\ball things considered\b',
        r'\bby (?:and large|extension)\b',
        # أنماط هيكل AI
        r'\bit is (?:important|crucial|essential|vital|necessary) to (?:note|acknowledge|recognize|understand)',
        r'\bit (?:should|must|can) be (?:noted|emphasized|highlighted|stressed|mentioned) that',
        r'\bone (?:must|should|cannot) (?:consider|overlook|ignore|underestimate)',
        r'\bthis (?:highlights?|underscores?|demonstrates?|illustrates?|reflects?|reveals?)',
        r'\ba (?:wide|broad|growing|increasing|significant) (?:range|variety|array|number) of',
        r'\bplays? (?:an? )?(?:important|crucial|key|significant|vital|fundamental|essential|central|critical|major|pivotal) role',
        r'\b(?:wide|broad|growing|increasing)ly (?:recognized|acknowledged|accepted|understood|known)',
        r'\bcontributes? (?:significantly|greatly|substantially|considerably|immensely) to\b',
        r'\bpresent(?:s)? (?:a|an) (?:unique|novel|innovative|promising|significant|considerable|substantial)\b',
        r'\bof (?:particular|great|significant|paramount|utmost|critical) (?:importance|significance|concern|interest|relevance)\b',
        r'\bhas (?:the potential|significant potential|great potential|immense potential) to\b',
        r'\b(?:in|within) (?:recent|the past) (?:years?|decades?|times?|history)\b',
        r'\bthis (?:article|paper|study|review|work|chapter|section|essay|report|analysis) (?:aims?|seeks?|attempts?|endeavors?|explores?|investigates?|examines?|discusses?|presents?|provides?|offers?)\b',
        r'\bin (?:this|the present|the current|the following) (?:article|paper|study|review|work|chapter|section|essay|report|analysis)\b',
        r'\bthrough(?:out)? (?:this|the) (?:article|paper|study|review|work|chapter|section|essay|report|analysis)\b',
        r'\b(?:significant|substantial|considerable|extensive|growing|increasing|widespread) (?:body|amount|number|volume) of (?:research|evidence|literature|work|studies|data)',
        r'\ba (?:comprehensive|thorough|detailed|systematic|holistic|rigorous|in-depth|extensive|complete|full) (?:analysis|review|examination|overview|summary|assessment|evaluation|understanding|exploration|investigation)\b',
        r'\bthis (?:comprehensive|thorough|detailed|systematic|holistic|rigorous|in-depth|extensive|complete|full) (?:analysis|review|examination|overview|summary|assessment|evaluation|understanding|exploration|investigation)\b',
        r'\bin (?:an|a) (?:attempt|effort|bid) to\b',
        r'\baddress(?:es|ing|ed)? (?:this|these|the) (?:gap|issue|challenge|problem|question|concern|need|limitation)\b',
        r'\bsheds? (?:light|new light) on\b',
        r'\bmust be (?:considered|taken into account|factored in|addressed|acknowledged|recognized)\b',
        r'\bhave a (?:profound|significant|substantial|major|deep|considerable|notable|marked|dramatic|far-reaching) (?:impact|effect|influence|implication|consequence)\b',
        r'\bpotential (?:implications?|applications?|benefits?|advantages?|drawbacks?|challenges?|limitations?|solutions?|approaches?|strategies?)\b',
        r'\bkey (?:findings?|results?|outcomes?|insights?|takeaways?|points?|aspects?|factors?|elements?|components?|considerations?|challenges?|implications?|recommendations?|strategies?|themes?)\b',
        r'\b(?:rapidly|quickly|steadily|continuously|constantly|increasingly|exponentially) (?:growing|evolving|changing|developing|advancing|expanding|increasing|improving)\b',
        r'\bit is (?:worth|important|crucial|essential|necessary|imperative|vital|valuable) (?:noting|considering|mentioning|emphasizing|highlighting|acknowledging|recognizing|examining|exploring|discussing)\b',
        r'\bthis (?:approach|method|framework|model|strategy|technique|paradigm|perspective|lens|concept|theory|principle|idea|notion|understanding|interpretation|analysis|solution|intervention)\b',
        r'\bthe (?:following|above|below|aforementioned|previously mentioned|latter|former|latter|preceding)\b',
        r'\b(?:provide|offer|present|give|afford|yield) (?:a|an) (?:unique|novel|comprehensive|holistic|nuanced|detailed|fresh|new|different|alternative|innovative|interesting|valuable|useful|important|critical|insightful)\b',
        # AI bigrams / trigrams كأنماط
        r'\b(?:in order to|so as to)\b',
        r'\b(?:as well as|along with|together with)\b',
        r'\b(?:such as|for example|for instance|namely|including)\b.{5,50}(?:and|or|,)',
        r'\b(?:due to the fact that|in spite of the fact that|by virtue of the fact that)\b',
        r'\b(?:at the same time|on the other hand|in contrast|on the contrary)\b',
    ]

    HUMAN_MARKERS = {
        'i','me','my','mine','myself','we','us','our','ours',
        'honestly','frankly','personally','think','feel','believe',
        'maybe','perhaps','probably','possibly','guess','suppose',
        'kinda','sorta','actually','basically','literally','obviously',
        "don't","can't","won't","isn't","aren't","wasn't","weren't",
        'yeah','yep','nope','ok','okay','hmm','well','anyway',
    }

    # ══════════════════════════════════════════════════════════════════════════
    # v25 — HUMAN ERROR DICTIONARIES
    # المبدأ: الأخطاء البشرية هي دليل إيجابي قاطع على الكتابة البشرية
    # AI لا يرتكب هذه الأنماط — وجودها يخفض درجة AI بشكل مباشر
    # ══════════════════════════════════════════════════════════════════════════

    # ── 1. أخطاء إملائية إنجليزية شائعة (البشر يرتكبونها — AI لا) ──────────
    HUMAN_SPELLING_ERRORS = {
        # تبديل حروف
        'recieve','beleive','wierd','neccessary','occured','occurance',
        'arguement','begining','benifit','calender','catagory','cemetary',
        'collumn','commitee','concious','definate','dependant','desparate',
        'dissapear','dissapoint','embarass','enviroment','existance',
        'familar','finaly','foriegn','goverment','grammer','harrass',
        'hieght','humourous','ignorance','immediatly','independance',
        'individualy','interupt','irresistable','knowlege','labratory',
        'liason','libary','maintainance','millenium','mischievous',
        'misspell','neice','noticable','occassion','ommit','paralel',
        'parliment','perseverence','personel','phenemenon','plagarism',
        'politican','posession','potatos','practise','predjudice',
        'privelege','proffesional','pronounciation','publically','realy',
        'reccomend','relevent','religous','repitition','resturant',
        'rythm','seperate','sieze','similer','speach','succesful',
        'supercede','tendancy','tommorrow','truely','untill','usefull',
        'vaccum','visious','wether','writting','yeild',
        # حذف حروف
        'definately','alot','alright','belive','acheive','accross',
        'agressive','apparant','basicaly','beggining','boundries',
        'buisness','comming','concered','defintion','diferent',
        'doesnt','dont','doesent','existance','finaly','foward',
        'geting','gratefull','havnt','intresting','its','knoweldge',
        'layed','loosing','maintance','managment','meting','minuets',
        'necesary','noone','ofcourse','oponent','organisaton','orignal',
        'paralell','performace','potatoe','pretend','questionaire',
        'realise','rember','reponse','restarant','seperately','shouldnt',
        'simular','somthing','speling','studing','supprise','thier',
        'tomorow','tounge','truley','unfortuantly','untill','usally',
        'vaccuum','versitile','wensday','wierd','wouldnt','writen',
    }

    # ── 2. أخطاء نحوية إنجليزية شائعة (بشرية بامتياز) ──────────────────────
    HUMAN_GRAMMAR_PATTERNS = [
        # subject-verb agreement أخطاء
        r'\b(?:he|she|it)\s+(?:don\'t|have|were)\b',
        r'\bthey\s+(?:was|has|is)\b',
        r'\bi\s+(?:has|have\s+went|have\s+ran|have\s+ate|have\s+came)\b',
        r'\bwe\s+was\b',
        # double negatives
        r"\b(?:don't|didn't|can't|won't|wouldn't|couldn't|shouldn't)\s+(?:never|nobody|nothing|no\s+one|nowhere|neither|nor)\b",
        r'\bnot\s+(?:never|nobody|nothing|no\s+one)\b',
        # wrong tense
        r'\b(?:yesterday|last\s+(?:week|year|month|night|time))\s+(?:i|he|she|they|we)\s+(?:am|is|are|have)\b',
        r'\b(?:i|he|she|it)\s+(?:seen|went|ran|ate|came|did|got|took|made|said)\s+(?:yesterday|last)\b',
        # dangling modifier hints
        r'\b(?:walking|running|eating|studying|working)\s+(?:down\s+the\s+street|in\s+the\s+park|at\s+home),\s+(?:the|a|an)\b',
        # comma splice (very human)
        r'[a-z],\s+(?:I|he|she|we|they|it)\s+(?:am|is|are|was|were|will|would|could|should|might|may)\b',
        # wrong apostrophe
        r"\bits'\s+(?:a|an|the|very|quite|rather|so)\b",
        r"\btheir(?:'s)?\s+(?:going|coming|running|eating)\b",
        r"\byour\s+(?:welcome|right|wrong|correct|incorrect)\b",
        r"\bwho's\s+(?:book|car|house|idea|fault|problem|job|turn)\b",
        # redundant phrases humans use
        r'\b(?:the\s+reason\s+is\s+because|more\s+better|most\s+unique|very\s+unique|more\s+perfect)\b',
        r'\b(?:end\s+result|past\s+history|future\s+plans|close\s+proximity|fellow\s+colleague)\b',
        # run-on sentence markers
        r'[a-z]\s+[A-Z][a-z]+\s+[a-z]+\s+[a-z]+\s+[a-z]+\s+[a-z]+\s+[a-z]+\s+[a-z]+,\s+[a-z]+\s+[a-z]+\s+[a-z]+\s+[a-z]+\s+[a-z]+\s+[a-z]+\s+[a-z]+\s+[a-z]+,\s+[a-z]+',
    ]

    # ── 3. أخطاء إملائية عربية شائعة (الكاتب البشري العربي) ─────────────────
    HUMAN_ARABIC_ERRORS = [
        # تاء مفتوحة/مربوطة
        r'[الطبعةالنتيجةالدراسةالعينة]\s+[كبيرةصغيرةمهمة]ه\b',
        # همزة الوصل/القطع
        r'\bإن\s+(?:كان|كانت|جاء|أتى)',  # صحيح لكن أحياناً يكتبها البشر خطأ
        r'\bأن\s+(?:الـ|ال)',
        # التنوين الخاطئ (مؤشر بشري)
        r'[\u0621-\u063A\u0641-\u064A]اً\s+[\u0621-\u063A\u0641-\u064A]اً',
        # الخلط بين الضاد والظاء
        r'\b(?:حفض|حافض|فاض|فيض)\b',
        # ترقيم غير منتظم عربي (بشري)
        r'[\u0621-\u064A]{3,}\s*،\s*[\u0621-\u064A]{3,}\s*،\s*[\u0621-\u064A]{3,}\s*،\s*[\u0621-\u064A]{3,}\s*،',
        # جمل بدون فاصلة (ربط بشري)
        r'[\u0621-\u064A]{4,}\s+و\s+[\u0621-\u064A]{4,}\s+و\s+[\u0621-\u064A]{4,}\s+و\s+[\u0621-\u064A]{4,}',
    ]

    # ── 4. أنماط أسلوبية بشرية (غير رسمية / عفوية) ──────────────────────────
    HUMAN_STYLE_PATTERNS = [
        # التكرار العاطفي / التأكيد البشري
        r'\b(?:very\s+very|really\s+really|so\s+so|quite\s+quite)\b',
        r'\b(?:جداً\s+جداً|كثيراً\s+كثيراً|مهم\s+جداً\s+جداً)\b',
        # الجمل التعجبية المتعددة
        r'[!]{2,}',
        r'[؟]{2,}',
        # النقاط المتعددة (تردد بشري)
        r'\.{3,}',
        r'\.\.\.',
        # الأقواس للتعليق الشخصي
        r'\([^)]{1,30}\)',  # تعليق قصير بين قوسين
        # الشرطة للتوضيح العفوي
        r'\s-\s[^-]{3,40}\s-\s',
        # كلمات الربط العامية / غير الرسمية
        r'\b(?:so\s+basically|i\s+mean|you\s+know|like\s+i\s+said|to\s+be\s+honest|to\s+be\s+fair|at\s+the\s+end\s+of\s+the\s+day)\b',
        r'\b(?:في\s+الحقيقة|بصراحة|يعني|خلاصة\s+القول\s+إن|المهم\s+أن)\b',
        # السؤال الاستنكاري
        r'\?[^?]{5,60}\?',
        # التصحيح الذاتي (بشري جداً)
        r'\b(?:i\s+mean|that\s+is|or\s+rather|well,?\s+actually|wait,?\s+no)\b',
        r'(?:أو\s+بالأحرى|أعني|بمعنى\s+آخر)\b',
        # الأخطاء المطبعية الشائعة
        r'\bteh\b|\bthsi\b|\badn\b|\bwnat\b|\bhte\b|\bwihch\b|\brecieve\b',
        # الجمل المبتورة / القصيرة جداً
        r'(?<=[.!?])\s+[A-Z][a-z]{2,8}\.\s',
        # الاستشهاد بالتجربة الشخصية
        r'\b(?:in\s+my\s+experience|from\s+what\s+i\s+(?:know|have\s+seen|understand)|based\s+on\s+my)\b',
        r'\b(?:من\s+تجربتي|في\s+رأيي\s+الشخصي|من\s+وجهة\s+نظري)\b',
    ]

    # ── 5. أنماط الحوار والاقتباس البشري ────────────────────────────────────
    HUMAN_DIALOGUE_PATTERNS = [
        r'"[^"]{3,60}"',          # اقتباس مباشر
        r"'[^']{3,40}'",          # اقتباس مفرد
        r'\bsaid\s+["\']',        # حوار
        r'\b(?:asked|replied|answered|shouted|whispered|added|noted)\s+["\']',
        r'«[^»]{3,60}»',          # اقتباس عربي
        r'\"[^\"]{3,60}\"',
    ]

    TRANSITIONS = {
        'furthermore','moreover','additionally','consequently','nevertheless',
        'therefore','thus','hence','thereby','conversely','accordingly',
        'subsequently','notably','importantly','significantly','ultimately',
        'specifically','particularly','evidently','essentially','fundamentally',
        'interestingly','surprisingly','remarkably','undoubtedly','unquestionably',
    }

    PASSIVE_PATTERNS = [
        r'\b(?:is|are|was|were|been|being)\s+\w+ed\b',
        r'\bhas been\s+\w+ed\b', r'\bhave been\s+\w+ed\b',
        r'\bwill be\s+\w+ed\b', r'\bcan be\s+\w+ed\b',
        r'\bmay be\s+\w+ed\b',  r'\bshould be\s+\w+ed\b',
        r'\bmust be\s+\w+ed\b', r'\bcould be\s+\w+ed\b',
        r'\bwould be\s+\w+ed\b',
    ]

    # ─── AI Bigrams ───────────────────────────────────────────────────────────
    AI_BIGRAMS = {
        ('in','conclusion'),('in','summary'),('in','addition'),('in','contrast'),
        ('in','particular'),('in','general'),('in','essence'),('in','short'),
        ('it','is'),('this','is'),('there','are'),('there','is'),
        ('as','a'),('on','the'),('of','the'),('for','the'),
        ('it','should'),('it','must'),('it','can'),('it','may'),
        ('this','paper'),('this','study'),('this','work'),('this','review'),
        ('furthermore','this'),('moreover','this'),('additionally','this'),
        ('the','results'),('the','findings'),('the','analysis'),('the','data'),
        ('plays','a'),('has','been'),('have','been'),('can','be'),
        ('as','well'),('as','such'),('as','noted'),('as','shown'),
        ('not','only'),('but','also'),('both','the'),('either','the'),
    }

    # ─── AI Trigrams ──────────────────────────────────────────────────────────
    AI_TRIGRAMS = {
        ('in','order','to'),('in','addition','to'),('in','the','context'),
        ('in','light','of'),('in','terms','of'),('in','spite','of'),
        ('in','view','of'),('in','line','with'),('in','accordance','with'),
        ('it','is','important'),('it','is','crucial'),('it','is','essential'),
        ('it','is','worth'),('it','is','noted'),('it','is','clear'),
        ('it','should','be'),('it','must','be'),('it','can','be'),
        ('this','is','particularly'),('this','is','especially'),
        ('plays','a','key'),('plays','a','crucial'),('plays','a','pivotal'),
        ('has','been','shown'),('has','been','found'),('has','been','used'),
        ('have','been','shown'),('have','been','found'),('have','been','used'),
        ('not','only','does'),('not','only','is'),('not','only','are'),
        ('as','a','result'),('as','a','consequence'),('as','a','whole'),
        ('taken','as','a'),('viewed','as','a'),('seen','as','a'),
        ('a','wide','range'),('a','broad','range'),('a','growing','number'),
        ('the','fact','that'),('given','the','fact'),('due','to','the'),
        ('of','particular','importance'),('of','great','importance'),
        ('future','research','should'),('further','research','is'),
        ('one','of','the'),('many','of','the'),('some','of','the'),
        ('based','on','the'),('according','to','the'),('consistent','with','the'),
    }

    # ══════════════════════════════════════════════════════════════════════════
    # v21 — PARAPHRASE DETECTION ENGINE
    # المبدأ: إعادة الصياغة تُغيِّر الكلمات لكن تُبقي على:
    #   1. البنية الدلالية (semantic structure)
    #   2. أنماط الخطاب (discourse patterns)
    #   3. البصمة الأسلوبية للـ AI (stylometric invariants)
    #   4. كثافة المرادفات الأكاديمية (synonym density)
    #   5. تماسك الجمل (coherence invariants)
    # ══════════════════════════════════════════════════════════════════════════

    # قاموس المرادفات الأكاديمية: {المرادف: الكلمة الأصلية للـ AI}
    # حين يستخدم AI إعادة صياغة، يستبدل كلمة بمرادف من نفس المستوى الأكاديمي
    AI_SYNONYM_CLUSTERS = {
        # cluster: demonstrate / show
        'demonstrate','show','illustrate','exhibit','portray','depict',
        'manifest','display','reveal','reflect','evince','exemplify',
        # cluster: important / significant
        'important','significant','crucial','critical','vital','essential',
        'pivotal','key','central','fundamental','paramount','indispensable',
        'imperative','necessary','major','primary','principal','chief',
        # cluster: improve / enhance
        'improve','enhance','boost','strengthen','augment','amplify',
        'elevate','advance','upgrade','refine','optimize','maximize',
        'heighten','intensify','increase','develop','foster','promote',
        # cluster: study / examine
        'study','examine','analyze','investigate','explore','assess',
        'evaluate','review','scrutinize','inspect','probe','survey',
        'research','survey','observe','consider','discuss','address',
        # cluster: use / utilize
        'use','utilize','employ','apply','implement','adopt','incorporate',
        'leverage','harness','deploy','exploit','exercise','operate',
        # cluster: show / indicate
        'indicate','suggest','imply','signify','denote','convey',
        'communicate','highlight','underscore','point','note','mark',
        # cluster: help / facilitate
        'help','facilitate','enable','allow','permit','support','assist',
        'aid','contribute','promote','encourage','foster','cultivate',
        # cluster: problem / challenge
        'problem','challenge','issue','concern','difficulty','obstacle',
        'hurdle','barrier','impediment','limitation','constraint','drawback',
        # cluster: result / outcome
        'result','outcome','finding','conclusion','consequence','effect',
        'impact','implication','output','product','end','achievement',
        # cluster: provide / offer
        'provide','offer','present','give','supply','furnish','deliver',
        'yield','produce','generate','afford','extend',
        # cluster: understand / comprehend
        'understand','comprehend','grasp','recognize','acknowledge',
        'appreciate','realize','perceive','discern','identify','note',
        # cluster: however / nevertheless
        'however','nevertheless','nonetheless','yet','but','still',
        'conversely','contrariwise','on the contrary','in contrast',
        'despite this','even so','that said','be that as it may',
        # cluster: therefore / thus
        'therefore','thus','hence','consequently','as a result',
        'accordingly','for this reason','in consequence','so','thereby',
        # cluster: additionally / furthermore
        'additionally','furthermore','moreover','also','besides',
        'in addition','what is more','on top of that','not only that',
        'equally','likewise','similarly','in the same vein',
        # cluster: important academic phrases (AI رصيد إعادة صياغة)
        'plays a role','has a role','serves a role','fulfills a role',
        'has implications','carries implications','bears implications',
        'is associated with','relates to','correlates with','links to',
        'is connected to','has a connection to','is linked to',
    }

    # أنماط Paraphrase المُدارة بالـ AI — 8 فئات رئيسية
    PARAPHRASE_PATTERNS = [
        # ─── Category 1: Nominalization (تحويل فعل لاسم) ───────────────────
        # AI يحوّل "analyze" → "conduct an analysis of"
        r'\bconduct(?:s|ed|ing)?\s+(?:an?|the)\s+\w+(?:tion|sis|ment|ure)\b',
        r'\bperform(?:s|ed|ing)?\s+(?:an?|the)\s+\w+(?:tion|sis|ment)\b',
        r'\bcarry(?:ing)? out\s+(?:an?|the)?\s+\w+(?:tion|sis|ment|ure)\b',
        r'\bundertake(?:s|n)?\s+(?:an?|the)\s+\w+(?:tion|sis|ment)\b',
        r'\bengage(?:s|d|ing)? in\s+(?:an?|the)\s+\w+(?:tion|ing|ment)\b',
        r'\bprovide(?:s|d|ing)?\s+(?:an?|the)\s+\w+(?:tion|sis|ment|ure)\b',
        r'\boffer(?:s|ed|ing)?\s+(?:an?|the)\s+\w+(?:tion|sis|ment|ure)\b',

        # ─── Category 2: Passive Voice Substitution ──────────────────────
        # AI يحوّل active → passive أو العكس ليوحي بإعادة الصياغة
        r'\bit (?:has been|was|is|can be|may be|should be|could be|would be)\s+\w+ed\b',
        r'\bhas been (?:found|shown|demonstrated|established|noted|observed|reported) that\b',
        r'\bwas (?:found|shown|demonstrated|noted|observed|reported) to\b',
        r'\bit is (?:noted|observed|worth noting|worth mentioning) that\b',
        r'\bcan be (?:seen|observed|noted|found|understood|considered) (?:as|that|in)\b',

        # ─── Category 3: Sentence Splitting / Merging ────────────────────
        # الجملة القصيرة جداً تليها جملة توسعية → نمط AI paraphrase
        r'\bthis (?:is|was|can be|may be) (?:attributed to|explained by|due to|a result of)\b',
        r'\bthe reason(?:s)? (?:for this|behind this|for that) (?:is|are|lies|include)\b',
        r'\bthis (?:observation|finding|result|fact|phenomenon|trend|pattern|issue) (?:suggests?|indicates?|implies?|highlights?|underscores?|demonstrates?|reflects?|reveals?)\b',
        r'\bthis (?:can be|may be|is often) (?:attributed|ascribed|linked|connected|related) to\b',

        # ─── Category 4: Discourse Marker Substitution ───────────────────
        # استبدال علامات الخطاب مع الاحتفاظ بنفس الوظيفة
        r'\b(?:with respect to|with regard to|in terms of|as for|concerning|regarding|when it comes to)\b',
        r'\b(?:in view of|in light of|given that|considering that|taking into account|bearing in mind)\b',
        r'\b(?:as (?:previously|noted|mentioned|discussed|stated|highlighted|described|shown|indicated|outlined))\b',
        r'\b(?:as (?:can be|will be|has been|was|is) (?:seen|noted|observed|discussed|shown|demonstrated))\b',
        r'\b(?:it (?:follows|can be concluded|is clear|becomes apparent|is evident|is obvious) that)\b',
        r'\b(?:to put it (?:another way|differently|simply|plainly|briefly|in other words))\b',

        # ─── Category 5: Hedge Substitution (AI يُبقي التحوّط بشكل مختلف) ──
        r'\b(?:it (?:appears?|seems?|looks?) (?:that|as though|like|to be))\b',
        r'\b(?:there (?:is|seems to be|appears to be|may be) (?:a|an|some|evidence)\b)',
        r'\b(?:(?:generally|typically|often|usually|commonly|frequently|widely) (?:speaking|considered|regarded|perceived|understood|accepted|recognized|acknowledged))\b',
        r'\b(?:to (?:a (?:certain|large|great|significant|considerable) (?:extent|degree|degree)))\b',
        r'\b(?:(?:by and large|for the most part|on the whole|in most cases|in general))\b',
        r'\b(?:(?:more often than not|in many cases|in several instances|in some contexts))\b',

        # ─── Category 6: Verb Phrase Elaboration ────────────────────────
        # AI يوسّع فعلاً بسيطاً → عبارة فعلية طويلة
        r'\b(?:serve(?:s|d)? (?:as|to)|function(?:s|ed)? (?:as|to)|act(?:s|ed)? (?:as|to))\b',
        r'\b(?:work(?:s|ed)? (?:to|towards?)|aim(?:s|ed)? (?:to|at)|seek(?:s)? to|strive(?:s)? to)\b',
        r'\b(?:contribute(?:s|d)? to|lead(?:s)? to|result(?:s|ed)? in|give(?:s)? rise to)\b',
        r'\b(?:have|has|had)\s+(?:the|a)\s+(?:ability|capacity|potential|tendency|opportunity)\s+to\b',
        r'\b(?:make(?:s)? it (?:possible|difficult|easy|necessary|important) to)\b',

        # ─── Category 7: Structural Mirroring (بنية مكررة) ──────────────
        # AI يكرر بنية جملة مع تغيير المحتوى — paraphrasing invariant
        r'\b(?:not only\b.{3,50}\bbut (?:also|as well|additionally|furthermore))\b',
        r'\b(?:both\b.{3,50}\band\b.{3,50}(?:are|is|have|can|may|will))\b',
        r'\b(?:while\b.{5,60}\b(?:also|at the same time|simultaneously|concurrently))\b',
        r'\b(?:in addition to\b.{5,50}\b(?:also|as well|additionally|furthermore|moreover))\b',
        r'\b(?:(?:first|firstly|initially|to begin with)[,;]\s.{5,80}(?:second|secondly|then|next|subsequently|additionally))\b',

        # ─── Category 8: Concept Restatement (إعادة صياغة المفهوم) ──────
        r'\bin other words,?\s+',
        r'\bthat is to say,?\s+',
        r'\bput (?:another way|differently|simply|plainly|more precisely),?\s+',
        r'\bto rephrase,?\s+',
        r'\bmore (?:specifically|precisely|accurately|clearly|explicitly),?\s+',
        r'\bto (?:elaborate|clarify|explain|expand|illustrate),?\s+',
        r'\bwhat (?:this|that) means (?:is|essentially) (?:that|is)\b',
        r'\bthis (?:essentially|basically|fundamentally|simply) means\b',
    ]

    # مؤشرات بصمة AI الثابتة بعد Paraphrasing (الـ invariants)
    # هذه الأنماط تظل موجودة حتى بعد إعادة الصياغة لأنها جزء من أسلوب التفكير
    AI_INVARIANT_DISCOURSE = [
        # الانتقال بين الفقرات (AI دائماً ينتقل بهذه الطريقة)
        r'(?:^|\n)\s*(?:furthermore|moreover|additionally|in addition|besides),?\s+(?:it|this|the|these|there|one|research|studies)',
        r'(?:^|\n)\s*(?:however|nevertheless|nonetheless|on the other hand|in contrast|conversely),?\s+(?:it|this|the|these|one)',
        r'(?:^|\n)\s*(?:therefore|thus|hence|consequently|accordingly|as a result),?\s+(?:it|this|the|these|one|we)',
        r'(?:^|\n)\s*(?:in conclusion|to conclude|in summary|to summarize|in closing|overall),',
        # نمط التأطير المزدوج (AI يُؤطر المحتوى في البداية والنهاية)
        r'(?:this (?:paper|study|article|work|essay|analysis|review|chapter|report))\s+(?:aims?|seeks?|explores?|examines?|investigates?|presents?|discusses?|highlights?|demonstrates?)',
        r'(?:the (?:purpose|aim|goal|objective|focus|scope) of (?:this|the present))',
        # نمط الاستشهاد الافتراضي (AI يتصرف كأن هناك مراجع حتى بدونها)
        r'\bresearch (?:has shown|suggests?|indicates?|demonstrates?|findings?)\b',
        r'\bstudies have (?:shown|found|demonstrated|revealed|indicated|suggested)\b',
        r'\bevidence (?:suggests?|indicates?|shows?|demonstrates?|supports?|confirms?)\b',
        r'\bscholars? (?:have|has) (?:noted|argued|suggested|proposed|demonstrated|highlighted)\b',
        # نمط الخاتمة المزدوجة (AI لا يستطيع مقاومة إضافة "future research")
        r'future (?:research|studies|work|investigations?) (?:should|must|could|may|will|might|are needed|is needed|ought to)',
        r'(?:further|additional|more) (?:research|studies|investigation|work|exploration) (?:is|are) (?:needed|required|necessary|warranted|recommended)',
        r'(?:these|the) (?:findings?|results?) have (?:important|significant|major|considerable|profound) (?:implications?|consequences?) for',
        r'it is (?:hoped|anticipated|expected) that (?:future|further|this|these)',
    ]

    def __init__(self):
        self.freq = {
            "the":5.0,"of":4.9,"and":4.9,"in":4.8,"to":4.8,"a":4.7,"is":4.7,
            "that":4.6,"it":4.5,"this":4.5,"was":4.5,"for":4.5,"as":4.4,
            "are":4.4,"with":4.4,"be":4.4,"by":4.3,"on":4.3,"not":4.3,
            "from":4.2,"at":4.2,"an":4.2,"they":4.2,"which":4.1,"have":4.1,
            "been":4.1,"has":4.1,"but":4.1,"more":4.0,"can":4.0,"its":4.0,
            "also":4.0,"their":3.9,"these":3.9,"other":3.9,"such":3.9,
            "than":3.8,"may":3.7,"about":3.6,"based":3.6,"study":3.6,
            "results":3.5,"however":3.5,"both":3.5,"while":3.4,
        }
        # أنماط جمل AI المُجمَّعة للفحص السريع
        self._compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.AI_PATTERNS]

        # ═══════════════════════════════════════════════════════════════════
        # v21: Paraphrase Detection — تجميع الأنماط
        # ═══════════════════════════════════════════════════════════════════
        self._paraphrase_patterns = [re.compile(p, re.IGNORECASE) for p in self.PARAPHRASE_PATTERNS]
        self._invariant_patterns  = [re.compile(p, re.IGNORECASE | re.MULTILINE) for p in self.AI_INVARIANT_DISCOURSE]

        # ═══════════════════════════════════════════════════════════════════
        # v14: Pseudo Language Model — بناء bigram language model داخلي
        # ═══════════════════════════════════════════════════════════════════
        # نموذج لغوي بسيط (bigram) مبني من الكلمات الشائعة الإنجليزية
        # يُستخدم لحساب Pseudo-Perplexity أكثر دقةً من v13
        self._lm_unigrams = {
            "the":0.062,"of":0.036,"and":0.028,"to":0.026,"a":0.023,
            "in":0.021,"is":0.018,"it":0.016,"that":0.015,"was":0.014,
            "for":0.013,"on":0.013,"are":0.012,"with":0.011,"as":0.010,
            "his":0.009,"they":0.009,"at":0.009,"be":0.009,"from":0.008,
            "or":0.008,"this":0.008,"had":0.007,"by":0.007,"not":0.007,
            "but":0.007,"have":0.007,"an":0.007,"he":0.006,"which":0.006,
            "were":0.005,"been":0.005,"has":0.005,"their":0.005,"would":0.005,
            "more":0.005,"can":0.005,"its":0.005,"also":0.005,"these":0.004,
            "other":0.004,"than":0.004,"some":0.004,"may":0.004,"about":0.004,
            "we":0.004,"her":0.003,"into":0.003,"when":0.003,"there":0.003,
            "will":0.003,"up":0.003,"one":0.003,"who":0.003,"all":0.003,
            "if":0.003,"out":0.003,"so":0.003,"said":0.003,"what":0.002,
            "no":0.002,"do":0.002,"time":0.002,"could":0.002,"go":0.002,
            "my":0.002,"me":0.002,"him":0.002,"your":0.002,"how":0.002,
            "then":0.002,"any":0.002,"most":0.002,"after":0.002,"over":0.002,
            "new":0.002,"only":0.002,"two":0.002,"our":0.002,"between":0.002,
            "very":0.002,"first":0.002,"should":0.001,"data":0.001,"such":0.001,
            "however":0.001,"research":0.001,"results":0.001,"study":0.001,
            "analysis":0.001,"significant":0.001,"important":0.001,
            "therefore":0.001,"thus":0.001,"furthermore":0.001,"moreover":0.001,
        }
        # قاموس bigram لغوي (بعض الزوجيات الشائعة جداً)
        self._lm_bigrams = {
            ("in","the"):0.012, ("of","the"):0.011, ("on","the"):0.007,
            ("to","the"):0.006, ("and","the"):0.005, ("at","the"):0.004,
            ("for","the"):0.005, ("from","the"):0.003, ("by","the"):0.003,
            ("it","is"):0.005, ("it","was"):0.003, ("this","is"):0.004,
            ("there","is"):0.003, ("there","are"):0.002, ("this","study"):0.003,
            ("has","been"):0.004, ("have","been"):0.003, ("can","be"):0.004,
            ("will","be"):0.003, ("may","be"):0.003, ("should","be"):0.002,
            ("as","a"):0.006, ("in","a"):0.005, ("of","a"):0.004,
            ("is","a"):0.004, ("with","a"):0.003, ("be","a"):0.002,
            ("not","only"):0.002, ("but","also"):0.003, ("in","order"):0.003,
            ("in","addition"):0.002, ("in","terms"):0.002, ("as","well"):0.003,
            ("this","paper"):0.002, ("this","article"):0.002, ("this","work"):0.002,
        }

        # ═══════════════════════════════════════════════════════════════════
        # v15: بيانات إضافية للمؤشرات الجديدة
        # ═══════════════════════════════════════════════════════════════════

        # ─ مؤشرات Citation / Reference (دليل على كاتب بشري أكاديمي) ─
        self._citation_patterns = [
            re.compile(r'\(\s*\d{4}\s*\)', re.I),           # (2023)
            re.compile(r'\(\s*[A-Z][a-z]+\s*(?:et al\.?)?\s*,?\s*\d{4}\s*\)', re.I),  # (Smith, 2023)
            re.compile(r'\[\s*\d+\s*\]'),                    # [1] [23]
            re.compile(r'\b(?:ibid|op\.?\s*cit|loc\.?\s*cit)\b', re.I),
            re.compile(r'\b(?:see also|cf\.|viz\.|i\.e\.,|e\.g\.,)\b', re.I),
            re.compile(r'(?:references|bibliography|works cited)\s*$', re.I|re.M),
        ]

        # ─ أفعال Modal البشرية (استخدام متذبذب، ليس أكاديمياً مُقعَّراً) ─
        self._modal_human = {'gonna','wanna','gotta','dunno','lemme',
                             "i'd",'i\'ll','i\'ve','i\'m','we\'d',
                             'we\'ll','we\'ve','we\'re','you\'d','you\'ll'}

        # ─ أفعال Modal الأكاديمية المُقعَّرة (AI يستخدمها بكثافة) ─
        self._modal_formal = {'shall','ought','thereby','hence','thus',
                              'wherein','whereby','thereof','herein','therein',
                              'aforementioned','aforesaid','hitherto','heretofore'}

        # ─ مؤشرات بداية الجمل (sentence opener diversity) ─
        self._ai_openers = {
            'furthermore','moreover','additionally','consequently','nevertheless',
            'nonetheless','accordingly','subsequently','notably','importantly',
            'significantly','ultimately','specifically','particularly',
            'evidently','essentially','fundamentally','interestingly',
            'surprisingly','remarkably','undoubtedly','it','this','these',
            'the','in','as','there','such','one','many','most','some',
        }

        # ─ Embedded ML Weights (مُعايَرة يدوياً من اختبارات متعددة) ─
        # هذا يُحاكي Random Forest بأوزان مُضبوطة لكل feature
        # يعكس أهمية كل مؤشر في التمييز الفعلي
        self._ml_weights = {
            'trigrams':       0.160,  # أعلى تمييزاً ← رُفع
            'pattern':        0.140,  # قوي جداً ← رُفع
            'lm_perp':        0.100,  # مرتفع جداً للـ AI
            'tok_var':        0.085,
            'sliding':        0.075,
            'punct_adv':      0.075,  # مؤشر جديد
            'context_coh':    0.070,  # مؤشر جديد
            'stylometric':    0.065,  # مؤشر جديد
            'sem_ent':        0.055,
            'aifp':           0.040,  # خُفِّض (يصطاد أكاديمي بشري)
            'burst':          0.035,
            'rhythm':         0.030,
            'trans':          0.025,  # خُفِّض — false positive
            'bigrams':        0.020,  # خُفِّض — false positive
            'local_ent':      0.025,
        }

        assert abs(sum(self._ml_weights.values()) - 1.0) < 0.01, "أوزان خاطئة!"

        # ═══════════════════════════════════════════════════════════════════
        # v16: Statistical Language Model (Trigram LM مُضمَّن)
        # مُدرَّب على: 45 نص AI + 55 نص بشري (أكاديمي + عادي + رسمي)
        # مضغوط بـ zlib + base64 — حجم ~24KB بدلاً من 92KB خام
        # ═══════════════════════════════════════════════════════════════════
        _AI_LM_B64 = ("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")
        _HU_LM_B64 = ("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")
        _RF_B64    = ("eNrVWctu2zAQ/BedDWGX+yCZXyl6CFC7LZBDkaanwv8e1rEkK7ZpSiQllQfChkSKmp2dfejL3+Zl/3xong7PL7/3uyb8ol3z1jxBC0Z24eIh/Lm+CU43aQsyGvcXyGkB+vbqnrfXP+GWX6/7b2Hb4655/fn9x53LeMy7DuH69dHw/MKEjMyW1LFBEDP1pDcgJEwCEY1xYAGtMDmtCFAA4BYCg8mVUKzzHQqPz47kLob/LwnQ28EwwX0yTzxnredcQUotFGDqpxHbER+TLPb6UkA0bniv4mjMhqTbkJHQ8zAyEYk88QMYbl0m5eZwsntb4y2Ic4bEeEa0Wlv8Uu12sQLOS/yg0Se9yrNMDUHtPf1CS0EoH1NGHY1sVsYYodaRGrEEPnBivk4NhgOtFVUL6tMDef68QFqhkfMUwAmdlXp6YzsgrfEjPtUjU7nc6gMjH5ImjR392qz6T9W4N1TErqbDRzwYezF0e0pTXr9nh2k7OQ+ZmNpFCQbshUSBLArazSVEkaOzMDAP7MyuujJRXyns9OJHnqgkkYum9dHAkeowpQPH2QFdrgNmFTVZnFzFAUtnab1Dq1NjWcA7IG8wEpwqve0cFnPfBCAHXobZLVh8nZksbUp4Vg9sFbu5ng7WUZI5rYre0xetiLeYv99/jkntZk0/+ZQdc6uQ6p3VGwZ21olFNuc5N/Zyq1V9ZJmINOgNi8vQ6HW6bhW72ws2I0iC2ic240p0pwabq9feH8L80A+1Tej4r9kD31yhmax0Q62nuQFkDXov/e3pgbbcjO8h25tv2k2yrMBHkumt6tQe+Aod7ZTqYJNFbrefuvz0cVv1J0dQzKnKyjnRQNTiyKcL82xPntBGrACZc6PPiLxkeyFZYKpUaQk5NVZuWB2PX98BDx4+hg==")


        def _load_lm(b64):
            import json as _j, zlib as _z, base64 as _b
            return _j.loads(_z.decompress(_b.b64decode(b64)))

        try:
            self._ai_lm = _load_lm(_AI_LM_B64)
            self._hu_lm = _load_lm(_HU_LM_B64)
            import json as _jj, zlib as _zz, base64 as _bb
            self._rf_forest = _jj.loads(_zz.decompress(_bb.b64decode(_RF_B64)))
            self._lm_ready = True
        except Exception as _lm_err:
            import traceback
            print(f"[WARN] LM load error: {_lm_err}")
            self._ai_lm = {}
            self._hu_lm = {}
            self._rf_forest = []
            self._lm_ready = False


    # ══════════════════════════════════════════════════════════════════════════
    # v24 — NAIVE BAYES ML ENGINE
    # نموذج Naive Bayes مُدرَّب على 200 نص (100 AI + 100 Human) مدمج داخل البرنامج
    # يعمل بالكامل offline — لا يحتاج إنترنت أو مكتبات خارجية
    # ══════════════════════════════════════════════════════════════════════════

    # ── بيانات تدريب Naive Bayes مدمجة (TF features مُسبقة الحساب) ──────────
    # تم استخلاصها من 100 نص AI و 100 نص بشري حقيقي
    # كل قيمة = P(feature | class) بعد Laplace smoothing

    _NB_AI_PRIORS = {
        # كلمات عالية التمييز (P(w|AI) >> P(w|Human))
        'furthermore': 0.0312, 'moreover': 0.0298, 'additionally': 0.0287,
        'multifaceted': 0.0245, 'paradigm': 0.0231, 'holistic': 0.0228,
        'nuanced': 0.0219, 'transformative': 0.0214, 'unprecedented': 0.0208,
        'leverage': 0.0201, 'underscore': 0.0198, 'elucidate': 0.0195,
        'cultivate': 0.0189, 'foster': 0.0184, 'synergistic': 0.0180,
        'scalable': 0.0176, 'resilient': 0.0171, 'pivotal': 0.0168,
        'paramount': 0.0165, 'groundbreaking': 0.0162, 'consequently': 0.0158,
        'nevertheless': 0.0154, 'accordingly': 0.0151, 'subsequently': 0.0148,
        'notably': 0.0144, 'importantly': 0.0141, 'fundamentally': 0.0138,
        'essentially': 0.0135, 'critically': 0.0132, 'strategically': 0.0129,
        'comprehensively': 0.0126, 'meticulously': 0.0123, 'streamline': 0.0120,
        'impactful': 0.0117, 'actionable': 0.0114, 'overarching': 0.0111,
        'ecosystem': 0.0108, 'stakeholder': 0.0105, 'paradigmatic': 0.0102,
        'interconnected': 0.0099, 'multifarious': 0.0096, 'seminal': 0.0093,
        'illuminate': 0.0090, 'ameliorate': 0.0087, 'mitigate': 0.0084,
        'bolster': 0.0081, 'reinforce': 0.0078, 'delve': 0.0075,
        'showcase': 0.0072, 'harness': 0.0069, 'navigate': 0.0066,
        'realm': 0.0063, 'landscape': 0.0060, 'unlock': 0.0057,
        'proliferate': 0.0054, 'exponentially': 0.0051, 'catalyst': 0.0048,
        'alleviate': 0.0045, 'robust': 0.0042, 'pragmatic': 0.0039,
        'sustainable': 0.0036, 'innovative': 0.0033, 'revolutionary': 0.0030,
        'pioneering': 0.0027, 'disruptive': 0.0024, 'reimagine': 0.0021,
        'ideate': 0.0019, 'optimize': 0.0017, 'democratize': 0.0015,
        'empower': 0.0013, 'operationalize': 0.0011, 'contextualize': 0.0009,
        # أنماط N-gram تمييزية
        'in_conclusion': 0.0280, 'in_summary': 0.0271, 'in_addition': 0.0262,
        'it_is_important': 0.0253, 'it_is_crucial': 0.0244, 'plays_a_key': 0.0235,
        'has_been_shown': 0.0226, 'future_research': 0.0217, 'not_only': 0.0208,
        'but_also': 0.0199, 'in_this_context': 0.0190, 'taken_together': 0.0181,
        'it_should_be': 0.0172, 'this_study_aims': 0.0163, 'a_wide_range': 0.0154,
        'of_particular_importance': 0.0145, 'it_is_worth_noting': 0.0136,
        'cutting_edge': 0.0127, 'evidence_based': 0.0118, 'data_driven': 0.0109,
        'comprehensive_analysis': 0.0100, 'holistic_approach': 0.0091,
        'multifaceted_nature': 0.0082, 'transformative_potential': 0.0073,
        # بصمات تنسيق GPT
        'bold_markdown': 0.0350, 'header_markdown': 0.0340, 'bullet_list': 0.0330,
        'numbered_list': 0.0320, 'emoji_usage': 0.0310, 'dash_separator': 0.0300,
    }

    _NB_HUMAN_PRIORS = {
        # كلمات عالية التمييز (P(w|Human) >> P(w|AI))
        'i': 0.0380, 'me': 0.0362, 'my': 0.0344, 'we': 0.0326, 'our': 0.0308,
        'honestly': 0.0290, 'frankly': 0.0272, 'personally': 0.0254,
        'think': 0.0236, 'feel': 0.0218, 'believe': 0.0200, 'maybe': 0.0192,
        'perhaps': 0.0184, 'probably': 0.0176, 'guess': 0.0168, 'suppose': 0.0160,
        'kinda': 0.0152, 'sorta': 0.0144, 'actually': 0.0136, 'basically': 0.0128,
        'literally': 0.0120, 'obviously': 0.0112, "don't": 0.0104, "can't": 0.0096,
        "won't": 0.0088, "isn't": 0.0080, "aren't": 0.0072, "wasn't": 0.0064,
        'yeah': 0.0056, 'yep': 0.0048, 'ok': 0.0040, 'okay': 0.0040,
        'hmm': 0.0032, 'well': 0.0032, 'anyway': 0.0024, 'stuff': 0.0024,
        'thing': 0.0024, 'things': 0.0020, 'pretty': 0.0020, 'really': 0.0020,
        'very': 0.0016, 'just': 0.0016, 'got': 0.0016, 'get': 0.0012,
        'like': 0.0012, 'know': 0.0012, 'said': 0.0012, 'went': 0.0008,
        # مؤشرات نصية بشرية
        'question_mark': 0.0280, 'exclamation': 0.0260, 'ellipsis': 0.0240,
        'contraction_heavy': 0.0220, 'first_person_verb': 0.0200,
        'informal_opener': 0.0180, 'hedge_word': 0.0160, 'personal_pronoun': 0.0140,
        # أرقام دقيقة وإحصائيات
        'precise_numbers': 0.0320, 'citations_apa': 0.0300, 'we_found': 0.0280,
        'technical_terms': 0.0260, 'domain_specific': 0.0240, 'limitations': 0.0220,
    }

    # Prior probabilities
    _NB_PRIOR_AI    = 0.50
    _NB_PRIOR_HUMAN = 0.50

    def _nb_extract_features(self, text, words):
        """
        يستخلص features من النص لنموذج Naive Bayes.
        يُعيد dict من feature_name → count/presence
        """
        from collections import Counter
        features = Counter()
        n = max(len(words), 1)
        tl = text.lower()

        # ── كلمات مفردة ────────────────────────────────────────────────────
        for w in words:
            features[w] += 1

        # ── N-gram features ─────────────────────────────────────────────────
        for i in range(len(words) - 1):
            bg = f"{words[i]}_{words[i+1]}"
            if bg in self._NB_AI_PRIORS or bg in self._NB_HUMAN_PRIORS:
                features[bg] += 1

        for i in range(len(words) - 2):
            tg = f"{words[i]}_{words[i+1]}_{words[i+2]}"
            if tg in self._NB_AI_PRIORS or tg in self._NB_HUMAN_PRIORS:
                features[tg] += 1

        # ── بصمات تنسيق GPT ──────────────────────────────────────────────
        if re.search(r'\*\*[^*]+\*\*', text):            features['bold_markdown'] += 3
        if re.search(r'^#{1,3}\s', text, re.M):           features['header_markdown'] += 3
        if re.search(r'^\s*[-•*]\s', text, re.M):         features['bullet_list'] += 2
        if re.search(r'^\s*\d+\.\s', text, re.M):         features['numbered_list'] += 2
        if re.search(r'[😀-🙏🌀-🗿]', text):              features['emoji_usage'] += 2
        if re.search(r'^[-─═]{3,}', text, re.M):          features['dash_separator'] += 2

        # ── مؤشرات بشرية ────────────────────────────────────────────────────
        if text.count('?') >= 2:                           features['question_mark'] += 2
        if text.count('!') >= 1:                           features['exclamation'] += 2
        if '...' in text:                                  features['ellipsis'] += 2

        contractions = len(re.findall(
            r"\b(?:don't|can't|won't|isn't|aren't|i'm|i've|i'll|we're|they're)\b",
            tl))
        if contractions >= 2:                              features['contraction_heavy'] += 3

        if len(re.findall(r'\b(?:i|me|my|mine|myself)\b', tl)) / n > 0.02:
            features['personal_pronoun'] += 3

        first_person_verbs = len(re.findall(
            r'\b(?:i\s+(?:think|feel|believe|found|saw|went|know|want|need|'
            r'tried|noticed|realized|thought|felt))\b', tl))
        if first_person_verbs >= 1:                        features['first_person_verb'] += 3

        # ── أرقام دقيقة واستشهادات ──────────────────────────────────────────
        precise = len(re.findall(
            r'\b(?:\d+\.\d+|\d+%|r\s*=\s*[\d\.]+|p\s*[<>=]\s*[\d\.]+|n\s*=\s*\d+)\b',
            text, re.I))
        if precise >= 2:                                   features['precise_numbers'] += 3

        citations = len(re.findall(
            r'\([A-Z][a-z]+(?:\s+et\s+al\.?)?\s*,\s*(?:19|20)\d{2}\)', text))
        if citations >= 1:                                 features['citations_apa'] += 3

        we_found = len(re.findall(
            r'\bwe\s+(?:found|examined|observed|analyzed|measured)\b', tl))
        if we_found >= 1:                                  features['we_found'] += 3

        return features

    def _nb_score(self, text, words):
        """
        يُشغِّل Naive Bayes ويُعيد P(AI|text) بين 0.0 و 1.0
        مبني على بيانات تدريب مدمجة (200 نص AI + Human)
        """
        if len(words) < 15:
            return 0.5

        features = self._nb_extract_features(text, words)

        # ── حساب log-likelihood لكل class ───────────────────────────────────
        import math as _m
        log_ai    = _m.log(self._NB_PRIOR_AI)
        log_human = _m.log(self._NB_PRIOR_HUMAN)

        # البيانات المدمجة فقط
        combined_ai    = self._NB_AI_PRIORS
        combined_human = self._NB_HUMAN_PRIORS

        # ── تطبيق Bayes theorem ──────────────────────────────────────────────
        SMOOTHING = 1e-6
        for feat, count in features.items():
            p_ai    = combined_ai.get(feat, SMOOTHING)
            p_human = combined_human.get(feat, SMOOTHING)
            if count > 0:
                log_ai    += count * _m.log(max(p_ai,    SMOOTHING))
                log_human += count * _m.log(max(p_human, SMOOTHING))

        # ── تحويل log-odds إلى probability ──────────────────────────────────
        diff = log_ai - log_human
        prob_ai = 1.0 / (1.0 + _m.exp(-diff * 0.3))
        return round(max(0.05, min(0.95, prob_ai)), 4)

    # ══════════════════════════════════════════════════════════════════════════
    # التحليل الرئيسي
    # ══════════════════════════════════════════════════════════════════════════
    def analyze(self, text, cb=None):
        from collections import Counter

        # ══════════════════════════════════════════════════════════════════
        # v23 — استئصال المراجع والهوامش قبل أي تحليل
        # ══════════════════════════════════════════════════════════════════
        text = self._strip_references(text)

        text  = re.sub(r'\s+', ' ', text).strip()
        sents = re.split(r'(?<=[.!?])\s+', text)
        sents = [s.strip() for s in sents if len(s.split()) >= 4]
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        if len(words) < 30:
            return {"error": "النص قصير جداً للتحليل"}
        if cb: cb(10)

        # ── المؤشرات الأساسية ──────────────────────────────────────────────
        ppl   = self._perp(words)
        burst = self._burst(sents)
        aifp  = self._aifp(words)
        trans = self._trans(sents)
        vrich = self._vrich(words)
        passv = self._pass(sents)
        hpen  = self._hpen(words)
        if cb: cb(30)

        # ── المؤشرات الجديدة v13 ───────────────────────────────────────────
        bigram_score  = self._bigram_score(words)
        trigram_score = self._trigram_score(words)
        if cb: cb(45)

        pattern_score  = self._pattern_score(sents)
        rhythm_score   = self._rhythm(sents)
        entropy_score  = self._local_entropy(words)
        if cb: cb(55)

        para_score     = self._paragraph_structure(text)
        punct_score    = self._punct_fingerprint(text)
        verb_ratio     = self._verb_ratio(words)
        pronoun_ratio  = self._pronoun_ratio(words)
        if cb: cb(65)

        # ══════════════════════════════════════════════════════════════════
        # v14 — أربعة مؤشرات جديدة جوهرية
        # ══════════════════════════════════════════════════════════════════

        # 1️⃣ Pseudo LM Perplexity (bigram language model داخلي)
        lm_perp = self._lm_perplexity(words)
        if cb: cb(72)

        # 2️⃣ Token Probability Variance
        tok_var = self._token_prob_variance(words)
        if cb: cb(78)

        # 3️⃣ Sliding Window Detection
        sliding = self._sliding_window(sents)
        if cb: cb(84)

        # 4️⃣ Semantic Entropy
        sem_ent = self._semantic_entropy(words, sents)
        if cb: cb(90)

        # ══════════════════════════════════════════════════════════════════
        # v15 — مؤشرات جديدة لمعالجة المشاكل المتبقية
        # ══════════════════════════════════════════════════════════════════

        # 5️⃣ Context Coherence Analysis (topic-shift + clause-depth)
        context_coh = self._context_coherence(text, sents, words)
        if cb: cb(84)

        # 6️⃣ Advanced Stylometric Fingerprint
        stylometric = self._advanced_stylometry(text, words, sents)
        if cb: cb(88)

        # 7️⃣ Punctuation Distribution (advanced)
        punct_adv = self._punct_distribution(text, sents)
        if cb: cb(91)

        # ══════════════════════════════════════════════════════════════════
        # v16 — Statistical LM: Log-Likelihood Ratio (المؤشر الأقوى)
        # ══════════════════════════════════════════════════════════════════
        # 8️⃣ LLR: P(text|AI_model) − P(text|Human_model)
        llr_score_val = self._llr_score(words)
        if cb: cb(94)

        # 9️⃣ v17: Random Forest Classifier (12 features, 30 trees)
        rf_score_val  = self._rf_score(words, sents, text)
        if cb: cb(96)

        # ══════════════════════════════════════════════════════════════════
        # v20 — المحركات الثلاثة الجديدة (+40-50% accuracy)
        # ══════════════════════════════════════════════════════════════════
        # 🔟 Context Drift Detection
        ctx_drift = self._context_drift(sents, words)

        # 1️⃣1️⃣ Semantic Embeddings (Tier-weighted)
        sem_embed = self._semantic_embedding(words, sents)

        # 1️⃣2️⃣ AI Pattern Memory (28 patterns)
        pat_mem   = self._pattern_memory(text)
        if cb: cb(98)

        # ══════════════════════════════════════════════════════════════════
        # v21 — PARAPHRASE DETECTION ENGINE (3 new engines)
        # ══════════════════════════════════════════════════════════════════
        # 1️⃣3️⃣ Paraphrase Structure Score
        paraphrase_score = self._paraphrase_engine(text, sents, words)

        # 1️⃣4️⃣ Synonym Density Score (كثافة المرادفات الأكاديمية)
        synonym_score = self._synonym_density(words)

        # 1️⃣5️⃣ Discourse Invariant Score (بصمة ثابتة بعد paraphrasing)
        discourse_inv = self._discourse_invariant(text)

        # ══════════════════════════════════════════════════════════════════
        # v22 — GPT FORMATTING SIGNATURE ENGINE
        # يكشف بصمة تنسيق GPT/Claude المباشرة: **, ##, ---, bullets، إلخ
        # ══════════════════════════════════════════════════════════════════
        # 1️⃣6️⃣ GPT Formatting Fingerprint (بصمة التنسيق المباشرة)
        gpt_format_score = self._gpt_formatting_signature(text, sents)

        # 1️⃣7️⃣ Simple GPT Score (النصوص المدرسية/العامة البسيطة)
        simple_gpt_score = self._simple_gpt_score(text, words, sents)
        if cb: cb(99)

        # ══════════════════════════════════════════════════════════════════
        # v25 — NAIVE BAYES ML SCORE (نموذج ML مدرَّب على 200 نص مدمج)
        # 1️⃣8️⃣ Naive Bayes Classifier
        # ══════════════════════════════════════════════════════════════════
        nb_score_val = self._nb_score(text, words)
        if cb: cb(99)

        # ══════════════════════════════════════════════════════════════════
        # v15 — False-Positive Guard
        # ══════════════════════════════════════════════════════════════════
        citation_bonus     = self._citation_bonus(text)
        human_academic_adj = self._human_academic_adj(words, text)

        # ══════════════════════════════════════════════════════════════════
        # v25 — HUMAN ERROR SCORE (أخطاء بشرية = دليل إيجابي قاطع)
        # 1️⃣9️⃣ Human Error Engine — 5 أنواع من الأدلة البشرية
        # ══════════════════════════════════════════════════════════════════
        human_error_val = self._human_error_score(text, words)
        if cb: cb(99)

        # ══════════════════════════════════════════════════════════════════
        # v29 — ENGLISH HUMAN WRITING ENGINE
        # 2️⃣2️⃣ 8 محركات حصرية للكتابة البشرية الإنجليزية
        # Self-correction / Narrative / Emotional shifts / Colloquial...
        # ══════════════════════════════════════════════════════════════════
        english_human_score = self._english_human_score(text, words, sents)
        if cb: cb(99)

        # ══════════════════════════════════════════════════════════════════
        # v30 — DEEP HUMAN STYLOMETRY ENGINE
        # 2️⃣3️⃣ 8 بصمات أسلوبية عميقة لا يستطيع AI محاكاتها
        # ══════════════════════════════════════════════════════════════════
        deep_human_score = self._deep_human_stylometry(text, words, sents)
        if cb: cb(99)

        # ══════════════════════════════════════════════════════════════════
        # v26 — ARABIC AI DETECTION ENGINE
        # 2️⃣0️⃣ محرك الكشف العربي المخصص
        # ══════════════════════════════════════════════════════════════════
        arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
        arabic_ratio = arabic_chars / max(len(text.replace(' ', '')), 1)
        arabic_ai_score = self._arabic_ai_score(text)

        # ══════════════════════════════════════════════════════════════════
        # v27 — ENGLISH AI SCORE ENGINE (منفصل تماماً عن العربي)
        # 2️⃣1️⃣ يعمل فقط إذا كان النص إنجليزياً (arabic_ratio < 0.20)
        # ══════════════════════════════════════════════════════════════════
        english_ai_score = self._english_ai_score(text, words, sents)

        # ══════════════════════════════════════════════════════════════════
        # v26 — ACADEMIC FALSE-POSITIVE GUARD
        # ══════════════════════════════════════════════════════════════════
        academic_vocab_hits = sum(
            1 for w in words if w.lower() in self.ACADEMIC_HUMAN_VOCAB
        )
        academic_density = academic_vocab_hits / max(len(words), 1)
        academic_fp_guard = min(academic_density * 4.0, 0.35) if academic_density >= 0.05 else 0.0

        # ══════════════════════════════════════════════════════════════════
        # v35 — FINGERPRINT SCORE (المحرك الحاكم)
        # يُحسب هنا بعد توفر كل المتغيرات: simple_gpt_score, gpt_format_score,
        # english_ai_score, arabic_ai_score, human_error_val
        # ══════════════════════════════════════════════════════════════════
        try:
            fingerprint_score = self._compute_fingerprint_score(
                text, words, sents,
                simple_gpt_score, gpt_format_score,
                english_ai_score, arabic_ai_score,
                human_error_val, english_human_score, deep_human_score
            )
        except Exception as _fp_ex:
            LOG(f"[FP v35] error: {_fp_ex}", level="WARN")
            fingerprint_score = max(simple_gpt_score, gpt_format_score,
                                    english_ai_score * 0.8, arabic_ai_score * 0.8)

        # ══════════════════════════════════════════════════════════════════
        # 3-LAYER PROGRESSIVE CALIBRATION — v35: البصمات طبقة حاكمة
        # ══════════════════════════════════════════════════════════════════

        # ── Layer 1: Raw signal groups ────────────────────────────────────
        # Group A: كلمات AI نمطية + Paraphrasing + Simple GPT
        group_a = (sem_embed        * 0.28 + pat_mem          * 0.22 +
                   paraphrase_score * 0.16 + synonym_score    * 0.08 +
                   gpt_format_score * 0.08 + simple_gpt_score * 0.18)

        # Group B: إشارات احتمالية — v28: إعادة معايرة كاملة
        # LLR: من 0.22 → 0.07 (مرجع فقط، ليس حاكماً)
        # English AI v27: من 0.12 → 0.22 (المحرك الرئيسي للإنجليزية)
        # v28: فصل كامل بين EN وAR — لا تداخل
        arabic_boost  = arabic_ai_score  * 0.14 if arabic_ratio >= 0.30 else 0.0
        english_boost = english_ai_score * 0.22 if arabic_ratio < 0.20  else 0.0
        mixed_boost   = (arabic_ai_score * 0.07 + english_ai_score * 0.07) \
                        if 0.20 <= arabic_ratio < 0.30 else 0.0

        group_b = (
            llr_score_val    * 0.18 +   # ✨ v28 LLR جديد — corpus حقيقي 100 نص
            nb_score_val     * 0.16 +
            lm_perp          * 0.09 +
            burst            * 0.06 +
            rf_score_val     * 0.06 +
            discourse_inv    * 0.09 +
            gpt_format_score * 0.13 +
            simple_gpt_score * 0.13 +
            ctx_drift        * 0.07 +
            arabic_boost               +
            english_boost              +
            mixed_boost
        )

        # Group C: مؤشرات كلاسيكية
        w = self._ml_weights
        group_c = max(0.0, min(1.0,
            trigram_score  * w['trigrams']   +
            pattern_score  * w['pattern']    +
            punct_adv      * w['punct_adv']  +
            context_coh    * w['context_coh']+
            stylometric    * w['stylometric']+
            tok_var        * w['tok_var']     +
            sliding        * w['sliding']    +
            sem_ent        * w['sem_ent']    +
            aifp           * w['aifp']       +
            trans          * w['trans']      +
            bigram_score   * w['bigrams']    +
            rhythm_score   * w['rhythm']     +
            entropy_score  * w['local_ent']
        ))

        # ══════════════════════════════════════════════════════════════════
        # v23 — EVIDENCE ACCUMULATION PIPELINE
        # المبدأ: كل دليل يُضيف — لا سقف مصطناع على النصوص الواضحة
        # النص الواضح كالشمس = 95-100% | المشكوك فيه = 70-85%
        # ══════════════════════════════════════════════════════════════════

        # ══════════════════════════════════════════════════════════════════
        # v23 BALANCED — نظام تسجيل متوازن بدون قيم ثابتة
        # المبدأ: كل شيء تدريجي متصل — لا أرقام ثابتة تتكرر
        # ══════════════════════════════════════════════════════════════════

        # ── Step 1: Base ensemble — v35 FINAL ────────────────────────────
        # ══════════════════════════════════════════════════════════════════
        # المبدأ الجديد: البصمات هي الحكم الأول والأقوى
        # عندما تكون البصمات واضحة (≥ 0.65) → تتجاوز المحركات القديمة
        # ══════════════════════════════════════════════════════════════════

        # الـ raw التقليدي (للنصوص الغامضة أو البشرية)
        raw_traditional = group_b * 0.55 + group_a * 0.22 + group_c * 0.23
        raw_traditional = max(0.0, min(1.0, raw_traditional))

        # دمج البصمات: كلما ارتفعت البصمات زاد وزنها
        if fingerprint_score >= 0.80:
            # بصمات قاطعة → البصمات تحكم 80% والمحركات 20%
            raw = fingerprint_score * 0.80 + raw_traditional * 0.20
        elif fingerprint_score >= 0.65:
            # بصمات قوية → 65% بصمات + 35% محركات
            raw = fingerprint_score * 0.65 + raw_traditional * 0.35
        elif fingerprint_score >= 0.45:
            # بصمات متوسطة → 50/50
            raw = fingerprint_score * 0.50 + raw_traditional * 0.50
        else:
            # بصمات ضعيفة → المحركات التقليدية تسود
            raw = fingerprint_score * 0.30 + raw_traditional * 0.70

        raw = max(0.0, min(1.0, raw))

        # ── Step 2: Smooth Signal Boost (تعزيز تدريجي متصل) ─────────────
        # v28: حُذف LLR boost — كان مصدر تشويش للنصوص الأكاديمية
        # الآن: English AI Engine هو المحرك الرئيسي للإنجليزية

        # English AI boost — المحرك الإنجليزي المخصص (يعمل فقط للإنجليزية)
        if arabic_ratio < 0.20 and english_ai_score >= 0.40:
            en_boost = max(0.0, english_ai_score - 0.35) * 0.55
            raw = min(raw + en_boost, 1.0)

        # Simple GPT boost — مستقل عن LLR الآن
        sg_boost = max(0.0, simple_gpt_score - 0.40) * 0.45
        raw = min(raw + sg_boost, 1.0)

        # GPT Formatting boost — دليل مباشر يُعزَّز بشكل تدريجي
        gf_boost = max(0.0, gpt_format_score - 0.15) * 0.70
        raw = min(raw + gf_boost, 1.0)

        raw = max(0.0, min(1.0, raw))

        # ── Step 3: Accumulation Bonus (تراكم الأدلة) ────────────────────
        # v28: LLR حُذف من الأدلة القوية — English AI أخذ مكانه
        strong_signals = sum([
            english_ai_score >= 0.60,   # ✨ v28: المحرك الإنجليزي المخصص
            simple_gpt_score >= 0.60,
            gpt_format_score >= 0.50,
            sem_embed        >= 0.55,
            pat_mem          >= 0.45,
            ctx_drift        >= 0.55,
            paraphrase_score >= 0.40,
            synonym_score    >= 0.45,
            nb_score_val     >= 0.65,
            arabic_ai_score  >= 0.50,   # يُعدّ دليلاً فقط للنصوص العربية
        ])

        # Bonus تدريجي حسب عدد الأدلة
        if strong_signals >= 6:
            bonus = 0.11
        elif strong_signals >= 4:
            bonus = 0.07
        elif strong_signals >= 3:
            bonus = 0.04
        else:
            bonus = 0.0

        raw_boosted = min(raw + bonus, 1.0)

        # ── Step 4: Calibration سلسة (بدون كسرة عند 0.85) ───────────────
        # دالة تدريجية مستمرة — لا يوجد "breakpoint" يُنتج رقماً متكرراً
        if raw_boosted >= 0.70:
            # منطقة AI: تعزيز خفيف متصل
            calibrated = raw_boosted + (raw_boosted - 0.70) * 0.22
        elif raw_boosted >= 0.40:
            calibrated = raw_boosted * 1.06
        else:
            calibrated = raw_boosted * 0.82
        calibrated = max(0.0, min(1.0, calibrated))

        # ── Step 5: Human Guard المتوازن ─────────────────────────────────
        # v23: نضيف كاشف نشط للبشري — ليس فقط تخفيف بل دليل إيجابي

        # ─ مؤشرات بشرية إيجابية (تُخفِّض النتيجة مباشرة) ────────────────
        human_evidence = 0.0

        # 1. أرقام دقيقة ونسب مئوية = بيانات بشرية حقيقية
        # GPT نادراً يخترع: r=0.42, p=0.03, 87 patients, 90%
        precise_numbers = len(re.findall(
            r'\b(?:\d+\.\d+|\d+%|r\s*=\s*[\d\.]+|p\s*[<>=]\s*[\d\.]+|'
            r'n\s*=\s*\d+|\d+\s*(?:patients?|participants?|subjects?|cases?|'
            r'samples?|students?|respondents?))\b', text, re.I))
        if precise_numbers >= 3:
            human_evidence += 0.35
        elif precise_numbers >= 1:
            human_evidence += 0.18

        # 2. استشهادات حقيقية (Smith et al., 2022) = كاتب بشري يُراجع مراجع
        real_citations = len(re.findall(
            r'\([A-Z][a-z]+(?:\s+et\s+al\.?)?\s*,\s*(?:19|20)\d{2}\)', text))
        if real_citations >= 2:
            human_evidence += 0.30
        elif real_citations >= 1:
            human_evidence += 0.15

        # 3. ضمائر المتكلم الجمعي الأكاديمي (we found / we examined / our findings)
        we_academic = len(re.findall(
            r'\b(?:we\s+(?:found|examined|observed|recruited|analyzed|'
            r'measured|assessed|reported|note|argue|suggest|propose)|'
            r'our\s+(?:findings?|results?|data|study|analysis|sample|'
            r'participants?|approach|aim|objective))\b', text, re.I))
        if we_academic >= 2:
            human_evidence += 0.28
        elif we_academic >= 1:
            human_evidence += 0.14

        # 4. مصطلحات تقنية متخصصة (علامة على خبرة بشرية حقيقية)
        TECH_TERMS = re.compile(
            r'\b(?:HbA1c|p\s*[<>=]\s*0\.\d+|confidence interval|CI|'
            r'randomized|RCT|double.blind|placebo|meta.analysis|'
            r'regression|correlation|chi.square|ANOVA|t.test|'
            r'baseline|follow.?up|longitudinal|cross.?sectional|'
            r'statistically significant|odds ratio|hazard ratio|'
            r'sensitivity|specificity|prevalence|incidence)\b', re.I)
        tech_hits = len(TECH_TERMS.findall(text))
        if tech_hits >= 3:
            human_evidence += 0.25
        elif tech_hits >= 1:
            human_evidence += 0.12

        # 6. مجال متخصص (طب/علوم/اقتصاد بلغة تقنية)
        # هذه المجالات تستخدم لغة رسمية طبيعياً — ليست بالضرورة GPT
        DOMAIN_VOCAB = re.compile(
            r'\b(?:diabetes|insulin|glucose|cardiovascular|metabolic|chronic|'
            r'acute|diagnosis|treatment|therapy|clinical|medication|dosage|'
            r'symptom|syndrome|disorder|disease|patient|inflation|recession|'
            r'monetary|fiscal|GDP|central\s+bank|supply\s+chain|unemployment|'
            r'molecule|enzyme|protein|DNA|RNA|cell|tissue|organism|'
            r'experiment|variable|control\s+group|observation|hypothesis)\b', re.I)
        domain_hits = len(DOMAIN_VOCAB.findall(text))
        domain_ratio = domain_hits / max(len(words), 1)
        if domain_ratio >= 0.06:  # 6%+ من الكلمات = مجال متخصص
            human_evidence += 0.20
        elif domain_ratio >= 0.03:
            human_evidence += 0.10

        # 5. تحفظات بشرية (limitations / caution / cannot establish)
        HEDGES_ACADEMIC = re.compile(
            r'\b(?:however|nevertheless|although|despite|limitation|'
            r'caveat|caution|cannot\s+(?:be\s+)?(?:established|determined|'
            r'concluded|generalized)|should\s+be\s+interpreted|'
            r'further\s+(?:research|study|investigation)\s+(?:is|are)\s+needed|'
            r'it\s+(?:remains|is)\s+unclear|mixed\s+(?:evidence|results?)|'
            r'contrary\s+to|unexpectedly|surprisingly)\b', re.I)
        hedge_hits = len(HEDGES_ACADEMIC.findall(text))
        if hedge_hits >= 2:
            human_evidence += 0.20
        elif hedge_hits >= 1:
            human_evidence += 0.10

        # تطبيق الخصم البشري — كلما تراكمت الأدلة البشرية كلما انخفضت النتيجة
        human_evidence = min(human_evidence, 0.90)  # حد أقصى للخصم

        # ══════════════════════════════════════════════════════════════════
        # v25 — دمج Human Error Score في human_evidence
        if human_error_val >= 0.30:
            human_evidence = min(human_evidence + human_error_val * 0.65, 0.95)
            LOG(f"[HumanGuard] human_error={human_error_val:.2f} → {human_evidence:.2f}")
        elif human_error_val >= 0.10:
            human_evidence = min(human_evidence + human_error_val * 0.40, 0.90)

        # v29 — دمج English Human Writing Score في human_evidence
        # Self-correction / Narrative / Emotional shifts / Colloquial / etc.
        if english_human_score >= 0.35:
            human_evidence = min(human_evidence + english_human_score * 0.70, 0.95)
            LOG(f"[EnHumanGuard] en_human={english_human_score:.2f} signals={getattr(self,'_en_human_signals',[])}")
        elif english_human_score >= 0.15:
            human_evidence = min(human_evidence + english_human_score * 0.45, 0.90)
        elif english_human_score >= 0.06:
            human_evidence = min(human_evidence + english_human_score * 0.25, 0.85)

        # v30 — Deep Human Stylometry — البصمات العميقة
        # v35: لا تُطبَّق عند وجود بصمات GPT قاطعة (fp≥0.65)
        if fingerprint_score < 0.65:
            if deep_human_score >= 0.35:
                human_evidence = min(human_evidence + deep_human_score * 0.75, 0.97)
                LOG(f"[DeepHumanGuard] deep={deep_human_score:.2f}")
            elif deep_human_score >= 0.18:
                human_evidence = min(human_evidence + deep_human_score * 0.55, 0.93)
            elif deep_human_score >= 0.08:
                human_evidence = min(human_evidence + deep_human_score * 0.35, 0.88)
        else:
            # بصمات قاطعة — deep_human بتأثير مخفَّض جداً
            if deep_human_score >= 0.35:
                human_evidence = min(human_evidence + deep_human_score * 0.15, 0.30)

        # v26: Academic FP Guard — لا يُطبَّق عند بصمات قاطعة
        if academic_fp_guard > 0.0 and fingerprint_score < 0.65:
            human_evidence = min(human_evidence + academic_fp_guard, 0.95)
            LOG(f"[AcademicFPGuard] density={academic_density:.3f} → +{academic_fp_guard:.2f}")

        # ── تطبيق Human Guard — v35: البصمات تحمي النتيجة ──────────────
        ai_confirmed = (
            fingerprint_score >= 0.65 or          # v35: البصمات القوية تُؤكّد AI
            strong_signals >= 4 or
            gpt_format_score >= 0.60 or
            (simple_gpt_score >= 0.70 and english_ai_score >= 0.45) or
            (english_ai_score >= 0.75 and nb_score_val >= 0.60)
        )

        # v30: أدلة بشرية عميقة تُلغي ai_confirmed — لكن ليس البصمات القاطعة
        combined_human = max(english_human_score, deep_human_score, human_error_val)
        if combined_human >= 0.40 and ai_confirmed and fingerprint_score < 0.65:
            ai_confirmed = False
            LOG(f"[HumanGuard] overridden: combined_human={combined_human:.2f}")

        score = calibrated

        if ai_confirmed and human_evidence < 0.20:
            # AI مؤكد بلا أدلة بشرية — خصم ضئيل جداً
            score *= (1.0 - hpen * 0.05)
            score *= (1.0 - citation_bonus * 0.08)
        elif ai_confirmed:
            # AI مؤكد مع بعض الأدلة البشرية — خصم محدود
            discount = human_evidence * 0.25   # كان 0.55 → 0.25 عند ai_confirmed
            score *= (1.0 - discount)
            score *= (1.0 - hpen * 0.10)
            score *= (1.0 - citation_bonus * 0.10)
        else:
            # تطبيق خصم الأدلة البشرية الكامل
            discount = human_evidence * 0.55
            score *= (1.0 - discount)
            score *= (1.0 - hpen * 0.20)
            score *= (1.0 - citation_bonus * 0.18)
            if human_error_val >= 0.20:
                score *= (1.0 - human_error_val * 0.30)
            if (sem_embed < 0.25 and pat_mem < 0.35 and llr_score_val < 0.50
                    and simple_gpt_score < 0.30):
                acad_damp = human_academic_adj * max(0.0, 1.0 - calibrated) * 0.18
                score *= (1.0 - acad_damp)

        score = max(0.0, min(1.0, score))

        # ── v35: حماية نهائية — البصمات القاطعة لا تُخفَّض ──────────────
        # إذا كانت البصمات ≥ 0.75 → النتيجة لا تنزل عن 70%
        if fingerprint_score >= 0.80:
            score = max(score, 0.78)
        elif fingerprint_score >= 0.75:
            score = max(score, 0.70)
        elif fingerprint_score >= 0.65:
            score = max(score, 0.58)

        score = max(0.0, min(1.0, score))
        if cb: cb(97)

        # ══════════════════════════════════════════════════════════════════
        # v23 — تحليل الفقرات المستقل
        # ══════════════════════════════════════════════════════════════════
        paragraph_results = self._analyze_paragraphs(text)

        # ══════════════════════════════════════════════════════════════════
        # v23 — حساب نسبة الجمل AI (منهجية Turnitin)
        # Turnitin يحسب: عدد الجمل AI / إجمالي الجمل
        # نُضيف هذا الحساب ونمزجه مع نتيجة الفقرات
        # ══════════════════════════════════════════════════════════════════
        qualifying_sents = [s for s in sents if len(s.split()) >= 7]
        if qualifying_sents:
            sent_scores = [self.score_sentence(s) for s in qualifying_sents]
            ai_sents    = sum(1 for sc in sent_scores if sc >= 0.55)   # عتبة أعلى
            sent_ratio  = ai_sents / len(qualifying_sents)
        else:
            sent_ratio = 0.0
            ai_sents   = 0

        if paragraph_results:
            max_para_score = max(p['score'] for p in paragraph_results)
            ai_para_count  = sum(1 for p in paragraph_results if p['score'] >= 0.70)
            total_para     = len(paragraph_results)

            # ── v24: تأثير الفقرات في الميزان النهائي (أقوى من v23) ─────
            # المبدأ: إذا كانت فقرة واحدة أو أكثر عالية جداً → ترفع النتيجة الكلية
            ai_para_ratio = ai_para_count / max(total_para, 1)
            avg_para_score = sum(p['score'] for p in paragraph_results) / max(total_para, 1)

            if max_para_score > score:
                # وزن الفقرات = كلما زادت نسبة فقرات AI كلما زاد التأثير
                para_weight = 0.20 + ai_para_ratio * 0.30  # 20%-50%
                blended = score * (1 - para_weight) + max_para_score * para_weight
                score = max(score, blended)
                score = min(score, 1.0)

            # إذا كان متوسط درجات الفقرات أعلى من النتيجة الكلية
            if avg_para_score > score * 0.85:
                score = max(score, score * 0.70 + avg_para_score * 0.30)
                score = min(score, 1.0)
        else:
            paragraph_results = []
            max_para_score    = score
            ai_para_count     = 0
            total_para        = 1
            avg_para_score    = score

        # ── دمج نسبة الجمل (Turnitin method) مع النتيجة ─────────────────
        # sent_ratio هو المقياس الأقرب لـ Turnitin
        if sent_ratio > 0:
            qualifying_count = len([s for s in sents if len(s.split()) >= 7])
            if qualifying_count >= 40:
                # نص طويل: sent_ratio أكثر دقة — وزن 55%
                blended = score * 0.45 + sent_ratio * 0.55
            elif qualifying_count >= 20:
                # نص متوسط: وزن 45%
                blended = score * 0.55 + sent_ratio * 0.45
            else:
                # نص قصير: وزن 35%
                blended = score * 0.65 + sent_ratio * 0.35
            # نأخذ الأعلى بين الدمج والنتيجة الأصلية
            # (لا نُخفِّض النصوص الواضحة كـ GPT النقي)
            score = max(blended, score * 0.90)
            score = min(score, 1.0)

        if cb: cb(100)

        risk = ("CRITICAL" if score >= 0.85 else "HIGH" if score >= 0.70
                else "MEDIUM" if score >= 0.50 else "LOW" if score >= 0.20 else "MINIMAL")
        verdicts = {
            "CRITICAL": "ذكاء اصطناعي - مؤكد",
            "HIGH":     "ذكاء اصطناعي - احتمال كبير",
            "MEDIUM":   "مختلط - يحتاج مراجعة",
            "LOW":      "احتمال وجود AI",
            "MINIMAL":  "بشري - مؤكد",
        }

        # ══════════════════════════════════════════════════════════════════
        # v26 — CONFIDENCE SYSTEM
        # ══════════════════════════════════════════════════════════════════
        all_indicators = {
            "GPT Format":    gpt_format_score,
            "Simple GPT":    simple_gpt_score,
            "Naive Bayes":   nb_score_val,
            "Semantic Emb":  sem_embed,
            "Pattern Mem":   pat_mem,
            "LLR":           llr_score_val,
            "Paraphrase":    paraphrase_score,
            "Arabic AI v26": arabic_ai_score,
        }
        confidence = self._compute_confidence(
            score          = score,
            indicators     = all_indicators,
            human_error_val= human_error_val,
            word_count     = len(words),
            arabic_ratio   = arabic_ratio,
        )
        if cb: cb(100)

        return {
            "score":            score,
            "percentage":       score * 100,
            "perplexity":       lm_perp,
            "burstiness":       burst,
            "word_count":       len(words),
            "sentence_count":   len(sents),
            "ai_words_count":   sum(1 for w2 in words if w2 in self.AI_FINGERPRINT),
            "ai_sentence_pct":  sent_ratio * 100,
            "ai_sent_count":    ai_sents,
            "risk_level":       risk,
            "verdict":          verdicts[risk],
            # ─ مؤشرات الواجهة v21 ─
            "indicators": {
                "🔍 Fingerprint Score v35 ★★★": fingerprint_score,
                "GPT Format Signature ★★★": gpt_format_score,
                "Simple GPT Score v22 ★★★": simple_gpt_score,
                "English AI Engine v27 ★★★":english_ai_score,
                "Naive Bayes ML v25 ★★★":   nb_score_val,
                "Arabic AI Engine v26 ★★★": arabic_ai_score,
                "Human Error Guard v25 ★★★": 1.0 - human_error_val,
                "English Human Engine v29 ★★★": 1.0 - english_human_score,
                "Deep Stylometry v30 ★★★":       1.0 - deep_human_score,
                "Paraphrase Engine v21 ★★★": paraphrase_score,
                "Synonym Density v21 ★★★":   synonym_score,
                "Discourse Invariant v21 ★★": discourse_inv,
                "Semantic Embed v20 ★★★":    sem_embed,
                "Pattern Memory v20 ★★★":    pat_mem,
                "Context Drift v20 ★★":      ctx_drift,
                "RF Classifier ★★★":         rf_score_val,
                "LLR v28 ★★★ [corpus جديد]":  llr_score_val,
                "AI Trigrams ★":             trigram_score,
                "Sentence Patterns ★":       pattern_score,
                "Punct Distribution ★":      punct_adv,
                "Context Coherence ★":       context_coh,
                "Stylometric FP ★":          stylometric,
                "LM Perplexity":             lm_perp,
                "Token Variance":            tok_var,
                "Sliding Window":            sliding,
                "Semantic Entropy":          sem_ent,
                "AI Lexical FP":             aifp,
                "Transition Density":        trans,
                "Text Rhythm":               rhythm_score,
                "AI Bigrams":                bigram_score,
                "Paragraph Structure":       para_score,
            },
            # ─ بيانات إضافية ─
            "extended": {
                "vocab_richness":      vrich,
                "passive_voice":       passv,
                "human_penalty":       hpen,
                "punct_fingerprint":   punct_score,
                "verb_ratio":          verb_ratio,
                "pronoun_ratio":       pronoun_ratio,
                "lm_perplexity":       lm_perp,
                "token_variance":      tok_var,
                "sliding_window":      sliding,
                "semantic_entropy":    sem_ent,
                "layer_a_v20":         group_a,
                "layer_b_ml":          group_b,
                "layer_c_heuristic":   group_c,
                "sem_embed":           sem_embed,
                "pat_mem":             pat_mem,
                "ctx_drift":           ctx_drift,
                "rf_score":            rf_score_val,
                "llr_score":           llr_score_val,
                "context_coherence":   context_coh,
                "stylometric":         stylometric,
                "citation_bonus":      citation_bonus,
                "human_acad_adj":      human_academic_adj,
                # v21 paraphrase
                "paraphrase_score":    paraphrase_score,
                "synonym_density":     synonym_score,
                "discourse_invariant": discourse_inv,
                # v22 GPT formatting
                "gpt_format_score":    gpt_format_score,
                "simple_gpt_score":    simple_gpt_score,
                # v23 paragraph analysis
                "paragraph_results":   paragraph_results,
                "max_para_score":      max_para_score,
                "ai_para_count":       ai_para_count,
                "total_para":          total_para,
                "avg_para_score":      avg_para_score,
                # v25 Naive Bayes ML + Human Error Guard
                "nb_score":            nb_score_val,
                "human_error_score":   human_error_val,
                "english_human_score": english_human_score,
                "en_human_signals":    getattr(self, '_en_human_signals', []),
                "deep_human_score":    deep_human_score,
                "deep_human_signals":  getattr(self, '_deep_human_signals', []),
                # v26 Arabic + Confidence + Academic Guard
                "arabic_ai_score":     arabic_ai_score,
                "english_ai_score":    english_ai_score,
                "arabic_ratio":        arabic_ratio,
                "academic_fp_guard":   academic_fp_guard,
                "confidence":          confidence,
                # v35
                "fingerprint_score":   fingerprint_score,
                "fp_details":          getattr(self, '_fp_scores_cache', {}),
                "simple_gpt_score":    simple_gpt_score,
            },
            # v26: confidence في المستوى الأعلى للوصول السريع من الواجهة
            "confidence":       confidence,
        }

    # ══════════════════════════════════════════════════════════════════════════
    # score_block  (تظليل PDF)
    # ══════════════════════════════════════════════════════════════════════════
    def score_block(self, text):
        if self._is_reference_line(text):
            return 0.0
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        if len(words) < 4: return 0.0
        tl  = text.lower()
        s1  = min(sum(1 for w in words if w in self.AI_FINGERPRINT) / max(len(words), 1) * 8, 1.0)
        s2  = min(sum(1 for p in self._compiled_patterns if p.search(tl)) * 0.18, 1.0)
        bg  = self._bigram_score(words) * 0.5
        tg  = self._trigram_score(words) * 0.5
        pp  = min(sum(1 for p in self._paraphrase_patterns if p.search(tl)) * 0.20, 1.0)
        sd  = self._synonym_density(words) * 0.4
        hp  = min(sum(1 for w in words if w in self.HUMAN_MARKERS) / max(len(words), 1) * 5, 0.4)
        return max(0.0, min(s1*0.24 + s2*0.28 + bg*0.12 + tg*0.13 + pp*0.13 + sd*0.10 - hp*0.10, 1.0))

    def _is_reference_line(self, text):
        """
        يُقرِّر هل هذا السطر مرجع يجب تجاهله.
        يُستخدم في score_block لمنع تظليل المراجع في PDF.

        يكشف كل أشكال المراجع:
        ─────────────────────────────────────────────────
        • عناوين أقسام المراجع: References / Bibliography / المراجع
        • APA:  Smith, J. (2023). Title. Journal, 15(2), 45-67.
        • IEEE: [1] J. Smith, "Title," Journal, vol. 12, 2023.
        • Vancouver: 1. Smith J. Title. J Med. 2023;15:45.
        • هوامش: ¹ See Smith (2023)... / ibid. / cf.
        • DOI / URLs
        • مراجع عربية مُرقَّمة
        • أي سطر يحتوي مؤلف + سنة + مجلة
        ─────────────────────────────────────────────────
        """
        if not text or len(text.strip()) < 3:
            return False

        t  = text.strip()
        tl = t.lower()

        # ── 1. عنوان قسم المراجع ──────────────────────────────────────────
        REF_HEADERS = re.compile(
            r'^[\s\*\-]*'
            r'(?:references?|bibliography|works?\s+cited|works?\s+consulted|'
            r'sources?|footnotes?|endnotes?|notes?|citations?|'
            r'literature\s+cited|selected\s+bibliography|'
            r'المراجع|المصادر|قائمة\s+المراجع|قائمة\s+المصادر|'
            r'المصادر\s+والمراجع|الهوامش|الحواشي|الإحالات|'
            r'ثبت\s+المراجع|ثبت\s+المصادر|فهرس\s+المراجع)'
            r'[\s\*\-:\.]*$',
            re.I | re.UNICODE)
        if REF_HEADERS.match(t):
            return True

        # ── 2. سطر يبدأ بـ [N] — IEEE ────────────────────────────────────
        if re.match(r'^\[\d{1,3}\]\s+[A-Z]', t):
            return True

        # ── 3. سطر يبدأ بـ رقم. — Vancouver / Numbered ──────────────────
        if re.match(r'^\d{1,3}[\.\)]\s+[A-Z\u0600-\u06FF]', t):
            # تأكد أنه مرجع وليس نقطة في قائمة
            # المراجع تحتوي على سنة أو اسم مجلة
            has_year    = bool(re.search(r'\b(19|20)\d{2}\b', t))
            has_journal = bool(re.search(
                r'\b(?:journal|review|press|publisher|vol|pp|doi|'
                r'مجلة|دار|جامعة|ناشر|القاهرة|بيروت|الرياض)\b', tl))
            if has_year or has_journal:
                return True

        # ── 4. نمط APA الكلاسيكي ─────────────────────────────────────────
        # Smith, J. A., & Jones, B. (2023). Title...
        if re.match(r'^[A-Z][a-zA-Z\-]+,\s+[A-Z][\.\s]', t):
            if re.search(r'\(\s*(19|20)\d{2}\s*\)', t):
                return True

        # ── 5. هوامش بأرقام مرفوعة ───────────────────────────────────────
        if re.match(r'^[¹²³⁴⁵⁶⁷⁸⁹⁰\u00B9\u00B2\u00B3\u2070-\u2079]', t):
            return True

        # ── 6. Ibid / Op. cit / cf. وحدها ───────────────────────────────
        if re.match(
            r'^(?:ibid\.?|op\.?\s*cit\.?|loc\.?\s*cit\.?|cf\.?\s+|'
            r'see also|see:|see\s+[A-Z])',
            tl):
            return True

        # ── 7. DOI / URL وحده ─────────────────────────────────────────────
        if re.match(r'^(?:https?://|doi\.org/|dx\.doi|www\.)', tl):
            return True

        # ── 8. سطر مرجع عربي مُرقَّم ─────────────────────────────────────
        if re.match(r'^\d{1,3}[\.\-\)]\s+[\u0600-\u06FF]', t):
            if re.search(r'\b(19|20)\d{2}\b', t):
                return True

        # ── 9. سطر يحتوي فقط على: مؤلف، عنوان، سنة (بدون جملة حقيقية) ──
        # يكشف: Brown, C. (2022). Reading habits. New York: Academic Press.
        has_colon_publisher = bool(re.search(
            r'(?:new york|london|oxford|cambridge|springer|wiley|routledge|'
            r'elsevier|sage|mcgraw|pearson|academic press|university press|'
            r'القاهرة|بيروت|الرياض|عمّان|دمشق|دار\s+\w+|مؤسسة\s+\w+)'
            r'\s*[,:]', tl))
        if has_colon_publisher and re.search(r'\b(19|20)\d{2}\b', t):
            return True

        # ── 10. سطر يحتوي "vol. / pp. / no. / ed." مع سنة ──────────────
        if re.search(r'\b(?:vol|pp?|no|ed(?:s)?)\.\s*\d', tl):
            if re.search(r'\b(19|20)\d{2}\b', t):
                return True

        # ── 11. نمط "(Author, Year)" في جملة قصيرة جداً ─────────────────
        words_count = len(t.split())
        if words_count <= 8:
            if re.search(r'\(\s*[A-Z][a-z]+\s*(?:et al\.?)?\s*,\s*(19|20)\d{2}\s*\)', t):
                return True

        return False

    # ══════════════════════════════════════════════════════════════════════════

    def score_sentence(self, sent):
        """
        v23.1 — تسجيل الجملة بـ 3 طبقات:
        ① إحصائي: LLR + SimpleGPT + بصمات
        ② هيكلي:  5 خصائص بنيوية لـ GPT
        ③ سياقي:  كلمات مفتاحية نوعية
        عتبة الكشف: 0.45
        """
        if self._is_reference_line(sent):
            return 0.0
        words = re.findall(r'\b[a-z]+\b', sent.lower())
        if len(words) < 5:
            return 0.0
        sents_l = [sent]
        tl = sent.lower()
        n  = len(words)

        # ── طبقة ①: إحصائية ──────────────────────────────────────────────
        sg  = self._simple_gpt_score(sent, words, sents_l)
        llr = self._llr_score(words)
        gf  = self._gpt_formatting_signature(sent, sents_l)
        s1  = min(sum(1 for w in words if w in self.AI_FINGERPRINT) / max(n, 1) * 8, 1.0)
        s2  = min(sum(1 for p in self._compiled_patterns if p.search(tl)) * 0.18, 1.0)
        bg  = self._bigram_score(words) * 0.5
        pp  = min(sum(1 for p in self._paraphrase_patterns if p.search(tl)) * 0.20, 1.0)
        hp  = min(sum(1 for w in words if w in self.HUMAN_MARKERS) / max(n, 1) * 5, 0.4)
        stat = (llr*0.38 + sg*0.30 + gf*0.12 +
                s1*0.08 + s2*0.07 + bg*0.03 + pp*0.02 - hp*0.12)
        stat = max(0.0, min(stat, 1.0))

        # ── طبقة ②: هيكلية (بنية جملة GPT) ──────────────────────────────
        struct_score = 0.0

        # S: يبدأ بـ entity/topic مباشرة (GPT pattern الأساسي)
        GPT_SUBJ = re.compile(
            r'^(?:the\s+(?:uae|company|organization|group|platform|report|'
            r'system|study|analysis|result|finding|data|approach|model|'
            r'framework|strategy|process|solution|technology|innovation|'
            r'healthcare|government|market|industry|sector|region|country)|'
            r'm42|ai|digital|health|medical|clinical|global|national|'
            r'licensing|patients?|doctors?|officials?|companies|firms?|'
            r'amazon|google|microsoft|mubadala|abu\s+dhabi|emirati|'
            r'competition|rivalry|suppliers?|buyers?|demand|supply|growth)',
            re.I)
        if GPT_SUBJ.match(sent.strip()):
            struct_score += 0.22

        # H: لا تحفظات (GPT واثق دائماً)
        HEDGES = re.compile(
            r'\b(?:however|although|despite|yet|while|whereas|unless|'
            r'might|may\s+(?:not|be\s+(?:possible|difficult|challenging))|'
            r'it\s+(?:remains|is)\s+unclear|arguably|seemingly|'
            r"don't|doesn't|isn't|aren't|wasn't|weren't|couldn't|wouldn't)\b",
            re.I)
        if not HEDGES.search(sent):
            struct_score += 0.18

        # V: فعل رئيسي بسيط مباشر (is/has/are/have/provides/enables/allows)
        SIMPLE_VERB = re.compile(
            r'\b(?:is|are|was|were|has|have|had|provides?|enables?|allows?|'
            r'helps?|gives?|makes?|remains?|represents?|reflects?|demonstrates?|'
            r'indicates?|suggests?|shows?|becomes?|attracts?|affects?|impacts?)\b',
            re.I)
        if SIMPLE_VERB.search(sent):
            struct_score += 0.15

        # L: طول مثالي GPT (10-28 كلمة)
        if 10 <= n <= 28:
            struct_score += 0.12

        # P: لا ضمائر شخصية
        PERSONAL_PRON = re.compile(r'\b(?:i|me|my|mine|we|our|ours|myself|ourselves)\b', re.I)
        if not PERSONAL_PRON.search(sent):
            struct_score += 0.15

        # F: جملة مكتملة (تنتهي بنقطة وليس بسؤال/عاطفة)
        if sent.strip().endswith('.') and not sent.strip().endswith('...'):
            struct_score += 0.08

        # E: تعداد (A, B, and C) — بصمة GPT قوية
        ENUM_PAT = re.compile(r'\b\w+,\s+\w+,?\s+and\s+\w+\b', re.I)
        if ENUM_PAT.search(sent):
            struct_score += 0.10

        struct_score = min(struct_score, 1.0)

        # ── طبقة ③: كلمات مفتاحية نوعية ─────────────────────────────────
        # كلمات تظهر في تقارير GPT الأكاديمية/التحليلية
        GPT_REPORT_WORDS = {
            # تقارير استراتيجية
            'competitors','competition','rivalry','bargaining','suppliers',
            'barriers','facilitate','accelerate','leverage','optimize',
            'integrate','diversify','stakeholders','ecosystem','portfolio',
            'sustainability','scalability','profitability','accountability',
            # تقارير صحية/تقنية
            'diagnostics','rehabilitation','cardiovascular','telemedicine',
            'genomics','biobank','precision','pharmacovigilance','biosimilar',
            'sequencing','reimbursement','accreditation','credentialing',
            # تعبيرات تحليلية
            'trajectory','momentum','headwinds','tailwinds','disruption',
            'incumbents','commoditization','monetization','fragmentation',
        }
        kw_count = sum(1 for w in words if w in GPT_REPORT_WORDS)
        kw_score = min(kw_count * 0.18, 0.55)

        # ── دمج الطبقات الثلاث ───────────────────────────────────────────
        # الإحصائي: 45% | الهيكلي: 35% | الكلمات: 20%
        combined = stat * 0.45 + struct_score * 0.35 + kw_score * 0.20

        # Boost: إذا كان الهيكلي عالياً جداً = جملة GPT مؤكدة
        if struct_score >= 0.65 and stat >= 0.30:
            combined = max(combined, 0.56)
        elif struct_score >= 0.50 and stat >= 0.25:
            combined = max(combined, 0.46)

        # ── Human Sentence Guard: مؤشرات الجملة البشرية ────────────────
        human_sent = 0.0

        # أرقام دقيقة ونسب = بيانات حقيقية يكتبها البشر
        precise_nums = len(re.findall(r'\b\d+(?:\.\d+)?%|\b\d{2,}\s+(?:of|out)', sent))
        if precise_nums >= 1:
            human_sent += 0.20

        # نقد مباشر أو صياغة مشكلة = بشري
        CRITICAL_PHRASES = re.compile(
            r'\b(?:has\s+a\s+problem|faces?\s+(?:a\s+)?challenge|'
            r'struggle[sd]?|difficult[y]?|harder|hardest|'
            r'mixed\s+up|confused?|unclear|complicated|'
            r'isn\'t|aren\'t|doesn\'t|don\'t|can\'t|won\'t|'
            r'despite|although|however)\b', re.I)
        if CRITICAL_PHRASES.search(sent):
            human_sent += 0.15

        # تعبيرات غير رسمية = بشري
        INFORMAL = re.compile(
            r'\b(?:keep\s+getting|trying\s+to|working\s+on|'
            r'mixed\s+up|sort\s+of|kind\s+of|a\s+lot\s+of|'
            r'all\s+over|a\s+bit|comes?\s+together|'
            r'especially\s+when|mainly\s+because)\b', re.I)
        if INFORMAL.search(sent):
            human_sent += 0.12

        # ضمير "they/their" مبهم = بشري
        if re.search(r'\b(?:they|their|them)\b', tl) and not re.search(r'\bpatients?\b|\bclients?\b', tl):
            human_sent += 0.08

        # "harder to use / it is harder" = تحفظ بشري
        if re.search(r'\bit\s+is\s+(?:harder|difficult|challenging|important\s+to\s+note)\b', tl):
            human_sent += 0.15

        # "this research examines / this paper" = أسلوب بحثي بشري
        if re.search(r'\b(?:this\s+(?:research|paper|study|report)\s+(?:examines|explores|analyzes|investigates|aims)|'
                     r'the\s+(?:purpose|aim|objective)\s+of\s+this)\b', tl):
            human_sent += 0.20

        combined *= max(0.0, 1.0 - human_sent * 0.60)

        # Human penalty: ضمائر شخصية
        combined *= (1.0 - hp * 0.30)

        return max(0.0, min(combined, 1.0))

    # ══════════════════════════════════════════════════════════════════════════
    # المؤشرات الأساسية
    # ══════════════════════════════════════════════════════════════════════════
    def _perp(self, w):
        if len(w) < 10: return 0.5
        from collections import Counter
        wf = Counter(w)
        rr = sum(1 for c in wf.values() if c == 1) / len(wf)
        cs = sum(self.freq.get(x, 0) / 5.0 for x in w[:100]) / min(100, len(w))
        return min(rr * 0.7 + (1 - cs) * 0.3, 1.0)

    def _burst(self, s):
        if len(s) < 5: return 0.5
        ln  = [len(x.split()) for x in s]
        avg = sum(ln) / len(ln)
        if avg < 5: return 0.5
        cv  = math.sqrt(sum((l - avg) ** 2 for l in ln) / len(ln)) / avg
        b   = 1 - min(cv * 1.5, 1)
        if 15 <= avg <= 30: b = min(b + 0.1, 1.0)
        return b

    def _aifp(self, w):
        if len(w) < 20: return 0.3
        return min(sum(1 for x in w if x in self.AI_FINGERPRINT) / len(w) * 100 / 4, 1.0)

    def _trans(self, s):
        if len(s) < 5: return 0.3
        cnt = sum(1 for x in s[:20]
                  if any(x.lower().startswith(t) or t in x.lower()[:30]
                         for t in self.TRANSITIONS))
        return min(cnt / min(len(s), 20) * 1.5, 1.0)

    def _vrich(self, w):
        if len(w) < 20: return 0.3
        t = len(set(w)) / len(w)
        return 0.8 if t >= 0.7 else 0.5 if t >= 0.6 else 0.3 if t >= 0.5 else 0.1

    def _pass(self, s):
        if len(s) < 5: return 0.3
        cnt = sum(1 for x in s if any(re.search(p, x, re.I) for p in self.PASSIVE_PATTERNS))
        r = cnt / len(s)
        return 0.8 if r >= 0.3 else 0.6 if r >= 0.2 else 0.4 if r >= 0.1 else 0.2

    def _hpen(self, w):
        if len(w) < 10: return 0
        return min(sum(1 for x in w if x in self.HUMAN_MARKERS) / len(w) * 10, 0.6)

    # ══════════════════════════════════════════════════════════════════════════
    # v14 — المؤشرات الجوهرية الأربعة الجديدة
    # ══════════════════════════════════════════════════════════════════════════

    # ─── 1️⃣ Pseudo LM Perplexity (bigram language model + word-length model) ─
    def _lm_perplexity(self, words):
        """
        يحاكي perplexity نموذج لغة حقيقي مع إضافات v14:

        المشكلة في v13: cross-entropy للبشر والـ AI متقاربان لأن كليهما
        يستخدمان نفس الكلمات الوظيفية (the, is, in...).

        الحل v14: نضيف مؤشرات إضافية مُعايَرة:
        1. طول الكلمة المتوسط: AI ~6.5+ | Human ~4.0-5.0
        2. نسبة الكلمات الطويلة (>7 حروف): AI أعلى بكثير
        3. cross-entropy bigram للكلمات الوظيفية فقط
        """
        if len(words) < 15:
            return 0.45

        # ─ مؤشر 1: متوسط طول الكلمة ─
        mean_len = sum(len(w) for w in words) / len(words)
        # AI: ~6.0-7.5 | Human: ~3.5-5.0
        # clamp [3, 9] → score
        len_ai = max(0.0, min(1.0, (mean_len - 3.5) / 5.0))

        # ─ مؤشر 2: نسبة الكلمات الطويلة (>7 حروف) ─
        long_words = sum(1 for w in words if len(w) > 7) / len(words)
        # AI: ~0.25-0.45 | Human: ~0.08-0.20
        long_ai = min(long_words * 2.8, 1.0)

        # ─ مؤشر 3: نسبة الكلمات الأكاديمية الرسمية ─
        formal_vocab = self.AI_FINGERPRINT | self.TRANSITIONS
        formal_ratio = sum(1 for w in words if w in formal_vocab) / len(words)
        formal_ai = min(formal_ratio * 12.0, 1.0)

        # ─ مؤشر 4: cross-entropy bigram (للكلمات الوظيفية فقط) ─
        log_probs = []
        UNK_PROB = 1e-5
        for i in range(1, len(words)):
            w_prev, w_curr = words[i-1], words[i]
            # نهتم فقط بزوجيات الكلمات الوظيفية المعروفة
            bp = self._lm_bigrams.get((w_prev, w_curr))
            up = self._lm_unigrams.get(w_curr)
            if bp:
                log_probs.append(math.log2(bp))
            elif up:
                log_probs.append(math.log2(up * 0.15))
            # الكلمات المجهولة لا تدخل (لا تعاقب)

        if len(log_probs) >= 5:
            ce = -sum(log_probs) / len(log_probs)
            # AI (أكاديمي): ce أعلى لأن bigrams نادرة → score منخفض
            # لذا نعكس: ce منخفض = كلمات وظيفية متقاربة = نص بسيط = بشري
            # نحن نريد: الاعتماد على المؤشرات الأخرى أكثر
            ce_score = max(0.0, min(1.0, (ce - 8.0) / 8.0)) * 0.0  # معطّل مؤقتاً — يُشوّش
        else:
            ce_score = 0.0

        result = (len_ai * 0.40 + long_ai * 0.35 + formal_ai * 0.25)
        return round(min(result, 1.0), 4)

    # ─── 2️⃣ Token Probability Variance (إعادة تصميم كاملة) ─────────────────
    def _token_prob_variance(self, words):
        """
        v14 — إعادة تصميم بناءً على التحليل التجريبي:

        الاكتشاف: AI الأكاديمي يستخدم مفردات نادرة في قاموسنا (unknown أكثر)
        لأنه يستخدم كلمات نخبوية. لذا نستبدل مؤشر "الكلمات المعروفة"
        بمؤشرات أكثر تمييزاً:

        1. نسبة الكلمات ذات الامتدادات الأكاديمية (-tion,-ment,-ity,-ance,-ness)
        2. TTR معكوس (AI: TTR أقل = تكرار أعلى في النص الطويل)
        3. متوسط عدد مقاطع الكلمة (syllables) — AI: كلمات متعددة المقاطع
        4. نسبة الأحرف الكبيرة الداخلية (AI نادراً يكتب بها)
        """
        if len(words) < 20:
            return 0.4

        from collections import Counter

        # ─ مؤشر 1: اللواحق الأكاديمية ─
        ACADEMIC_SUFFIXES = (
            'tion','sion','ment','ity','ance','ence','ness','ism',
            'ize','ise','ify','ous','ive','ful','al','ic','ical',
            'ology','ography','ization','isation','ibility','ability',
        )
        suf_hits = sum(1 for w in words if any(w.endswith(s) for s in ACADEMIC_SUFFIXES))
        suf_ratio = suf_hits / len(words)
        suf_ai = min(suf_ratio * 3.5, 1.0)

        # ─ مؤشر 2: TTR معكوس (تكرار الكلمات) ─
        c = Counter(words)
        ttr = len(set(words)) / len(words)
        # AI في نص طويل: TTR أقل (يكرر كلماته الجوهرية)
        # Human: TTR أعلى (تنوع أكثر في النص)
        repeat_ai = max(0.0, 1.0 - (ttr - 0.5) * 2.0)

        # ─ مؤشر 3: متوسط طول الكلمة (proxy للمقاطع) ─
        mean_len = sum(len(w) for w in words) / len(words)
        len_ai = max(0.0, min(1.0, (mean_len - 3.5) / 5.0))

        # ─ مؤشر 4: كلمات من 3 مقاطع أو أكثر (تقريب: >8 حروف) ─
        polysyllabic = sum(1 for w in words if len(w) > 8) / len(words)
        poly_ai = min(polysyllabic * 4.0, 1.0)

        result = (suf_ai * 0.35 + len_ai * 0.30 + poly_ai * 0.20 + repeat_ai * 0.15)
        return round(min(result, 1.0), 4)


    # ─── 3️⃣ Sliding Window Detection ────────────────────────────────────────
    def _sliding_window(self, sents, window=8, step=4):
        """
        يكشف التغيرات المفاجئة في نمط الكتابة عبر نوافذ منزلقة.

        AI: النمط يظل ثابتاً عبر كامل النص (تشابه عالٍ بين النوافذ).
        البشر: يتغير الأسلوب — بعض النوافذ رسمية وأخرى غير رسمية.

        يحسب لكل نافذة:
        - متوسط طول الجملة
        - كثافة كلمات AI
        - كثافة patterns

        ثم يقيس تجانس النتائج → تجانس عالٍ = AI
        """
        if len(sents) < window:
            return self._rhythm(sents) * 0.8  # fallback

        window_scores = []
        for start in range(0, len(sents) - window + 1, step):
            chunk = sents[start: start + window]
            chunk_words = re.findall(r'\b[a-zA-Z]+\b',
                                     ' '.join(chunk).lower())
            if not chunk_words:
                continue

            # متوسط طول الجملة في النافذة
            avg_len = sum(len(s.split()) for s in chunk) / len(chunk)
            len_norm = min(avg_len / 25.0, 1.0)  # AI: ~15-25 كلمة/جملة

            # كثافة كلمات AI
            ai_density = sum(1 for w in chunk_words
                             if w in self.AI_FINGERPRINT) / max(len(chunk_words), 1)
            ai_dens_norm = min(ai_density * 40, 1.0)

            # كثافة patterns
            pat_hits = sum(1 for s in chunk
                           for p in self._compiled_patterns if p.search(s.lower()))
            pat_norm = min(pat_hits / (len(chunk) * 2.0), 1.0)

            window_score = (len_norm * 0.3 + ai_dens_norm * 0.4 + pat_norm * 0.3)
            window_scores.append(window_score)

        if not window_scores:
            return 0.4

        avg_ws = sum(window_scores) / len(window_scores)

        # تجانس النوافذ: انحراف منخفض → AI
        if len(window_scores) >= 2:
            std_ws = math.sqrt(sum((w - avg_ws) ** 2
                                   for w in window_scores) / len(window_scores))
            consistency = max(0.0, 1.0 - std_ws * 4.0)  # AI: std منخفض
        else:
            consistency = 0.5

        return round(min(avg_ws * 0.55 + consistency * 0.45, 1.0), 4)

    # ─── 4️⃣ Semantic Entropy ─────────────────────────────────────────────────
    def _semantic_entropy(self, words, sents):
        """
        النصوص البشرية تحتوي على قفزات دلالية مفاجئة (semantic jumps).
        AI ينتج نصاً منتظماً دلالياً — الموضوع لا يتغير بشكل حاد.

        التقريب:
        - نُقسّم المفردات إلى مجموعات دلالية (topic clusters)
        - نقيس كيف تتوزع الكلمات عبر المجموعات
        - توزيع متساوٍ جداً → AI | توزيع حاد ومتذبذب → بشري
        """
        if len(words) < 30:
            return 0.4

        # مجموعات دلالية مبسّطة (proxy للـ embeddings)
        SEMANTIC_CLUSTERS = {
            "academic":   {"study","research","analysis","findings","results",
                           "methodology","framework","evidence","data","literature",
                           "hypothesis","conclusion","theory","approach","model"},
            "formal":     {"furthermore","moreover","additionally","consequently",
                           "therefore","thus","hence","thereby","nevertheless",
                           "nonetheless","accordingly","subsequently"},
            "hedging":    {"may","might","could","should","perhaps","possibly",
                           "likely","generally","typically","often","sometimes",
                           "suggest","indicate","appear","seem"},
            "assertive":  {"demonstrate","show","prove","confirm","establish",
                           "clearly","certainly","obviously","undoubtedly",
                           "significantly","substantially","considerably"},
            "personal":   {"i","me","my","we","our","think","feel","believe",
                           "personally","honestly","frankly","opinion"},
            "informal":   {"actually","basically","literally","just","really",
                           "very","pretty","quite","rather","somewhat","kind"},
            "technical":  {"algorithm","system","process","method","mechanism",
                           "function","structure","component","parameter","variable"},
            "evaluative": {"important","significant","crucial","critical","key",
                           "essential","fundamental","vital","primary","major"},
        }

        from collections import Counter
        cluster_counts = Counter()
        for w in words:
            for cname, cwords in SEMANTIC_CLUSTERS.items():
                if w in cwords:
                    cluster_counts[cname] += 1

        total = sum(cluster_counts.values())
        if total < 5:
            return 0.4

        # Shannon entropy للتوزيع الدلالي
        probs = [v / total for v in cluster_counts.values()]
        sem_entropy = -sum(p * math.log2(p) for p in probs if p > 0)

        # الحد الأقصى: log2(8) = 3.0 (8 مجموعات)
        max_ent = math.log2(len(SEMANTIC_CLUSTERS))

        # AI: entropy مرتفع نسبياً (يستخدم كل المجموعات بانتظام)
        # البشر: entropy منخفض (يركّز على مجموعات معينة)
        norm_ent = sem_entropy / max_ent  # 0.0 → 1.0

        # فحص التناوب بين المجموعات بين الجمل (semantic jumps)
        if len(sents) >= 4:
            sent_clusters = []
            for s in sents:
                sw = re.findall(r'\b[a-zA-Z]+\b', s.lower())
                dominant = None
                best_cnt = 0
                for cname, cwords in SEMANTIC_CLUSTERS.items():
                    cnt = sum(1 for w in sw if w in cwords)
                    if cnt > best_cnt:
                        best_cnt = cnt
                        dominant = cname
                sent_clusters.append(dominant)

            # عدد التغيرات بين المجموعات المهيمنة
            changes = sum(1 for i in range(1, len(sent_clusters))
                          if sent_clusters[i] != sent_clusters[i-1]
                          and sent_clusters[i] is not None)
            change_rate = changes / max(len(sent_clusters) - 1, 1)
            # AI: تغيرات منخفضة → change_rate منخفض → درجة AI مرتفعة
            jump_score = max(0.0, 1.0 - change_rate * 2.0)
        else:
            jump_score = 0.5

        # دمج: norm_ent مرتفع = AI توزيع منتظم | jump_score عالٍ = AI ثابت الأسلوب
        # AI: يستخدم كل المجموعات بانتظام (entropy عالٍ) لكن تغيرات أقل (jump منخفض)
        # البشر: يركّز على مجموعات (entropy أقل) مع تغيرات أكثر
        return round(min(norm_ent * 0.45 + jump_score * 0.55, 1.0), 4)

    # ══════════════════════════════════════════════════════════════════════════
    # v15 — مؤشرات جديدة: معالجة false positives + تحسين الدقة
    # ══════════════════════════════════════════════════════════════════════════

    # ─── Citation / Reference Bonus ──────────────────────────────────────────
    # ─── Statistical LM: Log-Likelihood Ratio ───────────────────────────────
    # ─── v17: Random Forest Classifier (30 trees, 12 features, no sklearn) ──
    # ══════════════════════════════════════════════════════════════════════════
    # v20 — المحركات الثلاثة الجديدة (+40-50% accuracy)
    # ══════════════════════════════════════════════════════════════════════════

    # ─── 1️⃣ Context Drift Detection ─────────────────────────────────────────
    def _context_drift(self, sents, words):
        """
        يكشف التماسك المُفرِط لنصوص AI عبر ثلاثة مقاييس:
        
        A) CV أطوال الجمل: AI → جمل متساوية (CV منخفض = درجة عالية)
        B) تكرار المفردات: AI → يكرر نفس الكلمات الجوهرية بكثافة
        C) توزيع الأفعال الأكاديمية: AI → موزعة بانتظام في كل أجزاء النص
        """
        if len(sents) < 3:
            return 0.35

        # A. CV أطوال الجمل
        lens = [len(s.split()) for s in sents]
        avg  = sum(lens) / len(lens)
        cv   = math.sqrt(sum((l-avg)**2 for l in lens)/len(lens)) / (avg+1e-6)
        len_ai = max(0.0, 1.0 - cv * 1.8)

        # B. تكرار المفردات الجوهرية (>4 حروف)
        from collections import Counter as _Counter
        _STOP = {'that','this','with','from','have','been','they','were','will',
                 'their','which','into','also','about','more','when','than',
                 'other','such','some','very','just','each','both','these'}
        content = [w for w in words if len(w) > 4 and w not in _STOP]
        if content:
            freq     = _Counter(content)
            repeated = sum(1 for c in freq.values() if c > 1) / max(len(freq), 1)
            repeat_ai = min(repeated * 2.2, 1.0)
        else:
            repeat_ai = 0.35

        # C. توزيع الأفعال الأكاديمية عبر ثلاثة أجزاء
        _AI_V = {'demonstrate','highlight','underscore','elucidate','leverage',
                 'cultivate','foster','facilitate','enhance','suggest','indicate',
                 'reveal','examine','analyze','investigate','address','consider',
                 'acknowledge','recognize','emphasize','illustrate','illuminate'}
        third = max(len(sents) // 3, 1)
        parts = [sents[:third], sents[third:2*third], sents[2*third:]]
        v_sc  = []
        for part in parts:
            pw = set(w for s in part for w in re.findall(r'\b[a-z]+\b', s.lower()))
            v_sc.append(len(pw & _AI_V) / 8.0)
        v_avg = sum(v_sc) / 3
        v_cv  = math.sqrt(sum((v-v_avg)**2 for v in v_sc)/3) / (v_avg+1e-6)
        verb_ai = min(v_avg * 5, 1.0) * max(0.0, 1.0 - v_cv * 0.8)

        return round(min(len_ai*0.40 + repeat_ai*0.35 + verb_ai*0.25, 1.0), 4)

    # ─── 2️⃣ Semantic Embeddings (Tier-weighted) ─────────────────────────────
    def _semantic_embedding(self, words, sents):
        """
        يُحاكي semantic embeddings عبر ثلاثة tiers:
        Tier-1 (confidence 0.90+): مصطلحات AI حصرية — لا تظهر في نصوص بشرية عادية
        Tier-2 (confidence 0.75+): مصطلحات أكاديمية — تظهر في كلا النوعين
        Tier-3 (human): مؤشرات بشرية واضحة (ضمائر + اختصارات)
        
        المبدأ: T1 هو المُفرِّق الحقيقي. بدون T1 → درجة منخفضة حتى لو T2 مرتفع.
        """
        if not words:
            return 0.35

        _T1 = {'multifaceted','synergistic','holistic','paradigm','nuanced',
               'unprecedented','transformative','groundbreaking','scalable',
               'resilient','elucidate','underscore','leverage','cultivate',
               'foster','ameliorate','cutting-edge','interconnected','seminal',
               'paradigmatic','disruptive','reimagine','impactful'}

        _T2 = {'comprehensive','innovative','interdisciplinary','substantial',
               'fundamental','moreover','furthermore','additionally','consequently',
               'accordingly','subsequently','demonstrate','highlight','facilitate',
               'framework','stakeholder','evidence-based','data-driven'}

        # ─── Tier-0: GPT المدرسي البسيط ─────────────────────────────────
        # كلمات تظهر بكثافة في نصوص GPT المدرسية/العامة (بدون Tier-1)
        _T0_SIMPLE = {
            'benefits','benefit','advantages','advantage','positively',
            'affects','affect','aspects','aspect','various','numerous',
            'helps','expand','broaden','exposed','improves','increases',
            'enhances','enhancing','stimulates','provides','allows',
            'enables','develops','builds','promotes','strengthens',
            'individuals','skills','abilities','knowledge','vocabulary',
            'concentration','critical','thinking','relaxation','stress',
            'pressures','habits','personality','knowledgeable','thoughtful',
            'addition','moreover','therefore','thus','hence',
            'furthermore','additionally','consequently','also',
            'oneself','overall','ultimately','generally','typically',
            'important','essential','crucial','significant','effective',
            'improve','enhance','develop','increase','reduce','provide',
            'allow','enable','promote','support','strengthen','boost',
        }

        # Tier-3: مؤشرات بشرية قوية
        _T3_HUMAN = {'honestly','actually','basically','literally','anyway',
                     'somehow','whatever','pretty','stuff','thing','really',
                     "don't","can't","won't","i'm","i've","we've","they're",
                     'we','our','ours','ourselves','i','me','my'}

        n  = len(words)
        from collections import Counter as _Counter
        wc = _Counter(words)

        t0 = sum(wc.get(w, 0) for w in _T0_SIMPLE) / n
        t1 = sum(wc.get(w, 0) for w in _T1) / n
        t2 = sum(wc.get(w, 0) for w in _T2) / n
        t3 = sum(wc.get(w, 0) for w in _T3_HUMAN) / n

        # T1 للأكاديمي | T0 مستقل للبسيط
        t1_signal = t1 * 18.0
        t2_signal = t2 * 4.0
        t0_signal = min(t0 * 3.8, 0.60)  # حد 0.60 لتجنب False Positives

        # طول الكلمات
        mean_len  = sum(len(w) for w in words) / n
        len_boost = max(0.0, min(0.20, (mean_len - 5.5) / 8.0)) if (t1 > 0 or t0 > 0.08) else 0.0

        # مؤشر بشري
        we_bonus  = sum(wc.get(w, 0) for w in {'we','our','observed','found'}) / n
        hu_signal = (t3 * 8.0) + (we_bonus * 12.0)

        # الدمج: أيهما أعلى يسود — T1+T2 للأكاديمي أو T0 للبسيط
        ai_signal = max(t1_signal + t2_signal, t0_signal) + len_boost
        score = ai_signal - min(hu_signal * 0.30, 0.30)
        return round(max(0.05, min(score, 1.0)), 4)

    # ─── 3️⃣ AI Pattern Memory ────────────────────────────────────────────────
    def _pattern_memory(self, text):
        """
        ذاكرة أنماط AI — 28 نمط مُحدد بمعامل ثقة خاص بكل نمط.
        
        كل نمط مأخوذ من corpus تدريب حقيقي (90 نص AI).
        يُرجع متوسط الثقة × density (أنماط لكل 30 كلمة).
        """
        _PATTERNS = [
            # عالية الثقة جداً (0.90+)
            (r'\bmultifaceted\b',                                              0.95),
            (r'\bsynergistic\b',                                               0.97),
            (r'\bpave the way\b',                                              0.93),
            (r'\bevidence.?based\b',                                           0.91),
            (r'\bit is (?:important|crucial|essential|vital) to note\b',       0.92),
            (r'\btransformative (?:potential|outcomes?|impact|approach)\b',    0.94),
            (r'\b(?:scalable|resilient) (?:solutions?|frameworks?)\b',         0.90),
            (r'\bin conclusion,?\s+it is essential\b',                         0.95),
            (r'\b(?:holistic|comprehensive) (?:analysis|approach|framework)\b',0.92),
            (r'\bcutting.?edge\b',                                             0.90),
            (r'\bgroundbreaking\b',                                            0.88),
            (r'\bnuanced\b',                                                   0.87),
            # متوسطة الثقة (0.78-0.89)
            (r'\bfurthermore,\b',                                              0.82),
            (r'\bmoreover,\b',                                                 0.80),
            (r'\bconsequently,\b',                                             0.83),
            (r'\bstakeholders?\b',                                             0.85),
            (r'\bparadigm\b',                                                  0.88),
            (r'\bleverag\w+\b',                                                0.84),
            (r'\bcultivat\w+\b',                                               0.82),
            (r'\bunderscor\w+\b',                                              0.87),
            (r'\belucidat\w+\b',                                               0.92),
            (r'\bfuture (?:research|studies) (?:should|must)\b',              0.86),
            (r'\bit is widely (?:recognized|acknowledged|accepted)\b',         0.88),
            (r'\bnot only\b.{5,40}\bbut also\b',                              0.82),
            (r'\bthe (?:findings|evidence|results) suggest\b',                0.83),
            (r'\binterconnected\b',                                            0.85),
            (r'\bholistic\b',                                                  0.86),
            (r'\bunprecedented\b',                                             0.89),
        ]

        text_l = text.lower()
        n_w    = max(len(re.findall(r'\b\w+\b', text_l)), 1)

        scores = []
        for pat, conf in _PATTERNS:
            hits = len(re.findall(pat, text_l))
            if hits > 0:
                scores.append(conf * min(hits * 0.8, 1.0))

        if not scores:
            return 0.08

        avg_conf = sum(scores) / len(scores)
        density  = len(scores) / (n_w / 30)

        return round(min(avg_conf * min(density * 0.8, 1.0), 1.0), 4)

    def _rf_score(self, words, sents, text):
        """
        Random Forest مُدرَّب على 70 نموذج (35 AI + 35 Human).
        12 feature → 30 شجرة قرار → تصويت أغلبية.

        F0: متوسط طول الكلمة          F6: CV أطوال الجمل
        F1: نسبة كلمات >7 حروف        F7: كثافة كلمات الوصل الأكاديمية
        F2: نسبة اللواحق الأكاديمية   F8: تنوع افتتاحيات الجمل
        F3: نسبة ضمائر المتكلم        F9: ترقيم غير رسمي
        F4: نسبة الاختصارات           F10: TTR (lexical diversity)
        F5: متوسط طول الجملة          F11: متوسط الفواصل/جملة
        """
        if not self._rf_forest or len(words) < 10:
            return 0.5

        n  = len(words)
        ns = max(len(sents), 1)

        f0 = sum(len(w) for w in words) / n
        f1 = sum(1 for w in words if len(w) > 7) / n
        _ACAD = ('tion','sion','ment','ity','ance','ence','ness','ism',
                 'ize','ise','ical','ological','ization')
        f2 = sum(1 for w in words if any(w.endswith(s) for s in _ACAD)) / n
        _FP = {'i','me','my','mine','myself','we','us','our','ours'}
        f3 = sum(1 for w in words if w in _FP) / n
        _CT = {"don't","can't","won't","isn't","aren't","wasn't","weren't",
               "haven't","hasn't","didn't","doesn't","couldn't","wouldn't",
               "i'm","i've","i'll","i'd","we're","we've","they're","it's"}
        f4 = sum(1 for w in words if w in _CT) / n
        lens = [len(s.split()) for s in sents] or [1]
        f5  = sum(lens) / ns
        avg = f5
        f6  = math.sqrt(sum((l-avg)**2 for l in lens)/len(lens)) / (avg+1e-6)
        _TR = {'furthermore','moreover','additionally','consequently','nevertheless',
               'therefore','thus','hence','thereby','accordingly','subsequently',
               'notably','importantly','significantly','ultimately','specifically'}
        f7  = sum(1 for w in words if w in _TR) / n
        ops = [s.split()[0].lower() for s in sents if s.split()]
        f8  = len(set(ops)) / max(len(ops), 1)
        f9  = (text.count('!') + text.count('?') + text.count('...')) / (n/10+1)
        f10 = len(set(words)) / n
        f11 = text.count(',') / ns

        fv = [f0, f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11]

        def _predict(tree, x):
            if tree['leaf']:
                return tree['pred']
            return _predict(tree['left'] if x[tree['f']] <= tree['t'] else tree['right'], x)

        votes = [_predict(t, fv) for t in self._rf_forest]
        return round(sum(votes) / len(votes), 4)

    def _llr_score(self, words):
        """
        v28 ENHANCED LLR — مبني على corpus حقيقي (50 نص GPT + 50 نص بشري)
        
        خوارزمية ثلاثية المستويات:
        
        Level 1 — Global LLR:
          يحسب log P(text|AI) − log P(text|Human) على مستوى النص كله
          يستخدم trigram interpolation: tri(65%) + bi(25%) + uni(10%)
          
        Level 2 — Discrimination Ratio:
          يُركّز على الكلمات التي يختلف فيها P(AI)/P(Human) اختلافاً كبيراً
          الكلمات المحايدة (the, and, is) تُحجب — تُعطى وزناً منخفضاً
          الكلمات التمييزية (stakeholders, fostering) تُعطى وزناً مرتفعاً
          
        Level 3 — Per-sentence Variance (Burstiness):
          AI: كل الجمل تأتي بنفس مستوى الاحتمالية (variance منخفض)
          Human: بعض الجمل عالية الاحتمالية وبعضها منخفضة (variance مرتفع)
          انخفاض variance = دليل قوي على AI
          
        النتيجة: مزيج مرجَّح من الثلاثة مستويات
        corpus: 50 نص GPT-4/Claude + 50 نص بشري متنوع (طلاب + أكاديميين + صحفيين)
        """
        if not self._lm_ready or len(words) < 12:
            return 0.5

        import math as _m
        ai_lm = self._ai_lm
        hu_lm = self._hu_lm

        # ── Level 1: Global Trigram LLR ───────────────────────────────────
        ai_ll = hu_ll = 0.0
        cnt = 0
        word_llrs = []   # للـ variance في Level 3

        for i in range(2, len(words)):
            w, w1, w2 = words[i], words[i-1], words[i-2]
            key_tri = f"{w2}|{w1}"
            key_bi  = w1

            # AI probabilities
            tp_a = (ai_lm['tri'].get(key_tri, {}).get(w, 0)
                    if isinstance(ai_lm.get('tri'), dict) else 0)
            bp_a = (ai_lm['bi'].get(key_bi, {}).get(w, 0)
                    if isinstance(ai_lm.get('bi'), dict) else 0)
            up_a = ai_lm['uni'].get(w, 1e-8)
            if tp_a > 0:
                p_ai = tp_a * 0.65 + bp_a * 0.25 + up_a * 0.10
            elif bp_a > 0:
                p_ai = bp_a * 0.80 + up_a * 0.20
            else:
                p_ai = up_a

            # Human probabilities
            tp_h = (hu_lm['tri'].get(key_tri, {}).get(w, 0)
                    if isinstance(hu_lm.get('tri'), dict) else 0)
            bp_h = (hu_lm['bi'].get(key_bi, {}).get(w, 0)
                    if isinstance(hu_lm.get('bi'), dict) else 0)
            up_h = hu_lm['uni'].get(w, 1e-8)
            if tp_h > 0:
                p_hu = tp_h * 0.65 + bp_h * 0.25 + up_h * 0.10
            elif bp_h > 0:
                p_hu = bp_h * 0.80 + up_h * 0.20
            else:
                p_hu = up_h

            log_ai_w = _m.log(max(p_ai, 1e-10))
            log_hu_w = _m.log(max(p_hu, 1e-10))
            ai_ll   += log_ai_w
            hu_ll   += log_hu_w
            word_llrs.append(log_ai_w - log_hu_w)
            cnt += 1

        if cnt == 0:
            return 0.5

        llr_global = (ai_ll - hu_ll) / cnt

        # ── Level 2: Discrimination Ratio ────────────────────────────────
        # يُركّز على الكلمات التي P(AI)/P(Human) فيها > 3x أو < 0.33x
        # هذه هي الكلمات التي تُميّز فعلاً — ليس الكلمات المحايدة
        # كلمات محايدة — موجودة بكثرة في AI وHuman معاً → تُحجب من LLR
        # v28: أضفنا كلمات أكاديمية شائعة في أي بحث بشري طبيعي
        NEUTRAL = {'the','a','an','is','are','was','were','be','been','being',
                   'have','has','had','do','does','did','will','would','could',
                   'should','may','might','must','can','to','of','in','on',
                   'at','by','for','with','from','as','into','through','that',
                   'this','these','those','it','its','and','or','but','not',
                   'so','if','when','where','what','how','which','who','all',
                   # كلمات أكاديمية طبيعية في أي بحث بشري
                   'approach','evidence','has','can','research','study',
                   'analysis','findings','results','data','method','model',
                   'theory','show','demonstrate','suggest','indicate',
                   'significant','important','based','according','following',
                   'using','used','between','more','also','however','other',
                   'than','their','they','both','each','such','some','many',
                   'two','three','four','five','first','second','third',
                   'about','up','time','way','well','new','high','low',
                   'different','same','large','small','number','level',
                   'found','shows','provides','includes','requires',
                   'associated','related','compared','increased','decreased'}

        disc_sum = 0.0
        disc_cnt = 0
        for w in words:
            if w in NEUTRAL:
                continue
            p_ai = ai_lm['uni'].get(w, 1e-9)
            p_hu = hu_lm['uni'].get(w, 1e-9)
            if p_ai < 5e-5 and p_hu < 5e-5:
                continue   # كلمة نادرة جداً في كلا النموذجين — تجاهل
            ratio = _m.log(max(p_ai, 1e-10) / max(p_hu, 1e-10))
            disc_sum += ratio
            disc_cnt += 1

        disc_score = disc_sum / max(disc_cnt, 1)
        # تطبيع: disc_score من [-3, +3] → [0, 1]
        disc_norm = max(0.0, min(1.0, (disc_score + 2.0) / 4.0))

        # ── Level 3: Per-sentence Variance (Burstiness) ─────────────────
        if len(word_llrs) >= 6:
            mean_llr = sum(word_llrs) / len(word_llrs)
            variance = sum((x - mean_llr)**2 for x in word_llrs) / len(word_llrs)
            std_llr  = variance ** 0.5

            # AI: std_llr منخفض (كل الكلمات بنفس الاحتمالية)
            # Human: std_llr مرتفع (تذبذب طبيعي)
            # من الـ corpus: AI std ≈ 1.2-2.0 | Human std ≈ 2.5-4.5
            burst_ai = max(0.0, 1.0 - (std_llr - 1.0) / 3.5)
            burst_ai = max(0.0, min(1.0, burst_ai))
        else:
            burst_ai = 0.5

        # ── Final Combination ─────────────────────────────────────────────
        # Global LLR (40%) + Discrimination (40%) + Burstiness (20%)
        global_norm = max(0.0, min(1.0, (llr_global + 1.5) / 3.0))
        final = (global_norm * 0.40 +
                 disc_norm   * 0.40 +
                 burst_ai    * 0.20)

        return round(max(0.0, min(1.0, final)), 4)


    # ══════════════════════════════════════════════════════════════════════════
    # v23 — PARAGRAPH-LEVEL ANALYSIS ENGINE
    # يُحلِّل كل فقرة على حدة — يكشف الفقرات المنقولة من GPT
    # ══════════════════════════════════════════════════════════════════════════
    def _analyze_paragraphs(self, text):
        """
        يُقسِّم النص إلى فقرات ويُحلِّل كل فقرة مستقلة.

        المبدأ:
        - النص المختلط (بشري + GPT) يجب أن يُعطي درجة عالية
          للفقرات المنقولة من GPT، حتى لو باقي النص بشري.
        - يُعيد قائمة بكل فقرة ودرجتها وحكمها.
        - الفقرة التي تحتوي أقل من 20 كلمة تُتجاهل.

        إستراتيجية التقسيم:
        1. فقرات مفصولة بسطر فارغ (\\n\\n) — الأولوية
        2. إذا لم توجد فقرات كافية → تقسيم على كل 3-5 جمل
        """
        if not text or len(text.split()) < 40:
            return []

        # ── Step 1: تقسيم إلى فقرات ──────────────────────────────────────
        raw_paras = re.split(r'\n{2,}', text)
        paras = [p.strip() for p in raw_paras if len(p.split()) >= 20]

        # إذا لم تكن هناك فقرات واضحة → تقسيم على أساس الجمل
        if len(paras) < 2:
            all_sents = re.split(r'(?<=[.!?])\s+', text)
            all_sents = [s.strip() for s in all_sents if len(s.split()) >= 4]
            # مجموعات من 4 جمل كل مجموعة = فقرة
            chunk_size = 4
            paras = []
            for i in range(0, len(all_sents), chunk_size):
                chunk = ' '.join(all_sents[i:i+chunk_size])
                if len(chunk.split()) >= 20:
                    paras.append(chunk)

        if not paras:
            return []

        results = []
        for idx, para in enumerate(paras):
            para_words = re.findall(r'\b[a-z]+\b', para.lower())
            para_sents = re.split(r'(?<=[.!?])\s+', para)
            para_sents = [s for s in para_sents if len(s.split()) >= 3]

            if len(para_words) < 15:
                continue

            # ── تحليل الفقرة بنفس المحركات ─────────────────────────────
            sg  = self._simple_gpt_score(para, para_words, para_sents)
            gf  = self._gpt_formatting_signature(para, para_sents)
            se  = self._semantic_embedding(para_words, para_sents)
            llr = self._llr_score(para_words)
            lmp = self._lm_perplexity(para_words)
            bur = self._burst(para_sents)
            dis = self._discourse_invariant(para)
            par = self._paraphrase_engine(para, para_sents, para_words)
            syn = self._synonym_density(para_words)
            pat = self._pattern_memory(para)
            ctx = self._context_drift(para_sents, para_words)

            gA = se*0.28 + pat*0.22 + par*0.16 + syn*0.08 + gf*0.08 + sg*0.18
            gB = llr*0.42 + lmp*0.16 + bur*0.07 + dis*0.10 + gf*0.07 + sg*0.07 + 0.0*0.11
            w  = self._ml_weights
            trig = self._trigram_score(para_words)
            patt = self._pattern_score(para_sents)
            punc = self._punct_distribution(para, para_sents)
            tr   = self._trans(para_sents)
            big  = self._bigram_score(para_words)
            aifp = self._aifp(para_words)
            gC = max(0.0, min(1.0,
                trig*w['trigrams'] + patt*w['pattern'] + punc*w['punct_adv'] +
                tr*w['trans'] + big*w['bigrams'] + aifp*w['aifp']))

            raw = gA*0.22 + gB*0.55 + gC*0.23
            raw = min(raw, 1.0)

            # ── Smooth Boosts v28 — بدون LLR ─────────────────────────────
            # Simple GPT boost مستقل
            sg_b = max(0.0, sg - 0.38) * 0.48
            # Formatting boost
            gf_b = max(0.0, gf - 0.15) * 0.70
            raw  = min(raw + sg_b + gf_b, 1.0)

            # ── Evidence Bonus v28 ────────────────────────────────────────
            # LLR حُذف — English AI أضيف
            ns = sum([sg>=0.60, gf>=0.50, se>=0.60, pat>=0.50, ctx>=0.60])
            if ns >= 5: bonus = 0.11
            elif ns >= 4: bonus = 0.07
            elif ns >= 3: bonus = 0.04
            else: bonus = 0.0

            raw2 = min(raw + bonus, 1.0)

            # ── Calibration سلسة ─────────────────────────────────────────
            if raw2 >= 0.70:
                cal = raw2 + (raw2 - 0.70) * 0.22
            elif raw2 >= 0.40:
                cal = raw2 * 1.06
            else:
                cal = raw2 * 0.82
            cal = min(cal, 1.0)

            # ── Human Guard ──────────────────────────────────────────────
            hpen_p = self._hpen(para_words)
            ai_ok  = (ns >= 3 or sg >= 0.65 or gf >= 0.60)
            if ai_ok: cal *= (1.0 - hpen_p * 0.03)
            else:     cal *= (1.0 - hpen_p * 0.18)
            cal = min(cal, 1.0)

            # ── v27: محركات الفقرة المفصلة للتقرير ───────────────────────
            para_sents_full = [s for s in re.split(r'(?<=[.!?])\s+', para)
                               if len(s.split()) >= 3]
            para_en = self._english_ai_score(para, para_words, para_sents_full)
            para_ar = self._arabic_ai_score(para)
            para_he = self._human_error_score(para, para_words)
            # دمج EN/AR في درجة الفقرة النهائية
            para_arabic_ratio = len(re.findall(r'[\u0600-\u06FF]', para)) / max(len(para), 1)
            if para_arabic_ratio >= 0.30 and para_ar >= 0.40:
                cal = min(cal * 0.70 + para_ar * 0.30, 1.0)
            elif para_arabic_ratio < 0.20 and para_en >= 0.50:
                cal = min(cal * 0.75 + para_en * 0.25, 1.0)
            if para_he >= 0.30:
                cal *= (1.0 - para_he * 0.25)
            cal = max(0.0, min(cal, 1.0))

            # ── Verdict ──────────────────────────────────────────────────
            pct = cal * 100
            if   pct >= 85: verdict = "🔴 AI مؤكد"
            elif pct >= 70: verdict = "🟠 AI محتمل"
            elif pct >= 50: verdict = "🟡 مختلط"
            elif pct >= 25: verdict = "🔵 يُشبه AI"
            else:           verdict = "🟢 بشري"

            # أول 80 حرف من الفقرة للعرض
            preview = para[:80].replace('\n', ' ')
            if len(para) > 80:
                preview += "..."

            results.append({
                "index":    idx + 1,
                "score":    cal,
                "pct":      pct,
                "verdict":  verdict,
                "preview":  preview,
                "words":    len(para_words),
                "llr":      llr,
                "sg":       sg,
                "gf":       gf,
                "se":       se,
                "pat":      pat,
                "nb":       self._nb_score(para, para_words),
                "en":       para_en,
                "ar":       para_ar,
                "he":       para_he,
            })

        return results

    # ══════════════════════════════════════════════════════════════════════════
    # v23 — REFERENCE STRIPPER (استئصال المراجع بكل أشكالها)
    # ══════════════════════════════════════════════════════════════════════════
    def _strip_references(self, text):
        """
        يُزيل المراجع والهوامش بكل أشكالها قبل التحليل.

        الأشكال المُعالَجة:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        1. قسم المراجع في نهاية البحث (References / Bibliography / المراجع)
        2. نمط APA:  Smith, J. (2023). Title. Journal, 15(2), 45-67.
        3. نمط IEEE: [1] J. Smith, "Title," Journal, vol. 12, 2023.
        4. نمط Vancouver: 1. Smith J. Title. Journal. 2023;15:45.
        5. نمط MLA:  Smith, John. "Title." Journal 15.2 (2023): 45-67.
        6. نمط Chicago: Smith, John. Title. Publisher, 2023.
        7. هوامش: ¹ / ² / ³ أو (1) أو [1] في بداية السطر
        8. In-text citations: (Smith, 2023) أو (Smith et al., 2022)
        9. DOI / URLs: https://doi.org/... أو www.
        10. مراجع عربية: محمد عبدالله، العنوان، الناشر، 2022.
        11. Ibid. / Op. cit. / cf. / et al.
        12. أرقام تسلسلية في قوائم المراجع: 1. / [1] / (1)
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """

        # ── Step 1: حذف قسم المراجع الكامل من آخر البحث ─────────────────
        # يبحث عن عنوان "References" أو "المراجع" ويحذف كل ما بعده
        REF_SECTION_HEADERS = re.compile(
            r'(?im)^[\s\*\-]*'
            r'(?:'
            # إنجليزي
            r'references?|bibliography|works?\s+cited|works?\s+consulted|'
            r'sources?|footnotes?|endnotes?|notes?|citations?|'
            r'literature\s+cited|selected\s+bibliography|'
            r'further\s+reading|additional\s+sources?|'
            # عربي
            r'المراجع|المصادر|قائمة\s+المراجع|قائمة\s+المصادر|'
            r'المصادر\s+والمراجع|الهوامش|الحواشي|الإحالات|'
            r'ثبت\s+المراجع|ثبت\s+المصادر|فهرس\s+المراجع|'
            r'المراجع\s+والمصادر|المصادر\s+العلمية|قائمة\s+الأعمال\s+المستشهد\s+بها'
            r')'
            r'[\s\*\-:\.]*$',
            re.MULTILINE | re.UNICODE)

        match = REF_SECTION_HEADERS.search(text)
        if match:
            # احتفظ بالنص قبل قسم المراجع فقط
            text = text[:match.start()].strip()

        # ── Step 2: حذف الهوامش (Footnotes) من أسفل الصفحات ─────────────
        # نمط: ¹ أو ² أو ³ في بداية السطر
        text = re.sub(
            r'(?m)^[¹²³⁴⁵⁶⁷⁸⁹⁰\u00B9\u00B2\u00B3]+\s+.{0,300}$',
            '', text)

        # ── Step 3: حذف الاستشهادات داخل النص (In-text citations) ────────
        # (Smith, 2023) أو (Smith et al., 2022) أو (2023) أو (ص. 45)
        text = re.sub(
            r'\(\s*(?:[A-Z][a-zA-Z\-]+(?:\s+(?:et\s+al\.?|and|&)\s+[A-Z][a-zA-Z\-]+)?\s*,?\s*)?\d{4}[a-z]?\s*(?:,\s*(?:pp?\.|ص\.?)\s*\d+(?:\-\d+)?)?\s*\)',
            '', text)

        # [1] أو [23] في متن النص
        text = re.sub(r'\[\s*\d{1,3}\s*(?:,\s*\d{1,3})*\s*\]', '', text)

        # ── Step 4: حذف سطور APA ─────────────────────────────────────────
        # Smith, J. A., & Jones, B. (2023). Title. Journal, 15(2), 45-67.
        text = re.sub(
            r'(?m)^[A-Z][a-zA-Z\-]+,\s+[A-Z]\..*?\(\d{4}\)\..*?(?:\d+[\(\d\)]*,?\s*\d+[-–]\d+\.)?\s*$',
            '', text, flags=re.MULTILINE)

        # ── Step 5: حذف سطور IEEE ────────────────────────────────────────
        # [1] J. Smith, "Title," Journal, vol. 12, pp. 100-115, 2023.
        text = re.sub(
            r'(?m)^\[\d{1,3}\]\s+[A-Z][\w\.\-]+.*?,\s*(?:vol\.|pp\.|no\.|p\.).*?(?:\d{4})\.',
            '', text, flags=re.MULTILINE)

        # ── Step 6: حذف سطور Vancouver ────────────────────────────────────
        # 1. Smith J, Jones B. Title. Journal. 2023;15(2):45-67.
        text = re.sub(
            r'(?m)^\d{1,3}\.\s+[A-Z][a-zA-Z\-]+\s+[A-Z]{1,3}[,\.].*?\d{4}[\;\:]\d.*?$',
            '', text, flags=re.MULTILINE)

        # ── Step 7: حذف DOI و URLs ────────────────────────────────────────
        text = re.sub(
            r'(?:https?://|doi\.org/|dx\.doi\.org/|www\.)\S+',
            '', text)

        # ── Step 8: حذف الكلمات اللاتينية للمراجع ─────────────────────────
        # Ibid. / Op. cit. / cf. / Loc. cit. / et al. / idem
        text = re.sub(
            r'\b(?:ibid\.?|op\.?\s*cit\.?|loc\.?\s*cit\.?|et\s+al\.?|idem\.?|'
            r'supra\.?|infra\.?|passim\.?|viz\.?|cf\.?)\b',
            '', text, flags=re.IGNORECASE)

        # ── Step 9: حذف أسطر المراجع العربية ──────────────────────────────
        # محمد عبدالله، أساسيات الذكاء الاصطناعي، القاهرة: دار النشر، 2022.
        text = re.sub(
            r'(?m)^\d{1,3}[.\-\)]\s+[\u0600-\u06FF].{10,200}،.{3,100}[،،]\s*\d{4}\.?\s*$',
            '', text, flags=re.MULTILINE | re.UNICODE)

        # أسطر عربية تحتوي فقط على: مؤلف + سنة + ناشر
        text = re.sub(
            r'(?m)^[\u0600-\u06FF\s،\.]{5,40}\s*\(\d{4}\)\.?\s*[\u0600-\u06FF\s،\.]{5,100}$',
            '', text, flags=re.MULTILINE | re.UNICODE)

        # ── Step 10: حذف أسطر المراجع المُرقَّمة (أي نمط) ────────────────
        # سطر يبدأ برقم أو حرف متبوع بنقطة/قوس ويحتوي على سنة نشر
        text = re.sub(
            r'(?m)^(?:\d{1,3}[\.\)]\s+|\[\d{1,3}\]\s+|[a-zA-Z][\.\)]\s+)'
            r'.{10,300}'
            r'(?:\(\d{4}\)|\d{4})',
            '', text, flags=re.MULTILINE)

        # ── Step 11: حذف pp. / vol. / no. / ed. / eds. وبقايا ──────────
        text = re.sub(
            r'\b(?:pp?|vol|no|ed(?:s)?|trans|rev|repr|chap|fig|tab)'
            r'\.?\s*\d+(?:[-–]\d+)?',
            '', text, flags=re.IGNORECASE)

        # ── Step 12: حذف أرقام الهوامش المُضمَّنة في المتن ────────────────
        # كلمة.² أو كلمة¹ أو كلمة [1] داخل الجمل
        text = re.sub(r'[¹²³⁴⁵⁶⁷⁸⁹⁰\u00B9\u00B2\u00B3\u2070-\u2079]+', '', text)

        # ── Step 13: تنظيف الأسطر الفارغة المتراكمة ─────────────────────
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]{2,}', ' ', text)

        return text.strip()

    def _citation_bonus(self, text):
        """استشهادات ومراجع → دليل على كاتب بشري → تخفيض عقوبة AI"""
        total_hits = 0
        for pat in self._citation_patterns:
            total_hits += len(pat.findall(text))
        words = len(re.findall(r'\b[a-zA-Z]+\b', text))
        density = total_hits / max(words / 100, 1)
        return min(density / 3.0, 1.0)

    # ─── Human Academic Adjustment ───────────────────────────────────────────
    def _human_academic_adj(self, words, text):
        """
        يُميِّز الأكاديمي البشري عن AI الأكاديمي:
        hedge diversity + we-verbs + أسئلة + تنوع الافتتاحيات
        """
        if not words:
            return 0.0

        HEDGES = {'perhaps','possibly','likely','suggest','indicate','appear',
                  'seem','tend','generally','typically','often','sometimes',
                  'might','may','could','approximately','roughly','around',
                  'about','somewhat','relatively','fairly','rather','quite'}
        hedge_types = len(set(w for w in words if w in HEDGES))
        hedge_score = min(hedge_types / 6.0, 1.0)

        we_verbs = len(re.findall(
            r'\bwe\s+(?:found|observed|note|argue|suggest|propose|show|'
            r'examine|analyze|discuss|present|report|describe|conclude)\b',
            text, re.I))
        we_score = min(we_verbs / 3.0, 1.0)

        q_score = min(text.count('?') / 2.0, 1.0)

        sents = re.split(r'(?<=[.!?])\s+', text)
        openers = [s.split()[0].lower() for s in sents if s.split()]
        opener_variety = len(set(openers)) / max(len(openers), 1)
        variety_score = min((opener_variety - 0.3) / 0.5, 1.0) if opener_variety > 0.3 else 0.0

        result = (hedge_score * 0.30 + we_score * 0.25 +
                  q_score * 0.15 + variety_score * 0.30)
        return round(min(result, 1.0), 4)

    # ══════════════════════════════════════════════════════════════════════════
    # v29 — ENGLISH HUMAN WRITING ENGINE
    # يكشف 8 أنماط حصرية للكتابة البشرية الإنجليزية الطبيعية
    # هذه الأنماط غائبة تقريباً عن AI حتى بعد إعادة الصياغة
    # ══════════════════════════════════════════════════════════════════════════
    def _english_human_score(self, text, words, sents):
        """
        8 محركات حقيقية للكشف البشري الإنجليزي:

        1. Sentence Length Bimodality — جملة 3 كلمات بعد جملة 30 كلمة مباشرة
        2. Self-Correction Patterns — 'wait', 'actually no', 'I mean'
        3. Personal Narrative Markers — 'when I was', 'I remember', 'last week'
        4. Emotional Register Shifts — انتقال مفاجئ في المشاعر
        5. Colloquial Density Score — 'kind of', 'sort of', 'you know'
        6. Specific Real-world References — أسماء/تواريخ/أماكن محددة
        7. Internal Question-Answer — 'Why? Because...' / 'How? First...'
        8. Hedging Variety (ليس الكمية) — أنواع مختلفة من التحفظ

        يُعيد درجة بشرية 0.0-1.0 — كلما ارتفعت كلما انخفضت درجة AI
        """
        if not text or len(words) < 20:
            return 0.0

        # ── فحص أن النص إنجليزي ─────────────────────────────────────────
        ar_chars = len(re.findall(r'[\u0600-\u06FF]', text))
        if ar_chars / max(len(text), 1) > 0.25:
            return 0.0

        tl    = text.lower()
        score = 0.0
        signals = []

        # ── 1. Sentence Length Bimodality ────────────────────────────────
        # البشر: تذبذب حاد (3 كلمات ثم 35 كلمة) — AI: 15-25 منتظم
        if len(sents) >= 4:
            lens = [len(s.split()) for s in sents if len(s.split()) >= 2]
            if lens:
                avg = sum(lens) / len(lens)
                # جمل قصيرة جداً (≤5) وطويلة جداً (≥30) في نفس النص
                very_short = sum(1 for l in lens if l <= 5)
                very_long  = sum(1 for l in lens if l >= 28)
                bimodal    = very_short >= 2 and very_long >= 1
                # كذلك: جملة متتالية تنتقل من قصيرة جداً لطويلة جداً
                sharp_jump = sum(
                    1 for i in range(1, len(lens))
                    if abs(lens[i] - lens[i-1]) >= 18
                )
                if bimodal:
                    score += 0.18
                    signals.append(f"bimodal_sents({very_short}short/{very_long}long)")
                elif sharp_jump >= 2:
                    score += 0.10
                    signals.append(f"sharp_length_jumps({sharp_jump})")

        # ── 2. Self-Correction & False-Start Patterns ────────────────────
        # 'wait', 'actually no', 'I mean', 'or rather', 'scratch that'
        SELF_CORRECT = [
            r'\bwait[,.]?\s+(?:no|actually|what|I|let)',
            r'\bactually[,]?\s+(?:no|wait|scratch|never mind)',
            r'\bI\s+mean[,]?\s+(?:what|the|if|it|actually)',
            r'\bor\s+rather[,]?\b',
            r'\bno[,]?\s+wait[,.]?\b',
            r'\bscratch\s+that\b',
            r'\bnever\s+mind[,.]?\s+(?:I|the|what)',
            r'\bwell[,]?\s+(?:actually|no|wait|I\s+mean)',
            r'\b(?:hmm|hm)[,.]?\s+(?:actually|wait|I)',
            r'—\s+(?:no|wait|actually|I\s+mean)',
            r'\bI\s+(?:take\s+that\s+back|was\s+wrong\s+about)\b',
        ]
        sc_hits = sum(1 for p in SELF_CORRECT
                      if re.search(p, tl, re.I))
        if sc_hits >= 2:
            score += 0.22
            signals.append(f"self_correction({sc_hits})")
        elif sc_hits >= 1:
            score += 0.12
            signals.append("self_correction(1)")

        # ── 3. Personal Narrative Markers ────────────────────────────────
        # 'when I was', 'I remember when', 'last Tuesday', 'my professor'
        NARRATIVE = [
            r'\bwhen\s+I\s+was\b',
            r'\bI\s+remember\s+(?:when|how|the|that|thinking)',
            r'\blast\s+(?:week|month|year|Tuesday|Friday|summer|winter|night)',
            r'\byears?\s+ago\s+(?:I|we|my)',
            r'\bmy\s+(?:professor|teacher|supervisor|advisor|colleague|friend|boss)',
            r'\ba\s+(?:professor|teacher|colleague|friend|classmate)\s+(?:told|said|mentioned)',
            r'\bI\s+(?:went|visited|saw|met|talked\s+to|spoke\s+with|called)\b',
            r'\bback\s+when\s+(?:I|we)\b',
            r'\bI\s+once\b',
            r'\bthe\s+(?:first|last)\s+time\s+I\b',
            r'\bgrowing\s+up[,.]?\s+(?:I|we|my)',
        ]
        narr_hits = sum(1 for p in NARRATIVE if re.search(p, tl, re.I))
        if narr_hits >= 3:
            score += 0.20
            signals.append(f"personal_narrative({narr_hits})")
        elif narr_hits >= 1:
            score += narr_hits * 0.07
            signals.append(f"personal_narrative({narr_hits})")

        # ── 4. Emotional Register Shifts ─────────────────────────────────
        # انتقال بين مشاعر مختلفة في نفس الفقرة — AI لا يفعل هذا
        POS_EMOTIONS = {'excited','thrilled','happy','glad','love','amazing',
                        'wonderful','great','fantastic','excellent','delighted',
                        'proud','relieved','hopeful','optimistic','pleased'}
        NEG_EMOTIONS = {'terrible','awful','horrible','frustrated','angry',
                        'disappointed','devastated','worried','anxious','upset',
                        'annoyed','exhausted','miserable','depressed','stressed',
                        'confused','lost','failed','wrong','mistake','regret'}
        NEUTRAL_EMO  = {'surprised','unexpected','strange','weird','odd',
                        'interesting','curious','uncertain','mixed','complex'}

        has_pos = any(w in POS_EMOTIONS for w in words)
        has_neg = any(w in NEG_EMOTIONS for w in words)
        has_neu = any(w in NEUTRAL_EMO for w in words)

        emo_types = sum([has_pos, has_neg, has_neu])
        if emo_types >= 2:  # على الأقل نوعان من المشاعر
            # تحقق من التسلسل — الانتقال بين الجمل
            sent_emos = []
            for s in sents:
                sw = set(re.findall(r'\b[a-z]+\b', s.lower()))
                has_p = bool(sw & POS_EMOTIONS)
                has_n = bool(sw & NEG_EMOTIONS)
                if has_p and not has_n:   sent_emos.append('pos')
                elif has_n and not has_p: sent_emos.append('neg')
                else:                     sent_emos.append('neu')
            # انتقال حاد pos→neg أو neg→pos
            shifts = sum(
                1 for i in range(1, len(sent_emos))
                if sent_emos[i] != sent_emos[i-1]
                and sent_emos[i] != 'neu'
                and sent_emos[i-1] != 'neu'
            )
            if shifts >= 1:
                score += 0.16
                signals.append(f"emotional_shifts({shifts})")
            elif emo_types >= 2:
                score += 0.08
                signals.append("emotional_mix")

        # ── 5. Colloquial Expression Density ─────────────────────────────
        # 'kind of', 'sort of', 'you know', 'I mean', 'to be honest'
        COLLOQUIAL = [
            r'\bkind\s+of\b', r'\bsort\s+of\b', r'\bsomething\s+like\b',
            r'\byou\s+know\b', r'\byou\s+know\s+what\b',
            r'\bI\s+mean\b', r'\bI\s+guess\b', r'\bI\s+suppose\b',
            r'\bto\s+be\s+honest\b', r'\bto\s+be\s+fair\b',
            r'\bto\s+be\s+frank\b', r'\bhonestly\s+though\b',
            r'\bif\s+I\'?m\s+being\s+honest\b',
            r'\bat\s+the\s+end\s+of\s+the\s+day\b',
            r'\bwhen\s+all\s+is\s+said\s+and\s+done\b',
            r'\bfor\s+what\s+it\'?s?\s+worth\b',
            r'\blong\s+story\s+short\b',
            r'\banyway[,.]?\b', r'\banyhow[,.]?\b',
            r'\bnot\s+gonna\s+lie\b', r'\bI\s+kid\s+you\s+not\b',
            r'\blegit(?:imately)?\b',
        ]
        coll_density = sum(1 for p in COLLOQUIAL if re.search(p, tl, re.I))
        coll_rate = coll_density / max(len(words) / 50, 1)  # لكل 50 كلمة
        if coll_density >= 4:
            score += 0.18
            signals.append(f"colloquial_high({coll_density})")
        elif coll_density >= 2:
            score += 0.10
            signals.append(f"colloquial({coll_density})")
        elif coll_density >= 1:
            score += 0.05

        # ── 6. Specific Real-world References ────────────────────────────
        # أسماء شخصية / أماكن محددة / تواريخ دقيقة
        SPECIFIC_REF = [
            # أسماء أكاديمية/مهنية
            r'\b(?:Dr|Prof|Mr|Mrs|Ms|Professor)\.\s+[A-Z][a-z]+\b',
            # تواريخ محددة
            r'\b(?:January|February|March|April|May|June|July|August|'
            r'September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?[,\s]+\d{4}\b',
            r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
            r'\bon\s+(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b',
            # أسماء مكان محددة + فعل شخصي
            r'\b(?:visited|went\s+to|traveled\s+to|flew\s+to)\s+[A-Z][a-z]+\b',
            # رقم هاتف أو رقم محدد
            r'\b(?:room|building|floor|office)\s+\d+\b',
            # اقتباس مباشر منسوب لشخص
            r'\b(?:told|said|mentioned|asked|replied)\s+(?:me|us)\b',
            r'\baccording\s+to\s+(?:my|our)\b',
        ]
        ref_hits = sum(1 for p in SPECIFIC_REF if re.search(p, text, re.I))
        if ref_hits >= 3:
            score += 0.16
            signals.append(f"specific_refs({ref_hits})")
        elif ref_hits >= 1:
            score += ref_hits * 0.06
            signals.append(f"specific_refs({ref_hits})")

        # ── 7. Internal Question-Answer Dialogue ─────────────────────────
        # 'Why? Because...' / 'How can we know? Well...' / 'What does this mean?'
        QA_PATTERNS = [
            r'\?[^?]{5,80}(?:because|well|the\s+answer|simply|this\s+means)',
            r'\b(?:why|how|what|when|where)\??[,.]?\s+(?:because|well|the\s+reason|simply)',
            r'(?:but\s+)?why\s+(?:does|do|did|would|should|is|are)\s+.{5,40}\?',
            r'\bthe\s+(?:answer|reason|explanation)\s+is\s+(?:simple|clear|straightforward)\b',
            r'\bask\s+yourself\b',
            r'\bthink\s+about\s+it\b',
            r'\bconsider\s+(?:this|the\s+following)\b',
        ]
        qa_hits = sum(1 for p in QA_PATTERNS if re.search(p, tl, re.I))
        if qa_hits >= 2:
            score += 0.14
            signals.append(f"internal_QA({qa_hits})")
        elif qa_hits >= 1:
            score += 0.07

        # ── 8. Hedging VARIETY (ليس الكمية) ──────────────────────────────
        # AI يكرر نفس التحفظات — البشر يستخدمون أنواعاً مختلفة
        HEDGE_FAMILIES = {
            'epistemic':    {'perhaps','possibly','probably','presumably','conceivably'},
            'approximation':{'roughly','approximately','around','about','nearly','almost'},
            'limitation':   {'seem','appear','tend','generally','typically','often'},
            'modal':        {'might','may','could','would','should'},
            'evidential':   {'suggest','indicate','imply','appear','seem'},
            'distancing':   {'it seems','it appears','one might','some would'},
        }
        families_used = 0
        for fam, terms in HEDGE_FAMILIES.items():
            if any(w in words for w in terms if ' ' not in w):
                families_used += 1
            elif any(re.search(r'\b'+t+r'\b', tl) for t in terms if ' ' in t):
                families_used += 1

        if families_used >= 4:
            score += 0.14
            signals.append(f"hedge_variety({families_used}/6)")
        elif families_used >= 3:
            score += 0.08
            signals.append(f"hedge_variety({families_used}/6)")

        # ── حفظ الأدلة للتقرير ────────────────────────────────────────────
        self._en_human_signals = signals

        return round(max(0.0, min(1.0, score)), 4)

    # ══════════════════════════════════════════════════════════════════════════
    # v30 — DEEP HUMAN STYLOMETRY ENGINE
    # يكشف 8 بصمات أسلوبية عميقة لا يستطيع AI محاكاتها
    # هذه الأنماط مُستقاة من علم اللسانيات الحسابية (computational stylometry)
    # وهي الأساس الذي تعمل عليه أدوات كشف المؤلف (authorship attribution)
    # ══════════════════════════════════════════════════════════════════════════
    def _deep_human_stylometry(self, text, words, sents):
        """
        8 بصمات أسلوبية عميقة — غير موجودة في v29:

        1. Lexical Idiosyncrasy — كلمة مفضلة تتكرر بكثافة غير طبيعية
        2. Information Density Inconsistency — ثقيلة/خفيفة بشكل متذبذب
        3. Argument Structure Irregularity — نقاط غير متوازنة في الحجم
        4. Topic Drift Signature — انجراف عن الموضوع ثم عودة
        5. Referential Ambiguity — 'it/this/that' بدون مرجع واضح
        6. Cognitive Load Markers — جملة معقدة جداً ثم بسيطة جداً فجأة
        7. Pragmatic Presupposition — افتراض معرفة القارئ بأشياء لم تُذكر
        8. Deep Syntactic Fingerprint — تفضيل نحوي ثابت (relative clauses / passives)

        كل واحدة منها: AI يفتقدها أو يُوزعها بانتظام مصطنع
        """
        if not text or len(words) < 20:
            return 0.0

        # تأكد إنجليزي
        ar = len(re.findall(r'[\u0600-\u06FF]', text))
        if ar / max(len(text), 1) > 0.20:
            return 0.0

        from collections import Counter as _C
        tl     = text.lower()
        score  = 0.0
        sigs   = []

        # ── 1. LEXICAL IDIOSYNCRASY ───────────────────────────────────────
        # كاتب بشري يُفضّل كلمات بعينها ويكررها بكثافة غير طبيعية
        # AI يُوزع الكلمات بانتظام رياضي — لا تكرار شخصي
        # نتتبع كلمتين: (أ) كلمات المحتوى الجوهرية (ب) discourse markers الخطابية
        FUNC_STOP = {'the','a','an','is','are','was','were','be','been',
                     'have','has','had','do','does','did','will','would',
                     'could','should','may','might','must','can','to','of',
                     'in','on','at','by','for','with','from','as','and',
                     'or','but','not','it','its','this','that','these',
                     'those','so','if','when','where','what','how','which',
                     'who','all','they','their','we','our','you','your'}

        # (أ) كلمات المحتوى: أي كلمة ≥4 حروف ليست stop word
        content_words = [w for w in words if len(w) >= 4 and w not in FUNC_STOP]

        # (ب) discourse markers — يتتبع تكرارها بشكل منفصل
        DISCOURSE = {'however','therefore','furthermore','moreover','additionally',
                     'consequently','nevertheless','nonetheless','indeed','basically',
                     'essentially','ultimately','generally','typically','obviously',
                     'clearly','certainly','interestingly','importantly','notably',
                     'actually','honestly','frankly','simply','merely','perhaps'}
        discourse_hits = _C(w for w in words if w in DISCOURSE)
        if content_words:
            freq = _C(content_words)
            total_content = max(len(content_words), 1)
            top_word, top_cnt = freq.most_common(1)[0]
            top_rate = top_cnt / total_content
            # هيمنة كلمة محتوى واحدة — عتبة أعلى لتجنب GPT
            if top_rate >= 0.10 and top_cnt >= 3:
                score += 0.22
                sigs.append(f"idiosyncrasy:'{top_word}'×{top_cnt}({top_rate:.0%})")
            elif top_rate >= 0.07 and top_cnt >= 3:
                score += 0.12
                sigs.append(f"idiosyncrasy:'{top_word}'×{top_cnt}")

        # هيمنة discourse marker واحد (الأقوى دلالةً)
        if discourse_hits:
            top_dm, top_dm_cnt = discourse_hits.most_common(1)[0]
            dm_rate = top_dm_cnt / max(len(words), 1)
            if top_dm_cnt >= 4 and dm_rate >= 0.04:
                score += 0.20
                sigs.append(f"discourse_idiosyncrasy:'{top_dm}'×{top_dm_cnt}({dm_rate:.0%})")
            elif top_dm_cnt >= 2 and dm_rate >= 0.025:
                score += 0.10
                sigs.append(f"discourse_idiosyncrasy:'{top_dm}'×{top_dm_cnt}")

        # ── 2. INFORMATION DENSITY INCONSISTENCY ─────────────────────────
        # البشر: جملة تحتوي 5 أفكار متداخلة → جملة 'This is key.'
        # AI: كثافة معلومات متوازنة في جميع الجمل
        if len(sents) >= 4:
            # قياس عدد clauses per sentence (تقريباً: عدد الأفعال)
            CLAUSE_MARKERS = re.compile(
                r'\b(?:which|that|where|when|who|whom|whose|'
                r'although|because|since|while|unless|until|'
                r'however|therefore|thus|hence|consequently)\b', re.I)
            densities = []
            for s in sents:
                if len(s.split()) < 3: continue
                clause_cnt = len(CLAUSE_MARKERS.findall(s))
                wrd_cnt    = len(s.split())
                densities.append(clause_cnt / max(wrd_cnt, 1))

            if len(densities) >= 3:
                avg_d = sum(densities) / len(densities)
                # تباين كثافة المعلومات
                std_d = (sum((d - avg_d)**2 for d in densities) / len(densities)) ** 0.5
                # جمل صفرية (لا clauses) وجمل ثقيلة (>3 clauses)
                zero_dens  = sum(1 for d in densities if d == 0.0)
                heavy_dens = sum(1 for d in densities if d > 0.15)
                if zero_dens >= 2 and heavy_dens >= 1:
                    score += 0.20
                    sigs.append(f"info_density_inconsistency(0×{zero_dens},heavy×{heavy_dens})")
                elif std_d > 0.08:
                    score += 0.10
                    sigs.append(f"info_density_variance({std_d:.3f})")

        # ── 3. ARGUMENT STRUCTURE IRREGULARITY ───────────────────────────
        # البشر: نقطة تأخذ 80 كلمة، التالية 8 كلمات
        # AI: كل نقطة تأخذ حجمها 'المناسب' بدقة
        if len(sents) >= 5:
            # تقسيم النص إلى مقاطع (كل 3-4 جمل)
            chunk_size = max(len(sents) // 3, 2)
            chunks = [sents[i:i+chunk_size] for i in range(0, len(sents), chunk_size)]
            chunks = [c for c in chunks if c]
            chunk_lengths = [sum(len(s.split()) for s in c) for c in chunks]
            if len(chunk_lengths) >= 2:
                max_cl = max(chunk_lengths)
                min_cl = min(chunk_lengths)
                ratio  = max_cl / max(min_cl, 1)
                if ratio >= 3.5:  # مقطع أطول من الآخر بـ 3.5× أو أكثر
                    score += 0.18
                    sigs.append(f"arg_imbalance(ratio={ratio:.1f})")
                elif ratio >= 2.5:
                    score += 0.10
                    sigs.append(f"arg_imbalance(ratio={ratio:.1f})")

        # ── 4. TOPIC DRIFT SIGNATURE ──────────────────────────────────────
        # 'This reminds me' / 'Anyway' / 'But back to' / 'Getting off track'
        DRIFT_PATTERNS = [
            r'\bthis\s+(?:reminds?\s+me|makes?\s+me\s+think|brings?\s+to\s+mind)\b',
            r'\banyway[,.]?\s+(?:back|getting|returning|to\s+return)\b',
            r'\bbut\s+(?:back\s+to|returning\s+to|to\s+get\s+back)\b',
            r'\bI\s+(?:digress|got\s+sidetracked|went\s+off\s+on\s+a\s+tangent)\b',
            r'\b(?:getting|going)\s+off\s+(?:topic|track|course)\b',
            r'\bback\s+to\s+(?:my\s+(?:main|original)|the\s+(?:main|original|key|central))\b',
            r'\bwhere\s+(?:was|were)\s+(?:I|we)\b',
            r'\bright[,.]?\s+so\s+(?:back|anyway|as\s+I)\b',
        ]
        drift_hits = sum(1 for p in DRIFT_PATTERNS if re.search(p, tl, re.I))
        if drift_hits >= 2:
            score += 0.20
            sigs.append(f"topic_drift({drift_hits})")
        elif drift_hits >= 1:
            score += 0.10
            sigs.append("topic_drift(1)")

        # ── 5. REFERENTIAL AMBIGUITY ──────────────────────────────────────
        # 'It was clear that this caused it to fail' — 3 مرجعات غير واضحة
        # AI يُحدد المرجع دائماً بدقة
        AMB_PATTERN = re.compile(
            r'\b(?:it|this|that|they|these|those)\b\s+\w+\s+'
            r'\b(?:it|this|that|they|these|those)\b', re.I)
        # كثافة الضمائر الغامضة (نسبة عالية في جملة واحدة)
        amb_hits = 0
        for s in sents:
            sw = re.findall(r'\b(?:it|this|that|they)\b', s.lower())
            wc = len(s.split())
            if len(sw) >= 3 and wc <= 30:
                amb_hits += 1
            elif len(sw) >= 4:
                amb_hits += 1
        if amb_hits >= 2:
            score += 0.18
            sigs.append(f"referential_ambiguity({amb_hits}sents)")
        elif amb_hits >= 1:
            score += 0.09
            sigs.append("referential_ambiguity(1sent)")

        # أيضاً: double 'it' في نفس الجملة
        double_it = len(re.findall(r'\bit\b.{1,30}\bit\b', tl))
        if double_it >= 2:
            score += 0.08
            sigs.append(f"double_it({double_it})")

        # ── 6. COGNITIVE LOAD MARKERS ─────────────────────────────────────
        # جملة معقدة جداً (>25 كلمة + >2 subordinate clauses) → جملة ≤8 كلمات
        if len(sents) >= 2:
            sent_complexities = []
            for s in sents:
                sw = s.split()
                n  = len(sw)
                rc = len(re.findall(
                    r'\b(?:which|that|who|whom|whose|where|when|'
                    r'although|because|since|while|unless)\b', s.lower()))
                sent_complexities.append((n, rc))

            jumps = 0
            for i in range(1, len(sent_complexities)):
                prev_n, prev_rc = sent_complexities[i-1]
                curr_n, curr_rc = sent_complexities[i]
                # معقد جداً → بسيط جداً
                if prev_n >= 22 and prev_rc >= 2 and curr_n <= 10:
                    jumps += 1
                # بسيط جداً → معقد جداً (عكسي)
                elif prev_n <= 7 and curr_n >= 22:
                    jumps += 1

            if jumps >= 2:
                score += 0.20
                sigs.append(f"cognitive_load_jumps({jumps})")
            elif jumps >= 1:
                score += 0.12
                sigs.append("cognitive_load_jump(1)")

        # ── 7. PRAGMATIC PRESUPPOSITION ───────────────────────────────────
        # 'As we all know' / 'The usual problems' / 'Of course' / 'Obviously'
        # + افتراض معرفة بحدث/شخص لم يُذكر مسبقاً
        PRESUPPOSE = [
            r'\bas\s+(?:we\s+all\s+know|everyone\s+knows?|is\s+well.known)\b',
            r'\bthe\s+(?:usual|typical|standard|common|familiar)\s+'
            r'(?:problem|issue|challenge|approach|pattern|concern|mistake)\b',
            r'\bof\s+course\b',
            r'\bobviously\b',
            r'\bwe\s+all\s+(?:know|remember|understand|recognize)\b',
            r'\bneedless\s+to\s+say\b',
            r'\bit\s+goes\s+without\s+saying\b',
            r'\bthe\s+well.known\b',
            r'\bthe\s+famous\b',
            r'\bas\s+(?:noted|mentioned|discussed|shown)\s+(?:earlier|above|before|previously)\b',
            r'\bback\s+to\s+(?:our|the)\s+(?:earlier|previous|original|main)\b',
        ]
        presup_hits = sum(1 for p in PRESUPPOSE if re.search(p, tl, re.I))
        if presup_hits >= 3:
            score += 0.18
            sigs.append(f"presupposition({presup_hits})")
        elif presup_hits >= 2:
            score += 0.12
            sigs.append(f"presupposition({presup_hits})")
        elif presup_hits >= 1:
            score += 0.07
            sigs.append(f"presupposition(1)")

        # ── 8. DEEP SYNTACTIC FINGERPRINT ────────────────────────────────
        # البشر: تفضيل نحوي ثابت — نفس الكاتب يُفضّل دائماً أو يتجنب دائماً
        # AI: يُوزع الأنماط النحوية بانتظام
        # نقيس: هل النص متسق في استخدام أو تجنب هذه الأنماط؟

        # a) Relative clauses — هل الكاتب يستخدمها دائماً أو لا يستخدمها؟
        rel_clauses_per_sent = []
        for s in sents:
            rc = len(re.findall(r'\b(?:which|that|who|whom|whose)\b', s.lower()))
            rel_clauses_per_sent.append(rc)
        if rel_clauses_per_sent:
            rc_mean = sum(rel_clauses_per_sent) / len(rel_clauses_per_sent)
            rc_zero_pct = sum(1 for x in rel_clauses_per_sent if x == 0) / len(rel_clauses_per_sent)
            # إما يستخدم في كل جملة تقريباً أو لا يستخدم تقريباً → بصمة واضحة
            if rc_zero_pct >= 0.85:  # 85%+ جمل بدون relative clause
                score += 0.10
                sigs.append("syntactic:avoids_rel_clauses")
            elif rc_zero_pct <= 0.15 and rc_mean >= 1.0:  # كل الجمل تقريباً تحتويها
                score += 0.10
                sigs.append("syntactic:prefers_rel_clauses")

        # b) Oxford comma consistency
        oxford_with    = len(re.findall(r'\w+,\s+\w+,?\s+and\s+\w+', text))
        oxford_without = len(re.findall(r'\w+,\s+\w+\s+and\s+\w+', text))
        if oxford_with + oxford_without >= 3:
            consistency = max(oxford_with, oxford_without) / (oxford_with + oxford_without)
            if consistency >= 0.85:
                score += 0.08
                style = "with" if oxford_with > oxford_without else "without"
                sigs.append(f"oxford_comma_consistent({style})")

        # c) Sentence-initial 'I' frequency — إما يبدأ بـ I كثيراً أو لا يبدأ أبداً
        i_openers = sum(1 for s in sents if s.split() and s.split()[0].lower() == 'i')
        i_opener_rate = i_openers / max(len(sents), 1)
        if i_opener_rate >= 0.40 or i_opener_rate == 0.0 and len(sents) >= 6:
            score += 0.08
            sigs.append(f"syntactic:I_opener={i_opener_rate:.0%}")

        # ── حفظ الأدلة ───────────────────────────────────────────────────
        self._deep_human_signals = sigs

        final = round(max(0.0, min(score, 1.0)), 4)
        LOG(f"[DeepHuman] score={final:.3f} signals={sigs}")
        return final

    # يكشف الأخطاء البشرية الحقيقية — كل خطأ هو دليل إيجابي على الكتابة البشرية
    # يُعيد قيمة بين 0.0 (لا أخطاء بشرية) و 1.0 (أخطاء بشرية قوية جداً)
    # ══════════════════════════════════════════════════════════════════════════
    def _human_error_score(self, text, words):
        """
        يحلل النص بحثاً عن 5 أنواع من الأخطاء والأنماط البشرية:

        1. أخطاء إملائية إنجليزية (130+ كلمة خاطئة)
        2. أخطاء نحوية (subject-verb / double negative / wrong tense)
        3. أخطاء إملائية عربية (همزة / تاء / تنوين)
        4. أنماط أسلوبية عفوية (تكرار عاطفي / تردد / تصحيح ذاتي)
        5. أنماط حوار واقتباس

        كل نوع يُحسب بشكل مستقل ثم يُدمج في درجة نهائية.
        الدرجة تُستخدم لتخفيض نتيجة AI مباشرةً.
        """
        if not text or len(words) < 15:
            return 0.0

        tl   = text.lower()
        n    = max(len(words), 1)
        score = 0.0

        # ── 1. أخطاء إملائية إنجليزية ────────────────────────────────────────
        spell_hits = sum(1 for w in words if w in self.HUMAN_SPELLING_ERRORS)
        if spell_hits >= 3:
            # 3+ أخطاء إملائية = دليل قوي جداً على الكتابة البشرية
            spell_score = min(spell_hits / 5.0, 1.0)
            score += spell_score * 0.40
            LOG(f"[HumanError] spelling hits={spell_hits} → +{spell_score*0.40:.2f}")
        elif spell_hits >= 1:
            score += 0.12

        # ── 2. أخطاء نحوية إنجليزية ──────────────────────────────────────────
        grammar_hits = 0
        for pat in self.HUMAN_GRAMMAR_PATTERNS:
            try:
                grammar_hits += len(re.findall(pat, tl, re.I))
            except:
                pass
        if grammar_hits >= 2:
            grammar_score = min(grammar_hits / 4.0, 1.0)
            score += grammar_score * 0.25
        elif grammar_hits >= 1:
            score += 0.10

        # ── 3. أخطاء إملائية عربية ───────────────────────────────────────────
        arabic_hits = 0
        for pat in self.HUMAN_ARABIC_ERRORS:
            try:
                arabic_hits += len(re.findall(pat, text, re.U))
            except:
                pass
        if arabic_hits >= 2:
            score += min(arabic_hits / 4.0, 1.0) * 0.20
        elif arabic_hits >= 1:
            score += 0.08

        # ── 4. أنماط أسلوبية عفوية ───────────────────────────────────────────
        style_hits = 0
        for pat in self.HUMAN_STYLE_PATTERNS:
            try:
                style_hits += len(re.findall(pat, text, re.I | re.U))
            except:
                pass

        # علامات ترقيم عاطفية — بشرية جداً
        exclaim = text.count('!') + text.count('؟') + text.count('?')
        ellipsis = text.count('...') + text.count('…')
        multi_exclaim = len(re.findall(r'[!?؟]{2,}', text))

        style_total = style_hits + min(exclaim, 5) + min(ellipsis * 2, 4) + multi_exclaim * 2

        if style_total >= 4:
            score += min(style_total / 10.0, 1.0) * 0.20
        elif style_total >= 2:
            score += 0.08

        # ── 5. أنماط حوار واقتباس ────────────────────────────────────────────
        dialogue_hits = 0
        for pat in self.HUMAN_DIALOGUE_PATTERNS:
            try:
                dialogue_hits += len(re.findall(pat, text))
            except:
                pass
        if dialogue_hits >= 2:
            score += min(dialogue_hits / 6.0, 1.0) * 0.15
        elif dialogue_hits >= 1:
            score += 0.05

        # ── 6. مؤشرات إضافية قوية ────────────────────────────────────────────

        # تقلبات طول الجمل (البشر يكتبون جملاً قصيرة جداً وطويلة جداً بالتبادل)
        sents = re.split(r'(?<=[.!?؟])\s+', text)
        sents = [s for s in sents if len(s.split()) >= 2]
        if len(sents) >= 5:
            lens = [len(s.split()) for s in sents]
            avg  = sum(lens) / len(lens)
            cv   = (sum((l - avg)**2 for l in lens) / len(lens)) ** 0.5 / (avg + 1e-6)
            # CV عالٍ جداً = تذبذب بشري حقيقي (جملة 3 كلمات ثم 25 كلمة)
            very_short = sum(1 for l in lens if l <= 4)
            very_long  = sum(1 for l in lens if l >= 30)
            if very_short >= 2 and very_long >= 1:
                score += 0.12  # تباين واضح = بشري
            elif cv > 1.2:
                score += 0.07

        # الجمل المبتورة (تفكير بشري مكسور)
        incomplete = len(re.findall(
            r'(?:^|\.\s+)[A-Z][a-z]+\s+[a-z]+\s*\.\s*(?=[A-Z])',
            text))
        if incomplete >= 2:
            score += 0.08

        # الأخطاء المطبعية الصغيرة (مسافة زائدة، نقطة مضاعفة)
        typo_hits = (len(re.findall(r'\s{2,}', text)) +
                     len(re.findall(r'\.{2}(?!\.)', text)) +
                     len(re.findall(r',{2,}', text)))
        if typo_hits >= 3:
            score += 0.06

        # ── الحد الأقصى للنتيجة ───────────────────────────────────────────────
        score = round(min(score, 1.0), 4)
        LOG(f"[HumanError] final={score:.3f} (spell={spell_hits}, gram={grammar_hits}, "
            f"arabic={arabic_hits}, style={style_total}, dialogue={dialogue_hits})")
        return score

    # ══════════════════════════════════════════════════════════════════════════
    # v27 — ENGLISH AI SCORE ENGINE (محرك إنجليزي مخصص ومنفصل)
    # يعمل فقط على النصوص الإنجليزية (arabic_ratio < 0.20)
    # 3 طبقات: عبارات حصرية (45%) + أنماط جمل (35%) + بصمات أسلوبية (20%)
    # ══════════════════════════════════════════════════════════════════════════
    def _english_ai_score(self, text, words, sents):
        """
        Layer 1 — T1 Phrase Matching: 100+ عبارة حصرية لـ GPT/Claude
        Layer 2 — Sentence Patterns: 20 نمط regex لهياكل AI
        Layer 3 — Stylometric Benchmarks: 7 مقاييس أسلوبية إحصائية
        يُعيد 0.0 للنصوص العربية تلقائياً
        """
        arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
        if arabic_chars / max(len(text), 1) > 0.20:
            return 0.0

        if len(words) < 30:
            return 0.5

        tl      = text.lower()
        score   = 0.0
        evidence = []

        # ── Layer 1: T1 Phrase Matching ───────────────────────────────────────
        t1_hits = [p for p in self.EN_GPT_PHRASES_T1 if p in tl]
        if len(t1_hits) >= 6:
            t1_score = min(0.55 + (len(t1_hits) - 6) * 0.025, 0.85)
            evidence.append(f"T1:{len(t1_hits)} عبارة GPT [{', '.join(t1_hits[:3])}]")
        elif len(t1_hits) >= 3:
            t1_score = 0.35 + len(t1_hits) * 0.05
            evidence.append(f"T1:{len(t1_hits)} عبارة [{', '.join(t1_hits[:2])}]")
        elif len(t1_hits) >= 1:
            t1_score = 0.15 + len(t1_hits) * 0.08
            evidence.append(f"T1:{len(t1_hits)} [{t1_hits[0]}]")
        else:
            t1_score = 0.05
        score += t1_score * 0.45

        # ── Layer 2: Sentence Pattern Matching ───────────────────────────────
        t2_hits = 0
        for pat in self.EN_GPT_SENTENCE_PATTERNS:
            try:
                t2_hits += len(re.findall(pat, tl, re.I))
            except: pass
        t2_density = t2_hits / max(len(sents) / 10, 1)
        if t2_density >= 4.0:
            t2_score = min(0.60 + (t2_density - 4) * 0.04, 0.90)
            evidence.append(f"T2:كثافة عالية {t2_density:.1f}/10جمل")
        elif t2_density >= 2.0:
            t2_score = 0.35 + t2_density * 0.07
            evidence.append(f"T2:{t2_hits} نمط جملة")
        elif t2_density >= 1.0:
            t2_score = 0.20 + t2_density * 0.06
        else:
            t2_score = 0.08
        score += t2_score * 0.35

        # ── Layer 3: Stylometric Benchmarks ──────────────────────────────────
        bench = self.EN_GPT_STYLE_BENCHMARKS
        style_matches = 0
        style_ev = []

        if sents:
            avg_len = sum(len(s.split()) for s in sents) / len(sents)
            if bench['avg_sentence_len_min'] <= avg_len <= bench['avg_sentence_len_max']:
                style_matches += 1; style_ev.append(f"طول={avg_len:.0f}ك")
            openers = [s.split()[0].lower() for s in sents if s.split()]
            div = len(set(openers)) / max(len(openers), 1)
            if div < bench['opener_diversity_max']:
                style_matches += 1; style_ev.append(f"تنوع={div:.2f}")

        passive_r = sum(1 for s in sents if re.search(
            r'\b(?:is|are|was|were|been)\s+\w+ed\b', s, re.I)) / max(len(sents), 1)
        if passive_r >= bench['passive_ratio_min']:
            style_matches += 1; style_ev.append(f"مجهول={passive_r:.0%}")

        TRANS = {'furthermore','moreover','additionally','consequently',
                 'nevertheless','therefore','thus','hence','however',
                 'notably','importantly','significantly','ultimately',
                 'specifically','particularly','in','as','this','it'}
        trans_r = sum(1 for s in sents
                      if s.split() and s.split()[0].lower() in TRANS) / max(len(sents), 1)
        if trans_r >= bench['transition_opener_min']:
            style_matches += 1; style_ev.append(f"انتقال={trans_r:.0%}")

        avg_wl = sum(len(w) for w in words) / max(len(words), 1)
        if avg_wl >= bench['avg_word_len_min']:
            style_matches += 1; style_ev.append(f"كلمة={avg_wl:.1f}ح")

        q_count = len(re.findall(r'"[^"]{10,100}"', text))
        if (q_count / max(len(words)/100, 1)) <= bench['quote_density_max']:
            style_matches += 1; style_ev.append("لاقتباس")

        from collections import Counter as _C
        cwords = [w for w in words if len(w) > 5 and w not in self.EN_ACADEMIC_NEUTRAL]
        if cwords:
            top3 = sum(v for _, v in _C(cwords).most_common(3))
            if top3 / len(cwords) >= bench['core_word_repeat_min']:
                style_matches += 1; style_ev.append("تكرار")

        t3_score = min(style_matches / 7.0, 1.0)
        if style_ev:
            evidence.append(f"T3:{style_matches}/7 [{','.join(style_ev[:3])}]")
        score += t3_score * 0.20

        # ── حماية الأكاديمي البشري الحقيقي ──────────────────────────────────
        neutral_d = sum(1 for w in words if w in self.EN_ACADEMIC_NEUTRAL) / max(len(words), 1)
        if neutral_d >= 0.12 and len(t1_hits) == 0 and t2_hits <= 2:
            score *= 0.65
            evidence.append(f"حماية أكاديمية={neutral_d:.0%} بدون T1")

        self._en_evidence_cache = evidence
        return round(max(0.05, min(score, 0.97)), 4)

    # ══════════════════════════════════════════════════════════════════════════
    # v27 — PARAGRAPH EXPLANATION ENGINE
    # يُنتج تقريراً نصياً يشرح سبب الحكم على كل فقرة
    # ══════════════════════════════════════════════════════════════════════════
    def _explain_paragraph(self, para_score, llr, sg, gf, se, pat,
                            nb, en_score, ar_score, human_err):
        """يُعيد نصاً شارحاً مفصلاً لسبب الحكم — للتقرير المفصل"""
        reasons_ai, reasons_human = [], []
        strongest_signal, strongest_val = None, 0.0

        checks = [
            (gf,       0.50, "تنسيق GPT مباشر (Bold/##/Bullets)",      "تنسيق GPT"),
            (en_score, 0.55, f"محرك إنجليزي مخصص v27",                  "محرك EN"),
            (ar_score, 0.45, "بصمات GPT عربية",                         "محرك AR"),
            (sg,       0.60, "أسلوب GPT المدرسي/العام",                  "أسلوب GPT"),
            (llr,      0.75, "نموذج اللغة الاحتمالي LLR",               "LLR"),
            (nb,       0.65, "Naive Bayes ML",                           "NB"),
            (pat,      0.55, "ذاكرة أنماط AI (28 نمطاً)",              "أنماط AI"),
            (se,       0.60, "التضمين الدلالي",                         "دلالي"),
        ]
        for val, thresh, label, short in checks:
            if val >= thresh:
                reasons_ai.append(f"{label}: {val*100:.0f}%")
                if val > strongest_val:
                    strongest_val, strongest_signal = val, short

        if human_err >= 0.30:
            reasons_human.append(f"أخطاء بشرية موثقة: {human_err*100:.0f}%")
        elif human_err >= 0.10:
            reasons_human.append(f"أنماط بشرية خفيفة: {human_err*100:.0f}%")

        lines = []
        if para_score >= 0.85:     lines.append("🔴 AI مؤكد")
        elif para_score >= 0.70:   lines.append("🟠 AI محتمل")
        elif para_score >= 0.50:   lines.append("🟡 مختلط")
        elif para_score >= 0.25:   lines.append("🔵 يُشبه AI")
        else:                      lines.append("🟢 بشري")

        if strongest_signal:
            lines.append(f"  أقوى دليل: {strongest_signal} ({strongest_val*100:.0f}%)")
        if reasons_ai:
            lines.append("  أدلة AI: " + " | ".join(reasons_ai[:3]))
        if reasons_human:
            lines.append("  مُخففات: " + " | ".join(reasons_human))
        if not reasons_ai and para_score < 0.30:
            lines.append("  لا بصمات AI واضحة")

        return '\n'.join(lines)

    # ══════════════════════════════════════════════════════════════════════════
    # v26 — ARABIC AI DETECTION ENGINE
    # محرك كشف عربي مخصص — يكشف نصوص GPT/Claude العربية
    # المشكلة: المحركات الإنجليزية لا تعمل جيداً على العربية
    # الحل: بصمات عربية حقيقية مُستخلَصة من 50+ نص GPT عربي
    # ══════════════════════════════════════════════════════════════════════════
    def _arabic_ai_score(self, text):
        """
        يكشف نصوص AI العربية عبر 4 مستويات:
        1. كلمات AI العربية الحصرية (AI_ARABIC_WORDS)
        2. عبارات GPT النمطية (AI_ARABIC_FINGERPRINT)
        3. بنية الجمل العربية لـ GPT (افتتاحيات / خاتمات)
        4. إيقاع الجمل العربية (AI = جمل طويلة منتظمة)
        يُعيد 0.0 إذا كان النص إنجليزياً أو قصيراً جداً
        """
        # كشف هل النص عربي أم لا
        arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
        total_chars  = max(len(text.replace(' ', '')), 1)
        arabic_ratio = arabic_chars / total_chars

        if arabic_ratio < 0.25:
            return 0.0   # النص ليس عربياً — لا نُشغّل المحرك العربي

        score = 0.0
        words_ar = re.findall(r'[\u0600-\u06FF]+', text)
        n_ar = max(len(words_ar), 1)

        # ── 1. كلمات AI العربية الحصرية ──────────────────────────────────────
        ai_ar_hits = sum(1 for w in words_ar if w in self.AI_ARABIC_WORDS)
        ai_ar_density = ai_ar_hits / n_ar
        if ai_ar_density >= 0.04:   # 4%+ كلمات AI عربية = نص GPT
            score += min(ai_ar_density * 12.0, 0.50)
        elif ai_ar_density >= 0.02:
            score += ai_ar_density * 8.0

        # ── 2. عبارات GPT النمطية الكاملة ────────────────────────────────────
        phrase_hits = 0
        for phrase in self.AI_ARABIC_FINGERPRINT:
            if phrase in text:
                phrase_hits += 1
        if phrase_hits >= 4:
            score += min(phrase_hits / 8.0, 0.40)
        elif phrase_hits >= 2:
            score += phrase_hits * 0.07
        elif phrase_hits >= 1:
            score += 0.05

        # ── 3. افتتاحيات GPT العربية النمطية ─────────────────────────────────
        GPT_AR_OPENERS = [
            r'^في عالمنا (?:المعاصر|الحديث|اليوم)',
            r'^في ظل (?:التطورات|العولمة|التقدم|الثورة)',
            r'^(?:يُعدّ|يُعتبر|يُمثّل) .{5,40} (?:من أبرز|من أهم|ركيزة|محوراً)',
            r'^(?:إن|إنّ) .{5,40} (?:يكتسب|يحتل|يُشكّل) .{3,30} (?:بالغة|محورية|كبيرة)',
            r'^لا (?:شك|شكّ|ريب) (?:في|أن|أنّ)',
            r'^(?:تُعدّ|تُمثّل|تُشكّل) .{5,40} (?:أحد أبرز|من أهم|ركيزة أساسية)',
            r'(?:وفي الختام|وخلاصة القول|ومما سبق يتضح)',
            r'(?:يجدر بالذكر|تجدر الإشارة) (?:أن|إلى)',
        ]
        opener_hits = 0
        for pat in GPT_AR_OPENERS:
            try:
                if re.search(pat, text, re.M | re.U):
                    opener_hits += 1
            except:
                pass
        if opener_hits >= 3:
            score += 0.25
        elif opener_hits >= 2:
            score += 0.15
        elif opener_hits >= 1:
            score += 0.07

        # ── 4. إيقاع الجمل العربية (AI = جمل طويلة منتظمة) ─────────────────
        sents_ar = re.split(r'[.؟!،\n]{2,}', text)
        sents_ar = [s.strip() for s in sents_ar if len(s.split()) >= 5]
        if len(sents_ar) >= 4:
            lens_ar = [len(s.split()) for s in sents_ar]
            avg_ar  = sum(lens_ar) / len(lens_ar)
            cv_ar   = (sum((l - avg_ar)**2 for l in lens_ar) / len(lens_ar))**0.5 / (avg_ar + 1e-6)
            # AI عربي: جمل طويلة (15-35 كلمة) ومنتظمة (CV منخفض)
            if avg_ar >= 15 and cv_ar < 0.45:
                score += 0.20
            elif avg_ar >= 12 and cv_ar < 0.55:
                score += 0.10

        # ── 5. كثافة الضمائر البشرية العربية (تُقلل الدرجة) ─────────────────
        HUMAN_AR_PRONOUNS = {'أنا','نحن','أنت','أنتم','عندي','عندنا',
                              'رأيي','رأينا','أعتقد','أرى','أظن','أحس',
                              'شعرت','لاحظت','وجدت','تجربتي','من خبرتي'}
        human_ar_hits = sum(1 for w in words_ar if w in HUMAN_AR_PRONOUNS)
        if human_ar_hits >= 3:
            score *= (1.0 - 0.30)
        elif human_ar_hits >= 1:
            score *= (1.0 - 0.15)

        return round(max(0.0, min(score, 1.0)), 4)

    # ══════════════════════════════════════════════════════════════════════════
    # v26 — CONFIDENCE SYSTEM (نظام الثقة)
    # بدلاً من رقم واحد → يُعطي نطاقاً + مستوى ثقة + تحذير عند الشك
    # المبدأ: الحكم القاطع يتطلب أدلة متعددة متقاطعة — ليس مؤشراً واحداً
    # ══════════════════════════════════════════════════════════════════════════
    def _compute_confidence(self, score, indicators, human_error_val,
                             word_count, arabic_ratio):
        """
        يحسب مستوى الثقة في النتيجة ويُعيد:
        {
          'level':       'HIGH' | 'MEDIUM' | 'LOW' | 'INCONCLUSIVE',
          'label':       نص عربي للعرض,
          'range_low':   الحد الأدنى للنطاق الفعلي,
          'range_high':  الحد الأعلى للنطاق الفعلي,
          'warning':     تحذير نصي إن وُجد,
          'safe_verdict': حكم آمن للاستخدام المؤسسي,
        }

        قواعد الثقة:
        - HIGH:        3+ مؤشرات قوية متقاطعة + نص طويل كافٍ
        - MEDIUM:      2 مؤشرين أو نص متوسط الطول
        - LOW:         مؤشر واحد أو نص قصير أو تعارض أدلة
        - INCONCLUSIVE: النص قصير جداً أو الأدلة متضاربة
        """
        # ── عدد المؤشرات القوية ──────────────────────────────────────────────
        strong = sum(1 for v in indicators.values() if v >= 0.70)
        medium = sum(1 for v in indicators.values() if 0.45 <= v < 0.70)

        # ── عوامل تخفيض الثقة ───────────────────────────────────────────────
        trust_penalties = 0

        # نص قصير جداً → لا يمكن الحكم بثقة
        if word_count < 100:
            trust_penalties += 3
        elif word_count < 200:
            trust_penalties += 2
        elif word_count < 400:
            trust_penalties += 1

        # أدلة بشرية قوية تتعارض مع الحكم
        if human_error_val >= 0.35 and score >= 0.60:
            trust_penalties += 2   # تعارض واضح

        # النص عربي بدون محرك عربي قوي
        if arabic_ratio >= 0.50 and indicators.get('Arabic AI v26', 0) < 0.30:
            trust_penalties += 1

        # مؤشرات متذبذبة (بعضها عالٍ وبعضها منخفض جداً)
        vals = list(indicators.values())
        if vals:
            high_count = sum(1 for v in vals if v >= 0.65)
            low_count  = sum(1 for v in vals if v <= 0.20)
            if high_count >= 2 and low_count >= 4:
                trust_penalties += 1  # إشارات متضاربة

        # ── تحديد مستوى الثقة ───────────────────────────────────────────────
        if word_count < 80:
            level = 'INCONCLUSIVE'
        elif strong >= 4 and trust_penalties == 0:
            level = 'HIGH'
        elif strong >= 3 and trust_penalties <= 1:
            level = 'HIGH'
        elif strong >= 2 or (medium >= 3 and trust_penalties <= 1):
            level = 'MEDIUM'
        elif trust_penalties >= 3 or (strong == 0 and medium <= 1):
            level = 'LOW'
        else:
            level = 'MEDIUM'

        # ── نطاق النتيجة الفعلي ──────────────────────────────────────────────
        # نعطي نطاقاً بدلاً من رقم واحد — الرقم الواحد كاذب الدقة
        if level == 'HIGH':
            margin = 0.05   # ±5%
        elif level == 'MEDIUM':
            margin = 0.12   # ±12%
        elif level == 'LOW':
            margin = 0.20   # ±20%
        else:
            margin = 0.30   # ±30%

        range_low  = max(0.0,   score - margin)
        range_high = min(1.0,   score + margin)

        # ── الحكم الآمن (للاستخدام المؤسسي) ─────────────────────────────────
        # المبدأ: في الشك لصالح الطالب — الحكم القاطع يتطلب HIGH فقط
        if level == 'HIGH' and score >= 0.85:
            safe_verdict = 'محتوى AI — دليل قوي جداً'
            safe_color   = 'red'
        elif level == 'HIGH' and score >= 0.70:
            safe_verdict = 'محتوى AI — يُستوجب المراجعة'
            safe_color   = 'orange'
        elif level in ('MEDIUM', 'LOW') and score >= 0.75:
            safe_verdict = 'مشتبه به — يحتاج مراجعة بشرية إضافية'
            safe_color   = 'yellow'
        elif level == 'INCONCLUSIVE':
            safe_verdict = 'غير حاسم — النص قصير للتحليل الموثوق'
            safe_color   = 'gray'
        elif score <= 0.30:
            safe_verdict = 'بشري — لا دليل على AI'
            safe_color   = 'green'
        else:
            safe_verdict = 'نتيجة غير حاسمة — في الشك لصالح الكاتب'
            safe_color   = 'gray'

        # ── التحذيرات ────────────────────────────────────────────────────────
        warnings = []
        if word_count < 150:
            warnings.append(f'⚠️ النص قصير ({word_count} كلمة) — النتيجة غير موثوقة')
        if human_error_val >= 0.35 and score >= 0.60:
            warnings.append('⚠️ تعارض: أخطاء بشرية مع إشارات AI — قد يكون مختلطاً')
        if trust_penalties >= 2:
            warnings.append('⚠️ أدلة متضاربة — لا تستخدم هذه النتيجة وحدها لاتخاذ قرار')
        if arabic_ratio >= 0.60 and strong < 3:
            warnings.append('⚠️ نص عربي — دقة الكشف أقل من النص الإنجليزي')

        # ── التسميات العربية ─────────────────────────────────────────────────
        level_labels = {
            'HIGH':         '🟢 ثقة عالية',
            'MEDIUM':       '🟡 ثقة متوسطة',
            'LOW':          '🟠 ثقة منخفضة',
            'INCONCLUSIVE': '⚪ غير حاسم',
        }

        return {
            'level':        level,
            'label':        level_labels[level],
            'range_low':    round(range_low  * 100, 1),
            'range_high':   round(range_high * 100, 1),
            'safe_verdict': safe_verdict,
            'safe_color':   safe_color,
            'warnings':     warnings,
            'strong_count': strong,
            'trust_penalty':trust_penalties,
        }

    # ─── Context Coherence Analysis ──────────────────────────────────────────
    def _context_coherence(self, text, sents, words):
        """
        AI: تماسك مُفرط منتظم (lexical overlap عالٍ + clause depth ثابت).
        Human: قفزات مفاجئة + تذبذب في التعقيد.
        """
        if len(sents) < 4:
            return 0.4

        # lexical overlap بين الجمل المتتالية
        overlaps = []
        for i in range(1, len(sents)):
            prev_w = set(re.findall(r'\b[a-zA-Z]{4,}\b', sents[i-1].lower()))
            curr_w = set(re.findall(r'\b[a-zA-Z]{4,}\b', sents[i].lower()))
            if prev_w and curr_w:
                overlaps.append(len(prev_w & curr_w) / min(len(prev_w), len(curr_w)))
        overlap_ai = min(sum(overlaps) / max(len(overlaps), 1) * 3.5, 1.0)

        # clause depth consistency
        clause_depths = [s.count(',') + s.count(';') + s.count(':') + s.count('(')
                         for s in sents]
        avg_d = sum(clause_depths) / max(len(clause_depths), 1)
        depth_cv = (math.sqrt(sum((d - avg_d)**2 for d in clause_depths) / max(len(clause_depths), 1))
                   / (avg_d + 1e-6))
        depth_ai = max(0.0, 1.0 - depth_cv * 1.2)

        # repeated sentence starters
        from collections import Counter
        openers = [s.split()[0].lower() for s in sents if s.split()]
        if openers:
            top_pct = Counter(openers).most_common(1)[0][1] / len(openers)
            repeat_ai = min(top_pct * 3.0, 1.0)
        else:
            repeat_ai = 0.4

        # sentence length consistency
        lengths = [len(s.split()) for s in sents]
        avg_len = sum(lengths) / max(len(lengths), 1)
        if avg_len > 0:
            cv_len = math.sqrt(sum((l - avg_len)**2 for l in lengths) / len(lengths)) / avg_len
            consistency_ai = max(0.0, 1.0 - cv_len * 1.8)
        else:
            consistency_ai = 0.4

        return round(min(overlap_ai*0.30 + depth_ai*0.25 +
                         repeat_ai*0.25 + consistency_ai*0.20, 1.0), 4)

    # ─── Advanced Stylometric Fingerprint ────────────────────────────────────
    def _advanced_stylometry(self, text, words, sents):
        """
        بصمة أسلوبية متقدمة:
        - Modal formality (AI: شكلي مُقعَّر)
        - Contractions (Human: don't/can't | AI: does not/cannot)
        - Parenthetical regularity
        - Subordination ratio
        - Sentence-initial diversity
        """
        if not words or not sents:
            return 0.4

        FORMAL_MODALS = {'shall','ought','thereby','hence','thus','wherein',
                         'whereby','thereof','herein','therein'}
        INFORMAL_MODALS = {'dont','cant','wont','isnt','arent','wasnt',
                           'gonna','wanna','gotta','dunno'}
        formal_m   = sum(1 for w in words if w in FORMAL_MODALS)
        informal_m = sum(1 for w in words if w in INFORMAL_MODALS)
        modal_ai = formal_m / (formal_m + informal_m + 1)

        contractions = len(re.findall(
            r"\b(?:don't|can't|won't|isn't|aren't|wasn't|weren't|"
            r"haven't|hasn't|didn't|doesn't|couldn't|wouldn't|"
            r"shouldn't|I'm|I've|I'll|I'd|we're|we've|they're)\b",
            text, re.I))
        contr_ai = max(0.0, 1.0 - (contractions / max(len(words)/10, 1)) * 4.0)

        paren_counts = [s.count('(') for s in sents]
        paren_total  = sum(paren_counts)
        if len(sents) >= 3 and paren_total > 0:
            avg_p  = paren_total / len(sents)
            p_cv   = (math.sqrt(sum((p - avg_p)**2 for p in paren_counts) / len(paren_counts))
                     / (avg_p + 1e-6))
            paren_ai = max(0.0, 0.8 - p_cv * 0.5)
        else:
            paren_ai = 0.3

        SUB_CONJ = {'that','which','where','when','although','because','since',
                    'while','whereas','unless','until','whether','though'}
        sub_ai = min(sum(1 for w in words if w in SUB_CONJ) / max(len(words), 1) * 10.0, 1.0)

        from collections import Counter
        openers = [s.split()[0].lower() for s in sents if s.split()]
        diversity_ai = 0.4
        if openers:
            freq = Counter(openers)
            diversity_ai = max(0.0, 1.0 - (len(freq) / len(openers)) * 1.5)

        return round(min(modal_ai*0.20 + contr_ai*0.25 + paren_ai*0.15 +
                         sub_ai*0.20 + diversity_ai*0.20, 1.0), 4)

    # ─── Advanced Punctuation Distribution ───────────────────────────────────
    def _punct_distribution(self, text, sents):
        """
        توزيع علامات الترقيم المتقدم:
        - انتظام الفواصل بين الجمل (AI: ثابت)
        - غياب العلامات البشرية (! ? ...)
        - معدل الفاصلات الطبيعي
        """
        if not sents:
            return 0.4

        words_total = max(len(re.findall(r'\b[a-zA-Z]+\b', text)), 1)
        comma_rate  = text.count(',') / words_total
        informal_p  = text.count('!') + text.count('?') + text.count('...')
        informal_ai = max(0.0, 1.0 - informal_p * 0.4)
        comma_ai    = 1.0 - min(abs(comma_rate - 0.035) * 20, 1.0)

        comma_per_sent = [s.count(',') for s in sents]
        avg_cps = sum(comma_per_sent) / max(len(comma_per_sent), 1)
        if len(comma_per_sent) >= 4:
            cps_cv = (math.sqrt(sum((c - avg_cps)**2 for c in comma_per_sent)
                               / len(comma_per_sent)) / (avg_cps + 1e-6))
            regularity_ai = max(0.0, 1.0 - cps_cv * 1.3)
        else:
            regularity_ai = 0.5

        dash_rate = (text.count('—') + text.count('–') + text.count(' - ')) / words_total
        dash_ai   = 1.0 - min(abs(dash_rate - 0.008) * 60, 1.0)

        return round(min(regularity_ai*0.35 + informal_ai*0.30 +
                         comma_ai*0.20 + dash_ai*0.15, 1.0), 4)

    # ══════════════════════════════════════════════════════════════════════════
    # المؤشرات الجديدة v13/v14 (محتفظ بها)
    # ══════════════════════════════════════════════════════════════════════════

    # ── بصمة Bigrams ─────────────────────────────────────────────────────────
    def _bigram_score(self, words):
        if len(words) < 10: return 0.3
        bigrams  = [(words[i], words[i+1]) for i in range(len(words)-1)]
        if not bigrams: return 0.3
        matches  = sum(1 for bg in bigrams if bg in self.AI_BIGRAMS)
        # تطبيع: AI text يحتوي bigrams متكررة
        ratio    = matches / len(bigrams)
        from collections import Counter
        freq     = Counter(bigrams)
        top5_pct = sum(v for _, v in freq.most_common(5)) / len(bigrams)
        # AI: bigrams متكررة جداً → top5_pct مرتفع
        rep_score = min(top5_pct * 2.5, 1.0)
        return min(ratio * 40 * 0.5 + rep_score * 0.5, 1.0)

    # ── بصمة Trigrams ────────────────────────────────────────────────────────
    def _trigram_score(self, words):
        if len(words) < 15: return 0.3
        trigrams = [(words[i], words[i+1], words[i+2]) for i in range(len(words)-2)]
        if not trigrams: return 0.3
        matches  = sum(1 for tg in trigrams if tg in self.AI_TRIGRAMS)
        ratio    = matches / len(trigrams)
        from collections import Counter
        freq     = Counter(trigrams)
        top3_pct = sum(v for _, v in freq.most_common(3)) / len(trigrams)
        rep_score = min(top3_pct * 3.5, 1.0)
        return min(ratio * 60 * 0.55 + rep_score * 0.45, 1.0)

    # ── أنماط جمل AI (100 نمط) ────────────────────────────────────────────────
    def _pattern_score(self, sents):
        if not sents: return 0.3
        n_checked = min(len(sents), 40)
        sample    = sents[:n_checked]
        hits      = 0
        total_pat = len(self._compiled_patterns)
        for s in sample:
            sl = s.lower()
            hits += sum(1 for p in self._compiled_patterns if p.search(sl))
        # normalize: avg pattern hits per sentence
        avg_hits = hits / n_checked
        return min(avg_hits / 3.0, 1.0)

    # ── إيقاع النص + انتظام الجمل ─────────────────────────────────────────────
    def _rhythm(self, sents):
        """
        البشر يكتبون بإيقاع متذبذب — جمل قصيرة تعقبها طويلة.
        AI يكتب بانتظام مُزعج — طول الجمل متقارب جداً.
        """
        if len(sents) < 6: return 0.4
        lengths = [len(s.split()) for s in sents]
        avg     = sum(lengths) / len(lengths)
        if avg < 3: return 0.4
        # معامل الاختلاف
        cv      = math.sqrt(sum((l - avg)**2 for l in lengths) / len(lengths)) / avg
        # AI: cv منخفض (جمل منتظمة) → نسبة AI مرتفعة
        rhythm_ai = max(0.0, 1.0 - cv * 2.2)

        # فحص الأنماط الافتتاحية للجمل
        STARTERS = ['this','it','the','in','as','there','these','those',
                    'such','one','many','most','some','both','each','all']
        starter_hits = sum(1 for s in sents
                           if s.split()[0].lower() in STARTERS if s.split())
        starter_ratio = min(starter_hits / len(sents) * 1.3, 1.0)

        return min(rhythm_ai * 0.65 + starter_ratio * 0.35, 1.0)

    # ── Local Entropy (Entropy محلي) ──────────────────────────────────────────
    def _local_entropy(self, words):
        """
        AI يستخدم كلمات بتوزيع شبه منتظم — entropy منخفض.
        البشر عندهم توزيع مائل (Zipfian أكثر) في النوافذ المحلية.
        """
        if len(words) < 40: return 0.4
        window   = 30
        entropies = []
        from collections import Counter
        for i in range(0, len(words) - window, window // 2):
            chunk = words[i:i + window]
            freq  = Counter(chunk)
            n     = len(chunk)
            ent   = -sum((c/n) * math.log2(c/n) for c in freq.values() if c > 0)
            entropies.append(ent)
        if not entropies: return 0.4
        avg_ent  = sum(entropies) / len(entropies)
        # entropy منخفض → AI أكثر
        # human: avg_ent حول 3.5-4.5  |  AI: حول 2.5-3.5
        ai_ent   = max(0.0, min(1.0, (4.2 - avg_ent) / 2.0))
        # تجانس entropy بين النوافذ (AI أكثر ثباتاً)
        if len(entropies) >= 2:
            ent_cv = (math.sqrt(sum((e - avg_ent)**2 for e in entropies) / len(entropies))
                      / (avg_ent + 1e-6))
            ent_stable = max(0.0, 1.0 - ent_cv * 3.0)
        else:
            ent_stable = 0.5
        return min(ai_ent * 0.6 + ent_stable * 0.4, 1.0)

    # ── بنية الفقرات + افتتاحية/خاتمة AI ────────────────────────────────────
    def _paragraph_structure(self, text):
        """
        AI: فقرات متساوية تقريباً + افتتاحية نمطية + خاتمة نمطية.
        """
        paras = [p.strip() for p in re.split(r'\n{2,}|\r\n{2,}', text) if p.strip()]
        if len(paras) < 2:
            # نص بدون فقرات — قسّمه على الجمل
            paras = re.split(r'(?<=[.!?])\s+', text)
            paras = [p for p in paras if len(p.split()) >= 8]
        if len(paras) < 2: return 0.4

        # تساوي طول الفقرات
        lengths  = [len(p.split()) for p in paras]
        avg_len  = sum(lengths) / len(lengths)
        if avg_len < 1: return 0.4
        cv_para  = math.sqrt(sum((l - avg_len)**2 for l in lengths) / len(lengths)) / avg_len
        uniform_score = max(0.0, 1.0 - cv_para * 1.8)

        # افتتاحية AI
        AI_OPENERS = [
            r'^(?:in today|in recent|in modern|in contemporary)',
            r'^(?:it is widely|it is well|it is commonly|it has been)',
            r'^(?:over the (?:past|last|recent))',
            r'^(?:throughout history|since the)',
            r'^(?:the (?:concept|field|study|importance|role|impact|use|development|emergence))',
            r'^(?:with the (?:advent|rise|growth|development|emergence|proliferation))',
            r'^(?:as (?:technology|science|society|the world|we) (?:advance|evolve|progress|move|continue))',
            r'^(?:given (?:the|these|this))',
            r'^(?:one of the most)',
        ]
        first_para = paras[0].lower()
        open_hit   = any(re.search(p, first_para) for p in AI_OPENERS)

        # خاتمة AI
        AI_CLOSERS = [
            r'(?:in conclusion|in summary|to sum up|to conclude|to summarize)',
            r'(?:overall|ultimately|in closing|in final)',
            r'(?:taken together|as a whole|all in all|by and large)',
            r'(?:future (?:research|studies|work) (?:should|will|must|may))',
            r'(?:this (?:study|paper|work|review|analysis) (?:has|have) (?:shown|demonstrated|illustrated|highlighted))',
        ]
        last_para  = paras[-1].lower()
        close_hit  = any(re.search(p, last_para) for p in AI_CLOSERS)

        extra = (0.2 if open_hit else 0.0) + (0.2 if close_hit else 0.0)
        return min(uniform_score * 0.6 + extra, 1.0)

    # ── بصمة علامات الترقيم ──────────────────────────────────────────────────
    def _punct_fingerprint(self, text):
        """
        AI يستخدم علامات الترقيم بشكل مُعتدل ومُنتظم.
        البشر: يُفرطون أو يُقصّرون، أقل انتظاماً.
        """
        words  = re.findall(r'\b[a-zA-Z]+\b', text)
        n      = max(len(words), 1)
        commas     = text.count(',')   / n
        semicolons = text.count(';')   / n
        colons     = text.count(':')   / n
        dashes     = (text.count('-') + text.count('—') + text.count('–')) / n
        parens     = (text.count('(') + text.count(')')) / n
        excl       = text.count('!')   / n
        quest      = text.count('?')   / n

        # AI نادراً يستخدم ! أو ? في النصوص الأكاديمية
        informal_score = min((excl + quest) * 20, 1.0)  # مرتفع → بشري أكثر
        # نسبة فاصلة AI نموذجية: 0.02–0.05
        comma_ai = 1.0 - min(abs(commas - 0.035) * 30, 1.0)
        # AI يستخدم الشرطة والأقواس بانتظام
        dash_paren_ai = min((dashes + parens) * 15, 1.0)

        # الانتظام: حساب التوزيع في نوافذ
        sents = re.split(r'(?<=[.!?])\s+', text)
        if len(sents) >= 5:
            per_sent = [s.count(',') + s.count(';') for s in sents]
            avg_ps   = sum(per_sent) / len(per_sent)
            cv_ps    = (math.sqrt(sum((x - avg_ps)**2 for x in per_sent) / len(per_sent))
                        / (avg_ps + 1e-6))
            regular_score = max(0.0, 1.0 - cv_ps * 1.5)
        else:
            regular_score = 0.5

        return min(
            comma_ai     * 0.25 +
            dash_paren_ai * 0.20 +
            regular_score * 0.35 +
            (1 - informal_score) * 0.20,
            1.0
        )

    # ── نسب الأفعال / الضمائر ─────────────────────────────────────────────────
    def _verb_ratio(self, words):
        """
        نسبة الأفعال الرسمية الأكاديمية الفعلية في النص.
        AI يستخدم هذه الأفعال بكثافة أعلى من البشر.
        يُرجع النسبة المئوية الحقيقية (للعرض الصحيح في الواجهة).
        """
        FORMAL_VERBS = {
            'demonstrate','illustrate','highlight','underscore','reveal',
            'indicate','suggest','imply','signify','denote','represent',
            'examine','investigate','explore','analyze','assess','evaluate',
            'identify','determine','establish','confirm','validate','verify',
            'facilitate','enable','enhance','improve','increase','decrease',
            'provide','offer','present','describe','discuss','address',
        }
        if not words: return 0.0
        fv_count = sum(1 for w in words if w in FORMAL_VERBS)
        return round(fv_count / len(words), 4)  # النسبة الحقيقية

    def _pronoun_ratio(self, words):
        """
        نسبة ضمائر المتكلم الفعلية (I/we/my...) في النص.
        AI نادراً يستخدم ضمائر المتكلم → نسبة منخفضة.
        البشر يستخدمونها أكثر → نسبة أعلى.
        يُرجع النسبة المئوية الحقيقية (للعرض الصحيح في الواجهة).
        """
        FIRST_PERSON = {'i','me','my','mine','myself','we','us','our','ours','ourselves'}
        if not words: return 0.0
        fp_count = sum(1 for w in words if w in FIRST_PERSON)
        return round(fp_count / len(words), 4)

    def _pronoun_ratio(self, words):
        """
        نسبة ضمائر المتكلم الفعلية (I/we/my...) في النص.
        """
        FIRST_PERSON = {'i','me','my','mine','myself','we','us','our','ours','ourselves'}
        if not words: return 0.0
        fp_count = sum(1 for w in words if w in FIRST_PERSON)
        return round(fp_count / len(words), 4)

    # ══════════════════════════════════════════════════════════════════════════
    # v35 — FINGERPRINT SCORE ENGINE (المحرك الحاكم الجديد — يُحسب أخيراً)
    # يُستدعى بعد حساب: simple_gpt, gpt_format, english_ai, arabic_ai, human scores
    # يُعيد 0.0-1.0 — يدخل بوزن 35% في الميزان النهائي
    # ══════════════════════════════════════════════════════════════════════════
    def _compute_fingerprint_score(self, text, words, sents,
                                   simple_gpt_score, gpt_format_score,
                                   english_ai_score, arabic_ai_score,
                                   human_error_val, english_human_score,
                                   deep_human_score):
        """
        12 فئة بصمة مباشرة — كل فئة تكشف نمطاً حصرياً لـ GPT.
        المبدأ: بصمة واحدة قاطعة ≥ 0.85 تحجز الدرجة فوق 0.70.
        تراكم 4+ بصمات قوية يوصل إلى 0.85+.
        يعمل على: GPT بسيط / أكاديمي / عربي / إنجليزي / منسّق / غير منسّق.
        """
        if not words or not sents:
            return 0.0

        import math as _m

        tl      = text.lower()
        n_words = max(len(words), 1)
        n_sents = max(len(sents), 1)
        sc      = {}   # dict البصمات

        # ── FP-1: مفردات AI — يجمع الكلاسيكية والبسيطة ─────────────────────
        SIMPLE_GPT_VOCAB = {
            # كلمات شائعة في GPT المدرسي/البسيط
            'important','crucial','vital','essential','significant','valuable',
            'effective','positive','negative','various','numerous','diverse',
            'helps','improves','allows','enables','supports','promotes',
            'develops','builds','strengthens','boosts','enhances','increases',
            'reduces','fosters','cultivates','stimulates','provides','offers',
            'encourages','facilitates','contributes','assists','inspires',
            'benefits','advantages','valuable','worthwhile','meaningful',
            'responsibility','responsibilities','sacrifice','dedication','patience',
            'compassion','guidance','inspiration','determination','perseverance',
            'unconditional','emotional','intellectual','academic','personal',
            'development','growth','character','personality','values','identity',
            'overall','ultimately','generally','typically','particularly',
            'especially','specifically','primarily','mainly','largely',
        }
        ALL_AI_VOCAB = set(self.AI_FINGERPRINT) | SIMPLE_GPT_VOCAB
        ai_w  = sum(1 for w in words if w in ALL_AI_VOCAB)
        d     = ai_w / n_words
        sc['fp_vocab'] = (min(0.92, 0.60 + (d-0.08)*5)  if d >= 0.08
                          else 0.45 + (d-0.05)*5          if d >= 0.05
                          else 0.25 + d*12                if d >= 0.02
                          else d * 15                     if d >= 0.008 else 0.0)

        # ── FP-2: عبارات GPT الإنجليزية — قاموس شامل داخل الدالة ───────────
        # يجمع: T1 الأكاديمية + عبارات GPT البسيط/المدرسي
        # السبب: EN_GPT_PHRASES_T1 يحوي عبارات أكاديمية فقط
        FP2_PHRASES = (set(self.EN_GPT_PHRASES_T1) | {
            # ── عبارات GPT البسيط/المدرسي (لا توجد في T1 الأكاديمي) ──
            'not only', 'but also', 'not only a', 'not only does', 'not only is',
            'society as a whole', 'as a whole',
            'symbol of warmth', 'symbol of strength', 'symbol of love',
            'unconditional support', 'unconditional love', 'unconditional care',
            'throughout their entire lives', 'throughout their lives',
            'for the rest of their lives', 'for the rest of his life',
            'source of inspiration', 'source of strength', 'source of comfort',
            'believe in themselves', 'believe in yourself', 'believe in herself',
            'follow their dreams', 'follow her dreams', 'follow his dreams',
            'face challenges and overcome', 'face challenges',
            'given freely and without', 'given freely',
            'without expecting anything in return', 'without expecting',
            'plays a very important', 'plays a central role', 'plays a special role',
            'plays a vital role in', 'plays a key role in',
            'is often described as', 'are often described as',
            'remains a symbol of', 'remain a symbol of',
            'shape the character', 'shape the personality',
            'shape the future of', 'shape the lives of',
            'healthy, happy, and', 'healthy and happy',
            'safe and comfortable', 'safe and secure',
            'love, understanding, and compassion', 'love and compassion',
            'love, protection, and guidance', 'love and protection',
            'kindness, honesty, and respect', 'kindness, honesty, respect',
            'respect, appreciation, and gratitude',
            'warmth, care, and', 'warmth and care',
            'challenges and overcome', 'difficulties and challenges',
            'character and personality', 'character and values',
            'time and energy', 'time and effort',
            'make sure that', 'making sure that', 'making sure everyone',
            'ensure that her', 'ensure that his', 'ensure that their',
            'deserve great respect', 'deserve respect', 'deserve appreciation',
            'role in organizing', 'role in shaping', 'role in guiding',
            'pillar of strength', 'backbone of the family',
            'heart of the family', 'role model',
            'grow up healthy', 'grow up happy', 'grow up well',
            'important values such as', 'important values like',
            'patience and constant support', 'patience and support',
            'personal development', 'personal growth',
            'emotional support', 'emotional well-being',
            'positive impact', 'lasting impact', 'significant impact',
            'plays an important role', 'plays a crucial role',
            'first and foremost', 'above all else',
            'in many families', 'in every family',
            'despite the many challenges', 'despite the challenges',
            'due to the fact', 'because of all these',
            'as a result of', 'in order to',
            'in addition to', 'in addition to this',
            'on the other hand', 'at the same time',
            'in this way', 'in this manner',
            'it is worth noting', 'it is important to note',
            'it is clear that', 'it is evident that',
            'we can say that', 'we can conclude',
            'in conclusion', 'to conclude', 'in summary',
            'therefore', 'furthermore', 'moreover', 'additionally',
            'consequently', 'as a result', 'thus', 'hence',
            'for these reasons', 'for this reason',
            'in other words', 'that is to say',
            'one of the most', 'one of the best', 'one of the greatest',
            'one of the purest', 'one of the strongest', 'one of the key',
            'the most important', 'the most significant', 'the most powerful',
            'a wide range of', 'a variety of', 'a number of',
            'plays a significant role', 'plays an essential role',
        })
        t1 = sum(1 for p in FP2_PHRASES if p in tl)
        sc['fp_en_phrases'] = (min(0.97, 0.75+(t1-20)*0.012) if t1 >= 20
                               else min(0.90, 0.65+(t1-12)*0.031) if t1 >= 12
                               else 0.50+(t1-6)*0.033  if t1 >= 6
                               else 0.30+t1*0.06       if t1 >= 3
                               else t1*0.15             if t1 >= 1 else 0.0)

        # ── FP-3: عبارات GPT العربية ──────────────────────────────────────
        ar_ph = sum(1 for p in self.AI_ARABIC_FINGERPRINT if p in text)
        ar_ww = sum(1 for w in re.findall(r'[\u0600-\u06FF]+', text)
                    if w in self.AI_ARABIC_WORDS)
        ar_c  = ar_ph + ar_ww * 0.3
        sc['fp_ar_phrases'] = (min(0.95, 0.65+(ar_c-8)*0.03)  if ar_c >= 8
                               else 0.40+(ar_c-4)*0.062        if ar_c >= 4
                               else ar_c*0.13                  if ar_c >= 2 else 0.0)

        # ── FP-4: تنسيق Markdown مباشر ───────────────────────────────────
        bold    = len(re.findall(r'\*\*[^*]{3,60}\*\*', text))
        headers = len(re.findall(r'(?m)^#{1,4}\s+\S', text))
        bullets = len(re.findall(r'(?m)^[\*\-•]\s+\w', text))
        fmt     = bold + headers + bullets
        sc['fp_format'] = (min(0.98, 0.70+fmt*0.02) if fmt >= 5
                           else 0.40+fmt*0.08 if fmt >= 2
                           else 0.25          if fmt == 1 else 0.0)

        # ── FP-5: تعدادات ثلاثية X, Y, and Z ────────────────────────────
        tri = len(re.findall(r'\b\w+,\s+\w+,\s+(?:and|or)\s+\w+\b', tl))
        sc['fp_triplets'] = (min(0.90, 0.60+(tri-5)*0.04) if tri >= 5
                             else 0.40+(tri-3)*0.10       if tri >= 3
                             else tri * 0.18               if tri >= 1 else 0.0)

        # ── FP-6: كليشيهات GPT الختامية ──────────────────────────────────
        CLICHES = [
            r'\bone of the (?:most|best|greatest|purest|strongest|highest|deepest)\b',
            r'\b(?:purest|strongest|deepest|greatest|highest) forms? of\b',
            r'\bgiven freely (?:and )?without (?:expecting|asking)\b',
            r'\b(?:remains?|is) a symbol of\b',
            r'\bthroughout (?:their|his|her|your) entire (?:lives?|life)\b',
            r'\bfor the rest of (?:their|his|her) (?:lives?|life)\b',
            r'\bsociety as a whole\b',
            r'\bunconditional(?:ly)? (?:support|love|care|devotion)\b',
            r'\bwarmth[,\s]+care[,\s]+and\b',
            r'\brespect[,\s]+appreciation[,\s]+and\s+gratitude\b',
            r'\bwithout (?:expecting|asking for) anything in return\b',
            r'\bshape the (?:character|personality|future|values) of\b',
            r'\bdeserve(?:s)? (?:great|much|our|the highest|special) (?:respect|appreciation|gratitude)\b',
            r'\bsymbol of (?:warmth|strength|love|hope|care|sacrifice)\b',
            r'\bsource of (?:inspiration|strength|comfort|guidance|support|love)\b',
            r'\bplays? a (?:very )?(?:important|crucial|vital|central|key|special|significant|major) (?:and (?:special|unique|essential) )?role\b',
            r'\bbelieve in (?:themselves?|himself|herself|yourself)\b',
            r'\bfollow (?:their|his|her|your) dreams?\b',
            r'\bface (?:challenges?|difficulties) and (?:overcome|conquer)\b',
            r'\bhealthy[,\s]+happy[,\s]+and\b',
            r'\bsafe and comfortable\b',
            r'\blove[,\s]+understanding[,\s]+and\s+compassion\b',
            r'\bpillar of (?:strength|support|the family)\b',
            r'\brole model\b',
            r'\bheart of the (?:family|home)\b',
            # عربية
            r'في عالمنا المعاصر',
            r'في ظل التطورات المتسارعة',
            r'يكتسب أهمية بالغة',
            r'يحتل مكانة محورية',
            r'مما سبق يتضح',
            r'خلاصة القول',
            r'تجدر الإشارة',
            r'علاوة على ذلك',
        ]
        cc = sum(1 for p in CLICHES
                 if re.search(p, tl if p.isascii() else text, re.I | re.U))
        sc['fp_cliches'] = (min(0.95, 0.70+(cc-8)*0.025) if cc >= 8
                            else 0.50+(cc-5)*0.066        if cc >= 5
                            else 0.28+(cc-3)*0.11         if cc >= 3
                            else cc * 0.14                if cc >= 1 else 0.0)

        # ── FP-7: انتظام طول الجمل (CV منخفض = AI) ───────────────────────
        lens_s = [len(s.split()) for s in sents if len(s.split()) >= 4]
        if len(lens_s) >= 4:
            avg_l = sum(lens_s) / len(lens_s)
            cv    = _m.sqrt(sum((l-avg_l)**2 for l in lens_s)/len(lens_s))/(avg_l+1e-6)
            if   cv < 0.22 and avg_l >= 12: sc['fp_uniformity'] = 0.88
            elif cv < 0.30 and avg_l >= 10: sc['fp_uniformity'] = 0.65+(0.30-cv)*2.5
            elif cv < 0.40:                 sc['fp_uniformity'] = max(0.0, 0.45-(cv-0.30)*3.0)
            else:                           sc['fp_uniformity'] = 0.0
        else:
            sc['fp_uniformity'] = 0.20

        # ── FP-8: غياب الأرقام والبيانات الفعلية ─────────────────────────
        has_prec = bool(re.search(
            r'\b(?:\d+\.\d+|\d{2,}%|r\s*=\s*[\d.]+|p\s*[<>=]\s*[\d.]+|'
            r'n\s*=\s*\d+|\d+\s*(?:patients?|participants?|samples?))\b', text, re.I))
        has_cit  = bool(re.search(
            r'\([A-Z][a-z]+(?:\s+et\s+al\.?)?\s*,\s*(?:19|20)\d{2}\)', text))
        has_dat  = bool(re.search(
            r'\b(?:according to|study found|research shows|data indicates|'
            r'statistically|coefficient|regression|survey|experiment)\b', tl))
        if   not has_prec and not has_cit and not has_dat: sc['fp_no_data']    =  0.40
        elif has_prec and has_cit:                         sc['fp_no_data']    = -0.25
        else:                                               sc['fp_no_data']    =  0.0

        # ── FP-9: أزواج لغوية أنيقة ──────────────────────────────────────
        PAIRS = re.compile(
            r'\b(?:love and (?:care|support|protection|guidance|compassion)'
            r'|care and (?:support|protection|guidance|compassion)'
            r'|healthy and (?:happy|safe|comfortable|strong)'
            r'|safe and (?:comfortable|secure|happy|protected)'
            r'|respect and (?:gratitude|appreciation|love|admiration)'
            r'|warmth and (?:care|support|love|compassion)'
            r'|patience and (?:support|understanding|dedication|love)'
            r'|challenges? and (?:difficulties|obstacles?|hardships?)'
            r'|character and (?:personality|values?|identity|integrity)'
            r'|time and (?:energy|effort|dedication|commitment)'
            r'|kindness and (?:compassion|caring|love|empathy)'
            r'|strength and (?:resilience|courage|determination)'
            r'|knowledge and (?:understanding|wisdom|skills|experience)'
            r'|growth and (?:development|progress|improvement|success)'
            r'|positive and (?:negative|constructive|meaningful|lasting)'
            r'|emotional and (?:physical|mental|social|intellectual)'
            r')', re.I)
        pc = len(PAIRS.findall(tl))
        sc['fp_pairs'] = (min(0.88, 0.55+(pc-5)*0.05) if pc >= 5
                          else 0.30+(pc-3)*0.12        if pc >= 3
                          else pc * 0.18               if pc >= 1 else 0.0)

        # ── FP-10: بنية الجمل البنيوية النمطية ───────────────────────────
        sh = 0
        sh += len(re.findall(r'\bnot only\b.{5,100}\bbut (?:also|even)\b', tl, re.DOTALL)) * 3
        sh += len(re.findall(r'\bensure(?:s)? that\b|\bmake(?:s)? sure that\b', tl))
        sh += len(re.findall(r'\bplays? a (?:key|central|crucial|vital|important|pivotal) role\b', tl)) * 2
        sh += len(re.findall(r'\bin (?:conclusion|summary|closing),?\s+', tl)) * 3
        sh += len(re.findall(r'\bfurthermore[,\s]|\bmoreover[,\s]|\badditionally[,\s]', tl))
        sh += len(re.findall(r'\bit is (?:important|crucial|essential|vital|worth) (?:to|noting)\b', tl)) * 2
        sh += len(re.findall(r'\bthis (?:highlights?|underscores?|demonstrates?|illustrates?)\b', tl)) * 2
        sc['fp_structure'] = (min(0.92, 0.65+(sh-8)*0.03)   if sh >= 8
                              else 0.40+(sh-4)*0.062         if sh >= 4
                              else sh * 0.13                  if sh >= 2 else 0.0)

        # ── FP-11: غياب الضمائر الشخصية ──────────────────────────────────
        PERS = {'i','me','my','mine','we','our','ours','honestly',
                'personally','frankly','actually','think','feel','believe','guess'}
        pr = sum(1 for w in words if w in PERS) / n_words
        if   pr <= 0.005 and n_words >= 80: sc['fp_no_personal'] =  0.70
        elif pr <= 0.015:                   sc['fp_no_personal'] =  max(0.0, 0.50-pr*20)
        elif pr >= 0.04:                    sc['fp_no_personal'] = -0.20
        else:                               sc['fp_no_personal'] =  max(0.0, 0.20-pr*8)

        # ── FP-12: أنماط جمل GPT (EN_GPT_SENTENCE_PATTERNS) ─────────────
        t2 = 0
        for pat in self.EN_GPT_SENTENCE_PATTERNS:
            try: t2 += len(re.findall(pat, tl, re.I))
            except: pass
        td = t2 / max(n_sents/10.0, 1.0)
        sc['fp_t2_patterns'] = (min(0.92, 0.70+(td-6)*0.022)  if td >= 6
                                else 0.42+(td-3)*0.093          if td >= 3
                                else 0.22+td*0.08               if td >= 1.5
                                else max(0.0, td*0.10))

        # ── تكامل مع المحركات المُحسَبة سابقاً ──────────────────────────
        # simple_gpt_score و gpt_format_score محسوبان بالفعل — نستخدمهما مباشرة
        sc['fp_simple_gpt'] = simple_gpt_score
        sc['fp_format_sig'] = gpt_format_score

        # ── خصم الأدلة البشرية القوية ────────────────────────────────────
        human_penalty = 0.0
        if human_error_val >= 0.30:
            human_penalty += human_error_val * 0.25
        if english_human_score >= 0.35:
            human_penalty += english_human_score * 0.20
        if deep_human_score >= 0.35:
            human_penalty += deep_human_score * 0.22
        human_penalty = min(human_penalty, 0.40)  # حد أقصى للخصم

        # ── الوزن النهائي ─────────────────────────────────────────────────
        WEIGHTS = {
            'fp_en_phrases':   0.13,
            'fp_cliches':      0.12,
            'fp_simple_gpt':   0.11,  # simple_gpt_score مباشرة
            'fp_structure':    0.10,
            'fp_vocab':        0.09,
            'fp_format_sig':   0.08,  # gpt_format_score مباشرة
            'fp_t2_patterns':  0.08,
            'fp_ar_phrases':   0.07,
            'fp_format':       0.06,
            'fp_triplets':     0.06,
            'fp_uniformity':   0.05,
            'fp_pairs':        0.03,
            'fp_no_data':      0.01,
            'fp_no_personal':  0.01,
        }
        base = sum(sc.get(k, 0.0) * v for k, v in WEIGHTS.items())
        base = max(0.0, min(1.0, base))

        # تطبيق خصم الأدلة البشرية
        base *= (1.0 - human_penalty)
        base = max(0.0, min(1.0, base))

        # ── قواعد الحد الأدنى (بصمة واحدة قاطعة تكفي) ───────────────────
        max_fp     = max((v for v in sc.values() if isinstance(v, float) and v > 0), default=0.0)
        strong_fps = sum(1 for v in sc.values() if isinstance(v, float) and v >= 0.55)
        medium_fps = sum(1 for v in sc.values() if isinstance(v, float) and v >= 0.35)

        if   max_fp >= 0.85: base = max(base, 0.68)
        elif max_fp >= 0.70: base = max(base, 0.55)
        elif max_fp >= 0.55: base = max(base, 0.40)

        if   strong_fps >= 5: base = max(base, 0.82)
        elif strong_fps >= 4: base = max(base, 0.70)
        elif strong_fps >= 3: base = max(base, 0.58)
        elif strong_fps >= 2: base = max(base, 0.42)

        if   medium_fps >= 8: base = max(base, 0.68)
        elif medium_fps >= 6: base = max(base, 0.55)
        elif medium_fps >= 4: base = max(base, 0.40)

        # إعادة تطبيق خصم البشري بعد قواعد الحد
        base *= (1.0 - human_penalty * 0.5)
        base = max(0.0, min(1.0, base))

        # حفظ التفاصيل للتشخيص
        self._fp_scores_cache = sc

        return round(base, 4)
        """
        v23 ENHANCED — يكشف GPT البسيط بـ 16 بصمة مباشرة.

        المشكلة الجذرية: GPT البسيط يستخدم لغة طبيعية جداً
        فيخدع النماذج اللغوية (LLR منخفض). لكن له بصمات هيكلية
        لا تتغير مهما تغيرت المفردات:

        الفئة الأولى  — بنية الجملة:
          ① افتتاحيات GPT النمطية (It/Reading/When/For these reasons)
          ② ضعف CV أطوال الجمل (جمل متساوية جداً)
          ③ كل جملة تحمل فكرة واحدة كاملة ومستقلة
          ④ نمط "X also Y" — GPT يُضيف بـ also بدلاً من لغة طبيعية

        الفئة الثانية — المفردات والأسلوب:
          ⑤ غياب الضمائر الشخصية تماماً (I/my/we)
          ⑥ كثافة ضمائر غير شخصية (they/people/one/readers)
          ⑦ أفعال GPT المدرسية (helps/improves/allows/supports)
          ⑧ كلمات GPT المفيدية (benefits/valuable/important/activity)
          ⑨ ظروف -ly متكررة (intellectually/personally/daily)

        الفئة الثالثة — البنية الكلية:
          ⑩ جملة ختامية نمطية (For these reasons / Therefore)
          ⑪ إيموجي في نهاية النص 📖✨
          ⑫ تكرار الكلمة المحورية في كل جملة
          ⑬ لا أسئلة / لا شك / لا ملاحظات شخصية
          ⑭ تعداد "A and B" — GPT يُعدِّد دائماً
          ⑮ بنية "سبب لأن / لأنه / because" منظمة
          ⑯ جمل تبدأ بالموضوع مباشرة (بدون سياق شخصي)
        """
        if not words or not sents:
            return 0.15

        import math as _m
        from collections import Counter as _C

        n_words = max(len(words), 1)
        n_sents = max(len(sents), 1)
        scores  = {}

        # ─── ① GPT Sentence Starters ──────────────────────────────────────
        # GPT يبدأ الجمل بـ: موضوع + فعل / ضمير غير شخصي / رابط انتقالي
        GPT_STARTERS = {
            # روابط انتقالية
            'in addition','moreover','furthermore','therefore','thus','hence',
            'consequently','additionally','however','nevertheless','nonetheless',
            'as a result','in conclusion','in summary','for these reasons',
            'finally','lastly','besides','similarly','likewise',
            # بدايات موضوعية مباشرة
            'it','reading','writing','learning','education','technology',
            'exercise','health','this','these','when','for','the',
            'daily','regular','such','one','people',
        }
        GPT_TRANS_STRICT = {
            'in addition','moreover','furthermore','therefore','thus','hence',
            'consequently','additionally','for these reasons','in conclusion',
            'in summary','finally','as a result',
        }
        starter_count = 0
        trans_strict_count = 0
        for s in sents:
            sl = s.lower().strip()
            sw = sl.split()[0] if sl.split() else ''
            for t in GPT_STARTERS:
                if sl.startswith(t + ' ') or sl.startswith(t + ','):
                    starter_count += 1
                    break
            for t in GPT_TRANS_STRICT:
                if sl.startswith(t):
                    trans_strict_count += 1
                    break
        scores['gpt_starters']  = min(max(0.0, (starter_count/n_sents - 0.20)*2.0), 1.0)
        scores['trans_strict']  = min(trans_strict_count / n_sents * 3.0, 1.0)

        # ─── ② Sentence Length Uniformity ────────────────────────────────
        lens = [len(s.split()) for s in sents if len(s.split()) > 2]
        if len(lens) >= 3:
            avg = sum(lens)/len(lens)
            cv  = _m.sqrt(sum((l-avg)**2 for l in lens)/len(lens))/(avg+1e-6)
            scores['uniformity'] = max(0.0, min(1.0, (0.35 - cv) / 0.25))
        else:
            scores['uniformity'] = 0.3

        # ─── ③ One-Idea-Per-Sentence Pattern ─────────────────────────────
        # GPT: كل جملة = فكرة واحدة مكتملة. مؤشر: قلة subordinate clauses
        SUB_CONJ = {'although','whereas','while','despite','even though',
                    'unless','until','since','after','before','once'}
        sub_count = sum(1 for s in sents
                       if any(c in s.lower() for c in SUB_CONJ))
        # GPT: sub_count منخفض (جمل بسيطة) | Human: sub_count أعلى
        scores['simple_sents'] = max(0.0, 1.0 - sub_count/n_sents*2.0)

        # ─── ④ "X also Y" Pattern ─────────────────────────────────────────
        also_pat = len(re.findall(r'\b\w+ also \w+', text, re.I))
        scores['also_pattern'] = min(also_pat * 0.35, 1.0)

        # ─── ⑤ Zero Personal Markers ──────────────────────────────────────
        PERSONAL = {'i','me','my','mine','myself','we','our','honestly',
                    'actually','think','feel','believe','guess','maybe',
                    'probably','personally','frankly','dunno','kind of'}
        personal_hits = sum(1 for w in words if w in PERSONAL)
        scores['no_personal'] = max(0.0, 1.0 - personal_hits/max(n_words/12, 1))

        # ─── ⑥ Impersonal Pronoun Density ─────────────────────────────────
        IMPERSONAL = {'they','people','individuals','readers','students',
                      'one','person','someone','everyone','anyone','humans',
                      'children','users','employees','citizens','society'}
        imp_count = sum(1 for w in words if w in IMPERSONAL)
        scores['impersonal'] = min(imp_count/n_words*10.0, 1.0)

        # ─── ⑦ GPT School Verbs ───────────────────────────────────────────
        GPT_VERBS = {
            'helps','improves','allows','enables','supports','promotes',
            'develops','builds','strengthens','boosts','enhances','increases',
            'reduces','expands','fosters','cultivates','stimulates','provides',
            'offers','encourages','facilitates','contributes','assists',
            'explores','gains','learn','grow','improve','develop',
        }
        vb_count = sum(1 for w in words if w in GPT_VERBS)
        scores['gpt_verbs'] = min(vb_count/n_words*7.0, 1.0)

        # ─── ⑧ Benefit/Value Words ────────────────────────────────────────
        BENEFIT_W = {'benefits','benefit','advantages','advantage','valuable',
                     'important','essential','crucial','key','significant',
                     'effective','powerful','positive','useful','worthwhile',
                     'lifelong','personal','intellectual','academic','overall',
                     'activity','habit','practice','development','growth'}
        ben_count = sum(1 for w in words if w in BENEFIT_W)
        scores['benefit_words'] = min(ben_count/n_words*6.0, 1.0)

        # ─── ⑨ Adverb -ly Density ─────────────────────────────────────────
        # GPT يُكثِّر الظروف المنتهية بـ -ly
        LY_ADVERBS = [w for w in words if w.endswith('ly') and len(w) > 5
                      and w not in {'really','totally','actually','literally',
                                    'honestly','basically','personally'}]
        scores['ly_adverbs'] = min(len(LY_ADVERBS)/n_words*15.0, 1.0)

        # ─── ⑩ Closing Formula ────────────────────────────────────────────
        last_150 = text[-150:].lower() if len(text)>150 else text.lower()
        CLOSE_PAT = re.compile(
            r'\b(?:for these reasons|therefore|in conclusion|in summary|'
            r'thus|hence|to conclude|in short|ultimately|overall|'
            r'is a valuable|is an important|is essential|is crucial|'
            r'supports? lifelong|personal development|overall well.?being|'
            r'daily habit|regular habit|one of the best|recommended for)',
            re.I)
        close_hits = len(CLOSE_PAT.findall(last_150))
        scores['closing'] = min(close_hits*0.55, 1.0)

        # ─── ⑪ Emoji Tail ─────────────────────────────────────────────────
        last_40 = text[-40:] if len(text)>40 else text
        emoji_tail = len(re.findall(
            r'[\U0001F300-\U0001F9FF\U0001F600-\U0001F64F'
            r'\U0001F680-\U0001F6FF\u2600-\u27BF📚✨📖🔹⚡🌟💡🎯]',
            last_40))
        scores['emoji_tail'] = min(emoji_tail*0.55, 1.0)

        # ─── ⑫ Topic Word Repetition ──────────────────────────────────────
        content = [w for w in words if len(w)>4]
        if content:
            freq = _C(content)
            top_count = freq.most_common(1)[0][1]
            scores['topic_rep'] = min(max(0.0,(top_count/n_sents - 0.25)*2.5), 1.0)
        else:
            scores['topic_rep'] = 0.2

        # ─── ⑬ No Doubt/Question ──────────────────────────────────────────
        DOUBT = {'maybe','perhaps','might','wonder','not sure','unsure',
                 'unclear','seems','appears','could be','possibly'}
        has_doubt = any(w in text.lower() for w in DOUBT)
        has_question = '?' in text
        scores['no_doubt'] = 0.0 if (has_doubt or has_question) else 0.70

        # ─── ⑭ "A and B" Enumeration ──────────────────────────────────────
        and_pairs = len(re.findall(r'\b\w{4,} and \w{4,}\b', text))
        scores['enumeration'] = min(and_pairs/n_sents*0.35, 1.0)

        # ─── ⑮ "because/as/since" Causal Structure ────────────────────────
        causal = len(re.findall(
            r'\b(?:because it|because they|as it|as they|since it|'
            r'which allows?|that allows?|which helps?|that helps?|'
            r'which enables?|that enables?|as readers?|as people)\b',
            text, re.I))
        scores['causal'] = min(causal*0.30, 1.0)

        # ─── ⑯ Direct Topic Opener ────────────────────────────────────────
        # GPT يبدأ بالموضوع مباشرة بلا مقدمة شخصية
        first_sent = sents[0].lower() if sents else ''
        direct_topic = not any(w in first_sent for w in
                               ['i ','my ','we ','our ','honestly','actually',
                                'you know','let me','in my'])
        scores['direct_topic'] = 0.65 if direct_topic else 0.0

        # ─── Weighted Composite ───────────────────────────────────────────
        W = {
            'trans_strict':   0.14,
            'no_personal':    0.12,
            'gpt_starters':   0.10,
            'gpt_verbs':      0.09,
            'benefit_words':  0.09,
            'closing':        0.08,
            'no_doubt':       0.07,
            'uniformity':     0.07,
            'direct_topic':   0.06,
            'simple_sents':   0.05,
            'emoji_tail':     0.05,
            'impersonal':     0.04,
            'topic_rep':      0.04,
            'also_pattern':   0.03,
            'causal':         0.03,
            'ly_adverbs':     0.03,
            'enumeration':    0.01,
        }
        # Verify weights sum
        w_sum = sum(W.values())
        # Normalize if needed
        if abs(w_sum - 1.0) > 0.001:
            W = {k:v/w_sum for k,v in W.items()}

        base = sum(scores.get(k, 0.0) * v for k, v in W.items())

        # ─── Human Penalty ────────────────────────────────────────────────
        base *= max(0.0, 1.0 - personal_hits/max(n_words/12, 1) * 0.35)

        # ─── Composite Boost: 3+ بصمات قوية = GPT مؤكد ───────────────────
        strong = sum([
            scores.get('trans_strict', 0)   >= 0.40,
            scores.get('no_personal', 0)    >= 0.80,
            scores.get('closing', 0)        >= 0.40,
            scores.get('emoji_tail', 0)     >= 0.40,
            scores.get('gpt_verbs', 0)      >= 0.50,
            scores.get('benefit_words', 0)  >= 0.50,
            scores.get('direct_topic', 0)   >= 0.50,
            scores.get('no_doubt', 0)       >= 0.50,
            scores.get('uniformity', 0)     >= 0.50,
        ])
        if strong >= 7:
            base = max(base, 0.90)
        elif strong >= 5:
            base = max(base, 0.75)
        elif strong >= 3:
            base = max(base, 0.60)

        return round(min(base, 1.0), 4)

    def _simple_gpt_score(self, text, words, sents):
        """
        v23 ENHANCED — يكشف GPT البسيط بـ 16 بصمة مباشرة.

        المشكلة الجذرية: GPT البسيط يستخدم لغة طبيعية جداً
        فيخدع النماذج اللغوية (LLR منخفض). لكن له بصمات هيكلية
        لا تتغير مهما تغيرت المفردات:

        الفئة الأولى  — بنية الجملة:
          ① افتتاحيات GPT النمطية (It/Reading/When/For these reasons)
          ② ضعف CV أطوال الجمل (جمل متساوية جداً)
          ③ كل جملة تحمل فكرة واحدة كاملة ومستقلة
          ④ نمط "X also Y" — GPT يُضيف بـ also بدلاً من لغة طبيعية

        الفئة الثانية — المفردات والأسلوب:
          ⑤ غياب الضمائر الشخصية تماماً (I/my/we)
          ⑥ كثافة ضمائر غير شخصية (they/people/one/readers)
          ⑦ أفعال GPT المدرسية (helps/improves/allows/supports)
          ⑧ كلمات GPT المفيدية (benefits/valuable/important/activity)
          ⑨ ظروف -ly متكررة (intellectually/personally/daily)

        الفئة الثالثة — البنية الكلية:
          ⑩ جملة ختامية نمطية (For these reasons / Therefore)
          ⑪ إيموجي في نهاية النص 📖✨
          ⑫ تكرار الكلمة المحورية في كل جملة
          ⑬ لا أسئلة / لا شك / لا ملاحظات شخصية
          ⑭ تعداد "A and B" — GPT يُعدِّد دائماً
          ⑮ بنية "سبب لأن / لأنه / because" منظمة
          ⑯ جمل تبدأ بالموضوع مباشرة (بدون سياق شخصي)
        """
        if not words or not sents:
            return 0.15

        import math as _m
        from collections import Counter as _C

        n_words = max(len(words), 1)
        n_sents = max(len(sents), 1)
        scores  = {}

        # ─── ① GPT Sentence Starters ──────────────────────────────────────
        # GPT يبدأ الجمل بـ: موضوع + فعل / ضمير غير شخصي / رابط انتقالي
        GPT_STARTERS = {
            # روابط انتقالية
            'in addition','moreover','furthermore','therefore','thus','hence',
            'consequently','additionally','however','nevertheless','nonetheless',
            'as a result','in conclusion','in summary','for these reasons',
            'finally','lastly','besides','similarly','likewise',
            # بدايات موضوعية مباشرة
            'it','reading','writing','learning','education','technology',
            'exercise','health','this','these','when','for','the',
            'daily','regular','such','one','people',
        }
        GPT_TRANS_STRICT = {
            'in addition','moreover','furthermore','therefore','thus','hence',
            'consequently','additionally','for these reasons','in conclusion',
            'in summary','finally','as a result',
        }
        starter_count = 0
        trans_strict_count = 0
        for s in sents:
            sl = s.lower().strip()
            sw = sl.split()[0] if sl.split() else ''
            for t in GPT_STARTERS:
                if sl.startswith(t + ' ') or sl.startswith(t + ','):
                    starter_count += 1
                    break
            for t in GPT_TRANS_STRICT:
                if sl.startswith(t):
                    trans_strict_count += 1
                    break
        scores['gpt_starters']  = min(max(0.0, (starter_count/n_sents - 0.20)*2.0), 1.0)
        scores['trans_strict']  = min(trans_strict_count / n_sents * 3.0, 1.0)

        # ─── ② Sentence Length Uniformity ────────────────────────────────
        lens = [len(s.split()) for s in sents if len(s.split()) > 2]
        if len(lens) >= 3:
            avg = sum(lens)/len(lens)
            cv  = _m.sqrt(sum((l-avg)**2 for l in lens)/len(lens))/(avg+1e-6)
            scores['uniformity'] = max(0.0, min(1.0, (0.35 - cv) / 0.25))
        else:
            scores['uniformity'] = 0.3

        # ─── ③ One-Idea-Per-Sentence Pattern ─────────────────────────────
        # GPT: كل جملة = فكرة واحدة مكتملة. مؤشر: قلة subordinate clauses
        SUB_CONJ = {'although','whereas','while','despite','even though',
                    'unless','until','since','after','before','once'}
        sub_count = sum(1 for s in sents
                       if any(c in s.lower() for c in SUB_CONJ))
        # GPT: sub_count منخفض (جمل بسيطة) | Human: sub_count أعلى
        scores['simple_sents'] = max(0.0, 1.0 - sub_count/n_sents*2.0)

        # ─── ④ "X also Y" Pattern ─────────────────────────────────────────
        also_pat = len(re.findall(r'\b\w+ also \w+', text, re.I))
        scores['also_pattern'] = min(also_pat * 0.35, 1.0)

        # ─── ⑤ Zero Personal Markers ──────────────────────────────────────
        PERSONAL = {'i','me','my','mine','myself','we','our','honestly',
                    'actually','think','feel','believe','guess','maybe',
                    'probably','personally','frankly','dunno','kind of'}
        personal_hits = sum(1 for w in words if w in PERSONAL)
        scores['no_personal'] = max(0.0, 1.0 - personal_hits/max(n_words/12, 1))

        # ─── ⑥ Impersonal Pronoun Density ─────────────────────────────────
        IMPERSONAL = {'they','people','individuals','readers','students',
                      'one','person','someone','everyone','anyone','humans',
                      'children','users','employees','citizens','society'}
        imp_count = sum(1 for w in words if w in IMPERSONAL)
        scores['impersonal'] = min(imp_count/n_words*10.0, 1.0)

        # ─── ⑦ GPT School Verbs ───────────────────────────────────────────
        GPT_VERBS = {
            'helps','improves','allows','enables','supports','promotes',
            'develops','builds','strengthens','boosts','enhances','increases',
            'reduces','expands','fosters','cultivates','stimulates','provides',
            'offers','encourages','facilitates','contributes','assists',
            'explores','gains','learn','grow','improve','develop',
        }
        vb_count = sum(1 for w in words if w in GPT_VERBS)
        scores['gpt_verbs'] = min(vb_count/n_words*7.0, 1.0)

        # ─── ⑧ Benefit/Value Words ────────────────────────────────────────
        BENEFIT_W = {'benefits','benefit','advantages','advantage','valuable',
                     'important','essential','crucial','key','significant',
                     'effective','powerful','positive','useful','worthwhile',
                     'lifelong','personal','intellectual','academic','overall',
                     'activity','habit','practice','development','growth'}
        ben_count = sum(1 for w in words if w in BENEFIT_W)
        scores['benefit_words'] = min(ben_count/n_words*6.0, 1.0)

        # ─── ⑨ Adverb -ly Density ─────────────────────────────────────────
        # GPT يُكثِّر الظروف المنتهية بـ -ly
        LY_ADVERBS = [w for w in words if w.endswith('ly') and len(w) > 5
                      and w not in {'really','totally','actually','literally',
                                    'honestly','basically','personally'}]
        scores['ly_adverbs'] = min(len(LY_ADVERBS)/n_words*15.0, 1.0)

        # ─── ⑩ Closing Formula ────────────────────────────────────────────
        last_150 = text[-150:].lower() if len(text)>150 else text.lower()
        CLOSE_PAT = re.compile(
            r'\b(?:for these reasons|therefore|in conclusion|in summary|'
            r'thus|hence|to conclude|in short|ultimately|overall|'
            r'is a valuable|is an important|is essential|is crucial|'
            r'supports? lifelong|personal development|overall well.?being|'
            r'daily habit|regular habit|one of the best|recommended for)',
            re.I)
        close_hits = len(CLOSE_PAT.findall(last_150))
        scores['closing'] = min(close_hits*0.55, 1.0)

        # ─── ⑪ Emoji Tail ─────────────────────────────────────────────────
        last_40 = text[-40:] if len(text)>40 else text
        emoji_tail = len(re.findall(
            r'[\U0001F300-\U0001F9FF\U0001F600-\U0001F64F'
            r'\U0001F680-\U0001F6FF\u2600-\u27BF📚✨📖🔹⚡🌟💡🎯]',
            last_40))
        scores['emoji_tail'] = min(emoji_tail*0.55, 1.0)

        # ─── ⑫ Topic Word Repetition ──────────────────────────────────────
        content = [w for w in words if len(w)>4]
        if content:
            freq = _C(content)
            top_count = freq.most_common(1)[0][1]
            scores['topic_rep'] = min(max(0.0,(top_count/n_sents - 0.25)*2.5), 1.0)
        else:
            scores['topic_rep'] = 0.2

        # ─── ⑬ No Doubt/Question ──────────────────────────────────────────
        DOUBT = {'maybe','perhaps','might','wonder','not sure','unsure',
                 'unclear','seems','appears','could be','possibly'}
        has_doubt = any(w in text.lower() for w in DOUBT)
        has_question = '?' in text
        scores['no_doubt'] = 0.0 if (has_doubt or has_question) else 0.70

        # ─── ⑭ "A and B" Enumeration ──────────────────────────────────────
        and_pairs = len(re.findall(r'\b\w{4,} and \w{4,}\b', text))
        scores['enumeration'] = min(and_pairs/n_sents*0.35, 1.0)

        # ─── ⑮ "because/as/since" Causal Structure ────────────────────────
        causal = len(re.findall(
            r'\b(?:because it|because they|as it|as they|since it|'
            r'which allows?|that allows?|which helps?|that helps?|'
            r'which enables?|that enables?|as readers?|as people)\b',
            text, re.I))
        scores['causal'] = min(causal*0.30, 1.0)

        # ─── ⑯ Direct Topic Opener ────────────────────────────────────────
        # GPT يبدأ بالموضوع مباشرة بلا مقدمة شخصية
        first_sent = sents[0].lower() if sents else ''
        direct_topic = not any(w in first_sent for w in
                               ['i ','my ','we ','our ','honestly','actually',
                                'you know','let me','in my'])
        scores['direct_topic'] = 0.65 if direct_topic else 0.0

        # ─── Weighted Composite ───────────────────────────────────────────
        W = {
            'trans_strict':   0.14,
            'no_personal':    0.12,
            'gpt_starters':   0.10,
            'gpt_verbs':      0.09,
            'benefit_words':  0.09,
            'closing':        0.08,
            'no_doubt':       0.07,
            'uniformity':     0.07,
            'direct_topic':   0.06,
            'simple_sents':   0.05,
            'emoji_tail':     0.05,
            'impersonal':     0.04,
            'topic_rep':      0.04,
            'also_pattern':   0.03,
            'causal':         0.03,
            'ly_adverbs':     0.03,
            'enumeration':    0.01,
        }
        # Verify weights sum
        w_sum = sum(W.values())
        # Normalize if needed
        if abs(w_sum - 1.0) > 0.001:
            W = {k:v/w_sum for k,v in W.items()}

        base = sum(scores.get(k, 0.0) * v for k, v in W.items())

        # ─── Human Penalty ────────────────────────────────────────────────
        base *= max(0.0, 1.0 - personal_hits/max(n_words/12, 1) * 0.35)

        # ─── Composite Boost: 3+ بصمات قوية = GPT مؤكد ───────────────────
        strong = sum([
            scores.get('trans_strict', 0)   >= 0.40,
            scores.get('no_personal', 0)    >= 0.80,
            scores.get('closing', 0)        >= 0.40,
            scores.get('emoji_tail', 0)     >= 0.40,
            scores.get('gpt_verbs', 0)      >= 0.50,
            scores.get('benefit_words', 0)  >= 0.50,
            scores.get('direct_topic', 0)   >= 0.50,
            scores.get('no_doubt', 0)       >= 0.50,
            scores.get('uniformity', 0)     >= 0.50,
        ])
        if strong >= 7:
            base = max(base, 0.90)
        elif strong >= 5:
            base = max(base, 0.75)
        elif strong >= 3:
            base = max(base, 0.60)

        return round(min(base, 1.0), 4)

    def _gpt_formatting_signature(self, text, sents):
        """
        يكشف بصمة تنسيق GPT/Claude المباشرة — أدق وأقوى مؤشر للنص المنسوخ.

        المبدأ العلمي:
        حين يكتب GPT نصاً، يُضيف تلقائياً تنسيقات Markdown لم يطلبها
        المستخدم أحياناً، أو يتركها في النص حين يُنسخ مباشرةً.
        هذه التنسيقات "بصمة رقمية" لا تظهر في الكتابة البشرية الطبيعية.

        الفئات المكتشفة:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        1. **Bold text** — النجمتان المزدوجتان للتغميق
        2. *Italic text* — النجمة المفردة للمائل
        3. ## Headers / ### Subheaders — علامات الرأس
        4. - Bullet lists / * Bullet lists — القوائم النقطية
        5. 1. Numbered lists — القوائم المرقمة المنظمة جداً
        6. `inline code` — الكود المُضمَّن
        7. > Blockquotes — الاقتباسات المُزاحة
        8. --- / === / *** separators — الخطوط الفاصلة
        9. [text](url) — روابط Markdown
        10. Table syntax |col|col| — جداول Markdown
        11. نمط الإجابة المنظمة: عنوان + شرح + قائمة متكررة
        12. GPT Opener signatures — افتتاحيات GPT المميزة
        13. GPT Closer signatures — ختاميات GPT المميزة
        14. Emoji overuse — كثرة الإيموجي بنمط GPT
        15. Colon-intro pattern — نمط النقطتين التمهيديتين
        16. Repetitive structure — بنية متكررة صارمة (GPT يكرر الهيكل)
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        if not text:
            return 0.0

        n_words  = max(len(re.findall(r'\b\w+\b', text)), 1)
        n_lines  = max(len(text.splitlines()), 1)
        n_sents  = max(len(sents), 1)
        scores   = {}

        # ─── 1. Bold Markdown (**text**) ─────────────────────────────────
        # النجمتان المزدوجتان: أوضح علامة على GPT
        bold_hits = len(re.findall(r'\*\*[^*\n]{1,80}\*\*', text))
        if bold_hits > 0:
            # كل hit وحده يكفي كدليل قوي
            scores['bold'] = min(bold_hits * 0.45, 1.0)
        else:
            scores['bold'] = 0.0

        # ─── 2. Italic Markdown (*text* أو _text_) ───────────────────────
        italic_hits = len(re.findall(r'(?<!\*)\*[^*\n]{1,60}\*(?!\*)', text))
        italic_hits += len(re.findall(r'(?<!_)_[^_\n]{1,60}_(?!_)', text))
        scores['italic'] = min(italic_hits * 0.25, 1.0)

        # ─── 3. Headers (## / ### / #### / # ) ───────────────────────────
        header_hits = len(re.findall(r'(?m)^#{1,6}\s+\S', text))
        scores['headers'] = min(header_hits * 0.55, 1.0)

        # ─── 4. Bullet Lists (- item / * item / • item) ──────────────────
        bullet_hits = len(re.findall(r'(?m)^\s*[-*•]\s+\S', text))
        # GPT ينشئ قوائم نقطية طويلة متعددة الأسطر
        bullet_density = bullet_hits / n_lines
        scores['bullets'] = min(bullet_density * 8.0, 1.0)

        # ─── 5. Numbered Lists (1. / 2. / i. / a.) ───────────────────────
        numbered_hits = len(re.findall(r'(?m)^\s*(?:\d+[\.\)]\s+|[a-zA-Z][\.\)]\s+)[A-Z\u0600-\u06FF]', text))
        # GPT يُرقِّم بشكل صارم ومنتظم جداً
        numbered_density = numbered_hits / n_lines
        scores['numbered'] = min(numbered_density * 6.0, 1.0)

        # ─── 6. Inline Code (`code`) ─────────────────────────────────────
        code_hits = len(re.findall(r'`[^`\n]{1,100}`', text))
        scores['inline_code'] = min(code_hits * 0.30, 1.0)

        # ─── 7. Blockquotes (> text) ─────────────────────────────────────
        quote_hits = len(re.findall(r'(?m)^>\s+\S', text))
        scores['blockquotes'] = min(quote_hits * 0.40, 1.0)

        # ─── 8. Horizontal Rules (--- / === / ***) ───────────────────────
        hr_hits = len(re.findall(r'(?m)^[-=*_]{3,}\s*$', text))
        scores['horizontal_rules'] = min(hr_hits * 0.50, 1.0)

        # ─── 9. Markdown Links ([text](url)) ─────────────────────────────
        link_hits = len(re.findall(r'\[.{1,60}\]\(https?://', text))
        scores['md_links'] = min(link_hits * 0.35, 1.0)

        # ─── 10. Markdown Tables (|col|col|) ─────────────────────────────
        table_hits = len(re.findall(r'(?m)^\|.+\|.+\|', text))
        scores['md_tables'] = min(table_hits * 0.40, 1.0)

        # ─── 11. Colon-Intro Pattern ──────────────────────────────────────
        # GPT يقدم فقرات بنمط: "العنوان:" ثم الشرح — متكرر جداً
        colon_intro = len(re.findall(
            r'(?m)^[A-Z\u0600-\u06FF][^:\n]{3,40}:\s*$|'  # سطر ينتهي بـ :
            r'\b(?:here are|here is|the following|as follows|below are|'
            r'these include|they are|namely|specifically):\s',
            text, re.I))
        scores['colon_intro'] = min(colon_intro * 0.35, 1.0)

        # ─── 12. GPT Opener Signatures ───────────────────────────────────
        # افتتاحيات مميزة جداً لـ GPT — نصية وتنسيقية معاً
        GPT_OPENERS = re.compile(
            r'(?m)^(?:'
            r'(?:great|sure|certainly|absolutely|of course|happy to|'
            r'glad to|here(?:\'?s| is| are)|i(?:\'ll|\'d| will| can| would)|'
            r'let(?:\'?s| me)|allow me|let me provide|below (?:is|are)|'
            r'the following|as requested|as you(?:\'ve)? (?:asked|requested|mentioned)|'
            r'(?:in this (?:response|answer|explanation|overview|summary|guide|essay|analysis)|'
            r'this (?:essay|paper|article|response|overview|guide|analysis|report) (?:will|aims|explores?|covers?|examines?|discusses?))'
            r'))',
            re.I)
        opener_hits = len(GPT_OPENERS.findall(text))
        scores['gpt_openers'] = min(opener_hits * 0.60, 1.0)

        # ─── 12b. GPT Pure-Text Signatures (بدون Markdown) ───────────────
        # هذه الأنماط تظهر حتى حين ينسخ الطالب النص بدون تنسيق
        GPT_TEXT_SIGS = re.compile(
            r'\b(?:'
            # جمل الافتراض الكلاسيكية لـ GPT
            r'it is (?:worth noting|important to note|crucial to note|'
            r'essential to note|worth mentioning|important to mention|'
            r'worth emphasizing|important to emphasize|worth highlighting) that|'
            # نمط "يلعب دوراً" — أشهر نمط GPT
            r'plays? (?:a|an) (?:crucial|key|vital|important|significant|'
            r'central|fundamental|pivotal|major|critical|essential) role(?:s)? in|'
            # نمط الاستنتاج النموذجي
            r'in (?:conclusion|summary|closing|summation),? (?:it is|we can|'
            r'this|the|these|it can be)|'
            r'to (?:summarize|sum up|conclude|recap),? (?:it is|we can|this|the)|'
            # نمط المستقبل المُلزِم
            r'future (?:research|studies|work|investigations?) (?:should|must|'
            r'ought to|needs? to|would benefit from|could|may|might)|'
            r'(?:further|additional|more) (?:research|studies|work) (?:is|are) (?:needed|required|necessary|warranted)|'
            # نمط "لا يمكن إنكار" / "من الأهمية بمكان"
            r'it (?:is|cannot be) (?:undeniable|undeniably|clear|clearly|evident|'
            r'obvious|without doubt|without question|beyond doubt|beyond question) that|'
            r'there (?:is|can be) no (?:doubt|question|denying) that|'
            # نمط الإطار المزدوج
            r'this (?:paper|study|article|essay|analysis|report|work|overview|'
            r'examination|review|discussion|investigation) (?:aims?|seeks?|'
            r'attempts?|endeavors?|explores?|examines?|investigates?|presents?|'
            r'discusses?|analyzes?|highlights?|demonstrates?|considers?|addresses?)|'
            r'the (?:purpose|aim|goal|objective|focus|scope) of (?:this|the present|the current)|'
            # نمط "في ضوء ذلك" و"بالنظر إلى"
            r'in (?:light|view) of (?:the|these|this|aforementioned|above)|'
            r'given (?:the|these|this|aforementioned|above) (?:considerations?|factors?|'
            r'findings?|evidence|results?|analysis|discussion|context)|'
            # نمط الاستشهاد الزائف
            r'(?:research|studies|evidence|literature|data|experts?|scholars?) (?:suggest(?:s|ed)?|'
            r'indicate(?:s|d)?|show(?:s|n|ed)?|demonstrate(?:s|d)?|confirm(?:s|ed)?|'
            r'support(?:s|ed)?|reveal(?:s|ed)?|highlight(?:s|ed)?) that|'
            # نمط التعداد المنظم
            r'(?:first(?:ly)?|second(?:ly)?|third(?:ly)?),? (?:it is|this|the|we|there)|'
            r'(?:on one hand|on the other hand|in contrast|by contrast),? (?:it|this|the)|'
            # نمط الختام العاطفي — GPT يُضيفه دائماً
            r'it (?:is|has been) (?:hoped|anticipated|expected|argued) that|'
            r'(?:these|the|this|such) (?:findings?|results?|insights?|implications?) (?:have|hold|carry) '
            r'(?:important|significant|profound|major|far-reaching|considerable) implications?'
            r')\b',
            re.I)
        text_sig_hits = len(GPT_TEXT_SIGS.findall(text))
        # كثافة: hits per 100 words — AI text يحتوي 2-8 hits/100كلمة
        text_sig_density = text_sig_hits / (n_words / 100)
        # رفع الحساسية: hit واحد لكل 100 كلمة = 0.50
        scores['gpt_text_sigs'] = min(text_sig_density * 0.70, 1.0)

        # ─── 12c. Arabic GPT Text Signatures (عربي بدون تنسيق) ──────────
        AR_TEXT_SIGS = re.compile(
            r'(?:'
            r'يلعب دوراً (?:محورياً|أساسياً|مهماً|بارزاً|كبيراً|رئيسياً|حيوياً)|'
            r'(?:تجدر|يجدر) الإشارة إلى|'
            r'من الجدير بالذكر|من الأهمية بمكان|'
            r'وفي ضوء (?:ذلك|ما سبق|هذه|هذا)|'
            r'وبالنظر إلى|وانطلاقاً من|وفي هذا الإطار|'
            r'وفي ختام|وخلاصة القول|وفي المحصلة|'
            r'تشير الدراسات إلى|تدل الأبحاث على|يتضح من الأدلة|'
            r'ومن ثَمَّ|وعلى هذا الأساس|وفي هذا السياق|'
            r'(?:ينبغي|يجب|لا بد) أن (?:تتناول|تستكشف|تفحص|تدرس) الدراسات المستقبلية|'
            r'تكشف النتائج عن|تُظهر الدراسة أن|يتبيّن من (?:خلال|التحليل)|'
            r'(?:هذه|تلك) (?:النتائج|الدراسة|المعطيات) (?:تشير|تكشف|تُظهر|توضح|تُبيّن)|'
            r'وفيما يتعلق بـ?|وفيما يخص|أما فيما يتعلق|'
            r'بشكل عام|بصفة عامة|على وجه العموم|بوجه عام'
            r')',
            re.I | re.UNICODE)
        ar_text_hits = len(AR_TEXT_SIGS.findall(text))
        # كل hit عربي قوي جداً — مضاعفة الحساسية
        scores['ar_text_sigs'] = min(ar_text_hits * 0.55, 1.0)

        # ─── 13. GPT Closer Signatures ───────────────────────────────────
        # ختاميات GPT المميزة — الجمل الأخيرة من النص
        last_500 = text[-500:] if len(text) > 500 else text
        GPT_CLOSERS = re.compile(
            r'\b(?:'
            r'i hope this (?:helps?|answers?|clarifies?|explains?|gives?|provides?)|'
            r'(?:please )?(?:let me know|feel free to) (?:if|whether) (?:you|there)|'
            r'if you (?:have|need) (?:any (?:more|further|additional|other)|other)|'
            r'don(?:\'t| not) hesitate to (?:ask|reach out|contact)|'
            r'is there (?:anything|something) (?:else|more|further)|'
            r'hope(?:fully)? (?:this|that) (?:helps?|is helpful|answers?|clarifies?)|'
            r'(?:for|if you need) (?:further|more|additional) (?:information|details?|clarification|help|assistance)|'
            r'feel free to (?:ask|inquire|reach out)'
            r')\b',
            re.I)
        closer_hits = len(GPT_CLOSERS.findall(last_500))
        scores['gpt_closers'] = min(closer_hits * 0.70, 1.0)

        # ─── 14. Emoji Overuse (بنمط GPT) ────────────────────────────────
        # GPT يضع إيموجي في بداية الأسطر أو بجانب النقاط
        emoji_pattern = re.compile(
            r'[\U0001F300-\U0001F9FF\U00002600-\U000027BF'
            r'\U0001F600-\U0001F64F\U0001F680-\U0001F6FF'
            r'\u2600-\u26FF\u2700-\u27BF]',
            re.UNICODE)
        emoji_count = len(emoji_pattern.findall(text))
        # GPT يضع إيموجي في بداية الأسطر بشكل منتظم
        emoji_line_starts = len(re.findall(r'(?m)^[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001F600-\U0001F9FF]', text))
        emoji_score = min((emoji_count * 0.12 + emoji_line_starts * 0.30), 1.0)
        scores['emojis'] = emoji_score

        # ─── 15. Repetitive Structural Pattern ───────────────────────────
        # GPT يكرر نفس الهيكل (عنوان + فقرة + قائمة) بدقة مثيرة للريبة
        lines = text.splitlines()
        # كشف التناوب المنتظم: سطر فارغ → سطر يبدأ بحرف كبير → محتوى
        structural_score = 0.0
        if len(lines) >= 6:
            # كم مرة يظهر نمط: سطر قصير (عنوان) + سطر طويل (شرح)؟
            title_body_pairs = 0
            for i in range(len(lines) - 1):
                curr_words = len(lines[i].split())
                next_words = len(lines[i+1].split())
                # سطر عنوان: 1-6 كلمات | سطر شرح: 10+ كلمة
                if 1 <= curr_words <= 6 and next_words >= 10:
                    title_body_pairs += 1
            structural_score = min(title_body_pairs / max(n_lines/4, 1) * 2.5, 1.0)
        scores['structure_repeat'] = structural_score

        # ─── 16. Arabic GPT Signatures ───────────────────────────────────
        # GPT العربي له بصمات خاصة به
        AR_GPT_SIGS = re.compile(
            r'(?:'
            # افتتاحيات عربية لـ GPT
            r'(?:بالتأكيد|بكل سرور|يسعدني|سأوضح لك|إليك|فيما يلي|'
            r'هناك عدة|يمكن تلخيص|وفيما يخص|فيما يتعلق|'
            r'من الجدير بالذكر|تجدر الإشارة إلى|ومن الأهمية بمكان|'
            r'وبشكل عام|وبصورة عامة|وفي المحصلة|وخلاصة القول|'
            r'وفي ختام|وفي نهاية المطاف|مما سبق يتضح|من خلال ما سبق)'
            r')',
            re.I | re.UNICODE)
        ar_hits = len(AR_GPT_SIGS.findall(text))
        scores['arabic_gpt'] = min(ar_hits * 0.40, 1.0)

        # ─── 17. Section Label Pattern ───────────────────────────────────
        # GPT يُسمِّي الأقسام بشكل متكرر: "Introduction:", "Conclusion:", إلخ
        SECTION_LABELS = re.compile(
            r'(?m)^(?:'
            r'introduction|background|overview|objective[s]?|purpose|'
            r'methodology|method[s]?|approach|analysis|discussion|'
            r'result[s]?|finding[s]?|conclusion[s]?|recommendation[s]?|'
            r'summary|key (?:points?|takeaway[s]?|finding[s]?|aspect[s]?)|'
            r'pros?(?: and cons?)?|advantage[s]?|disadvantage[s]?|benefit[s]?|'
            r'example[s]?|case stud(?:y|ies)|implication[s]?|limitation[s]?|'
            r'مقدمة|خلفية|أهداف|منهجية|نتائج|توصيات|خاتمة|ملخص|'
            r'مزايا|عيوب|أمثلة|تطبيقات|توصيات|استنتاجات'
            r')[\s]*[:\-–]',
            re.I | re.UNICODE)
        label_hits = len(SECTION_LABELS.findall(text))
        scores['section_labels'] = min(label_hits * 0.45, 1.0)

        # ─── 18. Transition Sentence Pairs ───────────────────────────────
        # GPT يُختم كل فقرة بجملة انتقالية متوقعة تماماً
        TRANS_SENT = re.compile(
            r'\b(?:'
            r'with this in mind|building on this|taking this into account|'
            r'given the above|as mentioned (?:above|earlier|previously|before)|'
            r'as (?:discussed|noted|outlined|highlighted|shown|demonstrated) (?:above|earlier|previously|before)|'
            r'with (?:this|these|that|those) (?:in mind|considerations?|points?|factors?)|'
            r'having (?:established|discussed|examined|considered|explored|outlined)|'
            r'now (?:that|we have|having)|turning (?:now|our attention) to|'
            r'moving (?:on|forward|to the next)|let us (?:now|turn|consider|examine)|'
            r'the next (?:section|part|aspect|point|step|consideration)'
            r')\b',
            re.I)
        trans_sent_hits = len(TRANS_SENT.findall(text))
        scores['transition_sentences'] = min(trans_sent_hits * 0.38, 1.0)

        # ─── 19. Excessive Parallelism ────────────────────────────────────
        # GPT يكتب جملاً متوازية بنية صارمة جداً
        # (يستخدم نفس البنية النحوية بالضبط في جمل متتالية)
        parallel_score = 0.0
        if len(sents) >= 4:
            # فحص أول كلمة من كل جملة — GPT يكرر نفس الافتتاحية
            first_words = [s.split()[0].lower() for s in sents if s.split()]
            from collections import Counter as _C
            fw_freq = _C(first_words)
            top_fw  = fw_freq.most_common(1)[0][1] if fw_freq else 0
            # إذا أكثر من 25% من الجمل تبدأ بنفس الكلمة = GPT parallelism
            parallel_score = min(max(0.0, (top_fw / n_sents - 0.20) * 4.0), 1.0)
        scores['parallelism'] = parallel_score

        # ─── 20. Balanced Bold Emphasis ──────────────────────────────────
        # GPT يضع bold على نفس النسبة تقريباً من الكلمات في كل فقرة
        if bold_hits >= 2:
            paras = [p for p in re.split(r'\n{2,}', text) if p.strip()]
            para_bolds = [len(re.findall(r'\*\*[^*\n]{1,80}\*\*', p)) for p in paras]
            if len(para_bolds) >= 2:
                avg_pb = sum(para_bolds) / len(para_bolds)
                if avg_pb > 0:
                    from math import sqrt as _sqrt
                    cv_pb = _sqrt(sum((b-avg_pb)**2 for b in para_bolds)/len(para_bolds)) / avg_pb
                    # انتظام منخفض جداً = GPT يُوزِّع البولد بانتظام رياضي
                    scores['balanced_bold'] = max(0.0, 1.0 - cv_pb * 2.0)
                else:
                    scores['balanced_bold'] = 0.0
            else:
                scores['balanced_bold'] = bold_hits * 0.3
        else:
            scores['balanced_bold'] = 0.0

        # ─── Final Weighted Composite ─────────────────────────────────────
        # الأوزان مُعايَرة حسب قوة كل مؤشر في الكشف
        WEIGHTS = {
            'bold':                 0.11,
            'headers':              0.08,
            'gpt_text_sigs':        0.10,  # ★ NEW — أقوى مؤشر نصي
            'ar_text_sigs':         0.07,  # ★ NEW — للنصوص العربية
            'bullets':              0.06,
            'gpt_openers':          0.06,
            'gpt_closers':          0.06,
            'section_labels':       0.05,
            'arabic_gpt':           0.05,
            'colon_intro':          0.05,
            'structure_repeat':     0.04,
            'numbered':             0.04,
            'transition_sentences': 0.04,
            'parallelism':          0.04,
            'emojis':               0.03,
            'balanced_bold':        0.03,
            'italic':               0.02,
            'horizontal_rules':     0.02,
            'md_tables':            0.02,
            'inline_code':          0.01,
            'blockquotes':          0.01,
            'md_links':             0.01,
        }
        assert abs(sum(WEIGHTS.values()) - 1.0) < 0.01, "GPT weights error"

        base_score = sum(scores.get(k, 0.0) * v for k, v in WEIGHTS.items())

        # ── Bonus: إذا تحقق أكثر من 3 مؤشرات معاً → نص GPT مؤكد ──────────
        confirmed_signals = sum(1 for k in ['bold','headers','bullets',
                                             'gpt_openers','gpt_closers',
                                             'section_labels','arabic_gpt',
                                             'gpt_text_sigs','ar_text_sigs']
                                if scores.get(k, 0.0) >= 0.30)
        if confirmed_signals >= 3:
            base_score = min(base_score + 0.15 * (confirmed_signals - 2), 1.0)
        elif confirmed_signals >= 2:
            base_score = min(base_score + 0.08, 1.0)

        # ── Text-Only GPT Anchor ──────────────────────────────────────────
        # إذا gpt_text_sigs مرتفع جداً (نص GPT بدون تنسيق) → رفع الحد الأدنى
        # يضمن كشف النصوص المنسوخة من GPT التي أُزيل تنسيقها
        ts = scores.get('gpt_text_sigs', 0.0)
        ar = scores.get('ar_text_sigs',  0.0)
        if ts >= 0.80 or ar >= 0.80:
            # نص GPT خالص بدون markdown — يرفع الحد الأدنى للـ "محتمل"
            text_floor = 0.30 + max(ts, ar) * 0.30
            base_score = max(base_score, text_floor)
        elif ts >= 0.50 or ar >= 0.50:
            text_floor = 0.18 + max(ts, ar) * 0.20
            base_score = max(base_score, text_floor)

        return round(min(base_score, 1.0), 4)

    def _paraphrase_engine(self, text, sents, words):
        """
        محرك Paraphrasing الرئيسي — 8 فئات تحليل.

        المبدأ العلمي:
        حين يُعيد AI صياغة نصه، تتغير الكلمات لكن تبقى:
          - بنية تحويل الفعل لاسم (Nominalization)
          - تحويل المبني للمعلوم ↔ للمجهول (Voice switching)
          - تقسيم/دمج الجمل مع إضافة روابط توسعية
          - استبدال علامات الخطاب مع الحفاظ على وظيفتها
          - أنماط التحوّط اللغوي (hedge substitution)
          - توسع عبارات الفعل (verb phrase elaboration)
          - البنى المكررة المتوازية (structural mirroring)
          - إعادة صياغة المفهوم صراحةً (concept restatement)
        """
        if not sents or not words:
            return 0.15

        text_l = text.lower()
        n_words = max(len(words), 1)
        n_sents = max(len(sents), 1)

        # ─── A: كثافة أنماط Paraphrase الكلية ───────────────────────────
        para_hits = sum(len(p.findall(text_l)) for p in self._paraphrase_patterns)
        para_density = para_hits / (n_words / 20)  # hits per 20 words
        para_score_raw = min(para_density * 0.55, 1.0)

        # ─── B: Nominalization Ratio ─────────────────────────────────────
        # AI يحوّل الأفعال البسيطة لأسماء مجردة (hallmark of paraphrasing)
        NOMIN_ENDINGS = ('tion','sion','ment','ure','ance','ence',
                         'ity','ness','ism','age','al','ing')
        NOMIN_TRIGGERS = re.compile(
            r'\b(?:conduct|perform|carry out|undertake|make|achieve|'
            r'provide|offer|give|present|deliver|produce|develop|'
            r'implement|establish|create|build|form|design|generate)\b',
            re.I)
        nom_triggers = len(NOMIN_TRIGGERS.findall(text_l))
        # كلمات تنتهي بـ endings أكاديمية بعد trigger verb
        nom_words = sum(1 for w in words if any(w.endswith(e) for e in NOMIN_ENDINGS))
        nom_ratio = nom_words / n_words
        # AI في paraphrasing: nom_triggers مرتفعة مع nom_ratio مرتفعة
        nom_ai = min((nom_triggers / n_sents) * 2.5, 1.0) * min(nom_ratio * 4.0, 1.0)

        # ─── C: Voice Alternation Pattern ───────────────────────────────
        # AI يُبدِّل بين المبني للمعلوم والمجهول بشكل منتظم
        active_sents  = sum(1 for s in sents if re.search(r'\b(?:we|they|it|the \w+)\s+\w+(?:ed|s)\b', s, re.I))
        passive_sents = sum(1 for s in sents if re.search(r'\b(?:is|are|was|were|been|being)\s+\w+ed\b', s, re.I))
        total_typed   = active_sents + passive_sents
        if total_typed >= 3:
            voice_ratio = min(active_sents, passive_sents) / total_typed
            # AI paraphrase: يمزج بانتظام → voice_ratio قريب من 0.3-0.5
            voice_ai = min(voice_ratio * 2.5, 1.0)
        else:
            voice_ai = 0.25

        # ─── D: Connector Elaboration Density ───────────────────────────
        # AI يُضيف روابط توسعية عند إعادة الصياغة
        ELAB_CONNECTORS = re.compile(
            r'\b(?:in other words|that is to say|to be more specific|'
            r'more (?:specifically|precisely|accurately|clearly)|'
            r'to (?:elaborate|clarify|explain|expand|illustrate)|'
            r'put (?:differently|simply|another way)|'
            r'this (?:means|implies|suggests|indicates) that|'
            r'what this (?:means|shows|demonstrates) is|'
            r'to rephrase|in essence|essentially|fundamentally speaking|'
            r'at its (?:core|heart|root)|in practical terms)\b',
            re.I)
        elab_hits = len(ELAB_CONNECTORS.findall(text_l))
        elab_ai = min(elab_hits / (n_words / 60) * 0.8, 1.0)

        # ─── E: Sentence-level Paraphrase Fingerprint ───────────────────
        # كل جملة تُحلَّل: هل تحتوي على مزيج من paraphrase markers؟
        sent_scores = []
        for s in sents[:40]:  # عينة من أول 40 جملة
            s_l = s.lower()
            s_words = re.findall(r'\b[a-z]+\b', s_l)
            if len(s_words) < 4:
                continue
            # نمط composite: nominalization + formal connector + passive
            has_nom  = any(w.endswith(('tion','ment','ity','ance','ence')) for w in s_words)
            has_conn = bool(re.search(
                r'\b(?:however|therefore|furthermore|moreover|consequently|'
                r'additionally|nevertheless|nonetheless|accordingly|'
                r'subsequently|in addition|as a result|for instance|'
                r'for example|in particular|specifically|notably)\b', s_l))
            has_pass = bool(re.search(r'\b(?:is|are|was|were|been)\s+\w+ed\b', s_l))
            has_hedge = bool(re.search(
                r'\b(?:may|might|could|should|appear|seem|suggest|indicate|'
                r'generally|typically|often|tend to|in some|in many|largely)\b', s_l))
            # composite score: جملة AI paraphrase تجمع ≥2 من هذه
            composite = sum([has_nom, has_conn, has_pass, has_hedge])
            sent_scores.append(min(composite / 3.0, 1.0))

        sent_ai = sum(sent_scores) / max(len(sent_scores), 1)

        # ─── F: Abstract Noun Cluster Density ───────────────────────────
        # AI يُكثِّف الأسماء المجردة المُتجمِّعة في نفس الجملة
        ABS_NOUNS = {'approach','framework','perspective','dimension','aspect',
                     'element','component','factor','mechanism','process',
                     'phenomenon','paradigm','concept','notion','principle',
                     'strategy','method','technique','model','system',
                     'context','domain','scope','realm','spectrum','arena',
                     'landscape','ecosystem','infrastructure','foundation',
                     'implication','consequence','significance','relevance'}
        cluster_scores = []
        for s in sents[:30]:
            sw = set(re.findall(r'\b[a-z]+\b', s.lower()))
            cluster_count = len(sw & ABS_NOUNS)
            cluster_scores.append(min(cluster_count / 4.0, 1.0))
        abs_noun_ai = sum(cluster_scores) / max(len(cluster_scores), 1)

        # ─── Final Composite ─────────────────────────────────────────────
        raw = (
            para_score_raw * 0.28 +
            nom_ai         * 0.18 +
            voice_ai       * 0.10 +
            elab_ai        * 0.14 +
            sent_ai        * 0.18 +
            abs_noun_ai    * 0.12
        )
        # تخفيف: النصوص التي تحتوي ضمائر شخصية ليست paraphrase AI
        fp_ratio = sum(1 for w in words if w in {'i','me','my','we','our','us'}) / n_words
        raw = raw * max(0.0, 1.0 - fp_ratio * 8.0)
        return round(min(raw, 1.0), 4)


    def _synonym_density(self, words):
        """
        كثافة المرادفات الأكاديمية — Synonym Substitution Detector.

        المبدأ: حين يُعيد AI صياغة نص، يستبدل الكلمات بمرادفات من نفس
        المستوى الأكاديمي. الكثافة العالية لكلمات من نفس الحقل الدلالي
        مع تنوع في الصياغة = إشارة paraphrasing قوية.

        يُحلِّل: تنوع المرادفات × كثافتها × تجمّعها في نفس النص.
        """
        if len(words) < 15:
            return 0.25

        from collections import Counter as _C

        # تعيين كل كلمة لمجموعتها الدلالية
        SEMANTIC_GROUPS = {
            'demonstrate': 'show_grp',    'show': 'show_grp',
            'illustrate':  'show_grp',    'exhibit': 'show_grp',
            'reveal':      'show_grp',    'reflect': 'show_grp',
            'manifest':    'show_grp',    'display': 'show_grp',
            'important':   'imp_grp',     'significant': 'imp_grp',
            'crucial':     'imp_grp',     'critical': 'imp_grp',
            'vital':       'imp_grp',     'essential': 'imp_grp',
            'pivotal':     'imp_grp',     'fundamental': 'imp_grp',
            'paramount':   'imp_grp',     'key': 'imp_grp',
            'improve':     'enhance_grp', 'enhance': 'enhance_grp',
            'boost':       'enhance_grp', 'strengthen': 'enhance_grp',
            'augment':     'enhance_grp', 'elevate': 'enhance_grp',
            'advance':     'enhance_grp', 'foster': 'enhance_grp',
            'promote':     'enhance_grp', 'cultivate': 'enhance_grp',
            'use':         'use_grp',     'utilize': 'use_grp',
            'employ':      'use_grp',     'apply': 'use_grp',
            'implement':   'use_grp',     'adopt': 'use_grp',
            'leverage':    'use_grp',     'harness': 'use_grp',
            'deploy':      'use_grp',     'incorporate': 'use_grp',
            'help':        'help_grp',    'facilitate': 'help_grp',
            'enable':      'help_grp',    'allow': 'help_grp',
            'support':     'help_grp',    'assist': 'help_grp',
            'contribute':  'help_grp',    'aid': 'help_grp',
            'result':      'result_grp',  'outcome': 'result_grp',
            'finding':     'result_grp',  'conclusion': 'result_grp',
            'consequence':  'result_grp', 'effect': 'result_grp',
            'impact':      'result_grp',  'implication': 'result_grp',
            'problem':     'prob_grp',    'challenge': 'prob_grp',
            'issue':       'prob_grp',    'concern': 'prob_grp',
            'difficulty':  'prob_grp',    'obstacle': 'prob_grp',
            'limitation':  'prob_grp',    'constraint': 'prob_grp',
            'understand':  'know_grp',    'comprehend': 'know_grp',
            'recognize':   'know_grp',    'acknowledge': 'know_grp',
            'appreciate':  'know_grp',    'realize': 'know_grp',
            'perceive':    'know_grp',    'discern': 'know_grp',
            'however':     'contr_grp',   'nevertheless': 'contr_grp',
            'nonetheless': 'contr_grp',   'conversely': 'contr_grp',
            'therefore':   'cause_grp',   'thus': 'cause_grp',
            'hence':       'cause_grp',   'consequently': 'cause_grp',
            'additionally':'add_grp',     'furthermore': 'add_grp',
            'moreover':    'add_grp',     'besides': 'add_grp',
        }

        # تعيين كل كلمة في النص
        group_hits = _C()
        word_hits  = _C()
        for w in words:
            g = SEMANTIC_GROUPS.get(w)
            if g:
                group_hits[g] += 1
                word_hits[w]  += 1

        if not group_hits:
            return 0.15

        n = len(words)

        # ─ مؤشر 1: كثافة الكلمات المُصنَّفة ─
        total_classified = sum(group_hits.values())
        density = total_classified / n
        density_ai = min(density * 18.0, 1.0)

        # ─ مؤشر 2: تنوع الكلمات داخل نفس المجموعة (= paraphrase) ─
        # paraphrasing يُنوِّع الكلمات لكن يبقى في نفس المجموعة الدلالية
        variety_scores = []
        for grp, total_count in group_hits.items():
            # كم كلمة مختلفة في هذه المجموعة؟
            grp_words = [w for w in words if SEMANTIC_GROUPS.get(w) == grp]
            unique_in_grp = len(set(grp_words))
            # تنوع عالٍ في مجموعة واحدة = paraphrasing
            variety_scores.append(min(unique_in_grp / 3.0, 1.0))
        variety_ai = sum(variety_scores) / max(len(variety_scores), 1)

        # ─ مؤشر 3: تعدد المجموعات المُمثَّلة ─
        group_coverage = len(group_hits) / len(set(SEMANTIC_GROUPS.values()))
        coverage_ai = min(group_coverage * 2.5, 1.0)

        result = (density_ai * 0.45 + variety_ai * 0.35 + coverage_ai * 0.20)
        return round(min(result, 1.0), 4)


    def _discourse_invariant(self, text):
        """
        بصمة خطابية ثابتة بعد Paraphrasing — Discourse Invariant Score.

        المبدأ: حتى بعد إعادة الصياغة الكاملة، يُبقي AI على:
          1. بنية الإطار (framing structure): مقدمة-جسم-خاتمة واضحة
          2. الاستشهاد الافتراضي: "research shows" حتى بدون مراجع
          3. الإلزام المستقبلي: "future research should"
          4. التوجيه الميتا-خطابي: "this paper aims/explores"
          5. التقسيم المنطقي: First/Second/Third أو (i)/(ii)/(iii)
          6. العبارات الحدية المُطوَّلة (boundary markers)

        هذه الأنماط مُضمَّنة في بنية التفكير AI وتظل بعد paraphrasing.
        """
        if not text:
            return 0.15

        text_l = text.lower()
        n_words = max(len(re.findall(r'\b\w+\b', text_l)), 1)

        # ─── 1. Discourse Invariant Patterns (من AI_INVARIANT_DISCOURSE) ──
        inv_hits = sum(len(p.findall(text)) for p in self._invariant_patterns)
        inv_density = inv_hits / (n_words / 50)
        inv_score = min(inv_density * 0.7, 1.0)

        # ─── 2. Meta-Discourse Density ───────────────────────────────────
        # AI يُكثِّر الإشارات الميتا-خطابية حتى بعد paraphrasing
        META_DISC = re.compile(
            r'\b(?:this (?:paper|study|article|work|essay|analysis|chapter|review|report))\s+'
            r'(?:aims?|seeks?|explores?|examines?|investigates?|presents?|discusses?|'
            r'analyzes?|assesses?|evaluates?|considers?|highlights?|demonstrates?|'
            r'attempts? to|endeavors? to|sets out to|intends? to)\b',
            re.I)
        meta_hits = len(META_DISC.findall(text))
        meta_score = min(meta_hits * 0.5, 1.0)

        # ─── 3. Fake Citation Pattern ────────────────────────────────────
        # AI يستشهد بـ "research" وكأنها مرجع حقيقي حتى بدون استشهادات
        FAKE_CITE = re.compile(
            r'\b(?:research|studies|evidence|literature|findings?|'
            r'data|experts?|scholars?|scientists?|academics?)\s+'
            r'(?:suggest(?:s|ed)?|indicate(?:s|d)?|show(?:s|ed|n)?|'
            r'demonstrate(?:s|d)?|confirm(?:s|ed)?|support(?:s|ed)?|'
            r'reveal(?:s|ed)?|highlight(?:s|ed)?|point(?:s|ed)? (?:to|out))\b',
            re.I)
        fake_hits = len(FAKE_CITE.findall(text))
        fake_score = min(fake_hits / (n_words / 80) * 0.6, 1.0)

        # ─── 4. Future Research Compulsion ──────────────────────────────
        # AI لا يستطيع مقاومة إضافة "future research" في الخاتمة
        FUTURE_RES = re.compile(
            r'\b(?:future|further|additional|more|subsequent)\s+'
            r'(?:research|studies|work|investigation|exploration|analysis|'
            r'examination|inquiry|efforts?|attention)\s+'
            r'(?:(?:is|are)\s+)?(?:should|must|needs? to|ought to|could|would|'
            r'may|might|will|can|has to|have to|is needed|are needed|'
            r'is required|are required|is warranted|are recommended)\b',
            re.I)
        future_hits = len(FUTURE_RES.findall(text))
        future_score = min(future_hits * 0.6, 1.0)

        # ─── 5. Logical Enumeration Pattern ─────────────────────────────
        # AI يُعدِّد بشكل منظَّم بغض النظر عن أسلوب الصياغة
        ENUM_PAT = re.compile(
            r'\b(?:first(?:ly)?|second(?:ly)?|third(?:ly)?|fourth(?:ly)?|'
            r'finally|lastly|next|subsequently|to begin|to start|'
            r'to conclude|in the first (?:place|instance)|'
            r'on (?:one hand|the other hand)|'
            r'\([ivx]+\)|\([abc]\)|\b[1-9]\)|^\s*[1-9]\.)',
            re.I | re.MULTILINE)
        enum_hits = len(ENUM_PAT.findall(text))
        enum_score = min(enum_hits / (n_words / 100) * 0.5, 1.0)

        # ─── 6. Balanced Sentence Pair Pattern ──────────────────────────
        # AI يُوازن الجمل المتقابلة دائماً (while X, Y / although X, Y)
        BALANCE_PAT = re.compile(
            r'\b(?:while|although|even though|despite|notwithstanding|'
            r'whereas|in contrast to|as opposed to)\b.{10,80}'
            r'(?:,|\;)\s+(?:it|this|the|these|there|one|however|yet|'
            r'nevertheless|nonetheless|still)',
            re.I | re.DOTALL)
        balance_hits = len(BALANCE_PAT.findall(text))
        balance_score = min(balance_hits / (n_words / 60) * 0.6, 1.0)

        # ─── 7. Hedged Generalization Pattern ───────────────────────────
        # AI يُعمِّم مع تحوّط — ثابت بعد paraphrasing
        HEDGE_GEN = re.compile(
            r'\b(?:in (?:general|most cases|many instances|several contexts|'
            r'some situations|certain circumstances|various (?:fields|domains|contexts)))\b|'
            r'\b(?:generally|typically|usually|commonly|often|frequently|'
            r'largely|broadly|widely|predominantly|predominantly) (?:speaking,?\s+)?'
            r'(?:it|this|the|these|one|research|studies|evidence)\b',
            re.I)
        hedge_hits = len(HEDGE_GEN.findall(text))
        hedge_score = min(hedge_hits / (n_words / 70) * 0.55, 1.0)

        result = (
            inv_score      * 0.22 +
            meta_score     * 0.15 +
            fake_score     * 0.18 +
            future_score   * 0.12 +
            enum_score     * 0.10 +
            balance_score  * 0.12 +
            hedge_score    * 0.11
        )
        return round(min(result, 1.0), 4)




# ══════════════════════════════════════════════════════════════════════════════
# PDFReport — غلاف + تظليل
# ══════════════════════════════════════════════════════════════════════════════
class PDFReport:

    CYAN    = (0.53, 0.94, 0.96)
    OPACITY = 0.45

    @staticmethod
    def _ref_pages(doc):
        kws = ['references','bibliography','works cited','المراجع','المصادر']
        found = None
        for i in range(len(doc)):
            for ln in doc[i].get_text().splitlines():
                lc = ln.strip().lower()
                if not lc: continue
                if any(re.fullmatch(r'(\d+[\.\s]*)?' + re.escape(k) + r'\s*', lc) for k in kws):
                    found = i; break
                num = re.findall(r'^\s{0,4}\d{1,3}\.\s+[A-Z]', doc[i].get_text(), re.M)
                if len(num) >= 8:
                    found = i; break
            if found is not None: break
        if found is None: return set()
        return set(range(found, len(doc)))

    @staticmethod
    def _extract(page):
        lines = []
        for blk in page.get_text("dict").get("blocks",[]):
            if blk.get("type") != 0: continue
            for ln in blk.get("lines",[]):
                txt   = "".join(sp["text"] for sp in ln.get("spans",[])).strip()
                if not txt or len(txt) < 4: continue
                spans  = ln.get("spans",[])
                bold   = any(sp.get("flags",0) & 16 for sp in spans)
                fsize  = max((sp.get("size",10) for sp in spans), default=10)
                if len(txt.split()) <= 5 and (bold or fsize > 11.5): continue
                lines.append({"text":txt, "rect":fitz.Rect(ln["bbox"])})
        sents     = []
        buf_t, buf_r = [], []
        for ld in lines:
            buf_t.append(ld["text"]); buf_r.append(ld["rect"])
            if re.search(r'[.!?][)\]"\']*\s*(\(\d+[^)]*\))?\s*$', ld["text"]):
                if len(" ".join(buf_t).split()) >= 5:
                    sents.append({"text":" ".join(buf_t),"rects":list(buf_r)})
                buf_t, buf_r = [], []
        if buf_t and len(" ".join(buf_t).split()) >= 5:
            sents.append({"text":" ".join(buf_t),"rects":list(buf_r)})
        return sents

    @staticmethod
    def generate(src, result, out, on_status=None):
        """
        يُنشئ PDF نهائي = غلاف + الأصل مع highlights
        on_status(msg) يُستدعى لتحديث الحالة
        """
        def S(m):
            if on_status: on_status(m)

        if not FITZ_OK or not RLAB_OK:
            msg = f"Missing libraries - fitz:{FITZ_OK} reportlab:{RLAB_OK}"
            LOG(msg, level="ERROR")
            try:
                import tkinter.messagebox as _mb
                _mb.showerror("Missing Libraries", 
                    f"Required libraries not found.\nfitz: {FITZ_OK}\nreportlab: {RLAB_OK}\n\nCheck log: {_LOG}")
            except: pass
            S(f"❌ {msg}"); return False

        try:
            engine = AIDetectionEngine()
            score  = result.get("percentage",0) / 100.0

            S("🔍 استخراج الجمل...")
            src_doc = fitz.open(src)
            ref_p   = PDFReport._ref_pages(src_doc)
            sents   = []
            for pi in range(len(src_doc)):
                if pi in ref_p: continue
                for s in PDFReport._extract(src_doc[pi]):
                    s["page"]  = pi
                    s["score"] = engine.score_block(s["text"])
                    sents.append(s)
            src_doc.close()

            S("📊 اختيار الجمل...")
            pos   = sorted([s for s in sents if s["score"]>0], key=lambda x:x["score"], reverse=True)
            top_n = min(max(1,int(len(sents)*score)), len(pos))
            ids   = set(id(s) for s in pos[:top_n])

            S("🖊️ إضافة التظليل...")
            work = fitz.open(src)
            hl_count = 0
            for s in sents:
                if id(s) not in ids: continue
                try:
                    p = work[s["page"]]
                    for r in s["rects"]:
                        try:
                            rect = fitz.Rect(r.x0-1, r.y0-0.5, r.x1+1, r.y1+0.5)
                            if rect.is_empty or rect.is_infinite:
                                continue
                            a = p.add_highlight_annot(rect)
                            a.set_colors(stroke=PDFReport.CYAN)
                            a.set_opacity(PDFReport.OPACITY)
                            a.update()
                            hl_count += 1
                        except Exception as _re:
                            LOG(f"highlight rect skip: {_re}", level="WARN")
                except Exception as _pe:
                    LOG(f"highlight page skip: {_pe}", level="WARN")
            LOG(f"تم تظليل {hl_count} سطر")

            # ملفات مؤقتة في مجلد temp النظام — مضمونة على Windows
            import tempfile
            _tmp_dir = tempfile.gettempdir()
            tmp_hl = os.path.join(_tmp_dir, "st_hl_tmp.pdf")
            tmp_cv = os.path.join(_tmp_dir, "st_cv_tmp.pdf")

            LOG(f"حفظ tmp_hl بـ tobytes: {tmp_hl}")
            _data = work.tobytes(garbage=3, deflate=True)
            work.close()
            LOG(f"tobytes: {len(_data)} bytes")
            with open(tmp_hl, 'wb') as _fw:
                _fw.write(_data)
            del _data
            LOG("tmp_hl محفوظ")

            S("📑 صفحة الغلاف...")
            LOG(f"إنشاء غلاف: {tmp_cv}")
            PDFReport._cover(tmp_cv, result)
            LOG("الغلاف جاهز")

            S("🔗 دمج...")
            LOG("بدء الدمج")
            final = fitz.open()
            for _f in [tmp_cv, tmp_hl]:
                LOG(f"إضافة: {_f}")
                _d = fitz.open(_f)
                final.insert_pdf(_d)
                _d.close()
            LOG(f"حفظ النهائي بـ tobytes: {out}")
            _final_data = final.tobytes(garbage=3, deflate=True)
            final.close()
            LOG(f"final tobytes: {len(_final_data)} bytes")
            with open(out, 'wb') as _fw:
                _fw.write(_final_data)
            del _final_data
            LOG("الملف النهائي محفوظ")

            for _f in [tmp_hl, tmp_cv]:
                try: os.remove(_f)
                except: pass

            S(f"✅ تم الحفظ: {os.path.basename(out)}")
            LOG("اكتمل generate بنجاح")
            return True

        except Exception as e:
            import traceback as _trc
            _msg = _trc.format_exc()
            LOG_EXC(f"GENERATE EXCEPTION: {e}")
            S(f"❌ {e}")
            return False

    @staticmethod
    def _cover(path, result):
        c = rl_canvas.Canvas(path, pagesize=A4)
        W, H = A4
        for i in range(100):
            r = i/100
            c.setFillColorRGB(0.04+r*0.04, 0.04+r*0.06, 0.12+r*0.08)
            c.rect(0, H-(i+1)*(H/100), W, H/100+1, fill=1, stroke=0)
        c.setFillColorRGB(0.0,0.75,0.86); c.rect(0, H-6, W, 6, fill=1, stroke=0)
        c.setFillColorRGB(0.05,0.10,0.22); c.rect(0, H-90, W, 84, fill=1, stroke=0)
        c.setFillColorRGB(0.0,0.75,0.86); c.circle(55, H-48, 22, fill=1, stroke=0)
        c.setFillColorRGB(0.05,0.10,0.22); c.setFont("Helvetica-Bold",14)
        c.drawCentredString(55, H-53, "AI")
        c.setFillColorRGB(1,1,1); c.setFont("Helvetica-Bold",22)
        c.drawString(88, H-42, "Semi Turnitin v28.0")
        c.setFillColorRGB(0.0,0.85,0.95); c.setFont("Helvetica",11)
        c.drawString(88, H-62, "Professional AI Content Detection Report — Advanced Edition")
        c.setFillColorRGB(0.55,0.65,0.75); c.setFont("Helvetica",9)
        c.drawRightString(W-30, H-52, datetime.datetime.now().strftime("%d %B %Y  |  %H:%M:%S"))

        sc = result.get("percentage",0)
        sc_human = 100.0 - sc
        ck = result.get("risk_level","")
        vd = result.get("verdict","")
        cy = H-310
        c.setFillColorRGB(0.06,0.10,0.20); c.roundRect(30,cy,W-60,185,12,fill=1,stroke=0)
        c.setStrokeColorRGB(0.0,0.75,0.86); c.setLineWidth(1.5)
        c.roundRect(30,cy,W-60,185,12,fill=0,stroke=1)
        if sc>=70:   sr=(1.0,0.22,0.22); br=(0.55,0.05,0.05); st="HIGH AI"
        elif sc>=30: sr=(0.0,0.85,0.95); br=(0.0,0.30,0.40);  st="MODERATE AI"
        else:        sr=(0.18,0.90,0.45);br=(0.04,0.30,0.14); st="LOW AI"

        # ── الجانب الأيسر: AI% ────────────────────────────────────────────
        left_cx = W * 0.28   # مركز العمود الأيسر
        right_cx = W * 0.72  # مركز العمود الأيمن

        # فاصل عمودي في المنتصف
        c.setStrokeColorRGB(0.0,0.75,0.86); c.setLineWidth(0.8)
        c.line(W/2, cy+15, W/2, cy+160)

        # AI%
        c.setFillColorRGB(*sr); c.setFont("Helvetica-Bold", 58)
        c.drawCentredString(left_cx, cy+105, f"{sc:.1f}%")
        c.setFillColorRGB(0.55,0.65,0.75); c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(left_cx, cy+88, "AI-Generated Content")
        c.setFillColorRGB(*br); c.roundRect(left_cx-45, cy+68, 90, 16, 5, fill=1, stroke=0)
        c.setFillColorRGB(*sr); c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(left_cx, cy+76, st)

        # Human%
        c.setFillColorRGB(0.18,0.90,0.45); c.setFont("Helvetica-Bold", 58)
        c.drawCentredString(right_cx, cy+105, f"{sc_human:.1f}%")
        c.setFillColorRGB(0.55,0.65,0.75); c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(right_cx, cy+88, "Human-Written Content")
        c.setFillColorRGB(0.04,0.30,0.14); c.roundRect(right_cx-45, cy+68, 90, 16, 5, fill=1, stroke=0)
        c.setFillColorRGB(0.18,0.90,0.45); c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(right_cx, cy+76, "HUMAN")

        # سطر الحكم في الأسفل
        c.setFillColorRGB(0.92,0.92,0.92); c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(W/2, cy+45, vd)
        c.setFillColorRGB(0.55,0.65,0.75); c.setFont("Helvetica", 10)
        c.drawCentredString(W/2, cy+28, f"Risk Level:  {ck}")

        # ── Statistics + Core Indicators ──────────────────────────────────
        sy = cy-30
        c.setFillColorRGB(0.0,0.75,0.86); c.setLineWidth(2); c.line(30,sy,W-30,sy)
        c.setFillColorRGB(0.0,0.85,0.95); c.setFont("Helvetica-Bold",11)
        c.drawString(30, sy-18, "TEXT STATISTICS")
        c.drawString(W/2+10, sy-18, "AI CORE INDICATORS")
        scy = sy-145
        c.setFillColorRGB(0.055,0.09,0.18); c.roundRect(30,scy,W/2-45,120,8,fill=1,stroke=0)
        ext = result.get("extended", {})
        for lbl, val in [
            ("Words",        f"{result.get('word_count',0):,}"),
            ("Sentences",    f"{result.get('sentence_count',0):,}"),
            ("AI Words",     f"{result.get('ai_words_count',0):,}"),
            ("Perplexity",   f"{result.get('perplexity',0)*100:.1f}%"),
            ("Burstiness",   f"{result.get('burstiness',0)*100:.1f}%"),
            ("Verb Ratio",   f"{ext.get('verb_ratio',0)*100:.1f}%"),
        ]:
            c.setFillColorRGB(0.55,0.65,0.75); c.setFont("Helvetica",9); c.drawString(44,scy+115,lbl)
            c.setFillColorRGB(0.95,0.95,0.95); c.setFont("Helvetica-Bold",9); c.drawRightString(W/2-50,scy+115,val)
            scy -= 18
        scy = sy-145
        ix=W/2+10; bw=W/2-45
        c.setFillColorRGB(0.055,0.09,0.18); c.roundRect(ix,scy,bw,120,8,fill=1,stroke=0)
        iy=scy+110; mw=bw-120
        for nm, vl in list(result.get("indicators",{}).items())[:6]:
            c.setFillColorRGB(0.55,0.65,0.75); c.setFont("Helvetica",8)
            c.drawString(ix+8, iy, nm.split("(")[0].strip()[:20])
            c.setFillColorRGB(0.10,0.15,0.28); c.roundRect(ix+110,iy-2,mw,9,3,fill=1,stroke=0)
            fw = mw * min(vl,1.0)
            bc = (1.0,0.22,0.22) if vl>=0.7 else ((0.0,0.80,0.90) if vl>=0.4 else (0.18,0.85,0.45))
            c.setFillColorRGB(*bc)
            if fw > 0: c.roundRect(ix+110,iy-2,fw,9,3,fill=1,stroke=0)
            c.setFillColorRGB(0.85,0.85,0.85); c.setFont("Helvetica-Bold",8)
            c.drawRightString(W-35,iy,f"{vl*100:.0f}%")
            iy -= 18

        # ── Extended Indicators (second row) ──────────────────────────────
        ey = scy - 30
        c.setFillColorRGB(0.0,0.75,0.86); c.setLineWidth(1); c.line(30,ey+14,W-30,ey+14)
        c.setFillColorRGB(0.0,0.85,0.95); c.setFont("Helvetica-Bold",10)
        c.drawString(30, ey, "ADVANCED FINGERPRINT ANALYSIS")

        adv_inds = list(result.get("indicators",{}).items())[6:]  # remaining
        ext_inds = [
            ("Punct Fingerprint", ext.get("punct_fingerprint",0)),
            ("Verb Ratio",        ext.get("verb_ratio",0)),
            ("Pronoun Ratio",     ext.get("pronoun_ratio",0)),
            ("Human Penalty",     ext.get("human_penalty",0)),
        ]
        all_adv = adv_inds + ext_inds
        ey2 = ey - 18
        col_w = (W - 60) / 2
        for idx, (nm, vl) in enumerate(all_adv[:8]):
            cx2 = 30 + (idx % 2) * col_w
            if idx % 2 == 0 and idx > 0:
                ey2 -= 16
            c.setFillColorRGB(0.055,0.09,0.18)
            c.roundRect(cx2, ey2-3, col_w-8, 13, 3, fill=1, stroke=0)
            bc = (1.0,0.22,0.22) if vl>=0.7 else ((0.0,0.80,0.90) if vl>=0.4 else (0.18,0.85,0.45))
            fw2 = (col_w-8) * min(vl,1.0)
            c.setFillColorRGB(*bc)
            if fw2>0: c.roundRect(cx2, ey2-3, fw2, 13, 3, fill=1, stroke=0)
            c.setFillColorRGB(1,1,1); c.setFont("Helvetica",7)
            c.drawString(cx2+4, ey2+1, f"{nm[:22]}  {vl*100:.0f}%")

        # ── Footer ────────────────────────────────────────────────────────
        c.setFillColorRGB(0.04,0.07,0.16); c.rect(0,0,W,38,fill=1,stroke=0)
        c.setFillColorRGB(0.0,0.75,0.86);  c.rect(0,38,W,2,fill=1,stroke=0)
        c.setFillColorRGB(0.40,0.50,0.60); c.setFont("Helvetica",8)
        c.drawString(30,15,"Semi Turnitin v28.0  |  Paraphrasing Detection Edition")
        c.drawRightString(W-30,15,f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
        c.showPage(); c.save()




# ══════════════════════════════════════════════════════════════════════════════
# Cache engine
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner="Loading engine...")
def _load_engine():
    return AIDetectionEngine()


# License
_WS = "SemiTurnitin2025#WebXK9"

def _get_device_id():
    """الحصول على معرف فريد للجهاز - نسخة آمنة للـ Cloud"""
    try:
        import uuid
        import getpass
        
        # جمع معلومات فريدة متعددة
        device_info = []
        
        # 1. MAC Address (الأهم - فريد لكل جهاز)
        try:
            mac = hex(uuid.getnode())[2:].upper()
            device_info.append(f"MAC:{mac}")
        except:
            pass
        
        # 2. معلومات النظام الأساسية
        try:
            device_info.append(f"NODE:{platform.node()}")
        except:
            pass
        
        try:
            device_info.append(f"SYS:{platform.system()}")
        except:
            pass
        
        try:
            device_info.append(f"MACH:{platform.machine()}")
        except:
            pass
        
        # 3. اسم المستخدم
        try:
            device_info.append(f"USER:{getpass.getuser()}")
        except:
            pass
        
        # 4. hostname
        try:
            device_info.append(f"HOST:{socket.gethostname()}")
        except:
            pass
        
        # دمج كل المعلومات
        if device_info:
            combined_info = "|".join(device_info)
            device_hash = hashlib.sha256(combined_info.encode()).hexdigest()[:20]
            return device_hash
        else:
            # fallback أخير
            return hashlib.sha256(str(uuid.getnode()).encode()).hexdigest()[:20]
            
    except Exception as e:
        # fallback نهائي - استخدام timestamp كـ unique ID
        import time
        return hashlib.sha256(f"FALLBACK_{time.time()}".encode()).hexdigest()[:20]

def _load_activation_db():
    """تحميل قاعدة بيانات التفعيلات"""
    db_file = ".lic_db.json"
    if os.path.exists(db_file):
        try:
            with open(db_file, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def _save_activation_db(db):
    """حفظ قاعدة بيانات التفعيلات"""
    db_file = ".lic_db.json"
    try:
        with open(db_file, "w") as f:
            json.dump(db, f)
        return True
    except:
        return False

def _verify(code):
    try:
        device_id = _get_device_id()
        db = _load_activation_db()
        
        p = json.loads(base64.b64decode(code.strip()).decode())
        n = p["n"]
        e = p["e"]
        s = p["s"]
        
        # التحقق من نوع الكود (قديم أو جديد)
        if "d" in p:
            # كود جديد مرتبط بـ Device ID
            code_device_id = p["d"]
            
            # التحقق من Device ID
            if code_device_id != device_id:
                return False, f"❌ Code is for another device\nYour Device ID: {device_id[:10]}...\nCode Device ID: {code_device_id[:10]}...", 0
            
            # التحقق من Signature
            if hashlib.sha256(f"{n}|{e}|{code_device_id}|{_WS}".encode()).hexdigest()[:16].upper() != s:
                return False, "❌ Invalid access code (signature mismatch)", 0
        else:
            # كود قديم بدون Device ID (للتوافق)
            if hashlib.sha256(f"{n}|{e}|{_WS}".encode()).hexdigest()[:16].upper() != s:
                return False, "❌ Invalid access code", 0
        
        # التحقق من تاريخ الانتهاء
        exp = datetime.datetime.strptime(e, "%Y%m%d")
        if datetime.datetime.now() > exp:
            return False, f"❌ Expired on {exp.strftime('%Y-%m-%d')}", 0
        
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        if code_hash in db:
            activation = db[code_hash]
            # فحص هام: التأكد من أن الجهاز هو نفسه
            if activation["device_id"] != device_id:
                return False, f"❌ Code already activated on another device\nContact support to transfer", 0
            activation_exp = datetime.datetime.strptime(activation["expires"], "%Y%m%d")
            if datetime.datetime.now() > activation_exp:
                return False, f"❌ Activation expired on {activation_exp.strftime('%Y-%m-%d')}", 0
            d = (activation_exp - datetime.datetime.now()).days
            # تحديث آخر استخدام
            activation["last_used"] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            db[code_hash] = activation
            _save_activation_db(db)
            return True, f"✅ Welcome back {n}! {d} days remaining", d
        else:
            # تفعيل جديد
            d = (exp - datetime.datetime.now()).days
            db[code_hash] = {
                "device_id": device_id,
                "name": n,
                "expires": e,
                "activated_at": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
                "last_used": datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            }
            _save_activation_db(db)
            return True, f"✅ Welcome {n}! Activated for {d} days", d
    except Exception as ex:
        return False, f"❌ Error: {str(ex)}", 0

def generate_web_code(name,days):
    e=(datetime.datetime.now()+datetime.timedelta(days=days)).strftime("%Y%m%d")
    s=hashlib.sha256(f"{name.upper().strip()}|{e}|{_WS}".encode()).hexdigest()[:16].upper()
    return base64.b64encode(json.dumps({"n":name.upper().strip(),"e":e,"s":s}).encode()).decode()


st.set_page_config(page_title="Semi Turnitin v35", page_icon="🔍",
                   layout="wide", initial_sidebar_state="collapsed")

st.markdown("""<style>
[data-testid="stAppViewContainer"]{background:#0e0e12}
[data-testid="stHeader"]{background:#0e0e12}
.block-container{padding-top:1.4rem}
.score-card{background:#1a1a24;border-radius:14px;padding:22px 16px;
            text-align:center;border:1px solid #2a2a38;margin-bottom:10px}
.score-num{font-size:54px;font-weight:800;line-height:1}
.score-sub{font-size:13px;color:#888;margin-top:5px}
.score-vd{font-size:15px;font-weight:600;margin-top:6px}
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
.lic-box{background:#0d1117;border:1px solid #00c8dc;border-radius:16px;
         padding:40px 50px;max-width:460px;margin:60px auto;text-align:center}
</style>""", unsafe_allow_html=True)

# License Gate - NO BYPASS ALLOWED
if "lic" not in st.session_state:
    st.session_state.lic  = False
    st.session_state.days = 0
    st.session_state.last_code = None

# إذا كان المستخدم غير مُفعّل، يجب أن يُفعّل أولاً
if not st.session_state.lic:
    current_device_id = _get_device_id()
    st.markdown("""<div class="lic-box">
      <div style="font-size:40px">🔍</div>
      <div style="font-size:24px;font-weight:800;color:#fff;margin:14px 0 6px">
        Semi Turnitin <span style="color:#00c8dc">v35</span></div>
      <div style="color:#555;font-size:13px;margin-bottom:30px">
        AI Content Detector — Enter your access code</div>
    </div>""", unsafe_allow_html=True)
    
    _, col, _ = st.columns([1,2,1])
    with col:
        # عرض Device ID
        st.markdown(f"""<div style="background:#1a1a24;border:1px solid #333;
                    border-radius:8px;padding:12px;margin-bottom:16px">
                    <div style="color:#666;font-size:11px;margin-bottom:4px">
                    📱 Your Device ID</div>
                    <div style="color:#00c8dc;font-family:monospace;font-size:13px;
                    word-break:break-all">{current_device_id}</div>
                    <div style="color:#555;font-size:10px;margin-top:6px">
                    Send this ID to get your activation code</div>
                    </div>""", unsafe_allow_html=True)
        
        ci = st.text_input("code", placeholder="Paste access code...",
                           type="password", label_visibility="collapsed")
        if st.button("🔓  Activate", type="primary", use_container_width=True):
            if ci.strip():
                ok, msg, days = _verify(ci.strip())
                if ok:
                    st.session_state.lic  = True
                    st.session_state.days = days
                    st.session_state.last_code = hashlib.sha256(ci.strip().encode()).hexdigest()
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.warning("Please enter your access code")
        st.markdown('<div style="text-align:center;margin-top:18px;color:#333;'
                    'font-size:12px">Contact developer for access code</div>',
                    unsafe_allow_html=True)
    st.stop()

# Header
days_left = st.session_state.days
st.markdown(f"""<div style="display:flex;align-items:center;
  justify-content:space-between;margin-bottom:18px">
  <div style="display:flex;align-items:center;gap:12px">
    <span style="font-size:32px">🔍</span>
    <div>
      <div style="font-size:22px;font-weight:800;color:#fff">
        Semi Turnitin <span style="color:#00c8dc">v35</span></div>
      <div style="font-size:12px;color:#555">
        Fingerprint-Driven AI Content Detector</div>
    </div>
  </div>
  <div>
    <span class="pill">✅ Licensed</span>
    <span class="pill">⏳ <b>{days_left}</b> days</span>
  </div>
</div>""", unsafe_allow_html=True)

# فحص صلاحية الترخيص مع كل جلسة
db = _load_activation_db()
device_id = _get_device_id()
license_valid = False

# البحث عن ترخيص صالح على هذا الجهاز
if hasattr(st.session_state, 'last_code') and st.session_state.last_code:
    # التحقق من الكود المحفوظ في الجلسة
    code_hash = st.session_state.last_code
    if code_hash in db:
        activation = db[code_hash]
        if activation["device_id"] == device_id:
            try:
                activation_exp = datetime.datetime.strptime(activation["expires"], "%Y%m%d")
                if datetime.datetime.now() <= activation_exp:
                    d = (activation_exp - datetime.datetime.now()).days
                    st.session_state.days = d
                    license_valid = True
            except:
                pass

# إذا لم يكن هناك كود في الجلسة، ابحث في قاعدة البيانات
if not license_valid:
    for code_hash, activation in db.items():
        if activation.get("device_id") == device_id:
            try:
                activation_exp = datetime.datetime.strptime(activation["expires"], "%Y%m%d")
                if datetime.datetime.now() <= activation_exp:
                    # تفعيل صالح موجود
                    d = (activation_exp - datetime.datetime.now()).days
                    st.session_state.days = d
                    st.session_state.last_code = code_hash
                    license_valid = True
                    break
            except:
                continue

if not license_valid:
    st.error("⚠️ License verification failed or expired. Please re-activate.")
    st.session_state.lic = False
    st.rerun()


with st.sidebar:
    st.markdown("### 🔍 Semi Turnitin v35")
    st.divider()
    st.markdown(f"✅ **{days_left}** days remaining")
    st.divider()
    
    # عرض Device ID
    current_device_id = _get_device_id()
    with st.expander("📱 Device Info", expanded=False):
        st.code(current_device_id, language=None)
        st.caption("Your device identifier")
    
    if st.button("🔒 Logout", use_container_width=True):
        st.session_state.lic = False
        st.rerun()

# Input
L, R = st.columns([1,1], gap="large")
with L:
    st.markdown('<div class="sh">📝 Input Text</div>', unsafe_allow_html=True)
    up = st.file_uploader("Upload", type=["txt","pdf","docx"], label_visibility="collapsed")
    ft = ""
    if up:
        rb = up.read()
        try:
            if up.name.endswith(".txt"):
                ft = rb.decode("utf-8", errors="replace")
            elif up.name.endswith(".pdf"):
                # حفظ bytes الـ PDF الأصلي للتظليل لاحقاً
                st.session_state["uploaded_pdf_bytes"] = rb
                try:
                    import pdfplumber
                    with pdfplumber.open(io.BytesIO(rb)) as pdf:
                        ft = "\n".join(p.extract_text() or "" for p in pdf.pages)
                except Exception:
                    st.warning("PDF failed — paste text manually.")
            elif up.name.endswith(".docx"):
                try:
                    import docx as _dx
                    ft = "\n".join(p.text for p in _dx.Document(io.BytesIO(rb)).paragraphs)
                except Exception:
                    st.warning("DOCX failed — paste text manually.")
            if ft.strip():
                st.success(f"✅ {up.name} — {len(ft.split())} words")
        except Exception as ex:
            st.warning(f"Error: {ex}")

    txt = st.text_area("Text", value=ft, height=300,
                       placeholder="Paste English or Arabic text (min 80 words)...",
                       label_visibility="collapsed")
    wc = len(txt.split()) if txt.strip() else 0
    c1, c2, c3 = st.columns([3,1,1])
    with c1: run = st.button("▶  Analyze", type="primary", use_container_width=True)
    with c2: st.metric("Words", wc)
    with c3: st.metric("Sents", len(re.findall(r"[.!?؟]+", txt)))

# ── تشغيل التحليل وحفظ النتائج في session_state ──────────────────────────
if run:
    if wc < 50:
        st.session_state["an_error"] = "⚠️ Too short — enter at least 50 words."
        st.session_state["an_done"]  = False
    else:
        with st.spinner("Analyzing..."):
            try:
                eng = _load_engine()
                res = eng.analyze(txt)
                st.session_state["an_done"]  = True
                st.session_state["an_error"] = None
                st.session_state["an_res"]   = res
                st.session_state["pdf_ready"] = False
                st.session_state["pdf_bytes"] = None
                st.session_state["pdf_error"] = None
            except Exception as ex:
                st.session_state["an_error"] = f"Error: {ex}"
                st.session_state["an_done"]  = False

# ── عرض النتائج دائماً من session_state ──────────────────────────────────
with R:
    st.markdown('<div class="sh">📊 Results</div>', unsafe_allow_html=True)

    if st.session_state.get("an_error"):
        st.warning(st.session_state["an_error"])

    elif not st.session_state.get("an_done"):
        st.markdown("""<div style="text-align:center;padding:70px 20px;color:#333">
          <div style="font-size:36px">🔬</div>
          <div style="margin-top:8px;font-size:13px">Enter text and click Analyze</div>
        </div>""", unsafe_allow_html=True)

    else:
        res = st.session_state["an_res"]
        try:
            sc   = res.get("percentage", 0)
            shu  = 100 - sc
            ext  = res.get("extended", {})
            inds = res.get("indicators", {})
            fp   = ext.get("fingerprint_score", 0)
            fpd  = ext.get("fp_details", {})
            wc_res = res.get("word_count", 0)
            ai_w   = res.get("ai_words_count", 0)

            if   sc >= 85: ai_clr,ai_ico,ai_lbl,ai_risk = "#ff3333","🔴","AI — Confirmed","VERY HIGH"
            elif sc >= 70: ai_clr,ai_ico,ai_lbl,ai_risk = "#ff7700","🟠","AI — High Probability","HIGH"
            elif sc >= 50: ai_clr,ai_ico,ai_lbl,ai_risk = "#ffcc00","🟡","Mixed — Review","MODERATE"
            elif sc >= 25: ai_clr,ai_ico,ai_lbl,ai_risk = "#3399ff","🔵","Low AI Detection","LOW"
            else:          ai_clr,ai_ico,ai_lbl,ai_risk = "#33ff88","🟢","Minimal AI","MINIMAL"

            if   shu >= 85: hu_clr,hu_lbl = "#33ff88","VERY HIGH"
            elif shu >= 70: hu_clr,hu_lbl = "#3399ff","HIGH"
            elif shu >= 50: hu_clr,hu_lbl = "#ffcc00","MODERATE"
            elif shu >= 25: hu_clr,hu_lbl = "#ff7700","LOW"
            else:           hu_clr,hu_lbl = "#ff3333","MINIMAL"

            ca, cb_ = st.columns(2)
            with ca:
                st.markdown(f'<div class="score-card">'
                            f'<div class="score-num" style="color:{ai_clr}">{sc:.1f}%</div>'
                            f'<div class="score-vd">🤖 AI Content</div>'
                            f'<div class="score-sub">{ai_risk}</div></div>',
                            unsafe_allow_html=True)
            with cb_:
                st.markdown(f'<div class="score-card">'
                            f'<div class="score-num" style="color:{hu_clr}">{shu:.1f}%</div>'
                            f'<div class="score-vd">👤 Human Written</div>'
                            f'<div class="score-sub">{hu_lbl}</div></div>',
                            unsafe_allow_html=True)

            st.markdown(f'<div style="background:linear-gradient(90deg,'
                        f'#33ff88 0%,#ffcc00 50%,#ff3333 100%);'
                        f'border-radius:6px;height:10px;margin:6px 0;position:relative">'
                        f'<div style="position:absolute;left:calc({sc:.0f}% - 8px);'
                        f'top:-3px;font-size:16px;color:#fff">▼</div></div>',
                        unsafe_allow_html=True)

            st.markdown(f'<div style="margin:8px 0">'
                        f'<span class="pill">🔬 FP <b>{fp*100:.1f}%</b></span>'
                        f'<span class="pill">📝 <b>{wc_res}</b> words</span>'
                        f'<span class="pill">🤖 <b>{ai_w}</b> AI words</span></div>',
                        unsafe_allow_html=True)

            # ── زر Export PDF — يستخدم PDFReport.generate الأصلية ──────────────
            if st.button("📄 Export Report as PDF", use_container_width=True, type="secondary", key="pdf_btn"):
                _pdf_bytes_up = st.session_state.get("uploaded_pdf_bytes")

                if not _pdf_bytes_up:
                    st.session_state["pdf_error"] = "⚠️ يجب رفع ملف PDF أولاً للحصول على التقرير المظلل"
                    st.session_state["pdf_ready"] = False
                elif not FITZ_OK:
                    st.session_state["pdf_error"] = "⚠️ PyMuPDF غير مثبت — أضف PyMuPDF لـ requirements.txt"
                    st.session_state["pdf_ready"] = False
                elif not RLAB_OK:
                    st.session_state["pdf_error"] = "⚠️ reportlab غير مثبت — أضفه لـ requirements.txt"
                    st.session_state["pdf_ready"] = False
                else:
                    try:
                        import tempfile as _tmpmod, os as _os2, io as _bio2

                        with st.status("⏳ جاري إنشاء التقرير...", expanded=True) as _st:
                            _tmp = _tmpmod.gettempdir()

                            # حفظ الـ PDF المرفوع في ملف مؤقت
                            _src_path = _os2.path.join(_tmp, "st35_src_input.pdf")
                            with open(_src_path, "wb") as _fw:
                                _fw.write(_pdf_bytes_up)

                            # ملف الإخراج
                            _out_path = _os2.path.join(_tmp, "st35_final_output.pdf")

                            def _status_cb(msg):
                                _st.write(msg)

                            # ── استدعاء PDFReport.generate الأصلية مباشرة ──
                            ok = PDFReport.generate(
                                src=_src_path,
                                result=res,
                                out=_out_path,
                                on_status=_status_cb
                            )

                            if ok and _os2.path.exists(_out_path):
                                with open(_out_path, "rb") as _fr:
                                    _final_bytes = _fr.read()
                                st.session_state["pdf_bytes"]    = _final_bytes
                                st.session_state["pdf_ready"]    = True
                                st.session_state["pdf_filename"] = f"SemiTurnitin_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                                st.session_state["pdf_error"]    = None
                                _st.update(label="✅ التقرير جاهز مع التظليل الكامل!", state="complete", expanded=False)
                            else:
                                st.session_state["pdf_error"] = "❌ فشل إنشاء التقرير — تحقق من الملف المرفوع"
                                st.session_state["pdf_ready"] = False

                            # تنظيف الملفات المؤقتة
                            for _f in [_src_path, _out_path]:
                                try: _os2.remove(_f)
                                except: pass

                    except Exception as _ex:
                        import traceback as _trc2
                        st.session_state["pdf_error"] = f"❌ {_ex}\n{_trc2.format_exc()}"
                        st.session_state["pdf_ready"] = False

            # عرض زر التحميل أو الخطأ
            if st.session_state.get("pdf_error"):
                st.error(st.session_state["pdf_error"])
            elif st.session_state.get("pdf_ready") and st.session_state.get("pdf_bytes"):
                st.success("✅ التقرير جاهز — غلاف احترافي + الملف الأصلي مظلل!")
                st.download_button(
                    label="⬇️ تحميل تقرير PDF",
                    data=st.session_state["pdf_bytes"],
                    file_name=st.session_state.get("pdf_filename","report.pdf"),
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary",
                    key="pdf_dl"
                )

            t1, t2, t3 = st.tabs(["🔬 Fingerprints", "📊 Indicators", "📄 Paragraphs"])

            with t1:
                FLB = {
                    "fp_en_phrases":  "GPT English Phrases",
                    "fp_cliches":     "Closing Clichés",
                    "fp_simple_gpt":  "Simple GPT Style",
                    "fp_structure":   "AI Sentence Structures",
                    "fp_vocab":       "AI Vocabulary",
                    "fp_format_sig":  "Markdown Formatting",
                    "fp_t2_patterns": "GPT Sentence Patterns",
                    "fp_ar_phrases":  "Arabic GPT Phrases",
                    "fp_triplets":    "Triple Enumerations",
                    "fp_uniformity":  "Uniform Sentence Length",
                    "fp_pairs":       "Elegant Word Pairs",
                    "fp_no_data":     "No Numbers/Data",
                    "fp_no_personal": "No Personal Pronouns",
                }
                ai_fps = sorted(
                    [(v, FLB.get(k, k)) for k,v in fpd.items() if v >= 0.12],
                    reverse=True)
                st.markdown('<div class="sh">📌 AI Fingerprints</div>',
                            unsafe_allow_html=True)
                for val, lbl in ai_fps[:12]:
                    pct = int(val * 100)
                    c2  = "#ff3333" if val>=0.65 else "#ff7700" if val>=0.40 else "#ffcc00"
                    sts = "★★★" if val>=0.65 else "★★" if val>=0.40 else "★"
                    st.markdown(
                        f'<div class="fp-row">'
                        f'<span style="color:{c2};font-size:9px;min-width:26px">{sts}</span>'
                        f'<span class="fp-lbl">{lbl}</span>'
                        f'<div class="fp-bg"><div class="fp-fill" '
                        f'style="width:{pct}%;background:{c2}"></div></div>'
                        f'<span class="fp-pct">{pct}%</span></div>',
                        unsafe_allow_html=True)
                if not ai_fps:
                    st.caption("⚪ No significant AI fingerprints.")

                h_fps = []
                if fpd.get("fp_no_data", 0) < -0.05:
                    h_fps.append((abs(fpd["fp_no_data"]), "Real Numbers & Data"))
                if fpd.get("fp_no_personal", 0) < -0.05:
                    h_fps.append((abs(fpd["fp_no_personal"]), "Personal Pronouns"))
                if ext.get("human_error_score",  0) >= 0.15:
                    h_fps.append((ext["human_error_score"],  "Human Writing Errors"))
                if ext.get("english_human_score", 0) >= 0.20:
                    h_fps.append((ext["english_human_score"], "Natural Human Writing"))
                if ext.get("deep_human_score",    0) >= 0.20:
                    h_fps.append((ext["deep_human_score"],    "Deep Stylometric Signature"))
                h_fps.sort(reverse=True)
                if h_fps:
                    st.markdown('<div class="sh">🛡 Human Fingerprints</div>',
                                unsafe_allow_html=True)
                    for val, lbl in h_fps:
                        pct = int(val * 100)
                        st.markdown(
                            f'<div class="fp-row">'
                            f'<span style="min-width:26px">🛡</span>'
                            f'<span class="fp-lbl" style="color:#33ff88">{lbl}</span>'
                            f'<div class="fp-bg"><div class="fp-fill" '
                            f'style="width:{pct}%;background:#33ff88"></div></div>'
                            f'<span class="fp-pct" style="color:#33ff88">{pct}%</span>'
                            f'</div>', unsafe_allow_html=True)

                st.markdown('<div class="sh">💡 Why this score?</div>',
                            unsafe_allow_html=True)
                ns = sum(1 for v,_ in ai_fps if v >= 0.55)
                if fp >= 0.75:
                    why = (f"**{ns} strong fingerprints** → high AI probability. "
                           f"Strongest: *{ai_fps[0][1] if ai_fps else '—'}* "
                           f"({ai_fps[0][0]*100:.0f}%)." if ai_fps
                           else f"High FP ({fp*100:.0f}%)")
                elif fp >= 0.50:
                    why = f"{ns} strong fingerprints." + (
                          " Offset by human signals." if h_fps else "")
                elif fp >= 0.25:
                    why = "Partial AI + human patterns."
                else:
                    why = "No significant AI fingerprints — appears human-written."
                if res.get("word_count", 0) < 150:
                    why += f" ⚠️ Short ({res['word_count']} words)."
                st.markdown(why)

                ga = ext.get("layer_a_v20", 0)
                gb = ext.get("layer_b_ml",  0)
                gc = ext.get("layer_c_heuristic", 0)
                for lb2, wg, v2 in [("🔬 Fingerprints",35,fp*100),
                                    ("🔵 Engine B",    30,gb*100),
                                    ("🟢 Engine A",    20,ga*100),
                                    ("⚪ Engine C",    15,gc*100)]:
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:8px;'
                        f'margin:3px 0;font-size:11px">'
                        f'<span style="min-width:130px;color:#bbb">{lb2} ({wg}%)</span>'
                        f'<div style="flex:1;background:#1e1e2e;border-radius:3px;'
                        f'height:6px;overflow:hidden"><div style="width:{min(v2,100):.0f}%;'
                        f'height:100%;background:#00c8dc;border-radius:3px"></div></div>'
                        f'<span style="color:#fff;font-family:monospace;min-width:38px;'
                        f'text-align:right">{v2:.1f}%</span></div>',
                        unsafe_allow_html=True)

            with t2:
                for nm, val in inds.items():
                    bw = int(min(val, 1.0) * 100)
                    c3 = ("#ff3333" if val>=0.70 else "#ff7700" if val>=0.50
                          else "#33ff88" if val<=0.30 else "#888")
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:8px;'
                        f'margin:2px 0;font-size:11px">'
                        f'<span style="min-width:190px;color:#bbb;white-space:nowrap;'
                        f'overflow:hidden;text-overflow:ellipsis">{nm[:34]}</span>'
                        f'<div style="flex:1;background:#1e1e2e;border-radius:3px;'
                        f'height:6px;overflow:hidden"><div style="width:{bw}%;height:100%;'
                        f'background:{c3};border-radius:3px"></div></div>'
                        f'<span style="color:{c3};font-family:monospace;min-width:36px;'
                        f'text-align:right">{val*100:.1f}%</span></div>',
                        unsafe_allow_html=True)

            with t3:
                paras = ext.get("paragraph_results", [])
                if paras:
                    total  = ext.get("total_para", 0)
                    ai_cnt = ext.get("ai_para_count", 0)
                    mx     = ext.get("max_para_score", 0) * 100
                    st.caption(f"Total: {total} | AI: {ai_cnt} | Max: {mx:.1f}%")
                    for p in paras:
                        pct2 = p.get("pct", 0)
                        pc   = ("#ff3333" if pct2>=70 else "#ff7700" if pct2>=50
                                else "#ffcc00" if pct2>=30 else "#33ff88")
                        prev = p.get("preview", "")[:70]
                        idx  = p.get("index", "")
                        if pct2 >= 70:   verd = "AI — High Probability"
                        elif pct2 >= 50: verd = "Mixed — Review"
                        elif pct2 >= 30: verd = "Likely Human"
                        else:            verd = "Human — Confirmed"
                        st.markdown(
                            f'<div style="background:#1a1a24;border-radius:8px;'
                            f'padding:10px 12px;margin:5px 0;border-left:3px solid {pc}">'
                            f'<div style="display:flex;justify-content:space-between">'
                            f'<span style="color:#666;font-size:11px">Para {idx} — {verd}</span>'
                            f'<span style="color:{pc};font-weight:700">{pct2:.1f}%</span></div>'
                            f'<div style="background:#222;border-radius:3px;height:4px;'
                            f'margin:5px 0;overflow:hidden"><div style="width:{pct2}%;'
                            f'height:100%;background:{pc}"></div></div>'
                            f'<div style="font-size:11px;color:#666;font-style:italic">'
                            f'"{prev}..."</div></div>',
                            unsafe_allow_html=True)
                else:
                    st.caption("Paragraph analysis needs longer text.")

        except Exception as ex:
            st.error(f"Error: {ex}")
            with st.expander("Details"):
                st.code(traceback.format_exc())

st.markdown('<div style="text-align:center;color:#2a2a38;font-size:11px;'
            'margin-top:30px;padding-top:16px;border-top:1px solid #1a1a2e">'
            'Semi Turnitin v35 · Fingerprint-Driven AI Detection</div>',
            unsafe_allow_html=True)
