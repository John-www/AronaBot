import argparse
import json
import math
import os
import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from xml.etree import ElementTree
from urllib import error, request


INDEX_DIR = Path("rag_index")
DOCS_DIR = Path("rag_docs")
CHUNKS_FILE = INDEX_DIR / "chunks.jsonl"
VOCAB_FILE = INDEX_DIR / "vocab.json"
EMBEDDINGS_FILE = INDEX_DIR / "embeddings.jsonl"
EMBEDDINGS_META_FILE = INDEX_DIR / "embeddings_meta.json"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"
LEGACY_OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
DEFAULT_EMBED_MODEL = os.getenv("RAG_EMBED_MODEL", "nomic-embed-text")


def normalize_text(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def looks_like_toc_line(line):
    compact = re.sub(r"\s+", "", line)
    if not compact:
        return False
    if compact in {"審定書i", "中文摘要ii", "英文摘要iii", "誌謝iv", "表目錄vii", "圖目錄viii"}:
        return True
    patterns = [
        r"^表\d+[、.].+\d+$",
        r"^圖\d+[、.].+\d+$",
    ]
    return any(re.match(pattern, compact) for pattern in patterns)


def format_toc_page_line(line):
    compact = re.sub(r"\s+", "", line)
    patterns = [
        r"^([一二三四五六七八九十]+、.+?)(\d+)$",
        r"^(\d+\.\d+[\u4e00-\u9fff].+?)(\d+)$",
        r"^(附錄.+?)(\d+)$",
        r"^(目錄)([ivxlcdmIVXLCDM]+)$",
    ]
    for pattern in patterns:
        match = re.match(pattern, compact)
        if match:
            return f"{match.group(1)}（第 {match.group(2)} 頁）"
    return line


def clean_document_text(text):
    text = normalize_text(text)
    if not text:
        return ""

    cleaned_lines = []

    for raw_line in text.split("\n"):
        line = raw_line.strip()
        compact = re.sub(r"\s+", "", line)

        if compact in {"表目錄", "圖目錄"} or looks_like_toc_line(line):
            continue

        if re.fullmatch(r"(?:第\s*)?\d+\s*(?:頁)?", compact):
            continue
        if re.fullmatch(r"[ivxlcdmIVXLCDM]+", compact):
            continue

        cleaned_lines.append(format_toc_page_line(line))

    cleaned = "\n".join(cleaned_lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def tokenize(text):
    tokens = re.findall(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]+", text.lower())
    expanded = []
    for token in tokens:
        expanded.append(token)
        if re.fullmatch(r"[\u4e00-\u9fff]+", token):
            expanded.extend(token[index : index + 2] for index in range(len(token) - 1))
            expanded.extend(token[index : index + 3] for index in range(len(token) - 2))
    return expanded


def chunk_text(text, source, chunk_size=900, overlap=150):
    text = normalize_text(text)
    if not text:
        return []

    chunks = []
    chunk_id = 0
    paragraphs = [paragraph.strip() for paragraph in re.split(r"\n{2,}", text) if paragraph.strip()]
    buffer = []
    buffer_size = 0

    def flush():
        nonlocal buffer, buffer_size, chunk_id
        if not buffer:
            return
        window = "\n\n".join(buffer).strip()
        chunks.append(
            {
                "id": f"{Path(source).stem}-{chunk_id}",
                "source": source,
                "text": window.strip(),
            }
        )
        chunk_id += 1
        keep = []
        kept_size = 0
        for paragraph in reversed(buffer):
            if kept_size + len(paragraph) > overlap:
                break
            keep.insert(0, paragraph)
            kept_size += len(paragraph)
        buffer = keep
        buffer_size = kept_size

    for paragraph in paragraphs:
        if len(paragraph) > chunk_size:
            flush()
            sentences = re.split(r"(?<=[。.!?？])", paragraph)
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                if buffer_size + len(sentence) > chunk_size:
                    flush()
                buffer.append(sentence)
                buffer_size += len(sentence)
            continue

        if buffer_size + len(paragraph) > chunk_size:
            flush()
        buffer.append(paragraph)
        buffer_size += len(paragraph)

    flush()

    return chunks


def read_pdf(path):
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("Missing dependency: run `python -m pip install pypdf`.") from exc

    reader = PdfReader(str(path))
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(f"[Page {index}]\n{text}")
    return "\n\n".join(pages)


def read_docx(path):
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    parts = []

    with zipfile.ZipFile(path) as archive:
        document_names = [
            name
            for name in archive.namelist()
            if name == "word/document.xml" or name.startswith("word/header") or name.startswith("word/footer")
        ]

        for name in document_names:
            root = ElementTree.fromstring(archive.read(name))
            for paragraph in root.findall(".//w:p", namespace):
                texts = [node.text or "" for node in paragraph.findall(".//w:t", namespace)]
                text = "".join(texts).strip()
                if text:
                    parts.append(text)

    return "\n\n".join(parts)


def read_text_file(path):
    return path.read_text(encoding="utf-8", errors="ignore")


def read_document(path):
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return read_pdf(path)
    if suffix == ".docx":
        return read_docx(path)
    if suffix in {".txt", ".md"}:
        return read_text_file(path)
    raise RuntimeError(f"Unsupported file type: {path.suffix}. Use PDF, DOCX, TXT, or MD.")


def iter_input_files(input_path):
    path = Path(input_path)
    if path.is_file():
        if not path.name.startswith("~$"):
            yield path
        return

    for pattern in ("*.pdf", "*.docx", "*.txt", "*.md"):
        for file_path in path.rglob(pattern):
            if not file_path.name.startswith("~$"):
                yield file_path


def build_index(chunks):
    doc_freq = defaultdict(int)
    chunk_terms = []

    for chunk in chunks:
        counts = Counter(tokenize(chunk["text"]))
        chunk_terms.append(counts)
        for term in counts:
            doc_freq[term] += 1

    total = max(1, len(chunks))
    vocab = {
        term: math.log((1 + total) / (1 + freq)) + 1
        for term, freq in doc_freq.items()
    }

    return vocab, chunk_terms


def save_index(chunks, vocab):
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    with CHUNKS_FILE.open("w", encoding="utf-8") as file:
        for chunk in chunks:
            file.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    VOCAB_FILE.write_text(json.dumps(vocab, ensure_ascii=False, indent=2), encoding="utf-8")


def normalize_embedding(vector):
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def ollama_embed_batch(texts, model):
    payload = {"model": model, "input": texts}
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(OLLAMA_EMBED_URL, data=data, method="POST", headers={"Content-Type": "application/json"})
    try:
        with request.urlopen(req, timeout=300) as response:
            result = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        if exc.code != 404:
            raise RuntimeError(f"Ollama embedding failed: HTTP {exc.code}") from exc
        return [ollama_embed_legacy(text, model) for text in texts]
    except error.URLError as exc:
        raise RuntimeError("Cannot connect to Ollama embeddings. Start it with `ollama serve`.") from exc

    embeddings = result.get("embeddings")
    if not embeddings:
        raise RuntimeError(f"Ollama did not return embeddings. Is `{model}` an embedding model?")
    return [normalize_embedding([float(value) for value in embedding]) for embedding in embeddings]


def ollama_embed_legacy(text, model):
    payload = {"model": model, "prompt": text}
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(LEGACY_OLLAMA_EMBED_URL, data=data, method="POST", headers={"Content-Type": "application/json"})
    try:
        with request.urlopen(req, timeout=300) as response:
            result = json.loads(response.read().decode("utf-8"))
    except error.URLError as exc:
        raise RuntimeError("Cannot connect to Ollama embeddings. Start it with `ollama serve`.") from exc

    embedding = result.get("embedding")
    if not embedding:
        raise RuntimeError(f"Ollama did not return an embedding. Is `{model}` an embedding model?")
    return normalize_embedding([float(value) for value in embedding])


def build_embedding_index(chunks, model=DEFAULT_EMBED_MODEL, batch_size=8):
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    dimension = None

    with EMBEDDINGS_FILE.open("w", encoding="utf-8") as file:
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start : start + batch_size]
            embeddings = ollama_embed_batch([chunk["text"] for chunk in batch], model)
            for chunk, embedding in zip(batch, embeddings):
                if dimension is None:
                    dimension = len(embedding)
                file.write(
                    json.dumps(
                        {"id": chunk["id"], "embedding": embedding},
                        ensure_ascii=False,
                        separators=(",", ":"),
                    )
                    + "\n"
                )
                count += 1
            print(f"  -> embedded {min(start + batch_size, len(chunks))}/{len(chunks)} chunk(s)")

    meta = {
        "model": model,
        "count": count,
        "dimension": dimension,
    }
    EMBEDDINGS_META_FILE.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def load_embedding_index():
    if not EMBEDDINGS_FILE.exists() or not EMBEDDINGS_META_FILE.exists():
        return None, None

    meta = json.loads(EMBEDDINGS_META_FILE.read_text(encoding="utf-8"))
    embeddings = {}
    with EMBEDDINGS_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            item = json.loads(line)
            embeddings[item["id"]] = item["embedding"]
    return embeddings, meta


def load_index():
    if not CHUNKS_FILE.exists() or not VOCAB_FILE.exists():
        raise RuntimeError("No index found. Run `python thesis_rag.py ingest rag_docs` first.")

    chunks = []
    with CHUNKS_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            chunks.append(json.loads(line))
    vocab = json.loads(VOCAB_FILE.read_text(encoding="utf-8"))
    return chunks, vocab


def vectorize(text, vocab):
    counts = Counter(tokenize(text))
    vector = {}
    for term, count in counts.items():
        if term in vocab:
            vector[term] = count * vocab[term]
    norm = math.sqrt(sum(value * value for value in vector.values()))
    return vector, norm


def cosine(left, left_norm, right, right_norm):
    if left_norm == 0 or right_norm == 0:
        return 0.0
    if len(left) > len(right):
        left, right = right, left
    score = sum(value * right.get(term, 0.0) for term, value in left.items())
    return score / (left_norm * right_norm)


def retrieve(question, top_k=5):
    chunks, vocab = load_index()
    embeddings, meta = load_embedding_index()
    if embeddings and meta:
        query_embedding = ollama_embed_batch([question], meta["model"])[0]
        scored = []
        for chunk in chunks:
            chunk_embedding = embeddings.get(chunk["id"])
            if not chunk_embedding:
                continue
            score = sum(left * right for left, right in zip(query_embedding, chunk_embedding))
            scored.append((score, chunk))

        scored.sort(key=lambda item: item[0], reverse=True)
        return scored[:top_k]

    query_vector, query_norm = vectorize(question, vocab)
    scored = []

    for chunk in chunks:
        chunk_vector, chunk_norm = vectorize(chunk["text"], vocab)
        score = cosine(query_vector, query_norm, chunk_vector, chunk_norm)
        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda item: item[0], reverse=True)
    return scored[:top_k]


