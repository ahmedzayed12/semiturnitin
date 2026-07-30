# AI Fingerprint Detector v6.0.1

نسخة إصلاح وتشديد لمحرك v6، مع الحفاظ على الواجهة نفسها وطريقة استخراج تقارير PDF وWord والتظليل فوق ملف PDF الأصلي.

## إصلاح الخطأ الخاص بـ model_type

كان الإصدار السابق يعتبر وجود مجلد `models/tmr-ai-text-detector` كافيًا لاستخدامه كنموذج PyTorch، حتى لو كان المجلد يحتوي ملفات ONNX فقط أو تنزيلًا ناقصًا. وعند فشل ONNX كان ينتقل إلى PyTorch ويفتح المجلد الخاطئ، فتظهر رسالة:

`Should have a model_type key in its config.json`

في v6.0.1 تم إصلاح ذلك كالتالي:

1. التحقق من أن `onnx/model_int8.onnx` ملف حقيقي وكامل، وليس ملف Pointer أو تنزيلًا مقطوعًا.
2. التحقق من أن `config.json` يحتوي `model_type: roberta`.
3. التحقق من ملفات الـTokenizer قبل بدء التحليل.
4. إصلاح الملفات الناقصة أو التالفة تلقائيًا.
5. منع تمرير مجلد ONNX إلى `AutoModelForSequenceClassification` نهائيًا.
6. عرض خطأ ONNX الحقيقي إذا تعذر تشغيله، بدل إخفائه برسالة PyTorch مضللة.

## التشغيل على Windows

### لأول مرة أو بعد ظهور خطأ النموذج

1. فك ضغط الحزمة في مسار قصير، مثل:
   `C:\AI_Fingerprint_Strict_v6_0_1`
2. شغّل `REPAIR_MODEL.bat`.
3. انتظر حتى تظهر الرسالة:
   `SUCCESS: model and tokenizer passed validation.`
4. شغّل `RUN_LOCAL.bat`.

يمكن أيضًا تشغيل `RUN_LOCAL.bat` مباشرة؛ فهو يفحص النموذج أولًا ويشغّل الإصلاح تلقائيًا عند الحاجة.

## التشغيل يدويًا

```bat
pip install -r requirements.txt
python download_model.py
python -m streamlit run app.py
```

## الملفات المهمة

- `app.py`: التطبيق والمحرك بعد الإصلاح.
- `REPAIR_MODEL.bat`: حذف واستبدال الملفات التالفة فقط.
- `download_model.py`: تنزيل وفحص النموذج والـTokenizer.
- `RUN_LOCAL.bat`: فحص تلقائي ثم تشغيل Streamlit.
- `requirements.txt`: المكتبات المطلوبة.

## Streamlit Community Cloud

ارفع ملفات المشروع إلى GitHub. عند أول تحليل، سيحاول التطبيق تنزيل نموذج ONNX INT8 وملفات الـTokenizer والتحقق منها. يجب أن تسمح البيئة بالاتصال بـHugging Face وأن تتوافر مساحة تخزين كافية لملف النموذج، الذي يبلغ حجمه نحو 126 MB.

## ملاحظة منهجية

المحرك يجمع المصنف المتعلّم مع التحليل البنيوي والأسلوبي، لكنه لا يمثل دليلًا قطعيًا على هوية الكاتب. يجب استخدام النتيجة كمؤشر مراجعة مع فحص بشري، خصوصًا في القرارات الأكاديمية الحساسة.
