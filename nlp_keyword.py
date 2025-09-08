# NLP keyword extraction from uploaded FAQ questions
import json
from pathlib import Path

# Try to use scikit-learn TF-IDF for better keyword extraction; fall back to a simple method if unavailable.
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    sklearn_available = True
except Exception as e:
    sklearn_available = False

INPUT_PATH = Path("C:\\Users\\bosma\\Documents\\Hackathon 2025\\faq_data.json")
OUTPUT_PATH = Path("C:\\Users\\bosma\\Documents\\Hackathon 2025\\faq_keywords.json")

# Load the JSON
with INPUT_PATH.open("r", encoding="utf-8") as f:
    faq = json.load(f)

questions = [item["question"] for item in faq]

def tfidf_keywords(texts, top_k=7):
    # Use unigrams and bigrams to capture short phrases as well
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), token_pattern=r"(?u)\b[A-Za-z][A-Za-z]+\b")
    X = vectorizer.fit_transform(texts)
    vocab = vectorizer.get_feature_names_out()
    results = []
    for row in range(X.shape[0]):
        vec = X[row].toarray().ravel()
        # Get indices of top_k highest values
        top_idx = vec.argsort()[::-1][:top_k]
        # Map to terms and filter duplicates while preserving order
        seen = set()
        top_terms = []
        for idx in top_idx:
            term = vocab[idx]
            if term not in seen:
                seen.add(term)
                top_terms.append(term)
        results.append(top_terms)
    return results

def simple_keywords(texts, top_k=7):
    # Very simple fallback: frequency-based keywords per question excluding common stopwords
    import re
    STOP = set("""a an and the is am are were was be been being to of in for on with by or at from into as about this that these those it its your you we our their his her they can will would should could do does did not no yes how why what where when who which""".split())
    # Build global doc frequency for a crude IDF-like weighting
    tokenized_docs = []
    df = {}
    for t in texts:
        tokens = [w.lower() for w in re.findall(r"[A-Za-z]{2,}", t)]
        uniq = set([w for w in tokens if w not in STOP])
        tokenized_docs.append(tokens)
        for w in uniq:
            df[w] = df.get(w, 0) + 1
    N = len(texts)
    import math
    idf = {w: math.log((N + 1) / (df[w] + 1)) + 1 for w in df}
    results = []
    for tokens in tokenized_docs:
        scores = {}
        for w in tokens:
            if w in STOP:
                continue
            scores[w] = scores.get(w, 0) + idf.get(w, 1.0)
        # Sort by score
        top = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
        results.append([w for w, s in top])
    return results

if sklearn_available:
    kw_lists = tfidf_keywords(questions, top_k=7)
else:
    kw_lists = simple_keywords(questions, top_k=7)

# Build the output structure
output = []
for item, kws in zip(faq, kw_lists):
    output.append({
        "question": item["question"],
        "keywords": kws
    })

# Save to a JSON file
with OUTPUT_PATH.open("w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

OUTPUT_PATH.as_posix()
