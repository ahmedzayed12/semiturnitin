# Model and license notes

The default supervised component uses the TMR AI text detector architecture and its ONNX INT8 conversion:

- Base detector: Oxidane/tmr-ai-text-detector
- ONNX conversion: onnx-community/tmr-ai-text-detector-ONNX
- Default file: onnx/model_int8.onnx
- Model license shown on the model card: MIT

The application does not redistribute model weights in this ZIP. It downloads the selected ONNX file on first use, unless the user places an offline copy under models/tmr-ai-text-detector/onnx/model_int8.onnx.
