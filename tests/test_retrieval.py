from rag_engine import ColdChainRAG

def test_new_engine_is_not_ready():
    engine = ColdChainRAG()
    assert engine.is_ready is False
    assert engine.stats()["documents"] == 0
