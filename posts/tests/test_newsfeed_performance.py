import requests
import time

def test_newsfeed_performance():
    start_time = time.time()
    
    # Test different pagination scenarios
    test_urls = [
        'https://127.0.0.1:8000/posts/api/posts//',
        'https://127.0.0.1:8000/posts/api/posts/?page=1&page_size=10',
        'https://127.0.0.1:8000/posts/api/posts/?page=2&page_size=5'
    ]
    
    for url in test_urls:
        response = requests.get(url)
        
        # Performance Assertions
        assert response.status_code == 200, f"Failed to fetch posts from {url}"
        
        data = response.json()
        assert 'posts' in data, "Response missing posts"
        assert 'pagination' in data, "Response missing pagination info"
        
        print(f"URL: {url}")
        print(f"Total Posts: {len(data['posts'])}")
        print(f"Pagination: {data.get('pagination', {})}")
    
    end_time = time.time()
    print(f"Total Execution Time: {end_time - start_time} seconds")

# Run the test
test_newsfeed_performance()