import requests
import json
import os

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print("Health Check:")
    print(json.dumps(response.json(), indent=2))
    print()

def test_upload_pdf():
    """Test PDF upload (you need a PDF file for this)"""
    # This is just a placeholder - you'll need an actual PDF file
    pdf_path = "sample.pdf"  # Replace with actual PDF path
    
    if os.path.exists(pdf_path):
        with open(pdf_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/upload-pdf", files=files)
            print("Upload PDF:")
            print(json.dumps(response.json(), indent=2))
            print()
            return response.json().get('document_id')
    else:
        print(f"PDF file {pdf_path} not found. Skipping upload test.")
        print()
        return None

def test_ask_question():
    """Test asking a question"""
    question_data = {
        "question": "What is machine learning?",
        "max_context_chunks": 3
    }
    
    response = requests.post(f"{BASE_URL}/ask", json=question_data)
    print("Ask Question:")
    print(json.dumps(response.json(), indent=2))
    print()

def test_documents():
    """Test getting documents list"""
    response = requests.get(f"{BASE_URL}/documents")
    print("Documents List:")
    print(json.dumps(response.json(), indent=2))
    print()

def test_stats():
    """Test getting stats"""
    response = requests.get(f"{BASE_URL}/stats")
    print("System Stats:")
    print(json.dumps(response.json(), indent=2))
    print()

if __name__ == "__main__":
    print("Testing RAG Production API\n" + "="*50)
    
    # Test all endpoints
    test_health()
    test_documents()
    test_stats()
    
    # Try upload if PDF exists
    doc_id = test_upload_pdf()
    
    # Test question (will work if documents exist)
    test_ask_question()
    
    print("Testing complete!")
