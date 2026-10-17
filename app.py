import os
import io
import glob
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image, ImageOps, UnidentifiedImageError
import tensorflow as tf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
CORS(app)

# Reject uploads larger than 10 MB
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

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

LOW_CONFIDENCE = 60.0

low_conf_msg = {
    "en": "Low confidence. Please upload a clearer, closer photo of a single leaf in good light.",
    "mr": "अचूकता कमी आहे. कृपया चांगल्या प्रकाशात एका पानाचा जवळून स्पष्ट फोटो अपलोड करा.",
}

# ---------------- INVALID IMAGE SETTINGS ----------------
INVALID_MSG = {
    "en": "Invalid image. Please upload a valid image.",
    "mr": "अवैध फोटो. कृपया वैध फोटो अपलोड करा.",
}

INVALID_HINT = {
    "en": "Please upload a clear, close photo of a cotton or tomato leaf.",
    "mr": "कृपया कापूस किंवा टोमॅटोच्या पानाचा स्पष्ट, जवळून फोटो अपलोड करा.",
}

MIN_LEAF_RATIO = 0.20        # at least 20% of pixels must be leaf-coloured; lower it if real leaves get rejected
MIN_IMAGE_SIDE = 64          # pixels
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "bmp"}


class InvalidImage(Exception):
    pass


def invalid_response(lang):
    """
    Returns the message in the normal result fields (status 200).
    There is NO 'error' key on purpose: the frontend treats 'error' as a failure
    and prints the word 'error' in the Disease box.
    """
    msg = INVALID_MSG.get(lang, INVALID_MSG["en"])
    hint = INVALID_HINT.get(lang, INVALID_HINT["en"])
    return jsonify({
        "prediction": msg,
        "disease": msg,
        "result": msg,
        "label": msg,
        "class": msg,
        "confidence": 0,
        "treatment": hint,
    })


# ---------------- HELPERS ----------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def load_image(file_bytes):
    """Open and validate the image. Raises InvalidImage if anything is wrong."""
    if not file_bytes:
        raise InvalidImage()
    try:
        Image.open(io.BytesIO(file_bytes)).verify()
        img = Image.open(io.BytesIO(file_bytes))
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError):
        raise InvalidImage()

    if img.width < MIN_IMAGE_SIDE or img.height < MIN_IMAGE_SIDE:
        raise InvalidImage()
    return img


def looks_like_leaf(img):
    """Fraction of green / yellow / brown pixels (HSV). Photos of faces, objects, screenshots score low."""
    hsv = np.array(img.resize((120, 120)).convert("HSV"), dtype=np.float32)
    hue = hsv[..., 0] * 360.0 / 255.0
    sat = hsv[..., 1] / 255.0
    val = hsv[..., 2] / 255.0
    leaf = (hue >= 30) & (hue <= 160) & (sat >= 0.20) & (val >= 0.15)
    return float(np.mean(leaf)) >= MIN_LEAF_RATIO


def preprocess(img):
    # Same as your original preprocessing
    img = img.resize((IMG_W, IMG_H))
    arr = np.array(img, dtype=np.float32) / 255.0   # remove "/ 255.0" if your model already rescales inside
    return np.expand_dims(arr, axis=0)


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


# ---------------- ERROR HANDLERS ----------------
@app.errorhandler(413)
def too_large(e):
    lang = request.form.get("lang", "en") if request.form else "en"
    lang = lang if lang in ("en", "mr") else "en"
    return invalid_response(lang)


# ---------------- API ----------------
@app.route("/predict", methods=["POST"])
def predict():
    lang = request.form.get("lang", "en")
    if lang not in ("en", "mr"):
        lang = "en"

    try:
        # ---- invalid image checks (run BEFORE prediction) ----
        if "file" not in request.files or request.files["file"].filename == "":
            raise InvalidImage()

        file = request.files["file"]
        if not allowed_file(file.filename):
            raise InvalidImage()

        img = load_image(file.read())

        if not looks_like_leaf(img):
            raise InvalidImage()

        # ---- prediction (unchanged) ----
        x = preprocess(img)
        probs = model.predict(x, verbose=0)[0]

        idx = int(np.argmax(probs))
        confidence = round(float(probs[idx]) * 100, 2)
        key = class_names[idx]

        treatment = treatments[lang][key]
        if confidence < LOW_CONFIDENCE:
            treatment = low_conf_msg[lang] + "\n\n" + treatment

        return jsonify({
            "prediction": display_names[lang][key],
            "confidence": confidence,
            "treatment": treatment,
        })

    except InvalidImage:
        return invalid_response(lang)

    except Exception as e:
        print("Prediction error:", e)   # real error stays in the terminal
        return invalid_response(lang)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)