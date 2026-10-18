# Consulta exploratória de agregações (size=0). Nunca imprime a chave.
import json, os, sys, time, requests
sys.path.insert(0, "src")
from datajud_tcc.cli import _load_dotenv
_load_dotenv()
KEY = os.environ["DATAJUD_API_KEY"]
URL = "https://api-publica.datajud.cnj.jus.br/api_publica_tjpr/_search"
def search(body):
    for i in range(4):
        r = requests.post(URL, json=body, headers={"Authorization": f"APIKey {KEY}", "Content-Type": "application/json"}, timeout=(10, 120))
        if r.status_code == 429:
            time.sleep(int(r.headers.get("Retry-After", 10))); continue
        if r.status_code >= 500: time.sleep(5); continue
        return r.status_code, r.json()
    return r.status_code, {"error": r.text[:500]}
if __name__ == "__main__":
    body = json.load(open(sys.argv[1], encoding="utf-8"))
    code, data = search(body)
    out = sys.argv[2]
    json.dump({"status": code, "body": body, "response": data}, open(out, "w", encoding="utf-8"), ensure_ascii=False)
    print(code, data.get("hits", {}).get("total"), data.get("took"), list(data.get("aggregations", {}).keys()), str(data.get("error",""))[:300])
