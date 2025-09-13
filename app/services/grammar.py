from typing import Dict, List

try:
    import language_tool_python
    TOOL_AVALIABLE = True
except Exception:
    TOOL_AVALIABLE = False

if TOOL_AVALIABLE:
    tool = language_tool_python.LanguageTool('en-US')

async def check_sentence(sentence: str) -> Dict[str, List[int] | bool]:

    if not TOOL_AVALIABLE:
        return {"is_correct": True, "error_indices": []}
    
    matches = tool.check(sentence)

    # Split sentence into words to map offsets -> word indices
    words = sentence.split()
    error_indices = set()

    for match in matches:
        start, end = match.offset, match.offset + match.errorLength
        running_length = 0
        for idx, word in enumerate(words):
            running_length += len(word) + 1 # +1 for space
            if running_length > start:
                error_indices.add(idx)
                break

    return {
        "is_correct": len(matches) == 0,
        "error_indices": list(error_indices)
    }