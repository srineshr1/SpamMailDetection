import numpy as np
import joblib
import re
import os
import nltk

from rest_framework.decorators import api_view
from rest_framework.response import Response

# Download NLTK stopwords if not already present (needed on fresh Render instance)
nltk.download('stopwords', quiet=True)

from nltk.corpus import stopwords

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load the model and vectorizer once at startup
model_path = os.path.join(BASE_DIR, "spam_model.joblib")
vectorizer_path = os.path.join(BASE_DIR, "tfidf_vectorizer.joblib")

model = joblib.load(model_path)
vectorizer = joblib.load(vectorizer_path)

STOPWORDS = set(stopwords.words("english"))


def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    words = text.split()
    words = [word for word in words if word not in STOPWORDS]
    return " ".join(words)


@api_view(['POST'])
def predict(request):
    mail = request.data.get('message', '')
    if not mail.strip():
        return Response({"error": "Empty message"}, status=400)

    cleaned_mail = clean_text(mail)
    vectorized_mail = vectorizer.transform([cleaned_mail])

    prediction_label = model.predict(vectorized_mail)[0]
    proba_all = model.predict_proba(vectorized_mail)[0]

    # Safely get spam probability
    if hasattr(model, 'classes_') and "spam" in list(model.classes_):
        spam_index = list(model.classes_).index("spam")
        proba = float(proba_all[spam_index])
    else:
        proba = 1.0 if prediction_label == "spam" else 0.0

    prediction = 1 if prediction_label == "spam" else 0

    return Response({
        "prediction": prediction,
        "confidence": proba
    })
