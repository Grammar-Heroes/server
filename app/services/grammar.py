from typing import Tuple

try:
    import language_tool_python
    TOOL_AVALIABLE = True
except Exception:
    TOOL_AVALIABLE = False

if TOOL_AVALIABLE:
    tool = language_tool_python.LanguageTool('en-US')

def check_sentence(sentence: str) -> Tuple[str, int]:

    if not TOOL_AVALIABLE:
        return sentence, 0
    
    matches = tool.check(sentence)
    corrected = language_tool_python.utils.correct(sentence, matches)
    return corrected, len(matches)