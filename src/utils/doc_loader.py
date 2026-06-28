import os
from typing import List, Dict

import fitz
import docx


def load_pdf(file_path: str) -> List[Dict]:
    documents = []

    pdf = fitz.open(file_path)

    for page_number, page in enumerate(pdf, start=1):
        text = page.get_text()

        if text.strip():
            documents.append(
                {
                    "text": text,
                    "metadata": {
                        "source": os.path.basename(file_path),
                        "page": page_number,
                        "file_type": "pdf",
                    },
                }
            )

    return documents


def load_docx(file_path: str) -> List[Dict]:
    document = docx.Document(file_path)

    full_text = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            full_text.append(paragraph.text)

    return [
        {
            "text": "\n".join(full_text),
            "metadata": {
                "source": os.path.basename(file_path),
                "page": 1,
                "file_type": "docx",
            },
        }
    ]


def load_txt(file_path: str) -> List[Dict]:
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    return [
        {
            "text": text,
            "metadata": {
                "source": os.path.basename(file_path),
                "page": 1,
                "file_type": "txt",
            },
        }
    ]


def load_document(file_path: str) -> List[Dict]:
    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":
        return load_pdf(file_path)

    if extension == ".docx":
        return load_docx(file_path)

    if extension == ".txt":
        return load_txt(file_path)

    raise ValueError(f"Unsupported file type: {extension}")