const imageInput = document.getElementById("imageInput");
const preview = document.getElementById("preview");
let selectedImageFile = null;

imageInput.addEventListener("change", function () {
    const file = this.files[0];
    if (file) {
        selectedImageFile = file;
        preview.src = URL.createObjectURL(file);
        preview.style.display = "block";
    }
});

let cameraStream = null;
const camera = document.getElementById("camera");
const cameraContainer = document.getElementById("cameraContainer");
const canvas = document.getElementById("canvas");

async function openCamera() {
    try {
        cameraStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" }, audio: false });
        camera.srcObject = cameraStream;
        cameraContainer.style.display = "block";
    } catch (error) { alert("Camera access denied."); }
}

function captureImage() {
    if (!cameraStream) { alert("Please open camera first."); return; }
    const context = canvas.getContext("2d");
    canvas.width = camera.videoWidth; canvas.height = camera.videoHeight;
    context.drawImage(camera, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(function (blob) {
        selectedImageFile = new File([blob], "camera-capture.jpg", { type: "image/jpeg" });
        preview.src = URL.createObjectURL(blob);
        preview.style.display = "block";
        closeCamera();
        alert("Image captured successfully!");
    }, "image/jpeg", 0.9);
}

function closeCamera() {
    if (cameraStream) { cameraStream.getTracks().forEach(t => t.stop()); cameraStream = null; }
    camera.srcObject = null; cameraContainer.style.display = "none";
}

const translations = {
en: { homeNav:"Home",aboutNav:"About",detectNav:"Detection",historyNav:"History",contactNav:"Contact",mainTitle:"AI-Based Crop Disease Detection",mainDescription:"Detect crop diseases quickly using Artificial Intelligence and get useful information about treatment and prevention.",startButton:"Start Detection",detectionHeading:"🌿 Detect Crop Disease",uploadDescription:"Upload or capture an image of a crop leaf to detect possible diseases.",uploadHeading:"Upload Crop Leaf Image",uploadInstruction:"Select a clear image of the affected leaf.",chooseButton:"📁 Choose Image",cameraButton:"📷 Open Camera",captureButton:"📸 Capture",closeCameraButton:"✖ Close",predictButton:"🤖 Predict Disease",resultHeading:"🔍 Prediction Result",diseaseLabel:"Disease",confidenceLabel:"Confidence",diseaseResult:"Please upload or capture an image.",confidenceResult:"--",treatmentHeading:"💊 Treatment / Prevention",treatmentResult:"Treatment information will appear after prediction.",historyHeading:"🕘 Search History",historyDescription:"View your previous crop disease predictions.",noHistory:"No search history available.",clearHistoryButton:"🗑️ Clear History",aboutHeading:"About the Project",aboutDescription:"Our system uses Artificial Intelligence to help identify crop diseases from leaf images.",aiCardHeading:"Artificial Intelligence",aiCardText:"AI technology analyzes the uploaded crop image to identify possible diseases.",diseaseCardHeading:"Disease Detection",diseaseCardText:"The system detects possible diseases based on the characteristics of the crop leaf.",treatmentCardHeading:"Treatment",treatmentCardText:"The system can provide basic information about treatment and prevention.",farmerCardHeading:"Farmer Friendly",farmerCardText:"The application supports English and Marathi languages for easier use.",workingHeading:"How It Works",step1Heading:"Upload / Capture",step1Text:"Upload an image or capture a photo using the camera.",step2Heading:"AI Analysis",step2Text:"The AI model analyzes the leaf image.",step3Heading:"Disease Detection",step3Text:"The system identifies the possible disease.",step4Heading:"Treatment",step4Text:"Get basic treatment and prevention information.",footerDescription:"AI-Based Crop Disease Detection System",footerCopyright:"© 2026 CropCare AI. All Rights Reserved."},
mr: { homeNav:"मुख्यपृष्ठ",aboutNav:"प्रकल्पाबद्दल",detectNav:"रोग ओळख",historyNav:"इतिहास",contactNav:"संपर्क",mainTitle:"AI आधारित पिकांच्या रोगांची ओळख",mainDescription:"कृत्रिम बुद्धिमत्तेच्या मदतीने पिकांचे रोग जलद ओळखा आणि उपचार व प्रतिबंधाची उपयुक्त माहिती मिळवा.",startButton:"रोग ओळख सुरू करा",detectionHeading:"🌿 पिकांचा रोग ओळखा",uploadDescription:"संभाव्य रोग ओळखण्यासाठी पिकाच्या पानाचा फोटो अपलोड करा किंवा कॅमेऱ्याने फोटो काढा.",uploadHeading:"पिकाच्या पानाचा फोटो अपलोड करा",uploadInstruction:"रोगग्रस्त पानाचा स्पष्ट फोटो निवडा.",chooseButton:"📁 फोटो निवडा",cameraButton:"📷 कॅमेरा उघडा",captureButton:"📸 फोटो काढा",closeCameraButton:"✖ बंद करा",predictButton:"🤖 रोग ओळखा",resultHeading:"🔍 रोग ओळखण्याचा निकाल",diseaseLabel:"रोग",confidenceLabel:"अचूकता",diseaseResult:"कृपया फोटो अपलोड करा किंवा कॅमेऱ्याने फोटो काढा.",confidenceResult:"--",treatmentHeading:"💊 उपचार / प्रतिबंध",treatmentResult:"रोगाचे निदान झाल्यानंतर उपचाराची माहिती येथे दिसेल.",historyHeading:"🕘 शोध इतिहास",historyDescription:"तुमच्या मागील पिकांच्या रोग निदानाचे निकाल पहा.",noHistory:"शोध इतिहास उपलब्ध नाही.",clearHistoryButton:"🗑️ इतिहास साफ करा",aboutHeading:"प्रकल्पाबद्दल",aboutDescription:"आमची प्रणाली पिकांच्या पानांच्या फोटोमधून रोग ओळखण्यासाठी कृत्रिम बुद्धिमत्तेचा वापर करते.",aiCardHeading:"कृत्रिम बुद्धिमत्ता",aiCardText:"अपलोड केलेल्या पिकाच्या फोटोचे विश्लेषण करून संभाव्य रोग ओळखण्यासाठी AI तंत्रज्ञानाचा वापर केला जातो.",diseaseCardHeading:"रोग ओळख",diseaseCardText:"पिकाच्या पानाच्या वैशिष्ट्यांवर आधारित प्रणाली संभाव्य रोग ओळखते.",treatmentCardHeading:"उपचार",treatmentCardText:"प्रणाली उपचार आणि रोग प्रतिबंधाबद्दल प्राथमिक माहिती देऊ शकते.",farmerCardHeading:"शेतकरी अनुकूल",farmerCardText:"शेतकऱ्यांच्या सोयीसाठी या प्रणालीमध्ये इंग्रजी आणि मराठी भाषांचा समावेश आहे.",workingHeading:"प्रणाली कशी कार्य करते",step1Heading:"अपलोड / फोटो काढा",step1Text:"फोटो अपलोड करा किंवा कॅमेऱ्याने पिकाच्या पानाचा फोटो काढा.",step2Heading:"AI विश्लेषण",step2Text:"AI मॉडेल पिकाच्या पानाच्या फोटोचे विश्लेषण करते.",step3Heading:"रोग ओळख",step3Text:"प्रणाली पिकाचा संभाव्य रोग ओळखते.",step4Heading:"उपचार",step4Text:"उपचार आणि प्रतिबंधाची प्राथमिक माहिती मिळवा.",footerDescription:"AI आधारित पिकांच्या रोगांची ओळख प्रणाली",footerCopyright:"© 2026 CropCare AI. सर्व हक्क राखीव."}
};

function changeLanguage(language) {
    const text = translations[language];
    for (let k in text) { let el = document.getElementById(k); if (el) el.innerText = text[k]; }
    localStorage.setItem("selectedLanguage", language);
    renderHistory();
}

function getHistory() { return JSON.parse(localStorage.getItem("cropDiseaseHistory") || "[]"); }

function saveHistory(disease, confidence, treatment, imageURL) {
    let h = getHistory();
    h.unshift({ disease, confidence, treatment, image: imageURL, date: new Date().toLocaleString() });
    if (h.length > 20) h = h.slice(0, 20);
    try {
        localStorage.setItem("cropDiseaseHistory", JSON.stringify(h));
    } catch (e) {
        // storage full: drop older entries and retry
        h = h.slice(0, 5);
        try { localStorage.setItem("cropDiseaseHistory", JSON.stringify(h)); } catch (e2) {}
    }
    renderHistory();
}

function renderHistory() {
    const list = document.getElementById("historyList");
    const h = getHistory();
    list.innerHTML = "";
    if (h.length === 0) {
        const lang = localStorage.getItem("selectedLanguage") || "en";
        list.innerHTML = `<p class="no-history">${translations[lang].noHistory}</p>`;
        return;
    }
    h.forEach(item => {
        const div = document.createElement("div");
        div.className = "history-item";
        div.innerHTML = `<img class="history-image" src="${item.image}"><div class="history-info"><h4>🌿 ${item.disease}</h4><p><strong>Confidence:</strong> ${item.confidence}</p><p><strong>Treatment:</strong> ${item.treatment}</p><p class="history-date">🕒 ${item.date}</p></div>`;
        list.appendChild(div);
    });
}

function clearHistory() {
    const lang = localStorage.getItem("selectedLanguage") || "en";
    const msg = lang === "mr" ? "तुम्हाला सर्व शोध इतिहास हटवायचा आहे का?" : "Do you want to delete all search history?";
    if (confirm(msg)) { localStorage.removeItem("cropDiseaseHistory"); renderHistory(); }
}

async function predictDisease() {
    const file = selectedImageFile || document.getElementById("imageInput").files[0];
    if (!file) { alert("Please upload or capture a crop leaf image first."); return; }

    document.getElementById("diseaseResult").innerText = "⏳ Analyzing...";
    document.getElementById("confidenceResult").innerText = "--";
    document.getElementById("treatmentResult").innerText = "Please wait...";

    let fd = new FormData();
    fd.append("file", file);
    let lang = localStorage.getItem("selectedLanguage") || "en";
    fd.append("lang", lang);

    try {
        let res = await fetch("/predict", { method: "POST", body: fd });
        let data = await res.json();
        if (data.error) throw new Error(data.error);

        document.getElementById("diseaseResult").innerText = data.prediction;
        document.getElementById("confidenceResult").innerText = data.rejected ? "--" : data.confidence + "%";
        document.getElementById("treatmentResult").innerText = data.treatment;

        // Only save real predictions to history, not rejected images
        if (!data.rejected) {
            const reader = new FileReader();
            reader.onload = e => saveHistory(data.prediction, data.confidence + "%", data.treatment, e.target.result);
            reader.readAsDataURL(file);
        }
    } catch (e) {
        document.getElementById("diseaseResult").innerText = "Error";
        document.getElementById("treatmentResult").innerText = e.message;
    }
}

const savedLanguage = localStorage.getItem("selectedLanguage");
if (savedLanguage) changeLanguage(savedLanguage);
renderHistory();