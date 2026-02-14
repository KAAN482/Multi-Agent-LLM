from duckduckgo_search import DDGS
import json

try:
    print("Testing DDGS (backend='html')...")
    with DDGS() as ddgs:
        # backend="html" is often more resilient
        results = list(ddgs.text("fenerbahçe başkanı kim", max_results=3, backend="html"))
        if results:
            print(f"Success! Found {len(results)} results.")
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print("No results found.")
except Exception as e:
    print(f"Error: {e}")
