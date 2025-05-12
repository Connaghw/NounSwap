import spacy
import re
from itertools import cycle, count, product

# Load the English NLP model
nlp = spacy.load("en_core_web_sm")

# Infinite codename generator
def codename_generator():
    base_names = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta", "Iota", "Kappa"]
    for i in count():
        for name in base_names:
            yield f"{name}{i if i > 0 else ''}"

def codify_proper_nouns(text):
    doc = nlp(text)
    codenames = codename_generator()
    noun_map = {}
    reverse_map = {}

    codified_tokens = []

    for token in doc:
        text_token = token.text

        # Handle possessive separately, e.g. "James's"
        if token.pos_ == "PROPN":
            base_text = text_token
            suffix = ""

            # Check for possessive 's (James's)
            if text_token.endswith("'s") or text_token.endswith("’s"):
                base_text = text_token[:-2]
                suffix = "'s"

            # Get or create codename
            if base_text not in reverse_map:
                code = next(codenames)
                noun_map[code] = base_text
                reverse_map[base_text] = code
            else:
                code = reverse_map[base_text]

            codified_tokens.append(code + suffix)
        else:
            codified_tokens.append(text_token)

    codified_text = " ".join(codified_tokens)
    return codified_text, noun_map

def decode_codified(codified_text, codename_map):
    # Handle possessives in decoding
    def replacement(match):
        codename = match.group(1)
        suffix = match.group(2) or ""
        original = codename_map.get(codename, codename)
        return original + suffix

    # Regex: capture codename optionally followed by 's
    pattern = re.compile(r"\b(" + "|".join(re.escape(k) for k in codename_map.keys()) + r")('s)?\b")
    return pattern.sub(replacement, codified_text)

# Example usage
if __name__ == "__main__":
    input_text = "Google documents are processed by Google's great machine. John spent a while processing documents from Kodak's project specifications"
    codified, mapping = codify_proper_nouns(input_text)
    print("Codified:", codified)
    print("Mapping:", mapping)

    decoded = decode_codified(codified, mapping)
    print("Decoded:", decoded)

