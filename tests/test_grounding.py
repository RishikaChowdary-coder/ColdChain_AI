from rag_engine import SYSTEM_PROMPT

def test_grounding_prompt_requires_context_and_no_fabrication():
    assert "only the supplied retrieved document context" in SYSTEM_PROMPT
    assert "Do not invent" in SYSTEM_PROMPT
    assert "Do not control equipment" in SYSTEM_PROMPT
