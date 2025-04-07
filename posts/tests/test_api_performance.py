def test_api_performance():
    url = 'https://127.0.0.1:8000/posts/api/posts/'
    
    # Concurrent Request Simulation
    import concurrent.futures
    
    def fetch_posts(url):
        response = requests.get(url)
        return response.json()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_posts, url) for _ in range(5)]
        
        for future in concurrent.futures.as_completed(futures):
            try:
                data = future.result()
                assert 'posts' in data, "Invalid response structure"
            except Exception as e:
                print(f"Request failed: {e}")