# NOTE : language_tool_python is rule based so that's bad.
# NOTE : I will instead use Gramformer, it is built on T5/BERT transformers, trained for GEC (grammar error correction).
#        IT HAS 220 MILLION PARAMETERS
#        Input  : raw sentence
#        Output : a corrected version of the sentence   

# Gramformer depends on Pytorch and Transformers, so install those first
# pip install torch torchvision torchaudio transformers

# Then, since Gramformer isn't on PyPl, we need to install it from GitHub and setup its dependencies
# pip install git+https://github.com/PrithivirajDamodaran/Gramformer.git

# NOTE : Make sure to install torch & transformers first before installing Gramformer
# NOTE : Additionally, make sure to install en_core_web_sm for spacy

from typing import Dict, List
import difflib # helpers for computing deltas between objects

# try:
#     import language_tool_python
#     TOOL_AVALIABLE = True
# except Exception:
#     TOOL_AVALIABLE = False

# if TOOL_AVALIABLE:
#     tool = language_tool_python.LanguageTool('en-US')

from gramformer import Gramformer
import language_tool_python

gf = Gramformer(models=1, use_gpu=False) # models=1 -> GEC model
tool = language_tool_python.LanguageTool('en-US') # i added this to get the error message, but it's not yet part of the schema

async def check_sentence(sentence: str) -> Dict[str, List[int] | bool]:

    # correction (returns set of corrected sentences)
    corrected_candidates = list(gf.correct(sentence))
    corrected_sentence = corrected_candidates[0] if corrected_candidates else sentence

    # if not corrected:
    #     return {"is_correct": True, "error_indices": []}
    
    # # matches = tool.check(sentence)
    # corrected_sentence = corrected[0]

    # tokenize words for comparison
    words_original = sentence.split()
    words_corrected = corrected_sentence.split()

    # if match exactly, sentence = correct
    if words_original == words_corrected:
        return {"is_correct": True, "error_indices": [], "feedback": []}
    
    # otherwise, find mismatch words
    error_indices = []
    feedback = []
    matcher = difflib.SequenceMatcher(None, words_original, words_corrected)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != "equal":
            wrong = " ".join(words_original[i1:i2])
            right = " ".join(words_corrected[j1:j2])
            error_indices.extend(range(i1, i2))
            feedback.append(f"Replace '{wrong}' with '{right}'") # not yet in the schema
    
    matches = tool.check(sentence) # not yet in the schema
    for match in matches:
        feedback.append(f"{match.ruleId}: {match.message}")

    # for match in matches:
    #     start, end = match.offset, match.offset + match.errorLength
    #     running_length = 0
    #     for idx, word in enumerate(words):
    #         running_length += len(word) + 1 # +1 for space
    #         if running_length > start:
    #             error_indices.add(idx)
    #             break

    return {
        "is_correct": False,
        "error_indices": list(set(error_indices)),
        "feedback": feedback
    }