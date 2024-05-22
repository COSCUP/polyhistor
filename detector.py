import os
import hashlib
import json

def calculate_file_hash(file_path):
    """Calculate the hash value of the given file"""
    hash_algo = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hash_algo.update(chunk)
    return hash_algo.hexdigest()

def get_files_hashes(directory):
    """Get hash values of all files in the directory"""
    files_hashes = {}
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            files_hashes[file_path] = calculate_file_hash(file_path)
    return files_hashes

def save_hashes(hashes, file_path):
    """Save hash values to a JSON file"""
    with open(file_path, 'w') as f:
        json.dump(hashes, f, indent=4)

def load_hashes(file_path):
    """Load hash values from a JSON file"""
    if not os.path.exists(file_path):
        return {}
    with open(file_path, 'r') as f:
        return json.load(f)

def compare(directory, hash_file):
    """Detect changes in the directory by comparing current hash values with saved hash values"""
    old_hashes = load_hashes(hash_file)
    new_hashes = get_files_hashes(directory)
    
    modified_files = [file_path for file_path, new_hash in new_hashes.items() if old_hashes.get(file_path) != new_hash]
    
    save_hashes(new_hashes, hash_file)
    
    return modified_files

def main():
    dir_path = 'path/to/directory'
    hash_file_path = 'path/to/hash_file.json'
    
    modified_files = compare(dir_path, hash_file_path)
    
    if modified_files:
        print("Modified files:")
        for file in modified_files:
            print(file)
    else:
        print("No files were modified.")


if __name__ == "__main__":
    main()