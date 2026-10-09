from pathlib import Path
from document_manager import save_uploaded_pdf
import pytest

class FakeUpload:
    def __init__(self, name, content):
        self.name = name
        self._content = content
    def getvalue(self):
        return self._content

def test_rejects_non_pdf():
    with pytest.raises(ValueError):
        save_uploaded_pdf(FakeUpload("notes.txt", b"hello"))

def test_rejects_invalid_pdf():
    with pytest.raises(ValueError):
        save_uploaded_pdf(FakeUpload("fake.pdf", b"not a pdf"))
