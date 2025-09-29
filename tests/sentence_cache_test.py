import sys
from pathlib import Path

# Add the parent directory (which contains 'app') to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.grammar import check_sentence
import asyncio

async def test_cache():
    sentence = "This is a test sentence."

    print("\n--- FIRST CALL ---")
    result1 = await check_sentence(sentence)
    print("Result:", result1)

    print("\n--- SECOND CALL ---")
    result2 = await check_sentence(sentence)
    print("Result:", result2)

if __name__ == "__main__":
    asyncio.run(test_cache())