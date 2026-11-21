import hashlib


def generate_fingerprint(file_path):
    try:
        hash_sh256 = hashlib.sha256()

        with open(file_path, "rb") as f:
            # Read the file in chunks to avoid loading the entire file into memory
            # Default page and sector size is 4096 bytes
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sh256.update(chunk)
        return hash_sh256.hexdigest()
    except Exception as e:
        raise Exception(f"Error occurred while generating fingerprint: {str(e)}")