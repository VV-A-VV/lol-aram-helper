import urllib.request
import json

url = 'https://hextech.dtodo.cn/api/aram/champions'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    with urllib.request.urlopen(req, timeout=10) as res:
        data = json.loads(res.read())
        with open('champions_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Success")
except Exception as e:
    print(f"Error: {e}")
