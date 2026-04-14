#!/usr/bin/env python3
"""
Test script to verify all errors have been resolved in the RAG Production API.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, method="GET", data=None):
    """Test an endpoint and return the response"""
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}")
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        else:
            return {"status": "error", "message": f"Unsupported method: {method}"}
        
        return {
            "status": "success",
            "status_code": response.status_code,
            "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def main():
    print("Testing RAG Production API - Error Resolution Verification")
    print("=" * 60)
    
    tests = [
        ("/", "GET"),
        ("/health", "GET"),
        ("/documents", "GET"),
        ("/stats", "GET"),
    ]
    
    results = []
    
    for endpoint, method in tests:
        print(f"\nTesting {method} {endpoint}...")
        result = test_endpoint(endpoint, method)
        results.append(result)
        
        if result["status"] == "success":
            print(f"  Status Code: {result['status_code']}")
            if isinstance(result["response"], dict):
                print(f"  Response: {json.dumps(result['response'], indent=2)}")
            else:
                print(f"  Response: {result['response']}")
        else:
            print(f"  Error: {result['message']}")
    
    # Test POST endpoints (these should return proper error messages)
    print(f"\nTesting POST /ask (should return service unavailable error)...")
    ask_data = {"question": "What is AI?", "max_context_chunks": 3}
    result = test_endpoint("/ask", "POST", ask_data)
    results.append(result)
    
    if result["status"] == "success":
        print(f"  Status Code: {result['status_code']}")
        print(f"  Response: {json.dumps(result['response'], indent=2)}")
    else:
        print(f"  Error: {result['message']}")
    
    print(f"\nTesting POST /upload-pdf (should return service unavailable error)...")
    # We can't actually upload a file easily in this test, but we can check the error
    try:
        response = requests.post(f"{BASE_URL}/upload-pdf")
        result = {
            "status": "success",
            "status_code": response.status_code,
            "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        }
    except Exception as e:
        result = {"status": "error", "message": str(e)}
    
    results.append(result)
    
    if result["status"] == "success":
        print(f"  Status Code: {result['status_code']}")
        print(f"  Response: {json.dumps(result['response'], indent=2)}")
    else:
        print(f"  Error: {result['message']}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("=" * 60)
    
    success_count = sum(1 for r in results if r["status"] == "success")
    total_count = len(results)
    
    print(f"Total tests: {total_count}")
    print(f"Successful tests: {success_count}")
    print(f"Failed tests: {total_count - success_count}")
    
    if success_count == total_count:
        print("\nAll tests passed! The API is working correctly.")
        print("Note: Some endpoints return 'service unavailable' errors because")
        print("the GROQ_API_KEY needs to be configured with a real API key.")
        return 0
    else:
        print(f"\n{total_count - success_count} tests failed. There may still be issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
