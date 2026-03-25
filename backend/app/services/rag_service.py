from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import requests
from bs4 import BeautifulSoup

model = SentenceTransformer('all-MiniLM-L6-v2')

data_store = []

# ✅ SCRAPER
def fetch_website(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        session = requests.Session()
        session.max_redirects = 5

        res = session.get(
            url,
            headers=headers,
            timeout=10,
            allow_redirects=True
        )

        if res.status_code != 200:
            print(f"❌ Failed: {url}")
            return ""

    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
        return ""

    soup = BeautifulSoup(res.text, "html.parser")

    # Remove garbage tags
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.extract()

    text = soup.get_text(separator=" ")

    return text[:15000]


# ✅ SMART CHUNKING
def split_text(text, chunk_size=300):
    sentences = text.split(". ")
    chunks = []
    chunk = ""

    for sentence in sentences:
        if len(chunk) + len(sentence) < chunk_size:
            chunk += sentence + ". "
        else:
            chunks.append(chunk)
            chunk = sentence

    if chunk:
        chunks.append(chunk)

    return chunks


# ✅ BUILD KNOWLEDGE BASE
def build_knowledge_base(urls):
    global data_store
    data_store = []

    print("⚡ Building RAG...")

    for url in urls:
        print(f"🔍 Scraping: {url}")
        raw_text = fetch_website(url)

        if not raw_text:
            continue

        chunks = split_text(raw_text)
        embeddings = model.encode(chunks)

        for chunk, emb in zip(chunks, embeddings):
            clean = chunk.strip()

            # ✅ FIX: Only filter by length — no keyword restriction
            # This ensures ALL content (fees, greetings, general info) is stored
            if len(clean) > 50:
                data_store.append({
                    "text": clean,
                    "embedding": emb
                })

    print(f"✅ RAG Ready | Chunks: {len(data_store)}")


# ✅ SEARCH (FAST + RELEVANT)
def search(query, top_k=3):
    if not data_store:
        return ["No data available"]

    query_emb = model.encode([query])[0]

    scored = []
    for item in data_store:
        score = cosine_similarity(
            [item["embedding"]],
            [query_emb]
        )[0][0]

        scored.append((score, item["text"]))

    scored.sort(key=lambda x: x[0], reverse=True)

    # ✅ FIX: Lowered threshold from 0.25 → 0.15 so more results pass through
    results = [text for score, text in scored if score > 0.15]

    return results[:top_k] if results else ["Not available on website"]