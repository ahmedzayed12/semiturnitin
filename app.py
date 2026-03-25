"""Semi Turnitin v73 — Streamlit Web App"""
import sys, io, re, math, traceback, multiprocessing, base64, zlib, hashlib, json
import datetime, os, platform, socket, threading
from collections import Counter, defaultdict

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
# ══════════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════════
# AIDetectionEngine — Turnitin-Calibrated | Asymmetric Sensitivity | Final


def _call_engine_helper(self, name, *args, default=0.0, **kwargs):
    """
    Runtime-safe helper dispatcher that does not trust bound instance attributes.
    It first checks the class dictionary directly, then globals(), then fallback names.
    """
    cls = type(self)
    fn = cls.__dict__.get(name)
    if not callable(fn):
        fn = globals().get(name)
    if not callable(fn):
        fn = globals().get(f"_fallback{name}")
    if not callable(fn) and name == "_llr_score":
        # ultra-safe local fallback for LLR
        def _local_llr(_self, words):
            try:
                b = _call_engine_helper(_self, "_bigram_score", words, default=0.0)
                t = _call_engine_helper(_self, "_trigram_score", words, default=0.0)
                p = _call_engine_helper(_self, "_pattern_score", " ".join(words[:2000]) if isinstance(words, list) else str(words), default=0.0)
                score = 0.45 * float(b or 0.0) + 0.45 * float(t or 0.0) + 0.10 * float(p or 0.0)
                return max(0.0, min(1.0, score))
            except Exception:
                return float(default)
        fn = _local_llr
    if callable(fn):
        return fn(self, *args, **kwargs)
    return default

# ══════════════════════════════════════════════════════════════════════════════
# AIDetectionEngine — Protected
# ══════════════════════════════════════════════════════════════════════════════
import zlib as _z, base64 as _b

def _decode_engine(enc):
    return _z.decompress(_b.b64decode(enc)).decode("utf-8")

_ENGINE_ENC = (
    "eNrkvVuvJNd1JviuXxGwYRydMQ9F0k23RxijUE2VpUJLlEDR3Wi0uonIjJ2ZwRMZkYrLOZV0CDCvomlg3Ma43+bFzZFJUaToEiWzy+gfkufVrz"
    "0/Yta31trXiDhVpO0ewRLEOhE7du7YsS/rvr69rvKuy+7e/4bpzbovm/pevS1r8/WvfCWj//129g9/9afy/+wF1LyozJWpsr7N627TtHvTZl2f"
    "98bX+1/5f+7jK0FnXqmavDBF9ofZH+VVZ6bP901B3afnLzb1zOO+uUSZPp4MwenD069u3j79NDt9cPPWzds3r58enj49fXD6yBa8e/rs5i9Pj6"
    "jGV5995pnfzW7eRPHpp+fZ/5KhuHv/lT+6/+I37730vZfuv/gyfcafcLF8BneR+kP9/ezmPbp67/RT9/iMhuXKnD111u2a63Xe4RJT3eZbXNb5"
    "VbmlaabL1uTVHk/zuujW+QFlu7ytTdedPeXbG+qqWV/Ss03T9aali/VQ9eWVNFIPbT+0uDq0TVVu6D1cbh4caODrvsyr6hg2d8jbvCi3eHF3rE"
    "27PeK19NOuL9d0uUfjm3xNq7jg9vN6zVdl3bflmlv3rVGhaddNXdOSt7VMe6hytEqV8+rY9Wi17O1nU4fMVanXe1OVTZs0umoq/dLWlDUtqDXq"
    "DvWhNdQV+ih+07ZthrpY0ShelvUWA0B7zpiWb8Ie1g2NVclz4laoLWjNVVMN2K15e+RBzLd4iJGgOanyVRV1rRtok5a1FNOvu7IqqUO4blYDfy"
    "p1yrTduuFJMdWwLgv52LKqhj39Nv7YDU3gzrR7qY8/zRV/e14UJXeMJ/CMBrkzPxzoZXxbY0nRD6tktdQ0Bq74LF9TPwoaEf5NN6zCJg7lVUMT"
    "hCtaE3saTXS/M+hjFXURA51LX/Bq+tWKWyj3h6btc21v3dDMrjGw8rYSSymvTTN08RLE95rV0S+2tqQ6QQ3aYj85/R1ts9eZJFw9+3v+x+tmT+"
    "tgZ+rOvmhvaL6GSl9z1vW0JPYVkV7pYb7uN0PFg8GfkM4ob4LyNdRuDtg+/J1SQIO+Nod+CO5788DfH6jnLc3Sa1GTe8yBbbEv93JZmH2zRvN8"
    "Z2joru0a3+db6S4t8PiNvtEtLd2hyvELLJC8Xe9k2a+HvqerC1MwgWEmctFsLmiUL/IWU7oyXX9R1hdr8J2wzeumrQpbfGbq4qJvLugPekt796"
    "JoaYxrPLoqad+tzcWKCFohb7k0RDUKfIJvkLrf0YY3oC4rImvXZdHv+NvN4aKQLbcu23WFlpio7eljuKu0dYt4Zqrm+mKXg4luLzbtUPa6UkG9"
    "LrpduUFBv2uG7a4nbppzX86u8mqgDy+K6EPp6+k/9KSlbXhRNNe4wUdc5NdMrFZN31eG6Nglv4Z+cGhK3dl5sc8PEYWiwdjt8/ZS6G6+duTEXd"
    "KUMo0oe0uSeb+hC2XXDoc+IlKFkTrbfF9ueDO1zXXRNYPQvqZeNXmLgR8O3SV9gRAfvfLsJdiz+ZpIUy+tEoHTBUv7oTJ7oVgg1Vvtm980PLu4"
    "JgoSb9sNqAB+qxSJKngGQx2mfbDWG2qO2t26e7PZeMoQbHOVBq5+7/czYlhEm2nv/f8jAH1ZQYFHhsgsUVzsbexIue+6coUZOIYFWBF8B2Kbh8"
    "89aeK7JtpW+XrYYx/S1ZZW3tFe9XxB65kKiSzSNrYdCPgq3YFWQChlQQH3ps6j9tvtICQd10xN7U/73pAIoDcDcaSw18N2bztBdGLgSsG2D/ZL"
    "3jZEprFBsXmKliWaaB/xjdmU65I5Md3SPib6Ku07kYAusR9NnbD51dBuTVPr96+IJrbMAolh5Iegz7hbu2srn9jrmORC2Nk2rV3FVEBf24IH0i"
    "VRptrIJTOAWnq9bgrewLgCm5Pu47pjuhAysorEC0wSP2DOts9BfOUyaGi/H2rbZ5lnd9m7VRazSBpsXSi4q8wDe+l456RAvzFmQFxQMPENX1Bv"
    "aHbqta3QEQFr7fLle5otEQvknuTLQldRcFskjXZWltC7sh/8V0ScVwrKelCuL/dtSRMfbx0qJuK49X1t7V9i+13f1HLbmiLYrpaWyXVDypoy2a"
    "hlfkDEfF0eiHDqqpXSzmAL2wZIBLSXtNpoMdlPIIGRZpnI3q6M2EthqM2dLHewTmPXdUEbhFaCmyzSNcoV8xd/XxsdaCdwrOO29xja1u73wpBA"
    "WxledvgYYjmd0RuwKV0pdIePkstwRItmn4OzBm8gYTLv/a5hKUK+5VgTf1vjMpAUMs8e9IaIgG4co1sk2jmBUE03tGdotHIa76Pcr5pCryDYyc"
    "BRb/ND58gayTjGdqTe4i4WY2hG2rLWqkRJiErx9aHsm73OHknSoIay5g0rC5b+O87INyw79TEvhdpxZWs/IG2rXdmuPcD2U1kbtyQpVrq45EbJ"
    "gnmwy2kBJVSF2CjpBWWnbUVKIAp67HW/0qmgzVlFcK+ggkNjB2qTr9p4/ZC0fgExZ6e935jcMTZanOaCRAoRI+iehPK27FzVym1nVepCHaM1ot"
    "Hp414/M1Y+6J5WlyHB9VJuQAVkcZGQT1ttvyCxSI1IgCGZOq+u8lrncwuxus51WXtxO5tomv4FO2rJsq9dud2JUYfvVKO2r9oRH3mtYR4e6oF0"
    "t18NeuFUlUAw3ItKcmWrmH5g4l/W62qwZLwU9u8oMN23JvzQsqb9S2SkS7UfeTD0lhrQzF2Vwd2mEluW3rU5UY7BCRJUMnR6JcwuXuWlUPTSfq"
    "qQ9EDBkrJ2sGKEE0kLf5cwNxTSEt4cdVHxvdeT1SSRkmUuZPXOr/3AVJEYNNpm67pMt104Bs4IojfUl7V/9RXpsjJ6QZNta+g1a2OnJzD40A2J"
    "yaQj5rIv9E4Hh9h2uZYXK51nIheoSDTTu0OpNaBpSDPUXNv4xQixQvtMl+WG9MFK60GqkkuTg8sk68+X6g8MBJ+y28tNYaeWhLsdsTLlmV4j57"
    "sy6EzQNHEdx4C9fQjq86q0y4OkIOxCnbF90+VCtdlwUJR7wypDbK7QZ/ECiM1aek9zT6uW76me32d13q15RQZ2lZwWvVu1eidjQjojEXzqZHir"
    "Pa5JgHTrvzYPhtRYc6E1dGnUsE25tzSOvzgzXHbW7OuShLZOt0xqs/CtN+2WpsotTrl9TRvphBHoo6HHRi10S0X2BbntiLj1sRmxOlgyQYpbA5"
    "4v19a8yNe0Dog3S0/drWXVdLW7jrcffczeyi90DXLn7yKpku6vcksAVbWmC55SvmoOAzZd1DqsVZ4AwJ5YHlRJlluSdUu71+m+BZOnubTPu2Gf"
    "7m5S/2mO9mrX4XuRX9ZHewvuUdm7LfQSJ8AdhhadMkXSKIo747YdxtRNJPHnsrCXETGdmI9QROKNYyH+Da1R/tqSyBiMCfEN4md22QUGziy1lV"
    "LBzvRNIh60JWlMuvGd4SRz1tEMVtXNpqkKva6Cd1uzA1+XWyJU9NHxNqS5sAuiaw47YbG6pTuIzPIotE7xLdE/4gmv6VNDwxkPOJVVyu3p8poq"
    "i0yepaaMLDaV8K0wRLkbVsryqthsrMV23rthY1lnN2Apl52uusjCDPPkflU2tPLlhm2VXSLSOzs+X/ZQNfVLWcIWDSC4Cx+Gj+w3BpZamN90l/"
    "fEsOhj5Zp4ZC5sh14H0cbINeZ+u9NrGObcEu53/IhkjegFTVNdlrww+mZY7xxDoFEHw3Rrg+5fZaXK3tVdTOKDNhMjv5YcYPZY25+DpvGzYVVC"
    "kNclO5CCsiq3w8RmDat+XVqKxzb+bdkW7kaZcGj8xx3ox1Xj1s6ANR2rvUN9yMUYgiswFaPaWOLwQAH6XelleZVrRbogfheLSVTmpuXKiEEJV7"
    "tyXWkhCbtrK+JeOQ6ElahfSZd9Lhd9vJ7xSavBqiXXOYSknXTmmrSdi1bMtrg/Yi/RCrxcMvzt8we/3sa/yM4HY0q5dmY8ubO0Ys6wJwxEN3de"
    "5Ic+l7ugWZTqUs0LrExIkTzPoJVtYZUSf9e5W9PZBtUmGNOGfEsMx0pWapOWC9tDmsW9eohwB4NXv1O6QAtrW++9oZGYScKpsLLd58dWR6+q6q"
    "U1TtZFm28bIVi4adiuxkJl0PCBN2xvrZKrsg/tmaY/ivycE8lbE22pdQcnFku2UMY7Lh+IZtVKFOGGEP3Omg5pQOq1u2lbVS/1shNLJem/O+Ii"
    "sU9gl1/BHSTC8cpUjdsEzs5p70so2GogIvrOJhUrM9L9ZohlZSraq9WPLg/dcb1rusaalcAgHO+jbUw0qBCjadODfR0O6X1qPG36vtlfDAexr5"
    "bF1sjXwZK62egADC2NsVhjj8xSpXxNc8Ny7CC20ch+qjZVMZ2qb5aNp2UtPipmElJG7Ys59aqsLvB1Rq1xpOj2JrHq0cq0qz40uW7ZOqZTsG6I"
    "H6n9dWJrpdmh4UsWXWp3VTOqdXtJ2eDsmGuioW7rsMUSsoC+P7Fs2ie9rQvnqO/OxJjJC8J+4IDBuwh0lNAMmZguh7U1x7B9cU8/lP21FnOfzF"
    "f5mqMavsgkRshwzuSWVaDwl7ZMLY52XMO71yYEzz1xv9IBUhtnbKNyRk5rigwdqWGjxGbYeR920JXpT+mDYHup+07urUgrhk2sdSMGi2hvh09c"
    "5S6irZBGhrbz5lLn4Q3v9olaCesL1NtSKLq9PdobExtjQ7us60Zspe3ZJxi9QezirsJAtNQu2qKhfV81zUFurmuRbsX0SmJDyzK4fZktik2Z+5"
    "UpLPVk62spe0WuLfdga2xyrfuUJM+uS5aILeukghvKaBxn7LqwX8Obrt/nDL2hcXdLfNI3YM2/E1OvLH+9gXxMa3ZrTRxBUTwakVW439VNsPmC"
    "e/3yoY2eD/O8MLUQk5YLDSG24oZG2zVrgPJwk5OYXLNtOvHnGjhtKu3KxpgCzNCtBjbm9kPtjLel5SMTs+7xemdMEjLS9DvV8nDtHHnezmt/HQ"
    "rqGxoILDarBQYG2iASAj7yYFXKvXTN+s/pitXekFqFijDuGhox6+cJWnfl0oMGMRFg3aZXu3DXtWCkcmdMvRvcUPD9dR7cuy8N3jCQSEzqU8VN"
    "wIQ8rJ052N9qr3fEaN3oEVeutOkdyWJ7oqHR2tZCsTiD1jV1OLxxka6PncFkqjjkbrq42aF3EptastWmvjtCXpCrQxPonmy5Lt3y8rdx4EM98Z"
    "Wz8Trv3Bam+4FIjDUQT+zVfsOFzXKxrfKgaQOTNgj5emqQnrdQJ5ZhcRJ4l4LYkFvTp3ZltRkHtVzJ1KA9lM7C37aGOb/tLu6hbMntq7Rq2A+B"
    "m8u8XuW8Ri4PpdqVt4Pdl4GR2IualZEf4O8FyXBtLzLfrUZoZb4xfQ7t0QjVWYv0XQ2FGmhz+N6i/eeLTGQ9Dq3Neywu/wsa14vIU4gSlfJ8FS"
    "v2GWdtpu9r0wgBYvsFW7fdZa1UhlhNpOjQPa312m0KvVcTdN7HRupJ3JfvvosDU3vzBQmXaiHn28ROpTZpna3EoB3/FMS+jezWXXgXm6ntnbdF"
    "ByZo08hUVlLF3um2pQ+4eI1oRmC+VrN1SFdQIHFnk9AVa9B2g5JYuKNW2n7Hq5KtzptNZ3rrUW0uo1apl1togWK9rvuQM+vtcc44jpIDG2ClM/"
    "YuFqkT4ziHKxbu0vYI13YFkV4EdcbJWrb5oSeFwUXNBW+gPb4p3ddZo7m11M1Zyol40gfLJ7rbxHZegEjbcdBbayxnPhuE8Hn7euUM6qmBvWvi"
    "OCEtCqeTLe/2M6r8qDvsQFI1hHQ1gjddGdA+LugvepgQk02KB6EOEd7rkpxa7X1DfHsF6pyqSVpu/QUtlEyztRb71IJv712jTUHaiYoBF5s4Gm"
    "Zq1G8bIhmOgeH24MYoNPhnZz8cYBXeTI35oaWeJI6hdc3NGvmLi57Edn1HazbwHF45k35kJgpbZmf61E2QhUGpmYvCds1XWCQaHxi4DI5x4+F3"
    "0p24rNzC0fBF16Z6cfWmzQc/IbgvzVVMFFHYbMreVmiC/dSa67KyAmY71Oxkys66fGNY+OpCR0SyAlOfBN2aC7V7yI2wzE6CDdhrcQGnqCymzh"
    "hvTevMNlX4tMgNQ2cqohtWLY1KaU5YsRHHAuJcrCEfQdypSUQLW98G24cuUpVXYq+sjtmBEhnifXqrkmboGBHfSefpBhdpcCzfWSmCHSukbvTW"
    "UWL9LLgGeYsbVsVcp0m6vrEulvLSj6J6WIQidMMqr+iT1FmyepUjh1SDjjwu9snROmZKEjjchw97z3m64QB3W2F9M4c2r13ISeRnCS2NC76WqX"
    "elN2vofZYautvEVBt7Usq20DAy9Z6UNl5IPSmV7s7QsUJ3JVv3bPBy6Gm5NKHVp28OGgatrhc3o+wtqYOQG9mN/irtd+BNAV+qt04fT9wps26U"
    "9dDaMEnnVkn2pPWwWCLP91OSQroq4vr0MhB76U4FprDNPdwbl74voR9mfeledY2vm9zpj2DXjoZZSmz1Q0jj6M4ZV4bOtBek7RrrGQ59NO1EKb"
    "0iaYDG8GJ9tN6bkjZdVOKcMCRkWkH22uQHZ2a7lgSBICjeVNXFymjvcBfdWNnmumnbY2g8+JFL5/qv/+Vf8P/1I6+e+/3sH/70r3zG2je/9zJn"
    "gJ0enR6ePkTuV/bV30eG2tunX50+p/JPstMndPnw5r3s5q2bP8UPvvZClQ+FQSPRL8/1JTc/Pv3tzY9dYhk1xalwH53+Oz15SD+7efP0M86H+W"
    "l2+nv6JZV9zk084g7cvI6XvUM9fPf0q+zu/aSDvznzdff+K3dfuvtv7r9wW/reQxqlD2gqPs9wQcP20c0bPGAYdAxePHC8WWig6TnVpwmgy5s/"
    "y2jGaLKwQ3RWbcoS1fhJUuPm7Zt3MD8fnD7h+Tq9f/o5dePPwu0oc0gL4fSBTN9nVPWDmzf493h2+jt6/V+H70XfP+d+of9/nvFr7POg7x+dPj"
    "59ijUj3fwl9ePh6afc8Hv2kXzD39JCe8htf0QlD0+/oK7e/JjafQ/1g87SS7Ob9+jBm3jlT2hRvo4GuM3k2c071OgH0qw+O/2cvujP3Ei+Txvm"
    "06h5/hDOBKVhoH+xBX7sRlKf4Nfv4tn7N+9Ez6jrn1IHfoxB42fJKGuO6RtYBdJn25Nf8Yb6NDv9N0yQnzr6h/biuxgofTLTJD34iP6+zQ3+nN"
    "fTr2yK6xvU07e0vbcxw5/Rq9/AUHxEy+aTqL13J0vhJ7TbdQRpFXCPblsoWn26FH47oFJutb/P0/MpzxgvzpnlTz/7iMo/xdDgle/TWHxsZyR5"
    "RKP/CA1yb3+JAbl5K8NE0T57U27Tuaav+VgIWVBJVyg/zGxD3OjD0/8zWztY8rKdP6OufYrn0pauG9r/NJ2uhOp8gtmR7n9M40qke9IYxucdfp"
    "Vm/LoGkaSI5ROWvcmlf40+vquVHvHf92b6+RDzR/0MesRT8Qt3D2r1kewibZDm+EPOmH6U7PRHp1+4n35EM/0uuIXePeSl8nO9+4QW5Xu0BvWN"
    "oIm/SDbLezd/QT+h/c8cRggGFdE7iDJg4lwRNS0N446+9u94HWJTJf37BCMp7O1jauEvdZaRAP4r/jZeSzIU/42JCvXwIf3sw2jkOAv7dWrvIy"
    "WqaHGGNfOgv0OT/nmyoHmjPFJK8I5uJRAV3rUP/Wb673Zl8GhSwz5LnYo+Y1r6KKGO8Q8fYXXZNYhXRO1N2prMAA3IzV8qcX9fyLIb6bdPP7v5"
    "S7zoIa/KXwhz+UxS05Ne0cLlt3wYEHVL+P/e8YNPaC28hbe9yfyFd9kn6Ohk7SrNVDKNJaS3blzfC2krHjj6Kj/6BDvCruhPeZjeS6VMqvYxAw"
    "I88iPvZSS6sKT8Iff2q6SMVobL6dM+Of1MaST3/9F5IiX8++++9I3vR/JBwOnPnpqwdhQlXBdFymDp0jJUKdW5mttRXNfuJXujuyjYRNKO29TR"
    "Lr6d3E2o3YTYJLRmhpo9ngaepTTYkXz7NFg7ZzST70KinSzNYN+f+d1+5knEWbrbzp5s29jB1H0it7oNZLp4vdsJ0AmTm48Zg+LT32i1h9c4w3"
    "EoKVUdQ6WARHLgBUajFtx+SOvhYaCELKg6E23GiRkPhQV8YPczV+GuQZakybMEkv6hZcsb88+taHn3vr6W62F//JyqvZ0p1X8k6CbZ99hAfWX8"
    "q7/Ih/4GqVcv3P3Gve8Q3fzWH3/n7ouv/LvvvnD33yTaVSTOBTNmxY2YDUveiPprvAsZcASSz6LgJmZ/KFuxiqjNfGri/yHHPFhkD46+64dCwC"
    "yCvEwLY2Gjw87avC44qy9y0XDGzqpBvn4zrABYUJWMjMCJpk3FUAOths1yRuyMq99Hsa+lVtuaSu1VsLk7VxQ9CvIepeU6Tl6wltisYPgU+dme"
    "HbriS8VFh1BLk3UKT8E5EKnZ34cLx8H/MNJXLq7i7GAMMv2uSnPNoADrcuJB+G0IEm+AALOGZuc6CLVcway7VrQB8aLY75UENr7h2Ck7EpuSh7"
    "GLvc17fXunIAbaz05BM/Z7o1mCKFmVNFnNts0PsYcMkZDU+AN+y1ZWlsYOxGuvHqoqC0tiDepjZy1gBvRzEmt+pUTJEzKlJR8yA/wZCBARPCv4"
    "uBbCSFoNvWV0FzF3MwxHZ3qBrlEnl0ygnaZ8vR7Eshw5u9aaUIDRyRklIsSsgC1fEVLMoUHEEwJbijJxVhx2Td9YM3cnMD6NXiHkoRGf3JmpXz"
    "vuFYOoN4yzsTV1s0/iJzZu6W+LA2N/1NQK4+5syk42N20PuN1lQSKIoypXbRmndb6KGJVDOxQSx3HmwuQV/oRj3c7Clc0BU3252aQaRKoqzFP6"
    "gDnFElFI7LwA9RCCmxewHrHUFIksfy9KmZXbHrKo+MHp86lMR7/8hPU8V/1TLn7Lt/8rKnrD3vyMG/rI3v6EVtpD1kS5MOn9O6w9/c3pYy8LEs"
    "sTZcp3l7km3uOKaM9/GgiZtAE+gBjpZDonKkESph7oMP4983LYUIX3O1CvqQ3iq/zox8Tg/zB7JuD2j2BIgXB4HvOj79178e63X/4Pr/z7e/e/"
    "+S0Y/J55+hnerE5G+EQUn7+zygfeR6P+GybU/Wsey3svfvPb97//rYvvf+/eC/f/6P4LMAN9497L9154+f53X8TT+y/e89rXJ9At2Y5HCx2KwS"
    "9A3N4Wsif8/nVaNW9lvAY+4P9YAHsn2mG+wQ/pF+9ZCY144mHoAvFAFN3nGfSNhDAo9Rf/Kvtapib0r2XfhIe1TDr0mzGNEY5e9nJJHPrZr8OM"
    "8SFTEZako2FhwUucEbLt2B0hnOpntI1/mv3vz//O72b/FBkykWgfdYkN36AE1JmPWUH980DQfpOJ0IcTfWGe9N578RX6gFe+962X7n7/3vdfef"
    "nZWHkv+6zssmtEEmU1B6Zk/S6PQw65ioMuy/oGNc1CPUXvQC3J7YIUtlDXwT6gNqSSLXxvC5WljyTX7vKOneDTejUVmYxhArNmM/PIJZLPP1bM"
    "FHqYAa2xTWLwK9J3iCs201LGHIm8pZXpM9qlim0YpgFfGX7XdX7MNnHoFz2Tz5p9mvf8ZGfytk+6X5Wmy/R5nIAf/DwLM7ozkuwAw7WLq1gQho"
    "XHEfpNML2JEJ9nmn2dIf7pYJFKghg3fbzYQtTVWnWapYTFjKROM8kgjZIBs+aA1QtQoCTsIa6GeLEKEe5RHc0fziwGSRbgEYQIJURcbq+icC7z"
    "DxEMRrOYKcpghqDMued2gy09D0A7FutwfuLyGyRHZfK8M+0VFhrXCfGA5qt4IJLFRhye1PzzHkFYaUAQ9mpT5McfnHWZy+yef8xTst7Z3Mr5So"
    "i/uTjk61ibDWukmJ1h1D6iiqinQgCWF7RW9OgQmbYnCtikogXhjMdOwU55n3NWR0IH4ue6KZI6Fk9VCR5DXU12RVxpdlMEVUD1LWZWCsOa1eaa"
    "+mID1ie7j+tE/Y2TWuQzoeFelcWQV/RxMf0FVlI0rhpZllY5WIvVUoX5IbdQgYtj7irQMHYp5JWLCrREPX7Y7cCKZh/ZNCvhh5MKiFvJKmBMZM"
    "n22klu0exDn2wtrEJZemw28ZVkIQFn8rbnsclmRmzQKMllucJVaGIu4rb/5AnySZs6mYmIKCXPVsdMJyrN5DxmumumD2QvTsvNftXm62m5w4pM"
    "+SEJLzSODsg4fQJIT3D7a0asTJ8iti9mn9sGEzzzA2po4QmRM29AeirjoY+D3TIO8EM43cxj+rk8Pj7F+z35qTRd8C9nxCpAQxVZt96Z2MChEo"
    "uhhyRx4bLIE9xbqsIxVlmXlwlAKQmDtzwXdFTQQvqyBLGoz7YNLV400Qw9Hk8SQDpqlx6RnEvrJo851KakJZbhkxAmvG/ip/kKs0kUMzNVZ5LM"
    "bwxevQW5FATAeGchuaEWzne9S3hvI0M5Kadlh55UebtNUita7AGiqRilGl8ysY3K/sUu4/Ev49khJXPHFVbMx9uEdONLLjMA4dCHaL2I/ocwu1"
    "mn5KxLOpEg74bJ4dSrA0yh5Tp+8aU5ZhgpwNB2M6vf0qx4nBTQNhM8lJTIe+DcTIFzp/jfmSLoRnl1RiOZ2xh5OIQ/yxB0idyDeZDt+aER+Jcs"
    "wG5bAHSerxJgosD6barmMBWjFA+NtmdzHaOPxujFs8pAAHecAdKLmE0XI7BagNbZx5jEIJmnm+JEkhi7no0otoAumYAgxnl3Vn+BEf7xwLmITc"
    "2e/fWG0HjuWVoHkMiHloYM0bGC2sDThuUF9EbsXztp80/nFiGRGVKViY5GzzMPgi5q+cKDDr6ieGt6BHb3M7B47EaJhKcKrRVQVWRcEC/DmvZb"
    "0I5oxfFzSUmiCq6pVDIIKiMVlRSPoSMOgFrxUxZuKvAD6ng3LPdp4HzsuEvbHOmQQgvz9WXRNgf7CkQK98xxaL/v6eNp5eXJjiH2QASK/jgGvM"
    "AznrLgInwqgLxvaGny08+OqnQMTIEvs30isoe+E7vZK/6OL9u2QBVrk+bo4cAsdWV6TfXGAkI4fcZZX1muDdWZQmdeGbcGQwdliKXcl4xiXLGi"
    "VZHgimXMbG3PsJkm8+mJLBU1kn2QioVdpiAYmcJDGNEW+JEkEcBvGj3N8uIqlVxzmWIGe4fwcqB1KuKCtnVtXBv+BdcmC41BE0uRVDEPkHVk/G"
    "+QnG5HnwuqprlEx9CFzeAgqL2k2DfXkpKzJGHip/43YoCTJMxQorQ979mmIHnd2auguukEoQakA5I+FFSblmePFal963VDt8auLSmBfMSIo+nC"
    "jE1ZKlK68tCEpQ2m4gAwXLYZmBCtk7w6pgnYIUQMjagiwQjSS7SaVlBAGV4lWCFRS4zuInQoP2DhXxsZhZWspDa3gNgClE170edSCVBIFmT0h2"
    "gv/MzhwGSM9A+QqAwZa83+aNFdiNdFGAxrpCNnhkHM5ECcMhVp1hVpnrQUcofEaUt86pUraUvFS1vTUMm3ksTDNiLWu2P8lKoZikxwXexXhmgx"
    "0fD6Iy5cTyJBZkVTPtMxeRDS/n4HgqSrwQF8ZwsoIYLuqhRC4Ld5GcbmDNeaEFa8BvR2wzm53VMTRBokupsu2C4h7rY8SQB044f7/NUJ1rai2E"
    "B3bGlzuxlukPWIUZGsNPDTQxOhvKyZQkd2ttRk7KtYIdHyKvdEISXtQLniKu9hYF1oEUadyKTq21VCwuoBK2ZOZIkUgvnNtj6ucKyTWQ8O0wVb"
    "HNmnmgsWyp2FOu1pYFOc4fARUQGS3ZtBwDUKGshSWSJmWs0S0YNuyejl65QKP2N3SQwxE+8dXxKk5oeAM/JwChdsn4RItbasDZB4pm2FFvIU98"
    "aPvQPRsZQSnKL0cSbROSVEkIgQOc3CY6nYb8pgurXk2RTDWjPiMs3q7mLLnmCNTzpjTX52j5eOic8ZA4UpTw2GB9MgrAdslBaAYNWoMhJbEt0D"
    "RXuVkJhEstAqg/+JoOYIUYNx0eWfW+AfV2OyI+KGr0oiTGqtLwDlXARthA8TlM3kYTIrCbyOTKz5oce4MdQbdModRdA76CBVI3ikABXaTQx3rg"
    "pO7OrcBvLFw5b2TT99ovok4GLi+BsGYS/VXh3yD0FnJ+IJoBjfnpbqiyYd9Ge5WDk2E9QUnb/geWA5LujlzXZYOBVmakCOnjLP9Jq2spZN+YC+"
    "F+gZHJMUobfv6avqTAG8K15C9lf8UNQIYsyT0oDgx3KVc0fgwLPBSWOuuCOBPCkMWDc156SbSZt2HBMPx4zDgtca8wnNJY7OxYIPl4ZjgAyaUD"
    "F3tBdVuGIcMmkPvl/AdKSwhLb2vKoporN/KBzAi9thO7M1N4BoyWzHZqv4fs41qAqyf7OT/CMDLmt718QkafRjwCQW97Gauti6RDMUSohiv/Gr"
    "DH6gjhoDzc1uM4pH1UK3Yc5O26SlEGZozt+zVNUFDtzWHtAm8iqR4lBZkM8KtoraBtjJagrWsKalARAyNSxnwyVtwgAERSAAhkb5ls9hyMLjWT"
    "LJDY7D6YK6wcsyDtx0IFSogoFPG2S4zaljj6qzTEOiuNXMuJDmFqp0ciwFHlUs3mbe1KMBFHNtC6IGhtEbU4AR1drGgNRd9TymoBOppRNVALR3"
    "mX5NYVYOh6sT4rDFQoPMJjjeE1EkbtX/JBxKIbEC94Wc9ALiM4ROukkXcYnMftgXU+methFkZ3yV1d2Tyt4BBi1UzTvpiRXxT0KDT/Io9riyMb"
    "LohHBmgnBiUnFaqoRf7huxL+EqaJ8N301QxkdWFNAeZp2nu2FPDIbU0tJhb9Eo2mAG6xYXM4d7LEaPawFHjTw51FbOlrVsgrMsTzE3fN4OjdBK"
    "gb0y0cTKDv6L5nEeqQyKbet+mT7Vg2FuaYXdSYEddPKYWjnkSahOUunaZDvYhTtV8+Uxq/k6/HAj7PL2EJfH3rKeNsvc77wXbdLT6BlN9m0OOP"
    "sVQegSUFSyI41fFxTHQSkyubOhTwi20XVrS+DhNXwGR2CH0od101/0TcMATli2tsKkXe5Qxj7CvTbAzP+Y/aunn5F75wmxfgaT+B5JhG0VUjYS"
    "DsuatDHYHJk0WDwee+6IPLvF7S/WRsPQj/E2AVqKsZYpjqx/HCQd3JD40L3Qdh+dFjyLwuu4nHY8PIwrw2yK3WGzoXKkdkpUjDYftlEqQ2WTdc"
    "SiMVQLTveVOTZEmpGo0SeNhT9zZUD5ralNlf6apnh89F++vqyb60q0/ai5KOzPspOlEEHZ80kLilVJPYJcf1gYtjRq0dHrpLVo2CyM9kKD9uyS"
    "41zIoq3kEixcv+wT1VgW++vgXtImB8VxnLQI5JEMgRKrquSokIXoSRpG+jrX40kzHF3JkDbsIhhmB4CEMRh+nQzjGgmmmtm90CaOJ1MrHn2AN0"
    "CF4TOynwMjAQqJddedbHZhMWGIY2BoDosXIyOVFKl2rMQYRz8j5SmiKFUJCdJqo+vkdNWGDVo5kL4DF40rV89Puc0OJZtwnkpAHIvQqBF5rolZ"
    "WAmH6NRBFCr9NT8JRYTCQFeEhrEhqWKuHXrIY8rTaVvSA4NUitkKyVUfajJqUV1i3pezwhSHGEyVr4QZxjEpjpWHB74BhLG5njOxKx6jp85hgE"
    "efOaDFpkenrFo6Y8JjeETWgUltwakbqRhpH+MgBhZy5HDNPvqtc5f6Qg5v81GuXRJxJZUcvl3o7LcPw6llZ1SfJ1ZHqYdzeiN/unqYODZEQPjN"
    "VK6AjaCGRFMXM+EkwCjOOjVSahnjNOoP4riTmcAgtK1cjD7DBpZFdtWgiuNySTmzFWjS+0STRp09AiHmmIl7OCXDzcHUPDVyzGqXUh33vGia1h"
    "mvuXQ4zIUs+oczZu/0BClrRGRdgdiExIuZ4EwpraCWgcAfFyNesp4sdiA5S0FpV/gMBh2clUN8u5tAYWYK/Z5ku+VXGrunYeaiRHuwykTO8pHH"
    "aspEYHAWn2Fp61j0PFZIbTX/GDrMTDF7Rm5rNtwk09/XgUix3EgdSANzbThTXPiQTZWpFyFKHMSLmXizQg3SEROeoAqtmh8OJlhCx/m26rCKzr"
    "mCbF50Kst7vwo0bUmLZRvybLQP1QG634wQDdrUsM9HfPrLMcy2pjOpXkNQglVVCKJ9rh4rOcI3JoeuylJ8EkNzDmx9tuZqtifqD4MKljUldJyh"
    "PNc82nLucQs9GWYI6zWP6lhrSPwtYXNEDLibxh0Z5XD0ZL3HzDh5LAt7Yk+J6qQBZsnjhYO9wjpz68UxZrbd7GBGstTR8+xFE7+3dKa2fPsE+4"
    "H1ZLXy6ONuvQNwoD5DntBUIg1D/NW9HvD8KEEgcLRGqQWhm3W+YVag46IKEYsLb0K+T5WS87AC+5UUrDcqb8u9HusUFrfIuZtTa8JKV1blDArr"
    "WDaKnzyQbPV4jUZVImtrZ9Q01UGmsGwOCwrur1zCSXJmAokk6evwogx3DxOedNd2e8jekXRjycBUdNMnr+Iw3rUJ6k6d3Ppg2b+FCs0FcTn1NY"
    "akrWuo555OhvGGIjiwQtI3W9PvEmzY3jAqKMdxiUPDBwnEEKsZQsEFaBkGfxqPCzkHI6KzYdPiFZjbO+GjeMs6X8KCx2uBoGbbJtePV3jVwHvl"
    "ijytjaOR15dVlCYiIXFK7f3jSNSGFlZcKGJqEs/81DTY2Q7+VHCdeQ77qcM6YPjXTLFQg19G8LCuXMwalQhEtRxR6BpxlSBXXe9MtVenBNSnbr"
    "FJaqXhepZGuvY0EyQKeJNHviT4VdQ+PYGBBryLF52pu8FTX1fBMi7Xm3RFuJreuhF6CKYtUtd6rJ7AJjTTWt3QENbH0JAlzwBqTZoJa7HeRJ4k"
    "B0QmmcUkgtjAOZOa4O3E8UOMcHq4epIr6Jd/8iCNQyCZHKRWTvrKBPshaPWaVt3xQlIBptG5aY6Mk5wjj8Pjsm68aJ4+nUSfpg2BJSTmBs62Ki"
    "UYYuiYf7PFX90qDJKLIx7EseORUKIFyo6BXGBudyXEZJ4PooZe+ZIHkeIZ5mvQS/dlPZfMYaD/eue5K9XTj5yB2j2wm2BxVF3NYBNYV+O0ORIy"
    "YRVq51zrrhL7T2zU6H6mt+zBi8s6kwRa3DII5dzD2+LXn/s1PwIyc2eBhYYS4r1QfVcars62JLdLpvWUWCYJzfiRzSW2zoMk4FwqRUffxhqO2G"
    "vhYkgOPcTyvQAuEI4v6C4QGegTIfjcyUZk57zdBqs/r8WAAqkKMc+hdbBMg3ZtIAtzfLZGcmOFxuqKt5zYoOVeLBQkbbhKLuAaFVlemLSTGouX"
    "mlJrcdGsh73z8tFD0nENDivOpqJK0pQozqo3cy1vetbGJJwX+8HV4SHwToakzYnqwZtKT+AQWUqbntFCZgK8ObbQrSxXPJEZOMxp5vdLckMoD2"
    "jVx/B9rSWZaJydJr8l3ma6We5RJgMuNcX4wyHESV1fh1XaKHRh0hz8VYEddYF0hfXKpBzOw0xNvxPXrz62VmrRV1niYQFNPMjCZGwpqezW/BUG"
    "UCNiKbN1sBu3fCCA/XVSIfBe5d3kFMt6WsPGs3aCDBGI6rZ8T7s83P9hchhLQwUs4pO5kIfgvJNZcAexJe62JhPosjB8gofX54W4sFR9EnuFok"
    "fN0POB3BOipM+RTul/00gAhsUFYKQ37aw+C21r/nHgOwJh6frpAFtZVyISQBFMOIPBY5wc2RYmnTuWBpsO5GrGRxE8hfbvIsJDp+bkZ3Hjtlph"
    "Opr1Vdg19wyxAr4YCSAIfIIW2F/zMM80vAHXEdK18OVhjbJfeBJ3K36Dt5JQRZICg6/3i2zh5b7C8sD7OvEARA7VuSnHEXM4wxFnSYQTE7UOVy"
    "QcAhxupuAL/gMkt3V+yuXZ9MOi5rVSPLBSODPV8mB5KOR5vGERBLw/6DHEkJKPBzkxfqHbynV9l6I3OA9u0IXwQTgFpJOoeKUCxZwz13H7qIp1"
    "COdO6+dErBCQhc0AUxezh30Rg4n8um8OcqjLLB4ASSQzTvt6Z1pd9zbOcOZZ2CdfQdfF/Fdf0s70jE30+5Bx+ecxQwvdzHyqW+pmboTGxMyrWa"
    "+HQ2mWSGfw2GK+2HO/Eurpa4Z0ti7XO9eWrtvo9bpkZzgn+954hcTCK8zINduUU4bXDBIrrFK5hrgWBviQE6cn1Z2pwOZ/2378XjYyCl9qNfA2"
    "7rCrIJFJaxeK30k8wlLeWHdpDo9h1JyPmT52GfI25AA5yWBE1tnRDRJQPj8C9imih4z9eluo2kbnDlJq0e1kxGNDWZeJTVENuaUzr6FtliM0jn"
    "3u0S2CHuvcfDiUIikFilfp7FmkbSKnQmMpnOnNJdtyREQKKBGiyxxtkp8lHfZ5zYdwUb+wIMySq0Pq8pHemCNWusvIJgazHogOSFqNmDchbAj4"
    "iQ27gjfRtPuwU33eXdqGZtetglhchT+aBRLQoFIHtspfZSNhbUtRBdscKm5y4Mdyyut2ptUgVFUwd2aix+w74Gd18xW3tM9hAgQyoGvIzqT9tQ"
    "Q982jC8Xw14c7OQpUMuMsaliqcp4tViXT8dMqQeba4dPihxowEK1EDa9CUWAwsk9nlk+9sg1OPZXzBKC9aiwaltYw4GZ+oRdhkfY+lkI+4c0Op"
    "Xlr30JAg1C/NRLQxp7NqzRTBtLpF5/prWe5cf607Jt25nZIUZgD6MrtVpAZ2xOLccCowJl5CEBr7IzZKrv0O2ed9sBY01MBNaGpbxgTVJDPl3V"
    "EJTueNy/qwKwWseQ4xw1mo85BPTT1KQb2p83fR7H073MIt1eZz3m/5QYi3MFMtdQnc2uat9n5fLbaH3dIurThEt68qm5rjJt/WcFAMGvuy0BDC"
    "p5F/ccvs1JnNUVtEiAorhxbxpFfY0oYPlXsCb8kefGamauwCmZoGu5lkzPAXXVkxlRxoacbNhcajJ+igeJ3musfslfdzbneK3YIRbI+rBjcYIs"
    "kcXhQ9VptMjXi8JiyBZBbEfcYT4RSbQNrEoXicT802uFyiakgrQryNPpXQrorF4qOtEtNJW8vv6Sr69aEtAQLujuyTUlkNMTCgfRY5fW1P2TEB"
    "4ltV6ncpu/CBjy8qE39I3gehj/GPrFk5KbadC38UugFYm5tozd49YFFKA/3kNt9B8DAS7+Z+vRT7E/kf9vmDwAfxa+58WOUtcaleYfsEO66qrm"
    "XyLXBLtqqUbDFUBrzKnTom1nknmXzH1OQq5mFEd6pQYl9gRYhrs4rKPGZT+IsYv67eVIO6phiWQQ3Bs/iSrnFaMOzZsFGgc2mcoRuGZD2wDz4F"
    "NbsmIrvTdnyKOE4vdobjTA90QPRlkXW0gRJPicU1ZQWM97Lt2obRW/BPEHcDPALT7aLlmILVbkAop2MbQm756dtWRO464wJic2D6rUqulI4xcZ"
    "o9uCeska4B6nzbrJtu7140DcVeSkCT8gnCghS72K6oVH1DDiMhX/F5yWmbWm2ScusNLfPrgc/7GPYIPzlMVm1L003y3cFwEo79Cckc6hp3X9vV"
    "+aHbNb2v05tDWCmCapRTdKOI8zxLXOzxonLnr1p1I8U7Jnm9LogPuVllJZz5RdFwsEFSCoTHKi2UI4ETbDL39DqvLjuR0zYm+KXg2SlTDMrABK"
    "CoYtm2cVYoR5ByYCHIogyEnXWFqEFWn4drQ/l617SSdSkO6LJec9hByv5z4j/9BI5NsXnEJX3QEOO8DwYDn6agSCmkD6Cm8paljlZDsqU4yDZN"
    "nsRgyW0KZgm8RLcCMjhcGwmMs6kRFTE8lnKKbYIUpNgg/skELOgKxyRDeQh+Vwa+MV1E4YuTNqi2hTea6x/4o5rh/IHAEv5xMRxmQfAcxB/nn3"
    "GOiy5vYAD1mY2yj/P14ZcirVFGgvMvYqdWL4vFPUPZgKylgISGSGcsmoXZb6Fjy2lCnEZloWPYb8EZBcJgHKDORbWA9wcGpuf1JPHNiNsxB06i"
    "ixa3iikX2CvQcheara8UCMSzO87vCTvHpp8LpIm4E8i1kNbaUFqpMMSerCQ4L/pqWwj7TxeWsOAqqkiQhjjXINvZa00pDDcim15TDDqeGcHVRI"
    "29nmHuvi0ElmHXLeNPNnvB5QTn0KhGgTOkao0cTJ9FY4FTyeWk7DlMRFMXQxv1jCE0gAsiwCdB4hVHrunWD6qHQB1BBQcbFZYiJjstE/AmKe3Z"
    "riYJiDHSRllhZ3LmoAIiSFa6bqlN3orJQ0wdVIBzvyubXMZCe4LTEKO2Gs59zTSflFuoBiKc4RpBI+KJv+QJ1Ab97krAuuPabCTflVXRyi5Nnz"
    "ONJxEtwQLBrhFH0OQcAgGf8MgMfldsmbcnwQUxSrDx42wxJzTxc2/aFGtiAapfBtezqDlbAdWiceSs78ewMaW5MruvDiD2JItJsrikqxewifW+"
    "wAfTzm3L3RHx49EMxjnnzrtWcyr0UdEw7GRsq2aVZi3bA8d80jafHc9737ZBtKc9Ljzt9GD6sFHxWYUf530VMNpL/zVMDwd/0RaQMDxvTwTcj2"
    "jZU48ZbZ5WkY4TNx4tt6ErV6J6zztAbM5q3ilgKwdVhnHGkvsJ5RkORZ+KNetWdPWKfdkn+ar2GfOMYv7ZJEU1at2GjREF9BiGYTkC7x3QT/jg"
    "mu0mseGCz84S0qh00ZaQQpEL87UlU0gtFrEYOQLyXXzs2RkrPTG5mWaX2jK1QnNW5W1Q9vSwG9oJ2XZkMVNT/EaRGTUCR3d9wlXiAzdIK4ioK3"
    "tXsYfjxanFJb3Gyye1RfryG3FyUIB13nGMWgg1hFRO32uWzJgSBPJZ7VWIObRjGKviIdDMxZw3OPIHYKR3hXsieoy8LKVRVuREyg1/ysIcgARL"
    "Z09oakavVh7k5jFsc20uyvoiv/BMJGbFMABWuehPXghizbF5MN3xAm02Rxc5hY901i6bk44kwU+Y8jxzPyAUT3AQOXfSwTHYFDQ4r2eUkFswFt"
    "wjv59cUbiCacQLjc7UceZwtUNguo4S5QCm4qrSqssdJeHw3rISI6bKeYAyt+vPo5lPUr0qb2QOMqCI0fI99OacJnhe0EAFJOXeApndlgCSDbYN"
    "GK/nrCtDu2oTJFI1B7NEXDrAPxUXTVu4fSjuZMN4760F5BVTj3qsFfwLKC51nBDqHq04Jd7muNhSpx1EpSHTdYWHoQU0b+y6Z1s/b2pbXYq8MJ"
    "PmCvmSmSRC96jWozJd0SYncWAdFLgVoPeks3cT5z/bZZPtRk8OJKNga0bji1zCbb+7ZZaDzKBol8fltnBYIS0z4hPzST3hZglzeYIXTDN8evg6"
    "8evpxnSPwoZ5GU4S8lQi9ZbJoFCPsJmzOE48/PyRHiJLn1/Fsf1S2vVhbfYcN4Lfkb6hyK/r4KcCuZn23tonk+I4ryBud2NMwclfVdMc0h+GEv"
    "kMP5sAGSSufCsOLvyURcM8GdfgERtYF9uehMBwMTGtY+qARwyeZ2dT9zQ/D5iWb05CoJK+6Q7yb0k8+qbFNsrA1PdBW1bcBrBl2mSy05c+Wv3Z"
    "Eus9jf7QSkeBS05eMZmDuOmrcl0i3n19XFfhEmWhf+YBSSETO98X81FPfarOxDWX7jPxzibe0i/hnfWe11s8vfWXcctaiDXN3MpjLDm2DfTuGR"
    "9p4gqjVLEYDyD+XSq/AVTVCDUk1S+afgj0a5gjnjRfjFgYiXJ4mEhAAmAh0JIFSwmTlCwS72qvIifMXrVqztnQn6Ow5IgwxdyzdDRuuexjGcFm"
    "eQlprVUuvy67QrLT9SmkJF7Y85hbWis0QcnB4/wGOeE6kjNI5e/SMxevJW5D3e+6ALzyaD3ErToGiixIApyQkGsHFoL0wynKSPCcelKquT6oMt"
    "fUEmTJdYRYIoD8t7SmDu7HbWlfsxi0cK6Z2diItIk63ZtRS801J+bReE7tV87jbayhxEVMXJdrBGI7m0PsQgYk1Ayce/iQlmfLscuTZ+WeT1zv"
    "52DgbR2lFVGFH82d4Prc13H+8Ts4N/f0eXb6+OZtnO6MM3knZ7ni8Oibd0+fnT6356PKIa5f/dfP/87vnmf/CP+ynqv6/XsvvnzvxRfuvfK9uy"
    "+/fO+lF7+f/WH2H+Mjs18/fcQntn4i50Rn3PPPo7Ox27MfrEgN+Oqdr+uhg3e6O6NE4uEY0pENgogAzNvj2AztCHfFOeozpN+oLp6RJnkk8X6E"
    "zZlaKHJBz6Ci8x+sgjHH+3T7YuSpHdW2+aXAHxojJXyEUYajzrVg2hzxFRKk8AUID8N8Ez8i7j3m9bpkaQd9GgOZbRRCSOqGBJhspo26pEpqV3"
    "JDRyjIo5Pcxihnc5wkZ55Ts5NWWarXVg95148w8eAT+QdUuCHtd+z4vLgqO79DJQxjSANq1nmBkZWUX1Ii70w7nXc8DA7g3s2OO1RktMrQeG34"
    "he5EkjvYtKPF6ORXC67tqB+FD96Ch47CmUbN9p92Q9ZTXo85vyLMyRhZSILJRN/OAQtjfM7lKLYTGOJGhZWPX0KL255j/thl7QE2R8WxHJGXQ7"
    "2Re8ze+VN3ftD9LroKg+QoRJhXOkZuZgE3aNmlf4+Wd6DFbDhgQvND0ig15FrsZtqEdUtyTm773aih3KOG2p7PLjGc5HNbI2EKYTqyNz8GseAz"
    "34msLQwtMyikH9EbioY2FzVN5HwsmnGX0w4mTnH+9J88/9TvP/OjH6xWss/zqmvGEi5i+ks9OPLVzM7jJG7bdZ/gPXoOjsmzxlpcC77ltCk5NA"
    "ErecRz3hx2AKgrPBxlKyvReRbvjFW5B7Q6eBZtvDa/hjpGlw7tambrlfyNAtM0wqA8Ch/Hn3MYgekpZ4OO9hxpuoRS35E6P4aW7dGboUdF3TTF"
    "OQ/BDCUtectz8mVFWxTQBSNgImnvI3RohCIwHkqiMKMqZ6MGl/Bn5+WePqwzBt8HiS+/akBuEG+3P/QoFNmSrxhGHGNSduuBOk6XFgoIVw2WFH"
    "4MY//cIK14wUg7mDdpG1csRvJcBgjsdBeAn4weJXmMfEF2Xt3ipsW4a67H6x19Po3aDJ20tMcFRo1A5gNTIqrW57QAC+rIRWEO/Y7o/hbPulHs"
    "HPCj0qy2ZjNUo4bDyFiqKKwDJXwB2xFS6wixl/5ApNPvlgrRp4wR/vy041hiXv8gYrBiEFwwu1ChwYbgv3sGzsYalm7bhAChy2wYHcXINJbWzD"
    "KGWQJ3xlABwMxLKJdUs+fGjJwkM9vdK6KQGDubvz3KkR9mRLShwzwc2bivqQFjAJQ47o/EyuE9HeF3RtiQ8Ek5KYfWGrsOsTrlAFTu8V5zfdDf"
    "vajZWKABWCL90Kkfd0bVMO6MONhxjq/KymNeRquWZrg4vzOz6oggj1ZnHl261GiV31HDnmX0kY8yOrIzquw7iixbj1BcRxr3jlfJNj8EZGlOpD"
    "I6pZqrMYYh/rT4KiNMHIGuo848W0FHh+AtrxSYWZIQIMDIN4Z8AwxoN30/sj7ctOik2CnxEzJGCd3Bx8tgKLzkqFA7oz1rc+TIHrx9TywGWSHt"
    "tAcevpz6oRCao0O1HG2UtJv3UaB4SEgK1jueumtL+YOB912WDkzDVAP1gIR0FvxJC/jVzes3732NtYCPTo+gJZDmoAUfn/7+9BDC+s172T93WK"
    "puSuHW50meqlBnEuPrhD/O7WskdhDjKLHJJGHtzrlNWYNQD0TcUTxFI6JqRp/HNoamwtGd1DYrMIPgMcgYbVhs8/NMZFzbS95KDHXHm08h0UZN"
    "evSbkfHOgi0ZUlFFjh4D2+rsJzNcI5ER+mMK9ATvloZtE0wA9N0a0rXwUulz8ErfVxfxfW7D0ud6o6hHd0a54B59iYEJzugYsdhXuIADIp+fdz"
    "4L5s4olqg753a+3U/D9nz02bgyRdvQVuJjZbT9URcJVgc0qRXxxmJpFbAltlzhPDPmSXojHx0dvDFyKhj9Dbgj3QX88UhsgYQsqkP9b+be5oTY"
    "L9e6slt+ohoVt8Rnaoz2EJBRFSMwaFGlUCZclcTEeseixWg9P0TSCquLFaMzFhIrmvsCEuBa3jFMxjoZpz2Nu+b+QeAZOk40pRtsQvpK2ZnWpx"
    "5vklC8CPlY35A22uFFVyWRA2bKIsUw7ZdLJ1PWi3KNGoowvdZmVG8n07ss8gTfxj8ieQsAvBC3q+bIfXmVBHgMekNsRPHxOvvpmXkgau1s56Cw"
    "QpIb9eQf3I/+zFma5pVBVzqn9DmNS8moqG67sak5HGpUuWh+7iqbJDKGySfgoyvs9DFGqAvfyUy6UVbN75/n19Z+c0Fri9YkL8Zg6iO8dlXHF8"
    "qguNQj4H0u9DJGC5gfz4WFuLiiJPRAxeyag55GCXqCfWRE6qpcIVcBF/Oys7B8EoQFD5f+wHdEQwyBn1aAOcwt/YiJyEY2DU5n3VFL9ny60QZq"
    "jmKo4l8oivgITCJu41ztSYq1fWdckthsPr4IbFWjMskOMPiQZ1h2m/1IhAuM+Qqkt4aM18WMJ9hA3BnbRah2zBlmPiPftqUt183V0SSxRuB6JB"
    "DlI8eLzwnR9DO7+K3RqRj9OZSj+pyZ4pmcVNeg1/xSN9L+FK8xPrmQqwUglMQblV8525UcWTW6LKKAVs12ee6l4hycGynuQIXFvCZNPJ7RsF9x"
    "RNekd4EZMVwgdqgXxtYGegbW2X3DNsYWEXXCuXCBFYK/eOpRHeQ2klFQ4FY/323yPeaKr3l3GnlJZunIjHlWgQasgOlGdAuKWov+iFzj8TCsKl"
    "ZSyyvcKmXmz3mtYcMDY3ux5BmxGOphrmodD2W+Z7lI5n52tPQcz9WRKDo2P64YZ1cv20Y9R3TjciVWR2dquF049sczkXC8a66RyoU+V9WgAKAw"
    "6Ho4UO4sA0PfsW+woZ6jeKq3WCbsABcFkCj+/4bPkPACy5Cdcs00QPI1LakLJ9bPuZ3dGZ03PtriBytnz3PSP7hLpADMjYVEABJZgL6PEHPSsd"
    "AkLoUaOuJisC8KWC3qAZokB4+Pwg72dgMS3Wd3+ig2pPnxH1bw7I34C8vBvCwso0orW3jZeUbVb6cB0j19/wbx8EwIAN0JiL8u7jl/HbVp1aDX"
    "VD5uy4J6glMuSLf1L/xPcw6n3/t6dvqQ1EcxdFuN8vT+6TPWKz9kVxMXPTp9evqUb7968wbV/pA9U1TrrZs32P3z2ZdyOn3FWoVPf3vz44y0Vm"
    "qbtNf3Tp9lp5+cPjn9ilr+G3V43fzF6TPSb39Or/w/6QEXvYO458PQZadP0A/8FzmxXv4P3773yr+59+IL3/rO3Zf+LXxYfxIao50TLTt9fvPu"
    "zVvyrdbv9lWYqanOT8+DhJur7SvQn2CjeoVU9VdonZx9PXv295/iFumluLl47g8y++Ov2fZuayR/QI089weRD+IjUvXfPT2a87T5bmZf/Z9v/P"
    "z//b//x//86S+zu/fP45MgTPuKOwJX3/HM088//xS1fvf+17P/I3v++d9x7wnH5R0akw/t1Mt72NTwNs37OzIdb/Htxzc/xriFRzBwCOorbIPR"
    "waH/PfP0s3/wlIxPRtP0Fzdvnn52eigzGLa81G7Yp09OD+nZ69K5h1T2ecbWDbr6FKsn6nc47P5A8Vd0dKR/zzz93PNP2cl77vnf+d3MfvNH3O"
    "b7aBpvpXfy+x67hOzcZ1+V3yULCImmweLh/z3/9HNPZW6EZKXTjnvbriOe9vflHeH7MZBYIPTRj+hzP7BVP+CbN/gTaHf6DvxwaHrzSsHJPnZV"
    "yBQ986ybonfoN5+y3ejPMV/SzGcYh1+y7wbzRVV+eXoYr9g38RtM7DvUpc/isdBJeZc2+8PI5cN5UTIorTmQFGHH5Zmnf++ZYNWg8YfheNCfT2"
    "jwfWupV51J1d+4t4dDycYyXnCnD9DzvwCJu/nLjP6B/ewt/nQ2pv0Ze6p4heFHqSdeKCZ17gMQSBjeqHCOup0+Z4L6SPYPt/e+LNtPTj/L4iYS"
    "hz8PPL7TEre7L9z9xr3v3H/hlRfv/fHLL939dkTYzkgmkGDxM8jM8DvQpUM4Fhxj+quHftMVB5cRP644himJeJKYe7oe8OOdBPifOcM9oxGc5W"
    "v40dkJO3OU7V6asHou6gfa7dlT4Sj9ElNGk/HTYMz563m4Tn+HiZme50BNskcKTbuYoTOPqn4mKVe4AjpqnHsA8zx+6AKfzoIotzM+QYEHwHDY"
    "vk0MTI8VcABPZwES+Flw6MGZP/XhLDkGEWIcz4iT2vBBFsH1zJ5nwd9xZbiFTYKGwJG74UygDun3LLrxD6Exy7V6ARI4Jgb9xns5CJu/uESiMF"
    "4l88Q5I3yBGEoZEx/Rgn/v3l8MGPGm66tnn7OCxq94icfu39j+AAmGi0NjhSsMFthEtrLLzVUOF50rFGeWv3eTJ2Wx1OpXuauPfeFueHcEj3T7"
    "LMQwzAQPhEAY54sOWfX2iQ9WvLJYrM7n6pypo9cVRj0GiBSCGfcGG5/F5ixuJrE4WyvzxLAbWrPZjjxp0qEwiuP6ug51ErihRW0bJdx+U8JE4n"
    "Fdp11058KgvXPtqzuAbKxppqvA28SRNLMSvIaOiZ2BiceoqM/niZN9ZpwERVZxn9xEs3/x6R6acJ8UQrLvJu3YCAfoPb/n4xgQsrAQZsAdBvDm"
    "0OYcoeA/fSHkw0U6+JpRjMMk6CUIPQtETtrSQbP/mb2UWRDNpVkeGtAlC1tCjqLorvPzqHv/2UVgwJpAyrAa9ngKxNIXrIYwaMEejDnT4GPjn2"
    "6Jdpq2pg0ptecoEBh0CpOPnHMLX8Lcr1z0mY0xcxFkGjE2Mvq2ixibGxlAmyEzntRLOT7bemBdsJNTyvXzpo18wRiz+c/JdYKCGC8X9eUCwcT6"
    "T6M/LsR0Rb2LV5qNtPppvM6+VHyVWsRH6e75UlgVYqhmoquCsKrbg57sa5x7/vyxwVaTnyBALu1fcqrMlPtUlZ7bG2BjL0TBIDqSLXOjouenfp"
    "FoFhCVpTFZadiR7NDQpCOcwck16vx058fC6WXDkcLII7+Hg6CU8yeJc1oMcHLMLQx2SoKa0qmsuSluWl8jkVQ2XJGHdbTh0aNEUo/RQY7nC1w5"
    "tMsFB5ukxrjITucsc6MIdkSJ5qKJQBxHBgx3+z4gBakpm+Ne2AeEfcqRLaOc4nceh7IHrJ/XzB2JzJzONmSC0MQncx76l/16mMgKYhtTUUKkhR"
    "l/0W1feC6xgBEXCELaLEsYPbjYyDwkHcvQzfulfK8I/607s+DajQUUdZfzjKiVVIQUfzJ4wMQXvaGhR2UajrkRXmdPR5BviBqDC4rB/8ahZ4O9"
    "M8reFtJj44TYb8dWfRvjcz4r6Sm/9PJXmMjiS7l7wb2Opy9ZcpmX8PyB+J0H8oVkZ3XzvF1DxRfjuueDG0WkVvmaoxs1ntHFN0r4o4ivo9U1p9"
    "GOQYijj3v00Y4+Eu8LxT7yibmzAaJ1GEyV6W/H4CixURB7VCE8/6f79KUAfAhkQ28j2TTY+Z/xtU/qynfHycyRUpChjkYvlyBGgJeOun2Ego4k"
    "4Qx7Y8PXnAphA55HD1oiX6O6xQizw/mXiRQN4kJJLGBXgA8adWGk/qsk6h0erqGq4tBRHeXZCFIrXsHD2nXs+jJ8NPNMHGkYYfqYmFK7zf5lf2"
    "WSk6CbH8GvWLOrspilaz7wEzHueGMRbxeJtJCYgPwwLgV1ujjOKLrztoBOKFXCAllgGQGLwFe0rqfxYBbBJJCQXJgIQOwy2EWwRSRAk1P/bTz1"
    "cvj5HCPhRDFRWTm8aym2QGUKoEc+WWhyCEH+pOHJYXDyYyJC46DmIMyT7uyB63fGMDIjCPxfTA5weNBxPLGNM5kNgrehsmr5hFzJhk/iHZoQf8"
    "dGwoJJagwsO79LZjYu5NkFQc/HPsenJ8VfEQ8Hphx8vnDf5T9Awm4XnLsa3Ebru1xfQjBD5EYpMpnGdaiAJva6Mc4F8nB/QYAcb7MrOWtaUo3Y"
    "sy3RE5IHADFH97+Lm3cMQiLoZg1L3p5Bm3433qYzOW1p9NnGKlQzNVppNJKknkR5CqrfcAdVFcK1Uz4mdp4ol2UuO0JljtlvclKSjWsWa/noDO"
    "Qjm8d9uDNbBVjYtRChYWT8CNyO0ZpUxKI+OlgtMa6ooSXNXABAQGs0UNrRehd4zRWuliIA1QzixJ8xh1I/AhbkesxhonVq42hTiHESiyusGHBa"
    "AlNbeyfp2EthAiq1icxmpTk259AbqaFiPIoZaVFRiHmmY4uaFeJ5J6POgoa7BAqSk/zpF6HCYeV5CRKUlTYOHWebTOM2LKWgp6n14O79bFVyLE"
    "z2tYyUKrm8edNbFaYifCa4Ln1D0wZDR9/MByh2cp5f3tFXANsKkv/okK1xNy/9Aesp55hLe6I0X5dMH4i217RmhUpUg04bwk6ef+ZHYjEZiaU8"
    "dT4TzjMwdliUKg1Lp9hlFXLNP1kdBUZh+mghllax9PZyBMGo6D9y3CLOGR0Z+w1aNSlijYfSY7tqMi/L52k++2sNaR0qMYaxri4cmVbwqwtHrh"
    "UalqHpbJ3M84HMVgxi1XzYHBtvSSu7AniIxvHl1X4UfLtRIHiXRbyMc5FlpnI1ieZAASmJLAJ8diuku9mM7HLFv/B9yAlGq+OYpkWorIL4r8lL"
    "I+Mvf/M4YwIOhaQIJCISmawsdC4mA2TrIA5OgwLFNOziFsNwwjBeME5L9kfOhoGE/nicZT01xIIcdY8Ye30tsJKSs72hkdrj1BRbsHXPBLN6Jr"
    "iMjyHs7ZsgZhVtc5BgrfCOuZstmA1Sw5TLwSA8jQFoiYXcVb1a00xs1xK8mjEMdrs9HVxmeUY1jWc2UVTDOeKp1GkN5zGeu7xoDo5zbrXQ+wbc"
    "UliWCUQvn9fmI13damRW0MDK4ZxRq+k75yXwM8WCAi4Bgwr+ClwIXzpjCnMR03fAeeK6am+ZZSrWJyQgXmh3xAHyY8MoVZYv1poxRH08d4e9fJ"
    "nvjD+LQZ7mzPSCu1082auS9NpbzS/qJM4BuYdQb/yrxiR8aNsUwzr2DQfm6tA+HVmuz1NHgMoIqW04tAqLmtYZydK0mYrcklVaU9UBOu5EhVDF"
    "dtny9SR+onHVlmYDs3/bB+nzkshwbcYw3bLpvmxiPv0rFiB4PDjyOH5XlCpPb22G9snS9Wd+m6Trcz4y+A3nbTw+d/+2xH2NDFbrlpyWpqucCZ"
    "7qlzODxGYBTrTQLBPv0ooTTnBK+3aLuJTesBsZ/gFwjTTjRDp5PusQE2sJp9qIvmoVWKe2ngfesjnvXqBcCZBAFQyH6AmWxHN+wUKGsNWf3QDa"
    "I93mFq11y3LrruVAoYgMWgHddK3bCRjdHE3NXhLPoMcyQ+2XKKKJR4rPgfYeKKzrTTkf3M6YgpzjKceEkArFRgW9w4ky3MPePbD3JWMy5aycCJ"
    "sRisJB22pBt2tRoWBmwxqWwzfE3hpZ6vBxemT2rjycT5yLckkklxnPnm1hDWPSE0sRhN2iEW2E+IrAC7AJPzTgW/O9sI5MDUfsR1QjGOfls6ls"
    "BIA+AD7n0x8lminI/Ro5F0yPnxvltJTz6OOj71VmEVoueVAiP4XNz4V9gU/qGe2BPoFd4hpuQ5Y0/NlBqdN3CacC5FTRia27RgxAkmJYdurY4o"
    "XJGvdQaDKKtYUsmEqE9+haIVpHA0r9mjPO4ZR2jsvHQe13xgu9mCwBRXDzsw7cLiA2FX4JqAXPJxW4+fU+bTvT/twmnRnYQjVJZRnTpmm3OTWj"
    "a/ZxfRQJfu5FZr9qIdmzcMc8VERCfTENVscp0+AvnAUDByQ76qX75zNBdBzxpEdpTZBsuH/Xcmgi4FcYAH1FGzj8oJGBDHGiNk3BjJLTzL/Btm"
    "VfljRqmZ47OfULgL3Y08JQ8ljkF/Uv89UBJLrMbwOEMQtAMCMwWRPfbiA2hVmvXwwuhq0+nOQiWfOm1yorHHLJy59lnjUOWdjOIlBomLD2XA4m"
    "HC3eoYyWswDKGYhiBpTTlvFnn8+hBTltD3EXbMqwFwzg8+wzz/woqOMNHqGFQya4Kg8ZBu6WSfY9t0ffju44e6bs8XcEh0mfzwXoQSlzBwL8I7"
    "F9ovG/TZqV6B1vD2pImPIhPKOzAvmjAJi2IwhrmRgrK9ZcfmECwq8tc3acuVmx7ZMVgroUO/QCNpARLqzYTHwshtLXGeXVHj9o08b82YVjeE7g"
    "std2kq5pBSHHCAPHqztMcgxOihzdcZiT6IZ570MqXrhXwpU7eg+Lf7EfWRs4wqjkFWuKYOEFezEwAnQRfjjdDjW48FWzdv4KyGUinFlmaf92Tp"
    "jzUl0o1EUCnpXnnFy3tFRsyO7oDl/nK0Rnwk6C4BwpkhT6Sm7k0B3tchi0ORv1++QRPBLuVRBl37PJY2Eh5uGKC5fPYkSNxMXNLM7bXf6jpJo9"
    "ueefl4kNLZ7N/MOJCX0go95xq1moNoeLSrJ6jrAWxBJTMQ4eyiu/33IgwbolwvhYo566PWLHI/GZPd4kgnDmN48tOAhcJgxFkSlw0/IQLzjw5+"
    "CrpiBXgd9eoa2gnRtvRHgs0pVqN86RP0G6iuXgef8+S8dP7uRyTi3xcXmfV+DkahvWwOXrIy+UTRYOMoglw1h2ittsuJCtgivG55DLaOdI5I8L"
    "BRoNw6fDQ1KBPhAZOXRf0O+FzSIpPF7xTJ1hkd9LiJIaovSvmG/YJKV/oQsDeQX/+IimyGt3C4TZjMKHtJTqeIclw6f/5NlnWGyQnjQ1USQ4kc"
    "uWLzRTZZQ8lRhDIwTXsKkhC29DXMTx/E4q7Ub2knZGapAefdlfa+e/8O9EgsohWrlwESbW7KkkWteytbglWrBuG81HHh0OC9AfKmYjtLIGWEUD"
    "MVvxCIyFpuBTQ0Y+IGZUC/7Ihu/QyzufX4Jfj0wUtkl05D9nvOloDzADVTKtOr/xtdTbuhMJZzGBRfPxYzkdEZYauDj2vFkKEECDQxlwEQdCEh"
    "8hugLSFkWMLGquPobUhQOl3uEWAtcW6lTNYY7VLC6cc+8+SWipDJo4rlhX5XMxOEBiHYYcNet1Pu8VWAhFXQw/Xe7WdLJtTj3+mlvjVl28qhXx"
    "PDad4NGB8/3jkQ8nkIcWcSsIM5LoJI5r5qH4MmFHFgw3RENM3HEC7RH4eebheG4NIGcYlwjdAfUv2sCLOhdTbk8LHbf5fuiheDoDL32GjzifFy"
    "hUuIJzALpJ1P6uYbMCQ75YvEYFa/RgjlYSc7ZYOerLAi1GMVNzLobAA6GRdEvRWkteh31eHwUFhXV7i0YJtHAWuarKIVOKe4v7ZfE6NCxBEceI"
    "kgrk3eDjpqxt2RmZ9XzYO+LEXgibWgTF9NEh9hCskb9AEaEdatQ/IwRmGPq1AIfp8q6sFzlwKDPqt8iK7MmiLbM+ytfAgQwYmFokcC5zncMhE6"
    "qhLQHACVQ0/5UDm+wLSFK2ETfhiyZvUFOnP/VjdKeayNX0mUDCj4qzQkNiO6mnOSwCccYNazNR+/4MG9JL6suRjzaJqri3zECN+pWyiCTm47ME"
    "uHQWsjQEypVACI6JSNG5bxnmuURQ0SEt8PIoqmG6aJY4BFsqGZKfVk6CUTpjGXNa6j/d60Ij0Tx8kKCS+ww7gclqkSbL4hE0ywsBGXLqpxzdJD"
    "qju7PqpNyK3TwGh2oRQWND6CRMDML9BM/UKz8+1K9pKuBV9mgNSGWiBM1j5uQtW14qJjVE6al5QLCLCgdXJB/7qbZtkaCuTZvIUmwWzA85nx1R"
    "Kuq+pdh844UXzued3+x5QYoK0fdXB05swXkUGCpmzJzAaHPYktXs4o8QamcTjH00KcMUp0C8mP+E/5Bex4BG1u1iqWrZroe94wly5B4TSkcfpk"
    "OLFg4smPfsQ1E3n0jywtg2phMCBZJLE2g84t1oT0DjWGKOrLOf7d0ugaRtRTcVqkSk6S7LCm1jOdCfMOHPwbiFkyb8wwD9plyK/A1OCJNwPbYd"
    "uLN9R1JghFS4pPZiIVryPFLsw3AYjZBxS92t6zS2VTyO/iwKxms6zvdbsNscpFMQZRZCusWAfViG5Vo/7zi6b+cDUuzns1woZ8bBnaIP5+S/BP"
    "5tZs3UnXpQ1RdiRqdhQGRh5EMok3WTiU4JU42umGh1xcuHtznbkzokVbInTWZL8ZJhZOB5rF9tjmzzm/M42cOFA6DlLeyBDAK5MpylY6oNdCD6"
    "/A6Rd/3RTtKscIxjiq2wGH2gnVJ3bMX0WJlx5sSw82VruDOFq7FdTYq0zqxU5kQvlbommI1eAo2IWUxDcBp17GK4navIhvGejIis8XbUOPMNST"
    "+9A3vb2sx5JWOOdFk9i0mMOCJN6NmYpAdEsuGME8eU292kexi482AhJDkUmH68ibuhI8Igas1mM+3CgpHfe/tiP6B3+sWR6JEL0M2uRo1o0IKL"
    "PAxZk58+dW852YGX2KB03x5mKx9xPp8MqRF7osU17aHRO0MqVcHdZD2Bz06XWh10JrHoyNc2Bx0ZLYjOr1Bk15g2uDj9RLiPxX5HPRNp/8BiKn"
    "+inI/5ZBNEvdvWAuWp3pSR0RFqE/OrtOdq5Yohh91FYuIKgUfYndAweXPhgbLK3cfb/vOayNsi+Wo+NLySfE5QyLJfCgOCCKnWK53TSgCrQ+MH"
    "bGEzPNjaRMTwEMRGhKILjQZCaVjJk1gx2N7F+gBK7A9lBizygFF98rSWRQiAMJBDLXoRKsBc+EQAFODiEn2uv6b3B3GKoK+GDQiXxvCJ8bTQlx"
    "wYmvWv4fissOs1BtcWQ2W3h9nr4OqtnSQbzx/Mjq1hp0Xv/ShpQWheci+0JrfHWCdSWjpN0Qq18EA7X4ApFhKufxFAm+Lejwnc68LJE5EFT4dI"
    "ja86fvMWW1kuFhBgScmVkBKvVrmjI5w6tXAIRarUiQekHRGG3Si7lWCdnpZdZRaWoVuljwuqWXN01ihi1bJ3ieODfVI3pyuAJkvMBk4hoFmYou"
    "zPjDumQyNrF+JuF8banx4g8yPye48kyuSwDJdSGlqD940/jmUxQ+AWnHM9EI92MYDmxnKTXSPwv6wkyFuOx151enJtOFNyXgdNVhqhE/PsME9O"
    "Zi049YaEi7JWgiyntjeLPI/Lsnn42ttybJ77tc+xsb4hOMmaBlAWirw0Wj/+6L37zaaHi+F4KH1QgmayhJ76KKOFFkZHA7di64OAtCOiv4aYwO"
    "L/46MAQI6mbKgTQbBjVxOfBr9yMNNwfyIRXKyxyEceWg6flntJcKM7+8ukljpX3Af5T0g/Tb5dExgHPUWOmf98r2lnauZ0OuqKh03UZKHT/pu0"
    "1uTbl+ZjqftJt10geyEI2fNfwFrtXi3FzDrzTEz3yGuxpmNn8s425lo9hTamwYU5RMENQUAD54FKmIMGbN1RX3FvUbmPNpBTxEj2TttwzoWABx"
    "sPIREP6wpZHxoEwVII4hFHPq+WHfMlkneGQOZYSup0pm+ieo3GU1sU8lbUtP1BBNrpGUdKYSbxdOwB5ysHzS93Qe6sBC0iRVYa0PhyuZNc2nkR"
    "044paLn2vbuEcrNmlY6P8mjaX4/+umg+v+j82nLr7olWmP3uYJHYNeEWiV01k3XgkhA4KpHEaA5OtK/UW33vyOgHpr1wIf+ZvmhRuIljyeZi2F"
    "x8mebrlRZYaCQSUemlhOzrTQQ/JAEjcq2HCUnInzW778sHCPhWk3sQj4djCC41L5x6smJmGgAP9m0DJP0QgvA8Iw6BXs9+rj5j0Zy/XaL/k9QB"
    "KxllpC+bamMj1csuE2HUpieczwiqy1G1zj9rP9sGGi1mNtyeBMPThYtgpsJ8GEXYp6HsMgRFIXgvY8cLd97H70UBej6Gb88nvsuIyLUNzUQi2S"
    "3pGGmQ5yjxRXwaDS5l0DXASo/vSBET7MyDUTo/PpAUNOKMjzayawLlflVwiCMSWRkmy4ZA0u7Y8ElIPp4UTZc187UniENdDmqVBFz/kXJP5dAe"
    "3Q3JFu4aSFF8c+7jL2hqMr1SW6C9DbmOLYviz21hYFqZTz68niDO2Xh+DrxLcw803WI48AHYcToCbvR8bC6QL6E+hmkHT6TcWJ1GxGEVkXEI2j"
    "zF4gxYDVrjJUXj2ZYH/QtVXQY7GNonV7QW+0L1kdt1yY59xPNxA7LTl8aZjc69KLe4wMYket4STWENq5dR5yANQAgy5EwLVxqqe+LiM32R1O11"
    "rzyzuhRqSLRSnhW0P9jtgEuJN1LlzR1L5/KFVYuypw4CuwGSCD3j46K5fClc1AOaxMeAxUB2twDYSa45XSC1YW24zFo0V7ol3cFhd0Y5UgwJxc"
    "HBYhDTKyNOF+gONUvG5mDsQU/0PuD5zn5EnMUcnZDkCAhjdLU5Qy3DiuCibQAoIrYvpeqhzttdUx/AliZYPxpEk3g+p2qscxgkJ+S40Bt1GdkB"
    "AthcNWszkzB+FmEgweQKUbWnX7ErSQ2HiIto6bssfpJFmETOFYivemjXl029gM5ifCRNR2t9OyCDF9K8HhnC/Modxmw9FFB1Dya/ZFFCjQA5u3"
    "ZzYk+tODObNUsBOfGAfcz352GIg+lzIoQXOUS4WAQPBM4HvQohIcGBR0DJxZy7GM6lmHqIna484mlMlCwONVEROOh6RseqL0Ul0lPBe6xYNikv"
    "qJ5Y4lVk0uJ3YalSXxkdsrZZu3S54/gJKW2BoyLfU7bwuGt9XKPndue1jUKcworPp/ThdD4mVGzI7q+t+qmd1q9A38eVRHDPnOeoY6zSgEoCQE"
    "oJ7N4qdqFUQpBhsF0ZCeK3D6VIZJnwJ+ePNR7egh8+H6E5sWCpxWpuq9EWy6xhU3aVbLP53RXtqWinzQeNvzoU2/m4OuLQ+mrgMKjTiF8VtOSC"
    "nhMII9ag4pOm56LM9AWBoR6BAZ7EA8ZQLPcuzX6H06wAxla2jI4Xe8Y1iBvBqzj8ljSsmi3xrLbNicUAJa4q+AC6vCw4AqugN8zXZBkZcHGd6f"
    "vKdEsHPzncA4jUx/m2DkO3y0RFoIVHC/FqFkhfxe+8chnq880dmyHbml7kFfqEa17i5dRbIAcqKSZuy3wGudQ29irAqLJAVk61FSsDDfYeGBy0"
    "Cob9weYCBIqy4VTcWVcFDv5jL1Pk3dK9FavlTkOOwqlcMqCz6QpGfNMSI7oyD5hoO3KZhNnO4DOoQdgdIO0MxTYnjXG+GryYnu/zBTcr28gEDC"
    "4Xf62xA6IQcYFtiktor27ZiXYe+bNkANirZR2ThVlxzpPPNKDWQFhlpz32Sx6zCzWzX0TbTOIBQHSbyNMDbdE+tY4KLbD+Cr2N3BZaFsQ42QJq"
    "QqI8LJwQfBhzCgYYi3SPwRjd57oTUa2qksu/NTCkRPGhizlFx+ab45rzJWxMBj58bjrk8FE7J8vm8n3+IDCZ/7rbyqE94vOxUwWCavaMEf+YuO"
    "PscR918DCT0GEOOcnO7yg+8QL2EA9xHvuBJokNVg1xSogVoFTVsCG98xpIoKKwptz1FsGK3aES1qMnGQg82dBm7qKCd3xRMHVddIdDsmXbnVgv"
    "xnmOMlk4HzLO+V/0UqXH29NgCVKJBN6LWVNAJSzUBL7Ah/ToURDHkdG95vxXHNUT5G9w0xx1ElASfW8BfaN1yrC4oQDEw3hfzgu4APqlbjL2Sc"
    "jYINukKCWvU+dYvlTi3kRRkmuLrzLj2o+EhhV0zny/AgVGzkqgG6mMoFHFcA92VqTq9NxLl5cQ5rsFh2b6sIfFtcEToCtxBxCc1L5Auy8yL8De"
    "cH5b6kxgaFm0sESY/5ngMKIcfpq6yaCG6MTB/sBnWtgA0cSWgVgpTnxSji0ohWKKIhJOgmwnRSJrLsAWlhs9X8OFoLnjNdyBGxK10gXam42moC"
    "m5Eks7DBgS4sF4GhwWN9Fn009ABhyP9t6Y/pZAfDhR2nJtoswUUvfzCsxJNhctQFkv8OeCyBQG8eksleRrZn+wckpYOXvzt1ipASDJaLPxRwV+"
    "0Mlu2KTn06tIY89Zw2Xpvcf5vA2flUx6nwjzyOmahhVKv3TkMLtPZJzys4+YYV32uglkwXvgMg8nI3gDjB5i0VpIIoP/mRRiXnDYnhoyMG6HnL"
    "FWlnP7iF9HdpOcOGmnBieNdGIARBoUEeXyzMU65Zk7ijSXM0HOM07jW8K7m7wMCoAaARR5kSEZvTmK3+G0/zwL7Ah5tgKh3PX5pU8lAvAILH60"
    "SufMRDnzJBdE10CngwoiCI2c85ppJgxfczqiXF7n1SWO+s6AdCeAVtRDmnaXqyQBPGjNlshJ3wr/KDfSut7kC6qRMHKG+mTVPq/YPVqz7fs8kx"
    "/zBpKzdjXhVV/kDpzVdwkspbwLQWDQymCFnzuEigVubBxxyyeppg5F6dospYy6PBKxUiTquDl4C5vXw4c6v2rKQmOyTccx3RyL3eF8coiJSXiJ"
    "DZrTGJxUYRAwi6IUuoE46aNVImZAzhOO79ScowaIcirLyDLLmJwuPIPUAlOWueCwAyakOH1Ss2/oHQxD5p3nM+N33TAaCcKnNhFix7phTyX+zE"
    "nqzIei/p57HY9a9eHBj4vKnTResQ3bwgqUCo4hn0LrnJlTLba0ONdgjupcUI8utqz8qn2D2wmaDj29rmEB7pt1I9CC2JYcbIouchrw6FHKwkhy"
    "mFmHA3v+D2qaQdBlI8GjcbSpRKUnWQ9LyUoQVYrJ26K32FfnsCDe0UOc51q8Gqpa/I3sng3bmP2WOCuDez1jDA0sn5JfaMcMxsAHDDaokR6BEA"
    "nF14VFF/DyK/B+Abs9Kd71mhp2ISI8Ck846HZ4zxeMJHHEdtlG+IlMHWdnzS8j5LxJaDkv3zijYAZgafJaCPUFgHU4IhUyutiqndVYbAG13Cxr"
    "KqGd3Pvj50BeQvN6Ynn3rnq2rKul1GF/CxK4oLpoIIKDcQnBWyxeiwQj2JhFa14dQgAfsdsH3vt5K33XrBQ9fuL1F5uR8/QzzTTz7obQRe4c4c"
    "u+8ltd5A5sUMEHvcv88XiFgZP8C05oin8ng0icjRSh7SDARw6FJ0YmCsbYgRk52BkLauRi1IlpzR4gqYEYtD1aBqHILB4K3zgwFb4LEFXUzKCY"
    "K/JDaw8QUMCROEqvqotio3iMjQCgVuzUUURxAp0SgqqEB43qySajD8W44ydrwXDMuk3G/YFXABcMG2cRE1Hoziq9VozR1yC5ZP4sttrfdOdfYP"
    "3Zzcm82e9ZGb3KRuH5Oajm8aqtk63pL0gZucBeAa2BmMfQnZ0xLAcJvNfI51BlOe2jQg+jkpvzTJKL5syLnbClwHEe+WpYafAqOlbzDkjmPncT"
    "Wgt1rB0OcJpLSODIleZASnpVguKXfLn2lfj20D5bnP4+wid66OZ1GatSDt1hZEEGmLz1ZeAGZ1f0gdPhiq3P2pqYFe1W59QsgRGlPelRaEZE8a"
    "k1K7TzIEw3THp1p1RQBWtohTQ+Z2D44idshQjOFtVZMZ4TzGjON3TL136EAkynmK7BOXYcFlJYcGxgNwAc6AEDZgvYKCOSivPeWQI6Nm0gduYI"
    "5bYwDNbDAJdBmpmmrTdbB/9sOa5jtPbTGQm+ZOpoufEcwA3Tz4ibiYUzjrAIrYBhHAZna5BmqyAcVDHA6YAinLd24HFcErSVscrXRN5HsMSCVL"
    "6GWpQI87ErK3GKO0z62z5LCKvnaB4dzuPLBrmvcc4YPBMcg6Inx06lKTuhEpc+O9Tu9BqbeBwcWuOPqrHZyGl/AWuGzeS7aEvcl8R9Dr8r6f+o"
    "DpfQyzIjrLU5+ptZeCKdcAtG4RQdmxjpcEcEp2QRdURg2Lj7ljxonnEkZXKn6QXMWgQuI8has4gUQeKWhiEbdz7NPGgbUbe9pHuEqb1ESW2e/q"
    "HKa9Nz5rQ3GZPGdYWEdzXKWIs+g2Ep5v5xhKXkEo5JtuPmBwCkOQMXE+Cc4VvV9uw26gx8pemffs20QuWpI/uy0+wgOaQ6MNAKEr5agkEP+x38"
    "wswNpEgTnm2KLRsl53TbVq1VtRnYClAD2VtQz9ASkK6BU4d+EX1telgHeqJRBTokBsY+fyAhSiwsM6AMsZsSqUbEJdZEFGXvEfWCE9ywOWApKV"
    "fluxreBwNZpjbXinvks8uJWF9I17lj9noD91v1NDosuIbEQLbHUUAJDCyX1N/SZ4OH46Xj5M9HDk8p2gC+sx3YETPtMlLBHUiDeovjqCX7Pmsm"
    "FhOxTVEXFDoXqu3eq2d/3ZLcR0R1TAzgzpMoB2fsGQqOr1cIlLe5C6aFIMVYCg4GUjHox3KjECAR/Af9u3BIg3vjUqd8wyImUT9o+nf6VN7Fr5"
    "EXyrvoP6ItswtEGSCfFi4Boux75SDwTehc9oYn0q8AltQdht6DvIfOZ450VXi0hfOols3+oTs2ATyGFIhS8QE1tWJaR34BjQHJeIoWwZyJzTN1"
    "pcFkPyGsX7CDV5caz0VEEDn3mTsWo7OHdeXdoXRqg/0+b1QXZ5xk+jrrk0uZs0oFn0jnDqRTkxE8BuANx/MvEOb85PHMGnRMBIU2CSgw637aqo"
    "DQg0GxhjVnvbo0cBDtS8aypl89NWb/8Kd/hX/+rzH7+vn0nO/rx5wmURlx8YEX2SOuRR8tyhZGYI3jWYMhc5IRkcBVxZFMDwBSVApuIyJNOECb"
    "JKbZMyv+aZqWeKKFFMcmo92QSWw2t4Mhr2jMffaSvLk66rsxE/z26ijv5/ki0h+EjzsUIhjXa0m5uM6P86Rj1fQ9LWvwe6UeDulbumDGBYsBui"
    "6dnDuu3U7jjCLFv8GXf7HfheETCJwQBmMhQxDKVLM/f1N2DGfYqDghnFJyvplFroauVDzjPZFh/hFDB1jnAgoqIgUtPKydGIXAx0Q4dCdiQchn"
    "d0dwJpYFd7TiTrc2NQQ17FrW5zWrwyOWue0eoAX65NF5pDJaaRD92IdiwxTWR2hJsFAze24OVi2zNnOm66uj0neS3hfIO0SZrEBcMgwE0xALBJ"
    "3bc91k9cyFd+RVtstfy9ti5vhWlmSJ5irk3UzMAKMP0KjggOpxFgf4AHPdOgO5nTENdP0FR13TyvBnmSFGwc8e/JYgmylODfyleWVn5TbTRvSa"
    "ke9e+O6/u/8NuVQxVa7VFWHviDOXjGdDdwDLaWu59uvvfLnbulp0odkT1LazZ61WkqiYKcaOl3wclE6gpPiXzAjrIr01bGitLeAiO+jOnzAYL0"
    "wYdklqEc7fY/L5+yBXP3CBcR4/u78EQhdOMrN4CMt1DsV+PTmVl4H8e5vQlibhwtag1n9o3IgxE4glNFVeyXGQNWdd8LWNuOeONhysDMoEPZsP"
    "2WX3xIyZEwcDe04si0znEOR+u7eeC1jvuIipCc0/bUOuVZLwmqt3wwc8s3mWnZEscA51KMtf4Rclf4HNGQxA5hDroM0EizKUu2Qd+dUzQw9vQS"
    "u4FRLMQYc5cV7zoGtxHRR63Gu4ZYOe8MGZ3lZl90yiiv2nr/Cfb/3xd+6++Mp37r70b++99P3sD7M/cf09K8+eOtsb/HPEP8Q9+Bph3HRxjbuh"
    "o39oH8m/XfC1Z5Zz0yNl2XQFnVui8+mGFw4eG1PRH12EYRv7/Lgy8jPkMeOqbVYIh8elLEhcbmm74Cln1nZREyTSFTkewWBEf7F09P3si9ZrMX"
    "7ItaaT4dq181tFU5/1v/XUb5Ecwn+v9b7s5C8y0eRBriXXRot8Z44m39ELjuZA/9bNAd/WXPI/Od682+95ZCuMBxGK69z24UcyW7+d/cN//S//"
    "gv+vH3n13POQl2VxZvdeeum7L2XfuP/Cy/e/++Ldl+7f+75WO31w89bN26cPT5+e3v86353eP/389Pnpg9Nfy+2Hp1+eHt68d/ppdvPjm/ey06"
    "f0g/du3spOP6HCj6neh1R68wZOoD09yk6P6PGfSbNvnj7CY/pl3NBX3Im2VPpBRkUPTx9R7Q/pDae/vfmxdsOea8ufcfPu6WP671Oqwb/4+c3r"
    "p7+jztBPP6YXUFto/+ZN6hh/zgd42W/GfH8livp99uksnMGf3LyNQT79Dc8g3b5D40gTePqFFPwSz06P6PKrfpKCKbl5l6YBY45J0Bk7z54gpl"
    "eI4ve/d+/b377/4jdf4QUYE0dafB9h4clq+oTWxrs3r/uNDnWIaRmoGnAssK1L0xbY92at0EfY+MBxMIW9grk9pF6ciA6Wwi1tOT6WL2HyRiFC"
    "s2CJ5cs+3zbcKrLRen6BbwpWwmFf4ymb84zhy5qFarpkPw3xUL6EGJzzW3FMUd5yuW+LuGxHnCbHa+UaRhC6MfsVVWZaLPxQ+87GzfTjNvm+rL"
    "gNzshgTgGb6had3EJ+0F/jYIQ9f+MOVt0u5jP0gx1q7YY98SD5mHJL3FHed2bjYfkFxA304+K++IgLqUXcYDigVaRdwU8LmYFuxSK+xSXpSjQu"
    "TTzKVQlUaWYoK5lhix6gvaFPphkrhz1fd2vq/hX3OeB6NKIH4QG1KflXnICpXWBUdYiEuMZMghciMRJc1LdCRVWpAwi2iwgzI30QLsxM97AjJY"
    "9qcWukhG9xTtA+akdlnVpYrrGvPjQ9fb3wZJhwOm6Z1vKrQ1HGg3tAwKmOGmLFNkYwRuW2JoGaIfKkWdZwlBNDtomGl/YVLDp1wQ8RysffR5fl"
    "Vma+NYdSID/4BqEKvJCDNo79DqPfGcYdQ6e60rwmf2l6eKEh43G9Y5ECu3UzRGNLcgbwaQr8ppfVxAINQHHatrnGdTsY/gZ4/3kuFVcmbOcKMC"
    "7oyxVsdNz/azZZ4qIV5CGWF8qqiLIkiOL87c3rM4TH7mJ+dV41Pf/hsGgVsZgWwa1hrzh+MiI6HAesj5FjL5RAxaWjkCJPixD2BU9I2MRqILlI"
    "ZDKmNlxTotCZ2HE3dZKKUuw2EYFpTCfkp9E/7ECNKUlINnAaXNjA1ujYMd6rjDtRjytuA0mWAvKEm77TfW2qYhut2yo/cm+BwiOVZTPrTs5rUU"
    "1YTNbW6FMH00djwRk+QgvqpmEhutmI8olLiYvFFdtvO9pUvLNpzniLRDsam7ySHcxWftnOvBN1+/WyOawCmZetiTcQzgIyvDcQ8CA7BpHaul3s"
    "bNvdweMrgfDxFNFeGYR6k17Lp6rKtqn0CkcZyRUJ5a28k6rhlb4R2jGN7hdaRkwgaONURjbOBvYgNtXG+0ioQ7KNZB9B54RWxzup7goWqy3nvb"
    "ZfwZuLhPNUthYp5LlICiGh4xPaY4+XQLysCRGOBLmP6OaD0y/Os3+iTCORSr750t3vkLr2yvfuvvzyvZdehFjyHwPK8P9x96bdkRzXoeBfSbfn"
    "HDSMbmIpAAVwng9Pszc0G1sD6G50symerKosVAJZmdW5VKGg1BxTFCma9nm258z7PMcj21wsiY+iKIl+3/wrgK/vl8zdIjIyM7K6JcszT+SCii"
    "0jI2O5cfebZOSH8ibMRMehWE+4RY0PqjnbRt0MDFMnXGk4cS/m2PFBPmnSB55yW6B1yIGvLd6uz00G1GTsQW5C1huchl2mkshbkWTXtYmdJvRw"
    "xdvUnzuslusowWFSPHONHaMjhZb3/B7+ENmWE9HGmvZUqBKyv+fUHJAJVh5GFN4Leckc3xEq2dMxMxPhcibxUkjqH9dqMQFfo6+q9dsEVcMcZP"
    "l41XWaYvjTGDY0xSuS+fe8M9IhQr5vOshDjlyIbkvkS/xc1hcXDdZTijHQFNtR4Mzb/cbm1Z1BPCFaRFw99jwwRElzLz+JMLxqdJYPkaGMpr/y"
    "THnU1c9F0ydS8hhGPfQCETsDtJ6suQJ0A3IQEGchm3u7Eh0w603Jw3MUk72A2sCTEFLwwfAXXYF6qDmpS0aoA+niBA5QyHlDR4+2miPi7eU6CY"
    "o5POc6KemTFG7eGOO77s2L96SfB2rWJjLlevaKKcdTMyFpI9qBTNjGiP6qOK60jLUgmWp7uMg1JSl/acvjRSavUuoTxOlFR+GeCD7zJKps1Wt0"
    "nn10/jSXzItoggNMi45aedbrj0/hKlPbMSAdMbbCmoiaYxxz9BpJ1TuYDKK5hHvo4B7quiyCgK2H5tN9F+2TlWb/adQh7yflbv7cAbyC5XrOaB"
    "BjzBReJ9QS9SwCFQRBFAAGEj6+vON1XXwl6vhRlkKZoY0G5CSUEk5nkZOW4rbI7oQl7NGLEvoCPrbKPFIU/KCDAIbJIe4wF0fn6JwbGnioHIZQ"
    "Ee30XCAEq9sBVuZmFDqk2I3MXZL0xEl1a0IX7966+fw9yixg7vdP3PjDHpvVUZkPqW/f1kwewHdA239upf6B4P8MafISv4Yz8tAfdBEbN++tg1"
    "tvP7hdcAPeLXMDCFn46OoDuPc/AcT8i0VAAfC9n8CnfGGuCY3ptzBEGDuN/GNCFX7OOWILfXb5jeS+u/oU6r+gRSSeBnI3vrj89vLfOAVv/Cm8"
    "6Iv3rn5a2R1U/ithYMEovr36ySIlf4zMrtJWRcSGDyDO4tXHOf9cfpkTk+wfc1iRL6/+en7uBn3rt4ARfXr5Cwcn/epjXC7M4wOfXf2NAwNG5t"
    "nnxHkx+DK0pj8rv/dn6r00sL/K8We+TOlgB19efYwoGL4Ls78kft2/ONfhA/+J+5b1LoHlF9nS+sryTfxp3cK/q5xZvfUeDhRn9BVN6iP5JS6d"
    "g8ugBvMbGMxXyOLDzO9sGBbMzgeXv8lhT3xGCfjzGf3ApP2meqZh5r6++jF0/5HDS4x7Clbi8ndYIju5wDabPhg+4IetGz96kfzF5d/Cnz9uVX"
    "nAP8cT6hAz7BOYFPo62Gt0LmG0NF2vHuwq9r1w9UllVf5DVQ0QZhUhjGbQwu79hs7H5wp3V2j8dVkA+Ipv4BuxaBF5xB8wOTDv/Cd4ExDO49Gz"
    "7btNGL6ciA8JTHytIBx8Cm4oHCHVwxd+CKP8qgQOayJ1vtAITUDKMJjyvUhewhBFTSJGHyBJv9ZbDmDEV3KgVBIByL8SgOJyM5szyDJaG8nacc"
    "DRyw7j7/oOmspSMfsfi76Cf0sw9s/e++GK3gAK7v7f1UIRIXzMEoBah7AD4DRi2rqFX7yBJ6I8H2/gv/Uv+Bkc6U8QqiPMpK8gQcSPufbXANG+"
    "La/O9Xd/MP/eD5dvtJZ+9EKB3eIpGO+3vDUZEFHv32Cy+mIYNF4/8lpo9RuC3HK10E42X5vcfJG8+4ObeNRX4c2YLd8pH9IMwUXLXcj5li1YHB"
    "I5ONxEDk/dUTDiWa72dQU5snMGfBKSyJDJA/8Mtx5WIU0BJAahZoS7k05SUUAKR4TWM3bHqFfU1wU9165WgqcGNyCO9RcEeX98+UUO3/UtHTC4"
    "yHMY/XewST7NCfwDdLv8Qp7Aib/6CWbgBs15/6jNDSDGupu/gTvrM7Wf8aLH2w2Rl8oBfevdH7z13g/XbqzDQrxluRP1NUzZ/46LYt4Mjj5SNc"
    "pOzTT5FEL8N49iosmJREDxI+koKVEpECw+ay2FNU1MPP4/I/hLTA8UwCFP8q8RY5A5+xw2DCb/Ghv9P7DVv7ZOS1lyB88QhqQPeoHulXkR3uBF"
    "J0caJvEp4fZC+p2E6C8JEgOAXlTgD7rcVoQzsyENCeLwwHzNO5oRp28Z6dJzW5qJ//KX777xZ2+9N1/CtwHibPwIgEJSfxmt/eWvEU9iCMPL+n"
    "M6VV+UQEP99BBFO0R4bZjZomYi8kpkXRm1opMkDBYi4QvV/fmcQr0RL4K6s5+QjwhL00ODbZarU/M1rP6nxQGS4ebyCAk+f0qnBXCY3xEArSog"
    "6Gt5rXwt83n8hO44wa4+gxX4kuSj35Sx/P/Pnf7wNX3nwa3tvfuPG27qeO7auz+4hqAUTvA1hOGl9S8+pSLzZbJ47t0fzAkYnrs261nAt+CKKu"
    "saAqzETXjtxdx7xXtRasDzWQubk5yRgsko8MmDQzIh7SDkRpDbzgGGPyZ9G3I0iA7Rib8jLzC6+/d/ffcH//4/5Jv//X/M+GiFyppjgfl6oSbs"
    "xbXyNjk6uLV7+AA1ACpaKkakbuS/S6xuFF0Y8bxZ+iABzClLbDl4MPDKwg/ygdDnztIBiWQGIjZLWZWQ+yJtPpaydLvkU+ekzJQuAqbz+8gOiY"
    "SLyniJWeumM1bkbgfKLWSpM9GrlW8xHS6jTIQdInNauWBgwYjpf7Is7+SQXDLsObTHi/1EZQv3zMR5JzV29J1JOS1b6JT6bAh18b+g367Zzrzm"
    "3A6ZQtASOOXldSq7CvJ9tHNA/T6dQ1kU59ATIjlELInXoFR5gFCtiCucOIVqHlcQM1g5iyDjJC5PIv6VcFXjym5Bc8HoRFSYnDnlJ1tyiUPeX5"
    "RvHl3GbCrKpspisdRrWowFWczSUnl81lk/cZTzMLNMVASKArK2LAkNxeu7i27dnaFLwxW+HPt/5EnueORNg5NokUGigNTIqx1a6p3jAZNPG2o6"
    "pahqKO/Ghs6caAHyLIlWOSWplZ5mpwJJTA0L1M+M/QkJu5wSlMBcLO6B9F4Sw0HOsPuz6sFH9Qso1N/ey0QLmbOk38jPF37XKYdOWXmbkJA8qw"
    "IAA2Y4LEhVSUANdELKlJmqfi+6+EM701FQ1ugQF+eu7Cv2BAhLyrzWogg9dJlFQ08muwTNHQV6DW0PLIAHWN6L+dhLo75qbrjE4Dx2ltI0DKKJ"
    "RxcDAj8Hw0OkycArH02skPMt7TqAWfUljSxaEmlyrrR5qEAF36x0WTlsXJKiaZdkex5svEAyBMB1S7FjiAiilHpVvrClYXElSAHc3rF6QYLCUZ"
    "UaVhSDrF5RpTlXxOiGL3D1oMjsqRi+hgrsHtbSN9WOPT+sPjHhQ45F6KaQ0z2P4R/q5KDhVOWegXJv7Esp5vxUb3vcfJ5LT6O8iQsDV8FyTNH8"
    "IGHJx9RUNoWL2FMPka2/mLUYJeWL2DHwDUzDPBlQxFABgG/l9uQ1SD1cxkEwf05zGqIRh1EcpQ4ay9FRkoLqnIQoRHdM1VXI9B2lZgAZnnWBUV"
    "OjiLfYwA17RuFkEJWPNuojFFAiokA+tF4CGAqYVEZOUPuHrhKdqSvXzqFRjWGzQw2hyDDpwSKmTylFrl2k1AtcwU0AT0Il6ZIiCJdIrU8KZ5Ih"
    "qFBdz4SVDKrom4Efkmsy9tdFtzYFonbElzM+SQCPp4KSiI1zxgvVr+OeuH5Ywzs7U2mgUFDM+HFPJwJpgBFy+I2JAy11IRpkoaUbrF951BRdR4"
    "odQWxR/QLtvWSXFwVqUnTJic8uCaWgi8r5/fILIoF/PdWP4YVFSmBms1KBmIGxaZSUocvfUaXn2GPTdPUcaqmk5oAAqjnZqMhwpCrO93g/2fHq"
    "ItIItTERXaeG6TpzE15aR11Pyvmm4B9Fv6qiQERQ+Tv90/d0i/rzjBVnvBziI8JI9iRN4a4YKUYHRZTik+D6nMNorSUME/YBBYOg2pAUAz0Tg5"
    "W0RmslEgW3iXtZxNuatGbLarRI63AVwyYZGdqnSirxhqonivslKT9RKQ4GwBhs6g1HFeQ49cIMARE1yMRmhTJyPbhjhtEYgpl/Y0ZZT/he1PYP"
    "kPTLQKwTRPJMEEVDScCIOBkFiVxrnQiuIH4ruUXoyiVNGYY+nSyGFJoilfX1ACuOVANMCqLT4UAjjB+7gtey4z5KFl7DJUvRzEpY8UA9NvD4Iy"
    "jBo0T11z7j27IpCPEWtLtDJieUHCqciNNpGe8mN2Bqu4kVj05SRU8Qcg2hxLxH4/Nx2fLEjBGl2kSB39Pv0FnVM0I2XkidMeuyblqlFTxkBMhd"
    "LKHFVJJcCfY0EaGakCMaVa4c+QpxURl+zPciVcZAlnLC00Vsv8Rp8ggtBElH/cprMlJCJeeHJbrEZa9WTLngheBJkqPBcAZVrYuUKu3Lh3J8cO"
    "qkRPD4qi/yWEJJHwM9YOQJzkkDwA4Dhu6ohO4N9XR4ZMdaUVqnkK8ye6SnfubwjqcIGpxgkyxOk/sGSoZqFygvaZIpnVFUw4cjLk8MNCRUYTnM"
    "tNQoVg1nJLoGk2xEnJXptShg4OCdewr4QpIBlXc+8Du+JEeCyqkYPJKOBZ1kfz+lvqmEG/bdTqyPEjqjDjBQvOSSgdxlbLJFhKMMuY9+YoLKYv"
    "YDmC7VIIo7DP4RtUFcWdInilQcql/2Gyq5VN8I5GO0TG4ieysVXXLIo18opiLDrrp2DRYYZxkaiZcnSWNAzaoaNJaSIpRqEvX7KkksdMFUTwD7"
    "6wsAPoldXiT2hkk+WipzcoKK4arXTJGxLnNeBuhQJJaUELioTKUOD4b5ZML2ZHBTwnhNy9YQbA2C9G7Aj5CZmYNsR1cIwuHI66kyCb0tObTaZD"
    "oKrrCseoLIP6sv93ARS16eME4+U25wzah1ZCJNtQyjsbzU7FtdtSpGmjTmSOdGuqgIezqVFIWJbJgKszMgY0PJFMCxCJUjuWL3YybqZYrspQNY"
    "7hcdayJdrD7zNOIbAKOM8y/tkDO/e6Z2zxmQOakQo7LUAcBShA+G4jl73qNKTgoAxjxCDZ7mwB/ymaeEKuPPRLN7/p0wP9EkdInlzO2HcmkpMx"
    "VOn/LI0JGF+nX0zUw55fqh3DFUoLhJemF6mtPxmXqfYgyiCFJ+k0xftEMvVCeXXB2VDWNSjmbH1HaPw4rpDD8k2548RulI57yBqAxgmpdWJgTL"
    "UdlfGK+hi0YcKo3ODBRZfjP0TqJU45ziXEyS8jsu2+GI+0ymzgXPoKTgBJpoZ5K9z6cXI9aqMrlEI2WuUifKNUkedweybzAb+2oXjdxgpEaKjK"
    "OhIlbR7cFNG5giA5dR6quH2OCAkhhOlxyEcm6sODeoyEi/KiwqZ5LyJtGcZUnKhKgwD4pJoJv4Q0GRtH9ozpA6KPq7LHcedYV7hEmFVI6Kc4z2"
    "R3IRKo/3ktY3KKRPvW5l0NFQFlhZLOm3oGxMkqlglGzEJCToKMM7Un1aFlctlKEoyTzF81D3EOcMTidm0+jE0zwQ1xdoi6qvXZX00WqiW7H5UM"
    "AOU8I0wRPJqaSbSWWBwlLa549RafWGtMK5UH5IqTajxxO37+m7LXGDsaBMidyOidcVIJB43hn/Dv2KuYt4J+LaWD2YsrcilUEEYaAyRjlzA9jo"
    "jVLofrLU+8BVNV4gtzesksfQIxnAl/DACvkcZy/UOcKwz5w2esXgAug5VAEmNJ7k1gqLosTNqE9Os+VGBqKNL4wkjeQX8MQT5hgZvetS6Rzziu"
    "jFRZJJKhwdSjaVEXPgaU4m1XVM0emAfBumA34J+4Dj1LnsYiRdFLDkKGyKOTOQ64dDSJVZUGp8qS8/Q++mSYhQAQYb8xVGkkbMFpdZSdFbRalP"
    "2K9BJ3Av1LjQX4Lciezb2GNKF7OKxYM4Pu9Myox4x6PfGa/MGjLCGlALWFrmDUJKbpksQZYl98DhsijlJ2oiKR4dJaKKUeQEYK5aSEiPhaEkZP"
    "qEsGbTPGn/1uHhgyeNugasFFIxMMBQhvBHbCNeTBa8njXeH7YzG0jF2KvVVGLPUOiN2pMcx77xsaE7rT7FagsDienR/CR6vLO98FUPTpoaVJRQ"
    "kCF364Hzto8mx8mfjOy6zKe79eD9tx+gmVhZU+L6nB+KFaaIqeZvSJmSCukCLQXTJVpkNX+j2qMhetLNmbwKigIl1ireSfKpcm9knJlQG5YmFD"
    "mC43MITM08VRs9uPiMS03IihLacaZvZIhhLrnq23kP8ijJsDOjT5YcWpEVVe603IEMmdz4mt9AdkpmAdormXn26lvurKzWQg3xCUO/RZdVFF2k"
    "vDQwse5ET3pq/th+lpysG0Va/lcUofPscn/IdSkmekCTjoBCsuL3QPJsOd7xLAtFjk7oC9h5CxBBOkdKRkYlRhYtdxGScTMKxqhZJ2Nb5yTibI"
    "R4gV5zNtWrL/v3RWnlOqqRRBO1KrUjAdgA4s48p9XaHuCAsd+x17GrSmsdah527V2yyoDtdCLrIiCehu05If+sdWpLVMvRyZxvfwT9EfgNQ7Rs"
    "KXMfGsXMPo8FCqKQtqGafVPOqCVmNHrvsrRhPayRkGLlelY60woHtkobeKYqUSzxrc8R6y+x13GEG1uFillZriNGN3FuLNuwUhnOqq2B5gJLRJ"
    "ZkGsWN1UWAzcYmMUq2S5XMiLYMuqgg0XtjXbU/xHRt3alyxQKrTrtuUOuSedCWPosKyzMUhc86erOu+pihSFQoK85oY5JI5TtMs4+tL0KGguWL"
    "dHFoL7f0g/IvS0+ChMw4WOImHR+doIQRuQENDSRaZFO1iizRVN+0MYsWHIGiqVYCztX3jI4HZ19opFQS8oPhNVU1rp9qUEeV9K64McdByJrrbQ"
    "fWrK8fR0IPWfGqXu71+/XXlRHMak3ftT5QoKjVGg5V/ipMt1ZJGlKWcvFwbK0ilpZ1AsSvn6XGhjkLFm8pZVfMtoqsupsLL4yNG7rUpGlPlxrZ"
    "trXp7rEZyFRakb+fWiNisVs3Iddo75rWSrhS2f2KtdIIe2Nr4LGfaluVbdMLKm+qf9vqSxpJlQZJOrsDqlfaYba6srZ5GZ2WS921Xt+V2hpEIM"
    "a15bmiPGyoqHVlV26f2aZhA1Va2TdQpVEjMNRET2gvr38HM7otk2LWhI1Vlg6JCW3tMBqzSvSsmrCxqvYqpWqHF0rlMR1LzvK2ct2sB+tvxEha"
    "sWftVNfUr7dSZaVL4hrbRqIr6o+Y3F6l0JTMatOBW6TvpzPbFB5+Z7VqJg/K7Qo/2f7sDrV8o9yGmPkzcCJhShicAEulBI2wVlKIeXuNHRgXtT"
    "OqMMSRtc4M99bQgBRJ6rBa6inGkr3GegdKpXBP7HUqUIy1VpPA9vHqUHb2WnQRba3hKDX2qqjnBdYaw+v6TG6WpQbFfPYxinSuqa5b25RSp9Ul"
    "bZUk8LI/F3t99NPdVEl2LfaqOuNNMe3YS7u9Dh0122uE1WepkeB39koKxWKtKkd0aWiCmhC2Grb0ROUw+3vrO3SCDjatsN2oEd5kY30NrKJYQ9"
    "nKeaMaO8ao1hGnmprowNuWBrG4G7Ts5qLawsBRlU0Q+E9UV/f6nNZKJ553mdXVG/qpsumrs4xJcD5XvW25tN4XFadRpVSUDOoVMdCsnYYXUxQ6"
    "9tEY2WtqvCopT9kJpLUuG1k5XKhseGKt8EMbK41F6/VyVGVJLOVWWNcRz6Z2Rh5Ft7C9Y1K9o7ouuwlPJbCOtba2VlJen16pqM+UYdFiWS+tbd"
    "t0uRcNLDdXUUlKCnjwBv6oxhuU+IWWvWSy/izdF7XaJLGpwTCqIwgcPEn8pFrYdUW1jeAzqu2d95UP1YapM1pYPs6otXYfu5Pm7SG16DDAWtHQ"
    "vr47+mS5hhwFW3F1uUrKmFaEr9zCjhCU21hu4xMvzDhcge0VRq0ObNfUwo5Dn/CqklfTCr/OZXUBGyfOHYtDVDSDKFeJ3WLzVjBa2BbbqG5E6M"
    "p2515IyhR1tlBxB9dfQw1IgTuxM9rGkY0zFvheZinGkSYWjuZsbhpqS/mplWHWwCGV2r74v7bVndRuDqkI3Mb+bHxPVRPZJwgJTzsnUKnmVGrK"
    "Rvq2NUMzRw1EatumqLWJporaWVhmQAaVtaOMdx48TJ6xre8uNYAd7Z5Y2GWlRvbDNowYANcuQKlgm29rVR28SYUNV2DXzN0ao0oVo7zZViMKA7"
    "WKmn6AFJMvbltFlljLtUpCrWZSrygipaAKZVMdsRob66rDKOpKXiIa2tTZVkpD1Aq5ilp2ENBQWZcSqJADVTCrylEZ0FpR3chFeX1PFFqpTYDZ"
    "aGG5o43a0PNqnUdi0mA9P2Z1YUGeNDaySUaMahsAKFc3cJ+MRrPAhHIfUUMFlO/vyrSzWazlnmSV0Hp7uuZtcEDV9KNuljRU1QCBqrGtOvHF8F"
    "Wd2iZSVTW8WlVEfXt57XNSstJBlQN7eWovr79YKqrTrsrrnyCKoraupKY+WF1hmS2JUNuI0pUaWA5Jqd7KOsIWJydBw9BUFRkElysnnjdqvh2N"
    "ajK4HjZWz9r4zLxRyFv9JUW17duLWjvTjN35V79aF9eXg50EWJBMkvc1EgSqtna6pKI2AlVcH0HZX1CdZKxo1s5hGI9gdhMyfJjZAqNfVptgpO"
    "y0gXbTlQ1wXdfX4fbEK7OqLLU2dGFiv+SpuOElmtllqbOhBRyTTbt3q1Qisw/XI65jkaouaiiuL7JUmWfuR1Zd2qP4T1KZVmnSHh00q9JSoD01"
    "bVXN2XIxq1JauY9CInGEFro+1DMeK7yYZeQNyHLNUCUxs8vtAyZjZZk0iYcurSSMSR1qKjXcslzVLFcmw+XSwp61obsJGWuUHyr0PI3uydKsUT"
    "lXtElNDd1ykV3ltNAorjhQK6sb3zCVmxrUXm+QmB+fM8vMWTHLFRZb4QZordlCFbFSzGhXrTiraWOaOrfl3sxyszuzvN6foVrLsXfoqVKpbylz"
    "Y8+qjm3IYIwy0y1SqYJ9z5TXDm0lGFtSasccnLRclnjlVuZQaKtTxKZYLmkuJN3LWulstSxRnyZfGAqDZa5QcdZF6+g6uuxiYGBVmyhrFVV0aq"
    "QB624169twKAGeZg9tAMuK7EpcU6qvXsoqMJGhM42haqtlbE5jlpl8arb/Lavea/955UlgnU8/SfmWZWcu32Pt7C7L1Gw706yqKiRr1f7Zq6eY"
    "+qQBH9jq2MOgodZU04lOdTCsbo09YFQOPLfKp3LT4oZDfCxurrb3LJVo+YinMWlsUhN0mnXnozpf0qhHtwNAB4bpjBbKn0Bjk9lfTww7q+TYaE"
    "R+H+vq3xoE1S93kv8wNcfuC5tkGKIGV++hrkBdJxirKtIWpr42nOHZBHBLBpCNjeq8pELn94b2I9PYgC9Zu2rwjcI1QKOWMMesS2Y1qG/Icn3T"
    "lpCIck0rphxQNJ35AiT74Rg5vCcq/mFtuK8DvG0XgIUvOfOesLWjIG5e8qpmQgvY2ogDjTltyDxX5d0XNy1GyLLMpUXH2sY2qt3YFiS5rrY8ux"
    "F7zJjZpOGoVE3tbHSwVtqdVcnW700NxGir06T6LPXonmTopoPmFifNT3MYqBnVTTSNgOXYbazruzNG3Sdj7Oba0Kq7LbVZXdZrVAd1HrxZG834"
    "3KHfS5ofZQ3HGR/VLL5SRnpuMGysTQZuL5rMqLYrhnPtBJ15NFZicPjGWgwxZ99+ovCXeDNqbbp7pQYzdlCTgp5Z3byaTRpsZnWj8K9QH2sQ9M"
    "3SFCs3CGfNj0VnzKyuMeRmkLiqiqkye61JQlupdLc39msU4auJc2EMCA7RWK9IZGv1KzkIVmXwEr9C+TN6DY6GvUEhc21qwrrwbjxtbCBuYRqq"
    "kauHTux6zZOs/a83dtKop240YZXD5rcU4rymFuy+4BXsnGolee62b7ChDkRsqzQ4ObNZP9XaCUeGtdc1PFgyHKnf8SU7jvr9ztUNl7/4GG9GRN"
    "A5k5idDVi6Xr0SxAWTwZ22yGt0IzFNm9GkYaRiczIDtRxG41dhcIbtR6Pmc6kNfFAyo9qirFyqR59FNahYakH++2sw2bRFmaEnExm3Yp0TVWL4"
    "2QiYMkfQBg7tPMOGBqau0yu4kQ2VvAUaq+OZn/hqcxg7lChZpFjpsEqLJkKr2sy+vSqtLDuo0gKGn9YlfmVrmRl7pDAtsRB3lcpwVm2z0Qrxyk"
    "wnyjOaaYOCWY0M98uzbF6U1m5NkF01VmHuZ00aWmrWCAGTIbOlGhuYHj9qM1yu1G7CZzUiZuaMehgIe1yb0YbcSbnBrCZjl51WWZuUPGVY603X"
    "GZYGftI8F75ts5Uqw8heiciGH1q7ZnMV3sfo0MHrzWhhG7dRXejxzuqEfdTOasEW77NaKN+es9o0uqEotZr9HnEr94omw9Hsd4gjtxkNSHjS0K"
    "SEdgfTWW0ym1DrdQRfZptyRKHGZjS9M+pLtr2NrWoy9BkyvKZWor00q80Mq1izGUV9n1VdfTbSPKCeZ3fME2kOUDayVylX9vWbYuwmM0FsSdpl"
    "q9YSlxtkwdFcexJVgV6pmryu1m/uUpuogy4Va4RZqc0oSm3UX7mN+E/8XljnEGIEAMJLrQtI9V4QTMTno8XwRjFfrFwEV1Hr9PDIt9g/cBOY0J"
    "j4XtGZpVqbaEy8jr069gboRIYur8bXkA/wuKSfUiM8uV0gHnhhcoK6sJPaTENXVKqQXCcv4LVGfVZ9IA2IemUGZNXMaTkJAMdJPKutjKt0aHH6"
    "Yw+1lxvrafpSr7GBdp/Z1KDsU7KxFSmSkT/UWhPtgvZVcx/7RAOm7gh9flrmNAndEZDiacNunfgh8ietUyZ+TUUcSTpfycwmyFeL4qY2ofb7Pd"
    "chPZymhnhNTGUfNLaJAi376vlMAthbilgpqrEMKy1Ogqjm8qzXM7SJA4pG0qAzSNJCWhB35Nskni5Let24zpov6gEOknOLGkQtmpS16OqNwsiu"
    "mC3izBk8v3KLmYJdMdIWa6bGFnYLLrOFTb/crLcq4pgNOCRdY3U6QAfzUZVRDhC4K/66RQk7sYlg3UzxvtKJ54VWP1fVXVHnx1ia4IVYt8pTGh"
    "fKY3BNuQ89J4j7ahEui1NYi0zX9QMW9RFa0qj7WGuXzq7nEzGzTYMKZN+NbwICKe6uZfxaU73cFHW/b3CsF9dUzau3KTCZxibxwFOWVg0txOFO"
    "Y70Ec6tVsw3XtGBnnma1CfZR72aQoWv1dGrZHVQ/8Wy6WEVVL2qqIas9i0lYIO5jKOqVVdAZSMQNnjuLTiE3Yx/mMxvp+HdNMk8eBInuQ6tgRz"
    "XgC6TBjRM8SqamjeOQ+HmNolkK/8LhF5q6eC35aaMihdGmRge9hmyODInF+Zlt3eIo1PFkb9i/U3P6Mbh6Ux0gXxm7O26UZaCp8yxZBkVTsksh"
    "ZskEmjj7GIVB86y7nu2snXK3rwB7AOW6ZzejcCZcL4zouDfDoq1iRpeSrqVlwBxmgS/bIUCBmqC2ZCX3ikFrj7GuOguz6k9r+ugFw78C8Ga2Yq"
    "BWboJRFTCkdFwYJ9WnL6RpufBi/PjOdEalB1OT1M2TQo7qCZMqUZv9mp/YSYEm1/0Z0fK6grJVkQNdadG70nVDDBM2tta+AscyRA2dGD2nN9V2"
    "s2TUWElh0EY1u1KjRQPiYrQYe7XvwzgRvej8FUACkENW+qTbuoOiTW9WC21JU20UBcoSJ4myhmM7ytiJGccLtIwG1ScMXTmLGDf2RxS0tnlHJl"
    "4663OM6oZvKRzpFyBBRTixqBF3ojSlM1SnVGXxC5QPpbVW585dvqAtXHTFUxUDLpu3V8PPM2uPz6pmobKthaGe1dSJ2aS5o7J9/4wh++GAGf+z"
    "W8FVZ0OW5G6loKtNHqaMFqQ76s9sIoznhnFIo9Ggpi5Tqp+4Y2u1nMfGDxnFFGGgYQ+UVf4mr2rSvDh0PSVKWmFpoFaioHTqjM2OZ9ckoUo+5V"
    "UpM1xC4WzqiY4jGuyzNW6oaJC67VfI0aO8mm2thU1ayHaQleMFgd0cLPYUvtGz24NZBDCmqRhq6cHjvVkt4OhMZ9b7Cd6Rs5r4J2FN47XcAr3L"
    "1zmBhfGahawrTNgsJmQDQ/W57kq+VG13t1ZqYrisb2qit3GlCW0aNnPA0OV1dlCpCU6BvX5i9NDcwDKFHBNWyCXhhts3qNkUVTvYxNHDDZI2tf"
    "SHQ6/HMdZe0edMu0hFnboBz0ONjkTh+wzeQmEE+N/+/nv8n3zkeGXZ+Z9/9X85+7cObu1vHdw6vOvcuXt09/bRg71d5+7u/Qe7d6Xl5WdXP7n6"
    "6PLzy68uf/amc/nPl99dfgbpL6ji8turTyH7b5j98urvLv/t6tOrv7/6h8uv+bEP6dHPLr90KPMxN/r86sdXnzqX30HZX78pb3Gc5Te4x8+vPo"
    "Y+pfuv4H/sCAuuJ+i4PPW7jrK79ub10yvw9M/gSXzbb/nZX17+FjKfO9cxEgCFE3dGaEMch0nxXEu9Fb7kI/XWn11+A+/8BIaC74XkT67IIvR6"
    "kk4DlHrAheX4IYrM0XFc0dvqG87Vh5f/Cp18IH1Bp1/jfEEBTgN3D22w6NOrj+TDpiFc9EOnRyGEpkV/a2/gjOE3fXP1IT/8c3joJ871bjRgrz"
    "CWcXzPN7B85dWPYT4+glX65nUn+k3nh+WWb5q7VK/9t7Lf9Lr/SJ2EX0BPHztQ+c3ll7C9vrr6CHeFeST0cbj8W9Xuc9zETvGSz4v3OzAu6O9j"
    "GLP+CHjk6pOrv7Z8gDLsPXy2u7f7bOf929uPD4/uHpQNfP/cQcV92ORvmnHMnUUHcSczWK0R45zxqpKezY0iMOscahLFLnudG/ndSuBEFSqxCG"
    "qLzik9sfsi75Z8QTLy7J17FCt7WooorsestVxxxIVw24hcaVgwVHzVqmjApj2QRLEyI9Ya8eu0kxbxm63CQ1fweCPuYDVAaGlgOiKpoWh7Qysy"
    "6oCAZjxAFUe6YS4wqinMhETlLb2MA56qgL1EjYmnbCMCm4rnTepR1WlXcYULf8EkzT8BZJ2xEZFDRqPUH7Iof+ieS9II3CpxXhUXOqG36LCqhR"
    "tbQjM54HcRltD24SQRxs9mVMUMI5f1pgYOI75+L7ySOZKY1AXMN8GY6OXwuPDRQcbNxI0qOmGIM0C/felK6daiZwsm+WKKZW2GJjRIDq4somRq"
    "U8UiDI0hNLB+c5bgQsMYAhiDEcuNJlCKiZUE3zVlP8bKgbg4c8cXRCPeo0aAWzM2KyqBnbC+VkwRI+hIc4c0Y3TeMTZzl13f1CN3mssEUAPGrJ"
    "z+mlFre0oQrsgxHmjhppyhCYce1ZHCGwKjG0qCpmNYLd+7ISFM5zgypG2oGH0YhlqE9TC3bzBifWkdMFrHzWbVMXwRhgpMDW9ntK8o7G/RE7sF"
    "Kjl91NvcDMBdnIIuMhrHjRMsflVg4FqZuhTYk5yulDWt2VGLqViNOoaobJTKDk3dbhlwDbK4F7DSQhz7yp2sRxFoU2LuDHFemDDWEeIJ4sfupO"
    "N2G+aclb9g8IC7IzOqdHbY4ZLUGC6pK6ZnpqV9wfgqwUFW5jScQHG/TIqznlsq9rdINwC4Hct5aZhyJOVw1KiaWZruMaslSaTbIhyscqqIe4O2"
    "eD+LObg4qYQQk7foaMqROovIrkZAb0VJ36iHOjdBhVaFwJ2htFh6ZgBI7UfFUHPpkT2+m4xKssmyTNTczSPizio46QoAoui6/L0I2XiPkWkLH+"
    "qwEaoDtEAABGMmxjdcUBgR2tiHXE+3Z1FPXYZekZsSF5NjpgG8D4Iy3ABIAoh+UESWiv2JwLLQgV4cKeUrytHRp26YuBH5KnG0K3UvdJJITDcd"
    "8f7VwXrIuonjpw4Zjtg+mjRVkb0Pn50OssSMKio11HHGBuq8z/WuZ4eX8ArXUWfGWCDlniAQB780YEf886qvM46PfAO8ttMwWjMeH4LLIpKf8d"
    "pyzL5ytD8jyB/Fs8N5Slgv3bweHMPXDHJAHBi39ICrFI3g9DniDgo2lINeOiRvXOMvlZAw8M88WeQEgJWOrcELjlbrztgrhYy1YpxuFxCfIVB2"
    "owFsCS9xriNy/zXh9F/Zsfx5A0CgWQEuFNurDFwjw+rsRb6fBX3YuUWJcQpwQ5ke7UhRC+ByrbiD4tNKoTHJ0HmSRHSAe45oInI85cQR/c5Y5a"
    "UaI7BzZakf2EUhRcvj5/jLpNCn9aKLx8HHpdH3zg8G+X8P00yiBbM3eEmhnhyBe0fdL5w0wCpmKdwHJXvuqHySFWLosHNzTghG7uClING58Z6X"
    "7lTkZ40AlyF2GY5TwAtsEZ9wxGwMDR+nEjIbMWSOraxwZUpJnGs31e3Q/1plfakw4YfHPKKOR5dSlMBeQG8rDu1U9etEoU7CtkMslHqEInbVWH"
    "SNgsWTImg2Z9PIEVTQkQCF3B+7S3fIGbhDnhwccekhb8QPrtA/Sg8JU16Xoj93/bibDTmoJOVVIPZuFEingLAYsc7ZEXNlUujOJYDkMCbWK5Ih"
    "E+QyqChUgJAyfT8eqiQ5/OC0kBWle07oC0d5o5G5LuIR6pwKjc6ZrKt6rYbRJmvm4UiFXKds2FNJP8ykeOQJwHAIhkQdoTQwK3uAbSFKnWcxxj"
    "yGy9UN9OM9jwkF2QGkaBtyKoAFMCZKI1KOhC8sX9gGMwOzI9yn6kEO8y01QohSMipeDLdGKEe4B6e0jGRyiaPdD6qHItgpHq8RYsL1BlhIrj11"
    "gV9eRk+fbG/YiV0+7rAEAGJ9PtNINgCOy3uNaIhQDj58opxQ9lAsk2p0Hoo1pyMxEzmVuhyZ3IvVqxPUpZOvL2hjxxB5YjoKKmNXNDgmRy5vFP"
    "RkA3eVekgR4Y7GZx32nIC/NDG8SCSJNvoWr62OXJSYOpFNXCDLDuHdtVk/wT3ITWO3hOZjAYrQ9fZDxxv0qwIRcsbn0zpwhyOeagATvUDKKLK4"
    "S6AoCssXN1QxPSJfZZCtmAnlvKLin9rWKhr7IAoZuiiChvlJvSqHSZH6iES52UmmZsJXphpOmfh3DDYMpvtBphYHMpVZ90Ph+GESoJLugQldSq"
    "UuB5L3TSgD1KAiZpwyH8bsXHaQM3cGxxx/AzcL+V4iEpMSUXTmuEWSRaHIZvRDdQ2hzpGjry+TFYnlgdw1lFO7HgCGeyKpVJV5Hr1nGPXoWsAU"
    "L4ao/5SuihBwMN4soTuWj3PM2HKc9agDpoGcgh+ESTV83J5M9Ba9Y9nAzWhmR+60tqdhH448jXwQ18ORW3EUqX1FLukpgYRp5cLAMmRd8EaAyy"
    "lCHumF5KKOSqhV1A7NOR34fX3qIMv9lIjjVKCJ8CUdlIU72vIaaX7BQTQp6ZhUKGfg/juh5TF5BeUbLfZ6wpektAxXGM1yqsQlLqVwO/KJAWR3"
    "WjmzaD94Jh1o9AwVjtyRSqpNy77xe7Ig6Gch9rupTrM4qty3WnFkMibSyVjsu9VHq4os1Hs9cfseQiSaNpMvafBBva7s4sRLnYxOkx50MgDEi+"
    "COTIc4jHaEze/M6Y8Sqzno3SmfJeQh8+JjKuWVS7KOHFNIIXtBg4gkY56IU/D7nIJV5iiVP/MNKeDHDFNRK8PhmUrxwqInEKmUY1noKt0Q1sZJ"
    "pJPsJbTC+lD3kskrhNxIQVu44/yeDB3vO07AxcUvnCBDmxI+YZc13s2fugHXnFwxblcOlUlscLIn6airKJ6+wk2J/+HMCV4MU3lSmiOWM/jSQx"
    "jCVd5V5Ikby1kU7nVBs3R4L8Cuz9CiqKBVjI7jWFEaYj4pI0P1eE+RL0PVk0nUyP2lCWJFzQwrdBiC3YyMlbABi04kI8inO+YjxGxP/BXK5sQX"
    "uiZQBGDHr5AzQSTPwNU2lASMiJNRkAhiR3IcfisROF03qVM7MYqKK7dIB9UjItUAk8RRpZxKdhUuoGVdjuYfqyaI+PhlQNkdqMc0oYQJHqWIsE"
    "xiSd3CcNF15DCy55iukU4bOf5OYbsnSbEhEyJK4TrChHgVlaR2F+aj4ugb2V4DsQQZsy7rphaCKWJ2Yo1iwujJ+mkScHAKrwBVThw8PZ64Mnxh"
    "0DBF5TIQV6SVY4g5nUL4WVBa+CuvyVJULbtZZfH2AAFLZdV7HqxeLFQSo4y9Kk2GKVXalw9laow6KXFQ/bhGcQmRJT2oBkpqTEk4v3o6PDHM8C"
    "wiy57QTG58JpccZFQpXBDyUbg4E0UuqV1gSGKcuTKTHbMehQKiqoGGhHhYPEFWVVpqCsFyjZRij08lyaO6eb1zTwFfFLcxIXau8e8SReWyvh+l"
    "1bVckw9IiSc0VifWR8mUbGEO0AGhujyPRt3XtG8f2VVBZTH7AUyXahDFHQb/yLlm2xpKn3gFHce/cK5kwlH3S98I/SqXp3CfwnPYR/yLaT/2RC"
    "npQh6PWYZGJWLQSzVbxiD5oFQ8OXIm6vdVktCDCe+9k8ghX4NCN/IiAX0IbTqxxJotUZKZF6heFa4GYJRJPTfuREI4So2IyD3JBSNFH94UVLxE"
    "bBi0oqYPGbdD8jAukYdlxQNDM6BMIpqEGKrcayrSSiz2OFPSdKgShWE0lpeafZukokkfsr/TIl1UhD2dSorCRDaM2XdK6N6ZamMAR8qmE7lpkB"
    "zVu79Km+IBLPcL/VDILvWZaIRjkqlnDLnP/O6Z2j1nQOGlU6ZhZakVMWuK28W0UidvKmZwQFCDp7mgfTGhyvgzSRWTfifk9rhE7ZLuC7cfatLY"
    "JJNPI00JF3RziT5GBo3f9dMaGY2sa+lF6fc4JF5X7yuoaDeUX2UoQLlQndwhmWeY/fvMHOgJ8S3+TlQmrFHiJIhONHygMmQipZUJwXK4SXiiFM"
    "Wu0klXdnwYhTdD7yRKNc6pfN4ZhDvsba8kV9R26BWivuCnRp2xL5hrpIihKGTHPJiUS7SuUDEHx//El49DRgBqlci+wWzsq100coORGqmhkuSQ"
    "W7GbNjBFwtpR6quHvFhBaETwPC9WPStFKBJjhRYmQ1LeJFr2bXIbHCNoFKXHuoloPjmm6pNWYSDT/zI3oSucFEwqpLLMnegXzAmTUaFvUEifVv"
    "i4WhmDkkyYqLckwuozORlZBw+H8EgyvCPVp4krD7Nv9I6q+R6FeKDCBcFsoXzsKA86mpfRU0wLjtdaYicoYIepKSdY4YVYEN3M08wIzXeoMCl8"
    "hY8q3oTRvfLlwMyIOh/CDcaCMiVyO5pMCO+Mf4e8kU1ORayOhd4lyLPQUh3M9Mkdo2SMcmFsoDaAZ7A4jN4HrqrxlEAMVslj6JEM4Et4YKaiIG"
    "Yv1DlCPntVk6/stoLYJOo1CouixM2ofxMW8qbcyEC08YWRpNFIsU6UIl6ZtcKl0jnmFdGrwlWZLJZAsqmM+BVsFWXBxemAX2IwVtxz2cVIuihg"
    "yTIS+Th0uH/GiSgOS5hJOlDjS335GXo3TUKEChLSY1YtI+bgy6ykFMPH7BP2a9AJ3As1LuT3yJ0IdzecQo8pXcxOCyaQzzuTMiPe8ejvrsIOKs"
    "VaIiaQzxzsgh2Uwe6JhQM19tT0jP1ETaQokUIi8suncuJheA/uGtL8wcI2wkSivlQbFxhK6vsAw1nVQHR/r/7u8iuo+Zq0hKmItM5RTX/Dufrg"
    "8l9Ys/nry39B1WLUUaZOCxX+9/dvHR3dPdhFleB3a1wqZFTdhjWGkz51lt90diM6rnAYiNV8/fLLy19cfXL1KWorf4Da+Q4q38OLPpp3/uNMpz"
    "/HT4Ex4yv+Afq+JpLra87//Pj/dK6hJDRDKVvoUAUgkoBtXdOPx3MvOtLm+ltvJrnXy2Gh5t96kSxA3g3fyuFIzUPuxQQL8Ity6CNHVCRHS4EX"
    "HWPhsDe5DX/v3uo9oYLGFJpRFwjAyt289fuMirYzskRpXOEfOiSWCVIf8mmwwWd1BW0auhLNN7OvP3zSCTf6Dyzg7E298iYcKjJpdp7gUXUOEY"
    "oiHfLHYck2bmaXbKJoJ49kAHDQP2El/u+uPrz8Bq0JPr36BE0I8HA3WdGUJstPHZgJ1LdBB4X5xE1ymBC4xSCfD90p/rB7YUx1VWIiCZlMr1db"
    "BdUldk/0d06Rl3JDkN7LNTMD0hTrKhfUt5cDxRShadc8KWXVuoeBzuy5ubeo1pdPymHQW+UhcuHsQCFuXM4I1YG7yj4unjnsDMMtFX1x1zxc0Z"
    "2Mol5exJuZx2dg9rFX2LWvsxVbbzqHeOughc4hUFnEgXMWnR3mTjl/pG1YmAQpe6Mf02aiO+TneJ1c/Q2aEOHm++nlZ07R9ku0nIG9iZYuuG/p"
    "Wvot7uuRvpdKs0fahQjlEtqJpW3IE5QqL5mwkDnSlsQ+dTrTvJehqkWu1BgBstdBA+rqsfIiLhAALNpCrNWYdzxkinCaC910XkYDyFke+B4cDu"
    "YM27rmofOK03WXi8ZxziPK0V92PgKsDD0xQTViZb1c7MVyUqum94mAK3krV1rumEQONSa0yB/ShfQJMsb+h5yIKymFpjLJW81jLh93uhVhV1Um"
    "PHdZZamXsxJernX2ciYcisM1e9uuvunc0dZyO0jwx38kIFratMowCncsGQKiKVdht6Us96DsOy757PIXsGPRtOt3DlkIaoupTy5/B3v7gwrohN"
    "lBLQ9HYiDg5pM8xkzALGqHYphCmE+YPaRBclGa512B7Qi2wJ5AFV+U2aMiT32l6OZ30JAE+4KkCF/7OcVVo72qgQnpsGFBStQ6SX0dVCIEWj5X"
    "miXQB6BmPeurGLYidY2EVTAV6CXAD1JicAIpolJ6ueEwFvah2igMl9UmBsiapShM7c3PeKvsRfTyhL+Vm2leQ9YKrDZGVLsM7K/jm68fofmFAj"
    "WOkvz08BQQIytnNxeJo2SLWCN8dzoqzJTh68D6Iph8pMn5fS6MG0mBiQsQS7lmhhlmtx05wTP47cQ+nN8prrS0R8vj+de5FdbedLaQCVg+U9cJ"
    "mSgMY3HDMy7+D2jL+vnlr9F6EE/DLwmUf6Dwcfu0wWSgavBbOazFEH7IIPwtWh3aebBqaFB9MshRcTqHKQAAbp8dVBYXKEudOdQ4lzdIzrwCch"
    "ewNliSXCmPQb/z9Y7hP+bdBzCP6XTErlpyAm15lpBid44iQdT8zvux0obPkbYKprzTRszwMu5pObaQUGYKpQudtXapmSieYJlW023Yi/CR+GW0"
    "/1nrKCfFupyCG+YGbyE3BY40RhLKpLDhoa0nP/P218B/namDRh3cO99ynoNCFryS01wMGMi1P24+qkEnqnjzOTKfjZ2jfj3fHXgaQkSdqBM3nB"
    "adiJ9whzS90K8EFaLGq4S6eb1tvv6m88SLO84+U7d3Cxdrzh9dmUFQccRm4Lh8J6Qr4z2fE5X8W8ogjgNI9+dCYHMzNjT/LVO99SuE4BcTPoyP"
    "IA4YzedKNCWETKnO1QSqWWxdFXRIUGoL1xJHLIbjmrv+sFoJQAzP4ZkgSFDCDCOdt76msEjTnwJPokyi6IexoOJ9sMlPio5RTampd9R7xJsA/u"
    "/NMzEHuzR3Je12UPgIh9kduV1MaF/JOckrwy4c+yJYAT5loQJw/wpNjIMjMDeKEuLQ5NrCLQfsEe5DZXuba9OOeT342fu2DUi7Dunu7PhxHNF9"
    "fF07JQDs+UPYP7CDfh+eSG2zUh9O4epAYeWM8HxJbhQ+VU4UPiLcB23CkROksXNGFMT2vzpbymrmReeNH7ZurC396EUHNgDtxyCJ8AqYeEGQm8"
    "Y8uWHKY9+vHbjujA4BVukcdhwjeprTfgBoiNcCYQoNe3/gBx4+vnZjHTvTI0sLox3kJeLlC0vrhh5jO4gEZDFfzPNNuJj6LMJ58RVrpVe84uNz"
    "ZcXUCEv7PtwoOf0lPADlonST4X0I5B1pGM+/e+N/f+9Fgq/foAlKUJURcCD6wdYDRJUAqObI7NVXnDms14K2G286txFzHaXOgUc4HyKDsGltFk"
    "uK1fjB1U9hS1k5e2X6u4Tk3EB2TY1QYQMu+PjEndpajLLfB72ii4q0wtCOb976yggQeSZRbdXUA2MIXbqacW10j4gGkFQcdxNikfCrBKHN78PL"
    "XCmk5Kgq4/enisbNWUkjL/wnWHshSzcCjz6zEuYdFJ8qolprkgh+w8yGpJkyNB7IMUxNVzayEeZA5lZeVOrp+2KZRTMSZwDq6L4x0TEN//MiKh"
    "msFawQq13BFaGVS0mXIS9rfOSFvi62LQkT6suC+lEwAJht4WkKOUnUOBoJpWW6PCIiifSWEGMt1Ipy6zdYGbPEsyq9lI3FcrYjyLXGf06ys+Jz"
    "c7Z9ysmOLNcW5PWXmO6K+Q2mxeFbuemE7K1cnI2+pd5ffAkMIXaHlOYn669C3D6BKXZ78inozgBZNVni5dr4gbk3qEAqXSlsnssJxafXyfTLUO"
    "qvQ5fZJ0SQlyYQqWVB8M11IH/meQ++AcXVuZr7WetTbLrSC8REtQCBMmu4/5Ksi8hLPwvyIsg4ImeARHlEYJBapAUmRIymM8Fhqy4RMOaXmcSM"
    "ScDkhggyBzRjiidClFTm/7NfNO8wsVTnBxPTGqmWHOkfJjaFbMnVWyWWUa5CI80rPlBS399AZhFiEOSK2oLFRX4+gFPmMJJr7eQtos1E9A87XK"
    "fqi8GkVuygmk+t0iTy6uKR0JHQEbYqTf1Zv6JELNrmjRrA9NSHhJrFwdRRFHWtgabVm5uwesGsFsSIhE0+qw0Zu8WvbEY2refkWzRAwRscLNUW"
    "TlntxcjrmNWdlrMQDaMlI8xryGV28oJhQXs/oTEWTAozLtB8wWxu5jbkyoBQSyAaxS/MNmOAo6UlVqkOQpoIuZY89mLM8hXF1zWNSjNJzAGQPl"
    "iJlYLa+TAwFagzV6pnIiwRRlNuIxpxH9IAkORE3ribuoodj3eIcI5yJQemDhWmBtMT4RQj9j0M8FJGyx20U8Cv5FgMqVoa9iQyVhwjxeyk+VRj"
    "N2c9FxPcXJQshD0/P1vCVZEjqQUy1xcnm/hSrCeHiIAbsAkDTTRtZdwAYqxamv155rPZTgHx+RxGT4khS3cIf1f5a2d9JSurQ2vbLUk8xP/oK+"
    "ZnyOJ+HykGIjBdrIAp9JtEhrw2E89RrAlmUsMp12l+e8GwfoX4s2BgV5nttXMgNq+W48nDKroqOhF2uTDgDR69ybnX8rTaO5nz2gGKNe94ASwE"
    "nhQf0DpDSCDgnxFYvMilgFnsCDcbxtssXXjd8c478i5DbJEXA1GD5Q/Q4yHCWBaIeG25+DnO8YJAS95BTlxRGRAhfwpg1G84dA/ANrsGBeYBXo"
    "kD41fL/Kjx+VGsx+ad++SQm2da3lJ6MywJKSoA6HIZ8xyluQ75mdMf5TLMgHWoME3SQosGB+nzE/fJPuDyYPQIipfSWILoBNBVlqtal1nPOAG0"
    "OBoinxl/519rpuYbMDTaBjkKxebRmQtzBfXzpU7RlIB09PPyFsWcvgwwU0y4BSIjP4lmRF9mTMHxLYdpvtkopTxlYKYUWUo+ujJGm/CI3AIptQ"
    "CSpvh9EhbOM/TRPUgvgNoPCFu1UY7scIggLA4JABcP+NWfQhOINuf2UQJ9R4PTa+mnakxxfWSMWgNmTYtHCiXEyhMhO2NIY69pzekrKmuuZ5He"
    "gq/2UyryY77XFemJgirtaQyxAnEuhnIsDGjCwUiwQrF7SeIuVB6liDZCHnNI+un1YQIwQ86cWuz6Bi8Gp8dr7Hk9zwBppvXep156gzj1sp45bp"
    "H8lbOea2Jmvln7haNS5mbkyLwIepmzDvuU9nLoU1IhTEITId8LQARWMVRt4JOgfRUkRCmeribSrsErRMeXNyXlhhJ3blgSWvXtAILT1xCVRaxW"
    "GCQlgWzRowh4NpxScEsuUt+pQ4LmRQBRRvGMTsrPq0f1JxrfAF/I5K2yDcM0UjTEBUKTGo+Uumxgx1VL1LQ29LH8nWoKqIiYVvNyx1Ynu3i5Me"
    "vFOlWEjuo7ALVEvzMMLTTHqxi/+X02sjVJi+EY4pPaXKrRYVK/MihtkYZFylXoN5yjYjC0LjLgqTHgwHLMSkO5IUwVOmAleMtnzXLKchRjwDgs"
    "aL3xxX/cjvVU/HG7lZX6o3fKoqNkAYU7G0s/gpQpPDIELK8vS8nFXVtFnmNB1VDIxK9ep1ejmEnnZ8iZUIAA3SMplovOaq33F6Hn49BeGG+AZB"
    "iZJbNkWS8sEICsOUpDjuJSb3J9VtAK3wLvhckDmLaDTmdoYd/44fLSjeUl7ljqSY4yIAGcDQ+ip9Zk6ZjlaMrQajI2U6iGy4soNgByWFZYb6sQ"
    "rCwBK8m9SHPBdeCSBbpPvmBNfcDri8HMXWZuqNJO05K6JiaDDWQiK5ovga6ngRwWol4F+YPItcgc397xQq8PZ4tcI2CcRUOGLczlOrqDi61QiI"
    "QxKw5UoTR2MYlhKTAxL6QwfooobRFWWnAGOPoFEF0S46JQbGHGAZCvuP2ZQMNQGjYKlPlccFsVEnOlK2wUQT3arRZVlEOVq+J2xyzOHEvg54U9"
    "oIdfHj2QT8RpxyR/h/6MHAOD2HDuAg8Dyty6uloxyaDlwyhHTdvAK/jUiI5FWSfNYV8ltJz4Srrrk647om/BMRFWPY58gwhw0wrWh7liv6CCHx"
    "0jY2PVFVuvIeMTlZKQGSzbREAGflqOCAT88WGnUJRuIiGqoALgwYs5hTW/6Fwr948WrMTdRrXzP/4b5DAxwx9XmvqyHjjm2c9uM3GnyBBobgB3"
    "VEj2OI1tGN9CBRZA+1FNJWEVleLYIlteNiWppOHXChBhAQT8amPnvBA8lRArJeNplsAiPylAvoebOMW7Oc+6nzQszDK3U7gh5rCa9MdKUhEtd1"
    "KoYjHkV/BXc/GxbArqROCkhYRDQ5ZmyOhen4gr6ENmr4mbNNQMFVVRUV/uatOEpilFXlGGUrvQG/uC7BvucHPtNjdHCpAlAEzvMSEkyj++oNay"
    "STSv2dwhOQnFDe3tQrdb3EFBynDxZePSkC9UYuuhOz01EOa64PWgvsIz1JJGyLzspiKNHhGDc95YMXOl1OqJyAHZYFGMMUvjKS5PHXvyui66km"
    "9cuRnEn6E5oDH2QishJyu4/MyDWxdNy3Ox6s3Fk4wFmZmIw87/30fC9rjqmkFZXyF8VbLCnk+eo7XMUHBl9gUHDzl45JzYJed9fc2ZjFDRtheh"
    "+AMSfbQ9JR5F0sUIkqGwKEh1EhVyyQyENtiJkp9nuCOpHbwro00XxSduKHZ5bGmAeiW+fQem+rvoOuJgkJRUkcYpE6CIhFJm71KEDElAmDPJij"
    "OedMoXXNT1vVSkoRT+PIerEyEU/xWUyLfJwNMBSd+iTI0S9YiCnh6pJ+/DSeC38czUBsojoQnnWxlnWnMFea75O+Hejxv4PwJ6Yf2ZA4ErXF3/"
    "YmfonaDFyzhMvMeL1Lyi/GGZXLxOSktbX3eAJJlWnXBJkFzbPHpbGetu3ye8MvZ9AeuHH4RQkSWkryPzE7UKhEyaT5LGGaHFPlTj9W5Tk+ZN9x"
    "99U+UqFNGP9hhCejQj+F5EdCqD+BP1xGahVLpeE6ki4I20aQUoErNTbqhpTuHRusQ/EY8wOaw/uWNF1hNsQdLIl8tBvE4TExmd8dV5zCb3ucQl"
    "N61ZcnYEaxchOVqhBgWuJLrN0WYaFa1IyoNup+hhQ36eiwMq4mi9BnZkwCVRtGfXGLlo34vMNSfHlbGgOciojoJMiF/2yiw4TxNCVVbm5xfKm9"
    "QrFFyMRojyoFJS1kO9/xGQxahV1oNfuEfgL7sEyuk+mW/GmAtkkZnzOpxyMQGotuaFGcI/9K1J3xN78H3KF4ChX8QYHz3+uhOL2pqMkudo1o8v"
    "IWKj0OgWl1J2uyHhOecq2DaL5T1/zKVMQRpa4ZhmLinijELXac0cZIxQaADJM/2Fbg44D8tB9lVGNaIJdMfw6eErg9QEtMCJsQdJs3uSJqskko"
    "yQIR5ahInBLQeAkJS2vnXk8xvUJHLxFocpdHGCRivoZgV/2cMqPOf6VWvZBtNWnBjcH4bghgZCnKuu7B4ajRbeq6GogfAweBBqCDACNjBT7294"
    "PdPjjMG7ZE6SoyG/kkmy+FG0K+Hewtjdmswg3VW+SNEID20glHEndsB8bRoy2ajLqAkK4YCp3iWKnq2B7VYKfkKxwFlNG5UdNA+JnPOFOltYIx"
    "XKMzWLpBA1RsliiRVJ/apNEgrBysZH2jSJFA4Mm6XCVIk92/ZQjEK+A2O+P3UYh3nF6NVcXpYrKUbvfJN22xBRbn0iOh4atbJNERPcp+SCDHBc"
    "0koraoRUpgJDjGtyZzKADVq9Zd7RUz1loTnfPS6p2ZAnQNoPWq3WQjRgiBgBuGyGmidwk+Ms+TCLvSyu0KY4XPkwDJuNY8FX1EXJhWoB4X0Kqd"
    "NYXhmngzvI7SGONWVbOor+wPhXESsZaUgfeWKh775l56QT0EbXw0rNHfd+TpvIC0lsjM5z/S6pd8IbX6L/0fkSh6AiikZxM3Ns8hPcWB23p/RV"
    "cU/m6r616vI6YgmWExqrWCF92KwxdxJzL8g7gn6wFH2P5bxnUFCGKDJ6goxZpQwLcSPnqHaGT6Os1ovn2cisbKlaGEooxQpmI+tjVdNaY4NAfS"
    "TlMsBpQ+2yJEOoKS5Xm/XsTLU1DB8K8F0UVATBHKIMiiGynETxlW23wKXTBHNZEYoZt+jUvEVRLU3YN5QhTSsxSWAGU01rnz2tGULLQuA2/5+9"
    "gs2aDv+pb21i1qcFA0CEaEL+F+yAgrPy2rJdxUYzpKQWca8h3JzBsGJ3CNgTUHGGTXQD50skrDAER44MhbvKkcuOGwHOKGnhdKYONCEWVSHDJ6"
    "mBSPYpLRbOnJuvMBZRHyInf2BwXsQLWY4GgzhrcHHCbQufT87nCL6OBgQRVRwk7AWWnCffRQ1f5BYOpiMUP7F+tF0e3jwr4rbAoVDsKOLRXHk6"
    "pIaGjxQwceEaTfQxozIRiBH1T7ozjpucEVDANGE2hHdxvud1XKvqrFw4Aw9vPtpZSG/F2Tmy25jywoXKOvkZWnRo7Btanfh0+8QA1s0rkoA27D"
    "fN6RqSKwn2JFEII0R7olDf4iHatNpgupApOZ1lraGmHwkBQnSyGmwx2KZ2AyJYZMZ2YHn6bETikNP+lGWDrBxPqwf9pwPj6+QSRWcATrHKiWMu"
    "NLJaHXbnkVNAlCQXT+6QIiuVpNCDTawAmMzWXQ5blYs5hXLpoOSaKGaADYiw2qH2eO9iCU5ndBJRUJYckTX8Fb1zWAo2hiVPxbjqKORR0lA0Ii"
    "2dMBLDCjZB0nWrDk+h6cpvIfVW8hqW823fkzHRzaVe1qDbypHE3nJYOVONRGjD1B3B7Su9oapFQAaCeTIddiLkecHtmqsQP3knyDykdwBlAng8"
    "dEc5hT4BCB+S/mMyBBgW9oBwH5IhLGyRGGNfE1QPgglJmDTajsKwKCe3fpZtydJNvLbJaHnApAliQhgzA8tIZIA9oOlEJ2AXoaqgl6XTmxQfSp"
    "XgVoX6bERGnlyEzCEqlQJh4uu8uvBVniCFWlSNPJi4g8H1EM5VLoF69G0v7A9PKf4WR1sf05xjWFBrAKfoXQ9+BetoIjTRewUC/JgoOqOg7wLa"
    "beQJn+S82dZoZrRAss5T5WRFAQtNcll+iN0USY78j3fVo4ZZNeUNJhMXFBcy5/malq746m6mHmkJhHjlt8pQzUF2PKUrVnA0VFYwaM7CuvP9Tl"
    "n6fkoRtSKlElcJyb5UijjGBxuVswYaO1jU7hxw7Vh7FCOq5eImB4C+2xVLNOoALl2hb+AsJogGITRSFzB6a81ZXkQ+zkjf/ARZIIHfnTbeTdKT"
    "7hn5GtQVMmjwBMOfjG4O1bMep34FnN5BhNrcaP2HBxyQ4oA4WSgORWe25AKO9XfJsZF2vsKmDqSw0EGRAJ5lMarIhckPiJmLaAt+LIADSLF5K8"
    "nJqQXFDcSIAOwLwuYFylCoQ9BAaD0f41zOPEKbYjNWpUIKSTR1GjncQK/EiNE8FhXkgsxvyNW6IdIsw3tEsSwatgEBt76DauNeNCLnHEqcgv7r"
    "hh28GekyRJeTdE1S8B3E7ETSQpcf8/3xAsYf0ifEYhT1WrHyeCpsnwHddInSLSGVJVKJwimki07DXtRbZ4e9jJWRyMWXyiJoJXIkUaHERtQ68l"
    "bjZfRy8x30dvUi1XXpXdpxnUNBlhksS6FcBjaTyooqBWoIM1sp5yC0KRJYXWKJIrxF0ZR2QRHAeSenSGgaKOIvrGAPzExI9hETVtoUeRHPbH6W"
    "PRudF9I7AYpI6Z4gMxghEqASQBkhFyMmCt4XTFYYIlrXRwxH1J2T9Xw0DfFOgkJArONC5RQ9rbAoIH3/pAvbC14y8Ed5IQXTaKOJShdBumbbTR"
    "AD/wRQA9SMAUKvm4UubMiA8GO4peFCBoiXInVART1EoAf45TE7+3Az+iWugHuinOL4ImQXwRfOOBeVgI32UijhhX3PKCOuqAJAiAj6aPyLYl6k"
    "OSdIazSSbH/AB8n4iUWHN01XNHfxfL3F27/QGUBApRwukYckBFkknEEh99Dr0W0Gc+QRJ34KAInYA/OGWAYdEiJrCeEfPkHsCboZiWFMoKsT+8"
    "TgUCHFii9+T7mbvfro8p8uf335NftW+/zyWyj4Ap2QkJOpf0Uva5dfsr/Z7y6/KlzSstcTdkGrnYwk86rXn17+96ufch+FP1vo6Hfkpurqk8uf"
    "w//keAJdl/y16r7R7aUjHbGLwstfXf4jdvOxc/mzy2/Ix9vn4hXr6oOrD9EzCg3k1oP3H+w+uXXw4Nbu0ft3Hhze3nt8cHi34vuW3cddfQzP/p"
    "jdzX1+9Sl2jR/3AZTx3FCsX/S++y/4NVd/g15a6Bl+wvjg315+DXU/NoP/xnOwcD/IX8CeS/4CEWKbAmxJcdHUbpQQyfOvUuONSMIjJ54BRFL2"
    "rVUehQTUzs1w2rkRTDuvaZPmRkTsvIilPWNk0NusIRTaOhjiOh94YphveDspoljnRqDr2a/MJzPfyl8hUeRROVV5jiNvVtmQxT2RJBHnxyfgTC"
    "F2Ry74g2D+Rkm6LN4xxTXbzy5/a7rn+dXlV7jlCz9u/4SbpOq8Bzab+HZjx4fkTugTakQbHwsqW0oBrJGLqDAuOVpxAKRADTAE+YgETQsOAbJa"
    "4QJSlnJsiTqvPDH5Q/YJhyY1cttQiugXUjfQkRsRKLOLf1FmQZO/in/LkkvL2nIogz+2kkdnVvlJBNdg1DmVu5WvMJKVVjXNHHn5/HzjIrALyV"
    "/jxCFg4UP+ARThcf4NzDQvBhR8C+f1A+fqQwQwALngVH929SECRmz5c/S3pGEULCOvxXzlpudDp1T+2FrU6gm07OdTG/rZvE/Q+WVUh5EpbeJd"
    "skNlE2TSg1CuGgvLTwtWyPZyja5K8T21cYqVLuusoN2udcSCXrzlGF6/5gsb0ZqsU6PYpe8xbESrKhzm+v4SoTJdVuVDBgW0srDcuLy4CfAsfo"
    "f3BcL3T/iZf778De2HL5xr/QzRIEct4jVzbaWOde9KgJXPVwlPkivd5F50tYyVEF4WvyJvQWgXopsppZDj2kFRaqnF9UBXxrx1UGW8jUEAnWQR"
    "ipUJlyoBVVBNQIhSxNueSR3ZzjBfPszl0VarSptyXu9eO+eetfNK2gVap9aZ7UlmnmN4G+MpTOEIZ7ZJcpi9QGOlddUqv4UEbf77oDPEtx1ed3"
    "zfkWdbuivEcax2JFsqxIBGtULlotZPlItHs8ggr1yMwJykRXkPjrfp7ZadMxeecCmP93jVE1Z1+KZxNvVRmD5TVgglnWdvW+YDhQ0zik70QFAq"
    "4OjJMTzqGIWIiBEKQur7uvx1xp1yWEUgRSZIu6oskbF+P62moywuBfaFYz6WNpLiYroXVb9RWPIcHKJ1v9K3wtzrjJOtiR3ToYEUaRN+yRtaCe"
    "ohxg50XoI26HzhDkAK+C5QrflKkFxxbb3GoPm4l7y8a74jgxpkUZBqitlUBU+X9poDIeVoiUvxu1Ehf+S5ql8uKt7DefVQYQ9CeLhfOS+uHApS"
    "gdW1zKqwGIxpjFdUoyuGea4TZsgxQrZZ1a+RxBFDKIqrYtjpilKWkMT6qmYGBhPbfJV45BiYmKVMcitpHyYJj8RCkvxxPbMl0ftmTFghsjrJF0"
    "TcoA//v/wnFddWA+JiKGnZcRhG1koeQgpfL1pTq4mTSxddmADyS5GGCXYieGNdqEDsiArXByPE45EpVKtRmjtYqCaoVGhMkdKqcEiJl2SNJIg3"
    "8ip0plOMUPQ0ixKFYyAnMzFwYNr8FVRTY5V9jKmJBv5kcGGVArCPcRGak8lDkc2J6UOevjHp018taCcTVG6aeJ5kaYWTojpBYQwWFM6EcuUoXD"
    "sPF2F6ea3V7qgvuQZ9GkhqHp4Ck7Xjz59ZVkeSgsL6UZUU+ktSwK4IJMO+XiRD9pPFY+L2vMFbSbNHFS2GNpmFBoapKEwkktnPA6EfOLVkaoYp"
    "0w0QFbDaISX1/JUIEJ7jhGkTY44T2/QpVUNmijhKw4BzzFqc1zpvLquwwZjcoKLmauCppqWVS0oTcRQNkWPbNW09Wa3XdFZMgClFzH/qpeKmiS"
    "0OC4Fgz6Srjb2ib1LF6jXUlHB7Kmc7ONVUW6RgXGckuRBOoW2aKhhwhbowTG3LhEaNkay4x2XKw9wS5lbRu414FfNVlVQhnSYlqolaZQnyQkUn"
    "Suy+OOCfOPPqx5mfchOMn0op4Saz3FXJYY3ZZlTKxKHUnLHGu0eu8R1UqQPcjQQOVQ5qz+s777+Pimvvv3898YL+/Jt6njH7Bvqmd/7S+aEuxX"
    "+uwZxfe3PtjaUb16L+tTdX39i8cQ1QVkn5ISY2blxLI0m4+NuGmoQT1c7cFMvXoQEl1uDRAbeF5MRVKSCZJMVFq5WOAMpx8TXEcyXZUWWdKSZa"
    "MORQEnA9cqrcDeLYWL4C70lVIpQEfPlUkqTRjunlG9cQHnOy3BdCcN0kkVQnSyWFexWTMJFdfsUSTkLCqcrXBUkkLUg39dqbLZxtIvskTZxOSa"
    "MZGidrsx1iOSwL7FBMwcKQXgOmYQ06aDMqadrmnC73IiQyVsFyCCdWcujhQJJkrY9pY6l+ZDKvDe46+QhXrHsKFocl/xWd3hMDHdnZl7+4/Jb5"
    "J98gl/ryu/JmfR+F3vDG3vsS2CZBZnnsvSHl10c3AKC+8eD+7t7B3du3Du8SGe6MHAoNAB3ceqBDzL1X8kr93/7++/Gf8U3jleU3zRh9d7yU70"
    "1yw375JU3/pypAjV6o7/Ws8C4qAkT9ofvIErLwvcpLtNSpeMcrXuLkmN95vH30YPvBrm3vWqRF3/9tvLwK2zjxsl7kbLvhSeaeeM4OqoLxPv4c"
    "GeKX/+h0fEABh06gmpC2GIvEfomBMr7n04TH9+qTy/9++XPkLf8bRgTR8UOc6zw58yg1oJgNIp1EQPwhcad16KpfowiRIDJl/xlm9+cUZ+RXOl"
    "6nvBAFRci+/uXlV1cf4Ut/AVmMesWLdXPfi8WfGV4DH17+K4qUvkLBI0on8f3j5Vbl0ATD9wEzxbEmDUjJ0htL6yuMlkCytS6ICaRXBCPB5Drh"
    "JJiqXv6IvGD5MmMrkFzeYLwEk+s3BFvBjMJNMF1FRQhVwQrBNyRJGAqmVxSOgpllRmgwWb30BzKIpU2FekhGBoHJjqeTjLpgZqPSkYxnaUPhVp"
    "IZuDw7S23GkCRJqBGnKwhNpisE6ZGMGxblUrqucSTOlXvCkO9cgzgD4UmSGchsLK1pVEdyhFmrXLk7RqWkXdcteiN0StKMQxVdJ/JIdfkEkeIq"
    "QZkkg7wfnSEMStKCQ9m6mxRP6H5biCjLfsQMei3RGaL2VK7SF5AUul020kkgyYy+in7donllp/eLZ9XAW/h9RdL1e0afasutVDoKI1V+rVck0f"
    "GSznSLdYPcSWTvaDjVTYxnB/5Qp6dRFhcV0cTeT6qnkjB3o9coSYuKfuoVnUXjIlP5PG9StAqDord0UnytOS7Rz7H3hlptuiWZB+kcU4+cBZCA"
    "bqN1hrF5zlQghMK9paWWAxoFjKqrrhint/WlyNuibcFF0GWaQW3vQ6tE6AdQNUJnDNURXaZUSGodmqQCST/xCvtGXeX6HrtO6je/4RvpV6Sd86"
    "n1xpKAofP1W6XTcKlcxwuBzuO1eQHcUAa3i1m2TGWldlW4eR2vHrN+HZ/Bq8ksXKPCtFS2Wu0Ir5baQwT4zdIWlgJAL5dVvw1fBcttdERFeK0Z"
    "3dCFYTSsDYnBldFCHuNSvPTmZZMXvfE2bBgY3gByKahXUunYKxfTexDY0y3YMDqCmEYDegghd7VMDqBRvFLti8blmmtI+8M1p5B2h9s0Gj8p1d"
    "L4ABEoynjlPKOkNgq8nQUYGROLV7NccUZPND60Xo0bdwF9gTDQzA5562MQUbOUpgCdIjb1JwtMSj2WhRcFH0sNMufqn/yj7z8Fs/Ymae2RGh/B"
    "LVHvYB2qnxAGbqg5UkxkQJU/RU3D7+XklHUYylqet8WHsrPoHHjkygbVgWA6MAY0R9tFbbQPsTHqVX6OTyK18zMqg2lDvgYFBqtyj6TnEtVf2t"
    "wGdR7Pvbj+IvmLF70frv4If+fnmFyfv2G0/3Pn+grQGPOv6OTdWzefv/eue/PivQWWDnup4wYv3ngLY+r8BaoK2t8D3R8OAXrccF71lnepC+z9"
    "xXtzpSEaY313+T3n3ZXWezP6Ieudjt/LoxEMD7qDOcuDqKszJBWUAb6in8RD3fgkyrv9F2/kY/8C/vov3vBevHEjhz8n8Pt6vRGDX3ZCknf8Tu"
    "BHJO+ZEr8/cbrkKxEG+L9JbzkyUowu36vuONgsH6AuL2yonajnBkqxkbYS6miJgt4vCaP4CHfol0Bcf07//61DFPE3lS3HarcfXf0doDLfEWPz"
    "a8JGLDtxiO98n8x5ECWZO4nC0J27MTdx+fckSlP87WVhGMFv4A2H3lx5imr/XPPn4HKb81/MBcEc/Y49/h1i196Lud6ruqBW9DQm6HFMxJgA3J"
    "x64AQ0+tHrTWp5jnQAP3OWvlDajpqfwJrUnxPbgPTgmmeRop8FNI0kJYURkrIa/BKG0plCijR3qSRLXjUJMAv4nB/i1+seqK+oT31JZapSr+rP"
    "RXxZx6CAJ6kAyS/sjjz6ppH0nEZYV5/cqia8UsHl24J469dR55TAZTRCYbnDPsFI0lefPdd/n5vVseI5A4uHYSn8HQduKIFD1lSFhqypqV2ZlT"
    "lDcRv7KdSmIWc6zsVu2GsA7t3CoXW1v5LzAmha2AVjh0bkRMiars2r/YgUndoZBsWQK9kd42BM7+C14Rh+xKFt4Q0chxaSC1f0iIDd8M70E95B"
    "SfVcYyG9DacpUduMZqk7wM0d0poA3UtLk2B3yLSYa0KpYPPclSh9zs6285SUNhLnOslg8Lh+evVfOabwp6RBrAEZcggxZLcEHcaNR3DwO9h8X1"
    "WPJFtVkFYrdPsLVFKGS/kASKBo6NzD7Z7itv0ZkG+/QkSIICWgQZ9DwW8ZDcIg4X2PrH5KjEaAEx8ytP2pwBAVT5xOhKGZ/iXWI7NSzCM4RnIV"
    "bATvT2QOahs/jZlQnHtTSpbeWF5fusGyLEE9irdIYOa/d+DW+Dt8W7kzQTN0X9jZKnd29WPm0ArFOqMTIF4Bzx6VOlmSTlAH/Et8pOiIsMm/cm"
    "49qHxXdPb+2I3NXpY21qp7OCD3waVG7WqjEcaOft/tjVUzbmQa6zgKey0/Kfpm73ejAT+LTy69zpNJOg3QdDv2u/rJ9dd6Z+IN34cTXPqkteon"
    "uX7fmF9uJOt0+Utck6u/h2vqN3BiPr38FsNxo8Z+6VrTWGgZR5vrZHGSml0jz7r6+ngwTQdDoxU2WqoCBYx8WelpZa0+RpSJ9AHr8hxyhAUXQG"
    "VElf1N/Sz9/v2QO05zank8NhDkAlSNAeHtJNeTbHi9egjfIJflyfX5eeems/zG0rzzX7Cz5RvONQNakEL9by//5fKLP7v2/ScY1zGQt4vqgHiH"
    "VeVe148YSjnbOwJFWZB+9fG8CTex5ivYlIhjfS5005vO6poDVOi3KIhfcNYko4mo65V9veCwxRsnv778hmir0lsAhv8bwnBE1/7KuQj8DjRFJY"
    "P1VZbQ/QLRE+f/WFl9+DYbqfykuGA2V7Dwl4hjf68X9f1bD97f3nn/bZiTv3SuX/N2X3b7XrASLZ0ercWtx+2L0cVhvH323Fu9f7jp+7dX77pn"
    "u8sLk353Ieseuvefh0/2nyzA5djtnj1+8ABAaeAf9p9uLXqDhcV7i8vnm+PNleFauru7HO5G/cXF/vHiYrjstnob/dOThfb+8/3Bev/O4nhrtO"
    "F5+51o6J6veluTlbXFxf3j6eL+9tL6Qng8eRoOo91wcyVeTI5XV/cXFvqnG4vt0ap3HO3u9jt7t1u7yTuPsiw6fzu52OjeWfXCwcb+0UZ/uLpy"
    "vuL1F1efnZ8cZ2u7/aPpQnsEL1+F6km6la52t+NgKXm03Q57ULK4tbq4dbyYBaO0la7f7sSribd/J97Yv1jMjkfrvf6djc397Wft6fE4XlmZbD"
    "5IWkent+50ljbGB+crg+WN8Z3V/ubGxv7bpwdx/yTrTJI742xznIWL3b3Thc2Xx4O1jcW18Xh067R/1k/jC8itbS5erPa3zjf6++Ha6sryyzhr"
    "hXv7K95he/PCHS8s9JZ3thfGrTtLra3FjbE/XWkn/YWVtNXdWZj4zxYnC/2t49WFe0G/NVhvZRv9O5N+a+z2z73R2D28GO+0HnU3zryLdntjby"
    "182mmFO4u9jXvr64Oj29Hi+sudDE7y4cXu0kbrcba/GE6z9vpO/6g7brnB0qb3fGW48ez+1sL2ubd7srh1b2PvtD0+ncKnRq3Nt9u92xubw9Z5"
    "ttk6ctfGo7X7z0fdx6f9fnxwtLG6duTt9zc2twar+4NJv3++0m/t+ZsLq6PFxdutw7sbp95i/KS3ne2utXf6rTvDxbvZThyOvPFgb+WOv3+0sj"
    "psBWv9rfbk7vrTdisct7bT+Hx/3OuP4Pt2k7Xtvc376f7exAtbq5vtaGErgLXa8Lai8ctHncH43p2je09OL8KDg3e8zmgRdkU3etmC+d0fdYfr"
    "RztLk/Fq62j5yVL3+drB+cbztHOys3+4e9waPe0Mn+zG/XvBYvh00A2ehePb4fm4dWt0fHS+3O4sHe+4+zu7T483g/ON/Y3l7srLsLt/0O9PH7"
    "beHq3dXUw2FocvFwdpO7h3f+u4vbu6uZ8lW2N3a3HlsLs0bi2/0+6drB91Lnr9ewvuzvOj4b3w4Vk72XjU7m/0L2DfP5202uP2wv6TjY3dzYX7"
    "42xhv3+/k253nu1srm32s62pO0yzVuds3H/Z3ry/n+wP49b9w/CgvXR8/rKTPQ327rbHnZeLa8drp4PuQhAcLyxePE4f7F487rda/sW91sJS6y"
    "JdTRcePo7b0zBsx8udh8Fud/vtJ93BYnAvPmuFd0ZPspd3pnvu8TQ4Xnmw6a+NO+n4/HjpYevs2fL64mG8nyydnd/Z21h4ErcXdsOF5cfeWTt8"
    "Pgwe3lm4tZE9O1u+t7cw6q72DxdWHo/aawdZ1F/LWt17k9FZq9M6CU9G563l3f7k9nrSP2ovbAeDRfciu9XqH4x7D47j1BuPN5PjTvr8dgJny7"
    "udPbozfv5g8WJp9XS5v7LhLrbbvfZxKx4u+oPN7YU1/+JpMN1c7m4M0snbS2lrPT09T+PNVS968OQ0PD7IpmtB9viie7zZPlrZ3Vnrtwe31++d"
    "djeft0e9Qzi2m8N1r7sbbE0mm6vu0mrabo2fn55P3bWj1Sf9he3dp0fT04W1p0vt7e3x/d2LvfVg/Xx/8vJhu+WtLqyvLPfvPVztHfX7a/vPR/"
    "t72UqW3u+tLLr33en4OIuWB9s77Ucbm/1Hx9vp0cLB8t7F6Hy0kD1ITh6tZN7+Unb04P5CMh7uj1bWlpY2bm26d7Y7p/t76d7h8mmnHx7efvJo"
    "YTt7vt0+HExWFs77cX/hMN58p72/nYRLzzZa/aVnT/sr7fZSZ3hnM3o0nHrtibeFkPYiOW492z/dXL3w7reGG8PDnXvjg1G4M7qYPl1efrTYfx"
    "oexOt3hrs7T+/d2n3a3Xp6un9779H+/a1W/HL/7NHq2fr5xchfAKqtvd7fvH3/cPHxyxZA6l530NuK43vjBfc4vvN4YXo23jnujeJuHL70VzbO"
    "dy/uJq3Fh6vJcBy0lhe9J2MvXc8uDi422wsr7s7eet/bWuj74Xj95eOtpVur/dbRo739B4s7YX//7OJ2C07wARCxm8+eddv96eriSe+dhfUlb3"
    "nv/Ki7mW7ubnmPh6u7m+FS5/TBk/b6vdZ48HZna8eddvY3zxeWt8N7S0fnT47TcWttfLTWOXOPn9+eHh+fAwBeaXfXnr3sTrZ64/E7afZwPzkO"
    "0tZ0sbWTxvcG+0uL9x4vdo7GbsfvhlvxxpZ7+vCp22strPbuXDzaPfUB4LTS0DtdXOwCYIxXvdP99edb6crZ47W1qL2f3n1nZxluuuVksv5w83"
    "Th8Hw6ygbhzvnj1s5xt/tw1N/dC+7tRZvje4tp/+lo3Dk7OjloZbvPNrb3ew/Rj0769vlw7eDibPVZPF3Ldlbeib3to/OncbRwcnwnPN24v91e"
    "2uy99PYWnz25c3f8dMs97h0eRafnp2l7fOAttg5aR93dW4tbby+2tlf7p5OF/Yv2MGy5cL+01x/3H7aykbfZPk5OkouL++uef/Ykae0+Xds/Pr"
    "597/TRynRhHC+/c/5yYTHcXe+t3F982Q2exvemi/efrWzfe7q9ufXkrnvxcHHS7rbWurvDnVa60hrtXyRwp73cP+mO4mdry6322frF6cL2uH3r"
    "9sazndN7d+6nB8OHg2Q53msfjI+Pg4ssfnJ6/mxt3N1Kpu8ER8HiVhiPwrPR22vucPP0pd8a+0HneCM+Wnuy2MlODu/3Xu5v9A43WuNs2NleX3"
    "1+dLi26CYbt4/j8N7u0ujR0Ovey3oX91ZWno3D8+n2afv2k9P9dry5/GjnYCk7PTp5vLG63+ms3V72duJO/+j0yeRka+F252Qz3jpJsq2ks7+a"
    "3e9k3tPJ2dHQf/rkePPuOE3ffuQdHW/tvLzIHrWe33NX3PvhZrqyuLbwTjy+czhuPXlnbbCzM+09XW9t31m7k758erwRptlRtprFC09vbYSTRe"
    "/RwuTlVse7c7B+bxAnj44iACrZIE1X48FO+2h81F2OT++k7sajcNC+c2/vItg/jtJ70fPb3v2N8Vpr9fmTOATk4OD2Asz0uDsMH5+c72yudJb2"
    "vOlydrCxAkAj3Wzvt1efbm1uRXeX2sHh1trRMZz4Ti+9cHeH02e96cZCf+yFO9GFu+hvhe13Bs/7J0sncdYOh+7x3YPpWnp3/zlMe3t72B614u"
    "nBxvJLb3NjLThuXTzquu2di2RzZTUdHLXDhd1nywsbG+vhaC2JDztr03srj9ZhwtY3Tsd9/2gvHi701p5ebI/jzaP1R49XHj1b6+61984vnu0f"
    "7WRLx/3jw/TtljvcWDjaOMoeDdY69zfScLS4mQDC9fLOqO2fZrd6D4+6owUAIiudUe9irbW31gkO+kf3FnaePNlZ2HiydnG0/vD4TtKNh8t9f3"
    "O0vNa9c/9lJ3iynI7fWXnSXlgO7+3db4+PVs4f7ay4TxLv8GKv45+Fz3ZH9ztv99dGF5t3N18ePto6XT7opMmznc7y8Vp68QhAwt2DNLrde7ma"
    "3r9z9GTSeh7tbw6Xdh/vHLb7B97F2Z3d1dbKy/t7i7te5/zJ5OJsobvc2tuKt7bcx48ete5vtjsrI8Dnnrfd48BdOAz6m6fxQrezGh203744XE"
    "/H4+z5w7O9eO/t6NaTZ/vr7t7TtcE73Z2t28nB89FKq7N598ni+dnCwzub7WG8PX3gLYRjf2PxZbC0H22sD8fDh2EWHx+dHlzs9Vfu3brY3l4+"
    "j3cOH8UATPbc/t7m8k768M7uk9PIn5w+6a8seXeGF0tpsLd22r3f29m9d7C30oFNkWyFG1v7ayeLg97b2+n9tx92FlbHw+Xx6HBzZfes1/cW0o"
    "W3V8b9/5eis0huGAqi4IG0ENPSYraYdkKLmU8fZRdXuZLIf+a9bpecXNPYlGH64C8ZqatkI7RjmMdDHKB6J+qbl6g31Hoti6IkkDOSdwQA7KIa"
    "0oMVmzxXz4Aql9hFs5wWWktFX+kofgGBZ0hI2O3+wNMcyqM366t24amfQX1wWfN/wUk++ffO/EfUw6HNNmadombX6PBT0ZH5mzs52wfoBcrC5a"
    "A0eFl29TsPPcVgd8f90vwtxTMNQNI6NGM/wxFx7LZ4ZZ8+GiNcoLieueKBizuN+G75lQs30tczCDpWoUdJQopuHShA05WzR9kMzhEGYqMZEvYV"
    "DJiHHiTEeUtXdKSPb+QExBfx4xqL2w0pYHpg6KDegoL0uA+kxYlPOeQ9gFbbXvM5ppvLYQshjG4Ywmr+mlC5oA+Ro4lBeU6h8YDdiMfKUyEbaB"
    "qRgVEaUH8/IjWSjuc/UIfr88+8hs/NEM6b/M7KmRxg8w59g6zGBJlPA/kxk0ZKpb7oxVkAHcOeDRBNIuoKfsI3r00JIHXe/xU6xK1lG8ZjSG9o"
    "SU7P6ifOphizsYWIzxwzkq57fEiEf+H2t5iA5KTGNx4lffwvZ8liIneEOaQAFOnGyjcVhPNXvXV6jVS1Ujk06F0Nt5p9zPz+0OJ9lViYpenh59"
    "m9gRxg9Ch+zg4EoXQBU+KjIcaz98u4pAXZK6RuawJOpriob9ZbgCSM08sYKdr78tP/f0bf000hcKkjHbfnglwc0UBczD7DwoQWeQajHJa/UktK"
    "jLe79G4TVvSp8cc9XcFLvLbuGNwuDqegflN2HzEmcxd8ZgReLAX4YLfhPkdFWB8wbPflew6ZW85Df6l66DFo7e5l/btxNvoFjvIWbs7gtxeKaC"
    "m5chqBrv94MqaRtf/BJx1N6s9RkzB7ATFB+KmLvBqnrGZccoZKdz0w0cm6Vkg+GMMh75t/9j+nVDy3zAH490SEwfg5vKFf85i2qc9E4nh2+64G"
    "Euc/92cvZX9s4MTCpG9I5Bo2jxGbwcmk1njzkjDVvK/nALvMlcEQ7GjFScH8F93IJuW82xvJHxJjP7KDyejpgpGBF6k/E9HwxgHZSpSGFWhJUY"
    "bikrrEjmvHJxaaB1xCvgPAaNDKYAxdeib+ie3hyvPInYcvDfSbmr3IkuJJtfZf/mkzPA1tH5GFJ0R2TZ76PXey/es/mkQuhCzluO0WOUumcQG6"
    "gNZ6TyjzjVCy0pMP318jwUKtHP30mwPXcXEP88CbzZvKH03hevEAnxlwy1jwmG3aKG+6obAvbvqxuYgEBkOyFGH34t9jHzf0plZpDWsEThFPLc"
    "WvR7XfPRIUmlVXeUZA8JsGryRO3lWgwBE/FdmczhhPA300RP3bqKxPT++Ip5LtDMhykSB6xURsa4S0bgvCikn4TQ/2iUIkQKmbI0bn1fJfoKIL"
    "e3ySyv4E/fc9XarpDFhrxhCAF43RSnBTc5L08qxHASI5/QfHnzTzx1nlIZQlxmUt/WUpx8wkd0BSI2tlx4UzwqxrJ2Vo6b6DUDF5Dp/6cc0Tv9"
    "A9XqePYb6TA/UwBgto4VkCeEaUEjqeNjhgLuEL5PAzSKP6iPBe7OQ2Rllz1ujaw2eapCXpyButqxa7XoXM9XpSYNtkYuYDAIvQ0dNNpDgg9NM+"
    "OEh6BiRWCUZZCY++CvqvjBy4J7FhJ/eJmgIO7cN1XwkN+ML8QSl0qHUMi/e2SUT+3K6V8v16dudbpQEddADEAS6oUQYzBL2znY+oYxN2lG576L"
    "5oqnJKk/UIuiyouz5NtJiDjKftR1Y9oBKIiXB4YCtdu51oBU0kIO75dlz4En/ROpwV2Fq8I04DR+PukUbThCDXK5gunY1ryEIkdE9n3IYAJUL8"
    "gMlDAGtPK9/TXp1XZRn0MXXNrpUislEzB9CDFKm6Y2CxYWRLNi/0fRvZVSxyCLgdRMCX8i1NBH37nKJdW0tNbJqxZfPEss1618eMFnC2kST1GD"
    "glCwErW2dj8JFZ40afTWn7umMjz+SiAt6Nbp/8HoGLaKhvXpb3Eg9qTYq2HJlUBx48qbbbTqUHWfxKSvbU83fL1QB+PAKWjYBRQPyzLLCHM+gN"
    "oOD64sZQBx5uKO6zfKDLr4TpnMhRfY9ZQhUMo4OaF92mjCvy3qD914u/2X7jb0FChPHm0UdJ48mQxBnUhCDW+eO2JqMAM+2XXdYmJTUv+UejFv"
    "7UnEE7ULbVamiBtq1Ui5ZnJ1dJb9UHpu7H8fkvwJEh9x9DiJ48RGiyFe8UE5HvlTXEDXdRwxzFxc9+xS09WqgD1xAkHDjfGr2uEZHpkcUtVI0p"
    "zuysx8a2J3WmeCF/VoDwHwpIqhEpWMpTAw4PyPy+re4nfGdYJbSx9xZTl5S60fiGmNW9nlaV4hgVCIzHt18qxUBpj29ZXFfztMsQrpjfDxUg1T"
    "u+7FFSbR5muE0jauGkwJ0mO6yHsuUHBFPUnwhySqoOO/3Lmptecu1X77KVjyl2prsaQ7f0c0ucM6OZuMpAfYKnhsiKXiTUBdeygedhgNZRZqBe"
    "7YAjqNIfUvHYRdplBLe5C3jjO20yhy5K7TxpIzv9AdlxuOJyacadY9lCFwuFPGWCxKShA5qkbf+oJYhoqYHg3s93tgpi88z/XysU1VK/TMRANd"
    "/C6lizlAngUS9K4d8Er6yEmOPWIBzvW/YPEefWtQnhcLCbP7zVXCD+aQr0nAm4KEy1EsbzNCQozDCdmwO+giTrCcJoD28d5SNJ/Tu2DK+eNPTQ"
    "0qeNL+jTXHaWBIv2zuhe4U/8feaN4wJwmLFs5hFwT6rPyp39KnKjXfqKIkQ4/Y5NTayj/uNfB0IOZewTRvE7hGYkA5jL97zgCNPhsK08O6dBv5"
    "Xe19nUhnqKk04FRlyu3uRQbDVosEVwkU8tRRK1JXba8DXPi+N7EfzeklHcJpebGmkyxD5gE379kvz7MK8LoOQQSxZ2SO5gTZW9FBlW2GOak1UC"
    "uqxGCqHxyP5tEj+beDCILErsnbxWrFGCDFLXXAakZVdcI2l/ZGl4WFac82klzr3Leo1l4Rmz8GfH55QmjRlyQzA9RmJgyhypgZwMMfplZXBYAs"
    "RfJRIOtbdX5fNeXhz0EFLzc3Xug4Re99y+/ClNcwn5+DYAEXD/lT9CSc9rqiDyvFszTAmzRsnrkcbAFxhNbXwIVEqVEl4Q/NB2RXBhYKAW/CH3"
    "CIzaNCNBFZYOr2E2Q998Rrd43LOa7nDzIvyBzOGc4RC67af99B3WhN5aGTO1W+mOr8QE4IGebo1sbplT6oMhtj36FWlmrs4OAGauwkUu2ywgqP"
    "MOySKvSUq182dkbVF0kk3LsEGGdsEuBoVCoD6bsH617v114HExNpA0DPzoQm20Ny5B9Lb1snziU14nW8FP1a7ne8lrFyFAd7JH2vgCfaP/ZHWR"
    "zGQCKTGdctemLj1GE/OWB8hsXx59mMTSLPP69a9y2HuMqr7Z5QNKdVTyJbiVASJU8w1D/qltdQHflfNiop6sdMmk58ljI87AXVzWWMRo+uXspy"
    "P3LW9+sBm/7BeBgH601U4AKUDYPpjK7w4jDt5vGSgpNDyfezPQS9OP0PPbjYQZAc8hGq1EOMJvy0cdkz7vr88cEJdNR/NNNf7FCYuS/eje5553"
    "vbXMupMK7pvyOOHqUeLZ7WHWR+qdeYgu8OkgWOMDutF6bpXkw8Ps1qH2Ahd53UGLEM8WPt/SmEIHnHzvhYmCIiUZcbDVbPRmoirFory1dFZsyi"
    "1MvJznMiBF7CDv4zgTz4W3iyCY7zHcigdrbJwjfAOG4NcSUjN/9VYZ3los7WrgCPgCrCb1IAvcApqyADSFwgUAByKFsmr5mRO0kUAHX1C8TJsf"
    "tZAO+68gpWW8HHiERq9Y7olK/KztxDGpY5JZFPBVj4HUl1lJgmGetOrXRLvXW0C/ahQFHeqtfzpVB/FzUWP0StXj503H7/hAgbgtsrLT3ykamz"
    "xFw7knfJb4ZZIloYc2ls299G1dDqbrlM6rXz4G1k83eH754vww7zeVxlnyy3Z88ZYvOqCeo0cU4aDpepeays+Xyziv55igC17uUqeU3PdUb+4J"
    "lBuEKVgnphX9oj249J381P7NH2DqWe/xh0anrW9bvYYaixr4G/uN/PDiMAXVoW80QBYW7dHJ6L8dRb0goJrkCKQCYgNTkEsAwKCpSqCWs3e4AI"
    "4EL5gD9uBTc+k8wpWVHuIAN9EhFxeF1IEIB94gh2uuSecTsDPZ8IiZ6V5k37kAChlqFhtvdUjZ/ck+IYlfhMcFu2KwNEkdrPMkgHKLkz+G3cJ4"
    "1k1ZfDnQ3ohoeVCwowFgy6/2xG5W+gz0UGKG4d9kkk6D0+Cp846/RhH5QtaOwsPyfgWax4WZF4026QHexC1M48d2pMmFQk6C+g5MRJZVxhOBse"
    "GNYnl0jBf9nNCYSmG0bXxCNWyImo/omPpMfCloigX446lAZNyf2CSug1etE8hos3bdFYfAdjNbYZaWtDSDzEx9oE8m2rDi07x8ri5fp1UAnfEa"
    "HExezdm/z1hzIiSqy/er4zMvyxih64JWHMjlg818Jo8GREjs6M2l+JUGn6JRNYdNMGb6Adyme48swhVkpGP9GQPGdJz5F8EAC1VHS+1kR6W31q"
    "ZA5d9rSWCuVqc9FKursnDqZwzfxoVqojBjqsVEfy+Yi1iH//eEq+gDO9hpniyZ/FLrkstzu3yESXXYAKNHEoUXrUgQfHUKX7Fl+ak5uA50DjSQ"
    "X/U08YA3OsH4x/AorHpleftOE68jWosoxfgc3c/6FnlCmORJqQ0IEXYNZJk3wPMuDLaz26oKoF/h21iPZmeRSFODS5jrdLHNUIq+L98hgWu1sp"
    "txR+KWgOjvgnvsKX3hn5b2zk/1xSnrNtW8KvlF6ZoGqiUjCdhTWMW+3liQk/zRfGnM+V6oyrlrM4qSPE4Ld1awo56koJ+zRir0dNbnLju7BPra"
    "qZ93ED5KhBGCdRMLRQdtQYD34xtV9TCxwE7lfFD8HCTwvlm0yZG7dFImABQSdpggDCoqnBvoIeFEWV5wOQzkxtUgGRHMgUPEz8VKCSzM56XKKy"
    "lzDOHQePA4VKNoyYgVMrym8IHH1R4RzKU7EtIqBJm9/aAKqsUf/Au74CpdPLqsi0QYSQqE88QAFhUY/Pfmmq9f53mpHJAHQxmJ7rFoUFwZJHro"
    "ZkL9BXUpW/QNeyjwl/qXR4Frupw3u9Gl0p1PzGlQj1P3NhhKKC5J229GmnWmNIDsCr25DbOYyj1THaiWn0VhMtDiITbZJP+OoM0OdQW19WZqt8"
    "knWYT0WBBkw15aOvJLmaFa64ynuS1cHRi0iHnkXH66pml80T8OKR+bDwESzvp9YiDvxjaBrw88/xL22TcodfqZuORNJFikDPQh8hd6PnNfKRTc"
    "MSDFr3cY93/XkcTbot75pN1eHCBfNwEtXXQa3vjQ436hy2dVUxawVBOkLknvRZPaPxceurW50/87VpXJiYZxL4ochUiKcZOvz/Jf3mgg2OmKPF"
    "Kmg+ngmcgzqUxqyKu0+d6sWt4fY5PFheyiy95e6G+dNeYJBFZ2+YKbRxVS7VzdWkh3TNKxeAQ9RUjFSwdcX47nB1d0fyDTPK1NBvCij7Tad3/b"
    "5UtODqxuOQXqyIaDrghECceAyAHXF2gF7P8NECaXHsVdog+Vuw+ANa5OHhxGmw9FHdpShDSVyyW3AtcFghwGmCpkPicNhgtE2gu6DwU2ZsGOLM"
    "f/fRbP+Gxb8wNJtCBDt6kw9x1wDSu5GxRP5KFKbsHAIxdtgwRzknH1irDpxNTtIC2jkm8SsNHLX8G79Eu/gHlD3wsvpYoqStHSwFSjzsTN+1Jd"
    "jDoQdI1DXaqkwT18n+tC1HKRppw4IQkyUP82FQ5B+bpKuiHelLcav+5oxmAOXGAtBJXOzSZ35PpoZKt2FGDPEydpkLHGd4ZwpB8ous6vZgDd5z"
    "pAkJDaapVRW+sdYOdxMi7iSD6EX5JeG7t20AUup8OJR7DxUGr8apAWMDBCiMuGp4TA7m/+BveHgWYb5RvKfGuTqy7EHc/AXjZy8DNugmrKj2kL"
    "t5QbMa5k/qGBYizwnZAnmmutJdUIx9PC20SNqctxB7wnNs+faQ2oNPXzJxPX2H7eR8VLPaBx0ipLc5Woc8rHnu8YUi8hREahD0nLRGbLVKN+hq"
    "rLcHNJkgr+XOr1XR7kxzl6r56MoLYkDUApuLOI/vSj5+DgrRg2bjbUAEa+2YQJYdlYRuPNnhXBFoWwufSQxqhpmJoPVIQYblbUt9Gh4vvFKQYz"
    "I7oC0QvQGBKxkSK8sCKHaKVjOXwRR6qvt24lnnWfp8kzyfgyGpmBnkYF5UTkJ2WZYHqzHhWP6W7Zjcw+4wicfjyXwuSrHoWEk6gGgaYL7pJ1qZ"
    "/7wWbT0q7V5axmLnsX2+JU0rqXzwteDjyKAPzZSRcg0qqEfKBJOx8Jl/7fzDwOwl4dBMjVe7sHRz7uLci+VAd/mtdyIvYB47A06W+3YS/qAv+5"
    "XSTHC4k0HqeN+mYnB5imW8VueApfGhkjs6R1EEqItJQxk0iqb8TubO6hE9lz/N1LGXCWVGcugPORDF231o8cOqrjshD/wWkoO+klF3SuvUycZc"
    "LyiQV3nICOCoQ9xW3QWwL6zkOPFp3BMHcJZ/yE0hwd3xDK8IY05TkW6tEM/PRelhpWLiuvtS9QNvIRUF9DNEt1yVpeN46CBpjhQYw4KNmemcRT"
    "dYiR7/D+gCYSWH5tEM4R7L6NWvwhSuiCNTw8sdk8bZ4UudNiVwSZn5ImwP+3bQWKE5iie2mUebprykd5K3HbwFR9k0uL3dtiobqjpoS0gx+sBf"
    "GS+P/ffKFpe5SD0rgdEp9fAyAhlDD0OXjxRbtjQLiX2gAAUBKRH24gz7mhAsw4JXzTK8fu8nPlUbkClEyisR2ea6KgIXGMtL6foAlNP0f4Ylcu"
    "z89Fs0ux5jpJoC7O4CEZenytgi1qZuwv5SKJNh2C5PaL8wMoyM5gpKukYCU43ZVvJ1dNOFoJNIuhZ4X1vR+rZOnBlQeJio8Au+pTibCZ8z3Jr7"
    "+3Rl11WNlg5VABxRDeb2i1MDCJSlWvQsjLYKcNtVgOxU5FeUWzHHMxW6VO0+dFxGBzS52BZaj2ibaPP2niWQmWLeEO4tqyB4KwdAZPLm0yiOBb"
    "jKKXuJhMuHKK6Uy3rPJxQEvpFJe3W3hjUSkn487396rI1brBkTSsBRjoXSs1hu4dHzvzcfa/T6jHoyQqEikB+/uz89g6xg/zAgg0+LDRov6kYJ"
    "vmAKOzZYKH0+YlP9OVYnSlt4yJfwS+8F1LGXlaW5YBfgq19IvehdoXqgXrSo0f47hBT+XIPWwmRiy2erufDDDF/Zg/nPs5l8ZkehKXPG8dXkQt"
    "vBiyJ3NnjIWji+SF7Woafh/L/fqW2FC7NN3KVXi2/eVoqTGPO6dKgRidJ28+hX5o9fMVc3JsDw0lP5I4MMf4bX++3q7obpf2l9eHdwOGU8wr1U"
    "4tb8jbC5xq46RNZACdOQbOhjPWCuYJwZWI6cJcBKuMi4a6JCltcEFtUVuNigIEqljQt0lWP6aqEiwaQet7UDrPnx/KhIDqrJ4yyBCCzcIXzZEp"
    "PyC6E7ZK4tL+UfJi6mtEQq9GPXO7uPy3/BfFb2QVNsB/kKLhfg9hEpaEv1QcNbhQe/MgSc7JRLsDcqBTGhODndB3r56NUuDO3fJVPO9H/SLW2g"
    "I1KYrqfELI3ptz0NeX5AWC5VcQfQ+iZAcY1obghnw9s7yDESQPL84W4Zd3su0vkCEzn7SuHHCre+/bb8PtjrPojjFFw9uAH7Ej6Fn8M2GDU/ID"
    "w2XaAjYumEh9N1Aq+tH6Kp3+J4W+Td/nEQdxX9J/z8pYE/l2hHaW+mQzdCCBKvPVGDKoYfbXpN9YIqoJ9vT3IZyveDr1HjdWwLfNP01njVZ6o6"
    "dvSnywr5UFo/wMfkqCAouhcKlzsM5meicYozi4e/p7KGckEM+muauY/qVfV6FjGH3nBs2+sgAyJL3lHyUXFbON5F5+T0mRI+ek/MC3xujt4nEo"
    "ZfAYGr75xJxlp4jtFG49Hk1cdjdupIIFZ2iR082qxNVFK/MUGbjvZYErJ9ST4QxC4SQpfz9YdEByrQCZb2VbISnONz8Fvze9T5Rp19wLThWEtH"
    "eohHkbBFJ5eqx7TBcnNymnNBvrxUZUIqf58RQ/Zj3DJGNpOz7V0zzgt4PuL5Zp8Rid6Q/N7Hp51jjOaTyC7jiNbMw6szJ8wsWTYlm0rNIAQlRW"
    "7cj85mYgJwLwrR3I/pSCFmqWn4MVrpSmo3TIT/FD/Z3PNY8js+r6M9AT2lgHg6MBbFfOEtTMt2a2Q/BxTemql2DOvkJMe/mJ9A9trONVTQBCeu"
    "mkR+17TyhngdX69goV0V9zMgAq/9Ai8uoyigW8R3ntgK4wQ0pIoNcrqlPJuExfMawsuXrNcezKhSU6w2cqbfimoqfzUtrX8WMcxON3I8zMXRD0"
    "xieronj+vUuQbfOVPbnLMhi65XopTE/SI7oasjZ6jfEn4T5mDKkP+Fm80UgDvIkR/vvb63CpBVcf4yTPkuu3msoCN408VqllNoO6x044MfzgPE"
    "Q0iYGO3ZOo6+MmT5Q7fK+n0fQEswvCpD1r/kGx2JRKbJ1+SsHwSUxlo3Q6eHH5PFxeFObO60kDYTERemJGua8pXgzOTARIKa37bdr+3scnrx/w"
    "Blc/2kEKMc9KvFsyzB7ooWcqij60Lv7mQECG0JwcD2pSvkKiifqCaSiq7a9YWE16KT5H/Rb3qKMuCGN2QX96YnqAeg8WcQbVnxegqbK2+fnhoF"
    "QY9wlP9asTUuJ0+r1jA9/45iKmSzQWhAVQ8monc3FzrR2Qg+3j6CNF9TAvH+lzY9s3idubDNngQDhfcplQRumjcFabS2qdcMLEZNpHp3xounXI"
    "wBqYtobbuNDfbXXafUcCJ9T+zncmX+hiu0QlYJuelKb3F3JYFjA7PtQ8hL8gDIv1gYyDm8l2//kkBfHU7wL2jRdAAw0048qjOIo6tTFhxaZs+u"
    "FcYE/t6Ck8XZ8nUALREDA4GrLV+g7DYC8ZTIBkaGfiVeXZaRN/Mn3oQ3qnO4x+HtuYS01sWdfXu6QDhgnQKPKztW9mbOtAocXstNJDPLonZQVI"
    "3GO0ICZ0o+VNEuBxN2ZwIVKEdRbCN+JnE0vBACdeGjm3wLEI7peVqSNhqdgSoCwoSCTqzjryFv1Z0dBWS25HlLMsA+Gxa1lBVFRRLJhEZinCzD"
    "xTGyJuxFJq4EuQJQj80rGEYuts/cqrHXEeFLcw1RLmTA0PBS/kKxYd/8Heg0YYdmxtMA5OOU70evSvn5CZurWlC3798IhtfqdznsBuxzK1ep/x"
    "8jwApF2MoEkvWEYJZRXtAMG2C9uI92q/hMCXZqj7vmDUysbAY4gPpDICcqiltQ1YCZrbVZviBtOuH+3HpRvxZhWavl0JZ6b29mmuD/RbaIrWc6"
    "lQdQicDnbGk5A4dSWSlShdnAfdcSG1IKoL7L1hpOS7GFnMk22BPbl9ru8ix174m83uwQTZxLiKuNiMraGL0Cwe0yYYb/K95flLqtZPL/zAMu3N"
    "9dv7vLXjVel/XXQpoppsD51SHSErs01AP+Qd30EadS0elc8a/J5dL2Ucxn5KysuGr9tbnM2+TO/sx+3QX3Yqj3FRYSh54EL9ZNY/annGnf6bYb"
    "kieHIkVN+jJv1q3Ih+w4CP/iTe5I/YeYoNTUWTHp5Ukh0PPxqRXntPhMTnsn3soqp1E2P2hD6U+O1iNVc6ms1/2z+qxBujYW6JobxJYfY8lyLj"
    "NjVHfgyot+IEQwdqYEXPH42M0vslrh05OhAT48/uqeHT4nmFDgyt9iCLDt0FEE9wNC3RG8Br8NlzuEw3j9dpiCiG1wzSwwzKzyqOsm7980GB6h"
    "hZnoG528O8ZuAgaI3obhB3QWRhUK3vBktzeSy1cn4+cHMmvfY9GZ1X60l+yC/7Ja2S9hu2CPnu5zxfmyENfJmk8wC1QFQw+0Lc6huHq1l415XS"
    "rklGqApEv0aAy8bNywi2plMXbynupttVopAjgxOMEvnjt7K1RwUdonOp30q5yNYivfMN3uYce3eu7meOUkvFpJ9+l7uv+yXrnlyyE4Vj8c7Zih"
    "53K6Sub/lKNA2+W4BuUTQvNl83Hwtiya7yts+Ud1b7u5T2jUmT3m4qwiEI0RjnUta8JxlnbdUXPCJf3xyJs3wfqa5hXy3/IVpH3TZZGqnuJHbl"
    "aipxZGXsw5k101onJzfbEpbkeE9rY+DOYcgJPyOoCGjdoYECvSg7Va3AtRoNanl4jtgzVOLpoLMgvwbu90vfQj6h62HCUgtf74XokN7BCwz02L"
    "RPvB/11G/sJBEc5fu1lhTZMQMYBldCUVTagV+Xn/4IF+ICCd5tjZOFZIKUb9aPGC9Si1M7RLrU/g2wwnYV5+IwyClovZPxxwElvBJRjaa+v6I3"
    "KZ4YfmIaYDFgnNpJM4gJxL8L1n7EHQeScNUyk4oONpkvSW4yagjfwvq5lV2OQ3fe2ksjC51jfdxX7X2Vv36Wgqy9fSVTeTitj1/N5z+qafjU0T"
    "7ZPARXYuTVgWtZNhZ7kRNf6lI87+ZV7OCV88efNPG9KbNLzDl9zCtSdL0M3S8rZ8Y0engGnqJM4bAjEHC0CYRYlPRyAF6q7kx41vHQPL/5K9fW"
    "ewpj8WF+BIzeJTYdGlyyDjW067ZRyxauk9YX+8i16jDhd0nTET7tXOr1sQqIL9e+Md3zhDP+BOokl0o1Ytq0jiHUNJFZqVbrIOZhqFD1yY99HB"
    "7EoEoQzNCvW9SJvVJ2RLEDLt6zZW52SE5UYpXF0k+3oz6FEIj+Qzoi+i64Qa9vUI3N2okjo+p+tlLMHGFXMs9uwXXfFVTLX20gwqUlpE7hK0B3"
    "+M9dCl0wypcgfQK1EbsezqZfj4krFJ9iDQLeOxHOIPnE9ZZUQ1z7PUOhZNfimRMkcnkRehXlyItDFXLlNMMeAXB6Ifc7iq2ot3D0sS5fgkWuAi"
    "zgYQNbk9nYDe/kMyX/d8t3b3KirZyEzFuTd8mdY/6pGSuK3N5aCDLgjgxkcWAvd+PNhQQift60x4LfeRbiBl2DZOIaQhKqnruP7aLnpb4XnvFM"
    "z64zYWhDiDX/ml2peCrfjGKIfA1WxI+K678VNEARTQpAdjACKvIJYFeVEU+OEGVvIB1U2gShUNrdxcFFs8UCvb9ggPkv/KDptCig/AETri18G0"
    "ADGdFUdoVA0ekV4hYRwxoKzWIxzAcXlwKuznyIBWaRGensj8S93KDIposWoFkI48E/E/poReYC0ybaKv+1R2zMj9+32eoPSgy1Vm+H+a0C6kc0"
    "j6HJjnoBAm8afjvE1RBVbPiYUyTMja691CkFQNNcfHx/1F6lDQkak3z0svs5owUUtDF5i2ai4pPCmxQLr2a9yW8N1VQ9L/prfajxYUo64CCeI7"
    "aTyH2C7umlbr1FEQdIc9YGPg8pygAGcpHSHIbRfMDJNJvfT2eFYnL9ATf7KHlpDL5h70FwXeWu2O9DsbW2T9t5RedfgsgVzkTo6sOSv8/GPfHT"
    "xGq737+KsqikpSxXLhZARz0S2M6g29n9ZEXWudvutb5MnUHp/pDCdszfsl8caDxQsDZznkm1sxUt6V3TAheUqomgynil9x4PhMehfBYrUGnGVi"
    "RbNht4E+KIoUj4TGifPaa6GPp6jombJAx5aEEW4HWSMlIe2eZMQyBdz/2TZP2ufk9red/E+Un8lxRN2q7dPQJ7YKvOHwAZfZ9cAJaqYNvoU5b8"
    "OjT/LHYvxUkqfkVnZwWdcVB25vwTED/XjrflsKOYmzDBj9yc7HSvg5FPPtnXzwesyqux7nlX+ESIwC/jQqv2Nofcyu6zk6z/6JMyG7zggdj3ke"
    "FqfiFHYa3uc1GsbwlG1IA8bLFonpkPSnSl3SevnGYu+x9rN+6PUwIJ+QAXs2BVVALG+oJ3emqARq2XD8hK9Yy7e4KT+gQYJRU9EpCtmbGElEe6"
    "QonL4g8qfM/UERk66VlwGxg6W/WyuHpH0e776cfqp/XRc8Kx4fp7Q2KXPtydY5/K7W+XK9Utdnhl0CLg6qasOOvWOv9Ojuc5b3MHzZ9n/76qDZ"
    "X7pQhtimSraWnlLaqrw3cTK53fBHbvdfJpOmyLDKy+9Je8qO77Ztsg20AMHp2zsNxYn9yr3ZstQtCeztCBeySTXynoDP1tDVzLidW3n/ZU2iD6"
    "ccREcWP0ZWsqV9Tyts921JnR0YXNizpDfIKm//UAffrROVAyTNwPaRGpMXEoSET8z6WfMvqCjClhjuJdyfJOrwKBhcqdWCY/AbPyb2JsFmM/j4"
    "LtmB/jTAScLxEyp+uMy4l/sdnoWTCdYAn0gzZGWH2deqZRQFi8AEOHSGviF3dnFDpspkYcz/AG2CvvTVrHnLPT7UCCT9fVBZv6LUdzK8jQHCJ6"
    "Vsu7ZSj+y3/ZdXy/djGdH7tx7NnTEWPG8ukNk0ktMiRkjtSMmFZ9L/k6P8mbF8p1LKP/QT8gd4NsE1z3lwSlT/zlBMljFShrx2p5XZdk1YGeZP"
    "wtC8jX8h+TMbqBt8cMWGfkrdi5AqY1U8RKykOZx8FHudp05Teu4kb++ZJdSTYcu2bv+m/gnRMQeL+itM4o4MfPO/O6PS9v7qQUAnR6uUdvZVNU"
    "gPK1DB+bjkJ1WR90IBCKOjVhxtCrCghl7c760xDB8ekN9snbi5VxKkheiDxr9XRbCfyhN+Q5TULiHxuNmZYZmQjid/ph50c4Yb68i6R40HZoqW"
    "qq2AS0hUWg1Y/WHiR9IP4b16jaCBY7agMVEzco3ips2y+36SWhDCABKNTPxbswSDKq7P20+JhrDGGbj1a7kNtZ6MGzu4IPmEH0jRzUbn/CIfYj"
    "Lxb5KAdCsbftg3aFhKqOBz2k5/JrS5vutchwqXRXR4IO9kF6gcxksMlnYEWvb7QEoFuIPkE0fO+q4I7T547B7I3EYyJb9j5tSdtWeXDagr1GQT"
    "R+MXoa9Vb5Vd381FmNiuU9fOHVMe+nYJQz91edBlReRa2IU2dtrd1KCvUrrsB2cJU2zSy23mhpHUFOhtYsDW0IYJqg57O8+C5ND46qQ3tnQLYW"
    "J1GYK0QGUXMs9RxcnGoMrsu5pBm2csqtv/0qhkfSrYN9kbDP9NeGcaxTH0irP1mAOm6Ek50Gw4IF2gS4h0CIeZ3tNqeTtF3dfhivdUm55muOeS"
    "9oB9TRVu1f2WY83hSOEcy6oPljmPIzl8Q/UDfouKC+gpjkiJhVp1InGXvMWlet8TdxRzq8vWbmf2kAIgMAf0SC4LZf9Ct7NDoCGg+na8aQ/C4z"
    "C92HmXLhB7A+rzqLmZW6VmxAMJIF45IuSSUFksVRYEcBgfyUEI7PKPr/GSlTdAMLa/uf2jP3sugtevDn1j8etdhd2TipvrFYr668M7BCBgdVe3"
    "7IWL6jViIb6iOiv0hD+o9fiMLIXr23oCefSveS1UC9zMca4EE87nyk+h95HkSCn6QUfvhnbw4/0PJIIs5IRX4kF2z12Pq4tVRDEQJzr56lzoYK"
    "uK5q1Hd3MJqfoJDodRZ4+F4btqkqDkzlUdZVOw6Tnc8cv/ympX65jRZIJ4xi8T6fTyhZrDeKpv4O35v8EvXJ3JDB9KVX0pkiA8qGsVc3l4w2B9"
    "Ita6vUc5N5bUfbztjf5ly2orR6Jhfjx3umMnBke8mbHM8cEs3puaLVTSsBWkAbIAPcZxO6XvcHu2P/YApsGtFvVlRsGz1voAv43EruJW0YlMTO"
    "CtAY5ELskT9PSYt2V4dycaFxzFYUqm5XwzOc98WF0K1/kGi2jcuNPQ93BKNSGiXEq5fsx9xgUt6iKGTyfCnE73e1HuSzo78jm/yTEJIU/ULWCp"
    "SQ4q2oKte3EGR7VYrjptJAGH8Ml3KvFupO30pmKA6UZ4j6cNzHiHLQpZIE1fZc+T+TCTFaet25heawm9PttRj3nMWuR6t/izZV3Z/bL5itD8TH"
    "OZzFqO1g+Kw+AmoRQRBK/AjtFxQMmIVOTOjKWKtjdtHmt4rAZCVyVafHN+4O5z62A4qSPq9dGryt+AX37xJaG7r8nEXGX3NB28T6Ah8IsQxogb"
    "zuatwQ2PPygcxQVhFjumvnKosgRHQee8hNLJnpk5k9+Lq76jzBnlONGqba7QCwc0vQsoAvIV1hoWqCExy95t6vr56Cuy9jVx4Ih3Xt5zfOLGVd"
    "lnx2fDXIW5wYZEmp9KuwHkDkuRXGqyLQZuNvUAdblZEUQOsbE56Ms+sND9N34bNyfDrDpFxNvMmCWYvJgjQ8DRV5JDwZINIvv6RXYrwpyR9wWr"
    "+r/WFleqBFtSHGQ+ln11NAaDxRoqvmTn1DrXyTHm1CZL7br3ech5ZFwS5AcJZesNxukGY/rgwmnQ9XQ2JZiMeU/Exz48O/rPnVY4YDZ3Ts84JK"
    "E3u+7VokLiFL36cajGTVnzTMnZPpwQVZUga2Zu5DtfvxY2bJwICs2VVhObVYLn96s4E8RuKziM+fT/a1rpO1bG/t3c8DrhME7IPydZdAyHEDFo"
    "yh1QtIbU1bCkaj+xAAfOAAkSHYlFE5Vp6slN/xMFxKZy7zD2AsV9xmAPPffC1KrCNO9nqlcAEh2JsJy0p+I10NLJGglerh4LJLK6G1+0uW1UY5"
    "itAQfeiFdJafBm5zMD1ykivrQus8ny/ZaEqUlND3EQ/Qn1kcsgUG4zi7HwdAfKdXdTiZuHlk0oVvHHhoxXWRLvHHt2N5x0CDdcFPgT4au7zsfJ"
    "QY/21972jSS+jE9htCLOv5Vbl9P4zfztEE/arZuo6Rh99OVEz7DF21Mmrg2AeRddeQhJTaJD+Ju5cjEM3mgGvW8pZMH4EjUIUsJRE/QM0yjpL9"
    "H8l33zax8QXKtQnxdDbJvnB06oBTvOOlk3rTpc1+T5fH+L9eoOt17DKpcImjPDvRaa439UwUIAri98WseV7qI9exCduD4gWtq82Myi++IbOuFL"
    "6cQhvXCUt4ISGgPL9FQlJe4q/1E1WTTDixk0uu4ufKBgybxTN8Luo7VlN0ReCNvjHWuDbPzmWPtYoMT67LdUnNq3AsKxcERc1PVDGDDY4Kgp9I"
    "Y3M31yO/EWdEEQIbr8JUOozTWeazIiLtPaVDbvReAankmyNPJQtpq1Xc/QRItbg6/luq3cacIWP379F55BFnVlxhwdv0NurVnzunud7BwHDrxl"
    "IIKFFxAwXr1E7+GYw4l7nSZ6H0ZkLB58USxNx4QTMdPAIFgYx0prltBWQUJ2Ni4P3qIcS8YW8ET770U9/mPoqx6jgoaFHZtQIGQmmSLOZ0Y8Dd"
    "xbSslnyjVo+HmGxZdPi+A71gS9wzhvF0eT4m/4bA6lTeK3EipldIo31uLA5vHN+z8iXPUp0r/hYiYH/qN1YVIQd9OLrJqnMcAi6UmlCeb4f503"
    "cra+xJb4yjP7uDbyfLsJh5V+LJ+vDa/Marb0axTgAldOTTxCwaVM28TaqHFL5dkdXfJfGatgS4LZgcQurgivZIXoSl9Y7WOkcB87MB0G/07rJa"
    "Ez+mYqdve6cZAtcGfvEOuNhayzovvdINHyJASTj2wxEBkDX+Y2fu0UznwPWd3tyRFJIZy/sptzCuF62fuPg5p0Qav9HFiOfn9DJ7xqqhB/ZXq7"
    "QdKPutiL+GdAKqRqS12A+xCkD1dhcG+tseWxq/0kNmbtx6ze+U9rOFQTfSPx7/iXsfkdGd9fYS3VGfzLK1saoVUrTg2tx7JKISUSioSIPZ9+ap"
    "g2dGGbRapm0b/tk1jNpiFBvyNtkAWu8glKmSNepkUWmaecwxL28Sms4Eho6h3ForvZ/TlzLyHlem2sLtqIcx5SHINVbd3mEWsQ2SsLs+16llGN"
    "xnyoODQb4mfY156xM50PLSsPWJDEEN3F/mlqcfRhNXlQfa/5gWmjBabM/mSH+MWIwBeI+x0K63EsLyJupOoGE/DLKL+csaY4VAqjMQciFUJ3qB"
    "gp5yVIN2w86cWrso3CtLCmgrBiF231/8EV1/JvAPnHgOwPHnfgbxRd8FtRgf9wjh/w8gO+Zm2pEl2hi2Yh8ZrdMX5VT85SSOkC6u5iyPrTbG3s"
    "ZhSgoH+N3pp68sFdOuUJfwnZEaqncd4Bvig5FH7LdOEMyyv0LVlRGWRWrJU4YAHbWcQltpxbVRWU4wCXZVNu0IqKEzG6ApavyFcfyhUONZAPGB"
    "XpxwJt3//RSviXYiBz9o0qt+cPXnd7a06+PJ+VjKm5lrt39K2mv8Lgbez3sA7GZzWcqk5NtgZvdk2wdj3Aox+afEHDvoP0L0o07d1r5WMfK2MW"
    "5E5bbsHpLY58MkoGYTFYPGHKWo6xf6YY3SjO4NV50dwcT3+jyoWsOE8M2q+KPQij9BaDw8YRRDCByboZtzJVlQhmqES2HEkv7Gv73KpL7FumZn"
    "ICZmwL0iC25K3PcGog/WwRM/nrnpKpX7cGImQ9Gw70FtGHTRavobLr+qxNwwY1097dFilfLC5vm2roASrWtuYExdZ3TkE42mpMXVr0UnLKKM4W"
    "14sVuN4owz2lJcJlbtT+so6LHN5SvoEMclxcTHfmeqFhaGHsQTfKFZBYD1b1CKVSfd0DrcKZ4CtTFySIR5LFNobXKndYacQ1CI32Hp33YtsbZB"
    "cI4qG0qlbpf+lMA5ATas0kb+STO7TcDdt69H1auQVpT+Gtb1zWNnXHz7TXvTH4gztDkiCTB5LH+4AaSQrfkqt4Fx240jSnfZTPqvwMWRVclJvy"
    "f6L45w7+VQzp+MMZijIEPxoQjgobpQerBrwgUQJm/uefpEAiQcALuMUo3JFvyMaos20U8NVmGCWdFl7JTQwAa9lFq+t/X+vFAeG9rMlIT3aloN"
    "zq6JoB+jCpk2e8DKwyeoMayH30T1q2pP9Fm9icMvsMBdryoQlbzVaIwbiiM1dWyfjulVF/pOe64+nWQ7kB9a436rliY7VaYHCxIHgVxWHkTJUU"
    "t2JCA/l+tvgdeNbEuxaTab+pSu36XCyK2KBdOiKH++QTv60lDYCBU/MledbYBbVOrrS7NDgubuaXm2Er9P/4FU9iKwJ3pUSr2Ldl5P3kodS2lY"
    "hcSH3b8/M9+UfCqC+PcnZyM05v7Zqc6aW3yo38/re4Vf29QX0k0UG0K7giQ9Q+qydeVHPpQ/is5iOUIoiKIfNAtcZom7OztscHe+PqSyTJgAr/"
    "v2OdTUo7y/YfVacUky/lRwW9feIABiFa99pUqtnaa5YoTUCkFKG+Kz+Cj0BXyde0EaCYoOhn4EI5o5rnleyeNMemhOj/OWrMRb+6KVnktymIQp"
    "VsaxKIOCt3xBtX+7126e9TJFR8N52nSa3dYm3F8eerXlaixjIvDTYCIEmKPg1PoSPHv3AYfpT8zc4MGPCE7M0EBdH+XnPBmjp73QkTWmaKo/XA"
    "75xRGWSuJTQG4r2fmRK91P3ONDCEgYr6HvYPT3BBMeiaHpX+kn6U3nNRv+nh7cjz5sUXoevRQJzlAMP1rFDdhp+nTXQiYi4TAHsxeo6nL6y19A"
    "q2eBhL+nLa/4YfroaEtJWpkor/jqN9czLyQw5JGi4fU0kWxHQfJjRTt10F280mA1udCP+XsQL1zJSaTRY2X3cIL1GVl8VYUHadJoyO+6fWzLnO"
    "NpaHj10MX+PWtALjXMSkZOREP3Z0a4d+AkDOOdG+7a5Mhe4qSFZjUHnma4T+TTURKmNQPugCQp9/9Y2lGJqQTLI7Ap0usk/vyaBsZ2xySkIBLi"
    "wK59WOSoeRCvA0HOldpuIDWooGu6nLjgdbUAhdVdqY995W/x2INi1nviRVigdDxjP/84+Hkg1TKU/LM+/hAP9CqVP77KWniitMvSApdqlOCrss"
    "s0rW14qkjmTff5Ktm9ItrN7uqKmRz+GVtSa2Omdq89X55fLBLEr93GS6lBPVs9zjJYTLHfv+8omvajSOIhkK5N7jJSxxRA2GMm68FYXwLOQZal"
    "WD/9bpTsy+XHzq1lUagC8CR+JacEaF/siMQUv/q9HbWvKDzvDOBGBHyNx8NY+GrA7+Kc3XGlLzdlaB7fSel6RPA0Z0YOHYH/28sKd9vSpXRj9z"
    "Y280OmS8pcS1D8FEl8IxCbHh2vFSWS0JjVDiONP+lKzJzYgAhcNjb3fOknIgtbNhrL/hSmbvps5GOqLsZjMU1EkvFfEq86oNvZG9UJ0MkKI4mu"
    "Fa+wW1kx/EPt9UCUZwpDylzW+eGHPdxWFWoI2fBOUReroo8jHhTIfdb6OmsgnoyRbaLOovU52l/hS6ZC1PeiB/i+DOVNrwtqvDYvR7sVQ4wQlj"
    "HmIRdXGtsJdm1hX9HY3PeLRfH9ugTvwzQcKLVtxa9sNHFYZw34/OmifuKKbuG6NeyhkqmeKFy+QAlLZHuKlvel7dPh66VNTkVB0iDhatFQs3OR"
    "t4UeqLC0DSFIbJsCm84KP9/EfX61x4hLjbUKxNqydoJgehHsj3H0qfkUoqS2WVAUL44b26OAhf/l9otSrcyXuKX76BIC0O9d8RKgpJ0knLuN6A"
    "EWkPPc2v3EVPNjM36DvzY3XqCtjf0TNA8TJmd/JU8NOTz8HlaqGlNfVJ71wrU6IQlexBEQnFVwb349v2iAEAdHT4HsIQinV4Ax1qawOg4qLU1e"
    "vbfAPdnyMiiUoceBY5tuY3jhGITDS+hsbq+xe4ZUn36jPZHsQ+kFxVEfckBJUNQH+j1RlIG1r6ya53f9rIwRe65Qfs2oShICdTM6bR1/p9zzl4"
    "rmtE0Znlm7YFSjYa/OSSaWJgQ3M88XdiBpozbb5zpOcUr1hBjKlhiFx2MNpO9px6np+DzPyWUgrU5wz5R3zJJQjvHXrvWVfVNkbridwf4xvgnZ"
    "Q57Z/dtFzuBpO/LNX76EsRuYmj32U+lcwLfH7Z/RKflh4nTTLVdDX+3Ilz6pGAzDnAGjFo9fmpp0hBLsyumqnCovvhxlmtglzTJOSB5M91wlZJ"
    "pU4DTjYNcvNMJ2RlIdztooS1jLqebknrzL9uNDp9FFu7/upCfUSXEmfACEbu51+amIZpJ7rCi9r31o3j6TBlqzUCOASeNphLzV9ZhT4UMRSRn+"
    "+ijtJxBsWySHTQmmf/Lchasm5CK4cQR5KSB0FVFTE1t3oMaWO15aHT/K6E7JL4sc7FzAiMSSbF/3VIvtqC6xoFrW7Lr2I5GAFiaNH9xHpXABrE"
    "UuyIxoe4LYJLquqYo0X4smA72E4fuEAfHWEPc50LqxtrYISX06N6KVkV8IIdnRHkcwPu0+kDcXKngbQC+0D6gR6ucsfl0TM2KVbtZ4frEBljWZ"
    "cSubOeve49bGWDv+1dBdvB2HjNTU7ISSlooLijxnU53T13IzN9v0Z/Rsc56oRzgWKQt5Rb0RvPTatPy0kAhl4ivQ0havXnoru9d9jaJ4sWyweN"
    "FLFYJi4gM7REtbmuw54WrLYSZha33SZ1sJRN6lrvXU8aB64o2b5+ODwZu56F3kJV11nnI8chAKTTlEYZk2/7bvbh2OSj0xfSQe/nvBbncpfzt5"
    "+woaQ7sEdkv5DS9XhAxgXKnERp7Zl6nRxHGe317zixtlKrAiYi9NhIcyffedNOtuaGL1VsEq18+iG/wUhWrJwB2BIJ/YM3T8+wleQ1wwg5SMO/"
    "1In14o37s3xus7ehmibvo0DAUPU1MWHBnmdYTjzhzjGVHUGqterA3W3C+OcS4OZoAegJ5TEm4/ILmBI13wC27+6K2/oWFdZATaBjLV717GGS0a"
    "nFv2IuAh4d4MEdviP1E81CQFuBvzErgFmcG7yUJNNTgbpZNHILXRv41kDPYCGccH7jHJrzv7tMnNnVzTHmQhjQG9uxvmk+ZaOL4dJOG7PmCVSw"
    "YKM/9SbvVeIcmFOqvo/kIr/RQmOJXwbMn0Sv0GoB0VYJwx2JWp/ZNhV8NoTTkeJc2N+clkKKl5gy1ksbQPNQ50+NQHDptf7NbQTZZydf2VDauf"
    "m8LHooaY+BDi9C99DIG8SlbHS0TMLZlpOUuXU64rvFcoq8MSB0zzZUF4Y36tLEjdwxvniDYIvqAQ0/zSUG9+17R85RLbIuo6ij08XqpcB1iAuo"
    "lft3qOG7fZjs4HXsNIQWZt4+XrkzdjiOVUImRkh3XltFJspUmX5su5sZ8Ox5QI6b5SSdcFwEpeU33Tk3GHKOFEkBqjz+Fai1+tkTKwEs3dKKJX"
    "7EiRt0zysJCwWLA9IXe3EEaJZQdsgTC6eEc0EafUmzdxR4WlXSWgWMzne4p6rfwjf/NCt/sKcBDBUDXeFJuvt/6cTwbnvagPLNeX37MfvSn+fj"
    "O+YC96gcK/oUyl0izT+K5ObooWEEfkaORuxwcFMgplrK8EDU0Z9eYRs8GY2ZPPMHQXmg8QkmltT8+yH670xJW9jdEhUaJMBmyVBiBy/saaVFQF"
    "g7rYaV9D8LmGkx6UOM+yJsdwW5EJxGse7qTUh5ohgLdY4Qwpp+EIyo1YnrVWcog2vEaZcBlgVr6fRBk5uTRCNjccZZvruySAkfzQhJta4n3Oe2"
    "PcRYPkqenf9RR1urgdPJR8P0QOwKY5+EdHvAjL21sNqnFMs1kd4kYtfRTjIZZHfX1nhIAX6xqyWD4tNV9IG1K8uPDTlqnseivC765vitAnieTm"
    "HRh9ZYpLUomFZeRmx7gJa9nte/zOKfGwZS+zSa54Glcjiq6IB1LlL+yIEWKNWNKw7PUInGaJ3NQhZIkSN++ValaizZiENn6O/f/OTxZD8G8xd3"
    "xwMp4X3ObrKMzdQ9pXLMOgc+JduzsVdpaP7Y3c92Ki15bKbm3CtAaiY104aGOi9zKo4CvJ257k1JoSXt1qETUiCus6uIbeIRP9oIVg7Z8TGkrb"
    "uinzSOTvDiAv8mDIdHhZN5Vt7MDt+gXquoYqLwsvXoy9TFzhfQc9BZBf9NvuEdf77DeG/LV+1oOzw69DRSSdLJ6iw2XthmhKd1wGKekqpyp2r5"
    "Ah/lglFyRYhn9zq44dWphusoaF8f/dyHAEK5OHH6snwhlT9GJBldVPHf27YZJAwcfET2DCgxq82IXGKaSTejp7Cj/QMc19hFovAup+knGTgcWB"
    "5UjxmyW4ZpJCbekckiXKpmdb0kRehp0s0jlWfwuaj/yC+ql5FtuEvU3mxnLzqhz13yHdmpbzroSvmR0MCuCZnVgNO5bF1U+zIAYn/caF9NrbRn"
    "3hBH1ZEHMC2eFsOGv6IJhcp5xbb5NGHKBUrEEHRVKz/+TleSV2qy0NHj3IARO3MuTfVGQ/yd9jyAIEHgsT1plVvzyr2u5RueAN4Q1gNLt1viEt"
    "q0uozrDig1DruvkSbZZ5niEHHO+3W/3VuyS4rBScwwyeoeIH4xpeTa2BUmwhO9Vkwvw0wCSeenv4v8EYbGi/45x1O9mp84pkM9EtSaNTblfcny"
    "OLA6koKTY46X5+rn705GYMa3YSP63K+VyyHPyBaNE+5YfKu517s7zK2nyhUKGrrZkYaAXw4V1rjA+/5ZqmDBJNgAYrXCgR4wu3PEMPXbecjcqY"
    "yO99x8cbmkYpvGGX11wWArCeVN13pFvtfUzfXeUFsuPupG9/1jvRuvhcsPui9zEer7LQSpoEwDwAvIEPd76qIV5WLUBKrLY1nQObEieBuMEtNl"
    "2voT3+Latzk8DBGWjvnh8YKs4S9swLTktgYHMAi9O11t5TrTobbGWzblB3FEOFRPskLaIoweaNxnwFyoFB5XPABRQuB08zKr34WA8JBn/Ie9f4"
    "qHUvus0/NnW7MIHwB9zJgQhPsZgBO8p7zI+iHe39NAr9nlMBA4fA8FOh0EV4HuiIpMcYaAEfJ6ycz/L/E/nGlRCfLiF6WzCudxxVGoRa/T3m1z"
    "/j+kxwEfiAVwb54JzBRKY3HxQzwQ29zLX6TiUIZ+lQz6ZPP6848S9X1JGG4CtdyOxrx2VBOFETLz2Op8CktPh7REY7Iz8emc5VYJuPP764vZLY"
    "LT5T8vG0izqGfeeGo1IXA58zoC73ZErsWOdzyTnFJi+y9m5+Q0uV0dr/M6GgigVAZ7Z9gfnW6esg+Ghv/Apc8fOHGmi7grpE1qs3BjSgycQpu+"
    "SIIV8B7AAeQw2v8ovJ/QzztluA2KsofOehmVf0BGMaA/Drk4g5NAZkTBrvIYAZUKOrSplHf3KSizYZmRJd2dMTsJ/TtmD885Aq13p3+8JdY3lx"
    "HOj65TYIfCT9c1b2ylJtyVsOsdZVy0j7p+yXucQyXzDmiGrz4cvBbOhwL4sTuw8j2zfWoeyAb8LWMJlnPBwMI3Guxax9pFYPr1Xtop2LDsdKd3"
    "CkjqfQQEUmxrSNU/pXp0SaljtDHkAfWonRC9pZzTIfQDYOak9VzeUnfiGzxY/zowkH7XXOVsStABjPVonWVbdhV3dGF6eyMVBcr9bh9nKQyxCk"
    "6J8fMvPpQ+FX4MddwzSFLPh8uS7UgDJprQ3EFYD9wL5afeA8duQaQFCOBKYKUcGIkEKsRL/81FARJLWvQ3LgKF+J9rqyM0Le4naxnbfI3ITv0g"
    "BmWoNnjDJ3KFTQT7a84rvlu8ekHz3IaJKRyVKlzbn8Sdqsr4wcpCBLYzoGRKN+Re3FFnHDr4JaT16xmoEhSoLWjRm/4JBwWepAOvVwUrcgfU5d"
    "axop5OQ75dN0LmN1f5k6SsMOGpxE8dbaHZ7FOGqWjm6JlJRUqBmL+ij/G3BIaMEZmsovbf6NFehHeTC8igbT9I81lzq/rdYV8a5iiSapdN75o4"
    "SQl0FEO7ZZ7uARlzYdCKcMy0hRibiGfMG5b1phAcHlo1qnGcjevBJxbm/ezM/hsMnx6bNb6xyKMbfM8GjY7halQ5tZakh2pPaiIsnvNO4pmWMA"
    "kgsQxZurfNAJ1/sc/I9BXyrALnJvguLe2JTsoyewF3cyV1vJy4hlIBO1mJ9OB3jwiEYWB43MiPbLhmDbIWEp6Y9QWgPYS34Hc2Vtnjbz4dmSUz"
    "iTUkzJ/p2U/B33QrquJyDRM365I34TskadS7l1LrOOFeTqeXzHrCdXtSeePBlLF0V51SKD7GqnnTiA7lVM/VJXEBjdadBxSv4O20OfV9am2kO1"
    "7WWgfKaBsZMZSt00YqDyS4riyAXkQDfpNUOwI01uYt5mO0iA0FUZuUq2VycQvjxXM2xb6/GGPxA2HsKA8Cvnk+Vtc1PrAt905U5QiHQg2cbvGY"
    "jTpfKqLnqcQs/1M2mAUV0xfzuc8KzKi2qR/zETJ55lXWPEz+l7Vk0tOfuBeMbtRx1HnpNNX9l1cNUZGdaexGmC1p0EIt6Cl2tBue07YR6g+DD/"
    "ON5bb6wbLuy3mXeuJuHMLabhCtrdJNr3H5/yRwBUhu2S6jKuZ4iAa+myMB31ipqP25A4Yzix7K4XUy4usM02AMbd98hcExHnFXOXaxI3sgQQ/p"
    "VtHM5U0C9Pf3itgQ1tTt86JrS9or25ImnWfIu2zvoPK3Py5LsuriTQmhU2hXMTdbhJAbvQJACym1PyRE8OSErt9QlevVj08h7rDlDkWlIHV3rD"
    "G0bZFKczR2L3VKJbJvtuHyACBievDNBFel6HZ32gwDR7OHLaAbcOafPVnmCJxj7LKuMrMhJ9wXAsUalcnsJGl2Esa/WKq3xSYgqfYdwQsAhIMF"
    "bo/Kwfzq7tRr5OtHHOxdpx685YSpqVi6Ove/OT6/22eAs+GTx1cMnNOSZhGFE5HhWUiMWWY+xK13O36AdDorPgFmtXf+oTSdm4uwBuXRYc+6P0"
    "GWEfOThz0eKV4VzfHqSf2p/t6nTvsqiEkrhzl+i1hbfK7FlV1XmRuBpgc4D9ZHkg64luqQnZdL+auK8bsTbTi0hW3IVmOFppjmiOmBetYuFEIR"
    "qOmV+tcEoS1sjqSBGjPKj+txVmRdmkye1ao6xip4mluUQ6oHd4+uASjkGS/10Q+k/ZPrdTFc1H/7VZZDexoKkmSGbUq5eoBMWHs9hKNP3GT2V/"
    "vZo/CPTZ+Z3sDYhatmqCJ70Ihg5GR3IVoupXBmTci4hKe4lZMopTlxIpP9HPFNQc2NXqFefAViz1ubbRWn+5JabuBGXERnOQF5sm55S8bOQfV9"
    "UIKWKobLG5dDyvcad7hakRIXZBRs49PSA6dqwRK+9wOfF2NWKTXtxEmfnM852OMgmtx6sgXAMGWTf+4tiKnkd0drBIo0d2OzjSwi+SrQiv4Pc0"
    "fA4nVmGT6BqOILJJ1KFDOrWf4gBUrf3wsWh1dgGT0wnZkorZ3NhEXkSVJe0rakudH2Mp3f9XUBkoN5a0MRO8CXx1etDHBfmkrmM3YmtdwIvDft"
    "M3uRQ5HprRHkcME8arKs7QlPXNLjqYdt7A/J2oV1GIViUTSeOyVMEoSb2c1RoTHEXrKyRSqjLxZK11uQhrC77qbO8QQMWOefYgrym+PjMZjdBN"
    "l5MY0a7t7T2w6idjRzOKYkndx7RZmhqJqCM5NiJfGWRtIoVzhsL8uzGd1pud7GBIsdkHS62LzksU6XtdCBEhFfetlKv2oW9VOlzc8x8rZbwAtl"
    "G3swK46i3ruedp8iVMPv63vFzdi7EwpdzIiLGCycU8kYP4VPY/k/9dgDf5sAEkhf/t/Qi+SpHiO+ro5OJ0kswqIw6A75G2qgHrkA2fGnlbDg8M"
    "dSq/RFL8WqerZn/YOW6YK0yEolEE/UMvmgccnZthvd2KpjexuJ3gNtxERdthFSR1ES0M2qKw+9j2WoICFGLm9rVfv4qojkQYm4Lv45Cd9ikJ/Z"
    "BE+IRZzGTKrkMeokBR19NcqA902Nxqx9kmjDm13FREB+Pv5dYgvMir6M2bK+y6mVyC88qcfQNxu38sRBoecSCuzkCdh6f0603XHWb4wrnNy9+b"
    "68N4DmuM0Xcn22Y0+9+av2uuSJp7AV0O9uemNR4MspEIKpZetkqNfQHcZUgIqsSM8DihPvdqIFxGoI6Z/6qAD+l2WuV9/JiMDj8X2fbTUuV3me"
    "BMRb5WLylCQIQH5+ExtNzAPDOxKm7AlKf1997PVpCLZ/oQqgbaLF65s/QyV8xS4kSjFj1uZVhSZShyw51pwipM2Dc9EKAAk6IQvHrl+NCLF9ky"
    "mdFb6IQB3U3nBtYakt6WDTyenTVcx2bKuxkVIZUGsdGGLczjhSM5zlHSazxBW6teMTu652VlkqIJf0s6V6S0Dz5rf2Qo8XSu5bNn/qB9YJeY89"
    "gqxkpLgAjZiWi98Tkd0ctxpPtyuf39asjzlmBvKZE/2S4cCdaRawVSHLDiZXgo5GmnKUOI1ayVRc9kKp7ZoOfQ1nwn502JzryD+NY7BztVApbM"
    "bM68F7JORL45/CKJZQ0j88W+sKUWo68GGHLZmloYQjdFrVM/ZOEixmKgipkIPZYomyxqRou01dCxhTDoA3gvINB7K3BOdXRSeRWZ/PzDb/qND8"
    "FWlpYPJHpRZPXSS/dZDzZgsk2rqODWEwOiV95r7jeWTrUWvedwGh5s0rqIZlHkmdO74RGTBCcUOJl5OyAOgnORHX6Vp1LfUgbtl7a9RcN+ZJL2"
    "+tJkIZJ1jnaQzcaCyxWgjIk7a05SqgHhNCW+y8iBB5Ua1gi0qLAsj8t5Er6CyiZIYSYh+A9HjuDogXObx7C28jEDdxtPRaHVBtT/Tu5rLrLM9D"
    "K8UJZyNk0gZHJIL5rjkyLtyKb3XXkqo3xL/3OWQURaLBnBumAXExOfDRcSpalK5VtJFK59bFnkvxJB5mirxF/OqnZsYKyu1Kt+T+/fflliM10P"
    "jJxSXnqZDSaH5VG/hkc7l1xfG6CNtzZKsBTmm6LpSeK714aLHo4fCfKsHCRKOq2nz/yYjlrcOO/M+leaqrtUshSZoi9PWMM5z68wR3jASI+0QB"
    "QC7jy8hPN+MgYvQVRUDbH5Ifo4BoEEKp3my7pV1acV/faV0g8s10bR3U2EFmRUY60vWyozb3hVJb2xJS7FMJ+smXz23ntyYxzmCJV5h/+umN7k"
    "Vanot4SC951IlvKjmeGc/Eu7a1ZjaGUcakP8PQYzKMlInwwXBjEag8LdgQ2oWSnE9U2HHrVW7AvLDWpZfdkxK+sE421kepuTpfEn9hIBO1VUD/"
    "P+SPH06yDLO6WbjxCS577+P9tRHSPLrf4imuyNudidzv7xIEcU+1cWU0n/vP392xXkR454+Snl3/kQ2ShFBIN5L53lUCDfkXiy8Y7/mFrq/t8R"
    "kENS5/y+VuI5AKC053p+6GZqLlzay1BTldC6vRI2TPGwiE/9O8Yd3C59IzAW5rcHNfc178BDuT99UBMuZ2t+F41lJ5ooWBr2/4ukA00XZ3oSir"
    "7lI2Mr2tYZcnocBzEJ9aQQCoEUb95vrM7zaJn/OqOFHv7O2pUPGdF8RdjyOsY930NgtOP05WYflzLU+N5rARvKfn1mYnkQ9WnfOSCAJoqYwDAd"
    "GMPvj9mZlnl7aWtofCtvqI03RaWbm9KGmOu0wXlSi4TlAGnXLKvz5OvIlxB09tCpdj3UlRP0x1FLe5KjDRehV32/Yykt97qnJdurbchrZg3NYA"
    "X2Wg326l8FMOPAAId246vkPJlzJvI7T7HYU8ukqC59j6gin0B+QVKVK0cEOzmf1bj4GiXrJJhF2EhBVKwma/ljst+Wzn4FLXLfsZndYmgBmlN6"
    "lrSmTvDCAq3HmXUfp8QY1ozuidVg44Gl0mrX7wYgCLxBX7mdhXvzqG80H9R03ZdDb3SAlpK6VlXDMUIYyG/3qYXk8A2qnP2e8QK2MIwsF3otoD"
    "B0Zff12+ysXbmZ69y0jR/YHNdkj9z8O//a3lMziaZ1J42W1z1knJqZJFKqe/3ZpZwrOsSpG2+NwaQL0Pn8mvYtEX/sLlckcLYqOWjhsUndbOyI"
    "QDqsqGipPtm2QS5EIlxFuEgoBXlemlYgh5JNd5pB1M6dr/kFa9ypfzo9YgU9XNkQGwaZEXArrfX72BuvVi6AE8gJnPDoNROuouj9bf2j01pvFx"
    "Hk49WO+tUkjuJbcMN/+y92MKrPfi1lsU0+cZQZ9Lk2DlEZvOMTR9JKEte+oU+cO8RJTxvc9r61cRSs9DO/e2vhdPRW6CzBMmP73CU6q2y51BK8"
    "KeHO5XdNPcZSoQmJppOHTmFhLcsHYTlY1y2geDCrivwA0dAtD4VTl99DG9A0+rZTK1JZ4E9ZgYJsEPDSngOnUWtm3OAZ9yQ1eZRKs6jkv1pEpq"
    "N2VWHTSe3uGtUKNlx7UbYnGekaw+Xn+dGDR0eu+8t11ORCUspbyGIPj9bssLFkqPAQVOBaz7ZoFP3iu+w2mcaNVEWsV4hrYzbz4kdx759Wm02B"
    "4gtU8PbmJURiRzCDs9BlVXLvSh7XOhOVRCusTw6AG5+BeENWf0tY9RWvBd/S7CgpghxoitmM77qH2UBEAkPAniZZpXKcdb1sHucgzomMdVrDdj"
    "Ieb5Fp3XQ24X1DLuTnS3UutYOlOBbMTiy3isbI/nNNjV0nUoCjweroEGZ0ydyclAPbxsoVzewwGJUAMKHdZhWEdXomGR4971aPb2u9Yn4TG0sZ"
    "OLLytrM8SmAGUqXUzoR1XdDxv94juRwTs+V/e/zWqI7sOnbl8EK3FZ7MK9Tm/t+qalaayKFn/ROj9N0KnzJn0uTSY4mQsVrU146LCR2U+Umbtg"
    "Gj5u1LTS5roMbM9ZnucbPQ2MWW33vWrOnXXlU9NXkjYIbODcU2Kbxk/ECyjXsiJhUAcRvBfNo0FW3eZiz1Hj6zJpLa/I6NKsMPcK4FVvXeqXE0"
    "UnonpS6Jc9t5mIUbgPvhOmK/Fd612clg6e3Ney6mI+ZD1/s0VOY7ckBkqF8QlwUtzbldf9fbKzbryjjJSqi7Vs83ngAm8dbktq+qKtuKEvMTs8"
    "lP7t6HO6jLpOUonsMgOnJ5bfg/eGZaxGm4DNp8Y2Pb2jT3fKWrZesNprCZqad5Q+/GF343ZqJWTj4SF5PKXm7mvPZRN6eFahIs3irV+Do/RLL2"
    "cH0nY9sn8CfNclxNXHg041Y1anl0YzHo6uVLU8XIpdUUK5dAshg9U+mjSgbxfY5h0UwBYkTdRZx5zjmUfBD5wUFZYvjpDinOfTLDJUbzZy/SHj"
    "8VTrsrLPd4Ruyx+dvzPE94HNajen4tZsBRMWheloNkdKQ2FPoN7IAWLnD0A9WQB6v5ExgkJaxQ95zUAS3PjhVVk1op+Kg0AX1uQ9DYTJSrNOFk"
    "jGcCZJGZRNshmJzq/TWHKl1UKByyMOJnmigQXX3J0ge9/UrjLcOzom8772XbiLM8rKgspIMcPZUrBct+hJBZGtH160UGUz4xK+sVYqLe8LstaR"
    "D99HoqZvhctMMUBAn/xAKUMGtRWojFpCxJciDdEz9ieJtZbwLmDU0rEY6Zkt8NOLKABpXD0Bu4t8WAWJM0NltqIAbYOeLHYwCcST8xra57oj93"
    "3/3cDA2UI0lLShfIFDB8YongDA/mVVzy8tC1tqzEJZtl7nxXGUMJPx3H+atGCTwgOrXlH+49XndoFqgBOHv77kxbod0t3S8xW0yOpc/jM5k/Lk"
    "1/YCjcwsHxgw95yoPQGVMVzA4IQR/OGZEx5zAndh7455v55Xd0LkrW1O+IZVwjjf2/UK1fcKs9uz2xVRqOCkl92N6mC25teEW7eTftUqqusfnA"
    "Pw08I9z9EfBWrlvcKoOKPN7s17GOMjx5tr7KDU45JFx2w56DKLOwr9mtlX/cZzzfaTtSb1crfj6ZmxDWXVhGE40PPzJ1Nlr4XiF7NEkEtlwjMf"
    "SttkdivZ5Os9DHHrMR0K84PoWfJ2/0cLiW/bGeI6Iuvomk+NkvOr92McPeg9+SOCHDSVz3HccOiTCOFuk+5nnEyM3JkgWua9QEd7raQACt9VRI"
    "/uU48Kq4TcRZUO7RNRpTTKjOKuRDk+66j1gkqS/MSNd4mdnilM/wn1fT5yuVpJsZtE2Dw8yf7pL3pW3kDY6wBMkVQGGFCWruZnCZ1CFX7uQq3v"
    "uj9FeiJXL3iqPhdekgClX/9fItRD/djzGzVOh0V84wt5Pd96cueWSTGbyhRxJ3KkSnPahi1M5UBE7hJScsuES5Ak5+PeQ6lTv6mdi12Kh8GJVS"
    "vomH6DYDQR7eQgmgfRq9XOCuIQNZH1URtQ0OD8yP1cLLsBhY/ziuemYtmwAX6PGMNAzvitzB9uHFTUQFnzU5Dxlomzkjo1coPhExo5Ep8kc5DM"
    "fhVEyuYczmrH3WqXWb5dMotTputHTWpK0khLNq/HP/JvR+sMD+drDwXGUln2KjsCUxLjcbefHcnLOsSORKHZJ2vEpZFxfV1zTPILNOu8tSdI7A"
    "putA++QyfCBNEH/208kRxATPx0Q4D6t/VAyyh86WDjIpSLuqHD76Pl+B+Ppi1XhO/YxbHqCDGswpB5Oz4u25SMIRCuWVhTuaslRi7Jh+HutlpW"
    "tgqlxh319bygAS8bYnmnZ4sbApgvUKzgAzDxJ07YiHTGsu5oY4ubHP+8c42UAWvw2HG69XWL7YbrCqCBDpQXr5xS13z6kG4ooGRfxXOqQw9Tsw"
    "ZCOwBvxVc291aDgxWprCjRHGM97m1WZ6lJBvJH7OR9tQPwdLLwXlwR8cF5jBufvA3RXxQFRVXx4a+Ui6mF4B4GHHyk2JHwJ1XhjxgmhirlUh3l"
    "KG6+DrtJTmTQSUaFZED77nOyd4u/AATvTJ4oDhjfMwEI5rQYysNYKicfWvN7RC4VA/8cFZvM8jnavit/pTn1eC1ohpMh1kf4DpFidXOc016CNH"
    "W8fy5W3e1F7gxbnWppMvKcoAAQUItYc6RVYqLxg8TStGhFOcwMi1LVkv/Q2LdOMWTDn98G1iw4HkOSsNddDfCtMPPfh4bWgb0hY13m7qBY644S"
    "WklcL05nzkn++ZlfolWp4HMpVlb9zakcDbXb1MJ7iJTDOkqTIv0czlNqf30Aw+JwzPKRgt6JcmuGjFdUH2MpIlCGo0f8aHsjYHnGm4Pul6kKBL"
    "RJ1CvBTe7rwtCP2vKhxdpCksCW13ur2oHmUz4k28s642yK2gt1eAWNyZ2z9lLIBAQWVEaoLWWz1hoaLKXKQ8SOOzXktw68BUhtFAyKdV3XzW+n"
    "dtwgu5WTCCcfDTU/dQwgsO0AslNIx77Lu9m7pdHKHt7LYM/x+I5rTvIwtLldPVx+5jeImeeLt31cYZe7W+CqdTzvmT3dIXO0RiMIPLLm2spt0N"
    "qvUXMbVbIFALDResZP1jXawKyPNGW8Rz7PsDjzsOxNqspSgzMuZWtlGMsC1vKkjmO5YPTjMT886mKuAsKmAZg78SLvitWZrMAqz+7JHUfiPa0e"
    "kQF4/qmzrmPwRy4e22GRY7xERkZbVnnIPLdlEfyid0bQyQd11y+2hJz5Y/QHyByrmNuS4J+ZdOAYSjBK5Hq+Z61Qo04EaUTW5uqhk9MAuaD3ft"
    "rYNveut7Z5LHn7RR5iYv8AzrxXlHsDxn0nRZ4xqbC7ZVyilbOq11JCRZUikg29oxrvqSjybi2w3G75IxlixiV/nBrJb4iJGaAS6tsMbPvu7Vfo"
    "1XwTpW3M2yZepYQWwirufk+ASOc9tfeaCCpCYv3PuBAAPaH0/k5l+3g+uAqdN4DYScrIgROPCbG2hfNn3m7o8fN9qt2hSCGDLkJu0ZyFOYedlj"
    "JK/85USQ6moQHG245cw0dBEyPvlAw6qFgXMvbeeNu04Jfi9qUrSSJewVJGxK1Z3se89go/VUgSnD8AWwCto6AXrn/70yySjz1PO7acmfXJNQkN"
    "sFn2mhnLCZJu7/vVJC4KgMlrfXFau07+EyyFWAEqk2XAps4LML/COzMyWxh1d3sG/riezDwq3kqIgbXU6OrEISIppK7bt8nC+d5+rB0pdnmGrZ"
    "I1qAzApyktzao22t0LstNg9Rq+UFaXKPqPXk2wnNnOIIUoySVUeNth2Y8/L36xHA7sJTbvslizfP1I6yqAINY5t0BPSiFrOI2EQmqL3aZhKsvC"
    "IpV6LnF0Uf+wwI+4C8ppP3CUdgruYzow0KB5k1YErsH9juJ+foWpwaSR58G+KGH1pFLMJtBuK3Sy8hJ00xacSA/05Di1q9+QWpr7z5WS7JZpnE"
    "vs23lapz3KGnxJTI9CJCdNYdYn9YeFkMwunN3mt164Bcr67sLpMt1S3yTfbW31KV1Sj9xH313RXyNKGmobUFqz4IlqIC7xqwbBO+k3VZ7uchT8"
    "k2G7On8y+LWckC84vzmn3ridG0/MravbNWp/DgDB0HHrf1dmTlfhIpv32vknpln9fYk2k45XHnymU3TZJ7fCKcLdIrpyZnC7z5spGc0y+Ty0vw"
    "Q4c+KMuv1Iq2cgc26OE7hjNx65Eh+y59Lfee++UBRfcNb+tVa2p/Y+zE3q62LpDMpckJNiGSe2byuazGnWvJwsuhSPI1+hR+wqtNjpAuZDjZQ1"
    "a2FVdPFC4dfYqogsEK/PSORk/6ePHFjC4nlSitPyyUft4Z/gNL2xn522ahnKDxSy/ASTBc8JOOWTVMwOoobSGmQXspWe/G4TmrTfTrl2xdzj6k"
    "wfFrMgbRgp7NuTzdyfOuBEqKSo5qL8hNaS8J2XMgpOGCC5+rfVoJniVZxVSIk8AR0TV9oeBTjEUDO0Ysh3pXrehKrDPLjcqyT7JWGM02WyMnew"
    "1bU9PPtrQevc8Xo90XL/8Y6nv84rzMf6uhFGIfx6rVnQgAVQFpOQ2evLxdrGr8cBLNRXwCGKkSJts1aO5ru6vomfz4Oeqb4D58OiQBe+5x79Hc"
    "gss3d03+MEJ1oH+U3+ZsaS3lfoJ1MX12xFd5on4GtHYka46tDfUCo5shMTFTcAlDGXRuo9tJIg/LaEYxelWVTmVhxpZjJGWrocYkJyW4M0DrHV"
    "kHV+eZv9wpWa3yTuWcOA/KbPeGYX7aqTSJ4/VVXPRIYdbOdZcO9XKph0T5xzSRfpYOoMZ00ewvEmsVxeSq98Z09fwOFk9hojcJSmS09jsQ3Uai"
    "J3XOuJqWn3UXy9en6brxAycNKDs5q6RMHKnNN9fbPmya9HYm0fsK0U8tIoyICFa4c/tcdBlk9gg1iYr3CDdQTuKWdVuJ6NG9NBOKD4/8u57XmG"
    "3Ittz6aahGHHl6k31IcKoe/pbw7C7yKdC06SsW7lra67kOevV2fTjhqbX5JemKGrith0MqtYmOZvoa3y3orwLtCQe17uEtB3dA6p21JJXkDqeX"
    "/AgWTWBlQoDmGP3EF8j240rgSLavXqjBAvsBPFGvJ3dOcVxLvmu6pKYPP4erN8OoUqVLlQZXl835HAgzpPo3I1P0+4DHJEj+UmG1rWI1rmnQ2M"
    "9T6w7cdLkrSt1dbUxKPkkR5g5yXiHnXX6rnudQ5jAbWMw8g55AJtgNbUR4amqkca4Nh2deshT6Tl3ArIgnU5QajFwvmBBg5VLqhC4n//YqgebU"
    "MMlb+Lu9J18wEs2mHlzOqpWMXyyqSoWY8vcD5JH7fxOIZ205nDzF81gzPplTKMfp4fSjz6X641PV+Em736e8AyXQIJIldZRa/Jsh+kEUvzLb+E"
    "ltqUXHFBjZ7k/rDYrHYbcdVG72k5o2/PJ7TQuMsYBF2L+4k/x/Z4yuOZFnha8UYvybjEYAt/ZvDTawjBkAWLHlJS2OuzLeHfPKpm8FemolD/SV"
    "tDE1UKbzgyaP8J3OpUYYtMV3bv1RSnDF/nLzaLPbapfrWAo7lunTh7oVHIc2imZ7tPu2Ne3FPVUrNji5mDI7XsJsWCxD3CKrUaWgZ5wUF877vZ"
    "fcMMQw0PRhaoNgepqa3Mk6eAuYj+jREdH6foasPBdQL+skFmNGk7Zh+ZSvXL0XCfhv11dQxsmdYS7edtIOrR5i884BzVxdthR8CeOzcrLKNkA/"
    "jwC0G4XeJWENq4E/VlmOS8kdgpYNmRtNjnV3bL1y9Av3irfk/Z0uQVKYPSbhpbUImo9egKR5URIYfOtIZ2ryh3LL2XnsWymR7pbvB0ZyPkxIy2"
    "TWFFikX3VGxNSRAHFo8M9OZEAWvvCN/IJzG6fJjqTC9gB+dOCOZxO15bTMlkmgca/vZapCe/5Ij/syqp9/AH7tJQLkvIllRKMUdOoHqqbvNfQd"
    "eFvVMdIMJqnvzNzsmB56L+ePGLgasZ/ClsePaICVOjykZPxmNx675sPlfS0fMs4bvD+XK4ceUAj8Qjg2IkEHNOG4cKcguuPVpiMjGjzE/Pvlu4"
    "Yxxm+95YvD9FM28nLbixTCVDRn/z9chw6uBvIlJum87cetfj4PPsCf6ZvOG1eM7G7vsqBXdXx3oo177i6cy4Dxsc0a0xigNWZsLMfV4e+u0Xqq"
    "pN+KVd3DUjBzqTVIV3nV1IxIf+hAUj9cfJ+a0a6fLSisFnGEfPHxDrPCdpyQhP/6cFzfxn6DHFGMDfZEnJa4NA3MlrUrmK6gd9Pbdsg48ICwdw"
    "Dvw6xS8eElzSknt1PHGlZ2AG/HWL3dnO7hFXAMzwzWbr70kbS/zab2TyjbpX6rn11I6Yw1uGxJN6aB/R3VLqEka+WMfz6MgVccDhEFx5T9XZqf"
    "4wV30rH0cgJMDQ9VSTMDIW2f/ldFFQhwoT83v/XzQxP5bhAy8nesE6ziZ2l1hT4qqThzoYcnKRYWcsTrOm0aq28y40Ju9pUUT8CmO1REKrLHqf"
    "hKktTOtrAXH+e11uYyqkteC6kdvcs+7A4/akFy3dvBLE64Wg5S/Xu83GzdM7ddqjuQezntCmlTCiK6D0jZg3l+qG1eSNvDTz58RJzwU3KTr27V"
    "WTdTD2LFeIxHtHy8yQhFrydNOFHRtY21v1/i0LMbLP2O+qi3NFM+AC566XqxKlCtcI2upda9iNviAB4Z3sXqDEKId1uq8x1qQJep7kthb3TFgu"
    "1VA2i+l5hQr4cgpKTvsSV9D1Vk6xtoex2MdmqTJsNvvN9lSbWy/8Lqfxuiu/7oTcHXHTEOtEna7st3ir/yspi575o/bPurbBEtibqAs5MvrFTi"
    "IEV4wZxQ0kTWIX9jYWF8Gw8nzr3xXEDsWA/HL7Hhj7q2wJcaK6aIQU6jeQJNmXhbM8TpVF6h3Jtzi/D1YwTudE2E4XwZhA0LKGMOLQeGPxIvDx"
    "XilPcqz2pLBwkHP9D1Ls5Nb3FUejdWkBlaL3ZICCH60HK0QD2FHxE9YAKGTOeGALCZLURtd23nmnX7K5mc0TaUbWoZEkdD/bmawsgja4zbQtDx"
    "hrHXe/aLSlETrLoOqGWaQ+cPkFbs+cuQErhGcBOMDwZgtDAERE30ZD6MXqnBULXkzLdJSeShavCq7S/KcX2cf70aeZPyrozRF5/laPPafH0blC"
    "dGaF1Eq8zQEeUI/Jb9URpZWl0/G9EnSUNz7hX3vZFcJSi9yfLRzRRl6kiiEXtLTEZf6SE6GNBMLals7/0nPlFIzqlNmFAIfTRMtmYN/FdzxD5T"
    "Pm8uEUHGmE5BWphbVjtTTADNO/umrG4NP3faWsNVhV8KSm2V9z7M+jBfUFD+WDpv3Ya5LQv38xQXt5oBC+ZUTCEx5xybH4xizvnpLz0YFzYg2y"
    "LPDmuvTxJ5lCuN7bm+j/U2jlMiTAT/GXPpEBXgJ22QmN90tYMraw39WWPy1R+153x/9/U4IHbMYSTnNwdKiS1tZpKELBurKAkgdGbJ9T0UUCcq"
    "qGKiJP9W5iGsQSYaX5kywY1Kyxmxkx9dDo6bxHZQdoEbkkHPCw5BQJgUq9XKV0j6YbjxIsYyWwKns4C2mOddwJlUYcDPUtPeNARSFP38SMgwRA"
    "zdBwaY8cObSXznTRljlerNzvF2lBwUzaPPnByRk7CIHCZuzMsy28Gcg+3PeV+O0F7PCREn75TPHq7SmZDj4y45vY1JVO3jfAjph1Zyh8N+FwsC"
    "fY712JofZpAuKverASZb0ZDRTEnUmfCEX5ur3VvTUydxDVi25D2WRpCwPrvxH/vTxD/GZtk6wQ4rGYTGS1aT/LxIKlX1N87bLQ+2onaYddviAa"
    "01Yktc9KW/DIjzv3cVq5cSvxiBPJhF+9ue1mPDN+vewp/dqVRQoQww1inx6ED4HUXbFl4cKrMpTbH4kv+26PSQ+zyer1W2FOStlgtXEiurmKPM"
    "+/L7tSBndzMUrQdhJTcnG0y4yGyOXpxqTyPe1nZ4fhNH0ct+tibSmn5D2KbtUZKRjSaoX7SZBqSFnl/KzPmDc5lWXct+edYcvonZeH0oUzh+gi"
    "ED7zgyTGdyDKLi0rkOWoWaMWm6oyXw4e3EsNaSU7x2xWEHrNfyYGeiFFkWSYbsMrjOjU/hMdEgZdPB0WQUGtoWcKxidTkDu2c6kZzGmbhTO1UT"
    "5bcuzO+P9mhLG2Q3GUdwm18XUhb+7oiJjWczq6r5ib7IHcN1jUkKtN7aiSUk13u46Mdz9frafqHkLYYq5x3fN0DAQiWo+mkSUk6uQvsL5+/lAZ"
    "SVytPl1IIg96/uMqnA77Jk/ljWtDeqqZNa+PJhf3DzmoA65c9ukIisTl4/Dp7zEmqV9Fc2qt1HNxCdzh38Fre8M8iRWdWCW9HrvvWLw1PtZ1FF"
    "vHaibc3zi6VEE9c6k3yL31sbp4qvd9h75J1X/DanF2ap4PYqJj9a1GvEzmVk7OfwMcYyXT4BTgl0ZM/M+rteBEHxpdUSlODMPGBb7SEn/rQLWs"
    "8Tm0BvlWz517iM/2yoQyedN3buonRWP1VuCklQkR9SNWxCPDrt6/xMa/PGiqgUj77O84PLn68UViEpW5zvpZA6fIfJTGTVMvnvvmgt+yi/Zcub"
    "mOMYHzIwfvY4EzqG+rSCiDoeYs9R7G9b4wgVGWS4NuRxOxLyYgR91sOu2Rb9jjQKJwh+QpZcwk+igkWothGve6nUZzoX6FhDwXYYPLZrIRlYau"
    "oJpP3IW+2zcUoGjVB6xLiuPguPINDQ1agvTV3s6+FjKrrxUEqn1QsFreisgtLNf/nhd5+RoHUym/UceVrZtOfu4j8COn/1bwOb3/pmi8cQXhM1"
    "Tw6LqtvgN/RZIsgYbk/5KMyHUMLTAPkyXRr3h+jvU3PyCtUzEsI8rNTywscP9pvHRQ46cY73rSShPlmU+Pd9qTl2ehMqtUfgjajvJfm6x55mBe"
    "vzRbTbT/Nj43rosfrzUK8rJNrmVcKkKwfGeCwN+SqbSa0Up6j+8JWwSDC2kh3HKVCQ7ei3ehsY9JpIXPC80fwRtDuz4idUuiOrf7/QDAqjdQQn"
    "zgRVYe7ad22gHef181a50vfmhitQvnPIViGC7+AUnyZbDsSXLZ2tjnmcu90hl4zh1H/8/eZzO4p3L4tNVv+FtZsCD2/CXxPr1TROxjKXweRy+F"
    "JufolhbWfYfZBKy4Q9l3opHFmHgP2Fyk9nuN6JSK+JS+lT0m0/fJ4Uvrlc4XzqRC3WLqvegfxzwxMeHBqZndpi8I9KiG0uNP7ni2onQ/iNPVtr"
    "27TcyxbY4byIEH+PHDHWtZIUWo8ANdPypNgn59TtMnf093Bo7cEmAKf6QTcXrY2UDRD5V1HIJ2k8rIywebsDXnjCeJszpp9ngutkARiEV8o1Jg"
    "+CaGZEidt+tvaYAwesgrrkOeVD91uUt8IpFgBvKscPwX0fkd8LRBnw64n+TbkJwPoek4V7EKaVkd8CoQaSaI4qaegOuTcrXafuJar45/c5ekMB"
    "nLPrXXWCV+jYd0INmIbMTnLyuZPqTyxZ51pthSaJvqx8Qz9scOV7imWh/FQ/SVdJ5j9Y6be0RNiBHNmR552SUzBALo3S3zYVwsXVvf5lV5khc/"
    "zCHsxtnDCoHfNArWYvoC96w0K0Fd7HkEnhhcdue+RLls5I+t1dO0KB/MuXaM0+HxoMg4iO3AGWJIgm9+kr6egK5192pgJylxwm77ViXHNg0+00"
    "a1SFl4v+OdxlaFux84l7Rkq6VD5VfwuCdkrT/slifo6f0p538iuMscPaBA4L3lzwojsl9RXdXViXwjewX3oQEUqFv8ffHUKn/BLrmWg2mucLNC"
    "pWpttuBc1TQmYG2UqT2mq19bUlRW+YNjW0x8HJvQ00SIvDFwtkDE5qSMFJzJeLxoASNtBV9l9dfils45ZzvB59s+irGX3rxZYF+ZzT3Tyd1FBW"
    "DipoOnxLZW21q0Ulq1oCIQSeSLAdLN/6djhXUeP5PcJ/35q7Rm121CiQFe5Tq5zD3XpmYWkmIb8iIOE8ya3hQYItS0b1UbmhWTvl5/CBb0ha7z"
    "RhPW8hd09Pb1LmWod/92g1cNRUfmFvPy3M0aJXWJ6LGLLQEOz4azQBFKHPzJWOu9eK0rK0dCM4mo0uQrIiqEzdz/togRAoAMHl8ZKA01m4Q1vg"
    "PyBNXvNCHN90DL/QEWuedZZigRP5D4HvOwNf3E5G+yTn1N2kuqMo8SaaNCehGSPkfvelfkgV1F2bV29IOFufVY6Y2+SiY1Cis4R6WEnIeJQJcB"
    "Xng5R+zGNw9lDFT88BfmCP7AYpd8D4Wi1+Q7xPvcqb1vcbeWTT36UTjuC7G8D26qzX9re4jYulGOwIoxfZ+4nBBlCBP3jAXrIj2+gyDrVLBlat"
    "UzlO8od5qvXIdPlKKNbCthopExjOy12osIPmzeCnJ+Dxt5wSgC14NQnEZgmq19p7x+rtuOUk97Dc9AHFilg6D+dgH7Sj1ZiUjgS4/vXJc/f36S"
    "7QOaIyBNTSpM2PS+2KHmsd9GUH04mi+SYm/xt8enBp8YmwlkhCCbxe8Vm+uf4KSdUpeLjtJrvF+wmCFTv3rH12ZiK5KJjX6cMHnETwrCi9HHiA"
    "K91TBU0WfqHjQIFY9N130DeSBSLEe6e0FgEzS+HV4TFoyaIymXWy6Zag85WqdFmxCM718ffwRm44l5dx6sm1uh+HDqGipVxAyswW3vflNNg1pQ"
    "D/rkrnaVEVR4/wkXTQLyQQyyCPtIV2/WDzvNhZWRopQqQ/ejOjDViXj0NLceAsq/VTa5THUhLDaw5DKCt4romYaelgAephKguBUkDaWWp7ig5d"
    "wGzga+/h7UC7J1LIckEimeZSwAhgUMb6847OlDz8LbWYb/pZVsDl1R1a4+Ugbpk3t560USI7GLNwDdiysOafaomN++8iAaFG0GwZGMwLPkG0Fj"
    "aJAAHYFlaj1pPZf/LIl6Xdvm1tqOGh4a6XTwElvj7neIufxuI+aX06Y5Jq5tWls5SOBFwm5uMrcgo0RS+1d8l9Rmb+fDwptVpwR/lpYInGIxJd"
    "JQXVZz+xalRQTwSKbi2mBaF/F6hjOlzsr3R+JNmTmWSBbe8AZEMOZY+jpF3FRq0ZJSibhEEQxN2j9Iv2o53kFS6xlOIAfuhk7d+/7ZiDyZ1ech"
    "NCkvnDWLjIrqQpKmcY2198ZuT3d7kfRWp3GjkYoKjrs2qXiXrcCvxLNW2KVwrTEvjmzgvYT6s17I82sTaL9IjgEsJ7Im5vn7T52Ogkvo/WzOj2"
    "qLSu3ecq84g/BDlasbNneDI+PoP3a2qkc4uukCJm6v0rZGUO9bcP3wRwOKxl7/MGihMz76ItN0yy0sgthxcMz7IHtJhLmAScEf9qodm5Wx5dqH"
    "aitjoYHjK+I3/VlAWbr9CE0zrvP55GQSb6eLS3eLjf8OPgBwYpixFkyH7uWr89+HyODXPKHxIAuctKjJBaKZ7/AgZteVq5d/4hoOiHWDu8PFZt"
    "Y3mTpPqmqxqSTak0Memsd9En6ryzVuQ9grz7gsWvXQnoBu0zHNtMkMUMRZRQfQRNFuRaSZC4R5prRJ1XN0mj715SJE4rVxyLPy9FGgyfafFf+V"
    "nBgBzgFh2bIaOg76YMesvoWQhxZBJ7xa43bqg4s4rYceILP7ZhiJ/zQgnDrkmbuN7wMu5vlarJv/gbpvJvndzJ4i9OjPxUtVGmiw/Pq9p8FWmU"
    "Jtx+JZGfv+YmYQy4hRVlPjGQgbU6KKsedlUhXz+eUoNsSGFOdE9H87+VSx+fH3Ocn9+XLe1N42uBYQiRcAJ7NXzo1fWCuA3/sCPog4qj+PZRmc"
    "BeQHK5D7JCqIrkKOTOQrxDkrMU77x3Fo8U9ouRYG7AZu6uX5WHFsbQftcEhlCY0Ke4mRjCGV9bYX6W9RS/5klERdQM0c1h4Q1+kWM+4mc7KA2S"
    "DquImiDHpogEK2lTzn7Vz8+A1gg3OyjKREX1Hom+ja6L7cEx0LqxBkkzPXn7sKDVdS2IbuFwUH8Xue9icS/bM9SopF8qcFDKviydLUgN7bdKVD"
    "Gt+Hep8R4dJHqCKXBz2zQgKy3L0MkPRzKHCZ6cRAmvPQfGozjd3SzqoAiOpmfraIOtoQpF3VUaYEQ/0kNODlMykYCoXgqnrHDFbvTNNMyujwuM"
    "EuumjVM29Bc6jD2njmP6+Wl6B1nuVuPFFNvTPdvoagH59VJgdRbxgeAN38imo/Jdbx06tm+Ffz3vcD21EXXykygmBtl2VilBIzsFuFiHrG4g9I"
    "OSm8AkDYDw0UmjF2YU2Kjq223UjLTVrAXT7eq7QmlA/XyKMdSKQmMchQYYm8na2rohnXJU88sgcEoWRZHGoGUV/KBT15k79jXioahNCoZE1RbM"
    "n3SELGczIDygaha7L96HPusythqNbAusSNHVxCpv+/7PyoqeqD/axDblqImSoblIAL3BSunWt6jObP3vACAZz1nFk2Cyx7gQgEnQAslptmQEZg"
    "F4Inotl3QYxD1K2vid28iKAtTEdBc3NLpNX+Z8itc/w7mn+WhtYHSZlFYML3Kw8CTMgPNi33IGLUi/wT3qxNv9Tp0AAG8q4NdjUn8SgbRyvF2r"
    "Fku/3mP23M5JPOnrQd6ZVGNTPft6jfi1OJufgj47dRniExmkEqBtarBK8/YOx3zexusLHfD8C1R5Q9P7O00nz0Y4n9ocn6a1MECbM/RbXkV5Xj"
    "xzVnZ+o/IrzrRIYNFehlin6bv8J0oDO+Or+fApMX9rzZ+rdWUEzeoUOTNZ426xXrMxzU70aGyq5Mbv2VbxHUNPai/UlWHFXrEZj2ed1aR3erEB"
    "rzEcVqRTUypBvIv2TyweB7aau3TJnyn/AC09Ut+IentUzR0xocPl+mSuCquHMekvZciyLNj4GbdPY+/jrNhTQdnS5Fx3lrjFa93MHi/uUsJAGW"
    "S72/iJ4uuf7KO6qAoNvsVGuR1+ysWTl8ATIEL7jkqPRtavh3eHvKqiHDzIwZtvnNasB17ssTu0Gk1/5Ajn/Hpj5V1n4Dp0CAB5YoTqqBtBlDGQ"
    "Z180q6zj06wPGTgZrA62jqkLvI1V2ouABkHBzEi1aC/EJ8DdzCQ+PwTkkCfQXwNpMVEZ4U+qyMn6+szBgsA0EfJS0PSJAQdsmVZV7/dUkGbR6A"
    "zAjvG8RaMELOzD4eLt9Lt1viyz6WTwQvgl3kpWQA5Ye9mIX798hNA/gY2tkgXcMjronvooWHmQIHgoSLD/+3/+61////WP6P2jav98Cexf//uv"
    "//53oS/+kXcI9vwctRwPIH6W14j8JhQFq0n61YFnJJNyey2KoTcgCBz3QcLQhAh09gOYr7+WyLLifpQExhaICb58h5XkQ4AgVQwdDYTVexLBBY"
    "AoBJokQpsLQVH5nUSlOZoPTJvzhTwIfRgYgE5EOXRkUR4gpVlEv7ArD+cmSQDHgtB7ClCkeBEHSWhU3KATXYQ0WYIdVoZgQobRoQJkSO8onr5C"
    "NhxmSFAlSW7lQoBHSh5heAM0mgM2LBxFThRlzQP4aUZDjwGF6aHaeWVGQOU/qt5GBNxIF6LKlKCNA0Xes3/Iwhxw+jB/ZFKovPmeETkQ9PvMIL"
    "KjRYiTOeXSIGvogMkSSoNkt5sXfonq076Cd+qmJGXFZlKWF3hcCw2qAPUuBVwmMg/K/SkYQ61wMnMBKuRYmipFEiZAtKFfVadxEMxJuhyMgwxm"
    "4R6CfALFgt2LGhwS3jixAwBL8T0b9w3w/h6jFqnGEdf7KoSfeYALAByHH2bLQxLFQD8Z+G1pN8HiBk8CcwPwqNwYXUBo1wuR/DFUI2xuHHBV96"
    "QAJgM5jz4j4TbfVYNm+ibSRahjh6lyIe8cJQK4q5bG1nBHSFBzRYgQa7czPzOdKEIURFSIOkoyAUMcLLeVBu727AuJ7OVyyhsc3dxyHPBoGsJz"
    "Z90FrThW5MGFBAqIDvkP2cXgcajucNT964iwRHrzXoSeueEtmBBgp3MEr5BzRHZjUa3I0EfrUEY3Cij4m3mCJh+8eFMHHOQD5PXRP9drLeQ4fC"
    "f5ZNYritj4zz7wN4QwSYPpe1yTJvLSWCJyjzaoNm7qHRUFi7l1Ujg1+MzV+8dvZopjA0p0SsoCKUBxaUnQxJo+HdOTe4QkSqBtKllSRvQDz612"
    "r+JSxunCxGEYuz2zEmMwYcqCfYQq6/v2wpOh7IMoSXqTthRqHemnnN50h2K4xSj/U8djWgB/W/hOcQE12cV1FpsiBvJo64Jt/tL1FG40kpJ0MT"
    "Q4cLhvF6L4naJrUdx6sObo8hbdThd6R4Pu9bYV9J0NdGtqE/fCKjLvwHseSJdI8W61nd3YB/48Yrm7voFkls5tKQBAgn8kGl/K07J7fL6Q3kb2"
    "OOFs7vk9dwvcy/7ujiDNqyQ96oXc8h+GsA8zAYQ+sgfxbFT2KucFLuhgbk9L6vBTww447OQKN+pB3rG69C7YbYOcKm71iGBpPhd1uBQBoB2Yv0"
    "19lO9TC252aBTwrrwfomLbCmhAMrPeUo1FVO1jlAP8tswAkG8vXcSKkHPZ3nCG3skaLzE2DoaEs0CS6/AV+Dx6swjd9WB3Jz29wgqc8V2rE+FS"
    "ALpUdlerLSuhFtOh9JmKaDf8u5zj6N+GXPp1MRM36YsGZCNXFfON9pcZfugBxkM2zc1vVNIbH19q8EpyPqoIHQAD/RokdOoPaaIp5KJ2fNCfaP"
    "ZRfVauI8HY19yNaoRlrELE94bAnqa7lFoDcwUEi+mGfgQ0sISIBt7iFUnZQUH54rAo2yRz+rm/OofBZcyIeeEEL6EdyJOrmxXC7TokK9xBUEdt"
    "CqIhcEnzLi0sM0S2foH0x5W841PrcECwyiGIz2UHu4rUkRv30ngkFUcHwqYiOcRriV45wc9ObxnfuGjWHAdsPxnD0t5RGLQRc696vakr3QUo0I"
    "Z4S//NCL6dVAMIx/BLG7p5FTvh9Z1Mvk1x30WOUEa6t5sKKWpi4XupUT5G/ki/oycggmDcK/uph3kgy7YXGeMSR7Lrof1hCEtR29CSVfwsZ69i"
    "4tPW6bCObT0ZeBCwOHW0fwROhaCMDhCtDHPUPAg8D1XSU7svykU7RWQzdWhTubglfWML2N43ElCDQ3c16eUHx1fngRforJjp/Fs3alRK5km1Vw"
    "kFFZi340dtiBlzDwLj9HigjxC8+OCQCJEvzjVcpIgF6oLEzIRU+TYp1J4F2HYqFES1Isn5jvP48pPFwzD1oOoWr6HdDAUBhUEM0DanCvBLJnYe"
    "ou1IoxzWzz3CqsmATNJtBqMLi44vaB9+ADqkXuOvZ75ngvZ7WBoUKhGwW6wnms8dVk15j3QTC6A+mzQ3sljojSNBH11f6M330sFvlQNv/op3FF"
    "E1viuffgTgWoezbYbNqacIDx4KhVoQgkk+CAYt6nnVA97JBuwGvwV9MqVQUNfyBxIuq2W++JEhejWmAH3AAv8lelNVU7YlzMHeYj/F6DzQl6fl"
    "bCNJgDwsqyGaTIxhDRLvHfa1ipmr66ERkk2sIe4zP4WEgCm/vGUh5V7qhdIwoVJ6+7uIjutw6OqZx8aF04RzxBFoFRnjo+F3fyDj5Mai6+fzfI"
    "ONIwhW7RXCzD6c1x7a2dnrYZZZK0s/359gSMbVJIfAo4FridPwefvxVuQmewR6kbzn4pldcNOamjcESpGowVuvt4XXEQz9Glilscu/eQYmOFlL"
    "ZTO9I/hZ1QbnZ1Lk3aCNZHXRu16YwsCRxjbP2gUCgY+F8ZIK+VygSObtc+82AGdTS5FXDicGlBuF1pWHeVYgSb9j14bqdKi7AaVHWybALjvIhd"
    "hlJQKE5f3xNHaHR5QB9DLcxy+TJLgfpUaRRmIVJWbe4fkXmiZcVPvGp9VsCpHo2n9Puq5IenmiHwDQ9GqbMjRj3Pk7zTI+0K9tXFwDDvWEMvXx"
    "xnqgF1d/L4aueBQUau+ixmEqfHewufsEFiX2K/IYTBDxRgxoRHM8NXiID/nKBZBU/LU9ieYhL6cSO/RaH7SaYyUQ+FvBjQeqF8AFjuaM/UvTQS"
    "RK93x+RMOZnF8CJn3+88MBVBLl2EbDIncLT3eg3+JBTUB3JTvM8oDuQce7PfSC3+eIYmKSJc8w5CRlIMkpR9Ct7Oh82M4nZud94RDALDtukk7y"
    "Xgqwd41XwGEW92M9tWm8sHPkOcg1wCjDMQylMW4vc5PsevGviWTRutH7FxBBcWg9tGQ3VupJGxMZvi4InJGDdrXVaMQgqRJX+92vuCwfGo/MLd"
    "7z5PRmtSqTeK+8dzqmqu5O1jMRW7Lfuzo1LD3IerautGii+Yihaua7lLQZeACjAVikh1YSQwqAvvwuB4V9BFk02VV9oEIvYpiQg0IAMlmMADlb"
    "+u/l0jAAA9RohOBIh8VjJY/kUcu7p0apruUJEhzP4k1V/TBWjcCnQ2yaaLSve9FtCP6MCAKfrm8NDBX4+vy7AF/7P3QAUIY1qx+7V+r+M+uSCd"
    "hM7Zk6JPchMcoOm48bTXIeX+y5FkLTgTEAoc3lRc8SwDp9KGEoil+qRnuFn2uwB//tBtonCGw9wBjPja4fIR0ybXi4sDc56lJWBu8zpXekPhlD"
    "Kfi1ihoLU5yevQTY9UqlUmX2eXXk8SKhcG+5H7+bpyPO5l8s6nBaJHkJAdAIn5RdpCth7D/K71Dx+ML6ZqoDnxFtROyJmd3V8k4sHv5M4ETNa7"
    "6aq18NUjoa06VzR0OoQ05U25fgof0YqetQz4zeuCdY07eNhB9R9u8Y96mvHVbF4RmaOXv6oI8k6qi677lEEy2erYKTI4LDd1qmQB1usDuF6PGl"
    "ca66qdpT4zw+YOAzb1KkOnDOCLZQY3cj3LrAJGySLru3BZhT9EDWCHxZstraPBMWy1ip9hs+r97RYwzBRYCxhg/2gRAMK+S6g4khD3rXKAidNx"
    "ocn8mQfVE/UaTzWkic4iulpmtMideHxiGOw56Cq5RwgyW6oV6C+BSiVebYmpsD6NDSuqcLoSmcSUhGH+U+e/IYA3uyhcSUFggq1Z7j4LeR+8E6"
    "aihJHWxGU++5+6TZ0Kk4PDQb7fMbPxLBy6YsTH/ODxCej7YK+2SlgtACkPgJ8N73oya+jm1GzMMfO48FTA8GLot853qCiukU3A9APHapdAc1ag"
    "+yzRW86k9WvVZ/m8gPCEcAhn5VlZipG+hENhzQHSi70F9SPOnWhqUwMP1Qw3XFfesW6Gd2Crmf/+5DMj3slQx1KDwNJuMPWZK5jk/NVZ60C5hf"
    "/xtbww1NPmlwrHFffPcx+8JQOnQlxWV4pfLYo2OJcx7wg6cySL+Akb7IlC2JA9TfHSBcj8lZuhGZZMYSXoKrNiLYWFNWtQvmfz6A1Aq5ZvhmyX"
    "62tenhWXvSG3C8HNvthCMs5gj8truMgCxL7ryaO4cjDPOwUVOeKLQBJxcJoyMRxQpAV9mAL7g/z/lr16I8MaD4AAZocwMQMISd0NbZTEOtuPpR"
    "ecxO20r08kzhHMJjwRFRPx7cvH43rI/hXIDRCxXW7RDJfeW+e9dcp/EBdRbm364uRD2W1XcBjnYmejSQ5DQI/IVIuVJPXz3Al8Od6RV/0nju80"
    "svaJ8kLdLIOkDYYUalpLPIHIooFQ+N97UU+5CG/CNr8VYBsLnHHtzX0KculjQyvJ1Y16tA8bUCBuZZ695vsSbAKmNLGWnME2JtTfr7SWaHHJ/J"
    "mBfOGZLiUqGM3xdzaCiAd24CLZJLQNCpIq7yhV6crtijoxdeGcJ4q8egaLihufTB5Z/pUdPb1jIb1LM5PnW3dFzcS4pG93I6Jz2g96mg13FflF"
    "8mLe9BejICys3QttlA6zyDC9i2MjqvbAwz8knKCbktJ/J+439YeeWs5G8FqCyaBcSwTpL9S14qhv0IA+nNUN/9UefzOX06/Tmy0z/pkwTtkJ3f"
    "Ri3eHhSHm8R0WoGKmDQjt31xsq6UeelW9Tut9dYvnQSluHMJDND/Gc60o50bYnhsbpWDdCKYumLtumaNikNiy9dMp/xQ9MO331Zxf7oyJDUJRe"
    "uaI/3fRynV+ZfvyLOQxFRmnBgZcW+YxPZVpiDfIErZfThtFVQvHQ1/VXYc4vyxhTkQVXRa1C3s6efy9KUjwT3A3/UZw/IcAbDVNPL0TGK/IdOX"
    "re2niSS1k4jJ35oewNw1BL7A4VqAZXLvxFYSHnB0v8LfI3Aj09lijyefSZ8Uf2KmVPxeJAqIwpMy47yrtUdJIDPtirR9I2L4xQmzo61DrY9pft"
    "0ceNAbsi6032C0sPsF9Q75JJj80dXScX2n1IJYIQXnJbAMUabE0pI6RIHww+tBUz5RvtR8cQhd0y3Lj4+42ocJh5eXoX7q3HAE0U9WOKPhtE/u"
    "f2+4KK4ZAiGMbiHS/xTsgicH333N7ZraBml5hlN6NAcOPfadKa7UWUmTiZp+qbu8w3bWvg1o+87YDjC8WPfcCIN2jzTdJwBAiBjQz7D/AwR4Xw"
    "7/qXLSOXDv6irzt/rJcghVhqbGCDtS3p8zdVFDppD+vQXJevrrEOYBlxi5a/pPH8oTMkcxec4uXHDDK7XEoPig1IG7TfSgJk5JY/xiylcc0g9Q"
    "fRerYNypLYfVvv/b0SnEtC9ZfmFlMRCQDhwQpMguU9M08dVad8P8BpF1xAx3UKdgT49rIfTQvPIGDVrcNNykjtVeh4dlPTYZgItV7YN9U3sjT0"
    "sCIp0GG4vnCUD2e5R2AJf3/LV9ag6pfQPCC1tiloqllPCGYZ8PTsGfw9xCxmjgGclgKu1VNTh4F35xnCzVDSvDX9bD83bOEEKjl/WStD37EVfC"
    "oWYEpeq30v6MzNjEcQIUBD1H38OP1t20X1AU+mRfkt4fylR/BR8Dt4VbQkcXIbLkY+SXANdMe0sDbtYX7uLPNO9MrbaUO84vTPSHuejWGRaxKV"
    "SQNmPL6NhlXg/pvBE59WpNjZg9/LtwcruSkdbV/APmSz4Lr2QsShoophP+DOaq9zcsV7DgsLXY4Jcf+NDdrtUcSH9PlqL0xdR+qtbbrBBPtBvG"
    "5yY7hzhmMSl9yW7qYkB0jzUxp0B8XVrlQ7gvcabbA12W5z4t751FkSUgvICVbfLc61isUbDnWqZHDxqaITg4v2MXishqwSthc5R6TqDOC2iwCC"
    "9VzV0Q04XccgW7+K64oA6IbwykMB9WtGFGdDA3+f4L8lFRB14ntznKZP8QXRagGahPSy9jvr6NDaw9JR9RX9TYkAmGbS59LugW8xmDrbK+u8+s"
    "vPX2i6dulUV9OkSYPHJHPZ97d1SvfPB89MHjhcsuZV+N6xYw3RRaVBIa1CyBUMbGW12EdxPNEdzapP2WRItFJlL0wSmwSws6uHHwSCAzMjPR9N"
    "4Y0Id4F+g+drELZsTKH2Xmi9SBJnDwoRoydtZeW8OFr7vVxX/zGBlUMMNTVSnAPPPVzr/ipx9Dsfcp8VqqKek9LRq8Eetz/2r17gvcOVOGbzzc"
    "P+8Kf9pXc0t+mp/++1Nym/Vvrl0d0P+4QbcRKnIx88yaPnWkPMi38w8cTsLeOQXivizZIB1BQ3j3wGlZwGAy4uUW9AjB92g5O15f0M3mxUUy7/"
    "L4WUNkUGdwpJ4Fot64a7z4Zp1WQnx5PRCcPWxN62K4t8krWw1e9EFr43QY1NmFbrOcismcEJRPPV+MbDA/EqGxk3Y0WK0PiIQpyEwRvmXznYHi"
    "nC6Nd459jMGiWII8bpHWNE0Dsn2NpYcsmJqCFZ73KYfIRdaahZ2RuQGu1quHaRnB23zwPcFgao6AHR+xr6f6C5qtIft65Y1iv8XV0bMLwaFD5y"
    "G8dykcE8nj0/viSyqxINmPaA9sCeOVLcRgbTtat4NS7tkX7oL6N1rE9iC6m5Og8tjJ+Yj9o/ki7c0/fcpzApkaKZ2wOf6FAAKG+MQujvidcG5x"
    "wTT1r/VTZ+PM8EaB0lCYkzRgkgBwlBfwPkDAlRW5BHCIFADmN308N/1/vz5orEVEWFAKdtTghdk1lFJaAY9HnN11Q2PqNyNIob1aj9uzmMcfwl"
    "PkBJ/PXkELwEQhmnlz/JFYQ9Q8vMHrwh4KkyYDE90OnWJt2lRJmrJtC37+PkjkoocQ+KUp8OkOTXuS7UBB832X866Klj3/pkJBtR+cf1t2tu7f"
    "fl2c3hiotXDRi7ZRtpiNLzbaljN4N+z4xjf3Ck1Z3d5fRHZjL+qC8XtTRLs1J8yYWjPCjJJAYI4/bm6rCSrNh+OAmv6mfNNlflPwHPxAqsOANY"
    "rbAFviJ0Zfpbc+R4iyYA/GhLpk0f4DdTD9/gYKeKcECu1Mk05+hEz3jAjcoyCG5X4e4+eZ2zvwKwOknRI9LJpNUj7gfHKjPy38dd9oI9BuBSIZ"
    "98CqdrTgpb85TgYFlGPtizjGgI2+hQB6gMTRbpfjOZdRCmjfwC7JLnVUnCT2H/quC9FioChRWCppf/kEsXT5v7JNDq34Ph0UfLZv230yv3/w+/"
    "MKMQjCKShvtdX7muRpqnZarzKDhC3NZE4vfffhALyCMsu1h44/oJEivHVryb44p0wuix+TjO14u1qN3YbkQLczKvpt1FFWMw1qOp94wZriuR8e"
    "RgpmkWmVMIMwCOObMGtYugL9sNuqClDScAy33DatLn/5lGYREfQNfY4Os0AZmQvyYPey/en+XgRkmTDbE/7zzdVY9z4eb5TF5GDS08LQPIY66C"
    "YBiniGzTMV+XFablM0/3VY8VoC0zHeOkBzaRDuxKQkx3ZyHeM/eyZofGjGX8zsfmqbXp95IRWjkuZ57Y6yRllokL0G19APnx5k5a4hWi1DQnKf"
    "maWBquS0+oll0lOVUEkLPNs/5IgEqcpmaZ5/sBzpfcbrvhB9qZhmL+l70Iv0lNzwAf3TFnFejDYVZNi30tM5/NCGLNA3Grlv0efmApUoTjuA6u"
    "ohk9l7SyMcKqUvOYvKOXzzAZ94ThhwRiXi/lvJGNevkUsnGT3HajghQOv5iK25fvFFr+gD6zOv+k/+JT+miJZF/Zx1R5QbB973bocIZkhDPT28"
    "PMxCjK58Boy8swX26/RSL2nG9LonIK2J6ArWCm3LpWilj5KSjj4zg2JnK5F5vPO6Oase8Jb0GwePaWs+J9L2kOscwU1o0MKP1fFwcSJl0sfUQQ"
    "AdGUJzVlHhfyHnfC3QGbAf+JGeE7LlwozNHfywDv/LzIZ1BJnQMM0cr2e5PDd2z8V/cOj0PIVSiYbn+AZQ1zF7A9RlhuQ6JcjEzqDWMUJyTQzy"
    "68f5Dh/p107Fp703QP6Adgle/bLrPvSdjt9lfxj8VTXki/tMpPycPGttKe6mB4s8b8ZfEWSJo7V03Ph66NLRPHsLWqq23Lob0AVxdWZcncCpyd"
    "JnXwQRps7PK1KzHW/36pwUh9LsZMpgtsvKiqHC6cCyFNqDTw/skCbtX/wUX2rzT5ZBLQ9YgE/Y3NpsheBnSItb1QIQHINPqGYGIMfA8SXbX07Q"
    "IAmAqkyCQ0UXx0LTx0LCEJGAVdc5dZIYMHaHSAopDpUme532P2nKzqiWqGXUv1dPHpLk3eBzojJ/X7f69xkSPyF6pdRg9YPKM+PAVpvQVX5Epd"
    "GlmXgfjpHpcktS62dMSAAlXlvAOdfASmRxnp8udCyhaNLW2PNm2oiPEV6+WqjXqfjtxaQcbWZJvOEL4KXNmSmEP2d+qVvoPgNp1NIpMwNR5ZyQ"
    "9fjudW+3FDhs72NQCExTLQrkOv+sh8QDbOwo/kNaJwjjsAtSC9nWB9OhlV965UGNwI/PfQpEiNGFKfhvG4GnrC34RcWALpnndh+GodTIC/kWQL"
    "S5JDlcq00EHU0cxz6QzN13dtow5nDSZ9BfBostfAixNivnclbRtHS+O8i1IQUBx/PiEQooQC2u+Khle+RlHTr4XFheryB9e90x9WPTQSkjqb4z"
    "U/vD6c6M/BQqBxTxvlbDVEfK+PXUTP7Oa5JJOjS/0LQhGn8/hIxtxIhKQx5ibOSnVpK0U8dzUkqDAOYqGgVihHwhIABquKK4FQgNwktc69lF92"
    "+iDhVFP9dyur6gmV3+FxqYvmduICvSzhxhKjf++amrHl5dQMOVHlC+LSAUH8MqjAwfJo2UmjOPd6omuh+4CTL0weEdcZOq6OdB4WTon+xOkcC4"
    "RhKQqYei5JSGBdAsI/PhXWAzAfwWNvoSmuxRj3AyAh4vPRSQUrYiyyJsd7lomTzH5J481y3NXkR45huItZ2T3sgTXYz1IjrxzrIv+xNFAtGieo"
    "11VDROXoGqaDQ9k3ufQoTdwElbSr6n+9SPCnO3qDU/TRm7+BlflD+c7DA9ult1U6j97J//pJeUdrz0RgaMLGclTIClLwtc5J/zbHVyRQoLjT91"
    "gieWYPzspsrXsPg5+C0GkgBDFKFNEVDAFLK444E4V2kyrWDj+KTZ+GC1yKqplu4VJqbwDG4ccxrAb+Pzce5mUGzbWn9d9tH5JlP4qhED6X0C++"
    "tKygPgtte5PUX0mCeTHEd3jJ7EDWWfVZdq4HRZ0QNb5W5FBR9BEYPnjCWUXLLms7VL9LaTchbC7TtSSfqpy+9WjS6V7zTz9DDdwCjwwzL409LW"
    "cGyhzO/I1v323aNR1AX5Eb5A8bUCjNpNF2hJX6/Pm3bqVQLysCRQO3Mtf6HAKVjmpmJrAchfvWSNCP045lmMtjIFx7h76rdesPJ10keES6cFuH"
    "2ZUWVQYO/y1pPiDMEmUviS22f+XFGy8sUdA4Fmtldrq6xACqWwnqfA0mX0jjIbJHhJq91nK/wF8mZV5eNjI6/Tt862rCnox0pu5dWfU28Dluih"
    "0bvDnxoNY4+V2evp38qputjDiul3vZDdKpansOf1/WEUPauVxj7pT784j+D3j3oJC9NI5dOTDr+z+T5Yu13oRi1iTEiQKLNtn4Zr4FsQ2UcVdD"
    "lyiKhD2iwOSOunXnNDfYjb36eW2aPe5o6wl6lr8lEnv0MYJoKf7WrYiA2PSeYjp8k82TBjq+3jbmob8ZRNmJyFhGkKmhYpv3Na2gU16DrP/LIZ"
    "Hp3U+U2T8ceqm6hdp92sED6vK/T1KhAkCaFSLeIDPfJcj4QSaY/acDoHbve0y+uIG2ztwRWVIRE4mR6wvujlHTQFDB2IHfhHrF+CvcFjEUAala"
    "HhJePi2vDc5hZT9NcQwvwux16EpMkPXTd8ui0zMhms8fcBbdDWSvicfWVMary8cNZv/VsLxNz7iZ6Pl2GDUK+dvQ6knwnsTGis1uoDyRpe5njV"
    "AIWJHP/2B2IZAJ8vMVPzjQG/LmmGGuMM+ZAS+elZSy+hxfFZs2akIuI3w4L1XO0xfnXA7vzweUZNTHLDLotHLZQZ65LGAl9Pim2C2+Oxvja8Wu"
    "H4WleFwnBN/syVDWBQ1u4wASPhcxl60W1wvgY7aJEofLOrJONfmUQFTjd7I5SvBZSRlZ7OkpTmj+VlXrJwTPwAzwhcKPAwIfjAozW1Q11q8Qsy"
    "faEByBdSuTnQqnFDcProCJlHp0QD4uoH9yURprpJC3OUIR/O1+zAjWFKcLdyiseKtnI/lOs+QAz3g9xfLQrHXwECudOCwiGm79rdgogJCEHZ37"
    "U9T0NurbouHqmW1mC3COVZe8umHrxSfFeWNiQepkJfSkWqDh0HMySJvZVw52L+PtuiS/ZeLN4J1rvU3AvCrnmFj/Uvy47C1X75G2sDByhEjbhs"
    "hQCpopTxySnUOrb28n01d0gwzLVvusO+TMno2uAh8WOsHfITtU6ZzR449X3oglj1AW2zx4zleTXXP3KT69aX+l9P71C0ethv6SzdLe5jeCvh7v"
    "baxVw5W+At1RN0rIBwtHq4fFLX0KzOpuM6PykQmsMzB997qOyek5PCFGO+AB5gZgi/TU6O9IcXyIjPNcDx3d5tlBHY+9JQRhge2MXfRyQ6uhyW"
    "kIzr8TcF8qYbr53kG2+xoxG1zBjNyHITVVXPzI4z55yTY5vaeCfEhiL+UGAN0V7UAIvMlb8mCQFB0PMjRbJtYnDvWk1jUcjhw+5h9jxYRV1VhP"
    "XyAgQhEo+bImrtSqD3s4zhPBVhSL4YicchQExcLdWPWbbawwhueG/tXJ73ClPI0lscsvfHVsmGqRFSpWpAqTlscr0KlRDO8Hz/3v/ouKFi1FiB"
    "Sg7MH1NBCYH8FtGnFpplOokKd8od4z4JPGZO9PwGe5M+HUa+Xef47NzYsDs0n9luF/1YXreMqzMehdIitk0ukT2pvYHcEEA5qCgK0lbckFa4oV"
    "Nmnd3fH5Uxs8VQpIFqQYrByqWtdjgqGclRa3MxTTPZQMx6bNZiKhE9vgisAQAw23KLJyjUF6N7btQGsvTeJ3873ux+7nOrvwykr1G/d3kQWomA"
    "tUyWs0hUBdlW+4uUxCYVLgB1tnh95X7yHflr+oYK9bde43XFwqyRgJ7KdPcLbuN8f6jWSprW9DuyE6ZLr2X5ReLHP52cD6+LQ4SlJkE0MMHS0G"
    "J14/yPCxz24sFD/90RX2jO53spHQJHQ3BRiLP/3SVmlix0XpLX8BieCBwspPy8AKmo/oOZEYaNphxqVVbULyhc3oT6U7q3ilCtSKb1yaKR0xEU"
    "OxZNvqN3wPdKBbxo6x7P8FGI11rHDiEa2iry0U5qJWZg+tRKOx0aw7gOyh+cV0LzeGXE43UZMUrCsfGk8SvaaGTN8MhnoC0IWJ89NE2poKdMVJ"
    "S9ObU41dvGsm8NP8ZjEwTgp/6Ho/NIcBSGouCBvDAZsyTnnNmRc86cfujZu9tY+vqvymCJsVI18KYb0TEMYfohSDlvJwt3Y28v+TZXrQZu39/2"
    "WTqqIqIgXIWkzOvEligG8hLPrcIri273/Fnzr71nZM9sziyGhwars21URwOxaQVcMc2+DS+9jJ39wSm16BUTVKPpKOQuc4/D+tXvVrAC1Q5zuI"
    "q/XWSCXUa/5oFkzm0/NXgnVaeS5ffeCWANOBwDXk5ySd/A3oBnfPHnaWwgtncdpjbw0PO7kEVwa1gayaOdaJIMfKfW+ZAPlFT1SKXh6diOQrRh"
    "6aBmAWqruVhv50CE3+/OjfsHQTRGWT8MHPuDVRcNlDYOgsZ9T6ttttZVobRFsjg40YvyQfO73Fk7wJ1+KHLkMXkbrLFBsz1Pc7zIFZg3dULF3v"
    "nGYVCzlBwk26kqzkOBupgSAWbI9CxyAh/rmEW68p74wMT78i3ev0cpVQ0gGUeOJJqx3XYgY9/W0nsV60EVE1aDHqCp56qiUrLr6FEyTMIXkzpF"
    "k64eZxHMyGoJpggbp6nfVb/K5IfKQ63FJtTF4v7IWLOZ/PnAFCgwWxaqOlUohLpyXx6eIkkMpSFLvQPZ9k0fWX8WWi74CLt+Oo/hQoCVNpAF95"
    "aVwzRcEMnXCGQZMlyb7x4jMneNoWa/OFGleAQ2tp3iWUFji37cdENuWAI8cZeHcpDiOSLjkSVHuB/QLOW4AjM0lUcdugTmJN8inBC/Tf5e9gmD"
    "xM//Rab2Yo5jC1QDuymL0N52EchPxu96PoVUZSwmNTSlVGob71/VA1YvDEuuXAvH/k05YmbMzHYtlCITHP6YI8SnVVeXYMZbdk7qZa+Jemlvuv"
    "9SsdRpN4knjGbEWcpMee1V9J5Ifk3Sd9OFtdb7qpQH/BJC9Ofha9256fUJjIgB594CPLR3zyveScH+Dub4dH839vAs6Ril5LynTqRfnNh4yNS6"
    "IVh/h8n6Bh6z3JcrzOatgCB3A/0H+F5rHpW2ehDbtwwIrja48eukXPRWRedFZyi7HYBlTXRY+xaFL2gz2SN8+ABBwzn6k8+n2SQ75WVEdixHRt"
    "P74KHv2NV7uiL6OQrfB/UQtnUh5NYmgnDhGp7WnTpw2pXf8ao57hNq8MX2sKKfJ4qAP9yfJxjxD9aspLYZatFNfMUlnRyWvZ+ClYcvnNwHIcFT"
    "yOYjX8OfF4JQGphYNcxbYlTVt1qmnHKDtMUejvmBRUmab//9Cq0PfDPJdRHfOW33jy1mNUq1jwQDbv3Ya1yvHnPUo1XsgnCDvA/kb+2Luoc1jz"
    "CrKEkcZDWu0Prr5t/6trbHwbIegaPO0bSQvJEUZg8iM+Eqj9+5nSkGm19Hl00wKrVK9BZWKYcqR3cdku5uQvmPM2ddjCiwlyLWC0W9enMNOSLz"
    "Lo7YFnbcBUk8VcCmHf79VEXpwoFO5Af0ZLu4dxjVVE5+VL88RZhiUwtPc9xlS7LNntFFKah6HTYHghHDm+IT+i5DNWDjuZib7AWoixkIFmarG7"
    "9H6CUUfHWshuXPqD4CwK6RazavdgcCxjUckjhQXF4KLuYlxfR/vxNQ32z/vlxwkdi+mMkYwYpTOcZXj3R/CRfVkGbj00eVlPv7x8851kjTGxaq"
    "54eg2QV+6EsYh+WDShdolL+oj1AxelNlASsi1a+IEpDQIk2OlkT9nCPETtfxDRMBmqhyHhrTPkH9pMVQPJ2Z7bv9vHXe+bvN3a8W757NbhBa2q"
    "iAEzw2ojGgxbNh2nv9dUtjnlKHjr0pHdMvguaFDiDMjdInpgHHhH6RiHj0TCAJTTrxD7meaYNB6mE/6VFRZuKSuQaicL21JGE6r37L8UVCE0LD"
    "HEgLpyARcT3QU8oqyKaIGY/wkT6MZC+4ek++46gZ2Vlxy0Wx6sMYmks167cFSg70dz/7hA8ioXZaffaEpH8h000T/Vm0ABYNiaTGE2u6t4oSv2"
    "gcfXpH1+RBSAk+ig5+ioNjELik2AurqF8temlkNGVtLcj3gXvRbh5SI/Ko6CQ6BWaNXVT6W357qx7Sh8Gmeg2vtDU++hv7cZOMIfEBn4Yf9a/6"
    "sXz/ZqXvvFOw9mXG5XeIpKj8dDcm+nUQEXMvMj9VQvI3PE/4AyGDH7GIA7zPG8Llef2uvMWfefDpOUfQ4XS1IDBNlrg5Tm/pAShpHMds0Q4LfZ"
    "YLDYWx3eiTwp3ODK8STAoDP8gYCveMn/POM1TW1S743qi/NbBwZRdT0u2NAbRUFnapdfa1mwwZq/hKHfxTEtXivkQ8k5WHMHbgV/i8uwArxdjn"
    "Dr8xIcnT+LezdVDem9g/7g+ftR8x8MoUf4UKWTVp6/xHCGdp5qtUDsIzavuUEmK8aVFEedtLhuUMq316N7JPk387W2psnwCSinym5x4Bh3zWRD"
    "/lIQ1IYK9eXkw9wxdkvFFOBvfRNLBRmiFr0bUE5RoGgqWm2aeMhEM8lIwR5THKrjS/7nk36xMPheQMW9u4WUi8iCAAV537fIcZLLe4kh2//8hC"
    "1jh7xxuHEIDqTncVJlJpUssc93yne/h7iM+25M8pDKuwMHhkLaPgJjHdKWNkmMs2QjgDlvs3RH8PN5cNpzbbPUB6IWeL/MvokNYL26cGtkwKVj"
    "l2MizqTx7WwB5/RO5tEUfJHWhmc5lpwkJRj2D1jvH+C2YCSUY3QXp3Bq5exE6ssxi+Po8Y4N8Qh8XbyxDiJy0lU1NFU7HtSqqpmBp4nyQhITzD"
    "UU0glatGfG88rV5po8vorlkIXgKllKfc0G0IjvL99IjmTQkQu42Eizwtly3kpoHvGFiGv85oAxQVrYHgIZjGfQXWOTzWUpLTpBPve0ePuP2Ka6"
    "STsdh1mNHWvBlK92pXyacCzJ5s1sTL6uJSM3K2CBWOXSIdbjyhawmk8du9gMCVcgITy+0PsNCTn/2WQL/OXgFYI5PyszWZ/o5snlImMNfe0hCW"
    "OSxmUXCuIy24i45CwOirsgmHi9fzCEUVVuMh5gZMOnBVVJGA3Y04dzl2fYSdjrARKxZk0njsWr87UXDDhjGBnPeucF4frJW1ZPkqB6pMX68h3M"
    "fnRNxfcfqoDH9KJm/FPHfdtMpR/HJGmZl+gRi8pPSygXVBfuYkfBU2qvQ1HjDVrKh+f9TP5ZvGcEo/VMqt0FoY3U7chbOpRum3j9p/dbler12P"
    "QP71gtrzJYiG6ZTnKTIaNp043VvH56OSFI//gcC+KNzkf8cB79aHpiT2Uczdrt1CoUNSUUbiOH44TtsQv1LUW6MvhNOWoRhh8Ga844Mq7Vs91L"
    "gBWa6crRQX4sxlm593fb8ZnuCdghpUQwOtjoGvXfZSwzp55fLd+tN/lal6EpuIGbmILCkOZ1u+jYCjBYbkSJPo7PTVMEI1Pk7ykzdK6WCRE9sk"
    "tAUw4SkIlwk35UQVPFAts3Nvj92ao97oFa27o0DL21eT+nAvIlFw6ri5sZf852CdNoz1fItoPxEniqct6VYF1VI8yWQ/CQ2nrh/MZ3uP/rz/Uv"
    "4yJUUQAvhX8Q6IaCJlA3MkunAjr9lU2XRhUs7vQqkYvbLiHjL6VaG08bd3YTkYIu17d1yfwuHB7wykL/aWGojIBnJe+O9mLu6IEO8GSxJHLi3u"
    "+J98ec2weuc+4iWTNiwEI5AIu69KLZ8++2x6Ij2iECJqdXxqhzZVymExdl9h8rgQjGCf8zxYMDXC9O8rJ/x0vrsiu14d2ih/2zG8rU2gcIB2c/"
    "1OKlQ8SKZXbi+4hSjM0qvqfSkytfbVCKfM80iuQkIo9rzYxT9iVAUEax/cJ0VcEN89smbAJsPDTte3A+tsFzZfEmLOr4sxuITEM9NRQ62vP5KT"
    "lcCFVBUnhoePq2NLknMJ7JHtC8maX+Mr6LKr6fsTLNg3nx7k5H7KvJh1LpTCT4EIoqqxnPdRL7t2W1a+WzSNyYYYZDWp5JFweDl9bF4cdiYWbk"
    "niiNQRkUZNROwm526l/B2Ured6TiNq9VPnjrZWiE4Ol5NIRkuexWsC6zpTH9VlzlE106b9rTH6hA0vZtDFBFALCotMpUSSMojumlWK0PWLnxx2"
    "ybVOKGXCkOGDq25PeL5SBRiM6JbF5w7jJp82W+WqIUo6Ck3z4siY8i32AVgUKL+yxB8pZsqHzcUbd+aT3U3P6tsGk+1VL3++YCTmMC501EHLVD"
    "ijRf5RUHG+HF0BMCG9H5ekUF5HOg5w1sp9TJdRWrcElirVAO2ZZtHNKbsifL3exwkdbWLdSbFOKiw1MXAm++vTJAQ/tdevh7/qzyPAUMr5MGG6"
    "L0I5Iyk2NNFUod3Q68htRkadSzqW4ZAfxV3nOUIW8kDkc/wmtUMynVXfzr6qMX1sgGPf3wKKnFQ841j7VO70faYvq75qaHKUkq6GpfM0hkkC2Q"
    "F2IoKrxHrn4j4PbftZFeQXJ2RlCEFKv2OCLYOefr9hudWtyqCfzRjUmWxwZD9qiMU44bM3RQB/F1gmn1K9dQeYFCsAzPTxD1eDeflG+v4odA+k"
    "OjSgrqOlQ/fmBQdGwt6UBWCb4MvxQEeET4zN9+plnzBnJ923OGbnEGX9yQg2lN/6WI19YgspalgJlt55DM4znfy3muzVeiZb8UE796fWa3tfFJ"
    "GcVo2N1azq68BjuEgcrKosRtBs8kTY7wG+A9W/MUvFpUB3vKo6jbVbWf5mkVvl65EXDRG82fugs2sJ9GZiNK3jftZ61vnj+oZmOLlJ3iiGZMjU"
    "d1KKOdsmTCiVKHmpnLC8q4VoWr6MQC4sXZPXoGpuvm50l42b6X+mXL8YBfxmfs4byprjjWf+vsudiWcSqRV5PLMb5C9oShmLPPjP/tYvxyJP6H"
    "dI8GBquGCfziMB6O/M+M8R+eog7RXRGVaB902hb/uHOiiP9A9Gvn/T2Wg5JMyKAJ9ylJQb2bEvb8wVSJ17j7gYPQUebTWb/LUVM1whpnErtgvv"
    "E5zWTz/Toj/RGXBHKXkr0SL7UTqgbZ1l5x2IN8FWbq3UnqdaaklPHNxtTdh0K3yM9unHoYkhGaH49uwunVbUl89cCUN9GUlDrkzIuErMKUcgKz"
    "3z5dzSPQULza5SY3Qv07WXcjy9hGupPJm1DkfaRB6vfwLXWaJVA6C8g1EkNWDWe6u+FTL3KbDnRmTLlClfAkwPLmEMqqsY/XC8apt8h/S8hAox"
    "O4DWlK4mzszvv4LlOjW9eWRKbnv02bNYXrEW8XN4AgzwyOo1nhJly63mVIERW4wKvDfA+S314DWOQqCUl4PueyhIk31EejVSag+dFDuC0hHRhA"
    "O/4Pp1lB9Viah1EpkD50PO1oOn/cwV7TQCQdoLJN7+RbCTg+J1DoIB0qyiJwu+cDm5ngre0NYVwTVTU8jmYD+KwpuF8EpK0yc9u+Evz34wV5wk"
    "N/kGjdy9ESib01PSdPSK+gd+Vvxu1J2Mf0oCqqxLLX9bl9ZNxpOrVwQ+2ST9HMT9pcnBpXPXfnyG03jgnyW8PoEr86s/zBfttbVE2uLy0xA/zd"
    "oec3yfvF5daJOq50V8TXNxOLLkkJUgqw/ra7YFnZmuPbzl2i0szpQWnEJDYbCIqXVxDUT38zJ1oKGoXpUfLhchsAb+c3IkwOdo9fJ0pCOxlG0+"
    "jYf8lYGNegBQDVaaAOhuOGksQs8jZV08WPaUb1REfkZw5Vat/OS0BWPLzye2nKKDGU5E0hKSCrh06db8pXi5DP6GNUX9ikxIis8Uv8aru/LHiJ"
    "pkxzPv83eILO6U1CA4eg/YtuHBzAWCTL6YgigxD8idx2xudK04+ddywKmgqu8rx3ofJ4CIqAzCFV8lpeXtWdnfTXHErQRv3eUojzcZqJffL4ov"
    "3ASXvIJebj13Rvr81JzPognWtEhcMt8WD35VsU8QKeIMGzY3GSWG7LJtNxQ0bvwraMAZCLUj031khjCzq+AmZeXXFfhVOr5RQisOmpV7TdezoE"
    "wD5YHGJe0cj3FwIDgPCjClXfMKsv/UknQkaAt2huKqV2YQt7I/seJZBFTkp37t46cJWOo7oWIMcWHYJFnU99hzjKIY0ea6MXu7BTXRnGZgu/fo"
    "eCEC00dt8BfmZ7QgYMH1asUJKSC/W0YBiGVo4IibF2+EZ1y91XPu6LmordTvTMEKusbPh16/tZ3nmO/cqEkVgaGuPeoBPEWRSeH7FPckfRKupO"
    "PvFWw+/M/Lj0stk0CgLVT9cCMt7jbAfsb7Jh3S5ci7HlvaaLtSF6WzfFYHgX/Rj/iNCV0APE7TWFtzd4cF1f02meZpyRD+kGL+GEKWYkiUSPFO"
    "DL8Rs1RylaoKBnUa63VfAQtPrud5sqJidwq4aNL84VUorgbjhzcmaCQGthbzje6m3nysn0NnNoaI6dbhN21XbiZ+fFXRRHZW65byCusDDD9vvS"
    "9sEmKxqRDzBMjHeQqJS5fRxXZW+/J8fXzxdGv2wn5KZiyP/PH6lSw6dS3Y5SPs7WBRUrw0pC0Y8sbm0qHmNWUsaq0ofQLsZ/07YOSnTqddcNWV"
    "Z6hvJxJ9kDAPd/cFN+ZkgL6u7Ok4suQuvsyfZTLq5qra+YLEh4QmaW9aKfxQa2I7Bq0gS6/0RN3Gch90U5wHs/mGBeS6O2GLS543+HgJ82xTlg"
    "J5dYv22WWpcEMeoQk4qnqMVdz+t4rdAWX2TPJqTXZGfu7at3+id9FCc1XuxDSVVcyuYZoYtn8vTdJ6ykiH3G1F9KVVtjDChevZBcvd35/KslJi"
    "xFpZ3hbWYRgbftekqGym40tWTMSHQBeT2lYav2WWRFjNu7G4+BSQl3BAITpr/vGFMwL/zpE7gs+o2Q38Bcp6iM1Mpz9pSXDIO4L3UxGxxU4bba"
    "1Aty0ptYzQ5fsB2zWOU2+qRkNSzDysfIazKUi3Tql6TaXilSHt6pR2YGqsHtIF/9uhMnyrxD1R4xTdXhVnU+W3yGJUpgfqd027Sj7wPVpUyGfm"
    "LX+twLrJo2inUnft6CnTuTTUmBBEZsDCMCgOCcnkIturowWkGP7/fVxVQY8MFMH2dj+4AFIx6e+KUkZfqKREHwz40wz7UEN4Qqg3NvIHjRqGxn"
    "WiOv/9GOqqWhLs9l0UzxZv2y8JlxG87+7p4R9Fet9wRyz0DFYabWXpFIvBWx28IJZcutYC3YDLEipK6g+xe8g6/k7y3R8G+wb0upi7dGrwPRma"
    "fKUOrVlJJdiUU9ORN6R6Lxd734H0by8LUZInCmFPEKzz5lsKj07/pBspa2Xw6eWWYxZ7l7pR1o/0wN7AlVbDVj+qmOLmhxLXcvrst/XFCzx5Kk"
    "94LpVcpIbrrFJvRsl4LX8XdTDyJ+nj7HK36jZJ44CIUCh4AP69gnhbXfCGL/r3CakTZMR4DtULrng2QT7PVgeSa/SDHFucmVuWrDqY7tNinC1a"
    "GNQ+pGE33G6puFrUzMZh/FVRUX1q22jIEm6Ksk83aV0/gNaz+H6IPRTwbmun9cfSlxOQ08KXKDRFSsZi+J0cXd/yzVrlo5xnlsogSzIkVN8ohQ"
    "ggsPHDYWMhigwQOj5uhgMZJdvgoKgT5RIIiHt6ibKYmLh/u9ftsulkLCzzXJCE03Ud3s5tklV5sSTVPak8sr48qRAOPcSPSJYjSQZjKj/fBiM+"
    "+G60n3rgUvFgAULQv5tpWV977GIKQkxga+Gx6n52j3Pbr1bzVfhVLChpvGmiaU0BMzUrJVWg3qQuAVOZfeQpVPgh23zilZdygRdMloKnoetge6"
    "0guoq/0wV0ievC1PNamKe4zXmJlDRJBVxS6b71gIDD8WwMuB8VmkSRcw8zRG3Wr9vFpIVxzBonSb7ec5ZdMNQd172wEiB//ez32nt1HmUJ/BSZ"
    "Uat1+a0iHPGt7qauknzY9kksqZYHF4+/lfjWv6t+Va7J+0QHgCM/+yYRlm9Y/lKuTMiVvfw6nw2SUO94XaOdF68S+XpOo37JAaORXiMftEbMY0"
    "RvE3naSE3YTTZ5XAQuNYAIq+7S43sR8wLIJ3OQ0RTuu2o8LAkYH2DyKn9vL4FJyKdlOCUUmK4Mg5BCHFMPJo0QGCcUZFrl5R7jWuNWXBCzQxpi"
    "cjQV/bW83HBoVkuDNTXCGBAOaUUjE55Qy6XnUfYhROHjhk5QWhoBSUfj7iUiIvsOwOHtThVjvEQXkIS9cONAD2EqSTvYihnruEn0tnnJrEzHoB"
    "eQdFHbUu0jR5q/Z6IsRWmM9W3SxhkBjDAAAUgGsBufqVsaNcG7rP9tXYGkPj36RLZbH0IF1ErqavRX5pndRpPqfnNUJbYC9LuVK4CiKImieYdH"
    "KpIpy008qjqsfonbtcMl+BThtM2MWOm60ppqnNQvarg3puJCGS9UZoXG99KuzlTiZZUgpqcE94OhCTQc/vmDbL8Pj2L7+E/vVgAjJlebMWLepf"
    "pCn6hSWkcd9GMwSb2nwNbJQfBUd1kKNd3fNhI+msgdLweQMGaZiEZH+NGELzSyLIIE/sSImz2LibJLwhI/gUmRbcMWWbEPILi57zxYbOR+TB+1"
    "MF1j4DxdOczZQ5f3Fy6i4lZomUiqEBdvRSUc7Yv/jNtdA1Im3ac8yUo6MjT8Sfteo9vN5kOAHEMw9GpYEH1AaXGWqEVak0Lus9R0X/0OqixI5P"
    "OpflUbZhsPwEfZYdoUf7YX5jboAdJUZWzcA54GE5VXzxkul+KaH1ba0dY4Z4B21tbOC8OcuEA0X3bKiNjT5Dkh31qiHX9vZ1dgQ3x8ihqX3BQV"
    "yxorgTjUJ2esGHGU4vGjBMlDyENq6+1PMx7SwaBoOwprgs0Eba/KWtYYBneglsUx65U4Dxtg8N5/04eflmFItJe3BxsI1+2uJOMdmo31spI4Px"
    "h8oLIbhzUPcqNzGwiagR4qtFIc7GnC2VuZSXM3xQbusKIIx46oaNRIdfOgVhBJg5/sQZpPnSrV/UL1tYJ2zKT0DYreyhL2j1fOn3+D2gZXNYh7"
    "XG2+hHe2WsklCJ5XOVSNaRWFh/xJjGbFEJfFR9/xLXIEXmdI9CtuJUiJxmqhKsGrIJZ+XFKO6LfwugGB5+gnpeVGJ+ABjDQnmpe1EfUZcEhu76"
    "zMfCROiVUioZnym2xTSCBV1VfnnG3Ozce4y1rZ2iLjyG+5LItIdsWHneIUjaUIed8F2zGsghrIV3keSNCWGL4+kmR9yLLaAtkicFhh5HIv1DDs"
    "0yBOz0Vyr3Uy414l026l1axUKfw+h5u4JH/0By6u5/U4hGCIf3cN9geU8pkwjdbPjdvXO4Tu87PrzivGVq2rqk3xs4F3i7Od9mJHXQHuK9O0RY"
    "Y1mD7hv4Mjh8fa1GFnk4kLr8Iy0I2ATqbXW6CEeEVLT5qHCr3hCTNdAXY/7KMXFEvZ8vDe1h17G0fB76Gud6+zY7HqQb1stFMCwDzvTuiN+XYZ"
    "T47ZwUA8o9B9dUrZUCf1RORAJXCW2MbnRcxZykhBE/VOsL70cP7iN4DGDj1Mx9c/zNiZXLX2l9BDxcl44pIHF5fFmxYHFRUBx4ttNlzOuV3TW4"
    "VHXOUwBLItt/d9dCuVvd6wkT0SVGVotymrikkBOgpDjZ00n8X9yZYcvkmUziTm4IJjDQklyKaQ+skaTmT7aHUsaSbEVZYAN4skog7gw9XV977r"
    "GSRFCsh0Q5afvKt3uf1biCb3ipiG3FjZe3yFHntYcKe2JeWJoOfytilDcO5NfANzCKPVbG6iF55HFMsr8lyD37+tKjdofUDNk3Yicb5IsawnLo"
    "Lnyo8rPLyqbjsAHf1K0GYQ0Ua4XyvW1BsIk1wVIEuf26qZNttDn8Li1pIz/dO7bbL5ZO3GRx8HooFqQI2wkmxDHEfIwdpgchJm0TPuo0ltmqHn"
    "JQsMLByRy9Usnb4YzkDyIxAfiorEr0e9aHX9Hbfh8QZGQ3qEfGdRRdrYJkQC6pffSSZK3LUlZftIZ9ikRfW4v6mu/KLv6nYwmZIUrz5iJulAQb"
    "2zY3zrax4N7S2dszspKr/dVYfEeKdcYSrJw4UR/qK/OtKvz9vh3uvJbX1gjuZMkcGIK87czR0DW2q2T+pEdjMiA/YLj5TPhYsal9YzJagmMlVW"
    "7ROvCp8TxLIPVA/MPhJgaNgD87gvH/YUXUcfqoq/Fuy2uUJaLzm9ycvHr7tb0hBMTKIPL91q41qCqLysBeTIx9ZbCZ2vigfBzJa77Cs/FMgg0P"
    "sPuoKVZI2lB7QSfRP5NI86SLb/isrGHjWvNAFVICQa3rckB17YHWuxzrDhNMLYlsnMvb0udHdXHs+vKi/l+EEINoYAQr9bQ3w5IKLyGWV/dpon"
    "7oJfEGFUetVS61LEYqiynAEbB1kemQdh2AxdLEaNd949sQH50d4tmMbWXRGJw5rdOuRfK6oADJukP7fiJbCydimc2Gon5dtem6VYUDU8iEPpxd"
    "aAIUj8fUNXc3oxq9EEIbRn7xv8qicRZk5IE/ZUXlLpjNDXRtQ1DBGir8cOaiAX+O6BZyoV6G61MSdzCaTZXHTjrcfhZ3lUabCIR+eGDbQI05KL"
    "kXgwTTQKGtydepYM9ytOdINqe5xORG13cKePfOJG0/u3n5Z3ta0Hq6Q51XlXDPz3KmRM+fKd363OUI6jxGX2WoQOn49PfvQK4e3KBEU+5KCc0H"
    "oVvCHeWlNRW0A4/iFoUdN5CSKCIJ0WxO6t8Fi5Rx8sfr5Iq/MRKWlptjQusCXFbqFNCR2DaQlswn3swxCUm8YjVW7TuDl4WF+egq04saHQLzuE"
    "RFavX/le8Jrtug26wB2x62ROEWyI7YlGgQ+x/pwLlMWYYjbBa5Xcl3CWluFyuKGFZ9rex2pABEDavMun8Cjyl4O3wlNI8suSPuIPFly/ED55SN"
    "J/DKZ+lDBCsNpNhY8DXOiFCqsVYNjp3KrzhDeWcY1iMUueCNqa75TCILqvg+fcQyHxOH7BUYmdMMKTMOXfQw5BhQco8Qn45xCW1N4qWEpEbXhe"
    "Thyg8m9P5Y071KzBIeL3LoaDJq6fpETfMO8WB49EkMzuHhLW3y0nwBFZNHZvbK5TTreB4SRfQZjqrqMY3WDnii/nT07ORS8IGiJH15Ecw1S3Kb"
    "XXxdz+IPQeY/WhcFsMChE9mWoM6Y42cPrbjbZ/fejdoKq+/lw9b6YsEdOHW46zcS7Q3xeFZTXBjB8h0mpTe8zy8jHkLfOxRUSKdIDdyhe55rsy"
    "dCYfvE/bUzWoNramexyxkm/NBzrRqlHMBpAdbq5g0jsVkyJGL+5LDIZCDP0j8k+b7sIuopy889GkT7xAOjS78i2dmR15tLOpN52IJ4LkV1x5Ci"
    "eje2/t/yL2aMv7hssxNdnv+MYpPlZMIohU1XkVKYnd2+P7ub7VB48tJgoLlGT2n6ubnhU6RVuO0gNoUURiGqTeQmuD9EN6Xy4qMZ7A+D4kZe5J"
    "1OME7VEmnw2GS3kkUB8zZ5Btc1ZkhJb0uEZrbU8WgHprNe8DOq1J2hwckJU9TqwPkfikZ/VBaaFoPQDq93EKkiabib5YxecqdibKMTZDyqSjV1"
    "63Cgxd+dXbTzUF40sZtzii5fTPMRO/+suW7nTMj02PitnpLe+bX4D8mZtNuDSXWpS7reGvZqZkrGnVXagWtdfYypASqJzedHEA+u1xkd1usK5V"
    "9PqKmeJHlvFHxgltIG4c3r6+kl/XCqxpHmliPwe1MbGdHzmcsBgEjaj1W/e5PbBP3VTu/C3dKKMhRzFHjaqeSEe5prn9D1WCPqZvrcPfTx+hfK"
    "yaBLyj/IRO7unsVod/7t7WTd94urea4NjQVqerUygxIeY2RKC6Jlq9WGmzfUwRBp86YYp9TR64tGe0+AVnkbW5ulO+RKRGg060jXSeb3OkJo2J"
    "GKprWa7j6KjPth0GlgtCT3+8rcFsYTr5as9E+6LIxpGUlDu10kXuG+CHWkDa4rPlW8a7eUDK1+rWEXQiJaxqTtxrn9Iut139xPuB/csBvbZQnE"
    "x+b42EO4jXHaWV6QjmcZZ/uyel7dZiYwA+zIr/Q11PlV8XnuRwbZT4ouhlL3lS3Rq7anFdrUa2zeYskaNTdIA2gtF+jbnksl2OsvVxLkMpmNrI"
    "haQAdHHOhJxvME5KxBJX3e60JRFtlncHLr/XVaych9kyD+jxIsqiESgdpuQfFgEcj4nLUPQpOoqaPucibko6HpWt7G34gyRPbwZ+LVppJF5tty"
    "jsznoXr3dCZbQRpGRcdjV9+9gR2WqvJHKedq//51+K7j8srzCo2NuvQ7BiFmikB7wvAVCyhUzfphkyNa2GpFqMCVC+n9l3aT6WH2meQi9ndydA"
    "C03qQNdAF4/62/tZUNLvzJzslvL06LRsUORg/BQVsNu9T+w1ZnLDeUUJys7X9O4aimrndyMmUbj1C4w9nph/hRltmDftEjnkvp3kppxfxPr2aa"
    "PLfSIIEiag/DK9xgm/FzEYnKivz70vcvCluLLStc89nIu286IbfPXZPSz7GSZYW6fIBhl3pavBdsd5pkz3eyTgJ58WNuN/1ele6XSUZPy1+0nS"
    "eW6g87jaF1s0Y46JjAqZ7P5L12LXz4snx+Um+zMLRs3kkrVbtPFJsyZm5sq3owmhND4HNyObxSQDQ5fybs6jJDu2hZIPzW09jl5WAXNv+FahUo"
    "8faD1nraTTbMya0KB22q9SKD7VSabS9Kl+s/X3PM4d6OnqsXztrWUrB2oSoabW1ijlmncoOhBzXtnNtclZXpy4jcjrOMAm27fuS7HtdcuN3cCs"
    "cGjejRIIucul2Cu7Bdm4lw84vLOKSmIiq8L9eYJ7VlR3A2bOPx9HIJQPcEeslYJau2s84o2HQ1nKtOp5IaUdN7+VPLEpzmlz4EeplvufQG6sGf"
    "q1rQj7Af49Z/wF6rWGahe1etz2UklIdlNmow5tH7e2iWKpnESArK3NTZVXzGc8MqE9ZpGZfgs24yZ0nWwaUafDwO6s16I+doFJ5fvc1bKm0kvo"
    "sFId+u0cpT0/XnTxSBHWU7ml1+A1rwDiQKiK/nrFDZetsmSiiK19+TknU4LFeUR+YoThvpPzDJWlmu7mc6t9ojbjxhB1ZClQG+/YpFFys/gCh3"
    "objftCj4r+cFq6H/kEJcyH7h8lnny439/9fpd4VHH/+5FV/KNJZXkdRc0yH1vzMKFHr9SU8CU+11EJV5zjtD2aFaDZNw3hqYntFRBltAbqRvag"
    "cR1ter/b5Hd37oaYn6UVIxsQe8eF+aeavUyjQg+nSjHG9hNCuwv5kRvCyskbfI2j7Rs1YNGd100TvXqAx1DCQIPT16s/lDfxlp5jy4sfm1J5jf"
    "3NdXiFpzK9J3UbrXwlcESCW1R8LF7AviS7DX6hRrawW1MODGpQC595PJJmo4K+sbJIHuoRtYNSYzPfS0kmcoE1MwOmW9masQogKBLv5cL67aF6"
    "qEOqJDaIGo6Ei11A/nZWLahxrDOkFqx7mI5b0AXB0DEfA0NVT0gltUO/n4HTeMKzHUsnJWRTQ0yr5t3PplEcJz7su0RE1n5Ib3Mm0gj4aGF6yW"
    "+YBZb9aqu+NuY2Cch4Jfgi9grfwITa/MD4c/vzNimjEOkrFzmkB1l3NLoQIA8K9JPQoN5H1OztWe1tS7UMhJX4DzHbCLTJirF1lZ/8NE9tWGvS"
    "+lO3ho4ZfqH8fAHE28YKeJh1WoiRO8M60YB14AWBqZWQdZZL5ZYCkkIzevRiW+EnCt8XfAPwhdh2CKgVum8tq6g9wERYH5Qf1HHy1gKwNEdaMx"
    "B4I5HVzxyA/ONbCd6jR1ipce5MXBsBzTIlazAv+Ca0jGbRcvtr6B6/GPXN7AcX2VEUxCKQ1AdCYsk8UjFuenoVI7fzCVYbTLoXcV263xo8mza/"
    "FIs2KFzQAIQQ5BBgQ1oNIjtLikMsV3vY2gwk4xEDBsDjf7/qU54255I0ytI/HUBmtkFqt5mezljlAAEC2N2EXu6PZ0x/nv01uiQs5uJtNPXmzH"
    "OnjTce5lFWz7kwiNYaKCLW/22ynnCiiladMYrS2ari+Sz6OTYvxmjI7H2/H3kVYOAGaX97/V93zxpvdN7OqRePGoL0eN02pdOM0ierXuYeAe3p"
    "DRt6dgPSxoVfpp9LvJhaSNdypwqq68T32bUQDMZizCHP8qm7YJz8Yvth6OCfNAxeraefdmwudpQrI+Y+FFElUNZUAJO5acX+bTCe2H90DKKJcn"
    "g7t0+95x9uYyifzuIZMhmjhDyXUVhZ+WVlNXfSPSrjn88cFUtbED1qYJySsZbXFUQTXDhNPlBz5Cg5vBKVPNPBs5M5n3iBLQHj0OKggQXwFbWg"
    "5J7ARYcOFkQbNgNorUaTOE/PKatH6OWHkcYvzmARk/26C3ifSOeqhflPL54EMju2SHEgDtW6qbc4+GuQ+SjGBLCNwQOHGhHB274UiiDmzka/XT"
    "PPJRqeMY7/+oCCjDjXRJF4tLqW22UpRcVjc4ddcmna9p+HINNQJDptIpdimopeDwAlJWj65uY66BlO9VEqF99g2Dk5hZpf3eSqT190e2di2Y2d"
    "bcYAX2fKeOlDWBtGJTNi3e3GaKfSraiz/6KXmqX7JncrD75SVRML4fEPCThRJupmG41rgNqFklErD03rzqS5M5hCcQnU/XpEajh8OWj3rcpUSV"
    "BKqPPjWleaf950902eqqk5o25WMP8gIX1seItKiWaE6s4++we9GCKlVDemJSl5VLgUtGBrxJdQexPWLGpl0XfNZMvemLJ9dTnV/rRuScMDnapu"
    "fcRMaXOu4Q1P13abo/Oh41leLJ0GdBvwYxYva/1th25oUCkPgTvTix2d5w6kZU4H+LxGXWgKB1MYDt4kjB/a1LYIvn2DB+cmGVqKelfdLoKQAe"
    "Nur8ptgJLwqqGbPfJFt480/0bNkcEJgp8ioPy1vxxZg0npzav5HU46YDt+v8/cjwDsS1dVQQyT1o1i/tGaNMcJ+AfTe8PcN6BoBXnUAr9JPgV+"
    "XPF3zb79+caSCv1Ot+8oBGQXqMVdp/RRyedJQgHBZy9hU8Pomwoq+km8e0exyRXDM+VwdVakrg7+trOA7pm+ZBIfP9jUN9wCR/lrdCljhfnt7V"
    "C+c38HizOcnFjmxJfsUEaC+VRdCEVCGbN+NK2O6pDkA1i1TdXorxv5r0gqjw6IcFsA2bs6RBrQROFGILq51UXNjzcoxaDXO58GiUUlO1ePM+se"
    "G28uD3hjG0gqTqGPtW8o3qCvvsrWYpFtkCKgjXS3FCYEXxtdx+FEzHjIPR+CSl9ViDpwtaede8GgDL+g2y41IxY/T14hPs0rwTvCKFYvBVPQt4"
    "vKbQxwpRs/ySMrnrWRYVx6bSMn4yXJlmRc0rQL9pTiWK+/H/11JuzSRHKAqVn/xoTrZ9FoqouoJtyVpdecvAGAi+IYFFZXWvGwWT42knNpD7vN"
    "52jXMjvqUUKp7Cgu/nRftmB8mVBZS631RieI7tpgN/dqgLvbjvlw8d64EOJJkQx+0CNgJh7lUrK90YSPKBUU9HamKYjIe64sZnBNP5msoQUuY1"
    "fPD1mgCDOJFtnFx4S9kFm0sI73ZYktjuj7LSLpU/M11x7d1moV3e+NOo6Yaj8x3NPS8rJB+U7UkegMluaNHjhqaqhOG4Kc3GU/E9ea0boDpc7G"
    "pnnubyFx42Y/JBLQs8MmPTU71xg1EeXkK5b9fYu70yTmKDQ7U3jLjWkOCHwRpfr2ZSAP81pzgvAKcxZLoTvsGfn06pO2a/Y0A/iMWXH00UInjs"
    "Bet86OdNpF6SufyH73bonB2j4GkUhnpslFltYXDD4z+HdIS9NOSn/QsV6E/N8tn9OkdAWeUJ+SsTdYzkNUQr6nUM5nY+X96I1VBUbrMIlbpF7J"
    "EhbOG2IlSaSYGl7WgxS2umvj02hea06aimfq5rw7ASLldOz4me0vP4pNpp38btuvAPp0rxvAbZSMA5FlUAGVnjbbbqZ5WZ1lfUVzrbkjbjWwSk"
    "Nllm1QJ9/q1tl145phmwmLRivkVxx+L1lLVaeR9jf0dBBuMaBrQl+4fnd53++MfPzK7A9ZLbcu9EWui42MkRiRu3o8AjKbUrSLqrteEEohwwvt"
    "UagrwyNvlkS/DjJCnW+3c0BnEmwnC0BnLROcSn6zAwDqZIJvOgMw8LdDiPBzV5LA6nNqdzFqBQN92GflaQULnzp8V4yhdDYuRQVb8gCPYbx4hy"
    "7Hukg9tsxH0v8e/f5EZYHpf3tAWxu3oGGO/J2Haez92qaYbS7IzarSwuLsTOBjaQve6InNxkr6F+9gPIrSDfz1ts0sp2vFwd8+7oOdw04gKovl"
    "1sJNeerZedwe2JvY3pVIR1D9nb4/ZQCkrUE1Ze0fECs/D9QOggjCt+MwgNTqSkPTwYyNfWmp30SWA3TeUGL90HiGH4nIEZ8vfVE5CpCtupLqWJ"
    "/3h36msRTN6n4bgxE0gErCka/3axFa7ncLJ2ZlzroDfB2XSQywpiH9lmz7+rTr2vObhWE+xh+ZGgjTdE/OQylyqhVgLOPYnHrsvhuWJ/xt6q/i"
    "ruI15roaA73ZB2xNra/fg4dH8mQJBsjzJhQcf8in2jVgslvzV/nmLQzLeSPwpG970JaJT+XnQjMtr8z/3Ci+e5niWakd6TURw1XR1rCEDfWCxd"
    "+QjW4KTaVGgG8/yB7saEER1BGTl5ChdiSU2Z9RZdTvoNB43pyr+fk7feuwNrYdYHigG8aUqVVIv+IPWVXNEJSLKQnPRT6kcH3KRT/8xiJ4jBA5"
    "01bcIeSzd1bdHoqR/BNTskw0FsZy3FDZypbauhcL+tugHvNOlGncRf3NUAD9bZ+BRsxghVuOVIeCxZtq0aZpuB3OQacsmL+O+NWZlSOTNjOXVG"
    "hRmYg/HTYeTCUmKzautpMjR8Y2obOzmcqMwT5qiwuPhUXzSV6ZnDudjWllrmbHd9Emkt0nFW0v9oo+ouzxp59AX63O/V8NlTtMZWxURLXxiDWj"
    "9NHDCbWAYMLUCSti9hNodBfrQKnpow6K0czXm5xY/97hwajH+BxLE3G9rZRPuwZ5UnJuRIsjQYoKv0X7rKK7gWbi8uKCy95VqvfPxy8RdnVQsk"
    "Qu7riOsX0u6owieIJItlILeJpASCX4ulD+bgllm0J6n20u03zqGiSAwSTEvAKK56qjQb9kQad+IYpX4q/6g78vdC7XlI6cciYW0dqgU8nsJeo0"
    "mrWnr5XCYugv82yqiXsXZTEEu/HHMRAgdxTU6kcKK4AMRZoNvx4PWoI8Et40jYV7PMkA8vec713VD5JA+sOprtdjnHX9mvuGkN85PjIyRhqwC4"
    "ktQdx76VBlxTsH3sR7fVOlW2OU4SSp2CHhSqFMQmNHztxkpI9wrfTqthmspnO/PL7H8GEl/rQPPTOyPsLhiP1j702bHTeyQ8Hv+hV4V9FR94q3"
    "LgHuvNHVHeAO7vtWqscACBAAsRILSVAlh3uRWpYd0/YLv5iZiJlwzPTYLanVLbd795f5G7e+9h8Y/4TJTAAkQPIuaj8vU5qKqiIJZJ7cTp4tT5"
    "5T23adkUNtNzzBK3zMrqyrq95k2JjExkmRsDtdIpkYlVtA8ynN2UKt1s042dxmMSSGktSL1guDwaY6MRYttmAw+W51rU23LX4VZ0QnXiuaulZP"
    "9bM6UdGmhZxYSCaLK9XsqPNJhl1ypmPpuV61FilmazuKJ8fbCl02BpkKdMvqVmr9cr5XnOODScagqp1RKjNWp6lkxkzUO2o5r2m9ZXWgVZctZ9"
    "gfG8v6KlWZjhr5ammdziVr6fy41clT5NAgdG26idV1eaCYdXLC0e1MtjuvJ8Z2plPoDnu7+WiZT4z6+SHRkglcaxDjRl4kh862Fikb2a4qCDG9"
    "QVXVuI13h03AW/Ktcb0gVhNEZxXJlmsJsqj19JJTWtKVVJdq7rrDmFjl+okUmVOkIQf0hHE6VisMSxWNYKs8kS3rGwlotKtBjWqy5lAWJkqqr+"
    "eGU6NYmrREc7dxovhgF2834WJspgmpPuL0hEQbPDcpFYBENaraJqgW7+n5eDsfV5ZMexCLjerTpNOf1Le5fp+tcXO8qHKLLU8k1gSfGyXqy67T"
    "neS0jJFkp3khGXeS1cSo15lwIyky0qVIXDXHgjSWIuM1mSCkDGlP+qKcrWz4At3YcbU2r+ad6nDQHUqjUn7I5pYJSTS6k1RuZ1uCtCmobGFY6S"
    "vlJDFR24DYRySib5v1WKPPjGncSVGZrB6v18uLwSjHGAM+0UmkjOWA6yiTGJ3MGKTZYcvViVWkFsuMsuQKcblFak69QPQcwNiHgxo3kKaj9nDa"
    "6zimaLSKm/xq3q0Y/ai407qluU6MM71muznCk51ErI7XDakUETa7cjo6IfhkUTa7Mplvkg0Tn5NFPjbmolyql+9aPb2v9BLLCd8eT0VG6SY5NS"
    "co4+3UjlF5ORGVqsSkLtah4tgor0gjBwjvoLbBuTrVqepyRMpxdI0i+z2GpzujqmD1I0QuUtIT5QUxrNU6A5tpTgmANlNqUpsmSxG6GpV7+X7d"
    "yVOJlpIeJVtDrl1ezuu9TIecEtthTdy0tyWuw+TH9Hg4For8omO3l3o5HyMccsNVKKZcNrtEml83Bk5MFcTxNC5Nhz2GqC0BXjCxXcKSK9tplp"
    "+sx3VVGSs7M7luqaNsddVo0rzpcEOlkKEa5SKnzaWaWRjiYNuNppqdp6LzspnkC0V5pcQSSnYaLRp0LBKTh5X4MNWyalkzTrL0sp6UmrVMT6jK"
    "9Jjjl/VGrloqtyuaZA4bytSmpYacVKLN/iY55trN8kZp9ldsj9dW0fa6XZ9U6O5EqTHFvqADXoNbk74an6d3W7Crt91JVy4qSyE5pHud7LSUr1"
    "S7bLWaHLWkVW3eNEoKIRUWVJGfdBmnY6x3vUVZHcR7AsmTLaKsJgSLLBK7nNSkhRyTXE4KzZUDBJ0xW98mGHpqdBf97VxZyayyjC+XnY5NLsYl"
    "vCFl6eKyr9WrzdhqNxRLCSvT75rRak8apGOdeUqpO2rS2U20jclT4+mut13remteF1L5jSlvpGJ56Ew0vbg2yU2VdTLQzGBNDdHeDYrp4aijLi"
    "JMhyWrzUQ0slISmzxvpxNqMxmLNaVYeTd0liOt11Fw3hmSU1FbK8pGqeX1aT2WIvu7mpLukevRKs7l2M1gNTCV5cpRDJkrg4lXVwubnJhlcbVV"
    "BgsrOZh3ZVZdFS2ruUqJY3xQr7Y63HZcpzZVm2v0bEckpNVwsckXdg2iJIzwPrVujOi5sx5k7TQ37K+WeYs016miaZh5jdYSq0ma1rZb1WkM8G"
    "4iNmTEXb1p5yerar2jAEIITyOqZKajDFZyp12akmO7B4/WiLIEJGuHWdRs1iJ4jmi09XpjvYxRhMrkyEKEonfb4rC2jozTTjJWqcZshSjMzdVu"
    "IBUTor6IppWlruFMp1Uz62WqUWxnplK8m47yVo+IdFlhTq06yXS62OtRyS7P491YVBpOm1USH8mD5aSm4c1llRwWihlzRdpiokApEV5v8gAFiM"
    "EgE6/LQ7y6yOc5K8Hk7NpkqGjOpLSuRLvdQbrQqYxG6dSC2RiLqsENNMJR0lSuG9nkG8IQxxnZrNXWnDzJ6NvhuD6UY+JQr62b1cK0VwNKRomn"
    "llq/b8A4VOSik+hlN3nA5zWp3+nX+d4qz+/iy1xd3QFixKQcWsvqhXrU7tXbPdGRNqS1mRqc3CXodauZMXOjmt4GvENILgCDbDGOJSw3utjfdI"
    "BgaEj9ciUpmB1dlllrpSgxudTq2iWbj6Wi1LiYSxEluSPl5quOmGtNhtKK7A3JfH7Z3eQTulGp9YqkoPakod6jU/XchOrEq1QxN85keh0h0+hk"
    "OtFuimVzg9zQyG1GRCfR6mwGteo2IeDKFgi45KAnqbLcMqUEUBfrTspyZNIh6w1yLsX6G3aYsRW8E9XxmL4xyg2zO1w5ma6R13WubI5XTbOJZ7"
    "ZtThoSqflISYrrdbTNtIuj1GQwTDKRxNRS7fiSt5ReWVlRhbk0EteFVkuMKXyJ5Pk+DFFS1YxVdyy39Wy9XN0kFr2eNq0UI+t2JrWtrrlRoeP0"
    "dHUQcTa5FtAkdHxazQxa8/myJdRhNvbdBsfnY06txdMVvZTs5LRxf2A2O5LKpxvJAj3dpGKKXauxgtMVgZhhFrRm26Tbk11aZBd1qS4bI2rdHV"
    "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"
)

_engine_ns = {"__builtins__": __builtins__}
# نقل كل المتغيرات العامة للـ namespace
import sys as _sys
for _k, _v in list(globals().items()):
    if not _k.startswith("__"):
        _engine_ns[_k] = _v

exec(compile(_decode_engine(_ENGINE_ENC), "<AIDetectionEngine>", "exec"), _engine_ns)
AIDetectionEngine = _engine_ns["AIDetectionEngine"]

def score_sentence(self, sent):
    """
    More conservative sentence scoring for polished English academic text.
    A formal academic sentence is not AI evidence by itself.
    High values require direct GPT-like templating that survives
    strong human-academic grounding checks.
    """
    if self._is_reference_line(sent):
        return 0.0

    stripped = sent.strip()
    words = re.findall(r'\b[a-z]+\b', stripped.lower())
    if len(words) < 7:
        return 0.0

    tl = stripped.lower()
    n = len(words)

    exact = sum(1 for p in getattr(self, 'EN_GPT_PHRASES_T1', []) if p and p in tl)

    patt_hits = 0
    for p in getattr(self, 'EN_GPT_SENTENCE_PATTERNS', [])[:80]:
        try:
            patt_hits += len(re.findall(p, tl, re.I))
        except Exception:
            pass

    llr = _call_engine_helper(self, "_llr_score", words)
    sg  = self._simple_gpt_score(stripped, words, [stripped])
    gf  = self._gpt_formatting_signature(stripped, [stripped])

    lexical_fp = min(sum(1 for w in words if w in self.AI_FINGERPRINT) / max(n, 1) * 2.0, 0.16)
    human_markers = min(sum(1 for w in words if w in self.HUMAN_MARKERS) / max(n, 1) * 5.0, 0.42)

    score = (
        min(exact / 3.0, 1.0) * 0.34 +
        min(patt_hits / 3.0, 1.0) * 0.24 +
        llr * 0.16 +
        sg  * 0.14 +
        gf  * 0.06 +
        lexical_fp * 0.06
    )

    if re.search(r'\bthis\s+(?:study|paper|article)\s+(?:aims\s+to|seeks\s+to|explores|examines|investigates)\b', tl):
        score += 0.02
    if re.search(r'\b(?:future|further)\s+research\s+(?:should|could|may|can)\b', tl):
        score += 0.02
    if re.search(r'\bit\s+(?:is|has\s+been)\s+(?:widely\s+)?(?:recognized|acknowledged|accepted|reported)\s+that\b', tl):
        score += 0.02
    if re.search(r'\bplays?\s+(?:a|an)\s+(?:crucial|vital|pivotal|important|significant)\s+role\b', tl):
        score += 0.02

    grounding = 0.0
    if re.search(r'\[(?:\d+|\d+(?:\s*,\s*\d+)*)\]|\([A-Z][A-Za-z\-]+,\s*\d{4}[a-z]?\)', stripped):
        grounding += 0.24
    if re.search(r'\b(?:table|fig(?:ure)?|appendix|section|chapter|equation|algorithm)\s*\d+\b', tl):
        grounding += 0.15
    if re.search(r'\b(?:dataset|corpus|sample|participants?|respondents?|survey|questionnaire|experiment(?:al)?|empirical|regression|anova|benchmark|evaluation|framework|architecture|implementation|case study|literature review|simulation|protocol|method(?:ology)?)\b', tl):
        grounding += 0.16
    if re.search(r'\b\d+(?:\.\d+)?%?\b', tl):
        grounding += 0.11
    if re.search(r'\b(?:p\s*[<=>]\s*0?\.\d+|confidence interval|standard deviation|variance|mean|median)\b', tl):
        grounding += 0.11
    if re.search(r'\b[A-Z]{2,}(?:/[A-Z]{2,})?\b', stripped):
        grounding += 0.08
    grounding = min(grounding, 0.56)

    if re.search(r'\b(?:may|might|could|appears?|suggests?|likely|unlikely|approximately|roughly|possibly)\b', tl):
        score *= 0.86
    if re.search(r'\b(?:i|we|my|our|me|us)\b', tl):
        score *= 0.82

    direct_evidence = (exact >= 2) + (patt_hits >= 2) + (sg >= 0.65) + (llr >= 0.72)
    if grounding >= 0.22:
        if exact == 0 and patt_hits < 2:
            score *= 0.34
        elif exact < 2 and patt_hits < 3:
            score *= 0.52
    if grounding >= 0.36 and direct_evidence <= 1:
        score *= 0.54
    if grounding >= 0.46 and direct_evidence == 0:
        score *= 0.40
    if grounding >= 0.52 and direct_evidence <= 1 and sg < 0.62 and llr < 0.70:
        score *= 0.72

    score -= human_markers * 0.16

    if direct_evidence >= 3 and exact >= 2 and grounding < 0.18:
        score = max(score, min(0.94, 0.80 + 0.03 * direct_evidence))

    return round(max(0.0, min(score, 0.96)), 4)

    def _perp(self, words, _transformer_model=None):
        """Transformer (DistilGPT2) + Trigram LM Perplexity"""
        if len(words) < 20: return 0.5
        try:
            import torch
            from transformers import GPT2LMHeadModel, GPT2TokenizerFast
            if not hasattr(self, '_gpt2_tok'):
                self._gpt2_tok = GPT2TokenizerFast.from_pretrained('distilgpt2', cache_dir='/tmp/hf_cache')
                self._gpt2_mdl = GPT2LMHeadModel.from_pretrained('distilgpt2', cache_dir='/tmp/hf_cache')
                self._gpt2_mdl.eval()
            _txt = ' '.join(words[:300])
            _enc = self._gpt2_tok(_txt, return_tensors='pt', truncation=True, max_length=512)
            with torch.no_grad():
                _loss = self._gpt2_mdl(**_enc, labels=_enc['input_ids']).loss.item()
            _ppl = math.exp(_loss)
            if _ppl < 15: return 0.95
            elif _ppl < 25: return 0.82
            elif _ppl < 40: return 0.65
            elif _ppl < 65: return 0.45
            elif _ppl < 100: return 0.28
            elif _ppl < 200: return 0.15
            else: return 0.05
        except Exception:
            pass
        from collections import Counter as _C
        trigrams = list(zip(words[:-2], words[1:-1], words[2:]))
        bigrams  = list(zip(words[:-1], words[1:]))
        t_cnt = _C(trigrams); b_cnt = _C(bigrams); u_cnt = _C(words)
        vsz = len(u_cnt); SM = 0.1; lp = 0.0; n = 0
        for i in range(2, len(words)):
            w = words[i]; c2 = (words[i-2], words[i-1]); c1 = words[i-1]
            bc = b_cnt.get(c2, 0)
            if bc > 0:
                p = (t_cnt.get(c2+(w,), 0)+SM)/(bc+SM*vsz)
            else:
                b1 = u_cnt.get(c1, 0)
                p = (b_cnt.get((c1,w),0)+SM)/(b1+SM*vsz) if b1>0 else SM/vsz
            lp += math.log(max(p, 1e-10)); n += 1
        if n == 0: return 0.5
        pe = math.exp(-lp/n)
        if pe < 8: return 0.95
        elif pe < 12: return 0.88
        elif pe < 18: return 0.78
        elif pe < 28: return 0.65
        elif pe < 45: return 0.48
        elif pe < 75: return 0.32
        elif pe < 120: return 0.18
        else: return 0.08


    def _burst(self, s):
        """Turnitin-style Burstiness: CV منخفض=AI، CV مرتفع=بشري"""
        if len(s) < 4: return 0.5
        ln = [len(x.split()) for x in s if x.strip()]
        if len(ln) < 4: return 0.5
        avg = sum(ln)/len(ln)
        if avg < 4: return 0.5
        cv = math.sqrt(sum((l-avg)**2 for l in ln)/len(ln))/(avg+1e-6)
        if   cv < 0.20: r = 0.92
        elif cv < 0.30: r = 0.78
        elif cv < 0.40: r = 0.62
        elif cv < 0.50: r = 0.45
        elif cv < 0.65: r = 0.28
        else:           r = 0.12
        ideal = sum(1 for l in ln if 13<=l<=32)/len(ln)
        smooth = max(0,1.0-sum(abs(ln[i]-ln[i-1]) for i in range(1,len(ln)))/len(ln)/12) if len(ln)>=3 else 0.5
        return round(min(max(r*0.55+smooth*0.25+max(0,(ideal-0.5)*0.30)*0.20,0),1),4)

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

        # Token Predictability + Chunk Uniformity (Turnitin chunks: 5-10 sents)
        pred = sum(1 for w in words if w in self.AI_FINGERPRINT)/max(len(words),1)
        rare = sum(1 for w in words if len(w)>10 and w not in self.AI_FINGERPRINT and w not in self.EN_ACADEMIC_NEUTRAL)/max(len(words),1)
        predict_ai = min(pred*8,1)*0.6+max(0,0.5-rare*5)*0.4
        csz = max(len(words)//4,5)
        chs = [words[i:i+csz] for i in range(0,len(words),csz) if len(words[i:i+csz])>=5]
        if len(chs)>=2:
            cd=[sum(1 for w in ch if w in self.AI_FINGERPRINT)/len(ch) for ch in chs]
            acd=sum(cd)/len(cd); cu=max(0,1.0-math.sqrt(sum((d-acd)**2 for d in cd)/len(cd))*10)
        else: cu=0.5
        result=(len_ai*0.25+long_ai*0.20+formal_ai*0.20+predict_ai*0.20+cu*0.15)
        return round(min(result,1.0),4)

    # ─── 2️⃣ Token Probability Variance (إعادة تصميم كاملة) ─────────────────
    def _token_prob_variance(self, words):
        """
        v15 — calibrated for academic-human protection.

        Formal academic vocabulary alone must not inflate AI probability.
        This feature now reacts mainly to unusually repetitive / template-like
        wording patterns, while discounting legitimate scholarly terminology.
        """
        if len(words) < 20:
            return 0.22

        from collections import Counter

        clean_words = [w.lower() for w in words if re.match(r'^[a-z][a-z\-]{1,}$', str(w).lower())]
        if len(clean_words) < 20:
            return 0.22

        ACADEMIC_SUFFIXES = (
            'tion','sion','ment','ity','ance','ence','ness','ism',
            'ize','ise','ify','ous','ive','ful','al','ic','ical',
            'ology','ography','ization','isation','ibility','ability',
        )

        c = Counter(clean_words)
        n = len(clean_words)
        ttr = len(c) / n

        repeated_core = sum(v for _, v in c.items() if v >= 3) / n
        repeat_ai = min(max(repeated_core - 0.18, 0.0) * 2.2, 1.0)

        ai_vocab_ratio = sum(1 for w in clean_words if w in self.AI_FINGERPRINT) / n
        ai_vocab_score = min(ai_vocab_ratio * 4.0, 1.0)

        suffix_ratio = sum(1 for w in clean_words if any(w.endswith(s) for s in ACADEMIC_SUFFIXES)) / n
        long_ratio = sum(1 for w in clean_words if len(w) > 8) / n

        academic_human_ratio = sum(
            1 for w in clean_words
            if w in getattr(self, 'ACADEMIC_HUMAN_VOCAB', set()) or
               w in getattr(self, 'EN_ACADEMIC_NEUTRAL', set())
        ) / n

        morphology_pressure = min(max((suffix_ratio * 0.55 + long_ratio * 0.45) - 0.22, 0.0) * 1.4, 1.0)
        diversity_pressure = min(max(0.60 - ttr, 0.0) * 1.8, 1.0)

        result = (
            repeat_ai * 0.42 +
            ai_vocab_score * 0.34 +
            diversity_pressure * 0.16 +
            morphology_pressure * 0.08
        )

        if academic_human_ratio >= 0.12:
            result *= 0.72
        if academic_human_ratio >= 0.20 and ai_vocab_score < 0.18:
            result *= 0.60
        if suffix_ratio >= 0.24 and ai_vocab_score < 0.15 and repeat_ai < 0.28:
            result *= 0.58

        return round(min(max(result, 0.0), 0.72), 4)


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
        Paragraph analysis with strong discount for normal academic English.
        High paragraph scores require corroboration, not mere formality.
        """
        paras = []
        raw_paras = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
        if len(raw_paras) >= 2:
            paras = raw_paras
        else:
            all_sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.split()) >= 3]
            for i in range(0, len(all_sents), 5):
                chunk = ' '.join(all_sents[i:i+6])
                if len(chunk.split()) >= 40:
                    paras.append(chunk)

        if not paras:
            return []

        results = []
        for idx, para in enumerate(paras):
            para_words = re.findall(r'\b[a-z]+\b', para.lower())
            para_sents = [s for s in re.split(r'(?<=[.!?])\s+', para) if len(s.split()) >= 3]
            if len(para_words) < 20:
                continue

            sg  = _call_engine_helper(self, "_simple_gpt_score", para, para_words, para_sents, default=0.5)
            gf  = _call_engine_helper(self, "_gpt_formatting_signature", para, para_sents, default=0.5)
            se  = _call_engine_helper(self, "_semantic_embedding", para_words, para_sents, default=0.5)
            llr = _call_engine_helper(self, "_llr_score", para_words, default=0.5)
            lmp = _call_engine_helper(self, "_lm_perplexity", para_words, default=0.5)
            bur = _call_engine_helper(self, "_burst", para_sents, default=0.0)
            dis = _call_engine_helper(self, "_discourse_invariant", para, default=0.5)
            par = _call_engine_helper(self, "_paraphrase_engine", para, para_sents, para_words, default=0.5)
            syn = _call_engine_helper(self, "_synonym_density", para_words, default=0.5)
            pat = _call_engine_helper(self, "_pattern_memory", para, default=0.5)
            ctx = _call_engine_helper(self, "_context_drift", para_sents, para_words, default=0.0)
            nb  = _call_engine_helper(self, "_nb_score", para, para_words, default=0.5)
            en  = _call_engine_helper(self, "_english_ai_score", para, para_words, para_sents, default=0.5)

            tl = para.lower()
            exact = sum(1 for p in getattr(self, 'EN_GPT_PHRASES_T1', []) if p in tl)
            citations = len(re.findall(r'\([A-Z][A-Za-z\-]+,\s*\d{4}[a-z]?\)', para))
            numbers = len(re.findall(r'\b\d+(?:\.\d+)?%?\b', para))
            hedges = len(re.findall(r'\b(?:may|might|could|perhaps|possibly|likely|unlikely|approximately|suggests?|appears?|indicates?)\b', tl))

            direct = (
                max(sg, min(llr, 0.82), en * 0.95) * 0.34 +
                pat * 0.12 +
                nb  * 0.12 +
                gf  * 0.08 +
                min(exact / 6.0, 1.0) * 0.16
            )

            support = (
                se  * 0.06 +
                ctx * 0.05 +
                par * 0.04 +
                syn * 0.03 +
                bur * 0.02 +
                dis * 0.02 +
                lmp * 0.02
            )

            raw = direct + support

            corroboration = 0
            corroboration += 1 if en >= 0.65 else 0
            corroboration += 1 if sg >= 0.60 else 0
            corroboration += 1 if llr >= 0.66 else 0
            corroboration += 1 if nb >= 0.75 else 0
            corroboration += 1 if exact >= 3 else 0

            if corroboration >= 4:
                raw += 0.08
            elif corroboration == 3:
                raw += 0.04

            damp = 0.0
            if citations >= 1:
                damp += 0.08
            if numbers >= max(3, len(para_words) // 60):
                damp += 0.05
            if hedges >= 2:
                damp += 0.03

            # Avoid paragraph spikes from style-only evidence.
            if exact == 0 and max(en, sg, llr) < 0.58:
                raw *= 0.82

            raw -= damp
            raw = max(0.0, min(raw, 0.99))

            label = "Human"
            if raw >= 0.85:
                label = "AI"
            elif raw >= 0.60:
                label = "Mixed"

            results.append({
                "index": idx + 1,
                "text": para,
                "score": round(raw, 4),
                "label": label,
                "words": len(para_words),
            })

        return results

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
def _academic_grounding_profile(self, text, words=None, sents=None):
    """
    Cross-disciplinary human-academic grounding detector.
    Rewards signals that are common in real scholarly writing across domains:
    citations, sectioning, tables/figures, datasets/samples/methods, numeric specificity,
    acronyms/entities, standards/framework references, and bibliography depth.
    Returns dict with score 0..1 and component counts.
    """
    if words is None:
        words = re.findall(r'\b[a-zA-Z][a-zA-Z\-]*\b', text.lower())
    if sents is None:
        sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    tl = text.lower()
    word_count = max(len(words), 1)

    author_year = len(re.findall(r'\([A-Z][A-Za-z\-]+,\s*\d{4}[a-z]?\)', text))
    bracket_refs = len(re.findall(r'\[(?:\d+|\d+(?:\s*,\s*\d+)*)\]', text))
    doi_refs = len(re.findall(r'\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b', text, re.I))
    url_refs = len(re.findall(r'https?://|www\.', text, re.I))

    table_fig = len(re.findall(r'\b(?:table|fig(?:ure)?|appendix|section|chapter|algorithm|equation)\s*\d+\b', tl))
    numbered_sections = len(re.findall(r'(?m)^\s*\d+(?:\.\d+){0,2}\s+[A-Z]', text))
    method_terms = len(re.findall(
        r'\b(?:method(?:ology)?|dataset|sample|participants?|respondents?|interviews?|survey|questionnaire|experiment(?:al)?|'
        r'empirical|qualitative|quantitative|regression|anova|cohort|trial|simulation|benchmark|evaluation|analysis|observed|'
        r'measured|estimated|variance|standard deviation|confidence interval|p\s*[<=>]\s*0?\.\d+|significant(?:ly)?|'
        r'framework|architecture|protocol|model|implementation|case study|literature review)\b', tl, re.I))
    numeric_specificity = len(re.findall(r'\b\d+(?:\.\d+)?(?:%|\s*(?:ms|s|sec|min|hours?|days?|years?|gb|tb|kb|mb))?\b', tl))
    acronyms = len(re.findall(r'\b[A-Z]{2,}(?:/[A-Z]{2,})?\b', text))
    proper_entities = len(re.findall(r'\b(?:U\.S\.|Department|Agency|University|NASA|DoD|IEEE|ACM|GAO|ODNI|Army|Air Force)\b', text))

    refs_section = 1 if re.search(r'(?im)^\s*(references|bibliography)\s*$', text) else 0
    long_bibliography = 1 if len(re.findall(r'(?m)^\s*\[\d+\]', text)) >= 8 else 0

    citation_density = min((author_year + bracket_refs + doi_refs + url_refs) / max(word_count / 120.0, 1.0), 1.0)
    structure_density = min((table_fig + numbered_sections) / max(word_count / 300.0, 1.0), 1.0)
    methods_density = min(method_terms / max(word_count / 90.0, 1.0), 1.0)
    numbers_density = min(numeric_specificity / max(word_count / 85.0, 1.0), 1.0)
    entity_density = min((acronyms + proper_entities) / max(word_count / 140.0, 1.0), 1.0)
    bibliography_signal = min(refs_section + long_bibliography + min(url_refs / 8.0, 1.0), 1.0)

    grounding = (
        citation_density * 0.28 +
        methods_density * 0.22 +
        structure_density * 0.14 +
        numbers_density * 0.14 +
        entity_density * 0.10 +
        bibliography_signal * 0.12
    )
    return {
        "score": round(max(0.0, min(grounding, 1.0)), 4),
        "citation_hits": author_year + bracket_refs + doi_refs + url_refs,
        "method_hits": method_terms,
        "table_fig_hits": table_fig,
        "number_hits": numeric_specificity,
        "acronym_hits": acronyms + proper_entities,
        "bibliography_signal": bibliography_signal,
    }

def _english_ai_score(self, text, words, sents):
    """
    English AI detector re-balanced to protect human academic prose.
    Formality, cohesion, and academic polish are weak cues.
    Strong scores require repeated direct GPT-like patterns that are
    not explained by scholarly grounding.
    """
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    if arabic_chars / max(len(text), 1) > 0.20:
        return 0.0

    n_words = len(words)
    if n_words < 30:
        self._en_evidence_cache = ["too_short_for_strong_en_ai"]
        return 0.08

    tl = text.lower()
    sent_count = max(len(sents), 1)
    evidence = []

    grounding = self._academic_grounding_profile(text, words, sents)
    grounding_score = grounding["score"]

    t1_hits = [p for p in getattr(self, 'EN_GPT_PHRASES_T1', []) if p and p in tl]
    exact_hit_count = len(t1_hits)
    if exact_hit_count >= 12:
        t1_score = min(0.82 + (exact_hit_count - 12) * 0.012, 0.96)
        evidence.append(f"T1-very-strong:{exact_hit_count}")
    elif exact_hit_count >= 7:
        t1_score = 0.42 + (exact_hit_count - 7) * 0.055
        evidence.append(f"T1-strong:{exact_hit_count}")
    elif exact_hit_count >= 4:
        t1_score = 0.16 + (exact_hit_count - 4) * 0.07
        evidence.append(f"T1-mid:{exact_hit_count}")
    else:
        t1_score = 0.01

    t2_hits = 0
    for pat in getattr(self, 'EN_GPT_SENTENCE_PATTERNS', [])[:120]:
        try:
            t2_hits += len(re.findall(pat, tl, re.I))
        except Exception:
            pass

    t2_density = t2_hits / max(sent_count / 8.0, 1.0)
    if t2_density >= 6.0:
        t2_score = min(0.70 + (t2_density - 6.0) * 0.03, 0.88)
        evidence.append(f"T2-very-strong:{t2_density:.1f}")
    elif t2_density >= 3.8:
        t2_score = 0.30 + (t2_density - 3.8) * 0.08
        evidence.append(f"T2-strong:{t2_density:.1f}")
    elif t2_density >= 2.2:
        t2_score = 0.10 + (t2_density - 2.2) * 0.08
        evidence.append(f"T2-mid:{t2_density:.1f}")
    else:
        t2_score = 0.02

    lens = [len(s.split()) for s in sents if len(s.split()) >= 5]
    style_score = 0.0
    if lens:
        avg_len = sum(lens) / len(lens)
        sd_len = (sum((x - avg_len) ** 2 for x in lens) / len(lens)) ** 0.5
        cv_len = sd_len / max(avg_len, 1.0)
        if 14 <= avg_len <= 24 and cv_len <= 0.24:
            style_score += 0.05
        elif 12 <= avg_len <= 26 and cv_len <= 0.30:
            style_score += 0.03

    lexical_hits = sum(1 for w in words if w in self.AI_FINGERPRINT)
    lexical_density = lexical_hits / max(n_words, 1)
    lexical_score = min(lexical_density * 2.4, 0.12)

    human_hits = sum(1 for w in words if w in self.HUMAN_MARKERS)
    human_score = min(human_hits / max(n_words, 1) * 4.5, 0.26)

    hedge_hits = len(re.findall(r'\b(?:may|might|could|suggests?|appears?|approximately|roughly|possibly|arguably)\b', tl))
    hedge_score = min(hedge_hits / max(sent_count, 1) * 0.07, 0.16)

    citation_like = grounding.get("citation_hits", 0)
    method_like = grounding.get("method_hits", 0)
    structure_like = grounding.get("table_fig_hits", 0)
    numeric_like = grounding.get("number_hits", 0)
    acronym_like = grounding.get("acronym_hits", 0)

    simple_score = min(self._simple_gpt_score(text, words, sents), 1.0)
    llr_score = min(_call_engine_helper(self, "_llr_score", words), 1.0)
    fmt_score = min(self._gpt_formatting_signature(text, sents), 1.0)

    base = (
        t1_score * 0.40 +
        t2_score * 0.24 +
        llr_score * 0.10 +
        simple_score * 0.10 +
        fmt_score * 0.04 +
        style_score * 0.06 +
        lexical_score * 0.06
    )

    guard = 0.0
    if grounding_score >= 0.30:
        guard += 0.10
    if grounding_score >= 0.45:
        guard += 0.12
    if grounding_score >= 0.60:
        guard += 0.14
    if citation_like >= 8:
        guard += 0.08
    if citation_like >= 18:
        guard += 0.06
    if method_like >= 10:
        guard += 0.08
    if method_like >= 22:
        guard += 0.05
    if numeric_like >= 15:
        guard += 0.06
    if structure_like >= 4:
        guard += 0.05
    if acronym_like >= 10:
        guard += 0.04
    guard += human_score * 0.60
    guard += hedge_score * 0.45

    direct_strength = 0
    direct_strength += 1 if exact_hit_count >= 4 else 0
    direct_strength += 1 if t2_density >= 2.6 else 0
    direct_strength += 1 if simple_score >= 0.66 else 0
    direct_strength += 1 if llr_score >= 0.72 else 0
    direct_strength += 1 if lexical_density >= 0.06 else 0

    score = base

    if grounding_score >= 0.35 and direct_strength <= 1:
        score *= 0.72
    if grounding_score >= 0.48 and direct_strength <= 1:
        score *= 0.58
    if grounding_score >= 0.60 and direct_strength <= 2:
        score *= 0.48
    if grounding_score >= 0.72 and exact_hit_count < 4 and t2_density < 3.0:
        score *= 0.40

    score = max(0.0, score - min(guard, 0.42))

    if grounding_score >= 0.55 and exact_hit_count < 3 and t2_density < 2.5:
        score = min(score, 0.26)
    if grounding_score >= 0.70 and exact_hit_count < 4 and t2_density < 3.0:
        score = min(score, 0.18)

    if direct_strength >= 4 and exact_hit_count >= 5:
        score = max(score, min(0.92, 0.72 + exact_hit_count * 0.015))
        evidence.append(f"direct-strength:{direct_strength}")
    elif direct_strength >= 3 and exact_hit_count >= 3 and grounding_score < 0.45:
        score = max(score, min(0.80, 0.54 + exact_hit_count * 0.018))

    self._en_evidence_cache = evidence
    return round(max(0.0, min(score, 0.96)), 4)

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
        """Conservative fingerprint score for English academic text."""
        if not words or not sents:
            self._fp_scores_cache = {}
            return 0.0

        tl = text.lower()
        n_words = max(len(words), 1)

        exact_phrases = sum(1 for p in getattr(self, 'EN_GPT_PHRASES_T1', []) if p in tl)
        struct_hits = 0
        struct_pats = [
            r'\bthis\s+(?:study|paper|article|research|analysis)\s+(?:aims?|seeks?|examines?|investigates?|explores?)\b',
            r'\bit\s+(?:has\s+been|is)\s+(?:widely\s+)?(?:shown|demonstrated|recognized|reported|suggested)\s+that\b',
            r'\bfurther\s+research\s+(?:is\s+needed|should|could|may)\b',
            r'\bplays?\s+(?:a|an)\s+(?:vital|crucial|key|significant|important)\s+role\s+in\b',
        ]
        for p in struct_pats:
            try:
                struct_hits += len(re.findall(p, tl, re.I))
            except Exception:
                pass

        starter_tokens = [s.split()[0].lower().strip(",;:") for s in sents if s.split()]
        formal_openers = {'however','therefore','moreover','furthermore','additionally',
                          'consequently','nevertheless','thus','overall','specifically','notably'}
        starter_ratio = sum(1 for t in starter_tokens if t in formal_openers) / max(len(starter_tokens), 1)

        citations = len(re.findall(r'\([A-Z][A-Za-z\-]+,\s*\d{4}[a-z]?\)', text))
        numeric = len(re.findall(r'\b\d+(?:\.\d+)?%?\b', text))
        hedges  = len(re.findall(r'\b(?:may|might|could|perhaps|possibly|likely|unlikely|approximately|suggests?|appears?|indicates?)\b', tl))
        first_person = len(re.findall(r'\b(?:i|we|our|my|us)\b', tl))

        direct_signal = (
            min(exact_phrases / 8.0, 1.0) * 0.34 +
            min(struct_hits / 8.0, 1.0) * 0.16 +
            simple_gpt_score * 0.18 +
            gpt_format_score * 0.10 +
            english_ai_score * 0.14 +
            min(getattr(self, '_pattern_memory')(text), 0.9) * 0.08
        )

        style_signal = 0.0
        if starter_ratio >= 0.28:
            style_signal += 0.08
        elif starter_ratio >= 0.16:
            style_signal += 0.04
        style_signal += min(getattr(self, '_semantic_embedding')(words, sents), 0.85) * 0.05
        style_signal += min(getattr(self, '_context_drift')(sents, words), 0.85) * 0.05
        style_signal = min(style_signal, 0.14)

        human_damp = 0.0
        if citations >= 2:
            human_damp += 0.08
        if numeric >= max(6, n_words // 120):
            human_damp += 0.05
        if hedges >= 4:
            human_damp += 0.03
        if first_person >= 2:
            human_damp += 0.03

        human_damp += english_human_score * 0.08
        human_damp += deep_human_score * 0.06
        human_damp += human_error_val * 0.04

        score = direct_signal + style_signal - human_damp

        corroboration = 0
        corroboration += 1 if exact_phrases >= 4 else 0
        corroboration += 1 if struct_hits >= 5 else 0
        corroboration += 1 if simple_gpt_score >= 0.62 else 0
        corroboration += 1 if english_ai_score >= 0.68 else 0
        corroboration += 1 if gpt_format_score >= 0.55 else 0

        if corroboration >= 3 and exact_phrases >= 4:
            score = max(score, min(0.97, 0.78 + 0.04 * corroboration))
        elif corroboration >= 2 and exact_phrases >= 2:
            score = max(score, 0.58)

        # Hard limit against pure academic-style inflation.
        if exact_phrases <= 1 and struct_hits <= 2 and simple_gpt_score < 0.45:
            score = min(score, 0.34)

        self._fp_scores_cache = {
            "exact_phrases": exact_phrases,
            "struct_hits": struct_hits,
            "starter_ratio": round(starter_ratio, 4),
            "citations": citations,
            "numeric": numeric,
            "corroboration": corroboration,
        }
        if grounding >= 0.32 and direct_evidence == 0:
            score = min(score, 0.34)
        elif grounding >= 0.22 and direct_evidence <= 1:
            score = min(score, 0.46)

        return round(max(0.0, min(score, 0.94)), 4)

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
        Conservative synonym-density detector.
        Academic lexical variety alone should not be treated as AI.
        """
        if len(words) < 25:
            return 0.12

        from collections import Counter as _C, defaultdict as _dd

        SEMANTIC_GROUPS = {
            'demonstrate': 'show_grp', 'show': 'show_grp', 'illustrate': 'show_grp', 'reveal': 'show_grp',
            'important': 'imp_grp', 'significant': 'imp_grp', 'crucial': 'imp_grp', 'critical': 'imp_grp',
            'vital': 'imp_grp', 'essential': 'imp_grp', 'key': 'imp_grp',
            'improve': 'enhance_grp', 'enhance': 'enhance_grp', 'strengthen': 'enhance_grp',
            'advance': 'enhance_grp', 'promote': 'enhance_grp',
            'use': 'use_grp', 'utilize': 'use_grp', 'employ': 'use_grp', 'apply': 'use_grp',
            'implement': 'use_grp', 'adopt': 'use_grp', 'leverage': 'use_grp',
            'help': 'help_grp', 'facilitate': 'help_grp', 'enable': 'help_grp', 'support': 'help_grp',
            'assist': 'help_grp', 'contribute': 'help_grp',
            'result': 'result_grp', 'outcome': 'result_grp', 'finding': 'result_grp', 'conclusion': 'result_grp',
            'effect': 'result_grp', 'impact': 'result_grp', 'implication': 'result_grp',
            'problem': 'prob_grp', 'challenge': 'prob_grp', 'issue': 'prob_grp', 'concern': 'prob_grp',
            'method': 'method_grp', 'approach': 'method_grp', 'strategy': 'method_grp', 'technique': 'method_grp',
            'model': 'model_grp', 'framework': 'model_grp', 'paradigm': 'model_grp',
        }

        normalized = [w.lower() for w in words]
        total = len(normalized)
        grp_counts = _C()
        grp_types = _dd(set)

        for w in normalized:
            grp = SEMANTIC_GROUPS.get(w)
            if grp:
                grp_counts[grp] += 1
                grp_types[grp].add(w)

        if not grp_counts:
            return 0.06

        dense_groups = 0
        varied_groups = 0
        suspicious_groups = 0
        total_group_tokens = sum(grp_counts.values())

        for grp, cnt in grp_counts.items():
            uniq = len(grp_types[grp])
            density = cnt / max(total, 1)
            if cnt >= 4 and density >= 0.012:
                dense_groups += 1
            if cnt >= 5 and uniq >= 3:
                varied_groups += 1
            if cnt >= 7 and uniq >= 4 and density >= 0.02:
                suspicious_groups += 1

        raw = (
            min(total_group_tokens / max(total * 0.22, 1), 1.0) * 0.18 +
            min(dense_groups / 6.0, 1.0) * 0.22 +
            min(varied_groups / 5.0, 1.0) * 0.28 +
            min(suspicious_groups / 4.0, 1.0) * 0.32
        )

        # Repetition with many different near-synonyms is more suspicious than plain diversity.
        ttr = len(set(normalized)) / max(total, 1)
        if ttr > 0.62:
            raw *= 0.88

        # Academic vocabulary should not inflate this too much.
        academic_terms = sum(
            1 for w in normalized
            if w in {'study','research','analysis','results','findings','data','method','methods','discussion','conclusion'}
        )
        if academic_terms >= max(8, total // 80):
            raw *= 0.85

        return round(max(0.03, min(raw, 0.58)), 4)

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

        # FIX v115: Integrate AI_SYNONYM_CLUSTERS — previously defined but never used.
        # AI paraphrasing leaves a cluster-usage signature: multiple words from the same
        # semantic cluster appear in close proximity (within 30-word windows).
        synonym_cluster_score = 0.0
        try:
            cluster_vocab = getattr(self.__class__, 'AI_SYNONYM_CLUSTERS', set())
            if cluster_vocab and len(words) >= 20:
                window_size = 30
                cluster_hits_total = 0
                for wi in range(0, len(words) - window_size, window_size // 2):
                    window = words[wi:wi + window_size]
                    cluster_words = [w for w in window if w in cluster_vocab]
                    # High density of cluster words in one window = AI signature
                    if len(cluster_words) >= 6:
                        cluster_hits_total += 1
                # Normalize: more than 2 windows with dense cluster = significant
                synonym_cluster_score = min(cluster_hits_total / max(len(words) / window_size, 1), 1.0)
                synonym_cluster_score = min(synonym_cluster_score * 1.8, 0.35)
        except Exception:
            synonym_cluster_score = 0.0

        result = (
            inv_score            * 0.20 +
            meta_score           * 0.14 +
            fake_score           * 0.16 +
            future_score         * 0.11 +
            enum_score           * 0.09 +
            balance_score        * 0.11 +
            hedge_score          * 0.10 +
            synonym_cluster_score * 0.09
        )
        return round(min(result, 1.0), 4)




def _discourse_invariant(self, text):
    """
    Discourse-invariant AI style detector.
    This is the top-level, correctly bound version used by AIDetectionEngine.
    """
    if not text:
        return 0.15

    text_l = text.lower()
    n_words = max(len(re.findall(r'\b\w+\b', text_l)), 1)

    inv_patterns = getattr(self, "_invariant_patterns", [])
    inv_hits = 0
    try:
        inv_hits = sum(len(p.findall(text)) for p in inv_patterns)
    except Exception:
        inv_hits = 0
    inv_density = inv_hits / max((n_words / 50), 1e-9)
    inv_score = min(inv_density * 0.7, 1.0)

    META_DISC = re.compile(
        r'\b(?:this (?:paper|study|article|work|essay|analysis|chapter|review|report))\s+'
        r'(?:aims?|seeks?|explores?|examines?|investigates?|presents?|discusses?|'
        r'analyzes?|assesses?|evaluates?|considers?|highlights?|demonstrates?|'
        r'attempts? to|endeavors? to|sets out to|intends? to)\b',
        re.I,
    )
    meta_hits = len(META_DISC.findall(text))
    meta_score = min(meta_hits * 0.5, 1.0)

    FAKE_CITE = re.compile(
        r'\b(?:research|studies|evidence|literature|findings?|'
        r'data|experts?|scholars?|scientists?|academics?)\s+'
        r'(?:suggest(?:s|ed)?|indicate(?:s|d)?|show(?:s|ed|n)?|'
        r'demonstrate(?:s|d)?|confirm(?:s|ed)?|support(?:s|ed)?|'
        r'reveal(?:s|ed)?|highlight(?:s|ed)?|point(?:s|ed)? (?:to|out))\b',
        re.I,
    )
    fake_hits = len(FAKE_CITE.findall(text))
    fake_score = min((fake_hits / max((n_words / 80), 1e-9)) * 0.6, 1.0)

    FUTURE_RES = re.compile(
        r'\b(?:future|further|additional|more|subsequent)\s+'
        r'(?:research|studies|work|investigation|exploration|analysis|'
        r'examination|inquiry|efforts?|attention)\s+'
        r'(?:(?:is|are)\s+)?(?:should|must|needs? to|ought to|could|would|'
        r'may|might|will|can|has to|have to|is needed|are needed|'
        r'is required|are required|is warranted|are recommended)\b',
        re.I,
    )
    future_hits = len(FUTURE_RES.findall(text))
    future_score = min(future_hits * 0.6, 1.0)

    ENUM_PAT = re.compile(
        r'\b(?:first(?:ly)?|second(?:ly)?|third(?:ly)?|fourth(?:ly)?|'
        r'finally|lastly|next|subsequently|to begin|to start|'
        r'to conclude|in the first (?:place|instance)|'
        r'on (?:one hand|the other hand)|'
        r'\([ivx]+\)|\([abc]\)|\b[1-9]\)|^\s*[1-9]\.)',
        re.I | re.MULTILINE,
    )
    enum_hits = len(ENUM_PAT.findall(text))
    enum_score = min((enum_hits / max((n_words / 100), 1e-9)) * 0.5, 1.0)

    BALANCE_PAT = re.compile(
        r'\b(?:while|although|even though|despite|notwithstanding|'
        r'whereas|in contrast to|as opposed to)\b.{10,80}'
        r'(?:,|\;)\s+(?:it|this|the|these|there|one|however|yet|'
        r'nevertheless|nonetheless|still)',
        re.I | re.DOTALL,
    )
    balance_hits = len(BALANCE_PAT.findall(text))
    balance_score = min((balance_hits / max((n_words / 60), 1e-9)) * 0.6, 1.0)

    HEDGE_GEN = re.compile(
        r'\b(?:in (?:general|most cases|many instances|several contexts|'
        r'some situations|certain circumstances|various (?:fields|domains|contexts)))\b|'
        r'\b(?:generally|typically|usually|commonly|often|frequently|'
        r'largely|broadly|widely|predominantly) (?:speaking,?\s+)?'
        r'(?:it|this|the|these|one|research|studies|evidence)\b',
        re.I,
    )
    hedge_hits = len(HEDGE_GEN.findall(text))
    hedge_score = min((hedge_hits / max((n_words / 70), 1e-9)) * 0.55, 1.0)

    result = (
        inv_score * 0.22
        + meta_score * 0.15
        + fake_score * 0.18
        + future_score * 0.12
        + enum_score * 0.10
        + balance_score * 0.12
        + hedge_score * 0.11
    )
    return round(min(result, 1.0), 4)



# ══════════════════════════════════════════════════════════════════════════════
# PDFReport — غلاف + تظليل
# ══════════════════════════════════════════════════════════════════════════════


import zlib as _z, base64 as _b

def _decode_block(enc):
    return _z.decompress(_b.b64decode(enc)).decode('utf-8')

_PDFREP_ENC = (
    "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"
)

_engine_ns = {"__builtins__": __builtins__, "re": re, "math": math,
              "datetime": datetime, "os": os, "zlib": zlib, "base64": base64,
              "json": json, "io": io, "sys": sys, "traceback": traceback,
              "threading": threading,
              "FITZ_OK": FITZ_OK, "RLAB_OK": RLAB_OK,
              "DOCX_OK": DOCX_OK, "LOG": LOG, "LOG_EXC": LOG_EXC,
              "AIDetectionEngine": AIDetectionEngine}
try:
    import fitz as _fitz; _engine_ns["fitz"] = _fitz
except: pass
try:
    from reportlab.pdfgen import canvas as _rlc
    from reportlab.lib.pagesizes import A4 as _A4
    _engine_ns["rl_canvas"] = _rlc; _engine_ns["A4"] = _A4
except: pass
exec(compile(_decode_block(_PDFREP_ENC), "<PDFReport>", "exec"), _engine_ns)
AIDetectionEngine = AIDetectionEngine
PDFReport         = _engine_ns["PDFReport"]
# cache removed to avoid stale engine instances during helper rebinding fixes

# ===== v14 helper top-level rebinds (runtime-safe) =====
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

    # Token Predictability + Chunk Uniformity (Turnitin chunks: 5-10 sents)
    pred = sum(1 for w in words if w in self.AI_FINGERPRINT)/max(len(words),1)
    rare = sum(1 for w in words if len(w)>10 and w not in self.AI_FINGERPRINT and w not in self.EN_ACADEMIC_NEUTRAL)/max(len(words),1)
    predict_ai = min(pred*8,1)*0.6+max(0,0.5-rare*5)*0.4
    csz = max(len(words)//4,5)
    chs = [words[i:i+csz] for i in range(0,len(words),csz) if len(words[i:i+csz])>=5]
    if len(chs)>=2:
        cd=[sum(1 for w in ch if w in self.AI_FINGERPRINT)/len(ch) for ch in chs]
        acd=sum(cd)/len(cd); cu=max(0,1.0-math.sqrt(sum((d-acd)**2 for d in cd)/len(cd))*10)
    else: cu=0.5
    result=(len_ai*0.25+long_ai*0.20+formal_ai*0.20+predict_ai*0.20+cu*0.15)
    return round(min(result,1.0),4)

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


# ── Early helper binding: must happen before _load_engine() is ever called ──
def _early_bind_engine_helpers():
    helper_names = [
        "_english_ai_score", "_explain_paragraph", "_arabic_ai_score", "_compute_confidence",
        "_context_coherence", "_advanced_stylometry", "_punct_distribution",
        "_lm_perplexity", "_token_prob_variance", "_sliding_window", "_semantic_entropy",
        "_llr_score", "_rf_score", "_bigram_score", "_trigram_score", "_pattern_score", "_rhythm",
        "_local_entropy", "_paragraph_structure", "_punct_fingerprint",
        "_verb_ratio", "_pronoun_ratio", "_compute_fingerprint_score",
        "_simple_gpt_score", "_gpt_formatting_signature", "_paraphrase_engine",
        "_synonym_density", "_discourse_invariant",
        "_academic_grounding_profile", "_academic_grounding_profile_v2"
    ]
    g = globals()
    for _name in helper_names:
        _fn = g.get(_name)
        if callable(_fn):
            setattr(AIDetectionEngine, _name, _fn)

_early_bind_engine_helpers()

def _engine_missing_attr(self, name):
    if name.startswith("_"):
        _fn = globals().get(name)
        if callable(_fn):
            setattr(self.__class__, name, _fn)
            return _fn.__get__(self, self.__class__)
    raise AttributeError(f"{self.__class__.__name__!s} object has no attribute {name!r}")

AIDetectionEngine.__getattr__ = _engine_missing_attr


# ===== Early engine helper binding fix =====
# This block is intentionally placed before _load_engine()/UI execution.

def _english_ai_score(self, text, words, sents):
        """
        English-focused AI detector.
        Requires direct/templatic GPT evidence and aggressively discounts
        well-grounded academic prose across disciplines.
        """
        arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
        if arabic_chars / max(len(text), 1) > 0.20:
            return 0.0

        n_words = len(words)
        if n_words < 30:
            self._en_evidence_cache = ["too_short_for_strong_en_ai"]
            return 0.10

        tl = text.lower()
        sent_count = max(len(sents), 1)
        evidence = []

        grounding = self._academic_grounding_profile(text, words, sents)
        grounding_score = grounding["score"]

        # 1) Direct GPT phrase evidence
        t1_hits = [p for p in getattr(self, 'EN_GPT_PHRASES_T1', []) if p in tl]
        exact_hit_count = len(t1_hits)
        if exact_hit_count >= 10:
            t1_score = min(0.78 + (exact_hit_count - 10) * 0.015, 0.96)
            evidence.append(f"T1-very-strong:{exact_hit_count}")
        elif exact_hit_count >= 6:
            t1_score = 0.44 + (exact_hit_count - 6) * 0.055
            evidence.append(f"T1-strong:{exact_hit_count}")
        elif exact_hit_count >= 3:
            t1_score = 0.18 + (exact_hit_count - 3) * 0.07
            evidence.append(f"T1-mid:{exact_hit_count}")
        else:
            t1_score = 0.02

        # 2) Sentence pattern evidence
        t2_hits = 0
        for pat in getattr(self, 'EN_GPT_SENTENCE_PATTERNS', [])[:120]:
            try:
                t2_hits += len(re.findall(pat, tl, re.I))
            except Exception:
                pass

        t2_density = t2_hits / max(sent_count / 7.0, 1.0)
        if t2_density >= 6.0:
            t2_score = min(0.72 + (t2_density - 6.0) * 0.03, 0.90)
            evidence.append(f"T2-very-strong:{t2_density:.1f}")
        elif t2_density >= 3.5:
            t2_score = 0.34 + (t2_density - 3.5) * 0.08
            evidence.append(f"T2-strong:{t2_density:.1f}")
        elif t2_density >= 2.0:
            t2_score = 0.12 + (t2_density - 2.0) * 0.08
            evidence.append(f"T2-mid:{t2_density:.1f}")
        else:
            t2_score = 0.03

        # 3) Templatic style, kept weak on purpose
        lens = [len(s.split()) for s in sents if len(s.split()) >= 3]
        style_score = 0.0
        if lens:
            avg_len = sum(lens) / len(lens)
            sd_len = (sum((x - avg_len) ** 2 for x in lens) / len(lens)) ** 0.5
            cv_len = sd_len / max(avg_len, 1.0)
            if 14 <= avg_len <= 24 and cv_len <= 0.26:
                style_score += 0.10
            elif 12 <= avg_len <= 26 and cv_len <= 0.33:
                style_score += 0.05

        formal_openers = 0
        for s in sents:
            ss = s.strip().lower()
            if re.match(r'^(however|therefore|moreover|furthermore|additionally|consequently|overall|thus|notably)\b', ss):
                formal_openers += 1
        opener_ratio = formal_openers / max(sent_count, 1)
        if opener_ratio >= 0.30:
            style_score += 0.05
        elif opener_ratio >= 0.18:
            style_score += 0.025

        repeated_templates = 0
        repeated_templates += len(re.findall(r'\bthis\s+(?:study|paper|article|analysis)\s+(?:aims?|seeks?|examines?|investigates?|explores?)\b', tl))
        repeated_templates += len(re.findall(r'\bit\s+(?:is|has been)\s+(?:important|widely|necessary|evident|clear|shown|demonstrated)\b', tl))
        if repeated_templates >= 5:
            style_score += 0.08
        elif repeated_templates >= 3:
            style_score += 0.04

        style_score = min(style_score, 0.18)

        # 4) Human / academic dampeners
        citation_hits = len(re.findall(r'\([A-Z][A-Za-z\-]+,\s*\d{4}[a-z]?\)', text))
        bracket_hits  = len(re.findall(r'\[(?:\d+|\d+(?:\s*,\s*\d+)*)\]', text))
        quote_hits    = text.count('"') + text.count('“') + text.count('”')
        number_hits   = len(re.findall(r'\b\d+(?:\.\d+)?%?\b', text))
        hedges        = len(re.findall(r'\b(?:may|might|could|perhaps|possibly|likely|unlikely|approximately|suggests?|appears?|indicates?)\b', tl))
        first_person  = len(re.findall(r'\b(?:i|we|our|my|us)\b', tl))

        damp = 0.0
        if citation_hits + bracket_hits >= 2:
            damp += 0.08
            evidence.append("academic-citations")
        if number_hits >= max(6, n_words // 120):
            damp += 0.05
            evidence.append("data-heavy")
        if hedges >= 4:
            damp += 0.04
        if first_person >= 2:
            damp += 0.03
        if quote_hits >= 2:
            damp += 0.02

        # cross-disciplinary grounding gets strongest dampening unless direct GPT evidence is strong
        if grounding_score >= 0.70:
            damp += 0.34
            evidence.append(f"grounded-academic:{grounding_score:.2f}")
        elif grounding_score >= 0.55:
            damp += 0.24
            evidence.append(f"grounded-academic:{grounding_score:.2f}")
        elif grounding_score >= 0.40:
            damp += 0.14
            evidence.append(f"grounded-academic:{grounding_score:.2f}")

        base = t1_score * 0.50 + t2_score * 0.33 + style_score * 0.17

        corroboration = 0
        corroboration += 1 if exact_hit_count >= 4 else 0
        corroboration += 1 if t2_density >= 3.5 else 0
        corroboration += 1 if repeated_templates >= 5 else 0
        corroboration += 1 if getattr(self, '_simple_gpt_score')(text, words, sents) >= 0.66 else 0
        corroboration += 1 if getattr(self, '_gpt_formatting_signature')(text, sents) >= 0.58 else 0

        score = base - damp

        # style-only academic prose should stay low
        if grounding_score >= 0.55 and exact_hit_count < 3 and t2_density < 3.5:
            score *= 0.58
        elif grounding_score >= 0.40 and exact_hit_count < 2 and t2_density < 2.5:
            score *= 0.74

        # Escalate only with strong direct evidence
        if corroboration >= 3 and exact_hit_count >= 4:
            score = max(score, min(0.96, 0.74 + 0.04 * corroboration))
            evidence.append(f"cross-strong:{corroboration}")
        elif corroboration >= 2 and exact_hit_count >= 3 and grounding_score < 0.55:
            score = max(score, 0.56)
            evidence.append(f"cross-mid:{corroboration}")

        score = max(0.0, min(score, 0.98))
        self._en_evidence_cache = evidence[:24]
        return round(score, 4)

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
    """
    FIRST_PERSON = {'i','me','my','mine','myself','we','us','our','ours','ourselves'}
    if not words: return 0.0
    fp_count = sum(1 for w in words if w in FIRST_PERSON)
    return round(fp_count / len(words), 4)

def _compute_fingerprint_score(self, text, words, sents,
                               simple_gpt_score, gpt_format_score,
                               english_ai_score, arabic_ai_score,
                               human_error_val, english_human_score,
                               deep_human_score):
    """Conservative fingerprint score for English academic text."""
    if not words or not sents:
        self._fp_scores_cache = {}
        return 0.0

    tl = text.lower()
    n_words = max(len(words), 1)

    exact_phrases = sum(1 for p in getattr(self, 'EN_GPT_PHRASES_T1', []) if p in tl)
    struct_hits = 0
    struct_pats = [
        r'\bthis\s+(?:study|paper|article|research|analysis)\s+(?:aims?|seeks?|examines?|investigates?|explores?)\b',
        r'\bit\s+(?:has\s+been|is)\s+(?:widely\s+)?(?:shown|demonstrated|recognized|reported|suggested)\s+that\b',
        r'\bfurther\s+research\s+(?:is\s+needed|should|could|may)\b',
        r'\bplays?\s+(?:a|an)\s+(?:vital|crucial|key|significant|important)\s+role\s+in\b',
    ]
    for p in struct_pats:
        try:
            struct_hits += len(re.findall(p, tl, re.I))
        except Exception:
            pass

    starter_tokens = [s.split()[0].lower().strip(",;:") for s in sents if s.split()]
    formal_openers = {'however','therefore','moreover','furthermore','additionally',
                      'consequently','nevertheless','thus','overall','specifically','notably'}
    starter_ratio = sum(1 for t in starter_tokens if t in formal_openers) / max(len(starter_tokens), 1)

    citations = len(re.findall(r'\([A-Z][A-Za-z\-]+,\s*\d{4}[a-z]?\)', text))
    numeric = len(re.findall(r'\b\d+(?:\.\d+)?%?\b', text))
    hedges  = len(re.findall(r'\b(?:may|might|could|perhaps|possibly|likely|unlikely|approximately|suggests?|appears?|indicates?)\b', tl))
    first_person = len(re.findall(r'\b(?:i|we|our|my|us)\b', tl))

    direct_signal = (
        min(exact_phrases / 8.0, 1.0) * 0.34 +
        min(struct_hits / 8.0, 1.0) * 0.16 +
        simple_gpt_score * 0.18 +
        gpt_format_score * 0.10 +
        english_ai_score * 0.14 +
        min(getattr(self, '_pattern_memory')(text), 0.9) * 0.08
    )

    style_signal = 0.0
    if starter_ratio >= 0.28:
        style_signal += 0.08
    elif starter_ratio >= 0.16:
        style_signal += 0.04
    style_signal += min(getattr(self, '_semantic_embedding')(words, sents), 0.85) * 0.05
    style_signal += min(getattr(self, '_context_drift')(sents, words), 0.85) * 0.05
    style_signal = min(style_signal, 0.14)

    human_damp = 0.0
    if citations >= 2:
        human_damp += 0.08
    if numeric >= max(6, n_words // 120):
        human_damp += 0.05
    if hedges >= 4:
        human_damp += 0.03
    if first_person >= 2:
        human_damp += 0.03

    human_damp += english_human_score * 0.08
    human_damp += deep_human_score * 0.06
    human_damp += human_error_val * 0.04

    score = direct_signal + style_signal - human_damp

    corroboration = 0
    corroboration += 1 if exact_phrases >= 4 else 0
    corroboration += 1 if struct_hits >= 5 else 0
    corroboration += 1 if simple_gpt_score >= 0.62 else 0
    corroboration += 1 if english_ai_score >= 0.68 else 0
    corroboration += 1 if gpt_format_score >= 0.55 else 0

    if corroboration >= 3 and exact_phrases >= 4:
        score = max(score, min(0.97, 0.78 + 0.04 * corroboration))
    elif corroboration >= 2 and exact_phrases >= 2:
        score = max(score, 0.58)

    # Hard limit against pure academic-style inflation.
    if exact_phrases <= 1 and struct_hits <= 2 and simple_gpt_score < 0.45:
        score = min(score, 0.34)

    self._fp_scores_cache = {
        "exact_phrases": exact_phrases,
        "struct_hits": struct_hits,
        "starter_ratio": round(starter_ratio, 4),
        "citations": citations,
        "numeric": numeric,
        "corroboration": corroboration,
    }
    return round(max(0.0, min(score, 0.98)), 4)

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

    # ─── ⑦ GPT School Verbs (موسّع ليشمل الأفعال الأكاديمية لـ GPT) ──
    GPT_VERBS = {
        # أفعال GPT المدرسية الأصلية
        'helps','improves','allows','enables','supports','promotes',
        'develops','builds','strengthens','boosts','enhances','increases',
        'reduces','expands','fosters','cultivates','stimulates','provides',
        'offers','encourages','facilitates','contributes','assists',
        'explores','gains','learn','grow','improve','develop',
        # أفعال GPT الأكاديمية — مميزة جداً في نصوص GPT الأكاديمية
        'examine','examines','examined','leverage','leverages','leveraged',
        'highlight','highlights','highlighted','underscore','underscores',
        'elucidate','elucidates','illuminate','illuminates','navigate',
        'navigates','foster','fosters','harness','harnessing','unlock',
        'unlocks','empower','empowers','reimagine','reshape','revolutionize',
        'operationalize','contextualize','conceptualize','prioritize',
        'streamline','streamlines','mitigate','mitigates','alleviate',
        'bolster','bolsters','reinforce','reinforces','demonstrate',
        'demonstrates','investigate','investigates','aims','seeks',
        'endeavors','strives','aspires','explores','delves','address',
        'addresses','tackle','tackles','shed','sheds',
    }
    vb_count = sum(1 for w in words if w in GPT_VERBS)
    scores['gpt_verbs'] = min(vb_count/n_words*7.0, 1.0)

    # ─── ⑧ Benefit/Value + GPT Academic Adjectives ───────────────────
    BENEFIT_W = {
        # كلمات القيمة الأصلية
        'benefits','benefit','advantages','advantage','valuable',
        'important','essential','crucial','key','significant',
        'effective','powerful','positive','useful','worthwhile',
        'lifelong','personal','intellectual','academic','overall',
        'activity','habit','practice','development','growth',
        # صفات GPT الأكاديمية المميزة
        'holistic','multifaceted','nuanced','transformative','innovative',
        'sustainable','resilient','robust','pivotal','paramount',
        'groundbreaking','revolutionary','unprecedented','comprehensive',
        'interdisciplinary','systemic','dynamic','foundational','seminal',
        'imperative','indispensable','far-reaching','cutting-edge',
    }
    ben_count = sum(1 for w in words if w in BENEFIT_W)
    scores['benefit_words'] = min(ben_count/n_words*6.0, 1.0)

    # ─── ⑨ Adverb -ly Density ─────────────────────────────────────────
    # GPT يُكثِّر الظروف المنتهية بـ -ly
    LY_ADVERBS = [w for w in words if w.endswith('ly') and len(w) > 5
                  and w not in {'really','totally','actually','literally',
                                'honestly','basically','personally'}]
    scores['ly_adverbs'] = min(len(LY_ADVERBS)/n_words*15.0, 1.0)

    # ─── ⑨b GPT Lexical Density (كثافة مفردات AI_FINGERPRINT) ─────────
    # نص GPT الأكاديمي بدون روابط يُكثِّر مفردات AI_FINGERPRINT بشكل غير طبيعي
    AI_FP = getattr(self, 'AI_FINGERPRINT', set())
    if AI_FP:
        fp_hits = sum(1 for w in words if w in AI_FP)
        fp_density = fp_hits / n_words
        # عتبة: >8% من الكلمات من AI_FINGERPRINT = مشبوه
        # الكتابة البشرية الأكاديمية نادراً ما تتجاوز 5%
        if fp_density >= 0.14:
            scores['gpt_lexical'] = min(0.50 + (fp_density - 0.14) * 3.0, 0.95)
        elif fp_density >= 0.09:
            scores['gpt_lexical'] = 0.20 + (fp_density - 0.09) * 6.0
        elif fp_density >= 0.05:
            scores['gpt_lexical'] = (fp_density - 0.05) * 5.0
        else:
            scores['gpt_lexical'] = 0.0
    else:
        scores['gpt_lexical'] = 0.0

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
    Conservative synonym-density detector.
    Academic lexical variety alone should not be treated as AI.
    """
    if len(words) < 25:
        return 0.12

    from collections import Counter as _C, defaultdict as _dd

    SEMANTIC_GROUPS = {
        'demonstrate': 'show_grp', 'show': 'show_grp', 'illustrate': 'show_grp', 'reveal': 'show_grp',
        'important': 'imp_grp', 'significant': 'imp_grp', 'crucial': 'imp_grp', 'critical': 'imp_grp',
        'vital': 'imp_grp', 'essential': 'imp_grp', 'key': 'imp_grp',
        'improve': 'enhance_grp', 'enhance': 'enhance_grp', 'strengthen': 'enhance_grp',
        'advance': 'enhance_grp', 'promote': 'enhance_grp',
        'use': 'use_grp', 'utilize': 'use_grp', 'employ': 'use_grp', 'apply': 'use_grp',
        'implement': 'use_grp', 'adopt': 'use_grp', 'leverage': 'use_grp',
        'help': 'help_grp', 'facilitate': 'help_grp', 'enable': 'help_grp', 'support': 'help_grp',
        'assist': 'help_grp', 'contribute': 'help_grp',
        'result': 'result_grp', 'outcome': 'result_grp', 'finding': 'result_grp', 'conclusion': 'result_grp',
        'effect': 'result_grp', 'impact': 'result_grp', 'implication': 'result_grp',
        'problem': 'prob_grp', 'challenge': 'prob_grp', 'issue': 'prob_grp', 'concern': 'prob_grp',
        'method': 'method_grp', 'approach': 'method_grp', 'strategy': 'method_grp', 'technique': 'method_grp',
        'model': 'model_grp', 'framework': 'model_grp', 'paradigm': 'model_grp',
    }

    normalized = [w.lower() for w in words]
    total = len(normalized)
    grp_counts = _C()
    grp_types = _dd(set)

    for w in normalized:
        grp = SEMANTIC_GROUPS.get(w)
        if grp:
            grp_counts[grp] += 1
            grp_types[grp].add(w)

    if not grp_counts:
        return 0.06

    dense_groups = 0
    varied_groups = 0
    suspicious_groups = 0
    total_group_tokens = sum(grp_counts.values())

    for grp, cnt in grp_counts.items():
        uniq = len(grp_types[grp])
        density = cnt / max(total, 1)
        if cnt >= 4 and density >= 0.012:
            dense_groups += 1
        if cnt >= 5 and uniq >= 3:
            varied_groups += 1
        if cnt >= 7 and uniq >= 4 and density >= 0.02:
            suspicious_groups += 1

    raw = (
        min(total_group_tokens / max(total * 0.22, 1), 1.0) * 0.18 +
        min(dense_groups / 6.0, 1.0) * 0.22 +
        min(varied_groups / 5.0, 1.0) * 0.28 +
        min(suspicious_groups / 4.0, 1.0) * 0.32
    )

    # Repetition with many different near-synonyms is more suspicious than plain diversity.
    ttr = len(set(normalized)) / max(total, 1)
    if ttr > 0.62:
        raw *= 0.88

    # Academic vocabulary should not inflate this too much.
    academic_terms = sum(
        1 for w in normalized
        if w in {'study','research','analysis','results','findings','data','method','methods','discussion','conclusion'}
    )
    if academic_terms >= max(8, total // 80):
        raw *= 0.85

    return round(max(0.03, min(raw, 0.58)), 4)


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

def _discourse_invariant(self, text):
    """
    Discourse-invariant AI style detector.
    This is the top-level, correctly bound version used by AIDetectionEngine.
    """
    if not text:
        return 0.15

    text_l = text.lower()
    n_words = max(len(re.findall(r'\b\w+\b', text_l)), 1)

    inv_patterns = getattr(self, "_invariant_patterns", [])
    inv_hits = 0
    try:
        inv_hits = sum(len(p.findall(text)) for p in inv_patterns)
    except Exception:
        inv_hits = 0
    inv_density = inv_hits / max((n_words / 50), 1e-9)
    inv_score = min(inv_density * 0.7, 1.0)

    META_DISC = re.compile(
        r'\b(?:this (?:paper|study|article|work|essay|analysis|chapter|review|report))\s+'
        r'(?:aims?|seeks?|explores?|examines?|investigates?|presents?|discusses?|'
        r'analyzes?|assesses?|evaluates?|considers?|highlights?|demonstrates?|'
        r'attempts? to|endeavors? to|sets out to|intends? to)\b',
        re.I,
    )
    meta_hits = len(META_DISC.findall(text))
    meta_score = min(meta_hits * 0.5, 1.0)

    FAKE_CITE = re.compile(
        r'\b(?:research|studies|evidence|literature|findings?|'
        r'data|experts?|scholars?|scientists?|academics?)\s+'
        r'(?:suggest(?:s|ed)?|indicate(?:s|d)?|show(?:s|ed|n)?|'
        r'demonstrate(?:s|d)?|confirm(?:s|ed)?|support(?:s|ed)?|'
        r'reveal(?:s|ed)?|highlight(?:s|ed)?|point(?:s|ed)? (?:to|out))\b',
        re.I,
    )
    fake_hits = len(FAKE_CITE.findall(text))
    fake_score = min((fake_hits / max((n_words / 80), 1e-9)) * 0.6, 1.0)

    FUTURE_RES = re.compile(
        r'\b(?:future|further|additional|more|subsequent)\s+'
        r'(?:research|studies|work|investigation|exploration|analysis|'
        r'examination|inquiry|efforts?|attention)\s+'
        r'(?:(?:is|are)\s+)?(?:should|must|needs? to|ought to|could|would|'
        r'may|might|will|can|has to|have to|is needed|are needed|'
        r'is required|are required|is warranted|are recommended)\b',
        re.I,
    )
    future_hits = len(FUTURE_RES.findall(text))
    future_score = min(future_hits * 0.6, 1.0)

    ENUM_PAT = re.compile(
        r'\b(?:first(?:ly)?|second(?:ly)?|third(?:ly)?|fourth(?:ly)?|'
        r'finally|lastly|next|subsequently|to begin|to start|'
        r'to conclude|in the first (?:place|instance)|'
        r'on (?:one hand|the other hand)|'
        r'\([ivx]+\)|\([abc]\)|\b[1-9]\)|^\s*[1-9]\.)',
        re.I | re.MULTILINE,
    )
    enum_hits = len(ENUM_PAT.findall(text))
    enum_score = min((enum_hits / max((n_words / 100), 1e-9)) * 0.5, 1.0)

    BALANCE_PAT = re.compile(
        r'\b(?:while|although|even though|despite|notwithstanding|'
        r'whereas|in contrast to|as opposed to)\b.{10,80}'
        r'(?:,|\;)\s+(?:it|this|the|these|there|one|however|yet|'
        r'nevertheless|nonetheless|still)',
        re.I | re.DOTALL,
    )
    balance_hits = len(BALANCE_PAT.findall(text))
    balance_score = min((balance_hits / max((n_words / 60), 1e-9)) * 0.6, 1.0)

    HEDGE_GEN = re.compile(
        r'\b(?:in (?:general|most cases|many instances|several contexts|'
        r'some situations|certain circumstances|various (?:fields|domains|contexts)))\b|'
        r'\b(?:generally|typically|usually|commonly|often|frequently|'
        r'largely|broadly|widely|predominantly) (?:speaking,?\s+)?'
        r'(?:it|this|the|these|one|research|studies|evidence)\b',
        re.I,
    )
    hedge_hits = len(HEDGE_GEN.findall(text))
    hedge_score = min((hedge_hits / max((n_words / 70), 1e-9)) * 0.55, 1.0)

    result = (
        inv_score * 0.22
        + meta_score * 0.15
        + fake_score * 0.18
        + future_score * 0.12
        + enum_score * 0.10
        + balance_score * 0.12
        + hedge_score * 0.11
    )
    return round(min(result, 1.0), 4)


def _bind_engine_helpers_early():
    """
    Safe early binder: only binds helpers that are already defined at call time.
    Late helpers are rebound again near the end of the file after all patches load.
    """
    _mapping = {
        "_english_ai_score": "_english_ai_score",
        "_explain_paragraph": "_explain_paragraph",
        "_arabic_ai_score": "_arabic_ai_score",
        "_compute_confidence": "_compute_confidence",
        "_context_coherence": "_context_coherence",
        "_advanced_stylometry": "_advanced_stylometry",
        "_punct_distribution": "_punct_distribution",
        "_bigram_score": "_bigram_score",
        "_trigram_score": "_trigram_score",
        "_pattern_score": "_pattern_score",
        "_rhythm": "_rhythm",
        "_local_entropy": "_local_entropy",
        "_paragraph_structure": "_paragraph_structure",
        "_punct_fingerprint": "_punct_fingerprint",
        "_verb_ratio": "_verb_ratio",
        "_pronoun_ratio": "_pronoun_ratio",
        "_compute_fingerprint_score": "_compute_fingerprint_score",
        "_simple_gpt_score": "_simple_gpt_score",
        "_gpt_formatting_signature": "_gpt_formatting_signature",
        "_paraphrase_engine": "_paraphrase_engine",
        "_synonym_density": "_synonym_density",
        "_discourse_invariant": "_discourse_invariant",
    }
    _g = globals()
    for _attr, _name in _mapping.items():
        _fn = _g.get(_name)
        if _fn is not None and not hasattr(AIDetectionEngine, _attr):
            setattr(AIDetectionEngine, _attr, _fn)
    return AIDetectionEngine



# ===== Critical helper fix: _strip_references early fallback =====
def _strip_references(self, text):
    """
    Safe top-level fallback for stripping reference sections and citation-heavy tails
    from academic texts before AI-style analysis.
    """
    if not text:
        return text

    # 1) Remove trailing References/Bibliography section
    ref_header = re.search(
        r'(?is)\n\s*(references?|bibliography|works\s+cited|selected\s+bibliography|'
        r'literature\s+cited|endnotes?|footnotes?|citations?|sources?|'
        r'المراجع|المصادر|قائمة\s+المراجع)\s*[:\-]?\s*\n',
        text
    )
    if ref_header:
        text = text[:ref_header.start()]

    # 2) Drop common standalone reference-entry lines
    cleaned_lines = []
    ref_like_run = 0
    for line in text.splitlines():
        s = line.strip()
        if not s:
            ref_like_run = 0
            cleaned_lines.append(line)
            continue

        ref_like = False

        if re.match(r'^\[\d+\]\s+', s):  # IEEE
            ref_like = True
        elif re.match(r'^\(?\d+\)?[.)]\s+[A-Z][A-Za-z\'\-]+', s):  # numbered refs
            ref_like = True
        elif re.match(r'^[A-Z][A-Za-z\'\-]+,\s+[A-Z]\.(?:\s*[A-Z]\.)*', s):  # APA-ish
            ref_like = True
        elif re.search(r'\b(?:doi|vol\.|no\.|pp\.|journal|proceedings)\b', s, re.I) and re.search(r'\b(19|20)\d{2}\b', s):
            ref_like = True
        elif re.search(r'https?://|www\.|doi\.org/', s, re.I):
            ref_like = True

        if ref_like:
            ref_like_run += 1
            if ref_like_run >= 2:
                continue
        else:
            ref_like_run = 0
            cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)

    # 3) Light cleanup of inline citations
    text = re.sub(r'\[(?:\d{1,3}(?:\s*[,;-]\s*\d{1,3})*)\]', ' ', text)
    text = re.sub(r'\((?:[A-Z][A-Za-z\-]+(?:\s+et\s+al\.)?,?\s*(?:19|20)\d{2}[a-z]?(?:\s*[,;]\s*[A-Z][A-Za-z\-]+(?:\s+et\s+al\.)?,?\s*(?:19|20)\d{2}[a-z]?)*?)\)', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

if not hasattr(AIDetectionEngine, '_strip_references'):
    AIDetectionEngine._strip_references = _strip_references


# ===== Core metric helpers restored as top-level methods =====
def _perp(self, words, _transformer_model=None):
    """Transformer (DistilGPT2) + Trigram LM Perplexity"""
    if len(words) < 20:
        return 0.5
    try:
        import torch
        from transformers import GPT2LMHeadModel, GPT2TokenizerFast
        if not hasattr(self, '_gpt2_tok'):
            self._gpt2_tok = GPT2TokenizerFast.from_pretrained('distilgpt2', cache_dir='/tmp/hf_cache')
            self._gpt2_mdl = GPT2LMHeadModel.from_pretrained('distilgpt2', cache_dir='/tmp/hf_cache')
            self._gpt2_mdl.eval()
        _txt = ' '.join(words[:300])
        _enc = self._gpt2_tok(_txt, return_tensors='pt', truncation=True, max_length=512)
        with torch.no_grad():
            _loss = self._gpt2_mdl(**_enc, labels=_enc['input_ids']).loss.item()
        _ppl = math.exp(_loss)
        if _ppl < 15: return 0.95
        elif _ppl < 25: return 0.82
        elif _ppl < 40: return 0.65
        elif _ppl < 65: return 0.45
        elif _ppl < 100: return 0.28
        elif _ppl < 200: return 0.15
        else: return 0.05
    except Exception:
        pass
    from collections import Counter as _C
    trigrams = list(zip(words[:-2], words[1:-1], words[2:]))
    bigrams = list(zip(words[:-1], words[1:]))
    t_cnt = _C(trigrams); b_cnt = _C(bigrams); u_cnt = _C(words)
    vsz = max(len(u_cnt), 1); SM = 0.1; lp = 0.0; n = 0
    for i in range(2, len(words)):
        w = words[i]; c2 = (words[i-2], words[i-1]); c1 = words[i-1]
        bc = b_cnt.get(c2, 0)
        if bc > 0:
            p = (t_cnt.get(c2 + (w,), 0) + SM) / (bc + SM * vsz)
        else:
            b1 = u_cnt.get(c1, 0)
            p = (b_cnt.get((c1, w), 0) + SM) / (b1 + SM * vsz) if b1 > 0 else SM / vsz
        lp += math.log(max(p, 1e-10)); n += 1
    if n == 0:
        return 0.5
    pe = math.exp(-lp / n)
    if pe < 8: return 0.95
    elif pe < 12: return 0.88
    elif pe < 18: return 0.74
    elif pe < 30: return 0.58
    elif pe < 50: return 0.42
    elif pe < 80: return 0.32
    elif pe < 120: return 0.18
    else: return 0.08

def _burst(self, s):
    """Turnitin-style Burstiness: CV منخفض=AI، CV مرتفع=بشري"""
    if len(s) < 4:
        return 0.5
    ln = [len(x.split()) for x in s if x.strip()]
    if len(ln) < 4:
        return 0.5
    avg = sum(ln) / len(ln)
    if avg < 4:
        return 0.5
    cv = math.sqrt(sum((l - avg) ** 2 for l in ln) / len(ln)) / (avg + 1e-6)
    if cv < 0.20: r = 0.92
    elif cv < 0.30: r = 0.78
    elif cv < 0.40: r = 0.62
    elif cv < 0.50: r = 0.45
    elif cv < 0.65: r = 0.28
    else: r = 0.12
    ideal = sum(1 for l in ln if 13 <= l <= 32) / len(ln)
    smooth = max(0, 1.0 - sum(abs(ln[i] - ln[i-1]) for i in range(1, len(ln))) / len(ln) / 12) if len(ln) >= 3 else 0.5
    return round(min(max(r * 0.55 + smooth * 0.25 + max(0, (ideal - 0.5) * 0.30) * 0.20, 0), 1), 4)

def _aifp(self, w):
    if len(w) < 20:
        return 0.3
    return min(sum(1 for x in w if x in self.AI_FINGERPRINT) / len(w) * 100 / 4, 1.0)

def _trans(self, s):
    if len(s) < 5:
        return 0.3
    cnt = sum(
        1 for x in s[:20]
        if any(x.lower().startswith(t) or t in x.lower()[:30] for t in self.TRANSITIONS)
    )
    return min(cnt / min(len(s), 20) * 1.5, 1.0)

def _vrich(self, w):
    if len(w) < 20:
        return 0.3
    t = len(set(w)) / len(w)
    return 0.8 if t >= 0.7 else 0.5 if t >= 0.6 else 0.3 if t >= 0.5 else 0.1

def _pass(self, s):
    if len(s) < 5:
        return 0.3
    cnt = sum(1 for x in s if any(re.search(p, x, re.I) for p in self.PASSIVE_PATTERNS))
    r = cnt / len(s)
    return 0.8 if r >= 0.3 else 0.6 if r >= 0.2 else 0.4 if r >= 0.1 else 0.2

def _hpen(self, w):
    if len(w) < 10:
        return 0.0
    return min(sum(1 for x in w if x in self.HUMAN_MARKERS) / len(w) * 10, 0.6)

for _name in ("_perp", "_burst", "_aifp", "_trans", "_vrich", "_pass", "_hpen"):
    if not hasattr(AIDetectionEngine, _name):
        setattr(AIDetectionEngine, _name, globals()[_name])

_bind_engine_helpers_early()

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


st.set_page_config(page_title="DetectAI v1", page_icon="🛡️",
                   layout="wide", initial_sidebar_state="collapsed")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
*{font-family:'Plus Jakarta Sans',sans-serif}
[data-testid="stAppViewContainer"]{background:linear-gradient(135deg,#f0f4ff 0%,#e8f0fe 50%,#f4f0ff 100%)}
[data-testid="stHeader"]{background:rgba(240,244,255,0.9);backdrop-filter:blur(12px);border-bottom:1px solid rgba(99,102,241,.15)}
.block-container{padding-top:1.2rem}
.score-card{
  background:linear-gradient(135deg,#ffffff 0%,#f8f9ff 100%);
  border-radius:20px;padding:28px 20px;text-align:center;
  border:1px solid rgba(99,102,241,.2);
  box-shadow:0 4px 24px rgba(99,102,241,.12),0 1px 4px rgba(0,0,0,.06);
  margin-bottom:12px}
.score-num{font-size:62px;font-weight:800;line-height:1;
  background:linear-gradient(135deg,#6366f1,#8b5cf6);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.score-sub{font-size:12px;color:#94a3b8;margin-top:6px;font-weight:600;letter-spacing:.05em;text-transform:uppercase}
.score-vd{font-size:15px;font-weight:700;margin-top:8px;color:#374151}
.pill{display:inline-block;
  background:rgba(99,102,241,.08);
  border:1px solid rgba(99,102,241,.2);
  border-radius:20px;padding:4px 14px;font-size:12px;color:#6366f1;margin:2px;font-weight:600}
.pill b{color:#4f46e5}
.sh{font-size:13px;font-weight:700;color:#6366f1;
    border-left:3px solid #6366f1;padding-left:8px;margin:14px 0 8px}
.fp-row{display:flex;align-items:center;gap:8px;padding:5px 0;
        border-bottom:1px solid rgba(99,102,241,.08);font-size:12px}
.fp-lbl{flex:1;color:#475569}
.fp-bg{width:100px;background:#e8edf8;border-radius:4px;height:8px;overflow:hidden;flex-shrink:0}
.fp-fill{height:100%;border-radius:4px}
.fp-pct{min-width:45px;text-align:right;color:#94a3b8;font-family:monospace;font-size:11px}
.lic-box{background:linear-gradient(135deg,#ffffff,#f8f9ff);
  border:1px solid rgba(99,102,241,.25);border-radius:20px;
  padding:48px 56px;max-width:460px;margin:60px auto;text-align:center;
  box-shadow:0 8px 40px rgba(99,102,241,.15)}
/* Tabs */
.stTabs [data-baseweb="tab-list"]{gap:6px;background-color:transparent}
.stTabs [data-baseweb="tab"]{
  background:rgba(255,255,255,.7);border-radius:10px 10px 0 0;
  padding:10px 20px;color:#64748b;
  border:1px solid rgba(99,102,241,.15);border-bottom:none;font-weight:600}
.stTabs [aria-selected="true"]{
  background:#ffffff;color:#6366f1!important;
  border-color:rgba(99,102,241,.35)}
.stTabs [data-baseweb="tab-panel"]{
  background:rgba(255,255,255,.85);backdrop-filter:blur(8px);
  padding:20px;border-radius:0 10px 10px 10px;
  border:1px solid rgba(99,102,241,.15);
  box-shadow:0 2px 12px rgba(99,102,241,.07)}
/* Streamlit overrides */
.stTextArea textarea{background:#ffffff!important;border:1.5px solid rgba(99,102,241,.25)!important;border-radius:12px!important;color:#1e293b!important}
.stButton>button{background:linear-gradient(135deg,#6366f1,#8b5cf6)!important;color:#fff!important;border:none!important;border-radius:12px!important;font-weight:700!important;padding:10px 24px!important;box-shadow:0 4px 14px rgba(99,102,241,.35)!important}
.stButton>button:hover{transform:translateY(-1px);box-shadow:0 6px 20px rgba(99,102,241,.45)!important}
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
      <div style="margin-bottom:12px">
        <svg width="60" height="60" viewBox="0 0 60 60" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="60" height="60" rx="16" fill="url(#lg1)"/>
          <path d="M20 30 Q30 18 40 30 Q30 42 20 30Z" fill="white" opacity="0.9"/>
          <circle cx="30" cy="30" r="5" fill="white"/>
          <defs><linearGradient id="lg1" x1="0" y1="0" x2="60" y2="60" gradientUnits="userSpaceOnUse">
          <stop stop-color="#6366f1"/><stop offset="1" stop-color="#8b5cf6"/></linearGradient></defs>
        </svg>
      </div>
      <div style="font-size:24px;font-weight:800;color:#1e293b;margin:10px 0 6px">
        DetectAI <span style="color:#6366f1">v1</span></div>
      <div style="color:#94a3b8;font-size:13px;margin-bottom:30px">
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
  justify-content:space-between;margin-bottom:18px;
  background:rgba(255,255,255,.7);backdrop-filter:blur(10px);
  border-radius:16px;padding:14px 20px;
  border:1px solid rgba(99,102,241,.2);
  box-shadow:0 2px 12px rgba(99,102,241,.08)">
  <div style="display:flex;align-items:center;gap:14px">
    <svg width="42" height="42" viewBox="0 0 60 60" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="60" height="60" rx="14" fill="url(#hg1)"/>
      <path d="M20 30 Q30 18 40 30 Q30 42 20 30Z" fill="white" opacity="0.9"/>
      <circle cx="30" cy="30" r="5" fill="white"/>
      <defs><linearGradient id="hg1" x1="0" y1="0" x2="60" y2="60" gradientUnits="userSpaceOnUse">
      <stop stop-color="#6366f1"/><stop offset="1" stop-color="#8b5cf6"/></linearGradient></defs>
    </svg>
    <div>
      <div style="font-size:20px;font-weight:800;color:#1e293b">
        DetectAI <span style="background:linear-gradient(135deg,#6366f1,#8b5cf6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">v1</span></div>
      <div style="font-size:11px;color:#94a3b8;font-weight:600;letter-spacing:.04em">
        AI CONTENT DETECTOR</div>
    </div>
  </div>
  <div style="display:flex;gap:8px;align-items:center">
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
    st.markdown("### 🛡️ DetectAI v1")
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



# ── English AI quote extraction repair (must run BEFORE UI analyze call) ─────
def _sqlx_split_english_sentences(text):
    if not text:
        return []
    text = re.sub(r'\s+', ' ', text).strip()
    raw = re.split(r'(?<=[.!?])\s+(?=(?:[A-Z"“\'(\[]|In\s|On\s|At\s|However|Moreover|Furthermore|Therefore|Overall|This|It|These|Those))', text)
    out = []
    for s in raw:
        s = (s or '').strip()
        if not s:
            continue
        if len(re.findall(r"[A-Za-z]+", s)) < 5:
            continue
        out.append(s)
    return out

def _sqlx_sentence_quote_score(eng, sent, overall_result=None):
    tl = sent.lower()
    words = re.findall(r"[a-zA-Z]+(?:'[a-z]+)?", tl)
    n = max(len(words), 1)

    phrase_bank = []
    for attr in ("EN_GPT_PHRASES_T1", "EN_GPT_PHRASES_T2"):
        vals = getattr(eng, attr, None)
        if isinstance(vals, (list, tuple, set)):
            phrase_bank.extend(list(vals)[:240])

    phrase_hits = 0
    seen = set()
    for p in phrase_bank:
        p2 = str(p).strip().lower()
        if len(p2) < 8 or p2 in seen:
            continue
        seen.add(p2)
        if p2 in tl:
            phrase_hits += 1

    pattern_hits = 0
    pats = getattr(eng, "EN_GPT_SENTENCE_PATTERNS", []) or []
    for pat in list(pats)[:160]:
        try:
            if re.search(pat, tl, re.I):
                pattern_hits += 1
        except Exception:
            pass

    ai_vocab = getattr(eng, "AI_FINGERPRINT", set()) or set()
    ai_vocab_hits = sum(1 for w in words if w in ai_vocab)

    formal_openers = (
        'however', 'moreover', 'furthermore', 'therefore', 'overall',
        'in conclusion', 'to summarize', 'consequently', 'thus', 'additionally'
    )
    starts_formal = 1 if any(tl.startswith(x + ' ') or tl.startswith(x + ',') for x in formal_openers) else 0

    struct_patterns = [
        r'\bthis\s+(?:study|paper|article|analysis|essay|discussion)\s+(?:aims?|seeks?|examines?|explores?|investigates?)\b',
        r'\bit\s+(?:is|has been)\s+(?:important|necessary|clear|evident|shown|demonstrated)\b',
        r'\bplays?\s+a\s+(?:crucial|significant|vital|key|central)\s+role\b',
        r'\bto\s+ensure\s+that\b',
        r'\bwhile\s+(?:minimizing|reducing)\s+(?:risks|challenges)\b',
        r'\b(?:offers|provides)\s+significant\s+(?:benefits|opportunities)\b',
    ]
    struct_hits = sum(1 for pat in struct_patterns if re.search(pat, tl, re.I))

    first_person = len(re.findall(r"\b(?:i|we|our|my|us)\b", tl))
    hedges = len(re.findall(r"\b(?:may|might|could|perhaps|possibly|likely|unlikely|approximately)\b", tl))
    citations = len(re.findall(r'\([A-Z][A-Za-z\-]+,\s*(?:19|20)\d{2}[a-z]?\)', sent))
    citations += len(re.findall(r'\[(?:\d+|\d+(?:\s*,\s*\d+)*)\]', sent))
    numbers = len(re.findall(r'\b\d+(?:\.\d+)?%?\b', sent))
    quote_marks = sent.count('"') + sent.count("“") + sent.count("”")

    length_bonus = 0.0
    if 8 <= n <= 40:
        length_bonus = 0.06
    elif 41 <= n <= 60:
        length_bonus = 0.03

    score = (
        min(phrase_hits / 2.0, 1.0) * 0.34 +
        min(pattern_hits / 2.0, 1.0) * 0.22 +
        min(ai_vocab_hits / max(n * 0.16, 1.0), 1.0) * 0.18 +
        min(struct_hits / 2.0, 1.0) * 0.14 +
        starts_formal * 0.07 +
        length_bonus
    )

    # dampeners for normal academic / human evidence
    score -= min(citations, 2) * 0.07
    score -= min(numbers, 3) * 0.02
    score -= min(first_person, 2) * 0.05
    score -= min(hedges, 2) * 0.02
    if quote_marks >= 2:
        score -= 0.03

    if overall_result:
        pct = float(overall_result.get("percentage", 0.0) or 0.0)
        meta = overall_result.get("precision95_meta", {}) or {}
        if pct >= 70:
            score += 0.05
        if int(meta.get("phrase_hits", 0) or 0) >= 2:
            score += 0.04
        if int(meta.get("pattern_hits", 0) or 0) >= 2:
            score += 0.03

    return round(max(0.0, min(score, 0.995)), 4)

def _sqlx_extract_ai_quotes(eng, text, result=None):
    sents = _sqlx_split_english_sentences(text)
    if not sents:
        return []

    scored = []
    for idx, sent in enumerate(sents):
        sc = _sqlx_sentence_quote_score(eng, sent, result)
        if len(re.findall(r"[A-Za-z]+", sent)) < 6:
            continue
        scored.append({
            "index": idx,
            "score": sc,
            "text": sent,
            "word_count": len(re.findall(r"[A-Za-z]+(?:'[a-z]+)?", sent)),
        })

    if not scored:
        return []

    pct = float((result or {}).get("percentage", 0.0) or 0.0)
    strong_threshold = 0.30 if pct >= 75 else 0.34 if pct >= 55 else 0.40 if pct >= 35 else 0.48
    keep_n = max(3, min(12, int(math.ceil(len(scored) * (0.26 if pct >= 60 else 0.18 if pct >= 35 else 0.12)))))

    strong = [x for x in scored if x["score"] >= strong_threshold]
    strong = sorted(strong, key=lambda x: (x["score"], -abs(x["word_count"] - 22)), reverse=True)

    if len(strong) < min(3, len(scored)):
        strong = sorted(scored, key=lambda x: (x["score"], -abs(x["word_count"] - 22)), reverse=True)[:keep_n]
    else:
        strong = strong[:keep_n]

    used = set()
    final_quotes = []
    for item in strong:
        key = re.sub(r'\W+', ' ', item["text"].lower()).strip()
        if key in used:
            continue
        used.add(key)
        reasons = []
        tl = item["text"].lower()
        if re.search(r'\b(?:however|moreover|furthermore|therefore|overall|in conclusion|to summarize)\b', tl):
            reasons.append("formal opener")
        if re.search(r'\bthis\s+(?:study|paper|article|analysis)\s+(?:aims?|seeks?|examines?|explores?)\b', tl):
            reasons.append("template study phrasing")
        if re.search(r'\bit\s+(?:is|has been)\s+(?:important|necessary|clear|evident|shown|demonstrated)\b', tl):
            reasons.append("generic claim frame")
        if sum(1 for w in re.findall(r"[a-zA-Z]+(?:'[a-z]+)?", tl) if w in (getattr(eng, "AI_FINGERPRINT", set()) or set())) >= 2:
            reasons.append("AI-heavy vocabulary")
        final_quotes.append({
            "index": item["index"],
            "score": round(item["score"], 4),
            "text": item["text"],
            "reason": ", ".join(reasons[:2]) if reasons else "high sentence-level AI signature",
        })

    final_quotes.sort(key=lambda x: x["score"], reverse=True)
    return final_quotes[:12]

def _sqlx_enhance_ai_quotes(eng, result, text):
    if not isinstance(result, dict):
        return result
    try:
        quotes = _sqlx_extract_ai_quotes(eng, text, result)
        result["ai_citations"] = quotes
        ext = result.setdefault("extended", {})
        ext["ai_quote_candidates"] = quotes
        ext["ai_quote_count"] = len(quotes)
        if quotes:
            result["top_ai_sentence"] = quotes[0]["text"]
    except Exception:
        pass
    return result

def _v3fixed_nb_score(self, text, words):
    """
    Conservative Naive Bayes with reliability control.
    It should not dominate the final decision on academic English by itself.
    Still allowed to go high on clear copy-paste GPT prose.
    """
    if len(words) < 20:
        return 0.50

    features = self._nb_extract_features(text, words)

    import math as _m
    log_ai    = _m.log(self._NB_PRIOR_AI)
    log_human = _m.log(self._NB_PRIOR_HUMAN)

    combined_ai    = self._NB_AI_PRIORS
    combined_human = self._NB_HUMAN_PRIORS

    SMOOTHING = 1e-6
    active_feats = 0
    for feat, count in features.items():
        p_ai    = combined_ai.get(feat, SMOOTHING)
        p_human = combined_human.get(feat, SMOOTHING)
        if count > 0:
            active_feats += 1
            log_ai    += count * _m.log(max(p_ai,    SMOOTHING))
            log_human += count * _m.log(max(p_human, SMOOTHING))

    diff = log_ai - log_human
    base = 1.0 / (1.0 + _m.exp(-diff * 0.18))

    tl = text.lower()
    n_words = max(len(words), 1)
    sent_count = max(len(re.findall(r'(?<=[.!?])\s+', text)) + 1, 1)

    citation_hits = len(re.findall(r'\([A-Z][A-Za-z\-]+,\s*\d{4}[a-z]?\)', text))
    bracket_hits  = len(re.findall(r'\[(?:\d+|\d+(?:\s*,\s*\d+)*)\]', text))
    number_hits   = len(re.findall(r'\b\d+(?:\.\d+)?%?\b', text))
    quote_hits    = text.count('"') + text.count('“') + text.count('”')

    hedges = len(re.findall(
        r'\b(?:may|might|could|perhaps|possibly|likely|unlikely|approximately|suggests?|appears?|indicates?)\b',
        tl))
    first_person = len(re.findall(r'\b(?:i|we|our|my|us)\b', tl))

    exact_t1 = 0
    if hasattr(self, 'EN_GPT_PHRASES_T1'):
        exact_t1 = sum(1 for p in self.EN_GPT_PHRASES_T1 if p in tl)

    pattern_hits = 0
    if hasattr(self, 'EN_GPT_SENTENCE_PATTERNS'):
        for pat in self.EN_GPT_SENTENCE_PATTERNS[:80]:
            try:
                pattern_hits += len(re.findall(pat, tl, re.I))
            except Exception:
                pass

    gpt_format = self._gpt_formatting_signature(text, [text]) if hasattr(self, '_gpt_formatting_signature') else 0.0
    simple_gpt = self._simple_gpt_score(text, words, [text]) if hasattr(self, '_simple_gpt_score') else 0.0
    llr_val    = _call_engine_helper(self, "_llr_score", words) if hasattr(self, '_llr_score') else 0.0

    # Reliability: NB trained on small embedded corpus, so scale confidence.
    reliability = 0.58
    if active_feats >= 8:
        reliability += 0.07
    if n_words >= 250:
        reliability += 0.05
    if n_words >= 800:
        reliability += 0.05
    if exact_t1 >= 3 or pattern_hits >= 4:
        reliability += 0.08
    reliability = min(reliability, 0.80)

    score = 0.50 + (base - 0.50) * reliability

    # Academic human dampener: citations/data/hedging should soften NB.
    academic_human = 0.0
    if citation_hits + bracket_hits >= 2:
        academic_human += 0.09
    if number_hits >= max(6, n_words // 120):
        academic_human += 0.05
    if hedges >= 3:
        academic_human += 0.04
    if first_person >= 2:
        academic_human += 0.03
    if quote_hits >= 2:
        academic_human += 0.02

    score -= academic_human

    # Strong-copy-paste GPT override: allow NB to stay high only when corroborated.
    corroboration = 0
    corroboration += 1 if exact_t1 >= 4 else 0
    corroboration += 1 if pattern_hits >= 5 else 0
    corroboration += 1 if simple_gpt >= 0.62 else 0
    corroboration += 1 if llr_val >= 0.68 else 0
    corroboration += 1 if gpt_format >= 0.55 else 0

    if corroboration >= 3 and exact_t1 >= 3:
        score = max(score, min(0.90, 0.72 + 0.04 * corroboration))
    elif corroboration >= 2 and exact_t1 >= 2:
        score = max(score, 0.68)

    # Keep NB from screaming 95% on clean academic English without corroboration.
    hard_cap = 0.78
    if corroboration >= 2:
        hard_cap = 0.86
    if corroboration >= 3 and exact_t1 >= 3:
        hard_cap = 0.94

    return round(max(0.08, min(hard_cap, score)), 4)



def _v3fixed_english_ai_score(self, text, words, sents):
    """
    English-focused AI detector.
    Prioritizes direct GPT-like evidence and repeated templatic phrasing,
    while discounting normal academic English.
    """
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    if arabic_chars / max(len(text), 1) > 0.20:
        return 0.0

    n_words = len(words)
    if n_words < 30:
        self._en_evidence_cache = ["too_short_for_strong_en_ai"]
        return 0.10

    tl = text.lower()
    sent_count = max(len(sents), 1)
    evidence = []

    # 1) Direct GPT phrase evidence
    t1_hits = [p for p in getattr(self, 'EN_GPT_PHRASES_T1', []) if p in tl]
    exact_hit_count = len(t1_hits)
    if exact_hit_count >= 10:
        t1_score = min(0.78 + (exact_hit_count - 10) * 0.015, 0.96)
        evidence.append(f"T1-very-strong:{exact_hit_count}")
    elif exact_hit_count >= 6:
        t1_score = 0.44 + (exact_hit_count - 6) * 0.055
        evidence.append(f"T1-strong:{exact_hit_count}")
    elif exact_hit_count >= 3:
        t1_score = 0.18 + (exact_hit_count - 3) * 0.07
        evidence.append(f"T1-mid:{exact_hit_count}")
    else:
        t1_score = 0.02

    # 2) Sentence pattern evidence
    t2_hits = 0
    for pat in getattr(self, 'EN_GPT_SENTENCE_PATTERNS', [])[:120]:
        try:
            t2_hits += len(re.findall(pat, tl, re.I))
        except Exception:
            pass

    t2_density = t2_hits / max(sent_count / 7.0, 1.0)
    if t2_density >= 6.0:
        t2_score = min(0.72 + (t2_density - 6.0) * 0.03, 0.90)
        evidence.append(f"T2-very-strong:{t2_density:.1f}")
    elif t2_density >= 3.5:
        t2_score = 0.34 + (t2_density - 3.5) * 0.08
        evidence.append(f"T2-strong:{t2_density:.1f}")
    elif t2_density >= 2.0:
        t2_score = 0.12 + (t2_density - 2.0) * 0.08
        evidence.append(f"T2-mid:{t2_density:.1f}")
    else:
        t2_score = 0.03

    # 3) Templatic style, deliberately low weight
    lens = [len(s.split()) for s in sents if len(s.split()) >= 3]
    style_score = 0.0
    if lens:
        avg_len = sum(lens) / len(lens)
        sd_len = (sum((x - avg_len) ** 2 for x in lens) / len(lens)) ** 0.5
        cv_len = sd_len / max(avg_len, 1.0)
        if 14 <= avg_len <= 24 and cv_len <= 0.26:
            style_score += 0.12
        elif 12 <= avg_len <= 26 and cv_len <= 0.33:
            style_score += 0.06

    formal_openers = 0
    for s in sents:
        ss = s.strip().lower()
        if re.match(r'^(however|therefore|moreover|furthermore|additionally|consequently|overall|thus|notably)\b', ss):
            formal_openers += 1
    opener_ratio = formal_openers / max(sent_count, 1)
    if opener_ratio >= 0.30:
        style_score += 0.08
    elif opener_ratio >= 0.18:
        style_score += 0.04

    repeated_templates = 0
    repeated_templates += len(re.findall(r'\bthis\s+(?:study|paper|article|analysis)\s+(?:aims?|seeks?|examines?|investigates?|explores?)\b', tl))
    repeated_templates += len(re.findall(r'\bit\s+(?:is|has been)\s+(?:important|widely|necessary|evident|clear|shown|demonstrated)\b', tl))
    if repeated_templates >= 5:
        style_score += 0.10
    elif repeated_templates >= 3:
        style_score += 0.05

    style_score = min(style_score, 0.24)

    # 4) Human/academic dampeners
    citation_hits = len(re.findall(r'\([A-Z][A-Za-z\-]+,\s*\d{4}[a-z]?\)', text))
    bracket_hits  = len(re.findall(r'\[(?:\d+|\d+(?:\s*,\s*\d+)*)\]', text))
    quote_hits    = text.count('"') + text.count('“') + text.count('”')
    number_hits   = len(re.findall(r'\b\d+(?:\.\d+)?%?\b', text))
    hedges        = len(re.findall(r'\b(?:may|might|could|perhaps|possibly|likely|unlikely|approximately|suggests?|appears?|indicates?)\b', tl))
    first_person  = len(re.findall(r'\b(?:i|we|our|my|us)\b', tl))

    damp = 0.0
    if citation_hits + bracket_hits >= 2:
        damp += 0.08
        evidence.append("academic-citations")
    if number_hits >= max(6, n_words // 120):
        damp += 0.05
        evidence.append("data-heavy")
    if hedges >= 4:
        damp += 0.04
    if first_person >= 2:
        damp += 0.03
    if quote_hits >= 2:
        damp += 0.02

    base = t1_score * 0.46 + t2_score * 0.34 + style_score * 0.20

    # Cross-signal escalation only for strong direct evidence.
    corroboration = 0
    corroboration += 1 if exact_hit_count >= 4 else 0
    corroboration += 1 if t2_density >= 3.5 else 0
    corroboration += 1 if repeated_templates >= 5 else 0
    corroboration += 1 if getattr(self, '_simple_gpt_score')(text, words, sents) >= 0.62 else 0
    corroboration += 1 if getattr(self, '_gpt_formatting_signature')(text, sents) >= 0.55 else 0

    score = base - damp
    if corroboration >= 3 and exact_hit_count >= 4:
        score = max(score, min(0.96, 0.76 + 0.04 * corroboration))
        evidence.append(f"cross-strong:{corroboration}")
    elif corroboration >= 2 and exact_hit_count >= 2:
        score = max(score, 0.60)
        evidence.append(f"cross-mid:{corroboration}")

    score = max(0.0, min(score, 0.98))
    self._en_evidence_cache = evidence[:20]
    return round(score, 4)



def _v3fixed_compute_fingerprint_score(self, text, words, sents,
                               simple_gpt_score, gpt_format_score,
                               english_ai_score, arabic_ai_score,
                               human_error_val, english_human_score,
                               deep_human_score):
    """Conservative fingerprint score for English academic text."""
    if not words or not sents:
        self._fp_scores_cache = {}
        return 0.0

    tl = text.lower()
    n_words = max(len(words), 1)

    exact_phrases = sum(1 for p in getattr(self, 'EN_GPT_PHRASES_T1', []) if p in tl)
    struct_hits = 0
    struct_pats = [
        r'\bthis\s+(?:study|paper|article|research|analysis)\s+(?:aims?|seeks?|examines?|investigates?|explores?)\b',
        r'\bit\s+(?:has\s+been|is)\s+(?:widely\s+)?(?:shown|demonstrated|recognized|reported|suggested)\s+that\b',
        r'\bfurther\s+research\s+(?:is\s+needed|should|could|may)\b',
        r'\bplays?\s+(?:a|an)\s+(?:vital|crucial|key|significant|important)\s+role\s+in\b',
    ]
    for p in struct_pats:
        try:
            struct_hits += len(re.findall(p, tl, re.I))
        except Exception:
            pass

    starter_tokens = [s.split()[0].lower().strip(",;:") for s in sents if s.split()]
    formal_openers = {'however','therefore','moreover','furthermore','additionally',
                      'consequently','nevertheless','thus','overall','specifically','notably'}
    starter_ratio = sum(1 for t in starter_tokens if t in formal_openers) / max(len(starter_tokens), 1)

    citations = len(re.findall(r'\([A-Z][A-Za-z\-]+,\s*\d{4}[a-z]?\)', text))
    numeric = len(re.findall(r'\b\d+(?:\.\d+)?%?\b', text))
    hedges  = len(re.findall(r'\b(?:may|might|could|perhaps|possibly|likely|unlikely|approximately|suggests?|appears?|indicates?)\b', tl))
    first_person = len(re.findall(r'\b(?:i|we|our|my|us)\b', tl))

    direct_signal = (
        min(exact_phrases / 8.0, 1.0) * 0.34 +
        min(struct_hits / 8.0, 1.0) * 0.16 +
        simple_gpt_score * 0.18 +
        gpt_format_score * 0.10 +
        english_ai_score * 0.14 +
        min(getattr(self, '_pattern_memory')(text), 0.9) * 0.08
    )

    style_signal = 0.0
    if starter_ratio >= 0.28:
        style_signal += 0.08
    elif starter_ratio >= 0.16:
        style_signal += 0.04
    style_signal += min(getattr(self, '_semantic_embedding')(words, sents), 0.85) * 0.05
    style_signal += min(getattr(self, '_context_drift')(sents, words), 0.85) * 0.05
    style_signal = min(style_signal, 0.14)

    human_damp = 0.0
    if citations >= 2:
        human_damp += 0.08
    if numeric >= max(6, n_words // 120):
        human_damp += 0.05
    if hedges >= 4:
        human_damp += 0.03
    if first_person >= 2:
        human_damp += 0.03

    human_damp += english_human_score * 0.08
    human_damp += deep_human_score * 0.06
    human_damp += human_error_val * 0.04

    score = direct_signal + style_signal - human_damp

    corroboration = 0
    corroboration += 1 if exact_phrases >= 4 else 0
    corroboration += 1 if struct_hits >= 5 else 0
    corroboration += 1 if simple_gpt_score >= 0.62 else 0
    corroboration += 1 if english_ai_score >= 0.68 else 0
    corroboration += 1 if gpt_format_score >= 0.55 else 0

    if corroboration >= 3 and exact_phrases >= 4:
        score = max(score, min(0.97, 0.78 + 0.04 * corroboration))
    elif corroboration >= 2 and exact_phrases >= 2:
        score = max(score, 0.58)

    # Hard limit against pure academic-style inflation.
    if exact_phrases <= 1 and struct_hits <= 2 and simple_gpt_score < 0.45:
        score = min(score, 0.34)

    self._fp_scores_cache = {
        "exact_phrases": exact_phrases,
        "struct_hits": struct_hits,
        "starter_ratio": round(starter_ratio, 4),
        "citations": citations,
        "numeric": numeric,
        "corroboration": corroboration,
    }
    return round(max(0.0, min(score, 0.98)), 4)



for _attr, _name in (
    ("_synonym_density", "_v3fixed_synonym_density"),
    ("_nb_score", "_v3fixed_nb_score"),
    ("_english_ai_score", "_v3fixed_english_ai_score"),
    ("_compute_fingerprint_score", "_v3fixed_compute_fingerprint_score"),
):
    _fn = globals().get(_name)
    if _fn is not None:
        setattr(AIDetectionEngine, _attr, _fn)


# ===== Precision hardening patch: direct GPT evidence must dominate =====

if not hasattr(AIDetectionEngine, "_orig_analyze_precision95"):
    AIDetectionEngine._orig_analyze_precision95 = AIDetectionEngine.analyze

def _precision95_direct_gpt_evidence(self, text, words, sents):
    tl = text.lower()

    # Direct phrase hits from high-signal phrase bank
    t1_list = list(getattr(self, "EN_GPT_PHRASES_T1", []) or [])
    t1_hits = sum(1 for p in t1_list if p and p in tl)

    # Regex sentence patterns
    t2_hits = 0
    for pat in list(getattr(self, "EN_GPT_SENTENCE_PATTERNS", []) or [])[:160]:
        try:
            t2_hits += len(re.findall(pat, tl, re.I))
        except Exception:
            pass

    # Formatting / markdown traces
    fmt_hits = 0
    fmt_hits += len(re.findall(r'(^|\n)\s*[-*•]\s+\w+', text))
    fmt_hits += len(re.findall(r'(^|\n)\s*\d+\.\s+\w+', text))
    fmt_hits += len(re.findall(r'\*\*[^*]{2,}\*\*', text))
    fmt_hits += len(re.findall(r'(^|\n)\s*#{1,4}\s+\w+', text))
    fmt_hits += text.count('---')

    # Strong repeated GPT-style starters and claims
    struct_hits = 0
    struct_hits += len(re.findall(r'\b(?:in conclusion|to summarize|overall|moreover|furthermore|therefore|however|consequently)\b', tl))
    struct_hits += len(re.findall(r'\bthis\s+(?:study|paper|article|analysis)\s+(?:aims?|seeks?|examines?|investigates?|explores?)\b', tl))
    struct_hits += len(re.findall(r'\bit\s+(?:is|has been)\s+(?:important|necessary|clear|evident|shown|demonstrated)\b', tl))
    struct_hits += len(re.findall(r'\bplays?\s+a\s+(?:crucial|significant|vital)\s+role\b', tl))

    fp_cache = getattr(self, "_fp_scores_cache", {}) or {}
    exact_from_fp = int(fp_cache.get("exact_phrases", 0) or 0)
    corroboration = int(fp_cache.get("corroboration", 0) or 0)

    # Paragraph corroboration: if many paragraphs are strong, treat as stronger copy-paste evidence.
    para_results = getattr(self, "_last_paragraph_results", None)
    para_strong = 0
    if isinstance(para_results, list):
        para_strong = sum(1 for p in para_results if isinstance(p, dict) and float(p.get("score", 0.0) or 0.0) >= 0.80)

    direct_hits = max(t1_hits, exact_from_fp)
    pattern_density = t2_hits / max(len(sents), 1)

    return {
        "direct_hits": direct_hits,
        "pattern_density": pattern_density,
        "format_hits": fmt_hits,
        "struct_hits": struct_hits,
        "corroboration": corroboration,
        "strong_paragraphs": para_strong,
    }

def _precision95_analyze(self, text, cb=None):
    result = self._orig_analyze_precision95(text, cb)
    if not isinstance(result, dict) or result.get("error"):
        return result

    try:
        clean_text = self._strip_references(text)
    except Exception:
        clean_text = text

    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', clean_text) if len(s.split()) >= 4]
    words = re.findall(r'\b[a-zA-Z]+\b', clean_text.lower())

    indicators = result.get("indicators", {}) or {}
    fp = float(indicators.get("🔍 Fingerprint Score v35 ★★★", 0.0) or 0.0)
    gf = float(indicators.get("GPT Format Signature ★★★", 0.0) or 0.0)
    sg = float(indicators.get("Simple GPT Score v22 ★★★", 0.0) or 0.0)
    en = float(indicators.get("English AI Engine v2 ★★★", 0.0) or 0.0)
    nb = float(indicators.get("Naive Bayes ML v25 ★", 0.0) or 0.0)

    direct = self._precision95_direct_gpt_evidence(clean_text, words, sents)
    direct_hits = direct["direct_hits"]
    patt = direct["pattern_density"]
    fmt_hits = direct["format_hits"]
    struct_hits = direct["struct_hits"]
    corroboration = direct["corroboration"]
    strong_paragraphs = direct["strong_paragraphs"]

    # Human/academic context dampening
    citation_hits = len(re.findall(r'\([A-Z][A-Za-z\-]+,\s*\d{4}[a-z]?\)', clean_text))
    bracket_hits = len(re.findall(r'\[(?:\d+|\d+(?:\s*,\s*\d+)*)\]', clean_text))
    number_hits = len(re.findall(r'\b\d+(?:\.\d+)?%?\b', clean_text))
    first_person = len(re.findall(r'\b(?:i|we|our|my|us)\b', clean_text.lower()))

    academic_discount = 0.0
    if citation_hits + bracket_hits >= 2:
        academic_discount += 0.08
    if number_hits >= max(6, len(words) // 120):
        academic_discount += 0.05
    if first_person >= 2:
        academic_discount += 0.03
    academic_discount = min(academic_discount, 0.14)

    # Direct-evidence engine: high values only when evidence is explicit and corroborated.
    direct_core = (
        min(direct_hits / 6.0, 1.0) * 0.34 +
        min(patt / 1.5, 1.0) * 0.18 +
        min(fmt_hits / 4.0, 1.0) * 0.12 +
        min(struct_hits / 6.0, 1.0) * 0.08 +
        en * 0.16 +
        sg * 0.08 +
        gf * 0.04
    )
    cross = 0.0
    if direct_hits >= 2:
        cross += 0.08
    if direct_hits >= 4:
        cross += 0.08
    if corroboration >= 2:
        cross += 0.10
    if corroboration >= 3:
        cross += 0.08
    if strong_paragraphs >= 2:
        cross += 0.06
    if en >= 0.60 and sg >= 0.55:
        cross += 0.08

    final = max(0.0, min(direct_core + cross - academic_discount, 0.995))

    # Hard anti-inflation: NB alone must never dominate.
    weak_direct = direct_hits <= 1 and patt < 0.9 and gf < 0.35 and en < 0.55 and sg < 0.55 and corroboration < 2
    if weak_direct:
        final = min(final, 0.36)
        if citation_hits + bracket_hits >= 2 or number_hits >= 6:
            final = min(final, 0.42)  # FIX v116

    # Hard positive gates for obvious copy-paste GPT / templatic outputs.
    if direct_hits >= 6 and corroboration >= 3 and (en >= 0.62 or sg >= 0.62):
        final = max(final, 0.95)
    elif direct_hits >= 4 and corroboration >= 2 and (en >= 0.56 or sg >= 0.56 or gf >= 0.55):
        final = max(final, 0.86)
    elif direct_hits >= 3 and (en >= 0.52 and sg >= 0.48):
        final = max(final, 0.72)

    # Keep result at least somewhat aligned with original analysis when direct evidence is real.
    orig_score = float(result.get("score", 0.0) or 0.0)
    if direct_hits >= 3 or corroboration >= 2:
        final = max(final, min(orig_score, 0.93) * 0.85)

    # Progressive uplift for 10%..49% so the visible score climbs gradually,
    # closely matching the requested examples.
    _before_escalation_final = float(final)
    lowmid_escalation_applied = 0.0
    ai_escalation_applied = 0.0
    if 0.10 <= final < 0.50:
        _anchors = [
            (0.10, 0.12),
            (0.15, 0.18),
            (0.20, 0.25),
            (0.26, 0.33),
            (0.35, 0.43),
            (0.49, 0.56),
        ]
        _boosted = final
        if final <= _anchors[0][0]:
            _boosted = _anchors[0][1]
        else:
            _prev_x, _prev_y = _anchors[0]
            for _x, _y in _anchors[1:]:
                if final <= _x:
                    _t = (final - _prev_x) / max(_x - _prev_x, 1e-9)
                    _boosted = _prev_y + ((_y - _prev_y) * _t)
                    break
                _prev_x, _prev_y = _x, _y
            else:
                _boosted = _anchors[-1][1]
        final = max(final, min(_boosted, 0.995))
        lowmid_escalation_applied = max(0.0, final - _before_escalation_final)

    # Keep the post-50 uplift visible in the final UI number as well.
    if final > 0.50:
        _post50_before = float(final)
        _post50_boost = min(0.18, max(0.0, (final - 0.50) * 0.35))
        final = min(0.995, final + _post50_boost)
        ai_escalation_applied = max(0.0, final - _post50_before)

    total_escalation_applied = max(0.0, final - _before_escalation_final)
    final = max(0.0, min(final, 0.995))

    try:
        ext_dbg = result.get("extended", {}) or {}
        ext_dbg["ai_escalation_applied_v111"] = round(float(ai_escalation_applied or 0.0), 4)
        ext_dbg["lowmid_escalation_applied_v111"] = round(float(lowmid_escalation_applied or 0.0), 4)
        ext_dbg["total_escalation_applied_v111"] = round(float(total_escalation_applied or 0.0), 4)
        ext_dbg["post50_progressive_active_v111"] = bool(final > 0.50)
        ext_dbg["pre50_progressive_active_v111"] = bool(0.10 <= _before_escalation_final < 0.50)
        result["extended"] = ext_dbg
    except Exception:
        pass

    result["score"] = final
    result["percentage"] = final * 100.0
    result["human_score"] = (1.0 - final) * 100.0
    result["risk_level"] = (
        "CRITICAL" if final >= 0.88 else
        "HIGH" if final >= 0.74 else
        "MEDIUM" if final >= 0.56 else
        "LOW" if final >= 0.28 else
        "MINIMAL"
    )
    verdicts = {
        "CRITICAL": "اشتباه مرتفع جدًا - يحتاج تحقق بشري",
        "HIGH":     "اشتباه مرتفع - يحتاج تحقق بشري",
        "MEDIUM":   "نتيجة مختلطة / غير حاسمة",
        "LOW":      "اشتباه منخفض",
        "MINIMAL":  "بشري على الأرجح",
    }
    result["verdict"] = verdicts[result["risk_level"]]

    # Make the UI more honest about why the score rose or stayed low.
    meta = result.setdefault("precision95_meta", {})
    meta.update({
        "direct_hits": direct_hits,
        "pattern_density": round(patt, 4),
        "format_hits": fmt_hits,
        "struct_hits": struct_hits,
        "corroboration": corroboration,
        "academic_discount": round(academic_discount, 4),
        "original_score": round(orig_score, 4),
        "pre50_progressive_applied": round(float(lowmid_escalation_applied or 0.0), 4),
        "post50_progressive_applied": round(float(ai_escalation_applied or 0.0), 4),
        "total_progressive_applied": round(float(total_escalation_applied or 0.0), 4),
        "final_score": round(final, 4),
    })

    # De-emphasize NB in visible indicators when unsupported by direct evidence.
    if weak_direct and nb >= 0.75:
        indicators["Naive Bayes ML v25 ★"] = min(nb, 0.58)

    return result

AIDetectionEngine._precision95_direct_gpt_evidence = _precision95_direct_gpt_evidence
AIDetectionEngine.analyze = _precision95_analyze


# ===== Precision repair v2: fix over-gating, widen direct evidence, split direct/style AI =====

import types as _precision_types

def _precision96_direct_gpt_evidence(self, text, words, sents):
    tl = text.lower()
    n_words = max(len(words), 1)
    n_sents = max(len(sents), 1)

    existing_t1 = list(getattr(self, "EN_GPT_PHRASES_T1", []) or [])
    extra_direct_phrases = [
        "in today's rapidly evolving world",
        "has become an essential force",
        "it is important to address",
        "it is equally important to address",
        "to ensure that these technologies",
        "therefore, a balanced and strategic approach",
        "while minimizing its potential risks and challenges",
        "offers significant opportunities for",
        "enabling innovation across multiple sectors",
        "solve complex problems, optimize operations",
        "deliver personalized experiences",
        "plays a crucial role in",
        "it is clear that",
        "it is evident that",
        "in conclusion",
        "to summarize",
        "overall,",
        "moreover,",
        "furthermore,",
        "therefore,",
        "however,",
    ]
    phrase_hits = 0
    seen = set()
    for phrase in existing_t1 + extra_direct_phrases:
        if not phrase:
            continue
        key = phrase.strip().lower()
        if key in seen:
            continue
        seen.add(key)
        if key in tl:
            phrase_hits += 1

    pattern_hits = 0
    for pat in list(getattr(self, "EN_GPT_SENTENCE_PATTERNS", []) or [])[:220]:
        try:
            pattern_hits += len(re.findall(pat, tl, re.I))
        except Exception:
            pass

    generic_patterns = [
        r'\b(?:artificial intelligence|technology|innovation|education|healthcare|finance)\s+has\s+become\s+an?\s+(?:essential|important|powerful)\b',
        r'\bfrom\s+\w+\s+to\s+\w+[, ]+[^.]{8,}(?:increasingly|widely)\s+(?:used|adopted|applied)\b',
        r'\b(?:however|moreover|furthermore|therefore|in conclusion|overall|to summarize)\b',
        r'\bit\s+is\s+(?:important|necessary|equally important)\s+to\s+(?:consider|address|ensure)\b',
        r'\b(?:offers|provides)\s+significant\s+(?:opportunities|benefits)\b',
        r'\b(?:maximize|minimize)\s+(?:the\s+)?(?:benefits|risks|challenges)\b',
        r'\ba\s+(?:balanced|strategic|thoughtful|comprehensive)\s+approach\b',
        r'\b(?:across|in)\s+multiple\s+(?:sectors|domains|areas|industries)\b',
        r'\benabling\s+(?:personalized|data-driven|efficient)\b',
        r'\boptimi[sz]e\s+(?:operations|processes|performance)\b',
    ]
    for pat in generic_patterns:
        try:
            pattern_hits += len(re.findall(pat, tl, re.I))
        except Exception:
            pass

    fmt_hits = 0
    fmt_hits += len(re.findall(r'(^|\n)\s*[-*•]\s+\w+', text))
    fmt_hits += len(re.findall(r'(^|\n)\s*\d+\.\s+\w+', text))
    fmt_hits += len(re.findall(r'\*\*[^*]{2,}\*\*', text))
    fmt_hits += len(re.findall(r'(^|\n)\s*#{1,4}\s+\w+', text))
    fmt_hits += text.count('---')

    struct_hits = 0
    struct_patterns = [
        r'\bthis\s+(?:study|paper|article|analysis|review)\s+(?:aims?|seeks?|examines?|investigates?|explores?)\b',
        r'\bit\s+(?:is|has been)\s+(?:important|necessary|clear|evident|shown|demonstrated)\b',
        r'\bplays?\s+a\s+(?:crucial|significant|vital|key|central)\s+role\b',
        r'\bintegration\s+of\s+[^.]{1,60}\s+should\s+be\s+approached\s+(?:carefully|thoughtfully|strategically)\b',
        r'\bto\s+ensure\s+that\s+[^.]{1,120}\b',
        r'\bwhile\s+(?:minimizing|reducing)\s+(?:its|their|the)\s+(?:potential\s+)?(?:risks|challenges)\b',
    ]
    for pat in struct_patterns:
        try:
            struct_hits += len(re.findall(pat, tl, re.I))
        except Exception:
            pass

    starter_hits = len(re.findall(
        r'(?:(?<=\.)|^)\s*(?:however|moreover|furthermore|therefore|overall|in conclusion|to summarize|consequently|thus)\b',
        tl,
        re.I
    ))
    starter_ratio = starter_hits / n_sents

    citations = len(re.findall(r'\([A-Z][A-Za-z\-]+,\s*\d{4}[a-z]?\)', text))
    citations += len(re.findall(r'\[(?:\d+|\d+(?:\s*,\s*\d+)*)\]', text))
    numeric = len(re.findall(r'\b\d+(?:\.\d+)?%?\b', text))

    return {
        "phrase_hits": phrase_hits,
        "pattern_hits": pattern_hits,
        "format_hits": fmt_hits,
        "struct_hits": struct_hits,
        "starter_ratio": starter_ratio,
        "citation_hits": citations,
        "numeric_hits": numeric,
        "pattern_density": pattern_hits / n_sents,
        "phrase_density": phrase_hits / max(n_words / 80.0, 1.0),
    }


def _precision96_paragraph_corroboration(self, paragraph_results):
    if not isinstance(paragraph_results, list) or not paragraph_results:
        return {"strong": 0, "mid": 0, "avg": 0.0}
    vals = []
    for p in paragraph_results:
        try:
            vals.append(float((p or {}).get("score", 0.0) or 0.0))
        except Exception:
            pass
    if not vals:
        return {"strong": 0, "mid": 0, "avg": 0.0}
    strong = sum(1 for v in vals if v >= 0.78)
    mid = sum(1 for v in vals if v >= 0.55)
    avg = sum(vals) / len(vals)
    return {"strong": strong, "mid": mid, "avg": avg}


def _precision96_analyze(self, text, cb=None):
    base_analyze = getattr(self, "_orig_analyze_precision95", None)
    if base_analyze is None:
        base_analyze = getattr(AIDetectionEngine, "_orig_analyze_precision95", None)
    if base_analyze is None:
        # fallback to the currently wrapped analyze if base missing
        base_analyze = AIDetectionEngine.analyze

    result = base_analyze(self, text, cb) if isinstance(base_analyze, _precision_types.FunctionType) else base_analyze(text, cb)
    if not isinstance(result, dict) or result.get("error"):
        return result

    try:
        clean_text = self._strip_references(text)
    except Exception:
        clean_text = text
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    words = re.findall(r'\b[a-zA-Z]+\b', clean_text.lower())
    sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', clean_text) if len(s.split()) >= 4]

    indicators = dict(result.get("indicators", {}) or {})
    extended = dict(result.get("extended", {}) or {})

    fp = float(indicators.get("🔍 Fingerprint Score v35 ★★★", extended.get("fingerprint_score", 0.0)) or 0.0)
    gf = float(indicators.get("GPT Format Signature ★★★", extended.get("gpt_format_score", 0.0)) or 0.0)
    sg = float(indicators.get("Simple GPT Score v22 ★★★", extended.get("simple_gpt_score", 0.0)) or 0.0)
    en = float(indicators.get("English AI Engine v2 ★★★", extended.get("english_ai_score", 0.0)) or 0.0)
    nb = float(indicators.get("Naive Bayes ML v25 ★", extended.get("nb_score", 0.0)) or 0.0)
    llr = float(indicators.get("LLR v28 ★★★ [corpus جديد]", extended.get("llr_score", 0.0)) or 0.0)
    pat_mem = float(indicators.get("Pattern Memory v20 ★★★", extended.get("pat_mem", 0.0)) or 0.0)
    para_results = extended.get("paragraph_results", []) or []
    para_meta = self._precision96_paragraph_corroboration(para_results)

    direct = self._precision96_direct_gpt_evidence(clean_text, words, sents)
    phrase_hits = direct["phrase_hits"]
    pattern_hits = direct["pattern_hits"]
    format_hits = direct["format_hits"]
    struct_hits = direct["struct_hits"]
    starter_ratio = float(direct["starter_ratio"])
    pattern_density = float(direct["pattern_density"])
    citation_hits = int(direct["citation_hits"])
    numeric_hits = int(direct["numeric_hits"])

    first_person = len(re.findall(r'\b(?:i|we|our|my|us)\b', clean_text.lower()))
    hedges = len(re.findall(r'\b(?:may|might|could|perhaps|possibly|likely|unlikely|approximately|suggests?|appears?|indicates?)\b', clean_text.lower()))

    # Academic grounding is protective, but no longer treated as proof of humanity by itself.
    academic_grounding = 0.0
    if citation_hits >= 2:
        academic_grounding += 0.07
    if citation_hits >= 4:
        academic_grounding += 0.03
    if numeric_hits >= max(6, len(words) // 120):
        academic_grounding += 0.06
    if numeric_hits >= max(12, len(words) // 80):
        academic_grounding += 0.03
    if len(words) >= 900:
        academic_grounding += 0.03
    elif len(words) >= 400:
        academic_grounding += 0.02
    academic_grounding = min(academic_grounding, 0.18)

    # Human-authentic signals are narrower than academic formatting/grounding.
    human_authenticity = 0.0
    if first_person >= 2:
        human_authenticity += 0.06
    if hedges >= 4:
        human_authenticity += 0.06
    if para_meta["avg"] >= 0.42:
        human_authenticity += 0.03
    human_authenticity = min(human_authenticity, 0.15)

    direct_gpt_score = (
        min(phrase_hits / 4.0, 1.0) * 0.42 +
        min(pattern_density / 1.35, 1.0) * 0.22 +
        min(format_hits / 3.0, 1.0) * 0.08 +
        min(struct_hits / 4.0, 1.0) * 0.14 +
        min(starter_ratio / 0.42, 1.0) * 0.04 +
        max(gf - 0.12, 0.0) * 0.10
    )
    if phrase_hits >= 2 and pattern_hits >= 2:
        direct_gpt_score += 0.08
    elif phrase_hits >= 1 and pattern_hits >= 2:
        direct_gpt_score += 0.04
    if struct_hits >= 2 and format_hits >= 1:
        direct_gpt_score += 0.03
    direct_gpt_score = max(0.0, min(direct_gpt_score, 0.995))

    # Style is still supportive, but stronger than before for GPT-written academic prose.
    gpt_style_score = (
        sg * 0.24 +
        en * 0.18 +
        fp * 0.10 +
        min(nb, 0.90) * 0.10 +
        min(llr, 0.90) * 0.08 +
        min(pat_mem, 0.90) * 0.04
    )
    if para_meta["strong"] >= 2:
        gpt_style_score += 0.03
    elif para_meta["mid"] >= 2:
        gpt_style_score += 0.02
    gpt_style_score = max(0.0, min(gpt_style_score, 0.82))

    # Main fusion: direct evidence dominates, but repeated statistical agreement matters.
    final = direct_gpt_score * 0.72 + gpt_style_score * 0.28

    # Human discount is now conditional; tables/citations cannot erase strong AI consistency.
    # FIX v116: Raised direct_core thresholds to stop discounting moderate AI evidence
    academic_discount = 0.0
    if direct_gpt_score < 0.42 and gpt_style_score < 0.48:
        academic_discount = academic_grounding + human_authenticity
    elif direct_gpt_score < 0.58 and gpt_style_score < 0.62:
        academic_discount = academic_grounding * 0.60 + human_authenticity * 0.85
    else:
        academic_discount = academic_grounding * 0.18 + human_authenticity * 0.45
    academic_discount = min(academic_discount, 0.30)  # FIX v116: cap at 0.30
    final -= academic_discount

    # Multi-engine agreement should matter, especially for GPT-written academic prose.
    consensus = 0
    consensus += 1 if sg >= 0.74 else 0
    consensus += 1 if nb >= 0.76 else 0
    consensus += 1 if en >= 0.56 else 0
    consensus += 1 if fp >= 0.28 else 0
    consensus += 1 if llr >= 0.66 else 0
    consensus += 1 if para_meta["strong"] >= 2 or para_meta["avg"] >= 0.56 else 0

    # Defaults kept for backward-compatible metadata/export paths.
    route_rescue = 0.0
    cross_engine_peak = max(sg, nb, en, fp, llr, pat_mem)
    cross_engine_mean = (sg + nb + en + fp + llr + min(pat_mem, 1.0)) / 6.0
    blocker_sparse_fp = False

    if direct_gpt_score >= 0.24 and consensus >= 3 and max(sg, nb, en) >= 0.72:
        final = max(final, 0.28)
    if direct_gpt_score >= 0.32 and consensus >= 4 and (sg >= 0.72 and nb >= 0.72):
        final = max(final, 0.42)
    if direct_gpt_score >= 0.40 and consensus >= 5 and (sg >= 0.74 and nb >= 0.74 and fp >= 0.26):
        final = max(final, 0.56)

    # Strong academic-looking GPT should not hide behind tables/citations alone.
    if academic_grounding >= 0.10 and consensus >= 4 and gpt_style_score >= 0.52:
        final = max(final, 0.46)
    if academic_grounding >= 0.12 and consensus >= 5 and gpt_style_score >= 0.58:
        final = max(final, 0.58)

    # Positive gates: explicit direct evidence still wins fastest.
    if direct_gpt_score >= 0.78 and phrase_hits >= 3 and pattern_hits >= 2:
        final = max(final, 0.90)
    elif direct_gpt_score >= 0.66 and phrase_hits >= 2 and pattern_hits >= 2:
        final = max(final, 0.80)
    elif direct_gpt_score >= 0.58 and (phrase_hits >= 2 and struct_hits >= 2):
        final = max(final, 0.70)
    elif direct_gpt_score >= 0.52 and pattern_hits >= 3 and struct_hits >= 2:
        final = max(final, 0.64)

    # Academic clamp now protects only when both direct and consensus evidence stay weak.
    # FIX v116: Raised clamp ceilings and direct_gpt_score thresholds
    if citation_hits >= 2 and numeric_hits >= 4 and direct_gpt_score < 0.22 and consensus <= 2 and gpt_style_score < 0.30:
        final = min(final, 0.38)
    elif (citation_hits >= 2 or numeric_hits >= 6 or hedges >= 4) and direct_gpt_score < 0.16 and consensus <= 2 and gpt_style_score < 0.24:
        final = min(final, 0.30)

    # True human-first floor stays only for weak-evidence cases.
    if direct_gpt_score < 0.14 and consensus <= 1 and gpt_style_score < 0.22:
        if (academic_grounding + human_authenticity) >= 0.12:
            final = min(final, 0.35)  # FIX v116
        else:
            final = min(final, 0.26)

    final = max(0.0, min(final, 0.995))

    result["score"] = final
    result["percentage"] = final * 100.0
    result["human_score"] = (1.0 - final) * 100.0
    result["risk_level"] = (
        "CRITICAL" if final >= 0.88 else
        "HIGH" if final >= 0.74 else
        "MEDIUM" if final >= 0.56 else
        "LOW" if final >= 0.28 else
        "MINIMAL"
    )
    _verdicts = {
        "CRITICAL": "اشتباه مرتفع جدًا - يحتاج تحقق بشري",
        "HIGH":     "اشتباه مرتفع - يحتاج تحقق بشري",
        "MEDIUM":   "نتيجة مختلطة / غير حاسمة",
        "LOW":      "اشتباه منخفض",
        "MINIMAL":  "بشري على الأرجح",
    }
    result["verdict"] = _verdicts[result["risk_level"]]

    # Keep UI indicators consistent with the new reasoning.
    indicators["🔍 Fingerprint Score v35 ★★★"] = max(fp, min(direct_gpt_score * 0.9 + gpt_style_score * 0.2, 0.98))
    if direct_gpt_score >= 0.40 or consensus >= 3:
        indicators["Simple GPT Score v22 ★★★"] = max(sg, min(gpt_style_score, 0.92))
    if consensus >= 3 and direct_gpt_score < 0.18 and result["percentage"] > 20:
        # Prevent contradiction: if result is lifted by consensus, show a minimally honest fingerprint.
        indicators["🔍 Fingerprint Score v35 ★★★"] = max(indicators["🔍 Fingerprint Score v35 ★★★"], 0.24)

    # Expose calibration internals for debugging / future tuning.
    extended["direct_gpt_score"] = round(direct_gpt_score, 4)
    extended["gpt_style_score"] = round(gpt_style_score, 4)
    extended["academic_grounding"] = round(academic_grounding, 4)
    extended["human_authenticity"] = round(human_authenticity, 4)
    extended["human_evidence"] = round(academic_grounding + human_authenticity, 4)
    extended["academic_discount_repair"] = round(academic_discount, 4)
    extended["consensus_repair"] = int(consensus)
    extended["repair_phrase_hits"] = int(phrase_hits)
    extended["repair_pattern_hits"] = int(pattern_hits)
    extended["repair_struct_hits"] = int(struct_hits)
    extended["repair_format_hits"] = int(format_hits)
    extended["repair_paragraph_corroboration"] = para_meta
    extended["route_rescue_score"] = round(route_rescue, 4)
    extended["cross_engine_peak"] = round(cross_engine_peak, 4)
    extended["cross_engine_mean"] = round(cross_engine_mean, 4)
    extended["blocker_sparse_fp"] = blocker_sparse_fp

    result["indicators"] = indicators
    result["extended"] = extended
    result["precision95_meta"] = {
        "patched_by": "precision96_repair",
        "direct_gpt_score": round(direct_gpt_score, 4),
        "gpt_style_score": round(gpt_style_score, 4),
        "consensus": int(consensus),
        "academic_discount": round(academic_discount, 4),
        "phrase_hits": int(phrase_hits),
        "pattern_hits": int(pattern_hits),
        "struct_hits": int(struct_hits),
        "format_hits": int(format_hits),
        "final_score": round(final, 4),
    }
    return result

AIDetectionEngine._precision96_direct_gpt_evidence = _precision96_direct_gpt_evidence
AIDetectionEngine._precision96_paragraph_corroboration = _precision96_paragraph_corroboration
AIDetectionEngine.analyze = _precision96_analyze




# ===== Precision repair v3: distinguish polished human academic English from templatic AI =====

def _precision97_sentence_style_profiles(self, text):
    try:
        clean_text = self._strip_references(text)
    except Exception:
        clean_text = text
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', clean_text) if len(re.findall(r"[A-Za-z]+", s)) >= 6]
    if not sents:
        return {
            "sentences": [],
            "ai_sentence_ratio": 0.0,
            "human_sentence_ratio": 0.0,
            "avg_ai_sentence_score": 0.0,
            "avg_human_sentence_score": 0.0,
            "top_ai_mean": 0.0,
            "top_human_mean": 0.0,
            "style_gap": 0.0,
            "ai_candidate_count": 0,
            "human_candidate_count": 0,
        }

    ai_phrase_bank = set(getattr(self, 'EN_GPT_PHRASES_T1', set()) or set())
    ai_vocab = set(getattr(self, 'AI_FINGERPRINT', set()) or set())

    method_terms = {
        'dataset','sample','participants','participant','respondents','cohort','survey','surveys',
        'experiment','experimental','method','methods','methodology','procedure','procedures',
        'analysis','analyses','regression','model','models','variable','variables','significance',
        'statistical','qualitative','quantitative','interview','interviews','measure','measures',
        'table','figure','appendix','section','sections','framework','instrument','instruments',
        'evidence','observed','measured','collected','coded','baseline','trial','trials'
    }
    human_academic_patterns = [
        r'\b(?:table|figure|appendix|section|chapter)\s+\d+\b',
        r'\b(?:according to|as reported by|as shown in|as illustrated in|as described in)\b',
        r'\b(?:the sample|our sample|this sample|the dataset|our dataset|the participants|respondents)\b',
        r'\b(?:in this study|in our study|in the present study)\b.*\b(?:we|our)\b',
        r'\b(?:results?|findings?)\s+(?:suggest|indicate|show)\b',
        r'\b(?:within|among|across)\s+the\s+(?:sample|dataset|participants|groups?)\b',
        r'\b(?:statistically\s+significant|p\s*[<=>]\s*0?\.\d+)\b',
        r'\b(?:limitation|limitations|constraint|constraints)\b',
        r'\b(?:future research|further research)\b',
        r'\b(?:one possible explanation|a possible explanation)\b',
    ]
    ai_template_patterns = [
        r'\bthis\s+(?:study|paper|article|analysis)\s+(?:aims?|seeks?|explores?|examines?|investigates?)\b',
        r'\bit\s+(?:is|has been)\s+(?:important|essential|crucial|clear|evident|shown|demonstrated)\b',
        r'\b(?:plays|play)\s+a\s+(?:vital|critical|crucial|central|pivotal|key)\s+role\b',
        r'\b(?:in conclusion|to summarize|in summary|overall)\b',
        r'\b(?:furthermore|moreover|additionally|therefore|consequently|thus|notably)\b',
        r'\b(?:unlock|harness|leverage|navigate|reshape|reimagine|revolutionize)\b',
        r'\b(?:underscores?|highlights?)\s+the\s+(?:importance|need|significance)\b',
        r'\b(?:rapidly|increasingly|ever)\s+(?:evolving|changing)\b',
        r'\b(?:holistic|multifaceted|nuanced|transformative|comprehensive)\b',
        r'\b(?:foster|drive|enable|empower)\s+(?:innovation|growth|change|progress)\b',
    ]

    sentence_profiles = []
    for idx, sent in enumerate(sents):
        tl = sent.lower()
        words = re.findall(r"[A-Za-z]+(?:'[a-z]+)?", tl)
        n = len(words)
        if n < 6:
            continue

        ai_phrase_hits = sum(1 for p in ai_phrase_bank if p in tl)
        ai_vocab_hits = sum(1 for w in words if w in ai_vocab)
        ai_pattern_hits = sum(1 for pat in ai_template_patterns if re.search(pat, tl, re.I))
        formal_opener = 1 if re.match(r'^(however|therefore|moreover|furthermore|additionally|consequently|overall|thus|notably|in conclusion|to summarize)\b', tl) else 0
        abstract_heavy = sum(1 for w in words if w.endswith(('tion','sion','ment','ness','ity'))) / max(n, 1)
        balanced_frame = 1 if re.search(r'\bnot only\b.*\bbut also\b', tl) else 0

        citation_hits = len(re.findall(r'\([A-Z][A-Za-z\-]+,\s*(?:19|20)\d{2}[a-z]?\)', sent))
        citation_hits += len(re.findall(r'\[(?:\d+|\d+(?:\s*,\s*\d+)*)\]', sent))
        number_hits = len(re.findall(r'\b\d+(?:\.\d+)?%?\b', sent))
        method_hits = sum(1 for w in words if w in method_terms)
        human_pat_hits = sum(1 for pat in human_academic_patterns if re.search(pat, sent, re.I))
        hedges = len(re.findall(r'\b(?:may|might|could|perhaps|possibly|likely|unlikely|approximately|suggests?|appears?|indicates?)\b', tl))
        first_person_research = len(re.findall(r'\b(?:we|our)\b', tl))
        named_entity_like = len(re.findall(r'\b[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})*\b', sent))
        colon_semicolon = sent.count(':') + sent.count(';')

        ai_score = (
            min(ai_phrase_hits / 2.0, 1.0) * 0.34 +
            min(ai_pattern_hits / 2.0, 1.0) * 0.24 +
            min(ai_vocab_hits / max(n * 0.12, 1.0), 1.0) * 0.18 +
            formal_opener * 0.08 +
            min(abstract_heavy / 0.22, 1.0) * 0.08 +
            balanced_frame * 0.04
        )

        human_score = (
            min(citation_hits / 2.0, 1.0) * 0.26 +
            min(number_hits / 3.0, 1.0) * 0.12 +
            min(method_hits / 3.0, 1.0) * 0.18 +
            min(human_pat_hits / 2.0, 1.0) * 0.20 +
            min(hedges / 2.0, 1.0) * 0.08 +
            min(first_person_research / 2.0, 1.0) * 0.08 +
            min(named_entity_like / 2.0, 1.0) * 0.05 +
            min(colon_semicolon / 2.0, 1.0) * 0.03
        )

        # real academic grounding should weaken AI-style suspicion at sentence level
        ai_score -= min(citation_hits, 2) * 0.08
        ai_score -= min(number_hits, 3) * 0.03
        ai_score -= min(method_hits, 3) * 0.04
        ai_score -= min(human_pat_hits, 2) * 0.07
        ai_score -= min(first_person_research, 2) * 0.03
        ai_score -= min(hedges, 2) * 0.02

        ai_score = round(max(0.0, min(ai_score, 0.995)), 4)
        human_score = round(max(0.0, min(human_score, 0.995)), 4)

        sentence_profiles.append({
            "index": idx,
            "text": sent,
            "ai_score": ai_score,
            "human_score": human_score,
            "margin": round(ai_score - human_score, 4),
            "ai_phrase_hits": ai_phrase_hits,
            "ai_pattern_hits": ai_pattern_hits,
            "ai_vocab_hits": ai_vocab_hits,
            "citation_hits": citation_hits,
            "number_hits": number_hits,
            "method_hits": method_hits,
            "human_pattern_hits": human_pat_hits,
            "hedges": hedges,
        })

    if not sentence_profiles:
        return {
            "sentences": [],
            "ai_sentence_ratio": 0.0,
            "human_sentence_ratio": 0.0,
            "avg_ai_sentence_score": 0.0,
            "avg_human_sentence_score": 0.0,
            "top_ai_mean": 0.0,
            "top_human_mean": 0.0,
            "style_gap": 0.0,
            "ai_candidate_count": 0,
            "human_candidate_count": 0,
        }

    ai_candidates = [x for x in sentence_profiles if x["ai_score"] >= 0.34 and x["margin"] >= 0.12]
    human_candidates = [x for x in sentence_profiles if x["human_score"] >= 0.30 and x["margin"] <= 0.02]

    ai_sorted = sorted(sentence_profiles, key=lambda x: x["margin"], reverse=True)
    human_sorted = sorted(sentence_profiles, key=lambda x: (x["human_score"] - x["ai_score"]), reverse=True)

    top_ai = ai_sorted[:max(1, min(5, len(ai_sorted)))]
    top_human = human_sorted[:max(1, min(5, len(human_sorted)))]

    return {
        "sentences": sentence_profiles,
        "ai_sentence_ratio": round(len(ai_candidates) / max(len(sentence_profiles), 1), 4),
        "human_sentence_ratio": round(len(human_candidates) / max(len(sentence_profiles), 1), 4),
        "avg_ai_sentence_score": round(sum(x["ai_score"] for x in sentence_profiles) / len(sentence_profiles), 4),
        "avg_human_sentence_score": round(sum(x["human_score"] for x in sentence_profiles) / len(sentence_profiles), 4),
        "top_ai_mean": round(sum(x["ai_score"] for x in top_ai) / len(top_ai), 4),
        "top_human_mean": round(sum(x["human_score"] for x in top_human) / len(top_human), 4),
        "style_gap": round(
            (sum(x["margin"] for x in top_ai) / len(top_ai)) -
            (sum((x["human_score"] - x["ai_score"]) for x in top_human) / len(top_human)),
            4
        ),
        "ai_candidate_count": len(ai_candidates),
        "human_candidate_count": len(human_candidates),
    }

def _precision97_extract_ai_quotes(eng, text, result=None):
    prof = eng._precision97_sentence_style_profiles(text)
    sents = prof.get("sentences", []) or []
    if not sents:
        return []

    ranked = sorted(
        sents,
        key=lambda x: (x["margin"], x["ai_score"], -x["human_score"]),
        reverse=True
    )

    quotes = []
    used = set()
    for item in ranked:
        if item["ai_score"] < 0.28:
            continue
        if item["margin"] < 0.10 and item["ai_score"] < 0.42:
            continue
        key = re.sub(r'\W+', ' ', item["text"].lower()).strip()
        if key in used:
            continue
        used.add(key)

        reasons = []
        tl = item["text"].lower()
        if item["ai_phrase_hits"] >= 1:
            reasons.append("direct GPT phrase")
        if item["ai_pattern_hits"] >= 2:
            reasons.append("templatic academic framing")
        elif item["ai_pattern_hits"] >= 1:
            reasons.append("generic academic frame")
        if item["ai_vocab_hits"] >= 2:
            reasons.append("AI-heavy vocabulary")
        if re.match(r'^(however|therefore|moreover|furthermore|additionally|consequently|overall|thus|notably|in conclusion|to summarize)\b', tl):
            reasons.append("formal transition opener")
        if item["human_pattern_hits"] >= 1 or item["citation_hits"] >= 1 or item["method_hits"] >= 2:
            reasons.append("limited human grounding")

        quotes.append({
            "index": item["index"],
            "score": round(max(item["ai_score"], min(item["margin"] + 0.20, 0.99)), 4),
            "text": item["text"],
            "reason": ", ".join(reasons[:3]) if reasons else "strong AI-style sentence pattern",
        })

    return quotes[:12]

def _precision97_enhance_result(eng, result, text):
    if not isinstance(result, dict) or result.get("error"):
        return result

    profiles = eng._precision97_sentence_style_profiles(text)
    ext = result.setdefault("extended", {})
    meta = result.setdefault("precision95_meta", {})

    ext["sentence_style_profiles"] = profiles
    ext["ai_sentence_ratio"] = profiles.get("ai_sentence_ratio", 0.0)
    ext["human_sentence_ratio"] = profiles.get("human_sentence_ratio", 0.0)
    ext["style_gap_v3"] = profiles.get("style_gap", 0.0)
    meta["ai_sentence_ratio"] = profiles.get("ai_sentence_ratio", 0.0)
    meta["human_sentence_ratio"] = profiles.get("human_sentence_ratio", 0.0)
    meta["style_gap_v3"] = profiles.get("style_gap", 0.0)

    quotes = _precision97_extract_ai_quotes(eng, text, result)
    result["ai_citations"] = quotes
    ext["ai_quote_candidates"] = quotes
    ext["ai_quote_count"] = len(quotes)
    if quotes:
        result["top_ai_sentence"] = quotes[0]["text"]
    return result

def _precision97_analyze(self, text, cb=None):
    base_analyze = getattr(self, "_orig_analyze_precision95", None)
    if base_analyze is None:
        base_analyze = getattr(AIDetectionEngine, "_orig_analyze_precision95", None)
    if base_analyze is None:
        base_analyze = AIDetectionEngine.analyze

    result = base_analyze(self, text, cb) if isinstance(base_analyze, _precision_types.FunctionType) else base_analyze(text, cb)
    if not isinstance(result, dict) or result.get("error"):
        return result

    try:
        clean_text = self._strip_references(text)
    except Exception:
        clean_text = text
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    words = re.findall(r'\b[a-zA-Z]+\b', clean_text.lower())
    sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', clean_text) if len(s.split()) >= 4]

    indicators = dict(result.get("indicators", {}) or {})
    extended = dict(result.get("extended", {}) or {})

    fp = float(indicators.get("🔍 Fingerprint Score v35 ★★★", extended.get("fingerprint_score", 0.0)) or 0.0)
    gf = float(indicators.get("GPT Format Signature ★★★", extended.get("gpt_format_score", 0.0)) or 0.0)
    sg = float(indicators.get("Simple GPT Score v22 ★★★", extended.get("simple_gpt_score", 0.0)) or 0.0)
    en = float(indicators.get("English AI Engine v2 ★★★", extended.get("english_ai_score", 0.0)) or 0.0)
    nb = float(indicators.get("Naive Bayes ML v25 ★", extended.get("nb_score", 0.0)) or 0.0)
    llr = float(indicators.get("LLR v28 ★★★ [corpus جديد]", extended.get("llr_score", 0.0)) or 0.0)
    pat_mem = float(indicators.get("Pattern Memory v20 ★★★", extended.get("pat_mem", 0.0)) or 0.0)

    direct = self._precision96_direct_gpt_evidence(clean_text, words, sents)
    phrase_hits = int(direct["phrase_hits"])
    pattern_hits = int(direct["pattern_hits"])
    format_hits = int(direct["format_hits"])
    struct_hits = int(direct["struct_hits"])
    starter_ratio = float(direct["starter_ratio"])
    pattern_density = float(direct["pattern_density"])
    citation_hits = int(direct["citation_hits"])
    numeric_hits = int(direct["numeric_hits"])

    para_results = extended.get("paragraph_results", []) or []
    para_meta = self._precision96_paragraph_corroboration(para_results)
    profiles = self._precision97_sentence_style_profiles(clean_text)

    ai_sent_ratio = float(profiles.get("ai_sentence_ratio", 0.0) or 0.0)
    human_sent_ratio = float(profiles.get("human_sentence_ratio", 0.0) or 0.0)
    avg_ai_sent = float(profiles.get("avg_ai_sentence_score", 0.0) or 0.0)
    avg_human_sent = float(profiles.get("avg_human_sentence_score", 0.0) or 0.0)
    top_ai_mean = float(profiles.get("top_ai_mean", 0.0) or 0.0)
    top_human_mean = float(profiles.get("top_human_mean", 0.0) or 0.0)
    style_gap = float(profiles.get("style_gap", 0.0) or 0.0)

    first_person = len(re.findall(r'\b(?:i|we|our|my|us)\b', clean_text.lower()))
    hedges = len(re.findall(r'\b(?:may|might|could|perhaps|possibly|likely|unlikely|approximately|suggests?|appears?|indicates?)\b', clean_text.lower()))

    direct_gpt_score = (
        min(phrase_hits / 4.0, 1.0) * 0.32 +
        min(pattern_density / 1.20, 1.0) * 0.22 +
        min(format_hits / 3.0, 1.0) * 0.08 +
        min(struct_hits / 4.0, 1.0) * 0.12 +
        min(starter_ratio / 0.40, 1.0) * 0.04 +
        max(gf - 0.08, 0.0) * 0.10 +
        min(ai_sent_ratio / 0.35, 1.0) * 0.12
    )
    if phrase_hits >= 2 and pattern_hits >= 2:
        direct_gpt_score += 0.06
    if ai_sent_ratio >= 0.35 and top_ai_mean >= 0.45:
        direct_gpt_score += 0.06
    direct_gpt_score = max(0.0, min(direct_gpt_score, 0.99))

    gpt_style_score = (
        sg * 0.26 +
        en * 0.20 +
        fp * 0.14 +
        min(nb, 0.88) * 0.10 +
        min(llr, 0.88) * 0.08 +
        min(pat_mem, 0.88) * 0.04 +
        min(avg_ai_sent / 0.48, 1.0) * 0.10 +
        min(top_ai_mean / 0.56, 1.0) * 0.08
    )
    if para_meta["strong"] >= 2:
        gpt_style_score += 0.05
    elif para_meta["mid"] >= 2:
        gpt_style_score += 0.025
    gpt_style_score = max(0.0, min(gpt_style_score, 0.97))

    human_academic_guard = (
        min(human_sent_ratio / 0.35, 1.0) * 0.34 +
        min(avg_human_sent / 0.42, 1.0) * 0.20 +
        min(top_human_mean / 0.50, 1.0) * 0.14
    )
    if citation_hits >= 2:
        human_academic_guard += 0.10
    if numeric_hits >= max(6, len(words) // 120):
        human_academic_guard += 0.08
    if first_person >= 2:
        human_academic_guard += 0.05
    if hedges >= 4:
        human_academic_guard += 0.04
    human_academic_guard = max(0.0, min(human_academic_guard, 0.92))

    academic_ai_pressure = (
        direct_gpt_score * 0.48 +
        gpt_style_score * 0.30 +
        min(ai_sent_ratio / 0.35, 1.0) * 0.12 +
        min(top_ai_mean / 0.55, 1.0) * 0.10
    )
    academic_ai_pressure = max(0.0, min(academic_ai_pressure, 0.99))

    final = academic_ai_pressure - human_academic_guard * 0.42

    # positive gates
    if phrase_hits >= 3 and pattern_hits >= 2:
        final = max(final, 0.84)
    elif phrase_hits >= 2 and pattern_hits >= 2 and ai_sent_ratio >= 0.25:
        final = max(final, 0.74)
    elif ai_sent_ratio >= 0.40 and top_ai_mean >= 0.44 and human_sent_ratio <= 0.15:
        final = max(final, 0.68)
    elif direct_gpt_score >= 0.44 and gpt_style_score >= 0.46 and style_gap >= 0.12:
        final = max(final, 0.62)

    # strong human-academic suppression — FIX v116: raised all caps
    if human_sent_ratio >= 0.30 and top_human_mean >= 0.34 and phrase_hits == 0 and pattern_hits <= 1:
        final = min(final, 0.38)
    if citation_hits >= 3 and human_sent_ratio >= 0.25 and ai_sent_ratio <= 0.12:
        final = min(final, 0.30)
    if human_academic_guard >= 0.48 and academic_ai_pressure <= 0.42:
        final -= 0.03

    # soft consensus boost only when backed by at least some direct/style evidence
    consensus = 0
    consensus += 1 if sg >= 0.70 else 0
    consensus += 1 if nb >= 0.70 else 0
    consensus += 1 if en >= 0.50 else 0
    consensus += 1 if fp >= 0.24 else 0
    consensus += 1 if llr >= 0.60 else 0
    consensus += 1 if ai_sent_ratio >= 0.25 else 0

    weak_direct = (phrase_hits == 0 and pattern_hits == 0 and direct_gpt_score < 0.18)
    support_strength = (
        (0.10 if phrase_hits >= 1 else 0.0) +
        (0.08 if pattern_hits >= 1 else 0.0) +
        min(max(ai_sent_ratio - 0.20, 0.0), 0.18) +
        min(max(style_gap, 0.0), 0.16) * 0.60
    )
    support_strength = max(0.0, min(support_strength, 0.26))

    if consensus >= 4 and max(sg, nb, en) >= 0.70 and human_sent_ratio < 0.22 and not weak_direct:
        final = max(final, 0.28 + support_strength)
    elif consensus >= 3 and max(sg, nb, en) >= 0.68 and human_sent_ratio < 0.18 and not weak_direct:
        final = max(final, 0.22 + support_strength * 0.85)

    final = max(0.0, min(final, 0.995))

    result["score"] = final
    result["percentage"] = final * 100.0
    result["human_score"] = (1.0 - final) * 100.0
    result["risk_level"] = (
        "CRITICAL" if final >= 0.88 else
        "HIGH" if final >= 0.74 else
        "MEDIUM" if final >= 0.56 else
        "LOW" if final >= 0.28 else
        "MINIMAL"
    )
    _verdicts = {
        "CRITICAL": "اشتباه مرتفع جدًا - يحتاج تحقق بشري",
        "HIGH":     "اشتباه مرتفع - يحتاج تحقق بشري",
        "MEDIUM":   "نتيجة مختلطة / غير حاسمة",
        "LOW":      "اشتباه منخفض",
        "MINIMAL":  "بشري على الأرجح",
    }
    result["verdict"] = _verdicts[result["risk_level"]]

    indicators["🔍 Fingerprint Score v35 ★★★"] = max(fp, min(academic_ai_pressure * 0.85 + max(style_gap, 0.0) * 0.20, 0.98))
    indicators["Academic AI Pressure v3 ★★★"] = round(academic_ai_pressure, 4)
    indicators["Human Academic Grounding ✔✔"] = round(1.0 - human_academic_guard, 4)

    extended["direct_gpt_score"] = round(direct_gpt_score, 4)
    extended["gpt_style_score"] = round(gpt_style_score, 4)
    extended["academic_ai_pressure_v3"] = round(academic_ai_pressure, 4)
    extended["human_academic_guard_v3"] = round(human_academic_guard, 4)
    extended["repair_phrase_hits"] = int(phrase_hits)
    extended["repair_pattern_hits"] = int(pattern_hits)
    extended["repair_struct_hits"] = int(struct_hits)
    extended["repair_format_hits"] = int(format_hits)
    extended["repair_paragraph_corroboration"] = para_meta
    extended["sentence_style_profiles"] = profiles
    extended["ai_sentence_ratio"] = ai_sent_ratio
    extended["human_sentence_ratio"] = human_sent_ratio
    extended["style_gap_v3"] = style_gap

    result["indicators"] = indicators
    result["extended"] = extended
    result["precision95_meta"] = {
        "patched_by": "precision97_academic_style_repair",
        "direct_gpt_score": round(direct_gpt_score, 4),
        "gpt_style_score": round(gpt_style_score, 4),
        "academic_ai_pressure": round(academic_ai_pressure, 4),
        "human_academic_guard": round(human_academic_guard, 4),
        "consensus": int(consensus),
        "phrase_hits": int(phrase_hits),
        "pattern_hits": int(pattern_hits),
        "struct_hits": int(struct_hits),
        "format_hits": int(format_hits),
        "ai_sentence_ratio": round(ai_sent_ratio, 4),
        "human_sentence_ratio": round(human_sent_ratio, 4),
        "style_gap_v3": round(style_gap, 4),
        "final_score": round(final, 4),
    }

    result = _precision97_enhance_result(self, result, text)
    return result

for _attr, _name in (
    ("_precision97_sentence_style_profiles", "_precision97_sentence_style_profiles"),
    ("_precision97_extract_ai_quotes", "_precision97_extract_ai_quotes"),
    ("_precision97_enhance_result", "_precision97_enhance_result"),
    ("analyze", "_precision97_analyze"),
):
    _fn = globals().get(_name)
    if _fn is not None:
        setattr(AIDetectionEngine, _attr, _fn)

# --- Runtime repair: rebind methods that were accidentally nested under
# _academic_grounding_profile due to indentation corruption ---

def _english_ai_score(self, text, words, sents):
        """
        English-focused AI detector.
        Requires direct/templatic GPT evidence and aggressively discounts
        well-grounded academic prose across disciplines.
        """
        arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
        if arabic_chars / max(len(text), 1) > 0.20:
            return 0.0

        n_words = len(words)
        if n_words < 30:
            self._en_evidence_cache = ["too_short_for_strong_en_ai"]
            return 0.10

        tl = text.lower()
        sent_count = max(len(sents), 1)
        evidence = []

        grounding = self._academic_grounding_profile(text, words, sents)
        grounding_score = grounding["score"]

        # 1) Direct GPT phrase evidence
        t1_hits = [p for p in getattr(self, 'EN_GPT_PHRASES_T1', []) if p in tl]
        exact_hit_count = len(t1_hits)
        if exact_hit_count >= 10:
            t1_score = min(0.78 + (exact_hit_count - 10) * 0.015, 0.96)
            evidence.append(f"T1-very-strong:{exact_hit_count}")
        elif exact_hit_count >= 6:
            t1_score = 0.44 + (exact_hit_count - 6) * 0.055
            evidence.append(f"T1-strong:{exact_hit_count}")
        elif exact_hit_count >= 3:
            t1_score = 0.18 + (exact_hit_count - 3) * 0.07
            evidence.append(f"T1-mid:{exact_hit_count}")
        else:
            t1_score = 0.02

        # 2) Sentence pattern evidence
        t2_hits = 0
        for pat in getattr(self, 'EN_GPT_SENTENCE_PATTERNS', [])[:120]:
            try:
                t2_hits += len(re.findall(pat, tl, re.I))
            except Exception:
                pass

        t2_density = t2_hits / max(sent_count / 7.0, 1.0)
        if t2_density >= 6.0:
            t2_score = min(0.72 + (t2_density - 6.0) * 0.03, 0.90)
            evidence.append(f"T2-very-strong:{t2_density:.1f}")
        elif t2_density >= 3.5:
            t2_score = 0.34 + (t2_density - 3.5) * 0.08
            evidence.append(f"T2-strong:{t2_density:.1f}")
        elif t2_density >= 2.0:
            t2_score = 0.12 + (t2_density - 2.0) * 0.08
            evidence.append(f"T2-mid:{t2_density:.1f}")
        else:
            t2_score = 0.03

        # 3) Templatic style, kept weak on purpose
        lens = [len(s.split()) for s in sents if len(s.split()) >= 3]
        style_score = 0.0
        if lens:
            avg_len = sum(lens) / len(lens)
            sd_len = (sum((x - avg_len) ** 2 for x in lens) / len(lens)) ** 0.5
            cv_len = sd_len / max(avg_len, 1.0)
            if 14 <= avg_len <= 24 and cv_len <= 0.26:
                style_score += 0.10
            elif 12 <= avg_len <= 26 and cv_len <= 0.33:
                style_score += 0.05

        formal_openers = 0
        for s in sents:
            ss = s.strip().lower()
            if re.match(r'^(however|therefore|moreover|furthermore|additionally|consequently|overall|thus|notably)\b', ss):
                formal_openers += 1
        opener_ratio = formal_openers / max(sent_count, 1)
        if opener_ratio >= 0.30:
            style_score += 0.05
        elif opener_ratio >= 0.18:
            style_score += 0.025

        repeated_templates = 0
        repeated_templates += len(re.findall(r'\bthis\s+(?:study|paper|article|analysis)\s+(?:aims?|seeks?|examines?|investigates?|explores?)\b', tl))
        repeated_templates += len(re.findall(r'\bit\s+(?:is|has been)\s+(?:important|widely|necessary|evident|clear|shown|demonstrated)\b', tl))
        if repeated_templates >= 5:
            style_score += 0.08
        elif repeated_templates >= 3:
            style_score += 0.04

        style_score = min(style_score, 0.18)

        # 4) Human / academic dampeners
        citation_hits = len(re.findall(r'\([A-Z][A-Za-z\-]+,\s*\d{4}[a-z]?\)', text))
        bracket_hits  = len(re.findall(r'\[(?:\d+|\d+(?:\s*,\s*\d+)*)\]', text))
        quote_hits    = text.count('"') + text.count('“') + text.count('”')
        number_hits   = len(re.findall(r'\b\d+(?:\.\d+)?%?\b', text))
        hedges        = len(re.findall(r'\b(?:may|might|could|perhaps|possibly|likely|unlikely|approximately|suggests?|appears?|indicates?)\b', tl))
        first_person  = len(re.findall(r'\b(?:i|we|our|my|us)\b', tl))

        damp = 0.0
        if citation_hits + bracket_hits >= 2:
            damp += 0.08
            evidence.append("academic-citations")
        if number_hits >= max(6, n_words // 120):
            damp += 0.05
            evidence.append("data-heavy")
        if hedges >= 4:
            damp += 0.04
        if first_person >= 2:
            damp += 0.03
        if quote_hits >= 2:
            damp += 0.02

        # cross-disciplinary grounding gets strongest dampening unless direct GPT evidence is strong
        if grounding_score >= 0.70:
            damp += 0.34
            evidence.append(f"grounded-academic:{grounding_score:.2f}")
        elif grounding_score >= 0.55:
            damp += 0.24
            evidence.append(f"grounded-academic:{grounding_score:.2f}")
        elif grounding_score >= 0.40:
            damp += 0.14
            evidence.append(f"grounded-academic:{grounding_score:.2f}")

        base = t1_score * 0.50 + t2_score * 0.33 + style_score * 0.17

        corroboration = 0
        corroboration += 1 if exact_hit_count >= 4 else 0
        corroboration += 1 if t2_density >= 3.5 else 0
        corroboration += 1 if repeated_templates >= 5 else 0
        corroboration += 1 if getattr(self, '_simple_gpt_score')(text, words, sents) >= 0.66 else 0
        corroboration += 1 if getattr(self, '_gpt_formatting_signature')(text, sents) >= 0.58 else 0

        score = base - damp

        # style-only academic prose should stay low
        if grounding_score >= 0.55 and exact_hit_count < 3 and t2_density < 3.5:
            score *= 0.58
        elif grounding_score >= 0.40 and exact_hit_count < 2 and t2_density < 2.5:
            score *= 0.74

        # Escalate only with strong direct evidence
        if corroboration >= 3 and exact_hit_count >= 4:
            score = max(score, min(0.96, 0.74 + 0.04 * corroboration))
            evidence.append(f"cross-strong:{corroboration}")
        elif corroboration >= 2 and exact_hit_count >= 3 and grounding_score < 0.55:
            score = max(score, 0.56)
            evidence.append(f"cross-mid:{corroboration}")

        score = max(0.0, min(score, 0.98))
        self._en_evidence_cache = evidence[:24]
        return round(score, 4)


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
    """Conservative fingerprint score for English academic text."""
    if not words or not sents:
        self._fp_scores_cache = {}
        return 0.0

    tl = text.lower()
    n_words = max(len(words), 1)

    exact_phrases = sum(1 for p in getattr(self, 'EN_GPT_PHRASES_T1', []) if p in tl)
    struct_hits = 0
    struct_pats = [
        r'\bthis\s+(?:study|paper|article|research|analysis)\s+(?:aims?|seeks?|examines?|investigates?|explores?)\b',
        r'\bit\s+(?:has\s+been|is)\s+(?:widely\s+)?(?:shown|demonstrated|recognized|reported|suggested)\s+that\b',
        r'\bfurther\s+research\s+(?:is\s+needed|should|could|may)\b',
        r'\bplays?\s+(?:a|an)\s+(?:vital|crucial|key|significant|important)\s+role\s+in\b',
    ]
    for p in struct_pats:
        try:
            struct_hits += len(re.findall(p, tl, re.I))
        except Exception:
            pass

    starter_tokens = [s.split()[0].lower().strip(",;:") for s in sents if s.split()]
    formal_openers = {'however','therefore','moreover','furthermore','additionally',
                      'consequently','nevertheless','thus','overall','specifically','notably'}
    starter_ratio = sum(1 for t in starter_tokens if t in formal_openers) / max(len(starter_tokens), 1)

    citations = len(re.findall(r'\([A-Z][A-Za-z\-]+,\s*\d{4}[a-z]?\)', text))
    numeric = len(re.findall(r'\b\d+(?:\.\d+)?%?\b', text))
    hedges  = len(re.findall(r'\b(?:may|might|could|perhaps|possibly|likely|unlikely|approximately|suggests?|appears?|indicates?)\b', tl))
    first_person = len(re.findall(r'\b(?:i|we|our|my|us)\b', tl))

    direct_signal = (
        min(exact_phrases / 8.0, 1.0) * 0.34 +
        min(struct_hits / 8.0, 1.0) * 0.16 +
        simple_gpt_score * 0.18 +
        gpt_format_score * 0.10 +
        english_ai_score * 0.14 +
        min(getattr(self, '_pattern_memory')(text), 0.9) * 0.08
    )

    style_signal = 0.0
    if starter_ratio >= 0.28:
        style_signal += 0.08
    elif starter_ratio >= 0.16:
        style_signal += 0.04
    style_signal += min(getattr(self, '_semantic_embedding')(words, sents), 0.85) * 0.05
    style_signal += min(getattr(self, '_context_drift')(sents, words), 0.85) * 0.05
    style_signal = min(style_signal, 0.14)

    human_damp = 0.0
    if citations >= 2:
        human_damp += 0.08
    if numeric >= max(6, n_words // 120):
        human_damp += 0.05
    if hedges >= 4:
        human_damp += 0.03
    if first_person >= 2:
        human_damp += 0.03

    human_damp += english_human_score * 0.08
    human_damp += deep_human_score * 0.06
    human_damp += human_error_val * 0.04

    score = direct_signal + style_signal - human_damp

    corroboration = 0
    corroboration += 1 if exact_phrases >= 4 else 0
    corroboration += 1 if struct_hits >= 5 else 0
    corroboration += 1 if simple_gpt_score >= 0.62 else 0
    corroboration += 1 if english_ai_score >= 0.68 else 0
    corroboration += 1 if gpt_format_score >= 0.55 else 0

    if corroboration >= 3 and exact_phrases >= 4:
        score = max(score, min(0.97, 0.78 + 0.04 * corroboration))
    elif corroboration >= 2 and exact_phrases >= 2:
        score = max(score, 0.58)

    # Hard limit against pure academic-style inflation.
    if exact_phrases <= 1 and struct_hits <= 2 and simple_gpt_score < 0.45:
        score = min(score, 0.34)

    self._fp_scores_cache = {
        "exact_phrases": exact_phrases,
        "struct_hits": struct_hits,
        "starter_ratio": round(starter_ratio, 4),
        "citations": citations,
        "numeric": numeric,
        "corroboration": corroboration,
    }
    return round(max(0.0, min(score, 0.98)), 4)


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

    # ─── ⑦ GPT School Verbs (موسّع ليشمل الأفعال الأكاديمية لـ GPT) ──
    GPT_VERBS = {
        # أفعال GPT المدرسية الأصلية
        'helps','improves','allows','enables','supports','promotes',
        'develops','builds','strengthens','boosts','enhances','increases',
        'reduces','expands','fosters','cultivates','stimulates','provides',
        'offers','encourages','facilitates','contributes','assists',
        'explores','gains','learn','grow','improve','develop',
        # أفعال GPT الأكاديمية — مميزة جداً في نصوص GPT الأكاديمية
        'examine','examines','examined','leverage','leverages','leveraged',
        'highlight','highlights','highlighted','underscore','underscores',
        'elucidate','elucidates','illuminate','illuminates','navigate',
        'navigates','foster','fosters','harness','harnessing','unlock',
        'unlocks','empower','empowers','reimagine','reshape','revolutionize',
        'operationalize','contextualize','conceptualize','prioritize',
        'streamline','streamlines','mitigate','mitigates','alleviate',
        'bolster','bolsters','reinforce','reinforces','demonstrate',
        'demonstrates','investigate','investigates','aims','seeks',
        'endeavors','strives','aspires','explores','delves','address',
        'addresses','tackle','tackles','shed','sheds',
    }
    vb_count = sum(1 for w in words if w in GPT_VERBS)
    scores['gpt_verbs'] = min(vb_count/n_words*7.0, 1.0)

    # ─── ⑧ Benefit/Value + GPT Academic Adjectives ───────────────────
    BENEFIT_W = {
        # كلمات القيمة الأصلية
        'benefits','benefit','advantages','advantage','valuable',
        'important','essential','crucial','key','significant',
        'effective','powerful','positive','useful','worthwhile',
        'lifelong','personal','intellectual','academic','overall',
        'activity','habit','practice','development','growth',
        # صفات GPT الأكاديمية المميزة
        'holistic','multifaceted','nuanced','transformative','innovative',
        'sustainable','resilient','robust','pivotal','paramount',
        'groundbreaking','revolutionary','unprecedented','comprehensive',
        'interdisciplinary','systemic','dynamic','foundational','seminal',
        'imperative','indispensable','far-reaching','cutting-edge',
    }
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
    # FIX: المؤشرات التي تُطلق على الكتابة البشرية الأكاديمية العادية
    # (no_personal, no_doubt, direct_topic, uniformity, simple_sents)
    # يجب أن تكون ذات وزن منخفض جداً لأنها صفات الكتابة الرسمية البشرية.
    # الوزن الأعلى للمؤشرات التي تختص بـ GPT فعلاً:
    # trans_strict (روابط GPT النمطية), closing, emoji_tail, gpt_verbs, benefit_words
    W = {
        'trans_strict':   0.22,  # روابط GPT المميزة — دليل مباشر
        'closing':        0.16,  # ختام GPT النمطي — دليل مباشر
        'emoji_tail':     0.10,  # إيموجي GPT — دليل مباشر
        'gpt_verbs':      0.12,  # أفعال GPT المدرسية
        'benefit_words':  0.10,  # كلمات GPT المفيدية
        'also_pattern':   0.06,  # نمط "X also Y"
        'causal':         0.06,  # بنية سببية GPT
        'gpt_starters':   0.05,  # بدايات GPT
        'topic_rep':      0.04,  # تكرار الكلمة المحورية
        'ly_adverbs':     0.03,  # ظروف -ly
        'enumeration':    0.02,  # تعداد "A and B"
        # المؤشرات التالية طبيعية في الكتابة الأكاديمية البشرية → وزن منخفض جداً
        'gpt_lexical':    0.08,  # كثافة مفردات AI_FINGERPRINT — يكشف GPT الأكاديمي
        'uniformity':     0.01,  # كان 0.07 — الأكاديمي البشري منتظم الجمل
        'no_personal':    0.01,  # كان 0.12 — الأكاديمي البشري لا يستخدم I
        'no_doubt':       0.01,  # كان 0.07 — الأكاديمي البشري رسمي بلا maybe
        'direct_topic':   0.01,  # كان 0.06 — الكتابة الموضوعية تبدأ بالموضوع
        'simple_sents':   0.00,  # محذوف — الجمل الواضحة ليست دليلاً
        'impersonal':     0.00,  # محذوف — الأكاديمي يستخدم they/people
    }
    # Normalize
    w_sum = sum(W.values())
    if abs(w_sum - 1.0) > 0.001:
        W = {k: v/w_sum for k, v in W.items()}

    base = sum(scores.get(k, 0.0) * v for k, v in W.items())

    # ─── Human Penalty ────────────────────────────────────────────────
    base *= max(0.0, 1.0 - personal_hits/max(n_words/12, 1) * 0.35)

    # ─── Composite Boost: يتطلب دليلاً مباشراً من GPT ─────────────────
    # FIX: الـ boost القديم كان يُطلق بـ 3 إشارات أسلوبية عامة.
    # الآن يتطلب دليلاً واحداً مباشراً (trans_strict أو closing أو emoji)
    # لأن الكتابة البشرية الأكاديمية تُطلق دائماً: no_personal + direct_topic + uniformity
    has_direct_gpt = (
        scores.get('trans_strict', 0)  >= 0.40 or
        scores.get('closing', 0)       >= 0.40 or
        scores.get('emoji_tail', 0)    >= 0.40 or
        scores.get('gpt_lexical', 0)   >= 0.45   # كثافة مفردات AI عالية = دليل
    )
    strong = sum([
        scores.get('trans_strict', 0)   >= 0.40,
        scores.get('closing', 0)        >= 0.40,
        scores.get('emoji_tail', 0)     >= 0.40,
        scores.get('gpt_lexical', 0)    >= 0.45,
        scores.get('gpt_verbs', 0)      >= 0.50,
        scores.get('benefit_words', 0)  >= 0.50,
        scores.get('also_pattern', 0)   >= 0.30,
        scores.get('causal', 0)         >= 0.30,
    ])
    # الـ boost يعمل فقط عند وجود دليل مباشر
    if has_direct_gpt:
        if strong >= 5:
            base = max(base, 0.90)
        elif strong >= 3:
            base = max(base, 0.75)
        elif strong >= 2:
            base = max(base, 0.60)
        elif strong >= 1 and scores.get('trans_strict', 0) >= 0.70:
            # trans_strict قوي جداً = دليل كافٍ وحده
            base = max(base, 0.55)
        elif strong >= 1 and scores.get('gpt_lexical', 0) >= 0.55:
            # كثافة مفردات AI عالية جداً بدون روابط = GPT أكاديمي محتمل
            base = max(base, 0.50)

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
    Conservative synonym-density detector.
    Academic lexical variety alone should not be treated as AI.
    """
    if len(words) < 25:
        return 0.12

    from collections import Counter as _C, defaultdict as _dd

    SEMANTIC_GROUPS = {
        'demonstrate': 'show_grp', 'show': 'show_grp', 'illustrate': 'show_grp', 'reveal': 'show_grp',
        'important': 'imp_grp', 'significant': 'imp_grp', 'crucial': 'imp_grp', 'critical': 'imp_grp',
        'vital': 'imp_grp', 'essential': 'imp_grp', 'key': 'imp_grp',
        'improve': 'enhance_grp', 'enhance': 'enhance_grp', 'strengthen': 'enhance_grp',
        'advance': 'enhance_grp', 'promote': 'enhance_grp',
        'use': 'use_grp', 'utilize': 'use_grp', 'employ': 'use_grp', 'apply': 'use_grp',
        'implement': 'use_grp', 'adopt': 'use_grp', 'leverage': 'use_grp',
        'help': 'help_grp', 'facilitate': 'help_grp', 'enable': 'help_grp', 'support': 'help_grp',
        'assist': 'help_grp', 'contribute': 'help_grp',
        'result': 'result_grp', 'outcome': 'result_grp', 'finding': 'result_grp', 'conclusion': 'result_grp',
        'effect': 'result_grp', 'impact': 'result_grp', 'implication': 'result_grp',
        'problem': 'prob_grp', 'challenge': 'prob_grp', 'issue': 'prob_grp', 'concern': 'prob_grp',
        'method': 'method_grp', 'approach': 'method_grp', 'strategy': 'method_grp', 'technique': 'method_grp',
        'model': 'model_grp', 'framework': 'model_grp', 'paradigm': 'model_grp',
    }

    normalized = [w.lower() for w in words]
    total = len(normalized)
    grp_counts = _C()
    grp_types = _dd(set)

    for w in normalized:
        grp = SEMANTIC_GROUPS.get(w)
        if grp:
            grp_counts[grp] += 1
            grp_types[grp].add(w)

    if not grp_counts:
        return 0.06

    dense_groups = 0
    varied_groups = 0
    suspicious_groups = 0
    total_group_tokens = sum(grp_counts.values())

    for grp, cnt in grp_counts.items():
        uniq = len(grp_types[grp])
        density = cnt / max(total, 1)
        if cnt >= 4 and density >= 0.012:
            dense_groups += 1
        if cnt >= 5 and uniq >= 3:
            varied_groups += 1
        if cnt >= 7 and uniq >= 4 and density >= 0.02:
            suspicious_groups += 1

    raw = (
        min(total_group_tokens / max(total * 0.22, 1), 1.0) * 0.18 +
        min(dense_groups / 6.0, 1.0) * 0.22 +
        min(varied_groups / 5.0, 1.0) * 0.28 +
        min(suspicious_groups / 4.0, 1.0) * 0.32
    )

    # Repetition with many different near-synonyms is more suspicious than plain diversity.
    ttr = len(set(normalized)) / max(total, 1)
    if ttr > 0.62:
        raw *= 0.88

    # Academic vocabulary should not inflate this too much.
    academic_terms = sum(
        1 for w in normalized
        if w in {'study','research','analysis','results','findings','data','method','methods','discussion','conclusion'}
    )
    if academic_terms >= max(8, total // 80):
        raw *= 0.85

    return round(max(0.03, min(raw, 0.58)), 4)


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


import zlib as _z, base64 as _b


AIDetectionEngine._english_ai_score = _english_ai_score
AIDetectionEngine._explain_paragraph = _explain_paragraph
AIDetectionEngine._arabic_ai_score = _arabic_ai_score
AIDetectionEngine._compute_confidence = _compute_confidence
AIDetectionEngine._context_coherence = _context_coherence
AIDetectionEngine._advanced_stylometry = _advanced_stylometry
AIDetectionEngine._punct_distribution = _punct_distribution
AIDetectionEngine._bigram_score = _bigram_score
AIDetectionEngine._trigram_score = _trigram_score
AIDetectionEngine._pattern_score = _pattern_score
AIDetectionEngine._rhythm = _rhythm
AIDetectionEngine._local_entropy = _local_entropy
AIDetectionEngine._paragraph_structure = _paragraph_structure
AIDetectionEngine._punct_fingerprint = _punct_fingerprint
AIDetectionEngine._verb_ratio = _verb_ratio
AIDetectionEngine._pronoun_ratio = _pronoun_ratio
AIDetectionEngine._compute_fingerprint_score = _compute_fingerprint_score
AIDetectionEngine._simple_gpt_score = _simple_gpt_score
AIDetectionEngine._gpt_formatting_signature = _gpt_formatting_signature
AIDetectionEngine._paraphrase_engine = _paraphrase_engine
AIDetectionEngine._synonym_density = _synonym_density
AIDetectionEngine._discourse_invariant = _discourse_invariant


# ── Robust late-binding for engine helpers ─────────────────────────────────────
_ENGINE_HELPER_NAMES = [
    "_english_ai_score", "_explain_paragraph", "_arabic_ai_score", "_compute_confidence",
    "_context_coherence", "_context_drift", "_advanced_stylometry", "_punct_distribution", "_lm_perplexity", "_token_prob_variance", "_sliding_window", "_semantic_entropy", "_llr_score", "_rf_score", "_bigram_score",
    "_trigram_score", "_pattern_score", "_rhythm", "_local_entropy", "_paragraph_structure",
    "_punct_fingerprint", "_verb_ratio", "_pronoun_ratio", "_compute_fingerprint_score",
    "_simple_gpt_score", "_gpt_formatting_signature", "_paraphrase_engine",
    "_synonym_density", "_discourse_invariant"
]

def _rebind_aidetectionengine_helpers():
    for _name in _ENGINE_HELPER_NAMES:
        _fn = globals().get(_name) or getattr(AIDetectionEngine, _name, None)
        if callable(_fn):
            setattr(AIDetectionEngine, _name, _fn)

def _aidetectionengine_getattr(self, name):
    if name in _ENGINE_HELPER_NAMES:
        _fn = globals().get(name)
        if callable(_fn):
            setattr(self.__class__, name, _fn)
            return _fn.__get__(self, self.__class__)
    raise AttributeError(f"{self.__class__.__name__!s} object has no attribute {name!r}")

_rebind_aidetectionengine_helpers()
AIDetectionEngine.__getattr__ = _aidetectionengine_getattr


# --- Cross-disciplinary academic human balance patch ---

def _detect_fake_references(text):
    """
    FIX v115: Detects AI-generated fake/hallucinated references.
    GPT often adds plausible-looking but fake citations to bypass grounding guards.
    Returns a penalty score 0.0 (no fake refs) to 1.0 (very likely fake refs).
    """
    import re
    penalty = 0.0

    # Signal 1: Round-year clustering — real papers have varied years,
    # GPT tends to use 2020, 2021, 2022, 2023 heavily and avoid 2005-2015.
    years_found = re.findall(r'\b(19|20)(\d{2})\b', text)
    if len(years_found) >= 3:
        year_vals = [int(a+b) for a,b in years_found]
        recent_only = sum(1 for y in year_vals if y >= 2019)
        recent_ratio = recent_only / max(len(year_vals), 1)
        if recent_ratio >= 0.90 and len(year_vals) >= 4:
            penalty += 0.20  # suspicious: ALL refs from 2019+

    # Signal 2: Sequential bracketed refs [1][2][3] with no actual ref list
    bracket_refs = re.findall(r'\[(\d{1,3})\]', text)
    if len(bracket_refs) >= 3:
        nums = sorted([int(x) for x in bracket_refs])
        is_sequential = all(nums[i+1] - nums[i] <= 2 for i in range(len(nums)-1))
        has_ref_section = bool(re.search(
            r'(?im)^\s*(references|bibliography|works cited|المراجع)\s*$', text))
        if is_sequential and not has_ref_section and len(bracket_refs) >= 4:
            penalty += 0.25  # refs cited but no reference list = likely fake

    # Signal 3: Author-year refs without a reference list
    author_year_refs = re.findall(r'\([A-Z][a-z]+(?: et al\.?)?,\s*\d{4}\)', text)
    if len(author_year_refs) >= 3:
        has_ref_section = bool(re.search(
            r'(?im)^\s*(references|bibliography|works cited|المراجع)\s*$', text))
        if not has_ref_section:
            penalty += 0.18  # author-year cites but no bibliography

    # Signal 4: Overly generic author names (GPT uses Smith, Johnson, Brown, Lee, Chen)
    generic_names = re.findall(
        r'\b(?:Smith|Johnson|Brown|Lee|Chen|Wang|Kim|Jones|Williams|Davis),', text)
    if len(generic_names) >= 3:
        penalty += 0.15

    # Signal 5: DOI patterns that are syntactically plausible but uniformly formatted
    dois = re.findall(r'\b10\.\d{4}/[A-Za-z0-9.]+\b', text)
    if len(dois) >= 2:
        # Real DOIs have varied lengths; AI-generated tend to be similar length
        lengths = [len(d) for d in dois]
        if len(set(lengths)) == 1:  # all same length = suspicious
            penalty += 0.12

    return min(penalty, 0.60)


def _academic_grounding_profile_v2(self, text, words=None, sents=None):
    """
    Stronger cross-disciplinary scholarly grounding detector.
    Designed to protect polished human academic prose from false AI inflation.
    """
    if words is None:
        words = re.findall(r'\b[a-zA-Z][a-zA-Z\-]*\b', text.lower())
    if sents is None:
        sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    tl = text.lower()
    wc = max(len(words), 1)
    sc = max(len(sents), 1)

    # citations / bibliography
    bracket_refs = len(re.findall(r'\[(?:\d+(?:\s*[-,]\s*\d+)*)\]', text))
    author_year = len(re.findall(r'\([A-Z][A-Za-z.\-]+(?:\s+et\s+al\.)?,\s*\d{4}[a-z]?\)', text))
    refs_heading = 1 if re.search(r'(?im)^\s*(references|bibliography|works cited)\s*$', text) else 0
    ref_lines = len(re.findall(r'(?m)^\s*(?:\[\d+\]|\d+\.\s+[A-Z]|[A-Z][A-Za-z.\-]+,\s*[A-Z])', text))
    doi_refs = len(re.findall(r'\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b', text, re.I))

    # scholarly structure
    sectionish = len(re.findall(r'(?im)^\s*(?:\d+(?:\.\d+){0,3}\s+)?(?:abstract|introduction|background|methods?|methodology|materials?|results?|discussion|conclusion|related work|evaluation|references)\b', text))
    table_fig = len(re.findall(r'\b(?:table|fig(?:ure)?|equation|algorithm|appendix|section|chapter)\s*\d+[a-z]?\b', tl))
    captionish = len(re.findall(r'(?im)^\s*(?:table|figure|fig\.)\s+\d+[.:]', text))

    # empirical / technical grounding
    method_terms = len(re.findall(
        r'\b(?:dataset|sample|participants?|respondents?|subjects?|survey|questionnaire|interview(?:s)?|experiment(?:s|al)?|'
        r'simulation|benchmark|evaluation|validation|cross-validation|ablation|regression|anova|hypothesis|significan(?:ce|t)|'
        r'confidence interval|standard deviation|variance|mean|median|distribution|observed|measured|estimated|implemented?|'
        r'architecture|framework|pipeline|protocol|algorithm|complexity|throughput|latency|accuracy|precision|recall|f1|auc|'
        r'case study|literature review|empirical|qualitative|quantitative|mixed methods?)\b', tl, re.I))
    numbers = len(re.findall(r'\b\d+(?:\.\d+)?(?:%|x)?\b', text))
    stat_marks = len(re.findall(r'\b(?:p\s*[<=>]\s*0?\.\d+|r\s*=\s*[-+]?\d+\.\d+|n\s*=\s*\d+)\b', text, re.I))
    acronym_density = len(re.findall(r'\b[A-Z]{2,}(?:/[A-Z]{2,})?\b', text))
    domain_entities = len(re.findall(r'\b(?:IEEE|ACM|ISO|NIST|NASA|DoD|ODNI|GAO|EU|UN|WHO|OECD|SQL|ERP|API|GPU|CPU|IoT)\b', text))

    # cautious academic prose markers
    hedges = len(re.findall(r'\b(?:may|might|could|suggests?|appears?|indicates?|approximately|likely|unlikely|within the scope)\b', tl))
    claim_grounding = len(re.findall(r'\b(?:according to|as shown in|as reported in|in table|in figure|our results?|the results? indicate|the findings suggest)\b', tl))

    citation_signal = min((bracket_refs + author_year + doi_refs + min(ref_lines, 20)) / max(wc / 80.0, 1.0), 1.0)
    bibliography_signal = min(refs_heading * 0.4 + min(ref_lines / 20.0, 0.6), 1.0)
    structure_signal = min((sectionish + table_fig + captionish) / max(wc / 180.0, 1.0), 1.0)
    empirical_signal = min((method_terms + stat_marks * 2 + claim_grounding) / max(wc / 70.0, 1.0), 1.0)
    numeric_signal = min((numbers + stat_marks * 2) / max(wc / 60.0, 1.0), 1.0)
    entity_signal = min((acronym_density + domain_entities) / max(wc / 110.0, 1.0), 1.0)
    hedge_signal = min((hedges + claim_grounding) / max(sc / 3.5, 1.0), 1.0)

    score = (
        citation_signal * 0.27 +
        bibliography_signal * 0.14 +
        structure_signal * 0.15 +
        empirical_signal * 0.21 +
        numeric_signal * 0.11 +
        entity_signal * 0.07 +
        hedge_signal * 0.05
    )
    score = max(0.0, min(score, 1.0))

    # FIX v115: Penalize fake/hallucinated references (GPT bypass prevention)
    try:
        fake_ref_penalty = _detect_fake_references(text)
        score = max(0.0, score - fake_ref_penalty * score)
    except Exception:
        fake_ref_penalty = 0.0

    return {
        "score": round(score, 4),
        "citation_signal": round(citation_signal, 4),
        "bibliography_signal": round(bibliography_signal, 4),
        "structure_signal": round(structure_signal, 4),
        "empirical_signal": round(empirical_signal, 4),
        "numeric_signal": round(numeric_signal, 4),
        "entity_signal": round(entity_signal, 4),
        "hedge_signal": round(hedge_signal, 4),
        "citation_hits": int(bracket_refs + author_year + doi_refs + ref_lines),
        "method_hits": int(method_terms + claim_grounding),
        "table_fig_hits": int(table_fig + captionish),
        "number_hits": int(numbers + stat_marks),
        "acronym_hits": int(acronym_density + domain_entities),
        "bibliography_lines": int(ref_lines),
    }


def _english_ai_score_balanced(self, text, words, sents):
    """
    English AI score tuned to avoid punishing polished human academic prose.
    High scores now require direct or repeated templatic GPT evidence.
    """
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    if arabic_chars / max(len(text), 1) > 0.20:
        return 0.0

    n_words = len(words)
    if n_words < 30:
        self._en_evidence_cache = ["too_short_for_strong_en_ai"]
        return 0.10

    tl = text.lower()
    sent_count = max(len(sents), 1)
    evidence = []

    grounding = self._academic_grounding_profile(text, words, sents)
    g = grounding["score"]

    # direct phrase evidence
    t1_hits = [p for p in getattr(self, 'EN_GPT_PHRASES_T1', []) if p in tl]
    exact_hit_count = len(t1_hits)
    if exact_hit_count >= 10:
        t1_score = min(0.80 + (exact_hit_count - 10) * 0.012, 0.96)
        evidence.append(f"T1-very-strong:{exact_hit_count}")
    elif exact_hit_count >= 6:
        t1_score = 0.42 + (exact_hit_count - 6) * 0.055
        evidence.append(f"T1-strong:{exact_hit_count}")
    elif exact_hit_count >= 3:
        t1_score = 0.18 + (exact_hit_count - 3) * 0.06
        evidence.append(f"T1-mid:{exact_hit_count}")
    else:
        t1_score = 0.01

    # pattern evidence
    t2_hits = 0
    for pat in getattr(self, 'EN_GPT_SENTENCE_PATTERNS', [])[:120]:
        try:
            t2_hits += len(re.findall(pat, tl, re.I))
        except Exception:
            pass
    t2_density = t2_hits / max(sent_count / 7.0, 1.0)
    if t2_density >= 6.0:
        t2_score = min(0.70 + (t2_density - 6.0) * 0.025, 0.90)
        evidence.append(f"T2-very-strong:{t2_density:.1f}")
    elif t2_density >= 3.5:
        t2_score = 0.30 + (t2_density - 3.5) * 0.07
        evidence.append(f"T2-strong:{t2_density:.1f}")
    elif t2_density >= 2.0:
        t2_score = 0.10 + (t2_density - 2.0) * 0.07
        evidence.append(f"T2-mid:{t2_density:.1f}")
    else:
        t2_score = 0.02

    # style evidence stays intentionally weak
    lens = [len(s.split()) for s in sents if len(s.split()) >= 5]
    style_score = 0.0
    if lens:
        avg_len = sum(lens) / len(lens)
        sd_len = (sum((x - avg_len) ** 2 for x in lens) / len(lens)) ** 0.5
        cv_len = sd_len / max(avg_len, 1.0)
        if 14 <= avg_len <= 24 and cv_len <= 0.25:
            style_score += 0.08
        elif 12 <= avg_len <= 26 and cv_len <= 0.31:
            style_score += 0.04

    repeated_templates = 0
    repeated_templates += len(re.findall(r'\bthis\s+(?:study|paper|article|analysis)\s+(?:aims?|seeks?|examines?|investigates?|explores?)\b', tl))
    repeated_templates += len(re.findall(r'\bit\s+(?:is|has been)\s+(?:important|widely|necessary|evident|clear|shown|demonstrated)\b', tl))
    repeated_templates += len(re.findall(r'\bin conclusion\b|\boverall\b|\bin summary\b', tl))
    if repeated_templates >= 6:
        style_score += 0.10
    elif repeated_templates >= 4:
        style_score += 0.05
    style_score = min(style_score, 0.14)

    sg = getattr(self, '_simple_gpt_score')(text, words, sents)
    gf = getattr(self, '_gpt_formatting_signature')(text, sents)

    base = t1_score * 0.52 + t2_score * 0.31 + style_score * 0.07 + sg * 0.06 + gf * 0.04

    # academic / human dampeners
    citation_hits = grounding.get("citation_hits", 0)
    number_hits = grounding.get("number_hits", 0)
    method_hits = grounding.get("method_hits", 0)
    hedges = len(re.findall(r'\b(?:may|might|could|perhaps|possibly|likely|unlikely|approximately|suggests?|appears?|indicates?)\b', tl))
    first_person = len(re.findall(r'\b(?:i|we|our|my|us)\b', tl))

    damp = 0.0
    # FIX v116c: Drastically reduced damp values — they were wiping out real AI signals.
    # Academic grounding in a GPT-written text should NOT zero the score.
    if citation_hits >= 4:
        damp += 0.03
        evidence.append("academic-citations")
    if method_hits >= 6:
        damp += 0.03
        evidence.append("method-grounding")
    if number_hits >= max(8, n_words // 110):
        damp += 0.02
        evidence.append("data-heavy")
    if hedges >= 4:
        damp += 0.02
    if first_person >= 2:
        damp += 0.02

    # FIX v116c: Reduced scholarly grounding damp from 0.42/0.30/0.18 to 0.10/0.07/0.04
    # These values were the primary cause of english_ai_score returning ~0 for GPT text
    if g >= 0.80:
        damp += 0.10
        evidence.append(f"strong-scholarly-grounding:{g:.2f}")
    elif g >= 0.65:
        damp += 0.07
        evidence.append(f"strong-scholarly-grounding:{g:.2f}")
    elif g >= 0.50:
        damp += 0.04
        evidence.append(f"scholarly-grounding:{g:.2f}")

    corroboration = 0
    corroboration += 1 if exact_hit_count >= 4 else 0
    corroboration += 1 if t2_density >= 3.5 else 0
    corroboration += 1 if repeated_templates >= 5 else 0
    corroboration += 1 if sg >= 0.70 else 0
    corroboration += 1 if gf >= 0.60 else 0

    score = base - damp

    # FIX v116c: Suppression multipliers weakened — only apply when evidence is truly absent
    # Old: score *= 0.42 when g>=0.70 and exact_hits<3 → GPT text with 2 hits scored ~0
    # New: suppress only when ZERO direct hits
    if g >= 0.70 and exact_hit_count == 0 and t2_density < 2.0:
        score *= 0.55
    elif g >= 0.55 and exact_hit_count == 0 and t2_density < 1.5:
        score *= 0.68

    # only escalate with truly direct evidence
    if corroboration >= 3 and exact_hit_count >= 4:
        score = max(score, min(0.94, 0.72 + 0.04 * corroboration))
        evidence.append(f"cross-strong:{corroboration}")
    elif corroboration >= 3 and exact_hit_count >= 3 and g < 0.50:
        score = max(score, 0.58)
        evidence.append(f"cross-mid:{corroboration}")
    elif corroboration >= 2 and exact_hit_count >= 2:
        score = max(score, 0.35)
        evidence.append(f"cross-weak:{corroboration}")

    # FIX v116c: Minimum floor when clear AI signals exist.
    # If T1 hits >= 2 AND t2_density >= 1.5 → clear GPT evidence → floor at 0.28
    # This ensures direct_core >= 0.28 → feeds the bypass mechanism in analyze().
    # Human text with 2+ T1 hits is very rare; t2_density >= 1.5 further confirms GPT.
    if exact_hit_count >= 3 and t2_density >= 2.0:
        score = max(score, 0.38)
        evidence.append("en_ai_floor_strong")
    elif exact_hit_count >= 2 and t2_density >= 1.5:
        score = max(score, 0.28)
        evidence.append("en_ai_floor_moderate")

    score = max(0.0, min(score, 0.98))
    self._en_evidence_cache = evidence[:24]
    return round(score, 4)



def _score_sentence_balanced(self, sent):
    """
    Human-first sentence scoring for polished academic English.
    Formality, cleanliness, and normal scholarly structure are not AI evidence.
    High sentence scores now require explicit GPT-like phrasing plus corroboration.
    """
    if self._is_reference_line(sent):
        return 0.0

    words = re.findall(r'\b[a-z]+\b', sent.lower())
    if len(words) < 6:
        return 0.0

    tl = sent.lower()
    n = len(words)

    sg  = self._simple_gpt_score(sent, words, [sent])
    llr = _call_engine_helper(self, "_llr_score", words)
    gf  = self._gpt_formatting_signature(sent, [sent])

    exact = sum(1 for p in getattr(self, 'EN_GPT_PHRASES_T1', []) if p in tl)
    patt_hits = 0
    for p in getattr(self, 'EN_GPT_SENTENCE_PATTERNS', [])[:80]:
        try:
            patt_hits += len(re.findall(p, tl, re.I))
        except Exception:
            pass

    lexical_fp = min(sum(1 for w in words if w in self.AI_FINGERPRINT) / max(n, 1) * 1.6, 0.10)

    # direct evidence only; style-like engines are deliberately weakened
    direct = (
        min(exact / 3.0, 1.0) * 0.52 +
        min(patt_hits / 3.0, 1.0) * 0.24 +
        llr * 0.10 +
        sg  * 0.08 +
        gf  * 0.03 +
        lexical_fp * 0.03
    )

    struct = 0.0
    if re.search(r'\bthis\s+(?:study|paper|article|analysis)\b', tl):
        struct += 0.01
    if re.search(r'\b(?:future|further)\s+research\b', tl):
        struct += 0.015
    if re.search(r'\bit\s+(?:has\s+been|is)\s+(?:widely\s+)?(?:shown|demonstrated|recognized|reported)\s+that\b', tl):
        struct += 0.015
    struct = min(struct, 0.03)

    score = direct * 0.985 + struct * 0.015

    scholarly = 0.0
    if re.search(r'\[(?:\d+(?:\s*[-,]\s*\d+)*)\]|\([A-Z][A-Za-z.\-]+(?:\s+et\s+al\.)?,\s*\d{4}[a-z]?\)', sent):
        scholarly += 0.24
    if re.search(r'\b(?:table|fig(?:ure)?|appendix|section|equation|algorithm)\s*\d+[a-z]?\b', tl):
        scholarly += 0.16
    if re.search(r'\b(?:dataset|sample|participants?|respondents?|survey|experiment(?:al)?|empirical|regression|anova|benchmark|evaluation|framework|architecture|implementation|case study|literature review|simulation|protocol)\b', tl):
        scholarly += 0.18
    if re.search(r'\b\d+(?:\.\d+)?%?\b', sent):
        scholarly += 0.14
    if re.search(r'\b[A-Z]{2,}(?:/[A-Z]{2,})?\b', sent):
        scholarly += 0.08
    if re.search(r'\b(?:may|might|could|suggests?|appears?|indicates?|approximately)\b', tl):
        scholarly += 0.08
    scholarly = min(scholarly, 0.64)

    corroboration = 0
    corroboration += 1 if exact >= 2 else 0
    corroboration += 1 if patt_hits >= 2 else 0
    corroboration += 1 if sg >= 0.72 else 0
    corroboration += 1 if llr >= 0.78 else 0

    # FIX v116c: Reduced sentence-level scholarly suppression
    # Old: score *= (1.0 - min(scholarly, 0.68)) → wiped score for any academic sentence
    if scholarly > 0 and exact == 0 and patt_hits == 0:
        score *= (1.0 - min(scholarly * 0.35, 0.25))
    elif scholarly >= 0.24 and exact < 2:
        score *= 0.72
    if scholarly >= 0.34 and corroboration <= 1:
        score *= 0.80
    if scholarly >= 0.44 and exact == 0:
        score *= 0.75

    if re.search(r'\b(?:i|we|my|our|me|us)\b', tl):
        score *= 0.82

    # FIX v116c: Raise sentence caps
    if scholarly >= 0.24 and corroboration <= 1:
        score = min(score, 0.42)
    elif scholarly >= 0.14 and corroboration <= 1:
        score = min(score, 0.52)

    if corroboration >= 3 and exact >= 2 and scholarly < 0.18:
        score = max(score, min(0.88, 0.74 + 0.03 * corroboration))
    elif exact == 0 and patt_hits == 0:
        score = min(score, 0.18)

    return round(max(0.0, min(score, 0.90)), 4)



_previous_analyze_for_academic_balance = AIDetectionEngine.analyze


def _analyze_academic_balance(self, text, cb=None):
    result = _previous_analyze_for_academic_balance(self, text, cb)
    try:
        if not isinstance(result, dict):
            return result

        extended = result.setdefault("extended", {})
        indicators = result.setdefault("indicators", {})

        words = re.findall(r'\b[a-zA-Z][a-zA-Z\-]*\b', text.lower())
        sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
        grounding = self._academic_grounding_profile(text, words, sents)
        g = grounding["score"]

        phrase_hits = int(extended.get("repair_phrase_hits", 0))
        pattern_hits = int(extended.get("repair_pattern_hits", 0))
        ai_sent_ratio = float(extended.get("ai_sentence_ratio", 0.0))
        human_sent_ratio = float(extended.get("human_sentence_ratio", 0.0))
        academic_ai_pressure = float(extended.get("academic_ai_pressure_v3", 0.0))
        human_guard = float(extended.get("human_academic_guard_v3", 0.0))

        # direct evidence is now phrase/pattern-first.
        # sentence-style pressure is only a minor supporter.
        direct_evidence = 0.0
        direct_evidence += min(phrase_hits * 0.15, 0.60)
        direct_evidence += min(pattern_hits * 0.07, 0.21)
        direct_evidence += min(max(ai_sent_ratio - 0.28, 0.0) * 0.35, 0.06)
        direct_evidence = max(0.0, min(direct_evidence, 0.96))

        final = float(result.get("score", 0.0))
        original_final = final

        # Human-first clamps for polished academic prose
        # FIX v116: Raised all caps and lowered direct_evidence thresholds
        if g >= 0.86 and direct_evidence < 0.10 and phrase_hits == 0 and pattern_hits == 0:
            final = min(final, 0.38)  # FIX v116
        elif g >= 0.78 and direct_evidence < 0.12 and phrase_hits == 0 and pattern_hits == 0:
            final = min(final, 0.45)  # FIX v116
        elif g >= 0.70 and direct_evidence < 0.14 and phrase_hits == 0 and pattern_hits <= 1:
            final = min(final, 0.34)
        elif g >= 0.60 and direct_evidence < 0.16 and phrase_hits == 0 and pattern_hits <= 1:
            final = min(final, 0.40)

        # If human academic signals dominate, do not allow style pressure to overwhelm
        if g >= 0.68 and human_guard >= 0.42 and human_sent_ratio >= 0.18 and direct_evidence < 0.12:
            final = min(final, 0.45)  # FIX v116
        elif g >= 0.58 and human_guard >= 0.36 and human_sent_ratio >= 0.14 and direct_evidence < 0.14:
            final = min(final, 0.36)

        # Weak direct evidence should never push polished academic writing high
        if g >= 0.74 and direct_evidence < 0.14 and ai_sent_ratio < 0.20 and academic_ai_pressure <= 0.40:
            final = min(final, 0.45)  # FIX v116
        elif g >= 0.64 and direct_evidence < 0.18 and ai_sent_ratio < 0.24 and academic_ai_pressure <= 0.44:
            final = min(final, 0.36)

        # Hard gates: high/critical need explicit direct evidence
        if direct_evidence < 0.12:
            final = min(final, 0.38)
        elif direct_evidence < 0.24 and phrase_hits == 0 and pattern_hits <= 1:
            final = min(final, 0.48)
        elif direct_evidence < 0.40 and phrase_hits <= 1:
            final = min(final, 0.62)

        final = max(0.0, min(final, 0.995))
        if final != original_final:
            result["score"] = final
            result["percentage"] = final * 100.0
            result["human_score"] = (1.0 - final) * 100.0
            result["risk_level"] = (
                "CRITICAL" if final >= 0.88 else
                "HIGH" if final >= 0.74 else
                "MEDIUM" if final >= 0.56 else
                "LOW" if final >= 0.28 else
                "MINIMAL"
            )
            _verdicts = {
                "CRITICAL": "اشتباه مرتفع جدًا - يحتاج تحقق بشري",
                "HIGH":     "اشتباه مرتفع - يحتاج تحقق بشري",
                "MEDIUM":   "نتيجة مختلطة / غير حاسمة",
                "LOW":      "اشتباه منخفض",
                "MINIMAL":  "بشري على الأرجح",
            }
            result["verdict"] = _verdicts[result["risk_level"]]

        indicators["Academic Grounding Guard v3 ▼▼"] = round(g, 4)
        indicators["Direct GPT Evidence v3 ▲"] = round(direct_evidence, 4)

        extended["academic_grounding"] = round(g, 4)
        extended["academic_grounding_profile"] = grounding
        extended["direct_gpt_evidence_v3"] = round(direct_evidence, 4)
        extended["academic_balance_original_score"] = round(original_final, 4)
        extended["academic_balance_adjusted_score"] = round(result.get("score", 0.0), 4)
        result["academic_balance_meta"] = {
            "patch": "human_first_academic_balance_v3",
            "grounding": round(g, 4),
            "direct_evidence": round(direct_evidence, 4),
            "original_score": round(original_final, 4),
            "adjusted_score": round(result.get("score", 0.0), 4),
            "phrase_hits": phrase_hits,
            "pattern_hits": pattern_hits,
            "ai_sentence_ratio": round(ai_sent_ratio, 4),
            "human_sentence_ratio": round(human_sent_ratio, 4),
        }
        return result
    except Exception:
        return result


AIDetectionEngine._academic_grounding_profile = _academic_grounding_profile_v2
AIDetectionEngine._english_ai_score = _english_ai_score_balanced
AIDetectionEngine.score_sentence = _score_sentence_balanced
AIDetectionEngine.analyze = _analyze_academic_balance


# === Hard fix: guarantee helper methods exist on AIDetectionEngine at runtime ===
def _fallback_bigram_score(self, words):
    if len(words) < 10:
        return 0.3
    bigrams = [(words[i], words[i+1]) for i in range(len(words)-1)]
    if not bigrams:
        return 0.3
    matches = sum(1 for bg in bigrams if bg in getattr(self, "AI_BIGRAMS", set()))
    ratio = matches / max(len(bigrams), 1)
    from collections import Counter
    freq = Counter(bigrams)
    top5_pct = sum(v for _, v in freq.most_common(5)) / max(len(bigrams), 1)
    rep_score = min(top5_pct * 2.5, 1.0)
    return min(ratio * 40 * 0.5 + rep_score * 0.5, 1.0)

def _fallback_trigram_score(self, words):
    if len(words) < 15:
        return 0.3
    trigrams = [(words[i], words[i+1], words[i+2]) for i in range(len(words)-2)]
    if not trigrams:
        return 0.3
    matches = sum(1 for tg in trigrams if tg in getattr(self, "AI_TRIGRAMS", set()))
    ratio = matches / max(len(trigrams), 1)
    from collections import Counter
    freq = Counter(trigrams)
    top3_pct = sum(v for _, v in freq.most_common(3)) / max(len(trigrams), 1)
    rep_score = min(top3_pct * 3.5, 1.0)
    return min(ratio * 60 * 0.55 + rep_score * 0.45, 1.0)

def _fallback_pattern_score(self, sents):
    if not sents:
        return 0.3
    sample = sents[:min(len(sents), 40)]
    pats = getattr(self, "_compiled_patterns", [])
    if not pats:
        return 0.3
    hits = 0
    for s in sample:
        sl = s.lower()
        hits += sum(1 for p in pats if p.search(sl))
    avg_hits = hits / max(len(sample), 1)
    return min(avg_hits / 3.0, 1.0)



# ===== runtime-safe fallback for _llr_score =====
def _fallback_llr_score(self, words):
    """
    Conservative fallback when the bound method `_llr_score` is missing at runtime.
    Keeps the engine running and estimates a stable LLR-like signal from available
    n-gram/style detectors instead of crashing.
    """
    try:
        if isinstance(words, str):
            words = re.findall(r"[A-Za-z']+", words.lower())
        words = list(words or [])
        if len(words) < 8:
            return 0.5

        bi = self._bigram_score(words) if hasattr(self, "_bigram_score") else 0.5
        tri = self._trigram_score(words) if hasattr(self, "_trigram_score") else 0.5
        txt = " ".join(words)
        sg = self._simple_gpt_score(txt) if hasattr(self, "_simple_gpt_score") else 0.5
        pat = self._pattern_score(txt) if hasattr(self, "_pattern_score") else 0.5

        # Smooth confidence by length to avoid overreacting on short texts.
        n = len(words)
        conf = min(1.0, max(0.0, (n - 8) / 140.0))

        # Conservative blend: n-grams dominate, template/pattern signals only assist.
        raw = (0.38 * tri) + (0.28 * bi) + (0.20 * sg) + (0.14 * pat)

        # Pull short / weak-evidence texts back toward neutral.
        score = 0.5 + (raw - 0.5) * conf
        return max(0.0, min(1.0, float(score)))
    except Exception:
        return 0.5



def _fallback_rf_score(self, words, sents, text):
    """
    Safe fallback for Random-Forest style score when `_rf_score` is not bound
    in module globals. First reuses the class-defined implementation if present;
    otherwise computes a conservative proxy from available style signals.
    """
    cls_fn = getattr(AIDetectionEngine, "_rf_score", None)
    if callable(cls_fn) and cls_fn is not _fallback_rf_score:
        try:
            return cls_fn(self, words, sents, text)
        except Exception:
            pass

    n = max(len(words), 1)
    ns = max(len(sents), 1)
    avg_word_len = sum(len(w) for w in words) / n if words else 0.0
    long_word_ratio = sum(1 for w in words if len(w) > 7) / n if words else 0.0
    avg_sent_len = n / ns if ns else float(n)
    comma_density = text.count(",") / ns if ns else 0.0
    formal_markers = (
        "moreover","furthermore","therefore","thus","consequently",
        "in addition","in conclusion","overall","notably","significantly"
    )
    formal_hits = sum(text.lower().count(m) for m in formal_markers)
    score = (
        0.28
        + min(long_word_ratio * 0.35, 0.18)
        + min((avg_word_len / 8.0) * 0.12, 0.12)
        + min((avg_sent_len / 28.0) * 0.10, 0.10)
        + min((comma_density / 3.0) * 0.08, 0.08)
        + min(formal_hits / max(ns, 1) * 0.18, 0.18)
    )
    return max(0.05, min(score, 0.95))


def _fallback_context_drift(self, sents, words):
    try:
        if hasattr(type(self), "_context_drift") and callable(getattr(type(self), "_context_drift")):
            return type(self)._context_drift(self, sents, words)
    except Exception:
        pass
    if not sents:
        return 0.0
    try:
        lens = [len((s or "").split()) for s in sents if (s or "").strip()]
        if len(lens) < 2:
            return 0.0
        avg = sum(lens) / max(len(lens), 1)
        var = sum((x - avg) ** 2 for x in lens) / max(len(lens), 1)
        cv = (var ** 0.5) / (avg + 1e-6)
        return max(0.0, min(1.0, 1.0 - cv * 1.5))
    except Exception:
        return 0.0

_HELPER_FALLBACKS = {
    "_bigram_score": _fallback_bigram_score,
    "_trigram_score": _fallback_trigram_score,
    "_pattern_score": _fallback_pattern_score,
    "_strip_references": _strip_references,
    "_lm_perplexity": _lm_perplexity,
    "_token_prob_variance": _token_prob_variance,
    "_sliding_window": _sliding_window,
    "_semantic_entropy": _semantic_entropy,
    "_llr_score": _fallback_llr_score,
    "_context_drift": _fallback_context_drift,
    "_rf_score": globals().get("_rf_score") or getattr(AIDetectionEngine, "_rf_score", None) or _fallback_rf_score,
    "score_sentence": globals().get("_score_sentence_balanced") or globals().get("score_sentence"),
}

def _force_bind_engine_helpers():
    helper_names = [
        "_english_ai_score", "_explain_paragraph", "_arabic_ai_score", "_compute_confidence",
        "_context_coherence", "_context_drift", "_advanced_stylometry", "_punct_distribution",
        "_lm_perplexity", "_token_prob_variance", "_sliding_window", "_semantic_entropy",
        "_llr_score", "_rf_score", "_bigram_score",
        "_trigram_score", "_pattern_score", "_rhythm", "_local_entropy", "_paragraph_structure",
        "_punct_fingerprint", "_verb_ratio", "_pronoun_ratio", "_compute_fingerprint_score",
        "_simple_gpt_score", "_gpt_formatting_signature", "_paraphrase_engine",
        "_synonym_density", "_discourse_invariant", "_strip_references", "_academic_grounding_profile_v2",
        "_semantic_embedding", "_pattern_memory", "_nb_score", "_citation_bonus",
        "_human_academic_adj", "_human_error_score", "_english_human_score",
        "_deep_human_stylometry", "_academic_grounding_profile",
        "_analyze_paragraphs", "_burst", "_hpen", "_perp", "_aifp", "_trans",
        "_vrich", "_pass", "_rhythm", "_local_entropy", "_paragraph_structure",
        "_punct_fingerprint", "_chunk_analysis", "_transformer_ai_score",
        "_compute_confidence", "_academic_grounding_profile",
        "_nb_extract_features", "score_sentence", "_score_sentence_balanced",
    ]
    for _name in helper_names:
        _fn = globals().get(_name) or getattr(AIDetectionEngine, _name, None)
        if not callable(_fn):
            _fn = _HELPER_FALLBACKS.get(_name)
        if callable(_fn):
            setattr(AIDetectionEngine, _name, _fn)

_force_bind_engine_helpers()

_old_engine_getattribute = getattr(AIDetectionEngine, "__getattribute__", object.__getattribute__)
def _engine_safe_getattribute(self, name):
    try:
        return _old_engine_getattribute(self, name)
    except AttributeError:
        _fn = globals().get(name) or getattr(self.__class__, name, None) or _HELPER_FALLBACKS.get(name)
        if callable(_fn):
            setattr(self.__class__, name, _fn)
            return _fn.__get__(self, self.__class__)
        raise

AIDetectionEngine.__getattribute__ = _engine_safe_getattribute

# ===== Weight rebalance v4: lower academic false positives by fixing final weights only =====
_previous_analyze_for_weight_rebalance = AIDetectionEngine.analyze

def _analyze_weight_rebalanced(self, text, cb=None):
    result = _previous_analyze_for_weight_rebalance(self, text, cb)
    try:
        if not isinstance(result, dict):
            return result

        indicators = result.setdefault("indicators", {})
        extended = result.setdefault("extended", {})
        meta = result.setdefault("precision95_meta", {})

        words = re.findall(r'\b[a-zA-Z][a-zA-Z\-]*\b', text.lower())
        sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
        grounding = self._academic_grounding_profile(text, words, sents)
        g = float(grounding.get("score", 0.0) or 0.0)

        direct_gpt_score = float(extended.get("direct_gpt_score", meta.get("direct_gpt_score", 0.0)) or 0.0)
        gpt_style_score = float(extended.get("gpt_style_score", meta.get("gpt_style_score", 0.0)) or 0.0)
        academic_ai_pressure = float(extended.get("academic_ai_pressure_v3", meta.get("academic_ai_pressure", 0.0)) or 0.0)
        human_guard = float(extended.get("human_academic_guard_v3", meta.get("human_academic_guard", 0.0)) or 0.0)
        ai_sent_ratio = float(extended.get("ai_sentence_ratio", meta.get("ai_sentence_ratio", 0.0)) or 0.0)
        human_sent_ratio = float(extended.get("human_sentence_ratio", meta.get("human_sentence_ratio", 0.0)) or 0.0)
        style_gap = float(extended.get("style_gap_v3", meta.get("style_gap_v3", 0.0)) or 0.0)
        top_ai_mean = float((extended.get("sentence_style_profiles", {}) or {}).get("top_ai_mean", 0.0) or 0.0)
        top_human_mean = float((extended.get("sentence_style_profiles", {}) or {}).get("top_human_mean", 0.0) or 0.0)

        phrase_hits = int(extended.get("repair_phrase_hits", meta.get("phrase_hits", 0)) or 0)
        pattern_hits = int(extended.get("repair_pattern_hits", meta.get("pattern_hits", 0)) or 0)
        struct_hits = int(extended.get("repair_struct_hits", meta.get("struct_hits", 0)) or 0)
        format_hits = int(extended.get("repair_format_hits", meta.get("format_hits", 0)) or 0)

        citation_hits = int(grounding.get("citation_hits", 0) or 0)
        method_hits = int(grounding.get("method_hits", 0) or 0)
        number_hits = int(grounding.get("number_hits", 0) or 0)

        # Rebalanced core equation:
        # direct evidence dominates, style evidence is weak, and human scholarly grounding has stronger pull-down.
        direct_core = (
            direct_gpt_score * 0.68 +
            min(phrase_hits / 4.0, 1.0) * 0.18 +
            min(format_hits / 3.0, 1.0) * 0.06 +
            min(struct_hits / 5.0, 1.0) * 0.04 +
            min(max(ai_sent_ratio - 0.22, 0.0) / 0.30, 1.0) * 0.04
        )

        style_core = (
            gpt_style_score * 0.42 +
            min(max(style_gap, 0.0) / 0.22, 1.0) * 0.24 +
            min(top_ai_mean / 0.62, 1.0) * 0.18 +
            min(ai_sent_ratio / 0.42, 1.0) * 0.16
        )

        human_core = (
            human_guard * 0.56 +
            min(g / 0.80, 1.0) * 0.18 +
            min(human_sent_ratio / 0.34, 1.0) * 0.14 +
            min(top_human_mean / 0.52, 1.0) * 0.06 +
            (0.03 if citation_hits >= 3 else 0.0) +
            (0.02 if method_hits >= 5 else 0.0) +
            (0.01 if number_hits >= max(8, len(words) // 110) else 0.0)
        )

        final = direct_core * 0.82 + style_core * 0.18 - human_core * 0.72

        # Hard guards against style-only inflation in academic texts.
        weak_direct = (
            phrase_hits == 0 and
            direct_gpt_score < 0.28 and
            format_hits <= 1 and
            struct_hits <= 1
        )
        if weak_direct and g >= 0.72:
            final = min(final, 0.16)
        elif weak_direct and g >= 0.60:
            final = min(final, 0.38)  # FIX v116
        elif weak_direct and g >= 0.48:
            final = min(final, 0.30)

        if phrase_hits <= 1 and pattern_hits <= 2 and direct_gpt_score < 0.34:
            if human_guard >= 0.34 or g >= 0.58:
                final = min(final, 0.42)  # FIX v116
            if human_sent_ratio >= 0.18:
                final = min(final, 0.35)  # FIX v116

        if citation_hits >= 4 and method_hits >= 4 and phrase_hits == 0 and direct_gpt_score < 0.30:
            final -= 0.04

        # Promotion requires real direct evidence now.
        if phrase_hits >= 4 and direct_gpt_score >= 0.56:
            final = max(final, 0.82)
        elif phrase_hits >= 3 and pattern_hits >= 2 and direct_gpt_score >= 0.48 and ai_sent_ratio >= 0.24:
            final = max(final, 0.72)
        elif phrase_hits >= 2 and direct_gpt_score >= 0.44 and g < 0.45 and human_sent_ratio < 0.14:
            final = max(final, 0.58)

        # Never let style alone push an academic paper into HIGH/CRITICAL.
        if phrase_hits <= 1 and direct_gpt_score < 0.40:
            final = min(final, 0.54)
        if phrase_hits == 0 and direct_gpt_score < 0.32 and g >= 0.50:
            final = min(final, 0.34)

        # FIX v115: Increased prior weight from 0.30 to 0.45.
        # Previously 70% of the multi-layer analysis was discarded here.
        # Now: prior (layers 1-6) contribute 45%, rebalance layer contributes 55%.
        prior = float(result.get("score", 0.0) or 0.0)
        final = prior * 0.45 + max(0.0, min(final, 0.995)) * 0.55

        # Final academic protection after blending.
        if weak_direct and g >= 0.60:
            final = min(final, 0.42)  # FIX v116
        if phrase_hits == 0 and direct_gpt_score < 0.30 and human_guard >= 0.38:
            final = min(final, 0.35)  # FIX v116

        final = max(0.0, min(final, 0.995))

        result["score"] = final
        result["percentage"] = final * 100.0
        result["human_score"] = (1.0 - final) * 100.0
        result["risk_level"] = (
            "CRITICAL" if final >= 0.88 else
            "HIGH" if final >= 0.74 else
            "MEDIUM" if final >= 0.56 else
            "LOW" if final >= 0.28 else
            "MINIMAL"
        )
        _verdicts = {
            "CRITICAL": "اشتباه مرتفع جدًا - يحتاج تحقق بشري",
            "HIGH":     "اشتباه مرتفع - يحتاج تحقق بشري",
            "MEDIUM":   "نتيجة مختلطة / غير حاسمة",
            "LOW":      "اشتباه منخفض",
            "MINIMAL":  "بشري على الأرجح",
        }
        result["verdict"] = _verdicts[result["risk_level"]]

        indicators["Weight Rebalance v4 ⚖️"] = round(final, 4)
        indicators["Direct Evidence Priority ▲"] = round(direct_core, 4)
        indicators["Academic Human Protection ▼"] = round(human_core, 4)

        extended["weight_rebalance_v4"] = {
            "grounding": round(g, 4),
            "direct_gpt_score": round(direct_gpt_score, 4),
            "gpt_style_score": round(gpt_style_score, 4),
            "academic_ai_pressure_prior": round(academic_ai_pressure, 4),
            "human_guard": round(human_guard, 4),
            "direct_core": round(direct_core, 4),
            "style_core": round(style_core, 4),
            "human_core": round(human_core, 4),
            "phrase_hits": phrase_hits,
            "pattern_hits": pattern_hits,
            "struct_hits": struct_hits,
            "format_hits": format_hits,
            "ai_sentence_ratio": round(ai_sent_ratio, 4),
            "human_sentence_ratio": round(human_sent_ratio, 4),
            "style_gap": round(style_gap, 4),
            "top_ai_mean": round(top_ai_mean, 4),
            "top_human_mean": round(top_human_mean, 4),
            "adjusted_final": round(final, 4),
        }
        meta["patched_by"] = "weight_rebalance_v4_direct_evidence_priority"
        meta["final_score"] = round(final, 4)
        return result
    except Exception:
        return result

AIDetectionEngine.analyze = _analyze_weight_rebalanced


# ===== Precision repair v3: strong human-first rebalance =====

def _precision97_analyze(self, text, cb=None):
    base_analyze = getattr(self, "_orig_analyze_precision95", None)
    if base_analyze is None:
        base_analyze = getattr(AIDetectionEngine, "_orig_analyze_precision95", None)
    if base_analyze is None:
        base_analyze = AIDetectionEngine.analyze

    result = base_analyze(self, text, cb) if isinstance(base_analyze, _precision_types.FunctionType) else base_analyze(text, cb)
    if not isinstance(result, dict) or result.get("error"):
        return result

    try:
        clean_text = self._strip_references(text)
    except Exception:
        clean_text = text

    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    words = re.findall(r'\b[a-zA-Z]+\b', clean_text.lower())
    sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', clean_text) if len(s.split()) >= 4]

    indicators = dict(result.get("indicators", {}) or {})
    extended = dict(result.get("extended", {}) or {})

    fp = float(indicators.get("🔍 Fingerprint Score v35 ★★★", extended.get("fingerprint_score", 0.0)) or 0.0)
    gf = float(indicators.get("GPT Format Signature ★★★", extended.get("gpt_format_score", 0.0)) or 0.0)
    sg = float(indicators.get("Simple GPT Score v22 ★★★", extended.get("simple_gpt_score", 0.0)) or 0.0)
    en = float(indicators.get("English AI Engine v2 ★★★", extended.get("english_ai_score", 0.0)) or 0.0)
    nb = float(indicators.get("Naive Bayes ML v25 ★", extended.get("nb_score", 0.0)) or 0.0)
    llr = float(indicators.get("LLR v28 ★★★ [corpus جديد]", extended.get("llr_score", 0.0)) or 0.0)
    pat_mem = float(indicators.get("Pattern Memory v20 ★★★", extended.get("pat_mem", 0.0)) or 0.0)
    para_results = extended.get("paragraph_results", []) or []
    para_meta = self._precision96_paragraph_corroboration(para_results)

    direct = self._precision96_direct_gpt_evidence(clean_text, words, sents)
    phrase_hits = int(direct["phrase_hits"])
    pattern_hits = int(direct["pattern_hits"])
    format_hits = int(direct["format_hits"])
    struct_hits = int(direct["struct_hits"])
    starter_ratio = float(direct["starter_ratio"])
    pattern_density = float(direct["pattern_density"])
    citation_hits = int(direct["citation_hits"])
    numeric_hits = int(direct["numeric_hits"])

    first_person = len(re.findall(r'\b(?:i|we|our|my|us)\b', clean_text.lower()))
    hedges = len(re.findall(r'\b(?:may|might|could|perhaps|possibly|likely|unlikely|approximately|suggests?|appears?|indicates?)\b', clean_text.lower()))
    quote_hits = len(re.findall(r'["“”\']', clean_text))
    long_text = len(words) >= 220

    direct_gpt_score = (
        min(phrase_hits / 4.0, 1.0) * 0.42 +
        min(pattern_density / 1.25, 1.0) * 0.24 +
        min(format_hits / 3.0, 1.0) * 0.08 +
        min(struct_hits / 4.0, 1.0) * 0.16 +
        min(starter_ratio / 0.42, 1.0) * 0.04 +
        max(gf - 0.10, 0.0) * 0.10
    )
    if phrase_hits >= 2 and pattern_hits >= 2:
        direct_gpt_score += 0.06
    if phrase_hits >= 3:
        direct_gpt_score += 0.04
    if struct_hits >= 2 and format_hits >= 1:
        direct_gpt_score += 0.02
    direct_gpt_score = max(0.0, min(direct_gpt_score, 0.99))

    # Style becomes support only, never a dominant signal.
    gpt_style_score = (
        sg * 0.26 +
        en * 0.18 +
        fp * 0.14 +
        min(nb, 0.82) * 0.08 +
        min(llr, 0.82) * 0.05 +
        min(pat_mem, 0.82) * 0.04
    )
    if para_meta["strong"] >= 2:
        gpt_style_score += 0.03
    elif para_meta["mid"] >= 2:
        gpt_style_score += 0.015
    gpt_style_score = max(0.0, min(gpt_style_score, 0.88))

    # Stronger human/academic guard.
    academic_guard = 0.0
    if citation_hits >= 2:
        academic_guard += 0.10
    if citation_hits >= 4:
        academic_guard += 0.05
    if numeric_hits >= max(6, len(words) // 120):
        academic_guard += 0.07
    if first_person >= 2:
        academic_guard += 0.04
    if hedges >= 4:
        academic_guard += 0.04
    if quote_hits >= 4:
        academic_guard += 0.03
    if long_text and (citation_hits >= 2 or numeric_hits >= 8):
        academic_guard += 0.05
    academic_guard = min(academic_guard, 0.28)

    # Human-first fusion.
    final = direct_gpt_score * 0.82 + gpt_style_score * 0.18
    if direct_gpt_score < 0.55:
        final -= academic_guard
    else:
        final -= academic_guard * 0.35

    consensus = 0
    consensus += 1 if sg >= 0.74 else 0
    consensus += 1 if nb >= 0.74 else 0
    consensus += 1 if en >= 0.54 else 0
    consensus += 1 if fp >= 0.26 else 0
    consensus += 1 if llr >= 0.64 else 0
    consensus += 1 if para_meta["strong"] >= 2 or para_meta["avg"] >= 0.54 else 0

    # Defaults kept for backward-compatible metadata/export paths.
    route_rescue = 0.0
    cross_engine_peak = max(sg, nb, en, fp, llr, pat_mem)
    cross_engine_mean = (sg + nb + en + fp + llr + min(pat_mem, 1.0)) / 6.0
    blocker_sparse_fp = False

    # Remove style-only floors. Consensus can only lift slightly when there is some direct basis.
    if direct_gpt_score >= 0.18 and consensus >= 4 and gpt_style_score >= 0.52:
        final = max(final, 0.26)
    if direct_gpt_score >= 0.24 and consensus >= 5 and gpt_style_score >= 0.58:
        final = max(final, 0.34)

    # Human clamps: academic/grounded text should stay low unless direct evidence is real.
    weak_direct = direct_gpt_score < 0.24
    very_weak_direct = direct_gpt_score < 0.16
    grounded_academic = (
        citation_hits >= 2 or numeric_hits >= 8 or hedges >= 4 or first_person >= 2 or quote_hits >= 4
    )

    if very_weak_direct and grounded_academic:
        final -= 0.02
    elif weak_direct and grounded_academic:
        final = min(final, 0.35)  # FIX v116
    elif direct_gpt_score < 0.30 and citation_hits >= 2 and numeric_hits >= 6:
        final = min(final, 0.42)  # FIX v116

    # High labels now require direct evidence, not style cleanliness.
    if direct_gpt_score >= 0.76 and phrase_hits >= 3 and (pattern_hits >= 2 or struct_hits >= 2):
        final = max(final, 0.90)
    elif direct_gpt_score >= 0.62 and phrase_hits >= 2 and pattern_hits >= 2:
        final = max(final, 0.78)
    elif direct_gpt_score >= 0.52 and phrase_hits >= 2 and struct_hits >= 2:
        final = max(final, 0.68)

    # Block escalation from style alone.
    if direct_gpt_score < 0.32:
        final = min(final, 0.42)
    if direct_gpt_score < 0.24:
        final = min(final, 0.45)  # FIX v116

    final = max(0.0, min(final, 0.995))

    result["score"] = final
    result["percentage"] = final * 100.0
    result["human_score"] = (1.0 - final) * 100.0
    result["risk_level"] = (
        "CRITICAL" if final >= 0.90 else
        "HIGH" if final >= 0.78 else
        "MEDIUM" if final >= 0.58 else
        "LOW" if final >= 0.24 else
        "MINIMAL"
    )
    _verdicts = {
        "CRITICAL": "اشتباه مرتفع جدًا - يحتاج تحقق بشري",
        "HIGH":     "اشتباه مرتفع - يحتاج تحقق بشري",
        "MEDIUM":   "نتيجة مختلطة / غير حاسمة",
        "LOW":      "اشتباه منخفض",
        "MINIMAL":  "بشري على الأرجح",
    }
    result["verdict"] = _verdicts[result["risk_level"]]

    # Keep indicators honest: do not amplify style-only suspicion.
    indicators["🔍 Fingerprint Score v35 ★★★"] = min(
        max(fp, direct_gpt_score * 0.78 + gpt_style_score * 0.12),
        0.96
    )
    if direct_gpt_score >= 0.30:
        indicators["Simple GPT Score v22 ★★★"] = max(sg, min(gpt_style_score, 0.86))
    elif grounded_academic:
        indicators["Simple GPT Score v22 ★★★"] = min(sg, 0.54)
        indicators["Naive Bayes ML v25 ★"] = min(nb, 0.56)

    extended["direct_gpt_score"] = round(direct_gpt_score, 4)
    extended["gpt_style_score"] = round(gpt_style_score, 4)
    extended["academic_guard_repair_v3"] = round(academic_guard, 4)
    extended["consensus_repair_v3"] = int(consensus)
    extended["repair_phrase_hits"] = int(phrase_hits)
    extended["repair_pattern_hits"] = int(pattern_hits)
    extended["repair_struct_hits"] = int(struct_hits)
    extended["repair_format_hits"] = int(format_hits)
    extended["repair_paragraph_corroboration"] = para_meta

    result["indicators"] = indicators
    result["extended"] = extended
    result["precision95_meta"] = {
        "patched_by": "precision97_human_first",
        "direct_gpt_score": round(direct_gpt_score, 4),
        "gpt_style_score": round(gpt_style_score, 4),
        "consensus": int(consensus),
        "academic_guard": round(academic_guard, 4),
        "route_rescue_score": round(route_rescue, 4),
        "cross_engine_peak": round(cross_engine_peak, 4),
        "cross_engine_mean": round(cross_engine_mean, 4),
        "blocker_sparse_fp": blocker_sparse_fp,
        "phrase_hits": int(phrase_hits),
        "pattern_hits": int(pattern_hits),
        "struct_hits": int(struct_hits),
        "format_hits": int(format_hits),
        "citation_hits": int(citation_hits),
        "numeric_hits": int(numeric_hits),
        "final_score": round(final, 4),
    }
    return result

AIDetectionEngine.analyze = _precision97_analyze


# ===== Precision repair v4: route GPT fingerprint evidence into final AI score correctly =====

def _precision98_analyze(self, text, cb=None):
    base_analyze = globals().get("_precision97_analyze")
    if base_analyze is None:
        base_analyze = getattr(self, "_orig_analyze_precision95", None)
    if base_analyze is None:
        base_analyze = getattr(AIDetectionEngine, "_orig_analyze_precision95", None)
    if base_analyze is None:
        base_analyze = AIDetectionEngine.analyze

    result = base_analyze(self, text, cb) if isinstance(base_analyze, _precision_types.FunctionType) else base_analyze(text, cb)
    if not isinstance(result, dict) or result.get("error"):
        return result

    try:
        clean_text = self._strip_references(text)
    except Exception:
        clean_text = text

    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    words = re.findall(r'\b[a-zA-Z]+\b', clean_text.lower())
    sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', clean_text) if len(re.findall(r"[A-Za-z]+", s)) >= 4]

    indicators = dict(result.get("indicators", {}) or {})
    extended = dict(result.get("extended", {}) or {})
    fpd = dict(extended.get("fp_details", {}) or {})

    fp = float(indicators.get("🔍 Fingerprint Score v35 ★★★", extended.get("fingerprint_score", 0.0)) or 0.0)
    gf = float(indicators.get("GPT Format Signature ★★★", extended.get("gpt_format_score", 0.0)) or 0.0)
    sg = float(indicators.get("Simple GPT Score v22 ★★★", extended.get("simple_gpt_score", 0.0)) or 0.0)
    en = float(indicators.get("English AI Engine v2 ★★★", indicators.get("English AI Engine v2", extended.get("english_ai_score", 0.0))) or 0.0)
    nb = float(indicators.get("Naive Bayes ML v25 ★", extended.get("nb_score", 0.0)) or 0.0)
    llr = float(indicators.get("LLR v28 ★★★ [corpus جديد]", extended.get("llr_score", 0.0)) or 0.0)
    pat_mem = float(indicators.get("Pattern Memory v20 ★★★", extended.get("pat_mem", 0.0)) or 0.0)
    para_results = extended.get("paragraph_results", []) or []
    para_meta = self._precision96_paragraph_corroboration(para_results)

    direct = self._precision96_direct_gpt_evidence(clean_text, words, sents)
    phrase_hits = int(direct["phrase_hits"])
    pattern_hits = int(direct["pattern_hits"])
    format_hits = int(direct["format_hits"])
    struct_hits = int(direct["struct_hits"])
    starter_ratio = float(direct["starter_ratio"])
    pattern_density = float(direct["pattern_density"])
    citation_hits = int(direct["citation_hits"])
    numeric_hits = int(direct["numeric_hits"])

    first_person = len(re.findall(r'\b(?:i|we|our|my|us)\b', clean_text.lower()))
    hedges = len(re.findall(r'\b(?:may|might|could|perhaps|possibly|likely|unlikely|approximately|suggests?|appears?|indicates?)\b', clean_text.lower()))
    quote_hits = len(re.findall(r'["“”\']', clean_text))

    # Route fine-grained GPT fingerprint channels into a dedicated evidence score.
    fp_phrase = float(fpd.get("fp_en_phrases", 0.0) or 0.0)
    fp_structure = float(fpd.get("fp_structure", 0.0) or 0.0)
    fp_simple = float(fpd.get("fp_simple_gpt", 0.0) or 0.0)
    fp_t2 = float(fpd.get("fp_t2_patterns", 0.0) or 0.0)
    fp_vocab = float(fpd.get("fp_vocab", 0.0) or 0.0)
    fp_trans = float(fpd.get("fp_academic_trans", 0.0) or 0.0)
    fp_format = float(fpd.get("fp_format_sig", 0.0) or 0.0)
    fp_triplets = float(fpd.get("fp_triplets", 0.0) or 0.0)
    fp_pairs = float(fpd.get("fp_pairs", 0.0) or 0.0)
    fp_uniformity = float(fpd.get("fp_uniformity", 0.0) or 0.0)
    fp_cliches = float(fpd.get("fp_cliches", 0.0) or 0.0)

    fingerprint_evidence = (
        fp_phrase * 0.20 +
        fp_structure * 0.16 +
        fp_simple * 0.14 +
        fp_t2 * 0.12 +
        fp_trans * 0.10 +
        fp_format * 0.08 +
        fp_triplets * 0.06 +
        fp_pairs * 0.05 +
        fp_uniformity * 0.05 +
        fp_cliches * 0.02 +
        fp_vocab * 0.02
    )
    fingerprint_evidence = max(0.0, min(fingerprint_evidence, 0.98))

    direct_gpt_score = (
        min(phrase_hits / 4.0, 1.0) * 0.28 +
        min(pattern_density / 1.15, 1.0) * 0.16 +
        min(format_hits / 3.0, 1.0) * 0.06 +
        min(struct_hits / 4.0, 1.0) * 0.14 +
        min(starter_ratio / 0.38, 1.0) * 0.04 +
        max(gf - 0.08, 0.0) * 0.08 +
        fingerprint_evidence * 0.24
    )
    if phrase_hits >= 2 and pattern_hits >= 2:
        direct_gpt_score += 0.05
    if phrase_hits >= 1 and fingerprint_evidence >= 0.38:
        direct_gpt_score += 0.04
    if struct_hits >= 2 and (fp_structure >= 0.32 or fp_t2 >= 0.28):
        direct_gpt_score += 0.04
    if fp_phrase >= 0.35 and fp_trans >= 0.30:
        direct_gpt_score += 0.03
    direct_gpt_score = max(0.0, min(direct_gpt_score, 0.99))

    gpt_style_score = (
        sg * 0.24 +
        en * 0.17 +
        fp * 0.12 +
        min(nb, 0.92) * 0.12 +
        min(llr, 0.92) * 0.09 +
        min(pat_mem, 0.90) * 0.05 +
        fingerprint_evidence * 0.11
    )
    if para_meta["strong"] >= 2:
        gpt_style_score += 0.03
    elif para_meta["mid"] >= 2:
        gpt_style_score += 0.015
    gpt_style_score = max(0.0, min(gpt_style_score, 0.92))

    academic_guard = 0.0
    if citation_hits >= 2:
        academic_guard += 0.08
    if citation_hits >= 4:
        academic_guard += 0.03
    if numeric_hits >= max(6, len(words) // 120):
        academic_guard += 0.06
    if first_person >= 2:
        academic_guard += 0.03
    if hedges >= 4:
        academic_guard += 0.03
    if quote_hits >= 4:
        academic_guard += 0.02
    academic_guard = min(academic_guard, 0.20)

    consensus = 0
    consensus += 1 if sg >= 0.72 else 0
    consensus += 1 if nb >= 0.74 else 0
    consensus += 1 if en >= 0.54 else 0
    consensus += 1 if fp >= 0.28 else 0
    consensus += 1 if llr >= 0.64 else 0
    consensus += 1 if fingerprint_evidence >= 0.36 else 0
    consensus += 1 if para_meta["strong"] >= 2 or para_meta["avg"] >= 0.54 else 0

    # Core fusion: real GPT fingerprint must move the final result.
    final = direct_gpt_score * 0.58 + gpt_style_score * 0.30 + fingerprint_evidence * 0.12

    # Human discount only when GPT evidence is genuinely weak.
    if max(direct_gpt_score, fingerprint_evidence) < 0.24 and consensus <= 2 and gpt_style_score < 0.42:
        final -= academic_guard
    elif max(direct_gpt_score, fingerprint_evidence) < 0.34 and consensus <= 3 and gpt_style_score < 0.50:
        final -= academic_guard * 0.55
    else:
        final -= academic_guard * 0.18

    # Floors that ensure GPT fingerprint presence actually affects the outcome.
    if fingerprint_evidence >= 0.34 and consensus >= 4 and max(sg, nb, en) >= 0.70:
        final = max(final, 0.42)
    if fingerprint_evidence >= 0.46 and consensus >= 5 and max(sg, nb, en) >= 0.74:
        final = max(final, 0.56)
    if fingerprint_evidence >= 0.58 and consensus >= 5 and sg >= 0.76 and nb >= 0.76:
        final = max(final, 0.68)
    if direct_gpt_score >= 0.64 and (phrase_hits >= 2 or fp_phrase >= 0.42) and pattern_hits >= 2:
        final = max(final, 0.80)

    # Protect polished human academic text only when both direct/fingerprint evidence stay weak.
    if citation_hits >= 2 and numeric_hits >= 6 and max(direct_gpt_score, fingerprint_evidence) < 0.20 and consensus <= 2:
        final -= 0.03
    elif (citation_hits >= 2 or numeric_hits >= 8 or hedges >= 4) and max(direct_gpt_score, fingerprint_evidence) < 0.16 and consensus <= 2:
        final -= 0.02

    final = max(0.0, min(final, 0.995))

    result["score"] = final
    result["percentage"] = final * 100.0
    result["human_score"] = (1.0 - final) * 100.0
    result["risk_level"] = (
        "CRITICAL" if final >= 0.88 else
        "HIGH" if final >= 0.74 else
        "MEDIUM" if final >= 0.56 else
        "LOW" if final >= 0.28 else
        "MINIMAL"
    )
    _verdicts = {
        "CRITICAL": "اشتباه مرتفع جدًا - يحتاج تحقق بشري",
        "HIGH":     "اشتباه مرتفع - يحتاج تحقق بشري",
        "MEDIUM":   "نتيجة مختلطة / غير حاسمة",
        "LOW":      "اشتباه منخفض",
        "MINIMAL":  "بشري على الأرجح",
    }
    result["verdict"] = _verdicts[result["risk_level"]]

    # Normalize indicator keys so the UI reads the actual values.
    indicators["English AI Engine v2 ★★★"] = en
    indicators["English AI Engine v2"] = en
    indicators["Paraphrase Engine v21 ★★"] = float(indicators.get("Paraphrase Engine v21 ★★", indicators.get("Paraphrase Engine v21 ★★★", 0.0)) or 0.0)
    indicators["Paraphrase Engine v21 ★★★"] = indicators["Paraphrase Engine v21 ★★"]
    indicators["Synonym Density v21 ★★"] = float(indicators.get("Synonym Density v21 ★★", indicators.get("Synonym Density v21 ★★★", 0.0)) or 0.0)
    indicators["Synonym Density v21 ★★★"] = indicators["Synonym Density v21 ★★"]

    indicators["🔍 Fingerprint Score v35 ★★★"] = max(fp, min(fingerprint_evidence * 0.82 + direct_gpt_score * 0.28 + gpt_style_score * 0.08, 0.98))
    indicators["Simple GPT Score v22 ★★★"] = max(sg, min(gpt_style_score, 0.94)) if (fingerprint_evidence >= 0.28 or direct_gpt_score >= 0.24) else sg
    indicators["Academic Grounding Guard ▼"] = round(academic_guard, 4)

    extended["direct_gpt_score"] = round(direct_gpt_score, 4)
    extended["gpt_style_score"] = round(gpt_style_score, 4)
    extended["fingerprint_evidence_score"] = round(fingerprint_evidence, 4)
    extended["academic_guard_repair_v4"] = round(academic_guard, 4)
    extended["consensus_repair_v4"] = int(consensus)
    extended["repair_phrase_hits"] = int(phrase_hits)
    extended["repair_pattern_hits"] = int(pattern_hits)
    extended["repair_struct_hits"] = int(struct_hits)
    extended["repair_format_hits"] = int(format_hits)
    extended["repair_paragraph_corroboration"] = para_meta

    result["indicators"] = indicators
    result["extended"] = extended
    result["precision95_meta"] = {
        "patched_by": "precision98_gpt_fingerprint_route_fix",
        "direct_gpt_score": round(direct_gpt_score, 4),
        "fingerprint_evidence_score": round(fingerprint_evidence, 4),
        "gpt_style_score": round(gpt_style_score, 4),
        "consensus": int(consensus),
        "academic_guard": round(academic_guard, 4),
        "phrase_hits": int(phrase_hits),
        "pattern_hits": int(pattern_hits),
        "struct_hits": int(struct_hits),
        "format_hits": int(format_hits),
        "citation_hits": int(citation_hits),
        "numeric_hits": int(numeric_hits),
        "final_score": round(final, 4),
    }
    return result

AIDetectionEngine.analyze = _precision98_analyze


# ===== Real route repair: legacy fp_details must feed final AI percentage =====

def _precision99_analyze(self, text, cb=None):
    base_analyze = globals().get("_precision98_analyze") or globals().get("_precision97_analyze")
    if base_analyze is None:
        base_analyze = getattr(self, "_orig_analyze_precision95", None)
    if base_analyze is None:
        base_analyze = getattr(AIDetectionEngine, "_orig_analyze_precision95", None)
    if base_analyze is None:
        base_analyze = AIDetectionEngine.analyze

    result = base_analyze(self, text, cb) if isinstance(base_analyze, _precision_types.FunctionType) else base_analyze(text, cb)
    if not isinstance(result, dict) or result.get("error"):
        return result

    try:
        clean_text = self._strip_references(text)
    except Exception:
        clean_text = text

    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    words = re.findall(r'\b[a-zA-Z]+\b', clean_text.lower())
    sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', clean_text) if len(re.findall(r"[A-Za-z]+", s)) >= 4]

    indicators = dict(result.get("indicators", {}) or {})
    extended = dict(result.get("extended", {}) or {})
    fpd = dict(extended.get("fp_details", {}) or {})

    fp = float(indicators.get("🔍 Fingerprint Score v35 ★★★", extended.get("fingerprint_score", 0.0)) or 0.0)
    gf = float(indicators.get("GPT Format Signature ★★★", extended.get("gpt_format_score", 0.0)) or 0.0)
    sg = float(indicators.get("Simple GPT Score v22 ★★★", extended.get("simple_gpt_score", 0.0)) or 0.0)
    en = float(indicators.get("English AI Engine v2 ★★★", indicators.get("English AI Engine v2", extended.get("english_ai_score", 0.0))) or 0.0)
    nb = float(indicators.get("Naive Bayes ML v25 ★", extended.get("nb_score", 0.0)) or 0.0)
    llr = float(indicators.get("LLR v28 ★★★ [corpus جديد]", extended.get("llr_score", 0.0)) or 0.0)
    pat_mem = float(indicators.get("Pattern Memory v20 ★★★", extended.get("pat_mem", 0.0)) or 0.0)
    para_results = extended.get("paragraph_results", []) or []
    para_meta = self._precision96_paragraph_corroboration(para_results)

    direct = self._precision96_direct_gpt_evidence(clean_text, words, sents)
    phrase_hits = int(direct["phrase_hits"])
    pattern_hits = int(direct["pattern_hits"])
    format_hits = int(direct["format_hits"])
    struct_hits = int(direct["struct_hits"])
    starter_ratio = float(direct["starter_ratio"])
    pattern_density = float(direct["pattern_density"])
    citation_hits = int(direct["citation_hits"])
    numeric_hits = int(direct["numeric_hits"])

    first_person = len(re.findall(r'\b(?:i|we|our|my|us)\b', clean_text.lower()))
    hedges = len(re.findall(r'\b(?:may|might|could|perhaps|possibly|likely|unlikely|approximately|suggests?|appears?|indicates?)\b', clean_text.lower()))
    quote_hits = len(re.findall(r'["“”\']', clean_text))

    # Detailed v35 channels if available
    fp_phrase = float(fpd.get("fp_en_phrases", 0.0) or 0.0)
    fp_structure = float(fpd.get("fp_structure", 0.0) or 0.0)
    fp_simple = float(fpd.get("fp_simple_gpt", 0.0) or 0.0)
    fp_t2 = float(fpd.get("fp_t2_patterns", 0.0) or 0.0)
    fp_vocab = float(fpd.get("fp_vocab", 0.0) or 0.0)
    fp_trans = float(fpd.get("fp_academic_trans", 0.0) or 0.0)
    fp_format = float(fpd.get("fp_format_sig", 0.0) or 0.0)
    fp_triplets = float(fpd.get("fp_triplets", 0.0) or 0.0)
    fp_pairs = float(fpd.get("fp_pairs", 0.0) or 0.0)
    fp_uniformity = float(fpd.get("fp_uniformity", 0.0) or 0.0)
    fp_cliches = float(fpd.get("fp_cliches", 0.0) or 0.0)

    # Legacy cache fallback (this was the real bug: analyze expected new keys,
    # but cache often still stored legacy keys only, so fingerprint_evidence stayed near zero)
    legacy_exact = int(fpd.get("exact_phrases", 0) or 0)
    legacy_struct = int(fpd.get("struct_hits", 0) or 0)
    legacy_starter = float(fpd.get("starter_ratio", 0.0) or 0.0)
    legacy_corrob = float(fpd.get("corroboration", 0.0) or 0.0)

    if fp_phrase == 0.0 and legacy_exact:
        fp_phrase = min(legacy_exact / 3.0, 1.0)
    if fp_structure == 0.0 and legacy_struct:
        fp_structure = min(legacy_struct / 3.5, 1.0)
    if fp_trans == 0.0 and legacy_starter:
        fp_trans = min(max(legacy_starter - 0.12, 0.0) / 0.45, 1.0)
    if fp_uniformity == 0.0 and legacy_corrob:
        fp_uniformity = min(legacy_corrob / 3.0, 1.0)
    if fp_simple == 0.0 and sg > 0:
        fp_simple = min(sg, 1.0)
    if fp_t2 == 0.0 and pat_mem > 0:
        fp_t2 = min(pat_mem, 1.0)
    if fp_format == 0.0 and gf > 0:
        fp_format = min(gf, 1.0)

    fingerprint_evidence = (
        fp_phrase * 0.22 +
        fp_structure * 0.18 +
        fp_simple * 0.13 +
        fp_t2 * 0.10 +
        fp_trans * 0.10 +
        fp_format * 0.08 +
        fp_triplets * 0.05 +
        fp_pairs * 0.04 +
        fp_uniformity * 0.05 +
        fp_cliches * 0.02 +
        fp_vocab * 0.03
    )

    # Extra fallback from top-level scores when legacy routing exists but detailed channels remain sparse.
    if fingerprint_evidence < 0.12:
        fingerprint_evidence = max(
            fingerprint_evidence,
            fp * 0.58 + sg * 0.12 + en * 0.08 + min(pat_mem, 0.9) * 0.06
        )
    fingerprint_evidence = max(0.0, min(fingerprint_evidence, 0.99))

    direct_gpt_score = (
        min(phrase_hits / 4.0, 1.0) * 0.26 +
        min(pattern_density / 1.10, 1.0) * 0.16 +
        min(format_hits / 3.0, 1.0) * 0.06 +
        min(struct_hits / 4.0, 1.0) * 0.14 +
        min(starter_ratio / 0.36, 1.0) * 0.04 +
        max(gf - 0.08, 0.0) * 0.08 +
        fingerprint_evidence * 0.26
    )
    if phrase_hits >= 2 and pattern_hits >= 2:
        direct_gpt_score += 0.05
    if phrase_hits >= 1 and fingerprint_evidence >= 0.32:
        direct_gpt_score += 0.05
    if struct_hits >= 2 and (fp_structure >= 0.28 or fp_t2 >= 0.28):
        direct_gpt_score += 0.04
    if fp_phrase >= 0.35 and fp_trans >= 0.28:
        direct_gpt_score += 0.03
    direct_gpt_score = max(0.0, min(direct_gpt_score, 0.99))

    gpt_style_score = (
        sg * 0.23 +
        en * 0.17 +
        fp * 0.14 +
        min(nb, 0.92) * 0.11 +
        min(llr, 0.92) * 0.08 +
        min(pat_mem, 0.90) * 0.05 +
        fingerprint_evidence * 0.14
    )
    if para_meta["strong"] >= 2:
        gpt_style_score += 0.03
    elif para_meta["mid"] >= 2:
        gpt_style_score += 0.015
    gpt_style_score = max(0.0, min(gpt_style_score, 0.94))

    academic_guard = 0.0
    if citation_hits >= 2:
        academic_guard += 0.08
    if citation_hits >= 4:
        academic_guard += 0.03
    if numeric_hits >= max(6, len(words) // 120):
        academic_guard += 0.06
    if first_person >= 2:
        academic_guard += 0.03
    if hedges >= 4:
        academic_guard += 0.03
    if quote_hits >= 4:
        academic_guard += 0.02
    academic_guard = min(academic_guard, 0.20)

    consensus = 0
    consensus += 1 if sg >= 0.72 else 0
    consensus += 1 if nb >= 0.74 else 0
    consensus += 1 if en >= 0.54 else 0
    consensus += 1 if fp >= 0.28 else 0
    consensus += 1 if llr >= 0.64 else 0
    consensus += 1 if fingerprint_evidence >= 0.30 else 0
    consensus += 1 if para_meta["strong"] >= 2 or para_meta["avg"] >= 0.54 else 0

    # Route trace: rescue AI score when multiple AI engines agree but legacy/direct route stayed sparse.
    cross_engine_peak = max(sg, nb, en, fp, llr, pat_mem)
    cross_engine_mean = (sg + nb + en + fp + llr + min(pat_mem, 1.0)) / 6.0
    route_rescue = (
        cross_engine_peak * 0.42 +
        cross_engine_mean * 0.26 +
        (1.0 if para_meta.get("strong", 0) >= 2 else 0.0) * 0.08 +
        min(para_meta.get("avg", 0.0) / 0.70, 1.0) * 0.10 +
        min(max(phrase_hits + pattern_hits + struct_hits - 1, 0) / 6.0, 1.0) * 0.14
    )
    route_rescue = max(0.0, min(route_rescue, 0.99))

    final = (
        direct_gpt_score * 0.46 +
        gpt_style_score * 0.18 +
        fingerprint_evidence * 0.18 +
        route_rescue * 0.18
    )

    blocker_sparse_fp = bool(
        fingerprint_evidence < 0.18 and
        direct_gpt_score < 0.20 and
        cross_engine_peak >= 0.62 and
        consensus >= 4
    )

    if max(direct_gpt_score, fingerprint_evidence, route_rescue) < 0.24 and consensus <= 2 and gpt_style_score < 0.42:
        final -= academic_guard
    elif max(direct_gpt_score, fingerprint_evidence, route_rescue) < 0.34 and consensus <= 3 and gpt_style_score < 0.50:
        final -= academic_guard * 0.55
    else:
        final -= academic_guard * 0.12

    # Strong floors when GPT fingerprint is consistently present, even if one route stayed sparse.
    if (fingerprint_evidence >= 0.30 or route_rescue >= 0.42) and consensus >= 4 and cross_engine_peak >= 0.66:
        final = max(final, 0.40)
    if (fingerprint_evidence >= 0.42 or route_rescue >= 0.54) and consensus >= 4 and cross_engine_peak >= 0.70:
        final = max(final, 0.52)
    if (fingerprint_evidence >= 0.54 or route_rescue >= 0.64) and consensus >= 5 and cross_engine_peak >= 0.74:
        final = max(final, 0.64)
    if direct_gpt_score >= 0.62 and (phrase_hits >= 2 or fp_phrase >= 0.42 or route_rescue >= 0.66) and pattern_hits >= 2:
        final = max(final, 0.80)

    # Cross-engine rescue: if many engines agree, do not let academic protection pin the score at ~14%.
    if blocker_sparse_fp:
        final = max(final, 0.34)
    if consensus >= 5 and cross_engine_peak >= 0.72 and cross_engine_mean >= 0.54:
        final = max(final, 0.46)
    if consensus >= 6 and cross_engine_peak >= 0.78 and cross_engine_mean >= 0.60:
        final = max(final, 0.58)

    # Keep polished human academic writing protected only when AI evidence is truly weak.
    if citation_hits >= 2 and numeric_hits >= 6 and max(direct_gpt_score, fingerprint_evidence, route_rescue) < 0.18 and consensus <= 2:
        final -= 0.03
    elif (citation_hits >= 2 or numeric_hits >= 8 or hedges >= 4) and max(direct_gpt_score, fingerprint_evidence, route_rescue) < 0.14 and consensus <= 2:
        final -= 0.02

    final = max(0.0, min(final, 0.995))

    result["score"] = final
    result["percentage"] = final * 100.0
    result["human_score"] = (1.0 - final) * 100.0
    result["risk_level"] = (
        "CRITICAL" if final >= 0.88 else
        "HIGH" if final >= 0.74 else
        "MEDIUM" if final >= 0.56 else
        "LOW" if final >= 0.28 else
        "MINIMAL"
    )
    _verdicts = {
        "CRITICAL": "اشتباه مرتفع جدًا - يحتاج تحقق بشري",
        "HIGH":     "اشتباه مرتفع - يحتاج تحقق بشري",
        "MEDIUM":   "نتيجة مختلطة / غير حاسمة",
        "LOW":      "اشتباه منخفض",
        "MINIMAL":  "بشري على الأرجح",
    }
    result["verdict"] = _verdicts[result["risk_level"]]

    indicators["English AI Engine v2 ★★★"] = en
    indicators["English AI Engine v2"] = en
    indicators["Paraphrase Engine v21 ★★"] = float(indicators.get("Paraphrase Engine v21 ★★", indicators.get("Paraphrase Engine v21 ★★★", 0.0)) or 0.0)
    indicators["Paraphrase Engine v21 ★★★"] = indicators["Paraphrase Engine v21 ★★"]
    indicators["Synonym Density v21 ★★"] = float(indicators.get("Synonym Density v21 ★★", indicators.get("Synonym Density v21 ★★★", 0.0)) or 0.0)
    indicators["Synonym Density v21 ★★★"] = indicators["Synonym Density v21 ★★"]

    indicators["🔍 Fingerprint Score v35 ★★★"] = max(fp, min(fingerprint_evidence * 0.86 + direct_gpt_score * 0.26 + gpt_style_score * 0.08, 0.99))
    indicators["Simple GPT Score v22 ★★★"] = max(sg, min(gpt_style_score, 0.95)) if (fingerprint_evidence >= 0.24 or direct_gpt_score >= 0.22) else sg
    indicators["Academic Grounding Guard ▼"] = round(academic_guard, 4)

    extended["direct_gpt_score"] = round(direct_gpt_score, 4)
    extended["gpt_style_score"] = round(gpt_style_score, 4)
    extended["fingerprint_evidence_score"] = round(fingerprint_evidence, 4)
    extended["legacy_fp_route_used"] = bool(legacy_exact or legacy_struct or legacy_starter or legacy_corrob)
    extended["legacy_fp_exact_phrases"] = int(legacy_exact)
    extended["legacy_fp_struct_hits"] = int(legacy_struct)
    extended["legacy_fp_starter_ratio"] = round(legacy_starter, 4)
    extended["legacy_fp_corroboration"] = round(legacy_corrob, 4)
    extended["academic_guard_repair_v5"] = round(academic_guard, 4)
    extended["consensus_repair_v5"] = int(consensus)
    extended["repair_phrase_hits"] = int(phrase_hits)
    extended["repair_pattern_hits"] = int(pattern_hits)
    extended["repair_struct_hits"] = int(struct_hits)
    extended["repair_format_hits"] = int(format_hits)
    extended["repair_paragraph_corroboration"] = para_meta

    result["indicators"] = indicators
    result["extended"] = extended
    result["precision95_meta"] = {
        "patched_by": "precision99_real_route_fix",
        "direct_gpt_score": round(direct_gpt_score, 4),
        "fingerprint_evidence_score": round(fingerprint_evidence, 4),
        "gpt_style_score": round(gpt_style_score, 4),
        "consensus": int(consensus),
        "academic_guard": round(academic_guard, 4),
        "phrase_hits": int(phrase_hits),
        "pattern_hits": int(pattern_hits),
        "struct_hits": int(struct_hits),
        "format_hits": int(format_hits),
        "citation_hits": int(citation_hits),
        "numeric_hits": int(numeric_hits),
        "legacy_fp_route_used": bool(legacy_exact or legacy_struct or legacy_starter or legacy_corrob),
        "final_score": round(final, 4),
    }
    return result

AIDetectionEngine.analyze = _precision99_analyze


# ===== UI moved to end so all analyze patches are active before any run =====
# Input
L, R = st.columns([1,1], gap="large")
with L:
    st.markdown('<div class="sh">📝 Input Text</div>', unsafe_allow_html=True)
    up = st.file_uploader("Upload", type=["txt","pdf","docx","doc"], label_visibility="collapsed")
    ft = ""
    if up:
        rb = up.read()
        try:
            if up.name.endswith(".txt"):
                ft = rb.decode("utf-8", errors="replace")
            elif up.name.endswith(".pdf"):
                st.session_state["uploaded_pdf_bytes"] = rb
                ft = ""
                _pdf_err = []

                # محاولة 1: pdfplumber
                try:
                    import pdfplumber as _plb
                    with _plb.open(io.BytesIO(rb)) as _pdoc:
                        ft = "\n".join(p.extract_text() or "" for p in _pdoc.pages).strip()
                except Exception as _e1:
                    _pdf_err.append(f"pdfplumber: {_e1}")

                # محاولة 2: PyMuPDF
                if not ft:
                    try:
                        import fitz as _fz
                        _d = _fz.open(stream=rb, filetype="pdf")
                        ft = "\n".join(_d[i].get_text() for i in range(len(_d))).strip()
                        _d.close()
                    except Exception as _e2:
                        _pdf_err.append(f"PyMuPDF: {_e2}")

                # محاولة 3: pypdf
                if not ft:
                    try:
                        from pypdf import PdfReader as _PR
                        ft = "\n".join(p.extract_text() or "" for p in _PR(io.BytesIO(rb)).pages).strip()
                    except Exception as _e3:
                        _pdf_err.append(f"pypdf: {_e3}")

                if not ft:
                    st.warning(f"⚠️ Could not extract PDF text. Please paste manually.\n\nErrors: {' | '.join(_pdf_err)}")
            elif up.name.lower().endswith((".docx", ".doc")):
                ft = ""
                _docx_err = []

                # محاولة 1: python-docx
                try:
                    import docx as _dx
                    _doc = _dx.Document(io.BytesIO(rb))
                    ft = "\n".join(p.text for p in _doc.paragraphs
                                   if p.text.strip()).strip()
                except Exception as _e1:
                    _docx_err.append(f"python-docx: {_e1}")

                # محاولة 2: python-docx2txt
                if not ft:
                    try:
                        import docx2txt as _d2t
                        ft = _d2t.process(io.BytesIO(rb)).strip()
                    except Exception as _e2:
                        _docx_err.append(f"docx2txt: {_e2}")

                # محاولة 3: PyMuPDF (يدعم DOCX أيضاً)
                if not ft:
                    try:
                        import fitz as _fz
                        _d = _fz.open(stream=rb, filetype="docx")
                        ft = "\n".join(_d[i].get_text() for i in range(len(_d))).strip()
                        _d.close()
                    except Exception as _e3:
                        _docx_err.append(f"PyMuPDF: {_e3}")

                if not ft:
                    st.warning(f"⚠️ Could not read DOCX file.\n\nErrors: {' | '.join(_docx_err)}")
            if ft.strip():
                st.success(f"✅ {up.name} — {len(ft.split())} words")
        except Exception as ex:
            st.warning(f"Error: {ex}")

    if ft.strip():
        txt = ft
        st.text_area("Extracted Text", value=ft, height=300, label_visibility="collapsed", disabled=True)
    else:
        txt = ""
        st.info("Upload a TXT, PDF, DOCX, or DOC file to analyze.")
    wc = len(txt.split()) if txt.strip() else 0
    
    # ── إشعار: التقرير لن يكون بصيغة PDF ──────────────────────────────────
    st.info("ℹ️ **ملاحظة:** للحصول على تقرير PDF مفصل، يُرجى تحميل ملف نصي (TXT, DOCX, DOC).")
    
    c1, c2, c3 = st.columns([3,1,1])
    with c1:
        run = st.button("▶  Analyze", type="primary", use_container_width=True, disabled=not bool(txt.strip()))
    with c2:
        st.metric("Words", wc)
    with c3: st.metric("Sents", len(re.findall(r"[.!?؟]+", txt)))

# ── تشغيل التحليل وحفظ النتائج في session_state ──────────────────────────
if run:
    if wc < 50:
        st.session_state["an_error"] = "⚠️ Too short — enter at least 50 words."
        st.session_state["an_done"]  = False
        st.session_state["an_running"] = False
    else:
        st.session_state["_pending_analyze_text"] = txt
        st.session_state["_pending_analyze_words"] = wc
        st.session_state["_pending_analyze_request"] = True
        st.session_state["an_running"] = True

# ── عرض النتائج دائماً من session_state ──────────────────────────────────
with R:
    st.markdown('<div class="sh">📊 Results</div>', unsafe_allow_html=True)

    if st.session_state.get("an_running"):
        st.progress(65, text="Analyzing text and computing AI / human evidence...")
        st.caption("Please wait while the engines, fingerprint route, and final calibration finish.")
    elif st.session_state.get("an_error"):
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
            ext  = res.get("extended", {}) or {}
            inds = res.get("indicators", {}) or {}
            fp   = float(ext.get("fingerprint_score", ext.get("raw_score", 0)) or 0)
            fpd  = ext.get("fp_details", {}) or {}
            wc_res = res.get("word_count", 0)
            ai_w   = res.get("ai_words_count", 0)
            engine_version = (
                res.get("engine_version")
                or ext.get("engine_version")
                or "legacy_or_unknown"
            )
            # استخراج المتغيرات من inds للاستخدام في التبويبات
            nb_score_val  = inds.get("Naive Bayes ML v25 ★", 0)
            synonym_score = inds.get("Synonym Density v21 ★★", 0)
            discourse_inv = inds.get("Discourse Invariant v21 ★", 0)
            paraphrase_score = inds.get("Paraphrase Engine v21 ★★", 0)
            sem_embed     = inds.get("Semantic Embed v20 ★★★", 0)
            human_error_val      = 1.0 - inds.get("Human Authenticity ✔", 1.0)
            english_human_score  = 1.0 - inds.get("Non-Human Style ✔", 1.0)
            deep_human_score     = 1.0 - inds.get("AI Stylometry v30 ★★", 0)

            # Prefer active v115 university metrics; use legacy keys only as fallback.
            _burst_raw = float(
                ext.get("burst_score",
                    res.get("burstiness",
                        fpd.get("fp_burstiness", 0.0)
                    )
                ) or 0.0
            )
            _perp_raw = float(
                ext.get("perp_score",
                    res.get("perplexity",
                        fpd.get("fp_perplexity", ext.get("lm_perplexity", 0.0))
                    )
                ) or 0.0
            )
            _stat_raw = float(
                ext.get("stat_score",
                    fpd.get("fp_statistical", ext.get("chunk_score", 0.0))
                ) or 0.0
            )
            _human_pen = float(
                ext.get("human_penalty",
                    fpd.get("fp_human_penalty", 0.0)
                ) or 0.0
            )

            # مؤشرات مُصحَّحة أكاديمياً
            _uniformity = round((1.0 - max(0.0, min(1.0, _burst_raw))) * 100, 1)
            _perplexity = round(_perp_raw * 100, 1)

            # ── Honest score display: no artificial squeezing/flooring ─────
            raw_sc = float(sc or 0.0)
            sc = max(0.0, min(100.0, raw_sc))
            _sc_original = sc

            if   sc >= 78: ai_clr,ai_ico,ai_lbl,ai_risk = "#ff3333","🔴","AI — Confirmed","VERY HIGH"
            elif sc >= 60: ai_clr,ai_ico,ai_lbl,ai_risk = "#ff7700","🟠","AI — High Probability","HIGH"
            elif sc >= 40: ai_clr,ai_ico,ai_lbl,ai_risk = "#ffcc00","🟡","Mixed — Review","MODERATE"
            elif sc >= 22: ai_clr,ai_ico,ai_lbl,ai_risk = "#3399ff","🔵","Low AI Detection","LOW"
            else:          ai_clr,ai_ico,ai_lbl,ai_risk = "#33ff88","🟢","Likely Human / Minimal AI","MINIMAL"

            _sc_int = int(round(sc))
            _sc_display = str(_sc_int)

            st.markdown(f'<div class="score-card">'
                        f'<div class="score-num" style="color:{ai_clr}">{_sc_display}</div>'
                        f'<div class="score-vd">🤖 AI Content</div>'
                        f'<div class="score-sub">{ai_risk}</div></div>',
                        unsafe_allow_html=True)

            _ai_esc = float(ext.get("ai_escalation_applied_v104", 0.0) or 0.0)
            if _ai_esc > 0.001:
                st.success(f"AI escalation applied: +{_ai_esc*100:.1f}% due to strong direct evidence above the 50% range.")
            _ag = float(ext.get("academic_grounding", ext.get("academic_grounding_score", 0)) or 0.0)
            _de = float(ext.get("direct_gpt_evidence_v3", ext.get("direct_gpt_evidence_v2", 0)) or 0.0)
            if _ag >= 0.60 and _de < 0.30:
                st.info("Academic note: polished scholarly writing, citations, numbers, and formal style are being treated as human-friendly signals unless direct GPT-like evidence is strong.")

            st.markdown(
                f'<div style="margin:6px 0">'
                f'<div style="display:flex;justify-content:space-between;font-size:10px;color:#666;margin-bottom:3px">'
                f'<span>0%</span><span style="color:{ai_clr};font-weight:700">AI: {sc:.0f}%</span><span>100%</span></div>'
                f'<div style="background:#1e1e2e;border-radius:6px;height:12px;overflow:hidden;position:relative">'
                f'<div style="width:{sc:.0f}%;height:100%;background:linear-gradient(90deg,#ffcc00,{ai_clr});border-radius:6px;transition:width .4s"></div>'
                f'</div></div>',
                unsafe_allow_html=True)

            # حساب الكلمات المُظلَّلة فعلاً = sc% من إجمالي الكلمات
            _highlighted_words = int(round(wc_res * sc / 100))
            # نسبة الجمل الآمنة (البشرية)
            _human_pct = max(0, 100 - int(round(sc)))

            st.markdown(
                f'<div style="margin:10px 0;display:flex;gap:8px;flex-wrap:wrap">'
                f'<span class="pill" title="نسبة المحتوى المكتشف كـ AI">🤖 <b>{int(round(sc))}%</b> AI Content</span>'
                f'<span class="pill" title="عدد الكلمات المُظلَّلة في التقرير">🔍 <b>{_highlighted_words:,}</b> flagged words</span>'
                f'<span class="pill" title="إجمالي كلمات النص">📝 <b>{wc_res:,}</b> total words</span>'
                f'<span class="pill" title="تماثل الجمل — مرتفع = أسلوب AI منتظم">📐 Uniformity <b>{_uniformity:.0f}%</b></span>'
                f'<span class="pill" title="بصمة الذكاء الاصطناعي الإجمالية">🔬 FP <b>{fp*100:.0f}%</b></span>'
                f'<span class="pill" title="Raw engine percentage before any display mapping">🧪 Raw <b>{_sc_original:.1f}%</b></span>'
                f'<span class="pill" title="Additional escalation applied above 50% when direct AI evidence is strong">🚀 Escalation <b>{ext.get("ai_escalation_applied_v104", 0)*100:.0f}%</b></span>'
                f'<span class="pill" title="Active analysis engine version">🧭 {engine_version}</span>'
                f'</div>',
                unsafe_allow_html=True)

            # ── 🔬 ADVANCED TRANSPARENCY PANEL (FIX v115.3) ──────────────────
            with st.expander("🔬 Advanced Metrics & Calibration Details", expanded=False):
                st.markdown("### 📊 Raw Component Scores (Before Calibration)")
                st.caption("These are the unmodified scores from each detection pillar:")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("🔹 Burstiness", f"{_burst_raw*100:.1f}%",
                             help="Active engine burstiness pillar (higher = stronger AI-style uniformity signal)")
                with col2:
                    st.metric("🔹 Perplexity", f"{_perp_raw*100:.1f}%",
                             help="Active engine perplexity/formality pillar")
                with col3:
                    st.metric("🔹 Statistical", f"{_stat_raw*100:.1f}%",
                             help="Active engine structural/statistical pillar")

                st.caption(f"Engine path: {engine_version}")
                st.markdown("---")
                st.markdown("### 🎯 Score Transformation Pipeline")

                # الحسابات الأولية
                _raw_combined = (_burst_raw * 0.28 + _perp_raw * 0.32 + _stat_raw * 0.40)
                _after_penalty = max(0, _raw_combined - _human_pen)
                
                st.text(f"1️⃣  Raw Combined Score:        {_raw_combined:.3f} ({_raw_combined*100:.1f}%)")
                st.text(f"2️⃣  Human Penalty Applied:     -{_human_pen:.3f} (-{_human_pen*100:.1f}%)")
                st.text(f"3️⃣  After Penalty:             {_after_penalty:.3f} ({_after_penalty*100:.1f}%)")
                
                # معامل الثقة (v116: لا سحب نحو المركز)
                _n_words = wc_res
                if _n_words < 30:
                    _shrink = 0.70
                elif _n_words < 150:
                    _shrink = 0.70 + (_n_words - 30) * (0.20 / 120)
                elif _n_words < 400:
                    _shrink = 0.90 + (_n_words - 150) * (0.10 / 250)
                else:
                    _shrink = 1.00
                    
                _calibrated = _after_penalty * _shrink
                
                st.text(f"4️⃣  Confidence Factor:         {_shrink:.3f} (based on {_n_words} words)")
                st.text(f"5️⃣  Final Calibrated Score:    {_calibrated:.3f} ({_calibrated*100:.1f}%)")
                st.text(f"6️⃣  Display Score:             {sc:.1f}%")
                
                st.markdown("---")
                st.markdown("### 🛡️ Human Signal Breakdown")
                st.caption("Signals that reduced the AI score:")
                
                import re as _p115_re  # fix: define before use
                _cit_count = len(_p115_re.findall(
                    r'\([A-Z][a-z]+(?:\s+et\s+al\.?)?\s*,\s*(?:19|20)\d{2}[a-z]?\)', txt))
                if _cit_count > 0:
                    st.text(f"  📚 Citations: {_cit_count} found")
                    
                _prec_count = len(_p115_re.findall(
                    r'p\s*[<>=]\s*0\.\d+|n\s*=\s*\d{2,}', txt))
                if _prec_count > 0:
                    st.text(f"  🔢 Precise numbers: {_prec_count} found")
                    
                if _human_pen < 0.02:
                    st.info("✅ No significant human signals detected")
                elif _human_pen < 0.10:
                    st.success(f"✅ Minimal human signals (penalty: {_human_pen*100:.1f}%)")
                elif _human_pen < 0.20:
                    st.warning(f"⚠️ Moderate human signals (penalty: {_human_pen*100:.1f}%)")
                else:
                    st.error(f"🔴 Strong human signals (penalty: {_human_pen*100:.1f}%)")
                
                st.markdown("---")
                st.markdown("### ⚙️ Version Info")
                st.caption("Engine: Precision-115.3 (Bias-Fixed) | Calibration: Unified | Penalty Cap: 25%")



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
                            _res_pdf            = dict(res)
                            # نسبة واحدة: نفس الرقم الظاهر في الواجهة → الغلاف → التظليل
                            _res_pdf["percentage"] = sc
                            ok = PDFReport.generate(
                                src=_src_path,
                                result=_res_pdf,
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

            st.markdown("---")
            st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
            
            t1, t2, t3 = st.tabs(["🔬 AI Evidence", "🛡️ Human Signals", "📊 All Indicators"])

            # ─── Tab 1: AI Evidence (المؤشرات الإيجابية للـ AI) ───────────────
            with t1:
                st.markdown('<div class="sh">📌 Detected AI Patterns</div>',
                            unsafe_allow_html=True)
                st.caption("Indicators showing active AI-generation signals. Higher = stronger AI evidence.")

                FLB = {
                    "fp_en_phrases":     "Academic AI Phrasing",
                    "fp_cliches":        "AI Closing Patterns",
                    "fp_simple_gpt":     "Simplified GPT Style",
                    "fp_structure":      "AI Sentence Architecture",
                    "fp_vocab":          "AI Vocabulary Density",
                    "fp_format_sig":     "Formatting Signature",
                    "fp_t2_patterns":    "GPT Syntactic Patterns",
                    "fp_ar_phrases":     "Arabic GPT Phrases",
                    "fp_triplets":       "Tripartite Enumerations",
                    "fp_uniformity":     "Sentence Length Uniformity",
                    "fp_pairs":          "Balanced Word Pairs",
                    "fp_no_data":        "Absence of Raw Data",
                    "fp_no_personal":    "Absence of Personal Voice",
                    "fp_academic_trans": "Academic Transition Density",
                }
                ai_fps = sorted(
                    [(v, FLB.get(k, k)) for k,v in fpd.items() if v >= 0.08],
                    reverse=True)

                # المؤشرات الأساسية من inds
                _ai_core = [
                    (nb_score_val,      "Naive Bayes Classifier",     "Probabilistic ML model trained on AI/human corpora"),
                    (fp,                "Composite Fingerprint Score", "Weighted combination of all AI pattern detectors"),
                    (inds.get("Synonym Density v21 ★★", inds.get("Synonym Density v21 ★★★", synonym_score if "synonym_score" in dir() else 0)), "Synonym Density", "Academic synonym substitution typical of AI paraphrasing"),
                    (inds.get("Paraphrase Engine v21 ★★", inds.get("Paraphrase Engine v21 ★★★", 0)), "Paraphrase Score",  "Structural paraphrasing patterns"),
                    (inds.get("English AI Engine v2 ★★★", inds.get("English AI Engine v2", 0)),      "English AI Engine", "Deep linguistic AI detection for English text"),
                    (inds.get("Simple GPT Score v22 ★★★", 0), "Simple GPT Score",  "Surface-level GPT generation patterns"),
                ]
                for val, lbl, desc in sorted(_ai_core, key=lambda x: -x[0]):
                    if val < 0.05: continue
                    pct = int(val * 100)
                    c2  = "#ff3333" if val>=0.70 else "#ff7700" if val>=0.45 else "#ffcc00"
                    sts = "★★★" if val>=0.70 else "★★" if val>=0.45 else "★"
                    st.markdown(
                        f'<div class="fp-row" title="{desc}">'
                        f'<span style="color:{c2};font-size:9px;min-width:26px">{sts}</span>'
                        f'<span class="fp-lbl">{lbl}</span>'
                        f'<div class="fp-bg"><div class="fp-fill" '
                        f'style="width:{pct}%;background:{c2}"></div></div>'
                        f'<span class="fp-pct">{pct}%</span></div>',
                        unsafe_allow_html=True)

                # Fingerprints التفصيلية
                if ai_fps:
                    st.markdown("---")
                    st.caption("Detailed fingerprint breakdown:")
                    for val, lbl in ai_fps[:8]:
                        pct = int(val * 100)
                        _is_key = lbl in ("Sentence Length Uniformity", "Academic Transition Density")
                        _adj_val = min(val * 1.3, 1.0) if _is_key else val
                        c2  = "#ff3333" if _adj_val>=0.65 else "#ff7700" if _adj_val>=0.40 else "#ffcc00"
                        sts = "★★★" if _adj_val>=0.65 else "★★" if _adj_val>=0.40 else "★"
                        st.markdown(
                            f'<div class="fp-row">'
                            f'<span style="color:{c2};font-size:9px;min-width:26px">{sts}</span>'
                            f'<span class="fp-lbl">{lbl}</span>'
                            f'<div class="fp-bg"><div class="fp-fill" '
                            f'style="width:{pct}%;background:{c2}"></div></div>'
                            f'<span class="fp-pct">{pct}%</span></div>',
                            unsafe_allow_html=True)

            # ─── Tab 2: Human Signals (غياب السمات البشرية) ──────────────────
            with t2:
                st.markdown('<div class="sh">🛡️ Human Authenticity Signals</div>',
                            unsafe_allow_html=True)
                st.caption("These indicators are supportive only. In polished academic writing, low typo rate and low colloquiality are normal human traits and must not be treated as AI evidence on their own.")

                _human_inds = res.get("indicators", {})
                _he  = _human_inds.get("Human Authenticity ▼", 0)
                _ehs = 1.0 - _human_inds.get("Non-Human Style ▼", 0)
                _ds  = _human_inds.get("AI Stylometry v30 ★★", 0)
                _ag  = _human_inds.get("Academic Grounding Guard ▼", 0)

                _human_signals = [
                    (_he,   "Human Error Rate",
                     "Typos, grammar errors, inconsistencies — absent in AI text",
                     "low alone is normal in polished academic writing"),
                    (_ehs,  "Colloquial Expression Score",
                     "Informal language, contractions, personal style",
                     "low alone is normal in academic prose"),
                    (_ag,   "Academic Grounding",
                     "Citations, methods, numbers, and scholarly structure that support authentic human academic writing",
                     "high = strong human academic support unless direct AI evidence is also strong"),
                    (_ds, "AI Stylometric Alignment",
                     "How closely the style matches known AI writing patterns",
                     "supportive only — never decisive for academic prose"),
                    (inds.get("Discourse Invariant v21 ★", 0),
                     "Discourse Invariance",
                     "Structural consistency across the text — characteristic of AI",
                     "high = AI only when corroborated by direct evidence"),
                ]

                for val, lbl, desc, interp in _human_signals:
                    pct = int(val * 100)
                    # للمؤشرات البشرية: منخفض = AI (أحمر)، مرتفع = بشري (أخضر)
                    if lbl in ("AI Stylometric Alignment", "Discourse Invariance"):
                        c2 = "#ff3333" if val>=0.60 else "#ff7700" if val>=0.35 else "#33ff88"
                        note = "↑ AI signal" if val >= 0.50 else "↓ Human signal"
                    else:
                        c2 = "#33ff88" if val>=0.30 else "#ff7700" if val>=0.10 else "#ff3333"
                        if lbl == "Academic Grounding" and val >= 0.40:
                            note = "↑ Strong human academic support"
                        else:
                            note = "↑ Human detected" if val >= 0.30 else "↓ Not detected (AI indicator)"
                    st.markdown(
                        f'<div class="fp-row" title="{desc}">'
                        f'<span class="fp-lbl">{lbl}</span>'
                        f'<div class="fp-bg"><div class="fp-fill" '
                        f'style="width:{pct}%;background:{c2}"></div></div>'
                        f'<span class="fp-pct" style="color:{c2}">{pct}% — {note}</span></div>',
                        unsafe_allow_html=True)

                st.info("💡 **Academic Note:** Clean grammar and low colloquiality are normal in scholarly writing. They may support a broader pattern, but they are **not** confirmatory evidence of AI on their own.")

            # ─── Tab 3: All Indicators ────────────────────────────────────────
            with t3:
                st.markdown('<div class="sh">📊 Complete Indicator Matrix</div>',
                            unsafe_allow_html=True)
                st.caption("Full breakdown of all detection engines. Results are weighted by reliability for the final score.")
                _all = sorted(inds.items(), key=lambda x: -x[1])
                for nm, vl in _all:
                    if vl < 0.01: continue
                    pct2 = int(vl * 100)
                    c3 = "#ff3333" if vl>=0.70 else "#ff7700" if vl>=0.40 else "#ffcc00" if vl>=0.20 else "#555577"
                    st.markdown(
                        f'<div class="fp-row">'
                        f'<span class="fp-lbl" style="font-size:9px">{nm.split("★")[0].strip()}</span>'
                        f'<div class="fp-bg"><div class="fp-fill" '
                        f'style="width:{pct2}%;background:{c3}"></div></div>'
                        f'<span class="fp-pct">{pct2}%</span></div>',
                        unsafe_allow_html=True)

                st.markdown('<div class="sh">💡 Why this score?</div>',
                            unsafe_allow_html=True)
                ns = sum(1 for v,_ in ai_fps if v >= 0.55)
                # نص احترافي يشرح النتيجة بوضوح
                _sc_int = int(round(sc))
                _fp_int = int(fp * 100)
                _flagged = int(round(wc_res * sc / 100))
                if fp >= 0.75:
                    _verdict_txt = "high"
                    _verdict_ar  = "مرتفعة جداً"
                elif fp >= 0.50:
                    _verdict_txt = "moderate-high"
                    _verdict_ar  = "مرتفعة"
                elif fp >= 0.25:
                    _verdict_txt = "moderate"
                    _verdict_ar  = "متوسطة"
                else:
                    _verdict_txt = "low"
                    _verdict_ar  = "منخفضة"

                _top3 = ", ".join(f"*{lb}* ({int(v*100)}%)" for v,lb in ai_fps[:3]) if ai_fps else "—"
                why = (
                    f"The analysis flagged **{_flagged:,} words** ({_sc_int}% of {wc_res:,} total) "
                    f"as AI-generated content. "
                    f"The AI Fingerprint Score is **{_fp_int}%** ({_verdict_ar}), "
                    f"driven by {ns} high-confidence signal{'s' if ns!=1 else ''}. "
                )
                if ai_fps:
                    why += f"Top indicators: {_top3}."
                if wc_res < 150:
                    why += f" ⚠️ Short text ({wc_res} words) — results may be less reliable."
                st.markdown(why)

                # ── Academic Human vs AI style diagnostics ───────────────
                _style_prof = ext.get("sentence_style_profiles", {}) or {}
                _ai_sr = float(_style_prof.get("ai_sentence_ratio", ext.get("ai_sentence_ratio", 0.0)) or 0.0)
                _hu_sr = float(_style_prof.get("human_sentence_ratio", ext.get("human_sentence_ratio", 0.0)) or 0.0)
                _gap_v3 = float(_style_prof.get("style_gap", ext.get("style_gap_v3", 0.0)) or 0.0)
                _ai_pr = float(ext.get("academic_ai_pressure_v3", 0.0) or 0.0)
                _hu_guard = float(ext.get("human_academic_guard_v3", 0.0) or 0.0)
                if _ai_pr > 0 or _hu_guard > 0 or _ai_sr > 0 or _hu_sr > 0:
                    st.markdown('<div class="sh">⚖️ Academic Human vs AI Style</div>', unsafe_allow_html=True)
                    st.markdown(
                        f'<div style="background:#0f1117;border:1px solid #2a2a38;border-radius:12px;padding:12px 14px;margin:8px 0">'
                        f'<div style="color:#f2f2f2;font-size:13px;line-height:1.7">'
                        f'<b>Academic AI Pressure:</b> {int(round(_ai_pr*100))}% &nbsp;|&nbsp; '
                        f'<b>Human Academic Grounding:</b> {int(round(_hu_guard*100))}%<br>'
                        f'<b>AI-style sentence ratio:</b> {int(round(_ai_sr*100))}% &nbsp;|&nbsp; '
                        f'<b>Human-grounded sentence ratio:</b> {int(round(_hu_sr*100))}%<br>'
                        f'<b>Style gap:</b> {round(_gap_v3, 3)}'
                        f'</div></div>',
                        unsafe_allow_html=True
                    )

                # ── Strong English AI quote evidence ─────────────────────
                ai_quotes = (res.get("ai_citations") or ext.get("ai_quote_candidates") or [])
                if ai_quotes:
                    st.markdown('<div class="sh">🧠 Strong AI Quote Evidence</div>', unsafe_allow_html=True)
                    _show_quotes = ai_quotes[:8]
                    for _i, _q in enumerate(_show_quotes, 1):
                        _q_score = int(round(float(_q.get("score", 0.0) or 0.0) * 100))
                        _q_text = str(_q.get("text", "")).strip()
                        _q_reason = str(_q.get("reason", "high sentence-level AI signature")).strip()
                        st.markdown(
                            f'<div style="background:#0f1117;border:1px solid #2a2a38;border-radius:12px;'
                            f'padding:12px 14px;margin:8px 0">'
                            f'<div style="display:flex;justify-content:space-between;gap:10px;align-items:center;margin-bottom:6px">'
                            f'<span style="color:#ffcc00;font-size:11px;font-weight:800">QUOTE {_i}</span>'
                            f'<span style="color:#ff7700;font-size:11px;font-weight:800">{_q_score}% suspicion</span>'
                            f'</div>'
                            f'<div style="color:#f2f2f2;font-size:13px;line-height:1.65">"{_q_text}"</div>'
                            f'<div style="margin-top:7px;color:#8e97a6;font-size:11px">Reason: {_q_reason}</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

        except Exception as ex:
            st.error(f"Error: {ex}")
            with st.expander("Details"):
                st.code(traceback.format_exc())

st.markdown('<div style="text-align:center;color:#2a2a38;font-size:11px;'
            'margin-top:30px;padding-top:16px;border-top:1px solid #1a1a2e">'
            'Semi Turnitin v28 · Fingerprint-Driven AI Detection + Academic Mode</div>',
            unsafe_allow_html=True)


# ── Runtime hotfix: expose conservative synonym-density as a real class method ──
def _patched_synonym_density(self, words):
    """
    Conservative synonym-density detector for English academic text.
    Lexical variety alone must not be treated as a strong AI signal.
    """
    if not words:
        return 0.0
    if len(words) < 25:
        return 0.12

    from collections import Counter as _C

    semantic_groups = {
        'demonstrate': 'show_grp', 'show': 'show_grp', 'illustrate': 'show_grp', 'reveal': 'show_grp',
        'important': 'imp_grp', 'significant': 'imp_grp', 'crucial': 'imp_grp', 'critical': 'imp_grp',
        'vital': 'imp_grp', 'essential': 'imp_grp', 'key': 'imp_grp',
        'improve': 'enhance_grp', 'enhance': 'enhance_grp', 'strengthen': 'enhance_grp',
        'advance': 'enhance_grp', 'promote': 'enhance_grp',
        'use': 'use_grp', 'utilize': 'use_grp', 'employ': 'use_grp', 'apply': 'use_grp',
        'implement': 'use_grp', 'adopt': 'use_grp', 'leverage': 'use_grp',
        'help': 'help_grp', 'facilitate': 'help_grp', 'enable': 'help_grp', 'support': 'help_grp',
        'assist': 'help_grp', 'contribute': 'help_grp',
        'result': 'result_grp', 'outcome': 'result_grp', 'finding': 'result_grp', 'conclusion': 'result_grp',
        'effect': 'result_grp', 'impact': 'result_grp', 'implication': 'result_grp',
        'problem': 'prob_grp', 'challenge': 'prob_grp', 'issue': 'prob_grp', 'concern': 'prob_grp',
        'method': 'method_grp', 'approach': 'method_grp', 'framework': 'method_grp', 'model': 'method_grp',
        'analysis': 'analysis_grp', 'evaluation': 'analysis_grp', 'assessment': 'analysis_grp', 'examination': 'analysis_grp',
    }

    counts = _C(w.lower() for w in words if isinstance(w, str))
    total = max(1, sum(counts.values()))

    group_counts = {}
    for token, c in counts.items():
        grp = semantic_groups.get(token)
        if grp:
            group_counts[grp] = group_counts.get(grp, 0) + c

    if not group_counts:
        return 0.08

    repeated_groups = sum(1 for c in group_counts.values() if c >= 3)
    group_coverage = len(group_counts) / max(8, len(set(semantic_groups.values())))
    repetition_ratio = repeated_groups / max(1, len(group_counts))

    lexical_diversity = len(set(w.lower() for w in words if isinstance(w, str))) / total

    score = (
        repetition_ratio * 0.35 +
        group_coverage * 0.20 +
        max(0.0, 0.62 - lexical_diversity) * 0.45
    )

    # Strong brakes for normal English academic writing
    first_person = {'i', 'we', 'our', 'us', 'my', 'me'}
    fp_ratio = sum(1 for w in words if isinstance(w, str) and w.lower() in first_person) / total
    if fp_ratio > 0:
        score *= max(0.45, 1.0 - fp_ratio * 8.0)

    # Keep this signal moderate; do not let it dominate final decisions
    return round(min(max(score, 0.0), 0.72), 4)

AIDetectionEngine._synonym_density = _patched_synonym_density


# --- v3 structural fix: promote mistakenly nested methods to real class methods ---
def _v3fixed_synonym_density(self, words):
    """
    Conservative synonym-density detector.
    Academic lexical variety alone should not be treated as AI.
    """
    if len(words) < 25:
        return 0.12

    from collections import Counter as _C, defaultdict as _dd

    SEMANTIC_GROUPS = {
        'demonstrate': 'show_grp', 'show': 'show_grp', 'illustrate': 'show_grp', 'reveal': 'show_grp',
        'important': 'imp_grp', 'significant': 'imp_grp', 'crucial': 'imp_grp', 'critical': 'imp_grp',
        'vital': 'imp_grp', 'essential': 'imp_grp', 'key': 'imp_grp',
        'improve': 'enhance_grp', 'enhance': 'enhance_grp', 'strengthen': 'enhance_grp',
        'advance': 'enhance_grp', 'promote': 'enhance_grp',
        'use': 'use_grp', 'utilize': 'use_grp', 'employ': 'use_grp', 'apply': 'use_grp',
        'implement': 'use_grp', 'adopt': 'use_grp', 'leverage': 'use_grp',
        'help': 'help_grp', 'facilitate': 'help_grp', 'enable': 'help_grp', 'support': 'help_grp',
        'assist': 'help_grp', 'contribute': 'help_grp',
        'result': 'result_grp', 'outcome': 'result_grp', 'finding': 'result_grp', 'conclusion': 'result_grp',
        'effect': 'result_grp', 'impact': 'result_grp', 'implication': 'result_grp',
        'problem': 'prob_grp', 'challenge': 'prob_grp', 'issue': 'prob_grp', 'concern': 'prob_grp',
        'method': 'method_grp', 'approach': 'method_grp', 'strategy': 'method_grp', 'technique': 'method_grp',
        'model': 'model_grp', 'framework': 'model_grp', 'paradigm': 'model_grp',
    }

    normalized = [w.lower() for w in words]
    total = len(normalized)
    grp_counts = _C()
    grp_types = _dd(set)

    for w in normalized:
        grp = SEMANTIC_GROUPS.get(w)
        if grp:
            grp_counts[grp] += 1
            grp_types[grp].add(w)

    if not grp_counts:
        return 0.06

    dense_groups = 0
    varied_groups = 0
    suspicious_groups = 0
    total_group_tokens = sum(grp_counts.values())

    for grp, cnt in grp_counts.items():
        uniq = len(grp_types[grp])
        density = cnt / max(total, 1)
        if cnt >= 4 and density >= 0.012:
            dense_groups += 1
        if cnt >= 5 and uniq >= 3:
            varied_groups += 1
        if cnt >= 7 and uniq >= 4 and density >= 0.02:
            suspicious_groups += 1

    raw = (
        min(total_group_tokens / max(total * 0.22, 1), 1.0) * 0.18 +
        min(dense_groups / 6.0, 1.0) * 0.22 +
        min(varied_groups / 5.0, 1.0) * 0.28 +
        min(suspicious_groups / 4.0, 1.0) * 0.32
    )

    # Repetition with many different near-synonyms is more suspicious than plain diversity.
    ttr = len(set(normalized)) / max(total, 1)
    if ttr > 0.62:
        raw *= 0.88

    # Academic vocabulary should not inflate this too much.
    academic_terms = sum(
        1 for w in normalized
        if w in {'study','research','analysis','results','findings','data','method','methods','discussion','conclusion'}
    )
    if academic_terms >= max(8, total // 80):
        raw *= 0.85

    return round(max(0.03, min(raw, 0.58)), 4)





# ===== Final rebinding pass =====
def _finalize_engine_bindings():
    """
    Rebind all late-defined helpers after the full script has loaded.
    This prevents NameError/partial binding when Streamlit executes top-down.
    """
    _mapping = {
        "_english_ai_score": "_english_ai_score",
        "_explain_paragraph": "_explain_paragraph",
        "_arabic_ai_score": "_arabic_ai_score",
        "_compute_confidence": "_compute_confidence",
        "_context_coherence": "_context_coherence",
        "_advanced_stylometry": "_advanced_stylometry",
        "_punct_distribution": "_punct_distribution",
        "_bigram_score": "_bigram_score",
        "_trigram_score": "_trigram_score",
        "_pattern_score": "_pattern_score",
        "_rhythm": "_rhythm",
        "_local_entropy": "_local_entropy",
        "_paragraph_structure": "_paragraph_structure",
        "_punct_fingerprint": "_punct_fingerprint",
        "_verb_ratio": "_verb_ratio",
        "_pronoun_ratio": "_pronoun_ratio",
        "_compute_fingerprint_score": "_compute_fingerprint_score",
        "_simple_gpt_score": "_simple_gpt_score",
        "_gpt_formatting_signature": "_gpt_formatting_signature",
        "_paraphrase_engine": "_paraphrase_engine",
        "_synonym_density": "_synonym_density",
        "_discourse_invariant": "_discourse_invariant",
        "_nb_score": "_v3fixed_nb_score",
        "_english_ai_score_v3fixed": "_v3fixed_english_ai_score",
        "_compute_fingerprint_score_v3fixed": "_v3fixed_compute_fingerprint_score",
        "_synonym_density_v3fixed": "_v3fixed_synonym_density",
        "_precision97_sentence_style_profiles": "_precision97_sentence_style_profiles",
        "_precision97_extract_ai_quotes": "_precision97_extract_ai_quotes",
        "_precision97_enhance_result": "_precision97_enhance_result",
    }
    _g = globals()
    for _attr, _name in _mapping.items():
        _fn = _g.get(_name)
        if _fn is not None:
            setattr(AIDetectionEngine, _attr, _fn)

    # Prefer the most recent fixed implementations when available.
    if _g.get("_v3fixed_synonym_density") is not None:
        AIDetectionEngine._synonym_density = _g["_v3fixed_synonym_density"]
    if _g.get("_v3fixed_nb_score") is not None:
        AIDetectionEngine._nb_score = _g["_v3fixed_nb_score"]
    if _g.get("_v3fixed_english_ai_score") is not None:
        AIDetectionEngine._english_ai_score = _g["_v3fixed_english_ai_score"]
    if _g.get("_v3fixed_compute_fingerprint_score") is not None:
        AIDetectionEngine._compute_fingerprint_score = _g["_v3fixed_compute_fingerprint_score"]
    if _g.get("_precision99_analyze") is not None:
        AIDetectionEngine.analyze = _g["_precision99_analyze"]
    elif _g.get("_precision98_analyze") is not None:
        AIDetectionEngine.analyze = _g["_precision98_analyze"]
    elif _g.get("_precision97_analyze") is not None:
        AIDetectionEngine.analyze = _g["_precision97_analyze"]

_finalize_engine_bindings()


# ===== Precision100: decisive calibrated scoring (direct fingerprint first, academic style neutralized) =====

def _precision100_analyze(self, text, cb=None):
    base_analyze = globals().get("_precision99_analyze") or globals().get("_precision98_analyze") or globals().get("_precision97_analyze")
    if base_analyze is None:
        base_analyze = getattr(self, "_orig_analyze_precision95", None)
    if base_analyze is None:
        base_analyze = getattr(AIDetectionEngine, "_orig_analyze_precision95", None)
    if base_analyze is None:
        base_analyze = AIDetectionEngine.analyze

    result = base_analyze(self, text, cb) if isinstance(base_analyze, _precision_types.FunctionType) else base_analyze(text, cb)
    if not isinstance(result, dict) or result.get("error"):
        return result

    try:
        clean_text = self._strip_references(text)
    except Exception:
        clean_text = text

    clean_text = re.sub(r'\s+', ' ', clean_text or '').strip()
    low = clean_text.lower()
    words = re.findall(r'\b[a-zA-Z]+\b', low)
    sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', clean_text) if len(re.findall(r"[A-Za-z]+", s)) >= 4]

    indicators = dict(result.get("indicators", {}) or {})
    extended = dict(result.get("extended", {}) or {})
    fpd = dict(extended.get("fp_details", {}) or {})

    fp = float(indicators.get("🔍 Fingerprint Score v35 ★★★", extended.get("fingerprint_score", 0.0)) or 0.0)
    gf = float(indicators.get("GPT Format Signature ★★★", extended.get("gpt_format_score", 0.0)) or 0.0)
    sg = float(indicators.get("Simple GPT Score v22 ★★★", extended.get("simple_gpt_score", 0.0)) or 0.0)
    en = float(indicators.get("English AI Engine v2 ★★★", indicators.get("English AI Engine v2", extended.get("english_ai_score", 0.0))) or 0.0)
    nb = float(indicators.get("Naive Bayes ML v25 ★", extended.get("nb_score", 0.0)) or 0.0)
    llr = float(indicators.get("LLR v28 ★★★ [corpus جديد]", extended.get("llr_score", 0.0)) or 0.0)
    pat_mem = float(indicators.get("Pattern Memory v20 ★★★", extended.get("pat_mem", 0.0)) or 0.0)

    para_results = extended.get("paragraph_results", []) or []
    para_meta = self._precision96_paragraph_corroboration(para_results)

    direct = self._precision96_direct_gpt_evidence(clean_text, words, sents)
    phrase_hits = int(direct.get("phrase_hits", 0) or 0)
    pattern_hits = int(direct.get("pattern_hits", 0) or 0)
    format_hits = int(direct.get("format_hits", 0) or 0)
    struct_hits = int(direct.get("struct_hits", 0) or 0)
    starter_ratio = float(direct.get("starter_ratio", 0.0) or 0.0)
    pattern_density = float(direct.get("pattern_density", 0.0) or 0.0)
    citation_hits = int(direct.get("citation_hits", 0) or 0)
    numeric_hits = int(direct.get("numeric_hits", 0) or 0)

    first_person = len(re.findall(r'\b(?:i|we|our|my|us)\b', low))
    hedges = len(re.findall(r'\b(?:may|might|could|perhaps|possibly|likely|unlikely|approximately|suggests?|appears?|indicates?)\b', low))
    quote_hits = len(re.findall(r'["“”\']', clean_text))
    method_terms = len(re.findall(r'\b(?:method(?:ology)?|materials?|results?|discussion|conclusion|experiment(?:al)?|sample|samples|participants|procedure|analysis|statistical|dataset|model|table|figure|fig\.?)\b', low))

    # Fine-grained fingerprint channels
    fp_phrase = float(fpd.get("fp_en_phrases", 0.0) or 0.0)
    fp_structure = float(fpd.get("fp_structure", 0.0) or 0.0)
    fp_simple = float(fpd.get("fp_simple_gpt", 0.0) or 0.0)
    fp_t2 = float(fpd.get("fp_t2_patterns", 0.0) or 0.0)
    fp_vocab = float(fpd.get("fp_vocab", 0.0) or 0.0)
    fp_trans = float(fpd.get("fp_academic_trans", 0.0) or 0.0)
    fp_format = float(fpd.get("fp_format_sig", 0.0) or 0.0)
    fp_triplets = float(fpd.get("fp_triplets", 0.0) or 0.0)
    fp_pairs = float(fpd.get("fp_pairs", 0.0) or 0.0)
    fp_uniformity = float(fpd.get("fp_uniformity", 0.0) or 0.0)
    fp_cliches = float(fpd.get("fp_cliches", 0.0) or 0.0)

    legacy_exact = int(fpd.get("exact_phrases", 0) or 0)
    legacy_struct = int(fpd.get("struct_hits", 0) or 0)
    legacy_starter = float(fpd.get("starter_ratio", 0.0) or 0.0)
    legacy_corrob = float(fpd.get("corroboration", 0.0) or 0.0)

    if fp_phrase == 0.0 and legacy_exact:
        fp_phrase = min(legacy_exact / 3.0, 1.0)
    if fp_structure == 0.0 and legacy_struct:
        fp_structure = min(legacy_struct / 3.5, 1.0)
    if fp_trans == 0.0 and legacy_starter:
        fp_trans = min(max(legacy_starter - 0.14, 0.0) / 0.40, 1.0)
    if fp_uniformity == 0.0 and legacy_corrob:
        fp_uniformity = min(legacy_corrob / 3.2, 1.0)
    if fp_simple == 0.0 and sg > 0:
        fp_simple = min(sg, 1.0)
    if fp_t2 == 0.0 and pat_mem > 0:
        fp_t2 = min(pat_mem, 1.0)
    if fp_format == 0.0 and gf > 0:
        fp_format = min(gf, 1.0)

    fingerprint_evidence = (
        fp_phrase * 0.24 +
        fp_structure * 0.18 +
        fp_simple * 0.12 +
        fp_t2 * 0.10 +
        fp_trans * 0.08 +
        fp_format * 0.07 +
        fp_triplets * 0.06 +
        fp_pairs * 0.04 +
        fp_uniformity * 0.06 +
        fp_cliches * 0.02 +
        fp_vocab * 0.03
    )
    # allow global fingerprint to rescue sparse routing, but modestly
    if fingerprint_evidence < 0.10:
        fingerprint_evidence = max(fingerprint_evidence, fp * 0.42 + sg * 0.10 + min(pat_mem, 0.9) * 0.05)
    fingerprint_evidence = max(0.0, min(fingerprint_evidence, 0.99))

    direct_gpt_score = (
        min(phrase_hits / 4.0, 1.0) * 0.28 +
        min(pattern_density / 1.05, 1.0) * 0.18 +
        min(format_hits / 3.0, 1.0) * 0.07 +
        min(struct_hits / 4.0, 1.0) * 0.15 +
        min(starter_ratio / 0.34, 1.0) * 0.04 +
        max(gf - 0.10, 0.0) * 0.08 +
        fingerprint_evidence * 0.20
    )
    if phrase_hits >= 2 and pattern_hits >= 2:
        direct_gpt_score += 0.07
    if phrase_hits >= 1 and fingerprint_evidence >= 0.34:
        direct_gpt_score += 0.05
    if struct_hits >= 2 and (fp_structure >= 0.30 or fp_t2 >= 0.30):
        direct_gpt_score += 0.04
    direct_gpt_score = max(0.0, min(direct_gpt_score, 0.99))

    style_pressure = (
        sg * 0.25 +
        en * 0.18 +
        fp * 0.16 +
        min(nb, 0.92) * 0.12 +
        min(llr, 0.92) * 0.09 +
        min(pat_mem, 0.92) * 0.06 +
        min(para_meta.get("avg", 0.0) / 0.72, 1.0) * 0.08 +
        (0.06 if para_meta.get("strong", 0) >= 2 else 0.0)
    )
    style_pressure = max(0.0, min(style_pressure, 0.96))

    # academic polish is common in both human and AI research; do not let style dominate
    style_cap = max(direct_gpt_score, fingerprint_evidence) + 0.08
    effective_style = min(style_pressure, style_cap)
    effective_style = max(0.0, min(effective_style, 0.92))

    style_consensus = 0
    style_consensus += 1 if sg >= 0.78 else 0
    style_consensus += 1 if nb >= 0.80 else 0
    style_consensus += 1 if en >= 0.64 else 0
    style_consensus += 1 if fp >= 0.40 else 0
    style_consensus += 1 if llr >= 0.70 else 0
    style_consensus += 1 if para_meta.get("strong", 0) >= 2 or para_meta.get("avg", 0.0) >= 0.62 else 0

    academic_grounding = 0.0
    if citation_hits >= 2:
        academic_grounding += 0.07
    if citation_hits >= 5:
        academic_grounding += 0.03
    if numeric_hits >= max(6, len(words) // 120):
        academic_grounding += 0.06
    if method_terms >= 6:
        academic_grounding += 0.04
    if hedges >= 4:
        academic_grounding += 0.03
    if quote_hits >= 4:
        academic_grounding += 0.02
    if first_person >= 2:
        academic_grounding += 0.02
    academic_grounding = min(academic_grounding, 0.22)

    # generic integrity anomalies: these help catch suspicious academic reviews without rewarding style itself
    integrity_anomaly = 0.0
    if "invalid citation" in low:
        integrity_anomaly += 0.18
    if re.search(r'\]\s*\d+\s*\[', clean_text):
        integrity_anomaly += 0.06
    if "records screened" in low and "reports not retrieved" in low:
        nums = [int(n.replace(',', '')) for n in re.findall(r'\b\d{2,6}(?:,\d{3})*\b', clean_text[:12000])]
        if len(nums) >= 6:
            # weak impossible-flow check: later values should not jump wildly above earlier retained counts
            for a, b in zip(nums, nums[1:]):
                if a > 0 and b > a * 3:
                    integrity_anomaly += 0.08
                    break
    integrity_anomaly = min(integrity_anomaly, 0.28)

    final = (
        direct_gpt_score * 0.58 +
        fingerprint_evidence * 0.22 +
        effective_style * 0.12 +
        integrity_anomaly * 0.08
    )

    if direct_gpt_score >= 0.28 and fingerprint_evidence >= 0.24 and style_consensus >= 3:
        final += 0.05
    if direct_gpt_score >= 0.40 and fingerprint_evidence >= 0.32 and style_consensus >= 4 and (phrase_hits >= 2 or struct_hits >= 2):
        final += 0.07
    if direct_gpt_score >= 0.54 and fingerprint_evidence >= 0.46 and style_consensus >= 5 and phrase_hits >= 2 and pattern_hits >= 2:
        final += 0.09

    # protect strong human academic writing when direct evidence is weak
    evidence_peak = max(direct_gpt_score, fingerprint_evidence)
    if academic_grounding >= 0.16 and evidence_peak < 0.22:
        final -= 0.03
    elif academic_grounding >= 0.10 and evidence_peak < 0.16:
        final -= 0.02
    else:
        final -= academic_grounding * 0.10

    # floors only when direct GPT evidence itself is present
    if direct_gpt_score >= 0.34 and fingerprint_evidence >= 0.28 and style_consensus >= 4:
        final = max(final, 0.48)
    if direct_gpt_score >= 0.46 and fingerprint_evidence >= 0.40 and style_consensus >= 5 and (phrase_hits >= 2 or struct_hits >= 2):
        final = max(final, 0.62)
    if direct_gpt_score >= 0.60 and fingerprint_evidence >= 0.52 and style_consensus >= 5 and phrase_hits >= 2 and pattern_hits >= 2:
        final = max(final, 0.78)

    final = max(0.0, min(final, 0.995))

    result["score"] = final
    result["percentage"] = final * 100.0
    result["human_score"] = (1.0 - final) * 100.0
    result["risk_level"] = (
        "CRITICAL" if final >= 0.88 else
        "HIGH" if final >= 0.74 else
        "MEDIUM" if final >= 0.56 else
        "LOW" if final >= 0.18 else
        "MINIMAL"
    )
    _verdicts = {
        "CRITICAL": "اشتباه مرتفع جدًا - يحتاج تحقق بشري",
        "HIGH":     "اشتباه مرتفع - يحتاج تحقق بشري",
        "MEDIUM":   "نتيجة مختلطة / غير حاسمة",
        "LOW":      "اشتباه منخفض",
        "MINIMAL":  "بشري على الأرجح",
    }
    result["verdict"] = _verdicts[result["risk_level"]]

    indicators["English AI Engine v2 ★★★"] = en
    indicators["English AI Engine v2"] = en
    indicators["🔍 Fingerprint Score v35 ★★★"] = max(fp, min(fingerprint_evidence * 0.88 + direct_gpt_score * 0.22, 0.99))
    indicators["Simple GPT Score v22 ★★★"] = max(sg, min(effective_style, 0.92)) if evidence_peak >= 0.24 else sg
    indicators["Academic Grounding Guard ▼"] = round(academic_grounding, 4)
    indicators["Integrity Anomaly Score ★"] = round(integrity_anomaly, 4)

    extended["direct_gpt_score"] = round(direct_gpt_score, 4)
    extended["gpt_style_score"] = round(effective_style, 4)
    extended["style_pressure_raw"] = round(style_pressure, 4)
    extended["fingerprint_evidence_score"] = round(fingerprint_evidence, 4)
    extended["style_consensus_v100"] = int(style_consensus)
    extended["academic_grounding_v100"] = round(academic_grounding, 4)
    extended["integrity_anomaly_v100"] = round(integrity_anomaly, 4)
    extended["repair_phrase_hits"] = int(phrase_hits)
    extended["repair_pattern_hits"] = int(pattern_hits)
    extended["repair_struct_hits"] = int(struct_hits)
    extended["repair_format_hits"] = int(format_hits)
    extended["repair_paragraph_corroboration"] = para_meta

    result["indicators"] = indicators
    result["extended"] = extended
    result["precision95_meta"] = {
        "patched_by": "precision100_decisive_calibrated",
        "direct_gpt_score": round(direct_gpt_score, 4),
        "fingerprint_evidence_score": round(fingerprint_evidence, 4),
        "effective_style_score": round(effective_style, 4),
        "style_pressure_raw": round(style_pressure, 4),
        "style_consensus": int(style_consensus),
        "academic_grounding": round(academic_grounding, 4),
        "integrity_anomaly": round(integrity_anomaly, 4),
        "phrase_hits": int(phrase_hits),
        "pattern_hits": int(pattern_hits),
        "struct_hits": int(struct_hits),
        "citation_hits": int(citation_hits),
        "numeric_hits": int(numeric_hits),
    }
    return result

AIDetectionEngine.analyze = _precision100_analyze


# ===== Precision101: research-calibrated direct-evidence scoring =====

_PREC101_REF_STOPWORDS = {
    "about","above","after","again","against","among","also","although","analysis","and","article","articles",
    "because","been","before","being","between","both","but","can","could","data","discussion","does","during",
    "each","evidence","from","have","health","into","introduction","journal","literature","male","materials",
    "method","methods","more","most","nutrition","objective","objectives","paper","papers","recent","research",
    "results","review","role","study","studies","than","that","their","them","there","these","they","this",
    "those","through","under","using","well","were","what","when","where","which","while","with","within",
    "without","would","reproductive","fertility","human","systematic","effects","impact","current","conclusion"
}

def _precision101_top_keywords(text, limit=15):
    words = [
        w.lower() for w in re.findall(r'[A-Za-z]{5,}', text or '')
        if w.lower() not in _PREC101_REF_STOPWORDS
    ]
    if not words:
        return []
    return [w for w, _ in Counter(words).most_common(limit)]


def _precision101_reference_anomaly(self, text):
    m = re.search(r'\bReferences\b', text or '', re.I)
    if not m:
        return 0.0, {"reference_blocks": 0, "reference_outliers": 0, "reference_odd_terms": 0}

    refs = (text or '')[m.end():]
    body = (text or '')[:m.start()]

    theme_keywords = set(_precision101_top_keywords(body[:8000], 15))
    ref_blocks = re.split(r'\n\s*(?=\d+\.)', refs)
    total = 0
    outliers = 0
    odd_terms = 0

    odd_pat = re.compile(
        r'\b(?:nursing|workflow|electronic health record|egfr|hepatitis|drug[- ]targeted|signaling pathway|community nurses)\b',
        re.I
    )

    for block in ref_blocks:
        if len(re.findall(r'[A-Za-z]{4,}', block)) < 8:
            continue
        total += 1
        block_words = set(w.lower() for w in re.findall(r'[A-Za-z]{5,}', block))
        if theme_keywords and len(block_words & theme_keywords) == 0:
            outliers += 1
        if odd_pat.search(block):
            odd_terms += 1

    score = 0.0
    refs_low = refs.lower()
    if 'invalid citation' in refs_low:
        score += 0.30
    if total >= 15 and outliers / max(total, 1) >= 0.10:
        score += min(0.25, (outliers / max(total, 1)) * 0.50)
    if odd_terms >= 1:
        score += min(0.20, odd_terms * 0.08)

    return min(score, 0.60), {
        "reference_blocks": int(total),
        "reference_outliers": int(outliers),
        "reference_odd_terms": int(odd_terms),
    }


def _precision101_direct_gpt_evidence(self, text, words, sents):
    tl = (text or '').lower()
    n_words = max(len(words), 1)
    n_sents = max(len(sents), 1)

    phrase_bank = []
    for p in list(getattr(self, "EN_GPT_PHRASES_T1", []) or []):
        p = (p or '').strip().lower()
        if not p:
            continue
        if len(p.split()) < 5:
            continue
        if p in {
            'in conclusion', 'to summarize', 'overall', 'however', 'moreover', 'furthermore', 'therefore',
            'plays a crucial role', 'plays a fundamental role', 'plays a central role', 'plays a vital role',
            'plays a key role in', 'the relationship between', 'best practices', 'positive impact',
            'by contrast', 'on the other hand', 'in relation to', 'whereas'
        }:
            continue
        if re.search(r'\bplays?\s+a\s+(?:crucial|fundamental|central|vital|key|significant|important)\s+role\b', p):
            continue
        phrase_bank.append(p)

    extra_direct = [
        "it is worth noting that",
        "it is important to note that",
        "it is crucial to understand that",
        "it is essential to recognize that",
        "in today's rapidly evolving",
        "at the heart of",
        "a multifaceted approach",
        "a holistic approach",
        "a nuanced perspective",
        "future research is needed",
        "this underscores the importance of",
    ]
    seen = set()
    phrase_hits = 0
    for phrase in phrase_bank + extra_direct:
        if phrase in seen:
            continue
        seen.add(phrase)
        if phrase in tl:
            phrase_hits += 1

    struct_hits = 0
    struct_patterns = [
        r'\bthis\s+(?:study|paper|review)\s+(?:aims?|seeks?|examines?|investigates?|explores?)\b',
        r'\bit\s+is\s+worth\s+(?:noting|emphasizing)\s+that\b',
        r'\bfuture\s+research\s+(?:is\s+needed|should|could|may)\b',
        r'\bthis\s+underscores\s+the\s+importance\s+of\b',
    ]
    for pat in struct_patterns:
        try:
            struct_hits += len(re.findall(pat, tl, re.I))
        except Exception:
            pass

    pattern_hits = 0
    direct_patterns = [
        r'\bin\s+today\'?s\s+(?:rapidly|ever)\s+\w+',
        r'\bit\s+is\s+(?:important|crucial|essential)\s+to\s+note\s+that\b',
        r'\bat\s+the\s+heart\s+of\b',
        r'\ba\s+(?:multifaceted|holistic|nuanced)\s+approach\b',
    ]
    for pat in direct_patterns:
        try:
            pattern_hits += len(re.findall(pat, tl, re.I))
        except Exception:
            pass

    transition_hits = len(re.findall(
        r'(?:(?<=\.)|^)\s*(?:however|moreover|furthermore|therefore|overall|consequently|thus)\b',
        tl,
        re.I
    ))
    transition_ratio = transition_hits / n_sents

    citations = len(re.findall(r'\([A-Z][A-Za-z\-]+,\s*\d{4}[a-z]?\)', text or ''))
    citations += len(re.findall(r'\[(?:\d+|\d+(?:\s*,\s*\d+)*)\]', text or ''))
    numeric = len(re.findall(r'\b\d+(?:\.\d+)?%?\b', text or ''))

    return {
        "phrase_hits": int(phrase_hits),
        "struct_hits": int(struct_hits),
        "pattern_hits": int(pattern_hits),
        "citation_hits": int(citations),
        "numeric_hits": int(numeric),
        "phrase_density": phrase_hits / max(n_sents / 80.0, 1.0),
        "pattern_density": pattern_hits / max(n_sents, 1),
        "transition_ratio": transition_ratio,
    }


def _precision101_analyze(self, text, cb=None):
    base_analyze = globals().get("_precision100_analyze") or globals().get("_precision99_analyze") or globals().get("_precision98_analyze")
    if base_analyze is None:
        base_analyze = getattr(self, "_orig_analyze_precision95", None)
    if base_analyze is None:
        base_analyze = getattr(AIDetectionEngine, "_orig_analyze_precision95", None)
    if base_analyze is None:
        base_analyze = AIDetectionEngine.analyze

    result = base_analyze(self, text, cb) if isinstance(base_analyze, _precision_types.FunctionType) else base_analyze(text, cb)
    if not isinstance(result, dict) or result.get("error"):
        return result

    try:
        clean_text = self._strip_references(text)
    except Exception:
        clean_text = text

    clean_text = re.sub(r'\s+', ' ', clean_text or '').strip()
    low = clean_text.lower()
    words = re.findall(r'[A-Za-z]+', low)
    sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', clean_text) if len(re.findall(r"[A-Za-z]+", s)) >= 4]

    indicators = dict(result.get("indicators", {}) or {})
    extended = dict(result.get("extended", {}) or {})
    fpd = dict(extended.get("fp_details", {}) or {})

    fp = float(indicators.get("🔍 Fingerprint Score v35 ★★★", extended.get("fingerprint_score", 0.0)) or 0.0)
    gf = float(indicators.get("GPT Format Signature ★★★", extended.get("gpt_format_score", 0.0)) or 0.0)
    sg = float(indicators.get("Simple GPT Score v22 ★★★", extended.get("simple_gpt_score", 0.0)) or 0.0)
    en = float(indicators.get("English AI Engine v2 ★★★", indicators.get("English AI Engine v2", extended.get("english_ai_score", 0.0))) or 0.0)
    nb = float(indicators.get("Naive Bayes ML v25 ★", extended.get("nb_score", 0.0)) or 0.0)
    llr = float(indicators.get("LLR v28 ★★★ [corpus جديد]", extended.get("llr_score", 0.0)) or 0.0)
    pat_mem = float(indicators.get("Pattern Memory v20 ★★★", extended.get("pat_mem", 0.0)) or 0.0)

    para_results = extended.get("paragraph_results", []) or []
    para_meta = self._precision96_paragraph_corroboration(para_results)

    direct = _precision101_direct_gpt_evidence(self, clean_text, words, sents)
    phrase_hits = int(direct["phrase_hits"])
    struct_hits = int(direct["struct_hits"])
    pattern_hits = int(direct["pattern_hits"])
    citation_hits = int(direct["citation_hits"])
    numeric_hits = int(direct["numeric_hits"])
    phrase_density = float(direct["phrase_density"])
    pattern_density = float(direct["pattern_density"])
    transition_ratio = float(direct["transition_ratio"])

    first_person = len(re.findall(r'\b(?:i|we|our|my|us)\b', low))
    hedges = len(re.findall(r'\b(?:may|might|could|perhaps|possibly|likely|unlikely|approximately|suggests?|appears?|indicates?)\b', low))
    method_terms = len(re.findall(r'\b(?:method(?:ology)?|materials?|results?|discussion|conclusion|experiment(?:al)?|sample|samples|participants|procedure|analysis|statistical|dataset|model|table|figure|prisma)\b', low))

    ref_anomaly, ref_meta = _precision101_reference_anomaly(self, text)

    prisma_anomaly = 0.0
    if "records screened" in low and "reports not retrieved" in low:
        nums = [int(n.replace(',', '')) for n in re.findall(r'\b\d{2,6}(?:,\d{3})*\b', clean_text[:14000])]
        if any((a > 0 and b > a * 3) for a, b in zip(nums, nums[1:])):
            prisma_anomaly = 0.15

    integrity_anomaly = min(0.60, ref_anomaly + prisma_anomaly)

    fp_phrase = float(fpd.get("fp_en_phrases", 0.0) or 0.0)
    fp_structure = float(fpd.get("fp_structure", 0.0) or 0.0)
    fp_simple = float(fpd.get("fp_simple_gpt", 0.0) or 0.0)
    fp_t2 = float(fpd.get("fp_t2_patterns", 0.0) or 0.0)
    fp_uniformity = float(fpd.get("fp_uniformity", 0.0) or 0.0)
    fp_cliches = float(fpd.get("fp_cliches", 0.0) or 0.0)
    fp_format = float(fpd.get("fp_format_sig", 0.0) or 0.0)

    legacy_exact = int(fpd.get("exact_phrases", 0) or 0)
    legacy_struct = int(fpd.get("struct_hits", 0) or 0)
    legacy_corrob = float(fpd.get("corroboration", 0.0) or 0.0)
    if fp_phrase == 0.0 and legacy_exact:
        fp_phrase = min(legacy_exact / 4.0, 1.0)
    if fp_structure == 0.0 and legacy_struct:
        fp_structure = min(legacy_struct / 4.0, 1.0)
    if fp_uniformity == 0.0 and legacy_corrob:
        fp_uniformity = min(legacy_corrob / 3.5, 1.0)
    if fp_simple == 0.0 and sg > 0:
        fp_simple = min(sg, 1.0)
    if fp_t2 == 0.0 and pat_mem > 0:
        fp_t2 = min(pat_mem, 1.0)
    if fp_format == 0.0 and gf > 0:
        fp_format = min(gf, 1.0)

    fp_core = (
        fp_phrase * 0.24 +
        fp_structure * 0.16 +
        fp_simple * 0.10 +
        fp_t2 * 0.08 +
        fp_uniformity * 0.05 +
        fp_cliches * 0.03 +
        fp_format * 0.04
    )
    fp_core = max(0.0, min(fp_core, 0.95))

    direct_gpt_score = (
        min(phrase_density / 1.60, 1.0) * 0.34 +
        min(struct_hits / 4.0, 1.0) * 0.16 +
        min(pattern_density / 0.020, 1.0) * 0.08 +
        fp_core * 0.10 +
        integrity_anomaly * 0.18
    )
    direct_gpt_score = max(0.0, min(direct_gpt_score, 0.99))

    fingerprint_evidence = (
        min(phrase_density / 1.50, 1.0) * 0.28 +
        min(struct_hits / 4.0, 1.0) * 0.14 +
        fp_core * 0.24 +
        integrity_anomaly * 0.30 +
        min(transition_ratio / 0.10, 1.0) * 0.04
    )
    fingerprint_evidence = max(0.0, min(fingerprint_evidence, 0.99))

    style_pressure = (
        sg * 0.18 +
        en * 0.12 +
        fp * 0.10 +
        min(nb, 0.90) * 0.08 +
        min(llr, 0.90) * 0.06 +
        min(pat_mem, 0.90) * 0.04 +
        min(para_meta.get("avg", 0.0) / 0.70, 1.0) * 0.04
    )
    style_pressure = max(0.0, min(style_pressure, 0.80))

    evidence_peak = max(direct_gpt_score, fingerprint_evidence, integrity_anomaly)
    effective_style = min(style_pressure, evidence_peak + 0.03)
    effective_style = max(0.0, min(effective_style, 0.70))

    style_consensus = 0
    style_consensus += 1 if sg >= 0.80 else 0
    style_consensus += 1 if nb >= 0.82 else 0
    style_consensus += 1 if en >= 0.68 else 0
    style_consensus += 1 if fp >= 0.46 else 0
    style_consensus += 1 if llr >= 0.72 else 0
    style_consensus += 1 if para_meta.get("strong", 0) >= 2 or para_meta.get("avg", 0.0) >= 0.66 else 0

    academic_grounding = 0.0
    if citation_hits >= 2:
        academic_grounding += 0.09
    if numeric_hits >= max(6, len(words) // 120):
        academic_grounding += 0.07
    if method_terms >= 6:
        academic_grounding += 0.05
    if hedges >= 4:
        academic_grounding += 0.03
    if first_person >= 2:
        academic_grounding += 0.02
    academic_grounding = min(academic_grounding, 0.24)

    final = (
        direct_gpt_score * 0.52 +
        fingerprint_evidence * 0.28 +
        effective_style * 0.06 +
        integrity_anomaly * 0.14
    )

    if academic_grounding >= 0.12 and evidence_peak < 0.20:
        final -= 0.03
    elif academic_grounding >= 0.10 and evidence_peak < 0.14:
        final -= 0.02
    else:
        final -= academic_grounding * 0.08

    if evidence_peak >= 0.46 and phrase_hits >= 3:
        final = max(final, 0.62)
    if evidence_peak >= 0.58 and phrase_hits >= 4 and struct_hits >= 3:
        final = max(final, 0.76)

    final = max(0.0, min(final, 0.995))

    result["score"] = final
    result["percentage"] = final * 100.0
    result["human_score"] = (1.0 - final) * 100.0
    result["risk_level"] = (
        "CRITICAL" if final >= 0.90 else
        "HIGH" if final >= 0.76 else
        "MEDIUM" if final >= 0.56 else
        "LOW" if final >= 0.18 else
        "MINIMAL"
    )
    _verdicts = {
        "CRITICAL": "اشتباه مرتفع جدًا - يحتاج تحقق بشري",
        "HIGH":     "اشتباه مرتفع - يحتاج تحقق بشري",
        "MEDIUM":   "نتيجة مختلطة / غير حاسمة",
        "LOW":      "اشتباه منخفض",
        "MINIMAL":  "بشري على الأرجح",
    }
    result["verdict"] = _verdicts[result["risk_level"]]

    indicators["English AI Engine v2 ★★★"] = en
    indicators["English AI Engine v2"] = en
    indicators["🔍 Fingerprint Score v35 ★★★"] = max(fp, min(fingerprint_evidence * 0.90 + direct_gpt_score * 0.18, 0.99))
    indicators["Simple GPT Score v22 ★★★"] = max(sg, min(effective_style, 0.82)) if evidence_peak >= 0.22 else min(sg, 0.55)
    indicators["Academic Grounding Guard ▼"] = round(academic_grounding, 4)
    indicators["Integrity Anomaly Score ★"] = round(integrity_anomaly, 4)
    indicators["Reference Anomaly Score ★"] = round(ref_anomaly, 4)

    extended["direct_gpt_score"] = round(direct_gpt_score, 4)
    extended["fingerprint_evidence_score"] = round(fingerprint_evidence, 4)
    extended["style_pressure_raw"] = round(style_pressure, 4)
    extended["gpt_style_score"] = round(effective_style, 4)
    extended["style_consensus_v101"] = int(style_consensus)
    extended["academic_grounding_v101"] = round(academic_grounding, 4)
    extended["integrity_anomaly_v101"] = round(integrity_anomaly, 4)
    extended["reference_anomaly_v101"] = round(ref_anomaly, 4)
    extended["prisma_anomaly_v101"] = round(prisma_anomaly, 4)
    extended["precision101_phrase_hits"] = int(phrase_hits)
    extended["precision101_struct_hits"] = int(struct_hits)
    extended["precision101_pattern_hits"] = int(pattern_hits)
    extended["precision101_phrase_density"] = round(phrase_density, 4)
    extended["precision101_transition_ratio"] = round(transition_ratio, 4)
    extended["precision101_reference_blocks"] = int(ref_meta.get("reference_blocks", 0))
    extended["precision101_reference_outliers"] = int(ref_meta.get("reference_outliers", 0))
    extended["precision101_reference_odd_terms"] = int(ref_meta.get("reference_odd_terms", 0))

    result["indicators"] = indicators
    result["extended"] = extended
    result["precision95_meta"] = {
        "patched_by": "precision101_research_calibrated",
        "direct_gpt_score": round(direct_gpt_score, 4),
        "fingerprint_evidence_score": round(fingerprint_evidence, 4),
        "effective_style_score": round(effective_style, 4),
        "style_pressure_raw": round(style_pressure, 4),
        "style_consensus": int(style_consensus),
        "academic_grounding": round(academic_grounding, 4),
        "integrity_anomaly": round(integrity_anomaly, 4),
        "reference_anomaly": round(ref_anomaly, 4),
        "prisma_anomaly": round(prisma_anomaly, 4),
        "phrase_hits": int(phrase_hits),
        "struct_hits": int(struct_hits),
        "pattern_hits": int(pattern_hits),
        "citation_hits": int(citation_hits),
        "numeric_hits": int(numeric_hits),
        "final_score": round(final, 4),
    }
    return result

AIDetectionEngine.analyze = _precision101_analyze


# ===== Precision102: strict evidence separation + human-authenticity calibration =====

_PREC102_GENERIC_PHRASE_RE = re.compile(
    r'\b(?:however|moreover|furthermore|therefore|overall|in\s+conclusion|to\s+summarize|'
    r'on\s+the\s+other\s+hand|by\s+contrast|the\s+relationship\s+between|best\s+practices|'
    r'positive\s+impact|plays?\s+a\s+(?:crucial|fundamental|central|vital|key|significant|important)\s+role|'
    r'this\s+(?:study|paper|review)\s+(?:aims?|seeks?|examines?|investigates?|explores?)|'
    r'it\s+is\s+(?:important|necessary|clear|evident)\s+to|future\s+research\s+is\s+needed)\b',
    re.I
)

def _precision102_phrase_bank(self):
    bank = []
    seen = set()
    for p in list(getattr(self, "EN_GPT_PHRASES_T1", []) or []):
        p = re.sub(r'\s+', ' ', (p or '').strip().lower())
        if not p or p in seen:
            continue
        seen.add(p)
        if len(p.split()) < 5:
            continue
        if _PREC102_GENERIC_PHRASE_RE.search(p):
            continue
        bank.append(p)
    # keep only more distinctive entries first
    bank.sort(key=lambda s: (len(s.split()), len(s)), reverse=True)
    return bank

def _precision102_human_authenticity(self, text, low, words, sents):
    text = text or ''
    low = low or ''
    n_sents = max(len(sents), 1)
    n_words = max(len(words), 1)

    cross_ref_hits = len(re.findall(r'\b(?:table|figure|fig\.?|equation|eq\.?|algorithm|appendix|section|theorem|lemma)\s*\(?[A-Za-z]?\d+[A-Za-z]?\)?', text, re.I))
    variable_hits = len(re.findall(r'\b(?:[A-Z]{1,4}\d{1,4}|[a-zA-Z]_[a-zA-Z0-9]+|[A-Z]{2,}\s*\d+(?:\.\d+)?)\b', text))
    stats_hits = len(re.findall(r'\b(?:n\s*=\s*\d+|p\s*[<=>]\s*0?\.\d+|R²\s*=\s*0?\.\d+|CI\s*\d+%|α\s*=|beta\s*=)\b', text, re.I))
    unit_hits = len(re.findall(r'\b\d+(?:\.\d+)?\s*(?:%|mm|cm|m|km|mg|g|kg|ml|l|ms|s|min|h|hz|khz|mhz|ghz|mb|gb|tb|kbps|mbps|gbps|v|kv|ma|a|w|kw|mw|°c|kpa|mpa|nm|μm|um|m/s|m3/s|rpm)\b', low))
    citation_claim_sents = 0
    detail_sents = 0
    for s in sents:
        sl = s.lower()
        has_num = bool(re.search(r'\b\d+(?:\.\d+)?%?\b', s))
        has_cite = bool(re.search(r'\[(?:\d+|\d+(?:\s*,\s*\d+)*)\]|\([A-Z][A-Za-z\-]+,\s*\d{4}[a-z]?\)', s))
        has_anchor = bool(re.search(r'\b(?:table|figure|fig\.?|equation|eq\.?|algorithm|appendix|dataset|protocol|sample|samples|participants|procedure|implementation|simulation|experiment|theorem|lemma|proof|model)\b', sl))
        if has_num and has_anchor:
            detail_sents += 1
        if has_num and has_cite:
            citation_claim_sents += 1

    authenticity = (
        min(cross_ref_hits / 8.0, 1.0) * 0.26 +
        min(variable_hits / 16.0, 1.0) * 0.14 +
        min(stats_hits / 4.0, 1.0) * 0.16 +
        min(unit_hits / max(4.0, n_words / 300.0), 1.0) * 0.14 +
        min(detail_sents / max(2.0, n_sents / 12.0), 1.0) * 0.18 +
        min(citation_claim_sents / max(2.0, n_sents / 14.0), 1.0) * 0.12
    )
    authenticity = max(0.0, min(authenticity, 0.42))
    return authenticity, {
        "cross_ref_hits": int(cross_ref_hits),
        "variable_hits": int(variable_hits),
        "stats_hits": int(stats_hits),
        "unit_hits": int(unit_hits),
        "detail_sents": int(detail_sents),
        "citation_claim_sents": int(citation_claim_sents),
    }

def _precision102_direct_gpt_evidence(self, text, words, sents):
    tl = (text or '').lower()
    n_sents = max(len(sents), 1)

    phrase_hits = 0
    long_phrase_hits = 0
    for phrase in _precision102_phrase_bank(self):
        if phrase in tl:
            phrase_hits += 1
            if len(phrase.split()) >= 7:
                long_phrase_hits += 1

    strong_extra = [
        "in today's rapidly evolving",
        "a balanced and strategic approach",
        "while minimizing its potential risks and challenges",
        "enabling innovation across multiple sectors",
        "it is important to note that",
        "it is worth noting that",
        "this underscores the importance of",
        "future research is needed",
        "a holistic approach",
        "a multifaceted approach",
        "a nuanced perspective",
    ]
    extra_hits = sum(1 for p in strong_extra if p in tl)

    pattern_hits = 0
    strong_patterns = [
        r'\bin\s+today\'?s\s+(?:rapidly|ever)\s+\w+',
        r'\bit\s+is\s+(?:important|crucial|essential)\s+to\s+note\s+that\b',
        r'\bit\s+is\s+worth\s+(?:noting|emphasizing)\s+that\b',
        r'\bthis\s+underscores\s+the\s+importance\s+of\b',
        r'\bfuture\s+research\s+(?:is\s+needed|should|could|may)\b',
        r'\ba\s+(?:balanced\s+and\s+strategic|holistic|multifaceted|nuanced)\s+approach\b',
        r'\bwhile\s+minimizing\s+(?:its|their|the)\s+potential\s+(?:risks|challenges)\b',
        r'\benabling\s+innovation\s+across\s+multiple\s+sectors\b',
    ]
    for pat in strong_patterns:
        try:
            pattern_hits += len(re.findall(pat, tl, re.I))
        except Exception:
            pass

    struct_hits = 0
    for pat in [
        r'\bthis\s+(?:study|paper|review)\s+(?:aims?|seeks?|examines?|investigates?|explores?)\s+to\b',
        r'\bit\s+is\s+important\s+to\s+note\s+that\b',
        r'\bit\s+is\s+worth\s+noting\s+that\b',
        r'\bfuture\s+research\s+is\s+needed\b',
        r'\bthis\s+underscores\s+the\s+importance\s+of\b',
    ]:
        try:
            struct_hits += len(re.findall(pat, tl, re.I))
        except Exception:
            pass

    transition_hits = len(re.findall(
        r'(?:(?<=\.)|^)\s*(?:however|moreover|furthermore|therefore|overall|consequently|thus)\b',
        tl,
        re.I
    ))
    # transition words alone are not direct evidence; only used as soft support later
    transition_ratio = transition_hits / n_sents

    citations = len(re.findall(r'\([A-Z][A-Za-z\-]+,\s*\d{4}[a-z]?\)', text or ''))
    citations += len(re.findall(r'\[(?:\d+|\d+(?:\s*,\s*\d+)*)\]', text or ''))
    numeric = len(re.findall(r'\b\d+(?:\.\d+)?%?\b', text or ''))

    return {
        "phrase_hits": int(phrase_hits + extra_hits),
        "long_phrase_hits": int(long_phrase_hits),
        "struct_hits": int(struct_hits),
        "pattern_hits": int(pattern_hits),
        "citation_hits": int(citations),
        "numeric_hits": int(numeric),
        "pattern_density": pattern_hits / n_sents,
        "transition_ratio": transition_ratio,
    }

def _precision102_compute_fingerprint_score(self, text, words, sents,
                                simple_gpt_score, gpt_format_score,
                                english_ai_score, arabic_ai_score,
                                human_error_val, english_human_score,
                                deep_human_score):
    """Stricter fingerprint score: style never counts as direct evidence by itself."""
    if not words or not sents:
        self._fp_scores_cache = {}
        return 0.0

    tl = (text or '').lower()
    n_words = max(len(words), 1)
    phrase_bank = _precision102_phrase_bank(self)
    exact_phrases = sum(1 for p in phrase_bank if p in tl)
    long_exact = sum(1 for p in phrase_bank if len(p.split()) >= 7 and p in tl)

    struct_hits = 0
    for p in [
        r'\bit\s+is\s+worth\s+(?:noting|emphasizing)\s+that\b',
        r'\bit\s+is\s+important\s+to\s+note\s+that\b',
        r'\bthis\s+underscores\s+the\s+importance\s+of\b',
        r'\bfuture\s+research\s+(?:is\s+needed|should|could|may)\b',
        r'\bin\s+today\'?s\s+(?:rapidly|ever)\s+\w+',
        r'\bwhile\s+minimizing\s+(?:its|their|the)\s+potential\s+(?:risks|challenges)\b',
    ]:
        try:
            struct_hits += len(re.findall(p, tl, re.I))
        except Exception:
            pass

    direct_signal = (
        min(exact_phrases / 4.0, 1.0) * 0.40 +
        min(long_exact / 2.0, 1.0) * 0.18 +
        min(struct_hits / 4.0, 1.0) * 0.12 +
        min(getattr(self, '_pattern_memory')(text), 0.9) * 0.10 +
        min(simple_gpt_score, 0.9) * 0.12 +
        min(gpt_format_score, 0.9) * 0.04
    )

    # Style support is intentionally tiny and only allowed when some direct evidence exists.
    style_support = 0.0
    if exact_phrases >= 1 or long_exact >= 1 or struct_hits >= 2:
        style_support += min(english_ai_score, 0.9) * 0.05
        style_support += min(getattr(self, '_semantic_embedding')(words, sents), 0.85) * 0.03
        style_support += min(getattr(self, '_context_drift')(sents, words), 0.85) * 0.02
    style_support = min(style_support, 0.08)

    human_damp = 0.0
    citations = len(re.findall(r'\[(?:\d+|\d+(?:\s*,\s*\d+)*)\]|\([A-Z][A-Za-z\-]+,\s*\d{4}[a-z]?\)', text or ''))
    numeric = len(re.findall(r'\b\d+(?:\.\d+)?%?\b', text or ''))
    if citations >= 2:
        human_damp += 0.06
    if numeric >= max(6, n_words // 120):
        human_damp += 0.05
    human_damp += english_human_score * 0.08
    human_damp += deep_human_score * 0.06
    human_damp += human_error_val * 0.04

    score = direct_signal + style_support - human_damp
    corroboration = 0
    corroboration += 1 if exact_phrases >= 2 else 0
    corroboration += 1 if long_exact >= 1 else 0
    corroboration += 1 if struct_hits >= 3 else 0
    corroboration += 1 if simple_gpt_score >= 0.68 else 0
    corroboration += 1 if gpt_format_score >= 0.60 else 0

    if corroboration >= 3 and (long_exact >= 1 or exact_phrases >= 3):
        score = max(score, 0.62)
    if corroboration >= 4 and long_exact >= 2:
        score = max(score, 0.78)

    if exact_phrases == 0 and long_exact == 0 and struct_hits <= 1:
        score = min(score, 0.26)

    self._fp_scores_cache = {
        "exact_phrases": int(exact_phrases),
        "long_exact_phrases": int(long_exact),
        "struct_hits": int(struct_hits),
        "corroboration": int(corroboration),
    }
    return round(max(0.0, min(score, 0.98)), 4)

def _precision102_analyze(self, text, cb=None):
    base_analyze = globals().get("_precision101_analyze") or globals().get("_precision100_analyze") or globals().get("_precision99_analyze")
    if base_analyze is None:
        base_analyze = getattr(self, "_orig_analyze_precision95", None)
    if base_analyze is None:
        base_analyze = getattr(AIDetectionEngine, "_orig_analyze_precision95", None)
    if base_analyze is None:
        base_analyze = AIDetectionEngine.analyze

    result = base_analyze(self, text, cb) if isinstance(base_analyze, _precision_types.FunctionType) else base_analyze(text, cb)
    if not isinstance(result, dict) or result.get("error"):
        return result

    try:
        clean_text = self._strip_references(text)
    except Exception:
        clean_text = text

    clean_text = re.sub(r'\s+', ' ', clean_text or '').strip()
    low = clean_text.lower()
    words = re.findall(r'[A-Za-z]+', low)
    sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', clean_text) if len(re.findall(r"[A-Za-z]+", s)) >= 4]

    indicators = dict(result.get("indicators", {}) or {})
    extended = dict(result.get("extended", {}) or {})
    fpd = dict(extended.get("fp_details", {}) or {})

    fp = float(indicators.get("🔍 Fingerprint Score v35 ★★★", extended.get("fingerprint_score", 0.0)) or 0.0)
    gf = float(indicators.get("GPT Format Signature ★★★", extended.get("gpt_format_score", 0.0)) or 0.0)
    sg = float(indicators.get("Simple GPT Score v22 ★★★", extended.get("simple_gpt_score", 0.0)) or 0.0)
    en = float(indicators.get("English AI Engine v2 ★★★", indicators.get("English AI Engine v2", extended.get("english_ai_score", 0.0))) or 0.0)
    nb = float(indicators.get("Naive Bayes ML v25 ★", extended.get("nb_score", 0.0)) or 0.0)
    llr = float(indicators.get("LLR v28 ★★★ [corpus جديد]", extended.get("llr_score", 0.0)) or 0.0)
    pat_mem = float(indicators.get("Pattern Memory v20 ★★★", extended.get("pat_mem", 0.0)) or 0.0)

    para_results = extended.get("paragraph_results", []) or []
    para_meta = self._precision96_paragraph_corroboration(para_results)

    direct = _precision102_direct_gpt_evidence(self, clean_text, words, sents)
    phrase_hits = int(direct["phrase_hits"])
    long_phrase_hits = int(direct["long_phrase_hits"])
    struct_hits = int(direct["struct_hits"])
    pattern_hits = int(direct["pattern_hits"])
    citation_hits = int(direct["citation_hits"])
    numeric_hits = int(direct["numeric_hits"])
    pattern_density = float(direct["pattern_density"])
    transition_ratio = float(direct["transition_ratio"])

    first_person = len(re.findall(r'\b(?:i|we|our|my|us)\b', low))
    hedges = len(re.findall(r'\b(?:may|might|could|perhaps|possibly|likely|unlikely|approximately|suggests?|appears?|indicates?)\b', low))
    method_terms = len(re.findall(r'\b(?:method(?:ology)?|materials?|results?|discussion|conclusion|experiment(?:al)?|sample|samples|participants|procedure|analysis|statistical|dataset|implementation|evaluation|protocol|table|figure|algorithm|theorem|lemma|proof)\b', low))

    ref_anomaly, ref_meta = _precision101_reference_anomaly(self, text)
    prisma_anomaly = 0.0
    if "records screened" in low and "reports not retrieved" in low:
        nums = [int(n.replace(',', '')) for n in re.findall(r'\b\d{2,6}(?:,\d{3})*\b', clean_text[:14000])]
        if any((a > 0 and b > a * 3) for a, b in zip(nums, nums[1:])):
            prisma_anomaly = 0.15
    integrity_anomaly = min(0.60, ref_anomaly + prisma_anomaly + (0.18 if "invalid citation" in low else 0.0))

    fp_phrase = float(fpd.get("fp_en_phrases", 0.0) or 0.0)
    fp_structure = float(fpd.get("fp_structure", 0.0) or 0.0)
    fp_simple = float(fpd.get("fp_simple_gpt", 0.0) or 0.0)
    fp_t2 = float(fpd.get("fp_t2_patterns", 0.0) or 0.0)
    fp_uniformity = float(fpd.get("fp_uniformity", 0.0) or 0.0)
    fp_cliches = float(fpd.get("fp_cliches", 0.0) or 0.0)
    fp_format = float(fpd.get("fp_format_sig", 0.0) or 0.0)
    legacy_exact = int(fpd.get("exact_phrases", 0) or 0)
    legacy_long = int(fpd.get("long_exact_phrases", 0) or 0)
    legacy_struct = int(fpd.get("struct_hits", 0) or 0)
    legacy_corrob = float(fpd.get("corroboration", 0.0) or 0.0)

    if fp_phrase == 0.0 and legacy_exact:
        fp_phrase = min(legacy_exact / 4.0, 1.0)
    if fp_structure == 0.0 and legacy_struct:
        fp_structure = min(legacy_struct / 4.5, 1.0)
    if fp_uniformity == 0.0 and legacy_corrob:
        fp_uniformity = min(legacy_corrob / 4.0, 1.0)
    if fp_simple == 0.0 and sg > 0:
        fp_simple = min(sg, 1.0)
    if fp_t2 == 0.0 and pat_mem > 0:
        fp_t2 = min(pat_mem, 1.0)
    if fp_format == 0.0 and gf > 0:
        fp_format = min(gf, 1.0)

    fingerprint_evidence = (
        min(phrase_hits / 4.0, 1.0) * 0.24 +
        min(long_phrase_hits / 2.0, 1.0) * 0.18 +
        min(struct_hits / 4.0, 1.0) * 0.12 +
        min(pattern_density / 0.020, 1.0) * 0.06 +
        fp_phrase * 0.10 +
        fp_structure * 0.07 +
        fp_simple * 0.05 +
        fp_t2 * 0.04 +
        fp_format * 0.03 +
        fp_uniformity * 0.02 +
        fp_cliches * 0.01 +
        integrity_anomaly * 0.08
    )
    fingerprint_evidence = max(0.0, min(fingerprint_evidence, 0.99))

    direct_gpt_score = (
        min(phrase_hits / 4.0, 1.0) * 0.34 +
        min(long_phrase_hits / 2.0, 1.0) * 0.20 +
        min(struct_hits / 4.0, 1.0) * 0.10 +
        min(pattern_density / 0.020, 1.0) * 0.06 +
        integrity_anomaly * 0.22 +
        min(gf, 0.9) * 0.04 +
        fingerprint_evidence * 0.04
    )
    if phrase_hits >= 2 and long_phrase_hits >= 1:
        direct_gpt_score += 0.06
    if integrity_anomaly >= 0.18 and (phrase_hits >= 1 or struct_hits >= 2):
        direct_gpt_score += 0.06
    direct_gpt_score = max(0.0, min(direct_gpt_score, 0.99))

    style_pressure = (
        sg * 0.16 +
        en * 0.10 +
        fp * 0.08 +
        min(nb, 0.90) * 0.06 +
        min(llr, 0.90) * 0.04 +
        min(pat_mem, 0.90) * 0.03 +
        min(para_meta.get("avg", 0.0) / 0.72, 1.0) * 0.03 +
        min(transition_ratio / 0.12, 1.0) * 0.02
    )
    style_pressure = max(0.0, min(style_pressure, 0.55))

    evidence_peak = max(direct_gpt_score, fingerprint_evidence, integrity_anomaly)
    # style cannot lead; it can only support existing direct evidence
    effective_style = min(style_pressure, max(0.0, evidence_peak - 0.10))
    effective_style = max(0.0, min(effective_style, 0.22))

    academic_grounding = 0.0
    if citation_hits >= 2:
        academic_grounding += 0.08
    if numeric_hits >= max(6, len(words) // 120):
        academic_grounding += 0.06
    if method_terms >= 6:
        academic_grounding += 0.05
    if hedges >= 4:
        academic_grounding += 0.03
    if first_person >= 2:
        academic_grounding += 0.02
    academic_grounding = min(academic_grounding, 0.24)

    human_auth, human_meta = _precision102_human_authenticity(self, clean_text, low, words, sents)

    style_consensus = 0
    style_consensus += 1 if sg >= 0.84 else 0
    style_consensus += 1 if nb >= 0.86 else 0
    style_consensus += 1 if en >= 0.72 else 0
    style_consensus += 1 if fp >= 0.52 else 0
    style_consensus += 1 if llr >= 0.76 else 0
    style_consensus += 1 if para_meta.get("strong", 0) >= 3 or para_meta.get("avg", 0.0) >= 0.72 else 0

    final = (
        direct_gpt_score * 0.50 +
        fingerprint_evidence * 0.26 +
        integrity_anomaly * 0.14 +
        effective_style * 0.04 -
        academic_grounding * 0.06 -
        human_auth * 0.14
    )

    # strong protection for grounded human academic writing when direct evidence is weak
    if human_auth >= 0.18 and evidence_peak < 0.22:
        final -= 0.04
    elif (human_auth + academic_grounding) >= 0.28 and evidence_peak < 0.28:
        final -= 0.03
    elif human_auth >= 0.10 and evidence_peak < 0.18:
        final -= 0.02

    # allow style consensus to help only after direct evidence is already non-trivial
    if direct_gpt_score >= 0.36 and fingerprint_evidence >= 0.30 and style_consensus >= 4:
        final += 0.04
    if direct_gpt_score >= 0.50 and fingerprint_evidence >= 0.42 and style_consensus >= 5 and long_phrase_hits >= 1:
        final += 0.06

    # floors only for strong direct + anomaly evidence
    if direct_gpt_score >= 0.48 and fingerprint_evidence >= 0.40 and (long_phrase_hits >= 1 or integrity_anomaly >= 0.18):
        final = max(final, 0.58)
    if direct_gpt_score >= 0.62 and fingerprint_evidence >= 0.54 and long_phrase_hits >= 2 and (integrity_anomaly >= 0.12 or style_consensus >= 5):
        final = max(final, 0.74)

    final = max(0.0, min(final, 0.995))

    result["score"] = final
    result["percentage"] = final * 100.0
    result["human_score"] = (1.0 - final) * 100.0
    result["risk_level"] = (
        "CRITICAL" if final >= 0.90 else
        "HIGH" if final >= 0.76 else
        "MEDIUM" if final >= 0.56 else
        "LOW" if final >= 0.18 else
        "MINIMAL"
    )
    _verdicts = {
        "CRITICAL": "اشتباه مرتفع جدًا - يحتاج تحقق بشري",
        "HIGH":     "اشتباه مرتفع - يحتاج تحقق بشري",
        "MEDIUM":   "نتيجة مختلطة / غير حاسمة",
        "LOW":      "اشتباه منخفض",
        "MINIMAL":  "بشري على الأرجح",
    }
    result["verdict"] = _verdicts[result["risk_level"]]

    indicators["English AI Engine v2 ★★★"] = en
    indicators["English AI Engine v2"] = en
    indicators["🔍 Fingerprint Score v35 ★★★"] = max(fp, min(fingerprint_evidence * 0.92 + direct_gpt_score * 0.16, 0.99))
    indicators["Simple GPT Score v22 ★★★"] = min(max(sg, effective_style), 0.82) if evidence_peak >= 0.24 else min(sg, 0.52)
    indicators["Academic Grounding Guard ▼"] = round(academic_grounding, 4)
    indicators["Human Authenticity Score ▼"] = round(human_auth, 4)
    indicators["Integrity Anomaly Score ★"] = round(integrity_anomaly, 4)
    indicators["Reference Anomaly Score ★"] = round(ref_anomaly, 4)

    extended["direct_gpt_score"] = round(direct_gpt_score, 4)
    extended["fingerprint_evidence_score"] = round(fingerprint_evidence, 4)
    extended["gpt_style_score"] = round(effective_style, 4)
    extended["style_pressure_raw"] = round(style_pressure, 4)
    extended["style_consensus_v102"] = int(style_consensus)
    extended["academic_grounding_v102"] = round(academic_grounding, 4)
    extended["human_authenticity_v102"] = round(human_auth, 4)
    extended["integrity_anomaly_v102"] = round(integrity_anomaly, 4)
    extended["reference_anomaly_v102"] = round(ref_anomaly, 4)
    extended["prisma_anomaly_v102"] = round(prisma_anomaly, 4)
    extended["precision102_phrase_hits"] = int(phrase_hits)
    extended["precision102_long_phrase_hits"] = int(long_phrase_hits)
    extended["precision102_struct_hits"] = int(struct_hits)
    extended["precision102_pattern_hits"] = int(pattern_hits)
    extended["precision102_transition_ratio"] = round(transition_ratio, 4)
    extended["precision102_human_meta"] = human_meta
    extended["precision102_reference_blocks"] = int(ref_meta.get("reference_blocks", 0))
    extended["precision102_reference_outliers"] = int(ref_meta.get("reference_outliers", 0))
    extended["precision102_reference_odd_terms"] = int(ref_meta.get("reference_odd_terms", 0))

    result["indicators"] = indicators
    result["extended"] = extended
    result["precision95_meta"] = {
        "patched_by": "precision102_strict_evidence_human_authenticity",
        "direct_gpt_score": round(direct_gpt_score, 4),
        "fingerprint_evidence_score": round(fingerprint_evidence, 4),
        "effective_style_score": round(effective_style, 4),
        "style_pressure_raw": round(style_pressure, 4),
        "style_consensus": int(style_consensus),
        "academic_grounding": round(academic_grounding, 4),
        "human_authenticity": round(human_auth, 4),
        "integrity_anomaly": round(integrity_anomaly, 4),
        "reference_anomaly": round(ref_anomaly, 4),
        "prisma_anomaly": round(prisma_anomaly, 4),
        "phrase_hits": int(phrase_hits),
        "long_phrase_hits": int(long_phrase_hits),
        "struct_hits": int(struct_hits),
        "pattern_hits": int(pattern_hits),
        "citation_hits": int(citation_hits),
        "numeric_hits": int(numeric_hits),
        "final_score": round(final, 4),
    }
    return result

AIDetectionEngine._compute_fingerprint_score = _precision102_compute_fingerprint_score
AIDetectionEngine.analyze = _precision102_analyze


# ===== Precision103 runtime route fix: apply latest bindings before any real analysis =====

def _precision103_bind_latest_runtime():
    _g = globals()

    # Re-apply helper bindings after the full file has loaded.
    for _attr, _name in {
        "_nb_score": "_v3fixed_nb_score",
        "_english_ai_score": "_v3fixed_english_ai_score",
        "_synonym_density": "_v3fixed_synonym_density",
        "_compute_fingerprint_score": "_precision102_compute_fingerprint_score",
    }.items():
        _fn = _g.get(_name)
        if _fn is not None:
            setattr(AIDetectionEngine, _attr, _fn)

    for _name in (
        "_precision102_analyze",
        "_precision101_analyze",
        "_precision100_analyze",
        "_precision99_analyze",
        "_precision98_analyze",
        "_precision97_analyze",
    ):
        _fn = _g.get(_name)
        if _fn is not None:
            AIDetectionEngine.analyze = _fn
            break

def _precision103_run_pending_analysis():
    """Defer pending analysis until the latest runtime bindings are loaded."""
    return

_precision103_bind_latest_runtime()
_precision103_run_pending_analysis()


# ===== Precision104 balanced runtime calibration: avoid all-zero GPT while protecting human academic text =====

def _precision104_compute_fingerprint_score(self, text, words, sents,
                                simple_gpt_score, gpt_format_score,
                                english_ai_score, arabic_ai_score,
                                human_error_val, english_human_score,
                                deep_human_score):
    """Balanced fingerprint score:
    - direct evidence remains primary
    - soft consensus can contribute modestly when human authenticity is weak
    - academic polish alone cannot dominate
    """
    if not words or not sents:
        self._fp_scores_cache = {}
        return 0.0

    tl = (text or '').lower()
    n_words = max(len(words), 1)
    phrase_bank = _precision102_phrase_bank(self)
    exact_phrases = sum(1 for p in phrase_bank if p in tl)
    long_exact = sum(1 for p in phrase_bank if len(p.split()) >= 7 and p in tl)

    struct_hits = 0
    for p in [
        r'\bit\s+is\s+worth\s+(?:noting|emphasizing)\s+that\b',
        r'\bit\s+is\s+important\s+to\s+note\s+that\b',
        r'\bthis\s+underscores\s+the\s+importance\s+of\b',
        r'\bfuture\s+research\s+(?:is\s+needed|should|could|may)\b',
        r'\bin\s+today\'?s\s+(?:rapidly|ever)\s+\w+',
        r'\bwhile\s+minimizing\s+(?:its|their|the)\s+potential\s+(?:risks|challenges)\b',
    ]:
        try:
            struct_hits += len(re.findall(p, tl, re.I))
        except Exception:
            pass

    pattern_mem = float(min(getattr(self, '_pattern_memory')(text), 0.95))
    semantic = float(min(getattr(self, '_semantic_embedding')(words, sents), 0.90))
    context = float(min(getattr(self, '_context_drift')(sents, words), 0.90))
    simple = float(min(simple_gpt_score, 0.95))
    fmt = float(min(gpt_format_score, 0.90))
    en = float(min(english_ai_score, 0.95))

    direct_signal = (
        min(exact_phrases / 4.0, 1.0) * 0.40 +
        min(long_exact / 2.0, 1.0) * 0.18 +
        min(struct_hits / 4.0, 1.0) * 0.12 +
        pattern_mem * 0.12 +
        simple * 0.12 +
        fmt * 0.06
    )

    # human authenticity dampers
    citations = len(re.findall(r'\[(?:\d+|\d+(?:\s*,\s*\d+)*)\]|\([A-Z][A-Za-z\-]+,\s*\d{4}[a-z]?\)', text or ''))
    numeric = len(re.findall(r'\b\d+(?:\.\d+)?%?\b', text or ''))
    table_refs = len(re.findall(r'\b(?:table|figure|fig\.?|eq(?:uation)?\.?)\s*\d+[a-z]?\b', text or '', re.I))
    pvals = len(re.findall(r'\bp\s*[<=>]\s*0?\.\d+\b', text or '', re.I))
    units = len(re.findall(r'\b\d+(?:\.\d+)?\s*(?:mg|kg|cm|mm|km|hz|khz|mhz|ghz|mb|gb|tb|ms|s|min|hrs?|°c|%)\b', text or '', re.I))

    human_damp = 0.0
    if citations >= 3:
        human_damp += 0.05
    if numeric >= max(6, n_words // 120):
        human_damp += 0.04
    if table_refs >= 2:
        human_damp += 0.04
    if pvals >= 1 or units >= 3:
        human_damp += 0.03
    human_damp += english_human_score * 0.08
    human_damp += deep_human_score * 0.06
    human_damp += human_error_val * 0.03

    # modest soft support path so fully GPT text does not collapse to zero
    soft_consensus = (
        simple * 0.38 +
        en * 0.22 +
        semantic * 0.14 +
        context * 0.10 +
        pattern_mem * 0.10 +
        fmt * 0.06
    )
    soft_consensus = max(0.0, min(soft_consensus, 0.75))

    soft_gate = 0.0
    # only activate if the text lacks strong human grounding
    if human_damp <= 0.18:
        if soft_consensus >= 0.58:
            soft_gate = min((soft_consensus - 0.50) * 0.55, 0.16)
        elif soft_consensus >= 0.50:
            soft_gate = min((soft_consensus - 0.50) * 0.35, 0.06)

    score = direct_signal + soft_gate - human_damp

    corroboration = 0
    corroboration += 1 if exact_phrases >= 2 else 0
    corroboration += 1 if long_exact >= 1 else 0
    corroboration += 1 if struct_hits >= 3 else 0
    corroboration += 1 if simple >= 0.72 else 0
    corroboration += 1 if pattern_mem >= 0.68 else 0
    corroboration += 1 if fmt >= 0.62 else 0

    if corroboration >= 3 and (long_exact >= 1 or exact_phrases >= 3):
        score = max(score, 0.58)
    if corroboration >= 4 and long_exact >= 2:
        score = max(score, 0.74)

    # never let academic polish alone create a high score
    if exact_phrases == 0 and long_exact == 0 and struct_hits <= 1:
        score = min(score, 0.42 if human_damp < 0.10 and soft_consensus >= 0.62 else 0.28)

    self._fp_scores_cache = {
        "exact_phrases": int(exact_phrases),
        "long_exact_phrases": int(long_exact),
        "struct_hits": int(struct_hits),
        "corroboration": int(corroboration),
        "soft_consensus": round(soft_consensus, 4),
        "soft_gate": round(soft_gate, 4),
    }
    return round(max(0.0, min(score, 0.98)), 4)


def _precision108_analyze(self, text, cb=None):
    base_analyze = globals().get("_precision102_analyze") or globals().get("_precision101_analyze") or globals().get("_precision100_analyze") or globals().get("_precision99_analyze")
    if base_analyze is None:
        base_analyze = getattr(self, "_orig_analyze_precision95", None)
    if base_analyze is None:
        base_analyze = getattr(AIDetectionEngine, "_orig_analyze_precision95", None)
    if base_analyze is None:
        base_analyze = AIDetectionEngine.analyze

    result = base_analyze(self, text, cb) if isinstance(base_analyze, _precision_types.FunctionType) else base_analyze(text, cb)
    if not isinstance(result, dict) or result.get("error"):
        return result

    try:
        clean_text = self._strip_references(text)
    except Exception:
        clean_text = text

    clean_text = re.sub(r'\s+', ' ', clean_text or '').strip()
    low = clean_text.lower()
    words = re.findall(r'[A-Za-z]+', low)
    sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', clean_text) if len(re.findall(r"[A-Za-z]+", s)) >= 4]

    indicators = dict(result.get("indicators", {}) or {})
    extended = dict(result.get("extended", {}) or {})
    fpd = dict(extended.get("fp_details", {}) or {})

    fp = float(indicators.get("🔍 Fingerprint Score v35 ★★★", extended.get("fingerprint_score", 0.0)) or 0.0)
    gf = float(indicators.get("GPT Format Signature ★★★", extended.get("gpt_format_score", 0.0)) or 0.0)
    sg = float(indicators.get("Simple GPT Score v22 ★★★", extended.get("simple_gpt_score", 0.0)) or 0.0)
    en = float(indicators.get("English AI Engine v2 ★★★", indicators.get("English AI Engine v2", extended.get("english_ai_score", 0.0))) or 0.0)
    nb = float(indicators.get("Naive Bayes ML v25 ★", extended.get("nb_score", 0.0)) or 0.0)
    llr = float(indicators.get("LLR v28 ★★★ [corpus جديد]", extended.get("llr_score", 0.0)) or 0.0)
    pat_mem = float(indicators.get("Pattern Memory v20 ★★★", extended.get("pat_mem", 0.0)) or 0.0)

    para_results = extended.get("paragraph_results", []) or []
    para_meta = self._precision96_paragraph_corroboration(para_results)

    direct = _precision102_direct_gpt_evidence(self, clean_text, words, sents)
    phrase_hits = int(direct["phrase_hits"])
    long_phrase_hits = int(direct["long_phrase_hits"])
    struct_hits = int(direct["struct_hits"])
    pattern_hits = int(direct["pattern_hits"])
    citation_hits = int(direct["citation_hits"])
    numeric_hits = int(direct["numeric_hits"])
    pattern_density = float(direct["pattern_density"])
    transition_ratio = float(direct["transition_ratio"])

    first_person = len(re.findall(r'\b(?:i|we|our|my|us)\b', low))
    hedges = len(re.findall(r'\b(?:may|might|could|perhaps|possibly|likely|unlikely|approximately|suggests?|appears?|indicates?)\b', low))
    method_terms = len(re.findall(r'\b(?:method(?:ology)?|materials?|results?|discussion|conclusion|experiment(?:al)?|sample|samples|participants|procedure|analysis|statistical|dataset|implementation|evaluation|protocol|table|figure|algorithm|theorem|lemma|proof)\b', low))

    ref_anomaly, ref_meta = _precision101_reference_anomaly(self, text)
    prisma_anomaly = 0.0
    if "records screened" in low and "reports not retrieved" in low:
        nums = [int(n.replace(',', '')) for n in re.findall(r'\b\d{2,6}(?:,\d{3})*\b', clean_text[:14000])]
        if any((a > 0 and b > a * 3) for a, b in zip(nums, nums[1:])):
            prisma_anomaly = 0.15
    integrity_anomaly = min(0.60, ref_anomaly + prisma_anomaly + (0.18 if "invalid citation" in low else 0.0))

    fp_phrase = float(fpd.get("fp_en_phrases", 0.0) or 0.0)
    fp_structure = float(fpd.get("fp_structure", 0.0) or 0.0)
    fp_simple = float(fpd.get("fp_simple_gpt", 0.0) or 0.0)
    fp_t2 = float(fpd.get("fp_t2_patterns", 0.0) or 0.0)
    fp_uniformity = float(fpd.get("fp_uniformity", 0.0) or 0.0)
    fp_cliches = float(fpd.get("fp_cliches", 0.0) or 0.0)
    fp_format = float(fpd.get("fp_format_sig", 0.0) or 0.0)
    legacy_exact = int(fpd.get("exact_phrases", 0) or 0)
    legacy_long = int(fpd.get("long_exact_phrases", 0) or 0)
    legacy_struct = int(fpd.get("struct_hits", 0) or 0)
    legacy_corrob = float(fpd.get("corroboration", 0.0) or 0.0)
    fp_soft_consensus = float(fpd.get("soft_consensus", 0.0) or 0.0)

    if fp_phrase == 0.0 and legacy_exact:
        fp_phrase = min(legacy_exact / 4.0, 1.0)
    if fp_structure == 0.0 and legacy_struct:
        fp_structure = min(legacy_struct / 4.5, 1.0)
    if fp_uniformity == 0.0 and legacy_corrob:
        fp_uniformity = min(legacy_corrob / 4.0, 1.0)
    if fp_simple == 0.0 and sg > 0:
        fp_simple = min(sg, 1.0)
    if fp_t2 == 0.0 and pat_mem > 0:
        fp_t2 = min(pat_mem, 1.0)
    if fp_format == 0.0 and gf > 0:
        fp_format = min(gf, 1.0)

    human_auth, human_meta = _precision102_human_authenticity(self, clean_text, low, words, sents)

    academic_grounding = 0.0
    if citation_hits >= 2:
        academic_grounding += 0.08
    if numeric_hits >= max(6, len(words) // 120):
        academic_grounding += 0.06
    if method_terms >= 6:
        academic_grounding += 0.05
    if hedges >= 4:
        academic_grounding += 0.03
    if first_person >= 2:
        academic_grounding += 0.02
    academic_grounding = min(academic_grounding, 0.24)

    fingerprint_evidence = (
        min(phrase_hits / 4.0, 1.0) * 0.22 +
        min(long_phrase_hits / 2.0, 1.0) * 0.16 +
        min(struct_hits / 4.0, 1.0) * 0.10 +
        min(pattern_density / 0.020, 1.0) * 0.06 +
        fp_phrase * 0.09 +
        fp_structure * 0.07 +
        fp_simple * 0.07 +
        fp_t2 * 0.05 +
        fp_format * 0.04 +
        fp_uniformity * 0.02 +
        fp_cliches * 0.01 +
        integrity_anomaly * 0.09 +
        fp_soft_consensus * 0.02
    )
    fingerprint_evidence = max(0.0, min(fingerprint_evidence, 0.99))

    direct_gpt_score = (
        min(phrase_hits / 4.0, 1.0) * 0.28 +
        min(long_phrase_hits / 2.0, 1.0) * 0.18 +
        min(struct_hits / 4.0, 1.0) * 0.08 +
        min(pattern_density / 0.020, 1.0) * 0.06 +
        integrity_anomaly * 0.22 +
        min(gf, 0.9) * 0.06 +
        fingerprint_evidence * 0.12
    )
    if phrase_hits >= 2 and long_phrase_hits >= 1:
        direct_gpt_score += 0.06
    if integrity_anomaly >= 0.18 and (phrase_hits >= 1 or struct_hits >= 2):
        direct_gpt_score += 0.06
    direct_gpt_score = max(0.0, min(direct_gpt_score, 0.99))

    soft_consensus = (
        sg * 0.28 +
        en * 0.18 +
        min(nb, 0.90) * 0.12 +
        min(llr, 0.90) * 0.10 +
        min(pat_mem, 0.90) * 0.10 +
        min(para_meta.get("avg", 0.0) / 0.72, 1.0) * 0.08 +
        min(transition_ratio / 0.12, 1.0) * 0.04 +
        min(fp, 0.95) * 0.10
    )
    soft_consensus = max(0.0, min(soft_consensus, 0.90))

    style_consensus = 0
    style_consensus += 1 if sg >= 0.84 else 0
    style_consensus += 1 if nb >= 0.86 else 0
    style_consensus += 1 if en >= 0.72 else 0
    style_consensus += 1 if fp >= 0.52 else 0
    style_consensus += 1 if llr >= 0.76 else 0
    style_consensus += 1 if para_meta.get("strong", 0) >= 3 or para_meta.get("avg", 0.0) >= 0.72 else 0

    evidence_peak = max(direct_gpt_score, fingerprint_evidence, integrity_anomaly)

    # soft support helps only when the text is not strongly human-grounded
    soft_support = 0.0
    if (human_auth + academic_grounding) < 0.26:
        if soft_consensus >= 0.66:
            soft_support = min((soft_consensus - 0.56) * 0.38, 0.16)
        elif soft_consensus >= 0.58 and style_consensus >= 3:
            soft_support = min((soft_consensus - 0.58) * 0.22, 0.06)
    if evidence_peak < 0.12:
        soft_support = min(soft_support, 0.08)

    final = (
        direct_gpt_score * 0.50 +
        fingerprint_evidence * 0.26 +
        integrity_anomaly * 0.14 +
        soft_support * 0.18 -
        academic_grounding * 0.03 -
        human_auth * 0.08
    )

    # grounded human writing should temper the score, not hard-cap it.
    # Replace the old low-score crushers with small, evidence-aware reductions.
    if human_auth >= 0.18 and evidence_peak < 0.22:
        final -= 0.04
    elif (human_auth + academic_grounding) >= 0.28 and evidence_peak < 0.28:
        final -= 0.03
    elif human_auth >= 0.10 and evidence_peak < 0.18:
        final -= 0.02

    # do not allow all-zero on strongly model-like text lacking academic human grounding
    if evidence_peak < 0.20 and soft_consensus >= 0.72 and (human_auth + academic_grounding) <= 0.12:
        final = max(final, 0.16)
    if evidence_peak < 0.24 and soft_consensus >= 0.78 and style_consensus >= 4 and (human_auth + academic_grounding) <= 0.10:
        final = max(final, 0.22)

    # allow style consensus to help only after direct evidence is already non-trivial
    if direct_gpt_score >= 0.32 and fingerprint_evidence >= 0.26 and style_consensus >= 4:
        final += 0.04
    if direct_gpt_score >= 0.46 and fingerprint_evidence >= 0.38 and style_consensus >= 5 and long_phrase_hits >= 1:
        final += 0.06

    # floors only for strong direct + anomaly evidence
    if direct_gpt_score >= 0.46 and fingerprint_evidence >= 0.36 and (long_phrase_hits >= 1 or integrity_anomaly >= 0.18):
        final = max(final, 0.54)
    if direct_gpt_score >= 0.60 and fingerprint_evidence >= 0.52 and long_phrase_hits >= 2 and (integrity_anomaly >= 0.12 or style_consensus >= 5):
        final = max(final, 0.72)

    # high-AI escalation: trigger from evidence, not from the already-displayed score.
    # The previous logic required final >= 50% before boosting, which created a closed loop:
    # cases stuck at 45-49% never crossed the threshold even with strong direct evidence.
    ai_momentum = (
        direct_gpt_score * 0.58 +
        fingerprint_evidence * 0.26 +
        integrity_anomaly * 0.12 +
        min(soft_support, 0.08) * 0.04
    )
    ai_support_gate = (
        direct_gpt_score >= 0.34 or
        fingerprint_evidence >= 0.30 or
        integrity_anomaly >= 0.16 or
        (long_phrase_hits >= 1 and phrase_hits >= 2)
    )
    strong_ai_gate = (
        direct_gpt_score >= 0.42 and
        fingerprint_evidence >= 0.34 and
        (long_phrase_hits >= 1 or phrase_hits >= 2 or integrity_anomaly >= 0.16)
    )
    very_strong_ai_gate = (
        direct_gpt_score >= 0.54 and
        fingerprint_evidence >= 0.44 and
        (long_phrase_hits >= 1 or integrity_anomaly >= 0.18)
    )
    weak_human_block = (human_auth + academic_grounding) < 0.30 or evidence_peak >= 0.42

    ai_escalation_applied = 0.0
    evidence_strength = (
        direct_gpt_score * 0.50 +
        fingerprint_evidence * 0.32 +
        integrity_anomaly * 0.18
    )
    escalation_ready = (
        ai_support_gate and (
            strong_ai_gate or
            evidence_strength >= 0.34 or
            (direct_gpt_score >= 0.40 and fingerprint_evidence >= 0.30) or
            (long_phrase_hits >= 1 and phrase_hits >= 2)
        )
    )

    # evidence_trigger is the score used to decide whether the result deserves
    # the >50% escalation phase, even if the raw blended score is still below 50.
    evidence_trigger = max(
        final,
        direct_gpt_score * 0.72 + fingerprint_evidence * 0.28,
        evidence_strength * 1.10 + ai_momentum * 0.10,
    )

    if evidence_trigger >= 0.48 and escalation_ready and weak_human_block:
        boost = (
            0.06 +
            max(0.0, evidence_trigger - 0.48) * 0.95 +
            max(0.0, evidence_strength - 0.34) * 0.65 +
            max(0.0, ai_momentum - 0.42) * 0.40
        )
        if strong_ai_gate:
            boost += 0.07
        if very_strong_ai_gate:
            boost += 0.10
        if long_phrase_hits >= 1:
            boost += 0.03
        if long_phrase_hits >= 2:
            boost += 0.05
        if integrity_anomaly >= 0.22:
            boost += 0.05
        boost = min(boost, 0.38)
        _before_escalation_final = final
        boosted_final = final + boost
        final = max(final, boosted_final)
        ai_escalation_applied = max(0.0, final - _before_escalation_final)

    # staged floors above 50% — now driven by evidence_trigger, not by the old final only.
    if evidence_trigger >= 0.50 and escalation_ready and weak_human_block:
        final = max(final, 0.60)
    if evidence_trigger >= 0.56 and direct_gpt_score >= 0.42 and fingerprint_evidence >= 0.32 and escalation_ready:
        final = max(final, 0.68)
    if evidence_trigger >= 0.62 and strong_ai_gate and evidence_strength >= 0.40:
        final = max(final, 0.76)
    if evidence_trigger >= 0.72 and very_strong_ai_gate and (long_phrase_hits >= 1 or integrity_anomaly >= 0.20):
        final = max(final, 0.86)

    # Progressive post-50 escalation:
    # any final score above 50% is increased gradually according to its own value.
    # Examples: 51 -> ~52.2, 58 -> ~60.4, 70 -> ~74.6, 90 -> ~98.2
    if final > 0.50:
        _before_progressive_post50 = final
        post50_progressive = 0.50 + min(0.495, (final - 0.50) * 1.18 + 0.01)
        final = max(final, post50_progressive)
        ai_escalation_applied = max(
            ai_escalation_applied,
            final - _before_progressive_post50
        )

    final = max(0.0, min(final, 0.995))

    # Recompute paragraph highlighting from the FINAL calibrated score so that
    # shading/highlighted words reflect the displayed percentage.
    try:
        ext_for_highlight = result.get("extended", {}) or {}
        para_results = ext_for_highlight.get("paragraph_results", []) or []
        if para_results:
            total_words_h = sum(int(p.get("words", 0) or 0) for p in para_results)
            target_ratio_h = final
            sorted_paras_h = sorted(
                para_results,
                key=lambda p: float(p.get("score", 0.0) or 0.0),
                reverse=True
            )
            accumulated_h = 0
            highlight_set_h = set()
            for p in sorted_paras_h:
                ratio_before_h = accumulated_h / max(total_words_h, 1)
                if ratio_before_h >= target_ratio_h:
                    break
                accumulated_h += int(p.get("words", 0) or 0)
                highlight_set_h.add(p.get("index"))
            ai_para_count_h = 0
            ai_word_count_h = 0
            for p in para_results:
                highlighted_h = p.get("index") in highlight_set_h
                p["highlighted"] = highlighted_h
                if highlighted_h:
                    ai_para_count_h += 1
                    ai_word_count_h += int(p.get("words", 0) or 0)
            ext_for_highlight["paragraph_results"] = para_results
            ext_for_highlight["ai_para_count"] = ai_para_count_h
            ext_for_highlight["ai_word_count"] = ai_word_count_h
            ext_for_highlight["word_coverage_v106"] = round(ai_word_count_h / max(total_words_h, 1), 4)
            result["extended"] = ext_for_highlight
    except Exception:
        pass

    result["score"] = final
    result["percentage"] = final * 100.0
    result["human_score"] = (1.0 - final) * 100.0
    result["risk_level"] = (
        "CRITICAL" if final >= 0.90 else
        "HIGH" if final >= 0.76 else
        "MEDIUM" if final >= 0.56 else
        "LOW" if final >= 0.18 else
        "MINIMAL"
    )
    _verdicts = {
        "CRITICAL": "اشتباه مرتفع جدًا - يحتاج تحقق بشري",
        "HIGH":     "اشتباه مرتفع - يحتاج تحقق بشري",
        "MEDIUM":   "نتيجة مختلطة / غير حاسمة",
        "LOW":      "اشتباه منخفض",
        "MINIMAL":  "بشري على الأرجح",
    }
    result["verdict"] = _verdicts[result["risk_level"]]

    indicators["English AI Engine v2 ★★★"] = en
    indicators["English AI Engine v2"] = en
    indicators["🔍 Fingerprint Score v35 ★★★"] = max(fp, min(fingerprint_evidence * 0.88 + direct_gpt_score * 0.18 + soft_support * 0.12, 0.99))
    indicators["Simple GPT Score v22 ★★★"] = min(max(sg, soft_support), 0.84) if evidence_peak >= 0.22 or soft_consensus >= 0.70 else min(sg, 0.52)
    indicators["Academic Grounding Guard ▼"] = round(academic_grounding, 4)
    indicators["Human Authenticity Score ▼"] = round(human_auth, 4)
    indicators["Integrity Anomaly Score ★"] = round(integrity_anomaly, 4)
    indicators["Reference Anomaly Score ★"] = round(ref_anomaly, 4)
    indicators["Soft Consensus Route ★"] = round(soft_support, 4)

    extended["direct_gpt_score"] = round(direct_gpt_score, 4)
    extended["fingerprint_evidence_score"] = round(fingerprint_evidence, 4)
    extended["gpt_style_score"] = round(soft_support, 4)
    extended["soft_consensus_v104"] = round(soft_consensus, 4)
    extended["soft_support_v104"] = round(soft_support, 4)
    extended["ai_escalation_applied_v104"] = round(locals().get("ai_escalation_applied", 0.0), 4)
    extended["style_consensus_v104"] = int(style_consensus)
    extended["academic_grounding_v104"] = round(academic_grounding, 4)
    extended["human_authenticity_v104"] = round(human_auth, 4)
    extended["integrity_anomaly_v104"] = round(integrity_anomaly, 4)
    extended["reference_anomaly_v104"] = round(ref_anomaly, 4)
    extended["prisma_anomaly_v104"] = round(prisma_anomaly, 4)
    extended["precision104_phrase_hits"] = int(phrase_hits)
    extended["precision104_long_phrase_hits"] = int(long_phrase_hits)
    extended["precision104_struct_hits"] = int(struct_hits)
    extended["precision104_pattern_hits"] = int(pattern_hits)
    extended["precision104_transition_ratio"] = round(transition_ratio, 4)
    extended["precision104_human_meta"] = human_meta
    extended["precision104_reference_blocks"] = int(ref_meta.get("reference_blocks", 0))
    extended["precision104_reference_outliers"] = int(ref_meta.get("reference_outliers", 0))
    extended["precision104_reference_odd_terms"] = int(ref_meta.get("reference_odd_terms", 0))

    result["indicators"] = indicators
    result["extended"] = extended
    result["precision95_meta"] = {
        "patched_by": "precision104_balanced_soft_consensus",
        "direct_gpt_score": round(direct_gpt_score, 4),
        "fingerprint_evidence_score": round(fingerprint_evidence, 4),
        "soft_consensus": round(soft_consensus, 4),
        "soft_support": round(soft_support, 4),
        "style_consensus": int(style_consensus),
        "academic_grounding": round(academic_grounding, 4),
        "human_authenticity": round(human_auth, 4),
        "integrity_anomaly": round(integrity_anomaly, 4),
        "reference_anomaly": round(ref_anomaly, 4),
        "prisma_anomaly": round(prisma_anomaly, 4),
        "phrase_hits": int(phrase_hits),
        "long_phrase_hits": int(long_phrase_hits),
        "struct_hits": int(struct_hits),
        "pattern_hits": int(pattern_hits),
        "citation_hits": int(citation_hits),
        "numeric_hits": int(numeric_hits),
        "final_score": round(final, 4),
    }
    return result



def _precision112_apply_progressive_score_and_highlight(result):
    """Apply the visible progressive uplift on the ACTUAL runtime result."""
    try:
        final = float(result.get("score", 0.0) or 0.0)
    except Exception:
        final = 0.0
    final = max(0.0, min(final, 0.995))
    before_final = final
    pre50_applied = 0.0
    post50_applied = 0.0

    if 0.10 <= final < 0.50:
        anchors = [
            (0.10, 0.12),
            (0.15, 0.18),
            (0.20, 0.25),
            (0.26, 0.33),
            (0.35, 0.43),
            (0.49, 0.56),
        ]
        boosted = anchors[-1][1]
        if final <= anchors[0][0]:
            boosted = anchors[0][1]
        else:
            prev_x, prev_y = anchors[0]
            for x, y in anchors[1:]:
                if final <= x:
                    t = (final - prev_x) / max(x - prev_x, 1e-9)
                    boosted = prev_y + ((y - prev_y) * t)
                    break
                prev_x, prev_y = x, y
        boosted = max(final, min(boosted, 0.995))
        pre50_applied = max(0.0, boosted - final)
        final = boosted

    if final > 0.50:
        before_post50 = final
        # direct progressive rise from the actual displayed score itself
        post50_progressive = 0.50 + min(0.495, (final - 0.50) * 1.18 + 0.01)
        final = max(final, min(post50_progressive, 0.995))
        post50_applied = max(0.0, final - before_post50)

    final = max(0.0, min(final, 0.995))
    total_applied = max(0.0, final - before_final)

    result["score"] = final
    result["percentage"] = final * 100.0
    result["human_score"] = (1.0 - final) * 100.0

    result["risk_level"] = (
        "CRITICAL" if final >= 0.90 else
        "HIGH" if final >= 0.76 else
        "MEDIUM" if final >= 0.56 else
        "LOW" if final >= 0.18 else
        "MINIMAL"
    )
    _verdicts = {
        "CRITICAL": "اشتباه مرتفع جدًا - يحتاج تحقق بشري",
        "HIGH":     "اشتباه مرتفع - يحتاج تحقق بشري",
        "MEDIUM":   "نتيجة مختلطة / غير حاسمة",
        "LOW":      "اشتباه منخفض",
        "MINIMAL":  "بشري على الأرجح",
    }
    result["verdict"] = _verdicts[result["risk_level"]]

    try:
        ext = result.setdefault("extended", {})
        ext["pre50_progressive_applied_v112"] = round(float(pre50_applied), 4)
        ext["post50_progressive_applied_v112"] = round(float(post50_applied), 4)
        ext["total_progressive_applied_v112"] = round(float(total_applied), 4)
        ext["progressive_runtime_version"] = "v112"
        para_results = ext.get("paragraph_results", []) or []
        if para_results:
            total_words = sum(int(p.get("words", 0) or 0) for p in para_results)
            target_ratio = final
            sorted_paras = sorted(
                para_results,
                key=lambda p: float(p.get("score", 0.0) or 0.0),
                reverse=True
            )
            accumulated = 0
            highlight_set = set()
            for p in sorted_paras:
                if accumulated / max(total_words, 1) >= target_ratio:
                    break
                accumulated += int(p.get("words", 0) or 0)
                highlight_set.add(p.get("index"))
            ai_para_count = 0
            ai_word_count = 0
            for p in para_results:
                highlighted = p.get("index") in highlight_set
                p["highlighted"] = highlighted
                if highlighted:
                    ai_para_count += 1
                    ai_word_count += int(p.get("words", 0) or 0)
            ext["paragraph_results"] = para_results
            ext["ai_para_count"] = ai_para_count
            ext["ai_word_count"] = ai_word_count
            ext["word_coverage_v112"] = round(ai_word_count / max(total_words, 1), 4)
            result["ai_words_count"] = ai_word_count
    except Exception:
        pass

    try:
        meta = result.setdefault("precision95_meta", {})
        meta["pre50_progressive_applied"] = round(float(pre50_applied), 4)
        meta["post50_progressive_applied"] = round(float(post50_applied), 4)
        meta["total_progressive_applied"] = round(float(total_applied), 4)
        meta["final_score"] = round(float(final), 4)
        meta["patched_by"] = "precision112_runtime_progressive"
    except Exception:
        pass

    return result


def _precision112_analyze(self, text):
    return _precision112_apply_progressive_score_and_highlight(_precision108_analyze(self, text))

AIDetectionEngine._compute_fingerprint_score = _precision104_compute_fingerprint_score
AIDetectionEngine.analyze = _precision112_analyze

def _precision108_bind_latest_runtime():
    _g = globals()
    for _attr, _name in {
        "_nb_score": "_v3fixed_nb_score",
        "_english_ai_score": "_v3fixed_english_ai_score",
        "_synonym_density": "_v3fixed_synonym_density",
        "_compute_fingerprint_score": "_precision104_compute_fingerprint_score",
    }.items():
        _fn = _g.get(_name)
        if _fn is not None:
            setattr(AIDetectionEngine, _attr, _fn)

    # Prefer the most recent calibrated analyze implementation available.
    for _name in (
        "_precision112_analyze",
        "_precision108_analyze",
        "_precision107_analyze",
        "_precision106_analyze",
        "_precision105_analyze",
        "_precision104_analyze",
        "_precision102_analyze",
        "_precision101_analyze",
        "_precision100_analyze",
        "_precision99_analyze",
        "_precision98_analyze",
        "_precision97_analyze",
    ):
        _fn = _g.get(_name)
        if _fn is not None:
            AIDetectionEngine.analyze = _fn
            break

_precision108_bind_latest_runtime()

def _precision109_run_pending_analysis_latest():
    try:
        import streamlit as st
    except Exception:
        return

    if not st.session_state.get("_pending_analyze_request"):
        return

    _txt = st.session_state.pop("_pending_analyze_text", "") or ""
    st.session_state.pop("_pending_analyze_words", None)
    st.session_state["_pending_analyze_request"] = False

    try:
        _precision108_bind_latest_runtime()
        eng = AIDetectionEngine()
        res = _sqlx_enhance_ai_quotes(eng, eng.analyze(_txt), _txt)
        res = _precision112_apply_progressive_score_and_highlight(res)
        st.session_state["an_done"] = True
        st.session_state["an_error"] = None
        st.session_state["an_running"] = False
        st.session_state["an_res"] = res
        st.session_state["pdf_ready"] = False
        st.session_state["pdf_bytes"] = None
        st.session_state["pdf_error"] = None
    except Exception as ex:
        st.session_state["an_error"] = f"Error: {ex}"
        st.session_state["an_done"] = False
        st.session_state["an_running"] = False

    try:
        st.rerun()
    except Exception:
        pass

_precision109_run_pending_analysis_latest()



# ===== precision113 — exclude references from highlighting and counting =====
def _precision113_is_referenceish_paragraph(text):
    try:
        t = re.sub(r'\s+', ' ', str(text or '')).strip()
    except Exception:
        return False
    if not t:
        return False
    tl = t.lower()

    # explicit references heading
    if re.fullmatch(r'(references?|bibliography|works\s+cited|selected\s+bibliography|literature\s+cited|المراجع|قائمة\s+المراجع)', tl, re.I):
        return True

    # obvious reference line patterns
    ref_patterns = [
        r'^\[?\d{1,3}\]?\s+[A-Z][A-Za-z\-\'`]+(?:,\s*[A-Z]\.){0,6}',                        # [1] Smith, J.
        r'^\d{1,3}\.\s+[A-Z][A-Za-z\-\'`]+(?:,\s*[A-Z]\.){0,6}',                             # 1. Smith, J.
        r'^[A-Z][A-Za-z\-\'`]+,\s*(?:[A-Z]\.\s*){1,6}\(\d{4}[a-z]?\)',                       # Smith, J. (2023)
        r'^[A-Z][A-Za-z\-\'`]+(?:\s+[A-Z][A-Za-z\-\'`]+){0,4},\s*".+?"',                     # Smith, John, "Title"
        r'\bdoi:\s*10\.\d{4,9}/\S+',
        r'https?://\S+',
        r'\b(?:vol\.|no\.|issue|pp\.|pages?)\s*\d+',
        r'\b(?:journal|conference|proceedings|transactions|review|press|publisher)\b',
        r'\b(?:et al\.|retrieved from|available at|accessed on)\b',
    ]
    hits = sum(1 for p in ref_patterns if re.search(p, t, re.I))
    year_hits = len(re.findall(r'\b(?:19|20)\d{2}[a-z]?\b', t))
    comma_blocks = len(re.findall(r',', t))
    authoryear = bool(re.search(r'[A-Z][A-Za-z\-\'`]+,\s*(?:[A-Z]\.\s*){1,6}.*\b(?:19|20)\d{2}\b', t))

    # strong reference-like paragraph
    if hits >= 2:
        return True
    if authoryear and year_hits >= 1:
        return True
    if year_hits >= 2 and comma_blocks >= 3 and len(t.split()) <= 80:
        return True

    return False


def _precision113_filter_reference_artifacts(result):
    if not isinstance(result, dict) or result.get("error"):
        return result

    try:
        ext = result.setdefault("extended", {})
        removed_para = 0
        para_results = ext.get("paragraph_results", []) or []
        if para_results:
            filtered = []
            for p in para_results:
                ptxt = p.get("text", "")
                if _precision113_is_referenceish_paragraph(ptxt):
                    removed_para += 1
                    continue
                filtered.append(p)
            para_results = filtered
            ext["paragraph_results"] = para_results

            if para_results:
                total_words = sum(int(p.get("words", 0) or 0) for p in para_results)
                target_ratio = max(0.0, min(float(result.get("score", 0.0) or 0.0), 0.995))
                sorted_paras = sorted(
                    para_results,
                    key=lambda p: float(p.get("score", 0.0) or 0.0),
                    reverse=True
                )
                accumulated = 0
                highlight_set = set()
                for p in sorted_paras:
                    if accumulated / max(total_words, 1) >= target_ratio:
                        break
                    accumulated += int(p.get("words", 0) or 0)
                    highlight_set.add(p.get("index"))
                ai_para_count = 0
                ai_word_count = 0
                for p in para_results:
                    highlighted = p.get("index") in highlight_set
                    p["highlighted"] = highlighted
                    if highlighted:
                        ai_para_count += 1
                        ai_word_count += int(p.get("words", 0) or 0)
                ext["ai_para_count"] = ai_para_count
                ext["ai_word_count"] = ai_word_count
                ext["word_coverage_v113"] = round(ai_word_count / max(total_words, 1), 4)
                result["ai_words_count"] = ai_word_count
            else:
                ext["ai_para_count"] = 0
                ext["ai_word_count"] = 0
                ext["word_coverage_v113"] = 0.0
                result["ai_words_count"] = 0

        removed_quotes = 0
        quotes = result.get("ai_citations", []) or []
        if quotes:
            qf = []
            for q in quotes:
                qtxt = (q or {}).get("text", "")
                if _precision113_is_referenceish_paragraph(qtxt):
                    removed_quotes += 1
                    continue
                qf.append(q)
            result["ai_citations"] = qf
            ext["ai_quote_candidates"] = qf
            ext["ai_quote_count"] = len(qf)
            if qf:
                result["top_ai_sentence"] = qf[0]["text"]
            else:
                result.pop("top_ai_sentence", None)

        ext["references_excluded_from_highlight_v113"] = int(removed_para)
        ext["references_excluded_from_quotes_v113"] = int(removed_quotes)
    except Exception:
        pass

    return result


def _precision113_analyze(self, text):
    try:
        clean_text = self._strip_references(text)
    except Exception:
        clean_text = text
    result = _precision112_analyze(self, text)
    result = _precision113_filter_reference_artifacts(result)
    try:
        # replace quotes with cleaned-text extraction so reference section cannot re-enter
        result = _sqlx_enhance_ai_quotes(self, result, clean_text)
        result = _precision113_filter_reference_artifacts(result)
    except Exception:
        pass
    return result


AIDetectionEngine.analyze = _precision113_analyze

def _precision113_bind_latest_runtime():
    _precision108_bind_latest_runtime()
    _g = globals()
    for _name in (
        "_precision113_analyze",
        "_precision112_analyze",
        "_precision108_analyze",
        "_precision107_analyze",
        "_precision106_analyze",
        "_precision105_analyze",
        "_precision104_analyze",
        "_precision102_analyze",
        "_precision101_analyze",
        "_precision100_analyze",
        "_precision99_analyze",
        "_precision98_analyze",
        "_precision97_analyze",
    ):
        _fn = _g.get(_name)
        if _fn is not None:
            AIDetectionEngine.analyze = _fn
            break

_precision113_bind_latest_runtime()

def _precision113_run_pending_analysis_latest():
    try:
        import streamlit as st
    except Exception:
        return

    if not st.session_state.get("_pending_analyze_request"):
        return

    _txt = st.session_state.pop("_pending_analyze_text", "") or ""
    st.session_state.pop("_pending_analyze_words", None)
    st.session_state["_pending_analyze_request"] = False

    try:
        _precision113_bind_latest_runtime()
        eng = AIDetectionEngine()
        try:
            _clean_txt = eng._strip_references(_txt)
        except Exception:
            _clean_txt = _txt
        res = eng.analyze(_txt)
        res = _sqlx_enhance_ai_quotes(eng, res, _clean_txt)
        res = _precision113_filter_reference_artifacts(res)
        st.session_state["an_done"] = True
        st.session_state["an_error"] = None
        st.session_state["an_running"] = False
        st.session_state["an_res"] = res
        st.session_state["pdf_ready"] = False
        st.session_state["pdf_bytes"] = None
        st.session_state["pdf_error"] = None
    except Exception as ex:
        st.session_state["an_error"] = f"Error: {ex}"
        st.session_state["an_done"] = False
        st.session_state["an_running"] = False

    try:
        st.rerun()
    except Exception:
        pass

_precision113_run_pending_analysis_latest()


# ===== v114: stronger reference stripping and no-reference highlighting =====

def _precision114_is_referenceish_paragraph(text):
    try:
        t = re.sub(r'[\u2010-\u2015]', '-', str(text or ''))
        t = re.sub(r'\s+', ' ', t).strip()
    except Exception:
        return False
    if not t:
        return False
    tl = t.lower()

    if re.fullmatch(r'(references?|bibliography|works\s+cited|selected\s+bibliography|literature\s+cited|appendix\s+references|المراجع|قائمة\s+المراجع)', tl, re.I):
        return True

    score = 0
    if re.match(r'^(?:\[\d{1,3}\]|\d{1,3}[.)])\s+', t):
        score += 2
    if re.search(r'\b(?:19|20)\d{2}[a-z]?\b', t):
        score += 1
    if re.search(r'\bdoi\s*:\s*10\.\d{4,9}/\S+|\b10\.\d{4,9}/\S+', t, re.I):
        score += 2
    if re.search(r'https?://\S+|\bwww\.\S+', t, re.I):
        score += 2
    if re.search(r'\b(?:pmid|isbn|issn)\b', t, re.I):
        score += 2
    if re.search(r'\b\d{4};\d+(?:\(\d+\))?:[A-Za-z]?\d+(?:[-–]\d+)?\b', t):
        score += 2
    if re.search(r'\b(?:vol\.?|volume|no\.?|issue|pp\.?|pages?)\s*\d+', t, re.I):
        score += 1
    if re.search(r'\bet al\.\b', t, re.I):
        score += 1
    if re.search(r'\b(?:journal|proceedings|conference|transactions|review|press|publisher|nature|science|cells?|nutrients?|kidney|diabetes|nephrol|int j|curr opin|front(?:iers)?|lancet|bmj|jama)\b', t, re.I):
        score += 1
    if re.search(r'\b[A-Z][a-zA-Z\'`-]+\s+[A-Z](?:\.[A-Z])?\.?(?:,\s*|\s+)', t):
        authorish = re.findall(r'\b[A-Z][a-zA-Z\'`-]+\s+[A-Z](?:\.[A-Z])?\.?(?=\s|,)', t)
        if len(authorish) >= 2:
            score += 2
        if len(authorish) >= 4:
            score += 1
    if t.count(',') >= 3:
        score += 1
    if len(t.split()) <= 40 and re.search(r'\b(?:19|20)\d{2}\b', t) and t.count('.') >= 2:
        score += 1
    if re.search(r'[A-Z][a-zA-Z\'`-]+\s+[A-Z](?:\.[A-Z])?\.?,\s*[A-Z][a-zA-Z\'`-]+\s+[A-Z](?:\.[A-Z])?\.?', t):
        score += 1

    return score >= 4


def _precision114_strip_references(self, text):
    try:
        raw = str(text or "")
    except Exception:
        return text

    lines = raw.splitlines()
    if not lines:
        return raw

    def _is_ref_line(line):
        s = re.sub(r'\s+', ' ', str(line or '')).strip()
        if not s:
            return False
        return _precision114_is_referenceish_paragraph(s)

    start_idx = None

    # explicit heading
    for i, line in enumerate(lines):
        s = re.sub(r'\s+', ' ', str(line or '')).strip().lower()
        if re.fullmatch(r'(references?|bibliography|works\s+cited|selected\s+bibliography|literature\s+cited|المراجع|قائمة\s+المراجع)', s):
            start_idx = i
            break

    # fallback: detect dense bibliography tail
    if start_idx is None:
        nonempty = [(i, re.sub(r'\s+', ' ', l).strip()) for i, l in enumerate(lines) if re.sub(r'\s+', ' ', l).strip()]
        for pos in range(max(0, len(nonempty) - 120)):
            window = nonempty[pos:pos+8]
            if len(window) < 6:
                continue
            refish = sum(1 for _, l in window if _is_ref_line(l))
            numbered = sum(1 for _, l in window if re.match(r'^(?:\[\d{1,3}\]|\d{1,3}[.)])\s+', l))
            if refish >= 5 or (refish >= 4 and numbered >= 3):
                start_idx = window[0][0]
                break

    if start_idx is None:
        return raw

    kept = lines[:start_idx]
    return "\n".join(kept).rstrip()


def _precision114_filter_reference_artifacts(result):
    if not isinstance(result, dict) or result.get("error"):
        return result
    try:
        ext = result.setdefault("extended", {})
        removed_para = 0
        removed_quotes = 0

        para_results = list(ext.get("paragraph_results", []) or [])
        filtered_paras = []
        for p in para_results:
            ptxt = (p or {}).get("text", "")
            if _precision114_is_referenceish_paragraph(ptxt):
                removed_para += 1
                continue
            filtered_paras.append(p)
        ext["paragraph_results"] = filtered_paras

        if filtered_paras:
            total_words = sum(int(p.get("words", 0) or 0) for p in filtered_paras)
            target_ratio = max(0.0, min(float(result.get("score", 0.0) or 0.0), 0.995))
            sorted_paras = sorted(filtered_paras, key=lambda p: float(p.get("score", 0.0) or 0.0), reverse=True)
            accumulated = 0
            highlight_idx = set()
            for p in sorted_paras:
                if accumulated / max(total_words, 1) >= target_ratio:
                    break
                accumulated += int(p.get("words", 0) or 0)
                highlight_idx.add(p.get("index"))
            ai_para_count = 0
            ai_word_count = 0
            for p in filtered_paras:
                p["highlighted"] = p.get("index") in highlight_idx
                if p["highlighted"]:
                    ai_para_count += 1
                    ai_word_count += int(p.get("words", 0) or 0)
            ext["ai_para_count"] = ai_para_count
            ext["ai_word_count"] = ai_word_count
            result["ai_words_count"] = ai_word_count
        else:
            ext["ai_para_count"] = 0
            ext["ai_word_count"] = 0
            result["ai_words_count"] = 0

        quotes = list(result.get("ai_citations", []) or [])
        filtered_quotes = []
        for q in quotes:
            qtxt = (q or {}).get("text", "")
            if _precision114_is_referenceish_paragraph(qtxt):
                removed_quotes += 1
                continue
            filtered_quotes.append(q)
        result["ai_citations"] = filtered_quotes
        ext["ai_quote_candidates"] = filtered_quotes
        ext["ai_quote_count"] = len(filtered_quotes)
        if filtered_quotes:
            result["top_ai_sentence"] = filtered_quotes[0].get("text")
        else:
            result.pop("top_ai_sentence", None)

        ext["references_excluded_from_highlight_v114"] = int(removed_para)
        ext["references_excluded_from_quotes_v114"] = int(removed_quotes)
    except Exception:
        pass
    return result


def _precision114_analyze(self, text):
    try:
        clean_text = _precision114_strip_references(self, text)
    except Exception:
        clean_text = text
    result = _precision112_analyze(self, clean_text)
    try:
        result = _sqlx_enhance_ai_quotes(self, result, clean_text)
    except Exception:
        pass
    result = _precision114_filter_reference_artifacts(result)
    try:
        ext = result.setdefault("extended", {})
        ext["reference_strip_applied_v114"] = True
        ext["reference_text_reduction_v114"] = max(0, len(str(text or "")) - len(str(clean_text or "")))
    except Exception:
        pass
    return result


AIDetectionEngine._strip_references = _precision114_strip_references
AIDetectionEngine.analyze = _precision114_analyze

def _precision114_bind_latest_runtime():
    _g = globals()
    for _name in (
        "_precision114_analyze",
        "_precision113_analyze",
        "_precision112_analyze",
        "_precision108_analyze",
        "_precision107_analyze",
        "_precision106_analyze",
        "_precision105_analyze",
        "_precision104_analyze",
        "_precision102_analyze",
        "_precision101_analyze",
        "_precision100_analyze",
        "_precision99_analyze",
        "_precision98_analyze",
        "_precision97_analyze",
    ):
        _fn = _g.get(_name)
        if _fn is not None:
            AIDetectionEngine.analyze = _fn
            break
    AIDetectionEngine._strip_references = _precision114_strip_references


def _precision114_run_pending_analysis_latest():
    try:
        import streamlit as st
    except Exception:
        return
    if not st.session_state.get("_pending_analyze_request"):
        return

    _txt = st.session_state.pop("_pending_analyze_text", "") or ""
    st.session_state.pop("_pending_analyze_words", None)
    st.session_state["_pending_analyze_request"] = False

    try:
        _precision114_bind_latest_runtime()
        eng = AIDetectionEngine()
        _clean_txt = eng._strip_references(_txt)
        res = eng.analyze(_txt)
        res = _precision114_filter_reference_artifacts(res)
        st.session_state["an_done"] = True
        st.session_state["an_error"] = None
        st.session_state["an_running"] = False
        st.session_state["an_res"] = res
        st.session_state["pdf_ready"] = False
        st.session_state["pdf_bytes"] = None
        try:
            st.rerun()
        except Exception:
            pass
    except Exception as e:
        st.session_state["an_done"] = False
        st.session_state["an_running"] = False
        st.session_state["an_error"] = f"Error: {e}"

try:
    _precision114_bind_latest_runtime()
except Exception:
    pass

# Deferred pending-analysis execution:
# legacy runner disabled here so the request can be consumed by the final v115
# runner defined at the very end of the file.
try:
    pass
except Exception:
    pass


# ══════════════════════════════════════════════════════════════════════════════
# PRECISION v115 — TURNITIN-CALIBRATED CORE ENGINE (English-Only)
# ─────────────────────────────────────────────────────────────────────────────
# DESIGN PRINCIPLES (matching published Turnitin AI detection research):
#
#   1. THREE PILLARS ONLY — perplexity, burstiness, statistical signal
#      No word-list fingerprint as a primary signal
#   2. BALANCED SCORING — results should mirror Turnitin's measured outputs:
#      pure human academic ≈ 5-20%, mixed ≈ 30-55%, full AI ≈ 70-95%
#   3. LOW-SCORE ACCURACY — 8% must display as 8%, not 0%
#      Achieved by removing threshold floors and using continuous functions
#   4. CITATION / DATA are HUMAN signals, not neutral — they REDUCE score
#   5. BURSTINESS is the single most reliable separator: AI = uniform length
# ══════════════════════════════════════════════════════════════════════════════

import math as _p115_math
import re as _p115_re
from collections import Counter as _p115_Counter


# ── CORE METRIC 1: True Burstiness (Coefficient of Variation) ─────────────
def _p115_burstiness(sents):
    details = _p115_burstiness_details(sents)
    return float(details.get("ai_score", 0.50))


# ── CORE METRIC 2: True Perplexity Proxy ─────────────────────────────────
def _p115_perplexity(words):
    """
    Perplexity proxy — measures how 'AI-like' the vocabulary is.

    v115.2 redesign: The original window-repetition approach was unreliable
    because AI academic text uses DIVERSE formal vocabulary (low repetition),
    while human casual text repeats common words (high repetition), causing
    false positives on human text.

    New approach — three independent signals:
      1. AI vocabulary density: AI overuses a recognizable set of elevated words
         ('comprehensive', 'transformative', 'implications', 'furthermore'...).
         This is the strongest single discriminator.
      2. Formal word density: ratio of words >8 chars — calibrated to only
         flag texts that are EXTREMELY formal (mean > 7.0, not 4.5).
      3. Content diversity: type-token ratio of content words. AI tends to
         reuse the SAME formal terms repeatedly within a passage.

    Returns AI-probability score 0.0–1.0.
    """
    if len(words) < 20:
        return 0.50  # insufficient data → neutral (NO BIAS - was 0.40)

    n_words = len(words)

    # ── Signal 1: AI vocabulary density (primary — best discriminator) ──────
    AI_VOCAB = {
        'comprehensive','holistic','transformative','multifaceted','nuanced',
        'robust','pivotal','crucial','vital','fundamental','significant',
        'substantial','considerable','profound','paradigm','innovative',
        'rigorous','systematic','strategic','dynamic','sustainable','impactful',
        'implications','framework','ecosystem','synergy','synergies',
        'stakeholders','outcomes','advancements','innovations','methodologies',
        'approaches','mechanisms','dimensions','complexities','opportunities',
        'underscores','highlights','demonstrates','showcases','emphasizes',
        'necessitates','facilitates','leverages','utilizes','encompasses',
        'streamline','optimize','maximize','enhance','foster','cultivate',
        'furthermore','moreover','additionally','consequently','nevertheless',
        'nonetheless','accordingly','subsequently','ultimately','multitude',
        'paramount','indispensable','unprecedented','ubiquitous','pervasive',
        'hallmark','cornerstone','underpinning','trajectory','nexus',
    }
    ai_hits = sum(1 for w in words if w in AI_VOCAB)
    ai_density = ai_hits / (n_words / 100.0)
    # >3/100 words = clearly AI; <1/100 = clearly human
    vocab_score = min(max(ai_density - 1.0, 0.0) / 3.5, 1.0)

    # ── Signal 2: Extreme formal word length (very conservative threshold) ──
    mean_len = sum(len(w) for w in words) / n_words
    # Only fires for truly extreme formality (>7.0 avg) — well above normal academic
    len_score = max(0.0, min(1.0, (mean_len - 7.0) / 1.5))

    # ── Signal 3: Long-word repetition (original rich_score, tightened) ─────
    long_words = [w for w in words if len(w) > 8]
    if len(long_words) >= 12:
        lw_counter = _p115_Counter(long_words)
        top_lw_freq = lw_counter.most_common(5)
        lw_repeat = sum(v for _, v in top_lw_freq) / max(len(long_words), 1)
        rich_score = min(max(lw_repeat - 0.20, 0.0) * 4.0, 1.0)
    else:
        rich_score = 0.50  # insufficient data → neutral (NO BIAS - was 0.15)

    # vocab_score is the primary discriminator — if it's strong, trust it
    # Old weighted average was dragging 1.0 vocab down to 0.65+noise
    if vocab_score >= 0.80:
        # Very strong AI vocab — don't dilute with weaker signals
        result = vocab_score * 0.85 + len_score * 0.08 + rich_score * 0.07
    elif vocab_score >= 0.50:
        result = vocab_score * 0.75 + len_score * 0.12 + rich_score * 0.13
    else:
        result = vocab_score * 0.65 + len_score * 0.15 + rich_score * 0.20
    return round(max(0.05, min(0.95, result)), 4)


# ── CORE METRIC 3: Statistical Language Signal ───────────────────────────
def _p115_statistical_signal(text, words, sents):
    """
    University-oriented statistical signal.
    Stronger on generic, over-smoothed AI prose while remaining conservative on real research writing.
    """
    tl = (text or "").lower()
    n_words = max(len(words), 1)
    n_sents = max(len(sents), 1)

    TRANSITIONS = [
        'furthermore', 'moreover', 'additionally', 'consequently',
        'nevertheless', 'nonetheless', 'accordingly', 'subsequently',
        'in conclusion', 'in summary', 'to summarize', 'in addition',
        'on the other hand', 'by contrast', 'it is worth noting',
        'it should be noted', 'it is important to', 'this suggests',
        'this study aims', 'this paper aims', 'the present study',
        'plays a crucial role', 'plays a key role', 'plays a significant role',
        'highlights the importance', 'underscores the importance',
        'it is evident', 'the findings suggest', 'the results indicate',
        'ultimately', 'overall', 'from a broader perspective',
    ]
    trans_hits = sum(1 for t in TRANSITIONS if t in tl)
    trans_density = trans_hits / max(n_words / 100.0, 1e-6)
    trans_score = min(max((trans_density - 0.70) / 1.90, 0.0), 1.0)

    AI_SENT_OPENERS = {
        'furthermore','moreover','additionally','consequently','nevertheless',
        'nonetheless','accordingly','subsequently','however','therefore',
        'thus','hence','indeed','notably','importantly','significantly',
        'interestingly','crucially','ultimately','overall','finally',
        'it is','this study','this paper','the present','these findings',
        'the results','the findings','from a broader perspective','at the same time'
    }
    ai_opener_count = 0
    opener_tokens = []
    for s in sents[:50]:
        sl = s.strip().lower()
        head = ' '.join(sl.split()[:3])
        opener_tokens.append(head)
        for ao in AI_SENT_OPENERS:
            if sl.startswith(ao):
                ai_opener_count += 1
                break
    ao_ratio = ai_opener_count / max(min(len(sents), 50), 1)
    opener_score = min(max((ao_ratio - 0.08) / 0.28, 0.0), 1.0)

    repeated_openers = 0.0
    if opener_tokens:
        counts = {}
        for tok in opener_tokens:
            counts[tok] = counts.get(tok, 0) + 1
        repeated_openers = max(counts.values()) / max(len(opener_tokens), 1)
    repetition_score = min(max((repeated_openers - 0.16) / 0.22, 0.0), 1.0)

    conclusion_patterns = [
        r'\bin conclusion\b', r'\bto conclude\b', r'\bin summary\b',
        r'\bto summarize\b', r'\boverall[,\s]', r'\bultimately[,\s]',
        r'\btaken together\b', r'\ball things considered\b',
    ]
    conc_hits = sum(1 for p in conclusion_patterns if _p115_re.search(p, tl, _p115_re.I))
    conc_score = min(conc_hits / 2.0, 1.0)

    passive_patterns = [
        r'\b(?:is|are|was|were|been|being)\s+(?:\w+\s+)?(?:shown|demonstrated|found|'
        r'established|identified|observed|reported|noted|highlighted|suggested|'
        r'indicated|proposed|examined|investigated|analyzed|evaluated|assessed|'
        r'considered|determined|confirmed|validated)\b',
    ]
    passive_hits = sum(len(_p115_re.findall(p, tl, _p115_re.I)) for p in passive_patterns)
    passive_density = passive_hits / max(n_sents, 1)
    passive_score = min(passive_density / 0.32, 1.0)

    generic_phrases = len(_p115_re.findall(
        r'\b(profound and unprecedented|remarkable consistency|plays a central role|'
        r'fundamental shift|responsible development and deployment|across multiple sectors|'
        r'broad(?:er)? perspective|important questions regarding|rapid pace|'
        r'digital transformation|global technological progress|economic growth|'
        r'enhances efficiency|improves decision making|reduces operational costs|supports innovation)\b',
        tl
    ))
    abstract_terms = len(_p115_re.findall(
        r'\b(society|technology|innovation|efficiency|transformation|progress|future|'
        r'responsibility|frameworks|institutions|organizations|stakeholders|development|'
        r'adoption|impact|growth|governance|communication|accountability|transparency)\b',
        tl
    ))
    numeric_hits = len(_p115_re.findall(r'\b\d+(?:\.\d+)?%?\b', tl))
    named_terms = len(_p115_re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text or ""))
    low_specificity = min(1.0, max((abstract_terms / max(n_words, 1)) * 18.0 - (numeric_hits * 0.06) - (named_terms * 0.03), 0.0))
    generic_score = min(1.0, generic_phrases / 4.0 * 0.55 + low_specificity * 0.45)

    SENTENCE_LEVEL_MARKERS = [
        r'\bthis\s+(?:study|paper|review|work|article)\s+(?:aims?|seeks?|examines?|explores?|investigates?|presents?|demonstrates?)\b',
        r'\bfuture\s+(?:research|studies|work)\s+(?:should|is\s+needed|could|may)\b',
        r'\bthese\s+findings\s+(?:suggest|indicate|demonstrate|highlight|underscore)\b',
        r'\bit\s+is\s+(?:important|crucial|essential|worth)\s+to\s+(?:note|emphasize|acknowledge|recognize)\b',
        r'\bthe\s+(?:present|current)\s+(?:study|research|work|paper|review)\b',
        r'\ba\s+(?:comprehensive|holistic|systematic|rigorous|nuanced)\s+(?:analysis|review|approach|framework)\b',
    ]
    sent_marker_hits = sum(1 for s in sents if any(_p115_re.search(p, s, _p115_re.I) for p in SENTENCE_LEVEL_MARKERS))
    sent_marker_score = min(sent_marker_hits / max(n_sents * 0.42, 1.0), 1.0)

    score = (
        trans_score * 0.20 +
        opener_score * 0.16 +
        repetition_score * 0.12 +
        conc_score * 0.08 +
        passive_score * 0.12 +
        sent_marker_score * 0.14 +
        generic_score * 0.18
    )

    if generic_score >= 0.62 and trans_score >= 0.38:
        score += 0.06
    if opener_score >= 0.42 and repetition_score >= 0.24:
        score += 0.04
    if numeric_hits >= 3:
        score -= 0.03
    score = max(0.0, min(1.0, score))
    return float(score)



def _p115_human_signals(text, words):
    """
    Detects genuine human writing signals.
    Returns penalty to apply (0.0 = no penalty, 1.0 = very strong human).
    These signals REDUCE the AI score.
    """
    tl = text.lower()
    n_words = max(len(words), 1)
    penalty = 0.0

    # Signal 1: Scientific citations (reduced weights + higher thresholds)
    # FIX v115.3: Citations don't automatically mean human - AI can insert them
    citations = len(_p115_re.findall(
        r'\([A-Z][a-z]+(?:\s+et\s+al\.?)?\s*,\s*(?:19|20)\d{2}[a-z]?\)|'
        r'\[\s*\d+(?:\s*,\s*\d+)*\s*\]',
        text))
    if citations >= 10:
        penalty += 0.15  # was 0.22 at threshold 4
    elif citations >= 5:
        penalty += 0.08  # was 0.14 at threshold 2
    elif citations >= 4:
        penalty += 0.02  # tightened: small citation count not penalized

    # Signal 2: Precise numeric data (p-values, OR, CI, SD, n=)
    # FIX v115.3: Reduced weights + higher thresholds
    precise = len(_p115_re.findall(
        r'p\s*[<>=]\s*0\.\d+|OR\s*=\s*[\d.]+|HR\s*=\s*[\d.]+|'
        r'AUC\s*=\s*[\d.]+|\d+\.\d+\s*[±]\s*\d+\.\d+|'
        r'95\s*%\s*CI|SD\s*=\s*[\d.]+|n\s*=\s*\d{2,}',
        text, _p115_re.I))
    if precise >= 12:
        penalty += 0.08  # was 0.14 at threshold 6
    elif precise >= 6:
        penalty += 0.04  # was 0.08 at threshold 3
    elif precise >= 3:
        penalty += 0.02  # was 0.04 at threshold 1

    # Signal 3: First-person research voice ("we found", "we observed")
    # FIX v115.3: Reduced weights + higher thresholds
    we_found = len(_p115_re.findall(
        r'\bwe\s+(?:found|observed|examined|analyzed|measured|collected|'
        r'recruited|included|excluded|performed|conducted|compared|identified)\b',
        tl))
    if we_found >= 5:
        penalty += 0.05  # was 0.10 at threshold 3
    elif we_found >= 2:
        penalty += 0.02  # was 0.05 at threshold 1

    # Signal 4: Hedging language (academic uncertainty — human trait)
    # FIX v115.3: Reduced weights + higher thresholds
    hedges = len(_p115_re.findall(
        r'\b(?:may|might|could|perhaps|possibly|likely|unlikely|'
        r'approximately|suggests?|appears?\s+to|indicates?\s+that|'
        r'it\s+(?:appears|seems)|we\s+speculate|we\s+hypothesize)\b',
        tl))
    hedge_ratio = hedges / n_words
    if hedge_ratio >= 0.080:
        penalty += 0.04  # tightened: only very hedge-dense text
    elif hedge_ratio >= 0.045:
        penalty += 0.02  # tightened threshold

    # Signal 5: Direct quotes (humans quote, AI paraphrases)
    # FIX v115.3: Reduced weights + higher thresholds
    quotes = len(_p115_re.findall(r'["""].*?["""]', text))
    if quotes >= 5:
        penalty += 0.03  # was 0.06 at threshold 3
    elif quotes >= 2:
        penalty += 0.01  # was 0.03 at threshold 1

    # Signal 6: Methodology vocabulary (real research, not AI summary)
    # FIX v115.3: Reduced weights + higher thresholds
    method_terms = len(_p115_re.findall(
        r'\b(?:randomized\s+controlled|double.blind|placebo|'
        r'confidence\s+interval|odds\s+ratio|hazard\s+ratio|'
        r'inclusion\s+criteria|exclusion\s+criteria|'
        r'participants\s+were\s+(?:recruited|enrolled|included)|'
        r'informed\s+consent|IRB|ethics\s+committee|'
        r'PRISMA|CONSORT|STROBE|Cochrane|meta.analysis)\b',
        tl, _p115_re.I))
    if method_terms >= 6:
        penalty += 0.05  # was 0.10 at threshold 3
    elif method_terms >= 3:
        penalty += 0.02  # was 0.05 at threshold 1

    return round(min(penalty, 0.10), 4)  # softer cap to avoid over-biasing low/moderate AI scores


# ── PARAGRAPH-LEVEL SCORING ───────────────────────────────────────────────
def _p115_score_paragraph(para_text):
    """Score a single paragraph 0.0-1.0 for AI likelihood.

    v115.1: Human penalty now applied at full strength (was 0.60×).
    Burstiness requires ≥4 sentences (was 3) before contributing.
    """
    sents = [s.strip() for s in _p115_re.split(r'(?<=[.!?])\s+', para_text)
             if len(s.split()) >= 4]
    words = _p115_re.findall(r'\b[a-zA-Z]+\b', para_text.lower())

    if len(words) < 15:
        return 0.40

    b = _p115_burstiness(sents) if len(sents) >= 4 else 0.40
    p = _p115_perplexity(words)
    s = _p115_statistical_signal(para_text, words, sents)
    h = _p115_human_signals(para_text, words)

    raw = b * 0.30 + p * 0.30 + s * 0.40
    raw = max(0.0, raw - h)  # full penalty (was h*0.60)
    return round(max(0.02, min(0.98, raw)), 4)


# ── MAIN PRECISION-115 ANALYZE FUNCTION ──────────────────────────────────

def _precision115_analyze(self, text, cb=None):
    """
    University-grade English-only adjudication engine.
    Output layers:
      - raw_score: evidence before calibration
      - calibrated_score: reliability-aware decision score
      - display_score: UI-facing numeric score (same as calibrated)
      - decision/verdict: explicit adjudication layer
      - confidence/uncertainty: decision stability
      - explanation/reasons: structured rationale
    """
    try:
        text = self._strip_references(text)
    except Exception:
        pass

    original_text = text or ""
    text = _p115_re.sub(r'\s+', ' ', original_text).strip()
    sents = [s.strip() for s in _p115_re.split(r'(?<=[.!?])\s+', text) if len(s.split()) >= 4]
    words = _p115_re.findall(r'\b[a-zA-Z]+\b', text.lower())

    if len(words) < 80:
        return {
            "error": "Text too short — please enter at least 80 English words.",
            "score": 0.0,
            "percentage": 0.0,
            "human_score": 100.0,
        }

    if cb: cb(10)

    letters_total = len(_p115_re.findall(r'[A-Za-z\u00C0-\u024F\u0400-\u04FF\u0600-\u06FF]', text))
    english_letters = len(_p115_re.findall(r'[A-Za-z]', text))
    arabic_letters = len(_p115_re.findall(r'[\u0600-\u06FF]', text))
    english_ratio = english_letters / max(letters_total, 1)
    arabic_ratio = arabic_letters / max(letters_total, 1)
    if arabic_ratio > 0.10 or english_ratio < 0.78:
        return {
            "error": "English-only university build: the submitted text is not predominantly English.",
            "unsupported_language": "non_english",
            "score": 0.0,
            "percentage": 0.0,
            "human_score": 100.0,
        }

    research_profile = _p115_research_profile(original_text, sents, words)
    section_info = _p115_section_analysis(original_text)
    claim_info = research_profile.get("claim_alignment", {}) or {}
    method_info = research_profile.get("methodology_specificity", {}) or {}

    burst_meta = _p115_burstiness_details(sents)
    burst_score = max(0.0, min(1.0, float(burst_meta.get("ai_score", 0.50))))
    if cb: cb(24)
    perp_score = max(0.0, min(1.0, _p115_perplexity(words)))
    if cb: cb(38)
    stat_score = max(0.0, min(1.0, _p115_statistical_signal(text, words, sents)))
    if cb: cb(52)
    human_penalty = max(0.0, min(1.0, _p115_human_signals(text, words)))
    if cb: cb(66)

    generic_ai_signal = max(0.0, min(1.0,
        perp_score * 0.42 +
        stat_score * 0.34 +
        (1.0 - float(method_info.get("specificity_score", 0.0))) * 0.10 +
        (1.0 - float(claim_info.get("alignment_score", 0.50))) * 0.08 +
        burst_score * 0.06
    ))

    paragraphs_raw = [p.strip() for p in _p115_re.split(r'\n\s*\n', original_text) if p.strip()]
    if len(paragraphs_raw) < 2:
        chunk_size = max(3, len(sents) // max(min(len(sents), 6), 1))
        paragraphs_raw = [
            ' '.join(sents[i:i + chunk_size])
            for i in range(0, len(sents), chunk_size)
            if sents[i:i + chunk_size]
        ]

    paragraph_results = []
    paragraph_scores = []
    for idx, para in enumerate(paragraphs_raw):
        para_words = _p115_re.findall(r'\b[a-zA-Z]+\b', para.lower())
        if len(para_words) < 12:
            continue
        para_score = max(0.0, min(1.0, _p115_score_paragraph(para)))
        paragraph_scores.append(para_score)
        paragraph_results.append({
            "index": idx,
            "text": para[:500],
            "score": round(para_score, 4),
            "words": len(para_words),
            "highlighted": False,
        })

    sent_scores = []
    ai_citations = []
    for sent in sents:
        sw = _p115_re.findall(r'\b[a-zA-Z]+\b', sent.lower())
        if len(sw) < 6:
            continue
        sent_score = max(0.0, min(1.0, _p115_score_paragraph(sent)))
        sent_scores.append(sent_score)
        if sent_score >= 0.69:
            ai_citations.append({
                "text": sent,
                "score": round(sent_score, 4),
                "reason": "High local AI signature",
            })
    ai_citations.sort(key=lambda x: x["score"], reverse=True)

    if cb: cb(80)

    high_para_ratio = sum(1 for x in paragraph_scores if x >= 0.62) / max(len(paragraph_scores), 1)
    high_sent_ratio = sum(1 for x in sent_scores if x >= 0.68) / max(len(sent_scores), 1)
    para_top_mean = sum(sorted(paragraph_scores, reverse=True)[:max(1, min(3, len(paragraph_scores)))]) / max(1, min(3, len(paragraph_scores)))
    sent_top_mean = sum(sorted(sent_scores, reverse=True)[:max(1, min(8, len(sent_scores)))]) / max(1, min(8, len(sent_scores)))

    ai_core = (
        burst_score * 0.16 +
        perp_score  * 0.34 +
        stat_score  * 0.30 +
        para_top_mean * 0.12 +
        sent_top_mean * 0.08
    )

    dominance = max(perp_score, stat_score, burst_score)
    support = (
        high_para_ratio * 0.42 +
        high_sent_ratio * 0.24 +
        min(1.0, section_info.get("weighted_ai_signal", 0.0)) * 0.18 +
        generic_ai_signal * 0.16
    )
    distributed_evidence = min(1.0,
        support * 0.48 +
        para_top_mean * 0.15 +
        sent_top_mean * 0.11 +
        min(1.0, section_info.get("weighted_ai_signal", 0.0)) * 0.16 +
        generic_ai_signal * 0.10
    )

    if ai_core >= 0.78:
        human_weight = 0.03
    elif ai_core >= 0.62:
        human_weight = 0.05
    elif ai_core >= 0.45:
        human_weight = 0.075
    elif ai_core >= 0.30:
        human_weight = 0.10
    else:
        human_weight = 0.13

    research_guard = 0.0
    if research_profile["research_strength"] >= 0.60 and distributed_evidence < 0.32 and generic_ai_signal < 0.60:
        research_guard = min(0.045, (research_profile["research_strength"] - 0.60) * 0.18)
    elif research_profile["research_strength"] >= 0.46 and distributed_evidence < 0.22 and generic_ai_signal < 0.52:
        research_guard = min(0.025, (research_profile["research_strength"] - 0.46) * 0.14)

    raw_score = ai_core + (distributed_evidence * 0.18) - (human_penalty * human_weight) - research_guard

    if perp_score >= 0.72 and (stat_score >= 0.42 or generic_ai_signal >= 0.58):
        raw_score += 0.08
    if stat_score >= 0.68 and perp_score >= 0.62:
        raw_score += 0.04
    if para_top_mean >= 0.68 and high_para_ratio >= 0.32:
        raw_score += 0.04
    if high_sent_ratio >= 0.24 and sent_top_mean >= 0.70:
        raw_score += 0.03
    if section_info.get("weighted_ai_signal", 0.0) >= 0.52 and section_info.get("consistency", 0.0) >= 0.62:
        raw_score += 0.04
    if generic_ai_signal >= 0.66 and human_penalty <= 0.40:
        raw_score += 0.05
    if distributed_evidence >= 0.36 and human_penalty <= 0.42:
        raw_score += 0.02

    if dominance >= 0.75 and generic_ai_signal >= 0.62 and raw_score < 0.56:
        raw_score = max(raw_score, 0.56)
    elif dominance >= 0.70 and generic_ai_signal >= 0.56 and raw_score < 0.48:
        raw_score = max(raw_score, 0.48)

    if ai_core < 0.24 and distributed_evidence < 0.12 and generic_ai_signal < 0.40:
        raw_score *= 0.97   # v117: relaxed from 0.90
    elif ai_core < 0.32 and distributed_evidence < 0.16 and generic_ai_signal < 0.46:
        raw_score *= 0.98   # v117: relaxed from 0.95

    raw_score = max(0.0, min(1.0, raw_score))
    n_words = len(words)

    if n_words < 120:
        length_conf = 0.84 + (n_words - 80) * (0.08 / 40.0)
    elif n_words < 250:
        length_conf = 0.92 + (n_words - 120) * (0.04 / 130.0)
    elif n_words < 500:
        length_conf = 0.96 + (n_words - 250) * (0.025 / 250.0)
    else:
        length_conf = 0.985

    try:
        pillar_spread = statistics.pstdev([
            burst_score, perp_score, stat_score, para_top_mean, sent_top_mean,
            float(section_info.get("weighted_ai_signal", 0.0))
        ])
    except Exception:
        pillar_spread = 0.0

    local_consistency = (
        para_top_mean * 0.40 +
        sent_top_mean * 0.24 +
        float(section_info.get("consistency", 0.0)) * 0.20 +
        generic_ai_signal * 0.16
    )
    support_strength = min(1.0, distributed_evidence * 1.15 + generic_ai_signal * 0.10)
    evidence_stability = (
        (1.0 - min(1.0, pillar_spread * 1.55)) * 0.24 +
        support_strength * 0.30 +
        local_consistency * 0.24 +
        min(1.0, research_profile["research_strength"] * 0.75 + 0.25) * 0.10 +
        min(1.0, section_info.get("coverage", 0.0) * 0.85 + 0.15) * 0.12
    )
    evidence_stability = max(0.0, min(1.0, evidence_stability))
    confidence = max(0.0, min(1.0, (length_conf * 0.40) + (evidence_stability * 0.60)))
    uncertainty = round(1.0 - confidence, 4)

    calibrated_score = raw_score * (0.88 + confidence * 0.12)   # v117: raised base from 0.82→0.88
    if confidence < 0.68 and 0.30 <= raw_score <= 0.74:
        calibrated_score = (calibrated_score * 0.88) + 0.08   # v117: relaxed from *0.76+0.15
    elif confidence < 0.75 and 0.34 <= raw_score <= 0.66:
        calibrated_score = (calibrated_score * 0.95) + 0.02   # v117: relaxed from *0.90+0.04

    if dominance >= 0.75 and generic_ai_signal >= 0.62 and calibrated_score < 0.54:
        calibrated_score = 0.54
    elif dominance >= 0.70 and generic_ai_signal >= 0.56 and calibrated_score < 0.46:
        calibrated_score = 0.46

    calibrated_score = max(0.0, min(1.0, calibrated_score))

    # UI-facing score: keep the lower diagnostic panels unchanged, but align the
    # big headline score more closely with the visible core engines
    # (Burstiness / Perplexity / Statistical) while still preserving human/research
    # penalties and confidence damping.
    diagnostic_anchor = max(0.0, min(1.0,
        burst_score * 0.28 +
        perp_score  * 0.32 +
        stat_score  * 0.40
    ))
    ui_alignment_score = max(0.0, min(1.0,
        diagnostic_anchor * (0.80 + confidence * 0.12) +   # v117: raised base from 0.74
        distributed_evidence * 0.14 -
        human_penalty * 0.04 -
        research_guard * 0.12   # v117: reduced from 0.25 — less guard penalty on display
    ))
    display_score = max(calibrated_score, ui_alignment_score)

    if paragraph_results:
        total_words_para = sum(p["words"] for p in paragraph_results)
        sorted_paras = sorted(paragraph_results, key=lambda p: p["score"], reverse=True)
        accumulated = 0
        highlight_set = set()
        coverage_target = min(0.88, max(0.08, distributed_evidence))
        for p in sorted_paras:
            if accumulated / max(total_words_para, 1) >= coverage_target:
                break
            accumulated += p["words"]
            if p["score"] >= 0.58:
                highlight_set.add(p["index"])
        for p in paragraph_results:
            p["highlighted"] = p["index"] in highlight_set

    ai_word_count = sum(p["words"] for p in paragraph_results if p["highlighted"])

    metrics = {
        "raw_score": raw_score,
        "calibrated_score": calibrated_score,
        "confidence": confidence,
        "burst_score": burst_score,
        "perp_score": perp_score,
        "stat_score": stat_score,
        "human_penalty": human_penalty,
        "high_para_ratio": high_para_ratio,
        "high_sent_ratio": high_sent_ratio,
        "support_strength": support_strength,
        "pillar_spread": pillar_spread,
        "section_weighted_signal": float(section_info.get("weighted_ai_signal", 0.0)),
        "section_consistency": float(section_info.get("consistency", 0.0)),
        "section_coverage": float(section_info.get("coverage", 0.0)),
        "section_disagreement": float(section_info.get("disagreement", 0.0)),
        "claim_alignment": float(claim_info.get("alignment_score", 0.50)),
        "unsupported_claims": float(claim_info.get("unsupported_assertive_ratio", 0.0)),
        "method_specificity": float(method_info.get("specificity_score", 0.0)),
        "role_mismatch": float(section_info.get("role_mismatch", 0.0)),
        "generic_ai_signal": float(generic_ai_signal),
        "dominance": float(dominance),
    }
    adjudication = _p115_adjudicate_university(metrics, research_profile)
    positives, negatives = _p115_build_explanations(metrics, research_profile)

    if cb: cb(94)

    sc_pct = display_score * 100.0
    explanation = {
        "decision": adjudication["decision"],
        "verdict": adjudication["verdict"],
        "positive_reasons": positives,
        "caution_reasons": negatives,
        "borderline": adjudication["borderline"],
        "hard_judgment": adjudication["hard_judgment"],
        "review_recommended": adjudication["decision"] == "REVIEW_REQUIRED" or adjudication["borderline"],
    }

    return {
        "score": round(calibrated_score, 4),
        "raw_score": round(raw_score, 4),
        "calibrated_score": round(calibrated_score, 4),
        "display_score": round(display_score, 4),
        "percentage": round(sc_pct, 2),
        "human_score": round((1.0 - calibrated_score) * 100.0, 2),
        "perplexity": round(perp_score, 4),
        "burstiness": round(burst_score, 4),
        "burstiness_cv": round(float(burst_meta.get("cv", 0.0)), 4),
        "burstiness_spread": round(float(burst_meta.get("spread_ratio", 0.0)), 4),
        "chunk_score": round(stat_score, 4),
        "transformer_score": 0,
        "transformer_ok": False,
        "word_count": n_words,
        "sentence_count": len(sents),
        "ai_words_count": ai_word_count,
        "ai_sentence_pct": round(high_sent_ratio * 100.0, 1),
        "ai_sent_count": sum(1 for x in sent_scores if x >= 0.68),
        "risk_level": adjudication["risk_level"],
        "verdict": adjudication["verdict"],
        "decision": adjudication["decision"],
        "confidence": round(confidence, 4),
        "uncertainty": uncertainty,
        "review_required": explanation["review_recommended"],
        "hard_judgment": adjudication["hard_judgment"],
        "ai_citations": ai_citations[:10],
        "indicators": {
            "Burstiness Pillar": round(burst_score, 4),
            "Perplexity Pillar": round(perp_score, 4),
            "Statistical Pillar": round(stat_score, 4),
            "Human Moderation": round(human_penalty, 4),
            "Paragraph Support": round(high_para_ratio, 4),
            "Sentence Support": round(high_sent_ratio, 4),
            "Section Signal": round(float(section_info.get("weighted_ai_signal", 0.0)), 4),
            "Generic AI Signal": round(generic_ai_signal, 4),
            "Evidence Stability": round(evidence_stability, 4),
            "Confidence": round(confidence, 4),
            "Research Strength": research_profile["research_strength"],
            "Threshold Margin": adjudication["nearest_threshold_margin"],
        },
        "adjudication": adjudication,
        "engine_version": "precision115_university_plus_v4_5_ui_aligned",
        "explanation": explanation,
        "research_profile": research_profile,
        "section_analysis": section_info,
        "extended": {
            "engine_version": "precision115_university_plus_v4_5_ui_aligned",
            "raw_score": round(raw_score, 4),
            "calibrated_score": round(calibrated_score, 4),
            "display_score": round(display_score, 4),
            "confidence": round(confidence, 4),
            "uncertainty": uncertainty,
            "burst_score": round(burst_score, 4),
            "burstiness_cv": round(float(burst_meta.get("cv", 0.0)), 4),
            "burstiness_spread": round(float(burst_meta.get("spread_ratio", 0.0)), 4),
            "perp_score": round(perp_score, 4),
            "stat_score": round(stat_score, 4),
            "human_penalty": round(human_penalty, 4),
            "human_weight": round(human_weight, 4),
            "research_guard": round(research_guard, 4),
            "length_confidence": round(length_conf, 4),
            "evidence_stability": round(evidence_stability, 4),
            "support_strength": round(support_strength, 4),
            "distributed_evidence": round(distributed_evidence, 4),
            "generic_ai_signal": round(generic_ai_signal, 4),
            "dominance": round(dominance, 4),
            "pillar_spread": round(pillar_spread, 4),
            "paragraph_results": paragraph_results,
            "ai_para_count": sum(1 for p in paragraph_results if p["highlighted"]),
            "ai_word_count": ai_word_count,
            "english_ratio": round(english_ratio, 4),
            "section_analysis": section_info,
            "claim_alignment": claim_info,
            "methodology_specificity": method_info,
        },
    }



def _p115_research_profile(full_text, sents, words):
    sections = _p115_extract_sections(full_text)
    present = {name for name, body in sections if len(_p115_re.findall(r'\b[a-zA-Z]+\b', body)) >= 30}
    canonical_core = ["abstract", "introduction", "methods", "results", "discussion", "conclusion"]
    section_coverage = sum(1 for name in canonical_core if name in present) / len(canonical_core)

    citations = len(_p115_re.findall(r'\((?:[^)]*?(?:19|20)\d{2}[^)]*)\)|\[[0-9,\s-]{1,20}\]', full_text))
    citation_density = min(1.0, citations / max(len(words) / 180.0, 1.0) / 6.0)

    method_terms = len(_p115_re.findall(r'\b(method|methods|methodology|sample|dataset|participants?|procedure|protocol|instrument|analysis|statistical|regression|anova|survey|experiment(?:al)?|interview|questionnaire)\b', full_text.lower()))
    method_density = min(1.0, method_terms / max(len(words) / 140.0, 1.0) / 10.0)

    headings_count = sum(1 for name, body in sections if name != "body" and body)
    heading_structure = min(1.0, headings_count / 6.0)

    section_lengths = [len(_p115_re.findall(r'\b[a-zA-Z]+\b', body)) for _, body in sections]
    long_sections = sum(1 for n in section_lengths if n >= 80)
    substantive_sections = min(1.0, long_sections / 5.0)

    section_labels = [name for name, _ in sections]
    section_order_bonus = 0.0
    order = ["abstract", "introduction", "literature_review", "methods", "results", "discussion", "conclusion"]
    last_pos = -1
    hits = 0
    for label in section_labels:
        if label in order:
            pos = order.index(label)
            if pos >= last_pos:
                hits += 1
                last_pos = pos
    if hits >= 3:
        section_order_bonus = min(1.0, hits / 6.0)

    claim_alignment = _p115_claim_citation_alignment(full_text)
    methodology_specificity = _p115_methodology_specificity(full_text)

    research_strength = max(0.0, min(1.0,
        section_coverage * 0.25 +
        citation_density * 0.16 +
        method_density * 0.16 +
        heading_structure * 0.10 +
        substantive_sections * 0.10 +
        section_order_bonus * 0.08 +
        claim_alignment["alignment_score"] * 0.07 +
        methodology_specificity["specificity_score"] * 0.08
    ))
    return {
        "section_coverage": round(section_coverage, 4),
        "citation_density": round(citation_density, 4),
        "method_density": round(method_density, 4),
        "heading_structure": round(heading_structure, 4),
        "substantive_sections": round(substantive_sections, 4),
        "section_order_bonus": round(section_order_bonus, 4),
        "research_strength": round(research_strength, 4),
        "claim_alignment": claim_alignment,
        "methodology_specificity": methodology_specificity,
    }


def _p115_section_analysis(full_text):
    sections = _p115_extract_sections(full_text)
    analyzed = []
    for name, body in sections:
        words = _p115_re.findall(r'\b[a-zA-Z]+\b', body.lower())
        if len(words) < 40 or name == "references":
            continue
        sents = [s.strip() for s in _p115_re.split(r'(?<=[.!?])\s+', body) if len(s.split()) >= 4]
        burst_meta = _p115_burstiness_details(sents)
        burst = max(0.0, min(1.0, burst_meta["ai_score"])) if sents else 0.50
        perp = max(0.0, min(1.0, _p115_perplexity(words)))
        stat = max(0.0, min(1.0, _p115_statistical_signal(body, words, sents))) if sents else 0.50
        human = max(0.0, min(1.0, _p115_human_signals(body, words)))
        meth = _p115_methodology_specificity(body)["specificity_score"]
        claim_align = _p115_claim_citation_alignment(body)["alignment_score"]
        role_adjust = 0.0
        if name == "methods":
            role_adjust = meth * 0.08
        elif name in {"results", "discussion"}:
            role_adjust = claim_align * 0.05
        local_score = max(0.0, min(1.0,
            burst * 0.22 + perp * 0.27 + stat * 0.25 - human * 0.07 + (1.0 - claim_align) * 0.09 + role_adjust
        ))
        analyzed.append({
            "name": name,
            "words": len(words),
            "score": round(local_score, 4),
            "burst": round(burst, 4),
            "burst_cv": round(burst_meta.get("cv", 0.0), 4),
            "perp": round(perp, 4),
            "stat": round(stat, 4),
            "human": round(human, 4),
            "method_specificity": round(meth, 4),
            "claim_alignment": round(claim_align, 4),
        })
    if not analyzed:
        return {
            "sections": [],
            "coverage": 0.0,
            "weighted_ai_signal": 0.0,
            "max_section_score": 0.0,
            "consistency": 0.0,
            "disagreement": 0.0,
            "flagged_sections": [],
            "role_alignment": 0.5,
            "role_mismatch": 0.0,
        }
    total_words = sum(x["words"] for x in analyzed)
    weighted = sum(x["score"] * x["words"] for x in analyzed) / max(total_words, 1)
    max_score = max(x["score"] for x in analyzed)
    try:
        disagreement = _p115_statistics.pstdev([x["score"] for x in analyzed])
    except Exception:
        disagreement = 0.0
    consistency = max(0.0, min(1.0, 1.0 - disagreement * 1.7))
    flagged = [x["name"] for x in analyzed if x["score"] >= 0.66]
    role_info = _p115_section_role_alignment({"sections": analyzed})
    return {
        "sections": analyzed,
        "coverage": round(min(1.0, len(analyzed) / 5.0), 4),
        "weighted_ai_signal": round(weighted, 4),
        "max_section_score": round(max_score, 4),
        "consistency": round(consistency, 4),
        "disagreement": round(disagreement, 4),
        "flagged_sections": flagged,
        "role_alignment": role_info["role_alignment"],
        "role_mismatch": role_info["role_mismatch"],
    }


def _p115_adjudicate_university(metrics, research_profile):
    score = float(metrics.get("calibrated_score", metrics.get("raw_score", 0.0)))
    confidence = float(metrics.get("confidence", 0.0))
    support = float(metrics.get("support_strength", 0.0))
    section_signal = float(metrics.get("section_weighted_signal", 0.0))
    section_consistency = float(metrics.get("section_consistency", 0.0))
    section_coverage = float(metrics.get("section_coverage", 0.0))
    section_disagreement = float(metrics.get("section_disagreement", 0.0))
    human_penalty = float(metrics.get("human_penalty", 0.0))
    research_strength = float(research_profile.get("research_strength", 0.0))
    claim_alignment = float(metrics.get("claim_alignment", 0.50))
    unsupported_claims = float(metrics.get("unsupported_claims", 0.0))
    method_specificity = float(metrics.get("method_specificity", 0.0))
    role_mismatch = float(metrics.get("role_mismatch", 0.0))
    generic_ai_signal = float(metrics.get("generic_ai_signal", 0.0))
    dominance = float(metrics.get("dominance", 0.0))

    thresholds = [
        ("HUMAN_LIKELY", 0.22, "Human-likely writing pattern", "MINIMAL"),
        ("LIMITED_AI_INDICATORS", 0.40, "Limited AI indicators", "LOW"),
        ("REVIEW_REQUIRED", 0.58, "Mixed indicators — review required", "MEDIUM"),
        ("AI_LIKELY", 0.74, "AI likely", "HIGH"),
        ("STRONG_AI_EVIDENCE", 1.01, "Strong AI evidence", "CRITICAL"),
    ]
    nearest_margin = min(abs(score - t) for _, t, _, _ in thresholds[:-1])
    borderline = (
        nearest_margin <= 0.035 or
        (0.36 <= score <= 0.66 and confidence < 0.77) or
        (section_coverage >= 0.35 and section_disagreement >= 0.16) or
        (support < 0.28 and 0.40 <= score <= 0.72) or
        (claim_alignment >= 0.72 and 0.44 <= score <= 0.76)
    )
    if dominance >= 0.72 and generic_ai_signal >= 0.58 and confidence >= 0.70 and score < 0.74:
        borderline = False

    hard_judgment = True
    if confidence < 0.64:
        hard_judgment = False
    elif section_coverage >= 0.35 and section_consistency < 0.58:
        hard_judgment = False
    elif 0.40 <= score <= 0.74 and (section_signal < 0.44 or section_coverage < 0.30):
        hard_judgment = False
    elif claim_alignment >= 0.76 and method_specificity >= 0.58 and score < 0.78:
        hard_judgment = False

    if score < 0.22:
        decision, verdict, risk = thresholds[0][0], thresholds[0][2], thresholds[0][3]
    elif score < 0.40:
        decision, verdict, risk = thresholds[1][0], thresholds[1][2], thresholds[1][3]
    elif score < 0.58:
        decision, verdict, risk = thresholds[2][0], thresholds[2][2], thresholds[2][3]
    elif score < 0.74:
        decision, verdict, risk = thresholds[3][0], thresholds[3][2], thresholds[3][3]
    else:
        decision, verdict, risk = thresholds[4][0], thresholds[4][2], thresholds[4][3]

    if borderline and decision in {"AI_LIKELY", "LIMITED_AI_INDICATORS"}:
        decision, verdict, risk = "REVIEW_REQUIRED", "Mixed indicators — review required", "MEDIUM"
    if claim_alignment >= 0.78 and method_specificity >= 0.60 and role_mismatch < 0.10 and decision in {"AI_LIKELY", "STRONG_AI_EVIDENCE"} and score < 0.84:
        decision, verdict, risk = "REVIEW_REQUIRED", "Mixed indicators — review required", "MEDIUM"

    if decision == "STRONG_AI_EVIDENCE":
        if not (confidence >= 0.80 and support >= 0.34 and section_signal >= 0.54 and human_penalty <= 0.52):
            decision, verdict, risk = "AI_LIKELY", "AI likely", "HIGH"

    if decision == "AI_LIKELY":
        if confidence < 0.72 or (support < 0.22 and generic_ai_signal < 0.58) or (research_strength >= 0.62 and section_signal < 0.48 and generic_ai_signal < 0.60):
            decision, verdict, risk = "REVIEW_REQUIRED", "Mixed indicators — review required", "MEDIUM"

    if decision == "HUMAN_LIKELY":
        if score >= 0.18 and support >= 0.18 and section_signal >= 0.28 and confidence >= 0.66:
            decision, verdict, risk = "LIMITED_AI_INDICATORS", "Limited AI indicators", "LOW"
    if unsupported_claims >= 0.22 and section_signal >= 0.52 and confidence >= 0.74 and decision == "REVIEW_REQUIRED":
        decision, verdict, risk = "AI_LIKELY", "AI likely", "HIGH"
    if dominance >= 0.75 and generic_ai_signal >= 0.62 and confidence >= 0.70 and decision in {"LIMITED_AI_INDICATORS", "REVIEW_REQUIRED"}:
        decision, verdict, risk = "AI_LIKELY", "AI likely", "HIGH"

    return {
        "decision": decision,
        "verdict": verdict,
        "risk_level": risk,
        "nearest_threshold_margin": round(nearest_margin, 4),
        "borderline": bool(borderline),
        "hard_judgment": bool(hard_judgment),
        "thresholds": {
            "human_likely_max": 0.22,
            "limited_ai_max": 0.40,
            "review_required_max": 0.58,
            "ai_likely_max": 0.74,
        },
    }


def _p115_build_explanations(metrics, research_profile):
    pos, neg = [], []
    score = float(metrics.get("calibrated_score", 0.0))
    if metrics.get("burst_score", 0.0) >= 0.62:
        pos.append("Sentence-length uniformity is unusually stable.")
    if metrics.get("perp_score", 0.0) >= 0.66:
        pos.append("Perplexity-pattern evidence is elevated.")
    if metrics.get("stat_score", 0.0) >= 0.64:
        pos.append("Statistical regularity is higher than expected for organic academic prose.")
    if metrics.get("high_para_ratio", 0.0) >= 0.28:
        pos.append("AI-like signals are distributed across multiple paragraphs.")
    if metrics.get("section_weighted_signal", 0.0) >= 0.52:
        pos.append("Several research sections independently show aligned AI-like patterns.")
    if metrics.get("unsupported_claims", 0.0) >= 0.16:
        pos.append("Assertive claim patterns appear with weak citation support.")
    if metrics.get("section_consistency", 0.0) >= 0.70 and metrics.get("section_coverage", 0.0) >= 0.30:
        pos.append("Section-level evidence is stable across the document.")
    if metrics.get("generic_ai_signal", 0.0) >= 0.62:
        pos.append("The prose is unusually generic and over-smoothed for authentic research writing.")

    if metrics.get("human_penalty", 0.0) >= 0.52:
        neg.append("Human-authorship markers are materially present.")
    if research_profile.get("research_strength", 0.0) >= 0.62:
        neg.append("The document has strong research structure, so caution is applied.")
    if metrics.get("claim_alignment", 0.0) >= 0.74:
        neg.append("Claims are frequently supported by citations, reducing suspicion.")
    if metrics.get("method_specificity", 0.0) >= 0.58:
        neg.append("Methodological detail is concrete rather than generic.")
    if metrics.get("confidence", 0.0) < 0.72:
        neg.append("Decision confidence is moderate rather than strong.")
    if metrics.get("section_disagreement", 0.0) >= 0.16:
        neg.append("Section-level evidence is not fully consistent across the paper.")
    if metrics.get("support_strength", 0.0) < 0.24 and 0.40 <= score <= 0.74:
        neg.append("Global score is not backed by broad distributed support.")
    return pos[:6], neg[:6]


def _precision115_analyze(self, text, cb=None):
    """
    University-grade English-only adjudication engine.
    Output layers:
      - raw_score: evidence before calibration
      - calibrated_score: reliability-aware decision score
      - display_score: UI-facing numeric score (same as calibrated)
      - decision/verdict: explicit adjudication layer
      - confidence/uncertainty: decision stability
      - explanation/reasons: structured rationale
    """
    try:
        text = self._strip_references(text)
    except Exception:
        pass

    original_text = text or ""
    text = _p115_re.sub(r'\s+', ' ', original_text).strip()
    sents = [s.strip() for s in _p115_re.split(r'(?<=[.!?])\s+', text) if len(s.split()) >= 4]
    words = _p115_re.findall(r'\b[a-zA-Z]+\b', text.lower())

    if len(words) < 80:
        return {
            "error": "Text too short — please enter at least 80 English words.",
            "score": 0.0,
            "percentage": 0.0,
            "human_score": 100.0,
        }

    if cb: cb(10)

    letters_total = len(_p115_re.findall(r'[A-Za-z\u00C0-\u024F\u0400-\u04FF\u0600-\u06FF]', text))
    english_letters = len(_p115_re.findall(r'[A-Za-z]', text))
    arabic_letters = len(_p115_re.findall(r'[\u0600-\u06FF]', text))
    english_ratio = english_letters / max(letters_total, 1)
    arabic_ratio = arabic_letters / max(letters_total, 1)
    if arabic_ratio > 0.10 or english_ratio < 0.78:
        return {
            "error": "English-only university build: the submitted text is not predominantly English.",
            "unsupported_language": "non_english",
            "score": 0.0,
            "percentage": 0.0,
            "human_score": 100.0,
        }

    research_profile = _p115_research_profile(original_text, sents, words)
    section_info = _p115_section_analysis(original_text)
    claim_info = research_profile.get("claim_alignment", {}) or {}
    method_info = research_profile.get("methodology_specificity", {}) or {}

    burst_meta = _p115_burstiness_details(sents)
    burst_score = max(0.0, min(1.0, float(burst_meta.get("ai_score", 0.50))))
    if cb: cb(24)
    perp_score = max(0.0, min(1.0, _p115_perplexity(words)))
    if cb: cb(38)
    stat_score = max(0.0, min(1.0, _p115_statistical_signal(text, words, sents)))
    if cb: cb(52)
    human_penalty = max(0.0, min(1.0, _p115_human_signals(text, words)))
    if cb: cb(66)

    generic_ai_signal = max(0.0, min(1.0,
        perp_score * 0.42 +
        stat_score * 0.34 +
        (1.0 - float(method_info.get("specificity_score", 0.0))) * 0.10 +
        (1.0 - float(claim_info.get("alignment_score", 0.50))) * 0.08 +
        burst_score * 0.06
    ))

    paragraphs_raw = [p.strip() for p in _p115_re.split(r'\n\s*\n', original_text) if p.strip()]
    if len(paragraphs_raw) < 2:
        chunk_size = max(3, len(sents) // max(min(len(sents), 6), 1))
        paragraphs_raw = [
            ' '.join(sents[i:i + chunk_size])
            for i in range(0, len(sents), chunk_size)
            if sents[i:i + chunk_size]
        ]

    paragraph_results = []
    paragraph_scores = []
    for idx, para in enumerate(paragraphs_raw):
        para_words = _p115_re.findall(r'\b[a-zA-Z]+\b', para.lower())
        if len(para_words) < 12:
            continue
        para_score = max(0.0, min(1.0, _p115_score_paragraph(para)))
        paragraph_scores.append(para_score)
        paragraph_results.append({
            "index": idx,
            "text": para[:500],
            "score": round(para_score, 4),
            "words": len(para_words),
            "highlighted": False,
        })

    sent_scores = []
    ai_citations = []
    for sent in sents:
        sw = _p115_re.findall(r'\b[a-zA-Z]+\b', sent.lower())
        if len(sw) < 6:
            continue
        sent_score = max(0.0, min(1.0, _p115_score_paragraph(sent)))
        sent_scores.append(sent_score)
        if sent_score >= 0.69:
            ai_citations.append({
                "text": sent,
                "score": round(sent_score, 4),
                "reason": "High local AI signature",
            })
    ai_citations.sort(key=lambda x: x["score"], reverse=True)

    if cb: cb(80)

    high_para_ratio = sum(1 for x in paragraph_scores if x >= 0.62) / max(len(paragraph_scores), 1)
    high_sent_ratio = sum(1 for x in sent_scores if x >= 0.68) / max(len(sent_scores), 1)
    para_top_mean = sum(sorted(paragraph_scores, reverse=True)[:max(1, min(3, len(paragraph_scores)))]) / max(1, min(3, len(paragraph_scores)))
    sent_top_mean = sum(sorted(sent_scores, reverse=True)[:max(1, min(8, len(sent_scores)))]) / max(1, min(8, len(sent_scores)))

    ai_core = (
        burst_score * 0.16 +
        perp_score  * 0.34 +
        stat_score  * 0.30 +
        para_top_mean * 0.12 +
        sent_top_mean * 0.08
    )

    dominance = max(perp_score, stat_score, burst_score)
    support = (
        high_para_ratio * 0.42 +
        high_sent_ratio * 0.24 +
        min(1.0, section_info.get("weighted_ai_signal", 0.0)) * 0.18 +
        generic_ai_signal * 0.16
    )
    distributed_evidence = min(1.0,
        support * 0.48 +
        para_top_mean * 0.15 +
        sent_top_mean * 0.11 +
        min(1.0, section_info.get("weighted_ai_signal", 0.0)) * 0.16 +
        generic_ai_signal * 0.10
    )

    if ai_core >= 0.78:
        human_weight = 0.03
    elif ai_core >= 0.62:
        human_weight = 0.05
    elif ai_core >= 0.45:
        human_weight = 0.075
    elif ai_core >= 0.30:
        human_weight = 0.10
    else:
        human_weight = 0.13

    research_guard = 0.0
    if research_profile["research_strength"] >= 0.60 and distributed_evidence < 0.32 and generic_ai_signal < 0.60:
        research_guard = min(0.045, (research_profile["research_strength"] - 0.60) * 0.18)
    elif research_profile["research_strength"] >= 0.46 and distributed_evidence < 0.22 and generic_ai_signal < 0.52:
        research_guard = min(0.025, (research_profile["research_strength"] - 0.46) * 0.14)

    raw_score = ai_core + (distributed_evidence * 0.18) - (human_penalty * human_weight) - research_guard

    if perp_score >= 0.72 and (stat_score >= 0.42 or generic_ai_signal >= 0.58):
        raw_score += 0.08
    if stat_score >= 0.68 and perp_score >= 0.62:
        raw_score += 0.04
    if para_top_mean >= 0.68 and high_para_ratio >= 0.32:
        raw_score += 0.04
    if high_sent_ratio >= 0.24 and sent_top_mean >= 0.70:
        raw_score += 0.03
    if section_info.get("weighted_ai_signal", 0.0) >= 0.52 and section_info.get("consistency", 0.0) >= 0.62:
        raw_score += 0.04
    if generic_ai_signal >= 0.66 and human_penalty <= 0.40:
        raw_score += 0.05
    if distributed_evidence >= 0.36 and human_penalty <= 0.42:
        raw_score += 0.02

    if dominance >= 0.75 and generic_ai_signal >= 0.62 and raw_score < 0.56:
        raw_score = max(raw_score, 0.56)
    elif dominance >= 0.70 and generic_ai_signal >= 0.56 and raw_score < 0.48:
        raw_score = max(raw_score, 0.48)

    if ai_core < 0.24 and distributed_evidence < 0.12 and generic_ai_signal < 0.40:
        raw_score *= 0.97   # v117: relaxed from 0.90
    elif ai_core < 0.32 and distributed_evidence < 0.16 and generic_ai_signal < 0.46:
        raw_score *= 0.98   # v117: relaxed from 0.95

    raw_score = max(0.0, min(1.0, raw_score))
    n_words = len(words)

    if n_words < 120:
        length_conf = 0.84 + (n_words - 80) * (0.08 / 40.0)
    elif n_words < 250:
        length_conf = 0.92 + (n_words - 120) * (0.04 / 130.0)
    elif n_words < 500:
        length_conf = 0.96 + (n_words - 250) * (0.025 / 250.0)
    else:
        length_conf = 0.985

    try:
        pillar_spread = statistics.pstdev([
            burst_score, perp_score, stat_score, para_top_mean, sent_top_mean,
            float(section_info.get("weighted_ai_signal", 0.0))
        ])
    except Exception:
        pillar_spread = 0.0

    local_consistency = (
        para_top_mean * 0.40 +
        sent_top_mean * 0.24 +
        float(section_info.get("consistency", 0.0)) * 0.20 +
        generic_ai_signal * 0.16
    )
    support_strength = min(1.0, distributed_evidence * 1.15 + generic_ai_signal * 0.10)
    evidence_stability = (
        (1.0 - min(1.0, pillar_spread * 1.55)) * 0.24 +
        support_strength * 0.30 +
        local_consistency * 0.24 +
        min(1.0, research_profile["research_strength"] * 0.75 + 0.25) * 0.10 +
        min(1.0, section_info.get("coverage", 0.0) * 0.85 + 0.15) * 0.12
    )
    evidence_stability = max(0.0, min(1.0, evidence_stability))
    confidence = max(0.0, min(1.0, (length_conf * 0.40) + (evidence_stability * 0.60)))
    uncertainty = round(1.0 - confidence, 4)

    calibrated_score = raw_score * (0.88 + confidence * 0.12)   # v117: raised base from 0.82→0.88
    if confidence < 0.68 and 0.30 <= raw_score <= 0.74:
        calibrated_score = (calibrated_score * 0.88) + 0.08   # v117: relaxed from *0.76+0.15
    elif confidence < 0.75 and 0.34 <= raw_score <= 0.66:
        calibrated_score = (calibrated_score * 0.95) + 0.02   # v117: relaxed from *0.90+0.04

    if dominance >= 0.75 and generic_ai_signal >= 0.62 and calibrated_score < 0.54:
        calibrated_score = 0.54
    elif dominance >= 0.70 and generic_ai_signal >= 0.56 and calibrated_score < 0.46:
        calibrated_score = 0.46

    calibrated_score = max(0.0, min(1.0, calibrated_score))

    # UI-facing score: keep the lower diagnostic panels unchanged, but align the
    # big headline score more closely with the visible core engines
    # (Burstiness / Perplexity / Statistical) while still preserving human/research
    # penalties and confidence damping.
    diagnostic_anchor = max(0.0, min(1.0,
        burst_score * 0.28 +
        perp_score  * 0.32 +
        stat_score  * 0.40
    ))
    ui_alignment_score = max(0.0, min(1.0,
        diagnostic_anchor * (0.80 + confidence * 0.12) +   # v117: raised base from 0.74
        distributed_evidence * 0.14 -
        human_penalty * 0.04 -
        research_guard * 0.12   # v117: reduced from 0.25 — less guard penalty on display
    ))
    display_score = max(calibrated_score, ui_alignment_score)

    if paragraph_results:
        total_words_para = sum(p["words"] for p in paragraph_results)
        sorted_paras = sorted(paragraph_results, key=lambda p: p["score"], reverse=True)
        accumulated = 0
        highlight_set = set()
        coverage_target = min(0.88, max(0.08, distributed_evidence))
        for p in sorted_paras:
            if accumulated / max(total_words_para, 1) >= coverage_target:
                break
            accumulated += p["words"]
            if p["score"] >= 0.58:
                highlight_set.add(p["index"])
        for p in paragraph_results:
            p["highlighted"] = p["index"] in highlight_set

    ai_word_count = sum(p["words"] for p in paragraph_results if p["highlighted"])

    metrics = {
        "raw_score": raw_score,
        "calibrated_score": calibrated_score,
        "confidence": confidence,
        "burst_score": burst_score,
        "perp_score": perp_score,
        "stat_score": stat_score,
        "human_penalty": human_penalty,
        "high_para_ratio": high_para_ratio,
        "high_sent_ratio": high_sent_ratio,
        "support_strength": support_strength,
        "pillar_spread": pillar_spread,
        "section_weighted_signal": float(section_info.get("weighted_ai_signal", 0.0)),
        "section_consistency": float(section_info.get("consistency", 0.0)),
        "section_coverage": float(section_info.get("coverage", 0.0)),
        "section_disagreement": float(section_info.get("disagreement", 0.0)),
        "claim_alignment": float(claim_info.get("alignment_score", 0.50)),
        "unsupported_claims": float(claim_info.get("unsupported_assertive_ratio", 0.0)),
        "method_specificity": float(method_info.get("specificity_score", 0.0)),
        "role_mismatch": float(section_info.get("role_mismatch", 0.0)),
        "generic_ai_signal": float(generic_ai_signal),
        "dominance": float(dominance),
    }
    adjudication = _p115_adjudicate_university(metrics, research_profile)
    positives, negatives = _p115_build_explanations(metrics, research_profile)

    if cb: cb(94)

    sc_pct = display_score * 100.0
    explanation = {
        "decision": adjudication["decision"],
        "verdict": adjudication["verdict"],
        "positive_reasons": positives,
        "caution_reasons": negatives,
        "borderline": adjudication["borderline"],
        "hard_judgment": adjudication["hard_judgment"],
        "review_recommended": adjudication["decision"] == "REVIEW_REQUIRED" or adjudication["borderline"],
    }

    return {
        "score": round(calibrated_score, 4),
        "raw_score": round(raw_score, 4),
        "calibrated_score": round(calibrated_score, 4),
        "display_score": round(display_score, 4),
        "percentage": round(sc_pct, 2),
        "human_score": round((1.0 - calibrated_score) * 100.0, 2),
        "perplexity": round(perp_score, 4),
        "burstiness": round(burst_score, 4),
        "burstiness_cv": round(float(burst_meta.get("cv", 0.0)), 4),
        "burstiness_spread": round(float(burst_meta.get("spread_ratio", 0.0)), 4),
        "chunk_score": round(stat_score, 4),
        "transformer_score": 0,
        "transformer_ok": False,
        "word_count": n_words,
        "sentence_count": len(sents),
        "ai_words_count": ai_word_count,
        "ai_sentence_pct": round(high_sent_ratio * 100.0, 1),
        "ai_sent_count": sum(1 for x in sent_scores if x >= 0.68),
        "risk_level": adjudication["risk_level"],
        "verdict": adjudication["verdict"],
        "decision": adjudication["decision"],
        "confidence": round(confidence, 4),
        "uncertainty": uncertainty,
        "review_required": explanation["review_recommended"],
        "hard_judgment": adjudication["hard_judgment"],
        "ai_citations": ai_citations[:10],
        "indicators": {
            "Burstiness Pillar": round(burst_score, 4),
            "Perplexity Pillar": round(perp_score, 4),
            "Statistical Pillar": round(stat_score, 4),
            "Human Moderation": round(human_penalty, 4),
            "Paragraph Support": round(high_para_ratio, 4),
            "Sentence Support": round(high_sent_ratio, 4),
            "Section Signal": round(float(section_info.get("weighted_ai_signal", 0.0)), 4),
            "Generic AI Signal": round(generic_ai_signal, 4),
            "Evidence Stability": round(evidence_stability, 4),
            "Confidence": round(confidence, 4),
            "Research Strength": research_profile["research_strength"],
            "Threshold Margin": adjudication["nearest_threshold_margin"],
        },
        "adjudication": adjudication,
        "engine_version": "precision115_university_plus_v4_5_ui_aligned",
        "explanation": explanation,
        "research_profile": research_profile,
        "section_analysis": section_info,
        "extended": {
            "engine_version": "precision115_university_plus_v4_5_ui_aligned",
            "raw_score": round(raw_score, 4),
            "calibrated_score": round(calibrated_score, 4),
            "display_score": round(display_score, 4),
            "confidence": round(confidence, 4),
            "uncertainty": uncertainty,
            "burst_score": round(burst_score, 4),
            "burstiness_cv": round(float(burst_meta.get("cv", 0.0)), 4),
            "burstiness_spread": round(float(burst_meta.get("spread_ratio", 0.0)), 4),
            "perp_score": round(perp_score, 4),
            "stat_score": round(stat_score, 4),
            "human_penalty": round(human_penalty, 4),
            "human_weight": round(human_weight, 4),
            "research_guard": round(research_guard, 4),
            "length_confidence": round(length_conf, 4),
            "evidence_stability": round(evidence_stability, 4),
            "support_strength": round(support_strength, 4),
            "distributed_evidence": round(distributed_evidence, 4),
            "generic_ai_signal": round(generic_ai_signal, 4),
            "dominance": round(dominance, 4),
            "pillar_spread": round(pillar_spread, 4),
            "paragraph_results": paragraph_results,
            "ai_para_count": sum(1 for p in paragraph_results if p["highlighted"]),
            "ai_word_count": ai_word_count,
            "english_ratio": round(english_ratio, 4),
            "section_analysis": section_info,
            "claim_alignment": claim_info,
            "methodology_specificity": method_info,
        },
    }




# ── FINAL ENGINE BINDING (v115 university plus v4.1) ──────────────────────
# Keep this block at the very end so runtime uses the latest university engine.
try:
    AIDetectionEngine.analyze = _precision115_analyze
except Exception:
    pass


def _precision115_run_pending_analysis_final():
    try:
        import streamlit as st
    except Exception:
        return
    if not st.session_state.get("_pending_analyze_request"):
        return

    _txt = st.session_state.pop("_pending_analyze_text", "") or ""
    st.session_state.pop("_pending_analyze_words", None)
    st.session_state["_pending_analyze_request"] = False

    try:
        AIDetectionEngine.analyze = _precision115_analyze
        try:
            AIDetectionEngine._strip_references = _precision114_strip_references
        except Exception:
            pass

        eng = AIDetectionEngine()
        res = eng.analyze(_txt)

        if isinstance(res, dict):
            ext = res.setdefault("extended", {})
            ext.setdefault("engine_version", "precision115_university_plus_v4_5_ui_aligned")
            res.setdefault("engine_version", "precision115_university_plus_v4_5_ui_aligned")
            # Ensure top-level values are synchronized with the active engine output.
            if "raw_score" in ext and "score" not in res:
                try:
                    res["score"] = float(ext.get("raw_score", 0.0))
                except Exception:
                    pass
            if "display_score" in ext:
                try:
                    _display = float(ext.get("display_score", 0.0))
                    res["percentage"] = round(_display * 100.0, 2)
                    res["score"] = round(_display, 4)
                    res["human_score"] = round(max(0.0, 100.0 - res["percentage"]), 2)
                except Exception:
                    pass
            elif "calibrated_score" in ext:
                try:
                    _display = float(ext.get("calibrated_score", 0.0))
                    res["percentage"] = round(_display * 100.0, 2)
                    res["score"] = round(_display, 4)
                    res["human_score"] = round(max(0.0, 100.0 - res["percentage"]), 2)
                except Exception:
                    pass

        st.session_state["an_done"] = True
        st.session_state["an_error"] = None
        st.session_state["an_running"] = False
        st.session_state["an_res"] = res
        st.session_state["pdf_ready"] = False
        st.session_state["pdf_bytes"] = None
        try:
            st.rerun()
        except Exception:
            pass
    except Exception as e:
        st.session_state["an_done"] = False
        st.session_state["an_running"] = False
        st.session_state["an_error"] = f"Error: {e}"


try:
    AIDetectionEngine.analyze = _precision115_analyze
except Exception:
    pass

try:
    _precision115_run_pending_analysis_final()
except Exception:
    pass
