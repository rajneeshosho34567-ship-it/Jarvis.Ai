import chromadb
from chromadb.utils import embedding_functions
import uuid
import time

class MemoryStore:
    def __init__(self, path="./chroma_db"):
        self.client = chromadb.PersistentClient(path=path)
        self.embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.collection = self.client.get_or_create_collection(
            name="personal_memory",
            embedding_function=self.embed_fn
        )

    def add_memory(self, text: str, category: str = "chat"):
        self.collection.add(
            documents=[text],
            metadatas=[{"category": category, "timestamp": time.time()}],
            ids=[str(uuid.uuid4())]
        )

    def retrieve_relevant(self, query: str, k: int = 4):
        results = self.collection.query(query_texts=[query], n_results=k)
        docs = results.get("documents", [[]])[0]
        return docs