from flask import Flask, request, jsonify
from flask_cors import CORS
import spacy
import re

nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)
CORS(app)

# Generator for infinite codename sequences
def codename_generator():
    from itertools import product
    base_names = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta", "iota", "kappa"]
    for size in range(1, 100):  # practically infinite
        for combo in product(base_names, repeat=size):
            yield "_".join(combo)

# Normalize noun (e.g., remove possessive 's)
def normalize_noun(token):
    if token.tag_ == "POS" and token.head.text.endswith("'s"):
        return token.head.text[:-2]
    return token.text

# Codify function
def codify_proper_nouns(text):
    doc = nlp(text)
    codename_map = {}
    reverse_map = {}
    generator = codename_generator()

    def get_codename(name):
        if name not in codename_map:
            code = next(generator)
            codename_map[name] = code
            reverse_map[code] = name
        return codename_map[name]

    new_tokens = []
    for token in doc:
        if token.ent_type_ in ["PERSON", "ORG", "GPE"]:
            base = token.text.rstrip("'s")
            code = get_codename(base)
            if token.text.endswith("'s"):
                new_tokens.append(code + "'s")
            else:
                new_tokens.append(code)
        else:
            new_tokens.append(token.text)

    result_text = " ".join(new_tokens)
    return result_text, codename_map

# Decode function
def decode_codified(text, codename_map):
    # Handle "codename's" separately
    reversed_map = {v: k for k, v in codename_map.items()}
    sorted_keys = sorted(reversed_map.keys(), key=len, reverse=True)  # prevent partial matches
    for code in sorted_keys:
        name = reversed_map[code]
        text = re.sub(rf"\b{re.escape(code)}'s\b", name + "'s", text)
        text = re.sub(rf"\b{re.escape(code)}\b", name, text)
    return text

@app.route("/codify", methods=["POST"])
def codify():
    data = request.get_json()
    text = data.get("text", "")
    codified, mapping = codify_proper_nouns(text)
    return jsonify({"codified": codified, "map": mapping})

@app.route("/decode", methods=["POST"])
def decode():
    data = request.get_json()
    codified_text = data.get("text", "")
    codename_map = data.get("map", {})
    decoded = decode_codified(codified_text, codename_map)
    return jsonify({"decoded": decoded})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)