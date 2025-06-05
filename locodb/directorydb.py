import json
from pathlib import Path
from datetime import datetime

from locodb.utility import get_timestamp


class LocoDatabase:
    """A class that mimics the pymongo API but stores data in a directory structure."""

    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.base_path.mkdir(
            parents=True, exist_ok=True
        )  # Ensure base directory exists

    def __getitem__(self, db_name):
        """Get a database (top-level directory)."""
        return Database(self.base_path / db_name)


class Database:
    """Represents a MongoDB-like database (maps to a top-level directory)."""

    def __init__(self, path):
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)  # Ensure database directory exists

    def __getitem__(self, collection_name):
        """Get a collection (second-level directory)."""
        return Collection(self.path / collection_name)

    def list_collections(self):
        """List available collections in the database."""
        return [d.name for d in self.path.iterdir() if d.is_dir()]


class Collection:
    """Represents a MongoDB-like collection (maps to a subdirectory)."""

    def __init__(self, path):
        self.path = Path(path)
        self.path.mkdir(
            parents=True, exist_ok=True
        )  # Ensure collection directory exists

    def insert_one(self, doc):
        """Insert a single document (store as a JSON file)."""
        doc_id = doc.get(
            "_id", str(len(list(self.path.iterdir())) + 1)
        )  # Auto-generate ID if not given
        doc["_id"] = doc_id  # Ensure _id exists
        doc["_timestamp"] = get_timestamp()
        with open(self.path / f"{doc_id}.json", "w") as f:
            json.dump(doc, f, indent=4)
        return {"_id": doc_id}

    def find_one(self, query):
        """Find a document that matches ALL key-value pairs in the query."""
        for file in self.path.glob("*.json"):
            with open(file, "r") as f:
                doc = json.load(f)
                # Check if all key-value pairs in the query exist in the document
                if all(doc.get(k) == v for k, v in query.items()):
                    return doc  # Return the first matching document
        return None  # No match found

    def find_all(self, query):
        """Find all documents that match ALL key-value pairs in the query."""
        matching_docs = []
        for file in self.path.glob("*.json"):
            with open(file, "r") as f:
                doc = json.load(f)
                # Check if all key-value pairs in the query exist in the document
                if all(doc.get(k) == v for k, v in query.items()):
                    matching_docs.append(doc)

        return matching_docs  # Return all matching documents (empty list if no match)

    def find_most_recent_matching(self, query):
        """Find the most recent document that matches ALL key-value pairs in the query."""
        most_recent_doc = None
        most_recent_time = datetime.min  # Start with the earliest possible datetime

        for file in self.path.glob("*.json"):
            with open(file, "r") as f:
                doc = json.load(f)

                # Check if the document matches the query
                if not all(doc.get(k) == v for k, v in query.items()):
                    continue  # Skip if it doesn't match

                # Parse '_timestamp' if it exists
                if "_timestamp" in doc:
                    try:
                        timestamp = datetime.fromisoformat(doc["_timestamp"])
                        if timestamp > most_recent_time:
                            most_recent_time = timestamp
                            most_recent_doc = doc
                    except ValueError:
                        continue  # Skip invalid date formats

        return most_recent_doc  # Return the most recent matching document (or None if no match)

    def find_most_recent_matching_set(self, query={}):
        """Find the set of documents with the most recent '_timestamp' timestamp."""
        most_recent_docs = []
        most_recent_time = datetime.min
        for file in self.path.glob("*.json"):
            with open(file, "r") as f:
                doc = json.load(f)
                # Check if the document matches the query
                if not all(doc.get(k) == v for k, v in query.items()):
                    continue  # Skip if it doesn't match

                if "_timestamp" in doc:
                    # _timestamp is stored as an ISO string
                    # e.g., "2025-03-14 16:15:30 UTC"
                    timestamp_str = doc["_timestamp"].replace(" UTC", "")
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    # If later _timestamp found, then update most_recent_time and most_recent_docs
                    if timestamp > most_recent_time:
                        most_recent_time = timestamp
                        most_recent_docs = [doc]
                    # If same _timestamp found, then just append to most_recent_docs
                    elif timestamp == most_recent_time:
                        most_recent_docs.append(doc)
        return most_recent_docs

    def find(self):
        """Return all documents in the collection."""
        documents = []
        for file in self.path.glob("*.json"):
            with open(file, "r") as f:
                documents.append(json.load(f))
        return documents

    def delete_one(self, query):
        """Delete a document by a simple key-value pair."""
        for file in self.path.glob("*.json"):
            with open(file, "r") as f:
                doc = json.load(f)
                if all(doc.get(k) == v for k, v in query.items()):
                    file.unlink()  # Delete the file
                    return {"deleted_count": 1}
        return {"deleted_count": 0}

    def list_documents(self):
        """List all document filenames in the collection."""
        return [file.name for file in self.path.glob("*.json")]


# Example Usage
if __name__ == "__main__":
    client = LocoDatabase("cluster")  # Base directory
    database = client["node0"]  # Access database
    collection = database["gpu0"]  # Access collection

    # Add document to collection
    collection.insert_one(
        {
            "vendor": "AMD",
            "model": "MI300X",
            "vram_total": 192,
            "vram_used": 98.384,
        }
    )

    # Metadata is prepended with "_"
    # "_id" is auto-generated if not provided
    # "_timestamp" is added automatically

    collection = database["gpu1"]
    collection.insert_one(
        {
            "vendor": "AMD",
            "model": "MI300X",
            "vram_total": 192,
            "vram_used": 23.294,
        }
    )

    # Retrieve documents
    print(
        "Find most recent:",
        collection.find_most_recent_matching({"model": "MI300X"}),
    )

    # Delete a document
    print("Delete Result:", collection.delete_one({"_id": "1"}))

    # List collections and documents
    print("Collections in DB:", database.list_collections())
    print("Documents in Collection:", collection.list_documents())
