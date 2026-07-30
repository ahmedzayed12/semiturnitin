# AI Fingerprint Detector — Streamlit Deployment

هذه الحزمة جاهزة للرفع إلى GitHub ثم النشر على Streamlit Community Cloud.

## الملفات الأساسية

- `app.py`: التطبيق الأساسي الموحد.
- `model_best.pt`: النموذج المدرّب المستخدم في التحليل.
- `vectorizer.joblib`: محول TF-IDF المرتبط بالنموذج.
- `requirements.txt`: مكتبات Python.
- `packages.txt`: حزم Linux المطلوبة، ومنها LibreOffice.
- `.streamlit/config.toml`: إعدادات رفع الملفات.

## الرفع إلى GitHub

1. فك ضغط ملف ZIP.
2. أنشئ مستودع GitHub جديدًا.
3. ارفع **محتويات هذا المجلد** إلى جذر المستودع، مع الاحتفاظ بمجلد `.streamlit`.
4. لا ترفع ملف ZIP نفسه فقط؛ ارفع الملفات الموجودة بداخله.

## النشر على Streamlit

1. افتح Streamlit Community Cloud واختر المستودع والفرع `main`.
2. اجعل Main file path هو `app.py`.
3. من Advanced settings اختر Python 3.12.
4. اضغط Deploy.

لا يحتاج التطبيق إلى ملفات `train.csv` أو `val.csv` أو ملفات BAT أثناء النشر؛ النموذج الجاهز موجود داخل الحزمة.

## اختبار محلي اختياري

```bash
pip install -r requirements.txt
streamlit run app.py
```

لفحص تحميل النموذج من الطرفية:

```bash
python app.py --model-status
```
