import re

def normalize_sentence(sentence: str) -> str:
    s = sentence.strip().lower()
    s = re.sub(r'[.?!]+$', '', s) # remove trailing punctuation(?)
    s = re.sub(r'\s+', ' ', s) # collapse whitespace
    return s