def ollama_generate(prompt, model):
    payload = {"model": model, "prompt": prompt, "stream": False}
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(OLLAMA_URL, data=data, method="POST", headers={"Content-Type": "application/json"})
    try:
        with request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result.get("response", "").strip()
    except error.URLError as exc:
        raise RuntimeError("Cannot connect to Ollama. Start it with `ollama serve`.") from exc


def format_context(results):
    parts = []
    for index, (score, chunk) in enumerate(results, start=1):
        parts.append(
            f"[{index}] Source: {chunk['source']} | Score: {score:.3f}\n{chunk['text']}"
        )
    return "\n\n".join(parts)


def direct_page_lookup(question, results):
    if not re.search(r"第幾頁|哪一頁|幾頁|page", question, re.IGNORECASE):
        return None

    stop_terms = {
        "第幾頁",
        "哪一頁",
        "幾頁",
        "開始",
        "部分",
        "從",
        "在",
        "第",
        "頁",
        "的",
        "是",
        "嗎",
    }
    question_terms = {
        term
        for term in tokenize(question)
        if len(term) > 1 and term not in stop_terms
    }

    best = None
    for _score, chunk in results:
        for line in chunk["text"].splitlines():
            match = re.search(r"(.+?)（第\s*([0-9ivxlcdmIVXLCDM]+)\s*頁）", line.strip())
            if not match:
                continue
            title = match.group(1).strip()
            page = match.group(2).strip()
            title_tokens = set(tokenize(title))
            overlap = len(question_terms & title_tokens)
            if "實驗" in question and "實驗" in title:
                overlap += 5
            if best is None or overlap > best[0]:
                best = (overlap, title, page)

    if not best or best[0] <= 0:
        return None
    return f"{best[1]} 從第 {best[2]} 頁開始。"


