import os
import io
import glob
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image
import tensorflow as tf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
CORS(app)

# ---------------- MODEL ----------------
# Finds crop_model.h5 or crop_model (1).h5 automatically
model_files = glob.glob(os.path.join(BASE_DIR, "crop_model*.h5"))
if not model_files:
    raise FileNotFoundError("No crop_model*.h5 file found next to app.py")
MODEL_PATH = model_files[0]
print("Loading model:", MODEL_PATH)

model = tf.keras.models.load_model(MODEL_PATH, compile=False)

# Image size is read from the model itself, so it matches training
_, IMG_H, IMG_W, _ = model.input_shape
print("Model input size:", IMG_H, IMG_W)

class_names = [
    'Tomato_Yellow_Leaf_Curl_Virus',
    'cotton_bacterial_blight',
    'cotton_curl_virus',
    'cotton_fussarium_wilt',
    'cotton_healthy',
    'tomato_Early_blight',
    'tomato_Late_blight',
    'tomato_healthy',
]

# ---------------- DISPLAY NAMES ----------------
display_names = {
    "en": {
        'Tomato_Yellow_Leaf_Curl_Virus': "Tomato Yellow Leaf Curl Virus",
        'cotton_bacterial_blight': "Cotton Bacterial Blight",
        'cotton_curl_virus': "Cotton Leaf Curl Virus",
        'cotton_fussarium_wilt': "Cotton Fusarium Wilt",
        'cotton_healthy': "Cotton - Healthy",
        'tomato_Early_blight': "Tomato Early Blight",
        'tomato_Late_blight': "Tomato Late Blight",
        'tomato_healthy': "Tomato - Healthy",
    },
    "mr": {
        'Tomato_Yellow_Leaf_Curl_Virus': "टोमॅटो पिवळा पान गुंडाळी विषाणू",
        'cotton_bacterial_blight': "कापूस जिवाणूजन्य करपा",
        'cotton_curl_virus': "कापूस पान गुंडाळी विषाणू",
        'cotton_fussarium_wilt': "कापूस फ्युजॅरियम मर",
        'cotton_healthy': "कापूस - निरोगी",
        'tomato_Early_blight': "टोमॅटो लवकर येणारा करपा",
        'tomato_Late_blight': "टोमॅटो उशिरा येणारा करपा",
        'tomato_healthy': "टोमॅटो - निरोगी",
    },
}

# ---------------- TREATMENT ----------------
treatments = {
    "en": {
        'Tomato_Yellow_Leaf_Curl_Virus':
            "Remove and destroy infected plants. Control whiteflies (the virus carrier) using yellow sticky traps "
            "and neem oil or recommended insecticides. Use virus-resistant varieties and nylon nets in nurseries.",
        'cotton_bacterial_blight':
            "Use disease-free certified seeds and treat seeds before sowing. Avoid overhead irrigation. "
            "Spray copper oxychloride as advised by your local agriculture officer. Destroy infected crop residue.",
        'cotton_curl_virus':
            "Control whiteflies with neem-based sprays or recommended insecticides. Uproot and destroy infected plants. "
            "Grow resistant varieties and remove nearby weed hosts.",
        'cotton_fussarium_wilt':
            "Use wilt-resistant varieties and practice crop rotation. Improve soil drainage, avoid waterlogging, "
            "and use bio-agents like Trichoderma in the soil. Remove infected plants.",
        'cotton_healthy':
            "The plant looks healthy. Continue regular watering, balanced fertilizer and monitor the crop for pests.",
        'tomato_Early_blight':
            "Remove infected lower leaves. Spray mancozeb or chlorothalonil as recommended. "
            "Rotate crops, mulch the soil and avoid wetting leaves while watering.",
        'tomato_Late_blight':
            "Act quickly: remove infected plants and spray recommended fungicides (e.g. metalaxyl + mancozeb). "
            "Avoid overcrowding, ensure good air flow and avoid evening irrigation.",
        'tomato_healthy':
            "The plant looks healthy. Maintain regular watering, proper spacing and monitor for early signs of disease.",
    },
    "mr": {
        'Tomato_Yellow_Leaf_Curl_Virus':
            "बाधित झाडे उपटून नष्ट करा. पिवळे चिकट सापळे आणि निंबोळी तेल किंवा शिफारस केलेली कीटकनाशके वापरून "
            "पांढऱ्या माशीचे (विषाणू वाहक) नियंत्रण करा. विषाणू प्रतिरोधक वाण आणि रोपवाटिकेत नायलॉन जाळी वापरा.",
        'cotton_bacterial_blight':
            "रोगमुक्त प्रमाणित बियाणे वापरा आणि पेरणीपूर्वी बीजप्रक्रिया करा. वरून पाणी देणे टाळा. "
            "कृषी अधिकाऱ्यांच्या सल्ल्याने कॉपर ऑक्सिक्लोराईडची फवारणी करा. बाधित अवशेष नष्ट करा.",
        'cotton_curl_virus':
            "निंबोळी अर्क किंवा शिफारस केलेल्या कीटकनाशकांनी पांढऱ्या माशीचे नियंत्रण करा. बाधित झाडे उपटून नष्ट करा. "
            "प्रतिरोधक वाण लावा आणि जवळील तण काढा.",
        'cotton_fussarium_wilt':
            "मर प्रतिरोधक वाण वापरा आणि पीक फेरपालट करा. पाण्याचा निचरा चांगला ठेवा, पाणी साचू देऊ नका "
            "आणि जमिनीत ट्रायकोडर्मा वापरा. बाधित झाडे काढून टाका.",
        'cotton_healthy':
            "झाड निरोगी दिसते. नियमित पाणी, संतुलित खत द्या आणि किडींसाठी पिकाचे निरीक्षण करा.",
        'tomato_Early_blight':
            "बाधित खालची पाने काढा. शिफारसीनुसार मॅन्कोझेब किंवा क्लोरोथॅलोनिलची फवारणी करा. "
            "पीक फेरपालट करा, आच्छादन वापरा आणि पानांवर पाणी पडू देऊ नका.",
        'tomato_Late_blight':
            "त्वरित कारवाई करा: बाधित झाडे काढा आणि शिफारस केलेली बुरशीनाशके (उदा. मेटालॅक्सिल + मॅन्कोझेब) फवारा. "
            "दाटी टाळा, हवा खेळती ठेवा आणि संध्याकाळी पाणी देणे टाळा.",
        'tomato_healthy':
            "झाड निरोगी दिसते. नियमित पाणी, योग्य अंतर ठेवा आणि रोगाच्या सुरुवातीच्या लक्षणांसाठी निरीक्षण करा.",
    },
}

