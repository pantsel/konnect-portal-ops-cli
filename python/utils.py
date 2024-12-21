import base64

def read_file_content(file_path: str) -> str:
    with open(file_path, 'rb') as f:
        return f.read()

def encode_content(content: str) -> str:
    return base64.b64encode(content).decode('utf-8')