import urllib.request, json

headers = {"User-Agent": "Mozilla/5.0"}

def fetch(url):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as r:
            return r.read().decode()
    except:
        return None

# Get all repos
req = urllib.request.Request(
    "https://api.github.com/users/ammarfitwalla/repos?per_page=100",
    headers=headers
)
with urllib.request.urlopen(req) as r:
    repos = json.load(r)

for repo in repos:
    name = repo['name']
    lang = repo['language'] or 'None'
    
    # Try requirements.txt
    deps = fetch(f"https://raw.githubusercontent.com/ammarfitwalla/{name}/main/requirements.txt")
    if not deps:
        deps = fetch(f"https://raw.githubusercontent.com/ammarfitwalla/{name}/master/requirements.txt")
    
    print(f"\n{'='*40}")
    print(f"Repo: {name} | Language: {lang}")
    if deps:
        print(f"Dependencies:\n{deps[:500]}")  # cap at 500 chars
    else:
        print("No requirements.txt found")