# ---------------- NOT-A-LEAF SETTINGS ----------------
REJECT_CONFIDENCE = 70.0   # below this, the model result is not trusted
MIN_PLANT_RATIO = 0.10     # at least 10% of pixels must look like plant colours

reject_msg = {
    "en": {
        "title": "Not a recognizable crop leaf",
        "text": "This does not look like a tomato or cotton leaf. Please upload a clear, close photo "
                "of a single tomato or cotton leaf in good light.",
    },
    "mr": {
        "title": "पिकाचे पान ओळखता आले नाही",
        "text": "हे टोमॅटो किंवा कापसाचे पान दिसत नाही. कृपया चांगल्या प्रकाशात टोमॅटो किंवा कापसाच्या "
                "एका पानाचा जवळून स्पष्ट फोटो अपलोड करा.",
    },
}


# ---------------- HELPERS ----------------
def preprocess(file_bytes):
    img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    img = img.resize((IMG_W, IMG_H))
    arr = np.array(img, dtype=np.float32) / 255.0   # remove "/ 255.0" if your model already rescales inside
    return np.expand_dims(arr, axis=0)


def plant_ratio(file_bytes):
    """Fraction of pixels with green / yellow / brown-ish plant colours."""
    img = Image.open(io.BytesIO(file_bytes)).convert("RGB").resize((128, 128))
    hsv = np.array(img.convert("HSV"), dtype=np.float32)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    # PIL hue is 0-255: ~20 to ~130 covers yellow-brown through green
    mask = (h >= 20) & (h <= 130) & (s >= 40) & (v >= 40)
    return float(mask.mean())


# ---------------- FRONTEND ROUTES (only these 3 files are served) ----------------
@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/style.css")
def css():
    return send_from_directory(BASE_DIR, "style.css")


@app.route("/script.js")
def js():
    return send_from_directory(BASE_DIR, "script.js")


# ---------------- API ----------------
@app.route("/predict", methods=["POST"])
def predict():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        file = request.files["file"]
        lang = request.form.get("lang", "en")
        if lang not in ("en", "mr"):
            lang = "en"

        file_bytes = file.read()

        # Check 1: does it even look like a plant?
        if plant_ratio(file_bytes) < MIN_PLANT_RATIO:
            return jsonify({
                "prediction": reject_msg[lang]["title"],
                "confidence": 0,
                "treatment": reject_msg[lang]["text"],
                "rejected": True,
            })

        x = preprocess(file_bytes)
        probs = model.predict(x, verbose=0)[0]

        idx = int(np.argmax(probs))
        confidence = round(float(probs[idx]) * 100, 2)

        # Check 2: is the model actually sure?
        if confidence < REJECT_CONFIDENCE:
            return jsonify({
                "prediction": reject_msg[lang]["title"],
                "confidence": confidence,
                "treatment": reject_msg[lang]["text"],
                "rejected": True,
            })

        key = class_names[idx]
        return jsonify({
            "prediction": display_names[lang][key],
            "confidence": confidence,
            "treatment": treatments[lang][key],
            "rejected": False,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
