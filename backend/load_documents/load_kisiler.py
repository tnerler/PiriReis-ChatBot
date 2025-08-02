import json
from langchain.schema import Document
import hashlib
import os
from typing import List, Dict, Any
import glob


def compute_hash(content: str) -> str:
    """
    Computes a SHA256 hash from content to prevent duplicate document loading.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def process_data(data: List[Dict], source_file: str) -> List[Document]:
    """
    Process people JSON structure which contains information about 
    people organized by department or role.
    """
    documents = []
    
    for item in data:
        if "type" in item and "context" in item:
            department = item["type"]
            
            # Process context which can be a list of strings with people info
            if isinstance(item["context"], list):
                # Join all entries with newlines to create a single document for this department
                people_info = "\n".join(item["context"])
                text = f"{department}:\n\n{people_info}"
                
                doc_hash = compute_hash(text)
                documents.append(Document(
                    page_content=text,
                    metadata={
                        "hash": doc_hash,
                        "department": department,
                        "type": "personnel",
                        "source": source_file
                    }
                ))
    
    return documents