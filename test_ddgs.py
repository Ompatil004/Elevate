from duckduckgo_search import DDGS

with DDGS() as ddgs:
    results = ddgs.images("push up exercise", type_image="gif", max_results=1)
    for r in results:
        print("Found GIF:", r['image'])
