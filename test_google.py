from googlesearch import search

try:
    print("Testing Google Search...")
    results = search("fenerbahçe başkanı kim", num_results=3, advanced=True)
    for i, result in enumerate(results):
        print(f"{i+1}. {result.title}")
        print(f"   {result.description}")
        print(f"   {result.url}")
except Exception as e:
    print(f"Error: {e}")