def ingest(input_path, embed_model=DEFAULT_EMBED_MODEL, use_embeddings=True):
    all_chunks = []
    for path in iter_input_files(input_path):
        print(f"Reading {path}")
        text = read_document(path)
        text = clean_document_text(text)
        chunks = chunk_text(text, str(path))
        print(f"  -> {len(chunks)} chunk(s)")
        all_chunks.extend(chunks)

    if not all_chunks:
        raise RuntimeError("No supported documents found.")

    vocab, _ = build_index(all_chunks)
    save_index(all_chunks, vocab)
    print(f"Indexed {len(all_chunks)} chunks from {input_path}")
    print(f"Index saved to {INDEX_DIR.resolve()}")
    if use_embeddings:
        print(f"Building embedding index with `{embed_model}`")
        build_embedding_index(all_chunks, model=embed_model)
        print(f"Embedding index saved to {EMBEDDINGS_FILE.resolve()}")


def ask(question, top_k, model=None):
    results = retrieve(question, top_k=top_k)
    if not results:
        print("No relevant chunks found.")
        return

    page_answer = direct_page_lookup(question, results)
    if page_answer:
        print(page_answer)
        return

    context = format_context(results)
    if not model:
        print(context)
        print("\nTip: add `--model llama3.1` to generate an answer with local Ollama.")
        return

    prompt = f"""You are a careful research assistant.
Answer the question using only the provided context.
If the context is not enough, say what is missing.
Cite sources with bracket numbers like [1], [2].

Question:
{question}

Context:
{context}

Answer in Traditional Chinese:"""
    print(ollama_generate(prompt, model))


def main():
    parser = argparse.ArgumentParser(description="Simple local RAG for thesis PDFs and Word files.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Index PDF/DOCX/TXT/MD files.")
    ingest_parser.add_argument("path", nargs="?", default=str(DOCS_DIR), help="File or folder to index.")
    ingest_parser.add_argument("--embed-model", default=DEFAULT_EMBED_MODEL, help="Ollama embedding model to use.")
    ingest_parser.add_argument("--no-embeddings", action="store_true", help="Build only the keyword index.")

    ask_parser = subparsers.add_parser("ask", help="Ask a question against the local index.")
    ask_parser.add_argument("question", help="Question to ask.")
    ask_parser.add_argument("--top-k", type=int, default=5, help="Number of chunks to retrieve.")
    ask_parser.add_argument("--model", help="Optional local Ollama model, for example llama3.1.")

    args = parser.parse_args()
    try:
        if args.command == "ingest":
            ingest(args.path, embed_model=args.embed_model, use_embeddings=not args.no_embeddings)
        elif args.command == "ask":
            ask(args.question, args.top_k, args.model)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
