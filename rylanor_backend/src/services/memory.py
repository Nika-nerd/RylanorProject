import chromadb
from typing import List, Dict

class MemoryManager:
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.chroma_client.get_or_create_collection(name="rylanor_long_term")
        
       
        self.short_term: Dict[str, List[Dict]] = {}
        self.max_short_term_history = 10 

    def add_to_short_term(self, user_id: str, role: str, text: str):
        if user_id not in self.short_term:
            self.short_term[user_id] = []
            
        self.short_term[user_id].append({"role": role, "parts": [text]})
        
        if len(self.short_term[user_id]) > self.max_short_term_history * 2:
            self.short_term[user_id] = self.short_term[user_id][-(self.max_short_term_history * 2):]

    def get_short_term(self, user_id: str) -> List[Dict]:
        return self.short_term.get(user_id, [])

    def add_to_long_term(self, user_id: str, text: str, doc_id: str):
        self.collection.add(
            documents=[text],
            metadatas=[{"user_id": user_id}],
            ids=[doc_id]
        )

    def get_relevant_context(self, user_id: str, query: str, n_results: int = 3) -> str:
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where={"user_id": user_id} 
        )
        
        documents = results.get("documents", [[]])[0]
        if not documents:
            return ""
            
        return "\n".join(documents)

memory_manager = MemoryManager()