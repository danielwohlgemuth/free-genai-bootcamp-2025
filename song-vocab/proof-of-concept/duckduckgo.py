from duckduckgo_search import DDGS

results = DDGS().text("python programming", max_results=1)

print(results)
# Output: [{'title': 'Welcome to Python.org', 'href': 'https://www.python.org/', 'body': "Python is a programming language that lets you work quickly and integrate systems more effectively. Learn More. Get Started. Whether you're new to programming or an experienced developer, it's easy to learn and use Python. Start with our Beginner's Guide. Download."}]

print([result['href'] for result in results])
# Output: ['https://www.python.org/']
