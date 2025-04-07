import requests
import time

def test_caching():
    url = 'https://127.0.0.1:8000/posts/api/posts/'
    
    # First request
    start_time = time.time()
    first_response = requests.get(url)
    first_time = time.time() - start_time
    
    # Second request (should be faster if cached)
    start_time = time.time()
    second_response = requests.get(url)
    second_time = time.time() - start_time
    
    print(f"First Request Time: {first_time}")
    print(f"Second Request Time: {second_time}")
    
    # Check if second request is significantly faster
    assert second_time < first_time, "Caching might not be working"