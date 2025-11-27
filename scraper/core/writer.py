# scraper/core/writer.py

import json
import os

class JSONLWriter:
    """
    JSONL writer that supports idempotent append or full overwrite
    Deduplicates documents using a content hash
    """

    def __init__(self, output_path, overwrite=False, hash_key="content_hash"):
        self.output_path = output_path
        self.overwrite = overwrite
        self.hash_key = hash_key
        self._seen_hashes = set()

        # If overwrite requested → delete old file
        if self.overwrite and os.path.exists(self.output_path):
            os.remove(self.output_path)

        # Load existing hashes only if not overwriting
        if not self.overwrite:
            self._load_existing_hashes()

        # Open file correctly
        mode = "w" if self.overwrite else "a"
        self.file = open(self.output_path, mode, encoding="utf-8")

    def _load_existing_hashes(self):
        """Load hash values from existing JSONL file to ensure idempotency."""
        if not os.path.exists(self.output_path):
            return

        with open(self.output_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    record = json.loads(line)
                    record_hash = record.get(self.hash_key)
                    if record_hash:
                        self._seen_hashes.add(record_hash)
                except json.JSONDecodeError:
                    continue  # skip malformed lines

    def write(self, record):
        """
        Write a single JSON object to the JSONL file if its hash is new.
        Ensures idempotency during append operations.
        """
        record_hash = record.get(self.hash_key)
        if not record_hash:
            raise ValueError(f"Record missing required key: '{self.hash_key}'")

        # Skip previously written content
        if record_hash in self._seen_hashes:
            return

        # Write new entry
        self.file.write(json.dumps(record, ensure_ascii=False) + "\n")
        self._seen_hashes.add(record_hash)

    def close(self):
        """Close the file handle."""
        if hasattr(self, "file") and not self.file.closed:
            self.file.close()