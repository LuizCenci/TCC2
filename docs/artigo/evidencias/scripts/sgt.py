# Consulta o webservice público SGT/CNJ: hierarquia (pais) e nome oficial de itens da TPU.
import json, re, sys, time, html, requests
URL = "https://www.cnj.jus.br/sgt/sgt_ws.php"
def call(op, inner):
    env = f'<?xml version="1.0"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:sgt="{URL}"><soapenv:Body><sgt:{op}>{inner}</sgt:{op}></soapenv:Body></soapenv:Envelope>'
    r = requests.post(URL, data=env.encode(), headers={"Content-Type": "text/xml; charset=utf-8", "SOAPAction": f"{URL}#{op}"}, timeout=60)
    r.raise_for_status(); time.sleep(0.5)
    try: return r.content.decode('utf-8')
    except UnicodeDecodeError: return r.content.decode('iso-8859-1')
def parents(code, tipo):
    m = re.search(r"<return>(.*?)</return>", call("getStringPaisItemPublicoWS", f"<seqItem>{code}</seqItem><tipoItem>{tipo}</tipoItem>"), re.S)
    return [int(x) for x in m.group(1).split(",") if x.strip()] if m else []
def item(code, tabela):
    t = call("pesquisarItemPublicoWS", f"<tipoTabela>{tabela}</tipoTabela><tipoPesquisa>C</tipoPesquisa><valorPesquisa>{code}</valorPesquisa>")
    g = lambda tag: (lambda m: html.unescape(m.group(1)).strip() if m else None)(re.search(fr"<{tag}[^>]*>(.*?)</{tag}>", t, re.S))
    return {"nome": g("nome"), "dispositivo_legal": g("dispositivoLegal"), "artigo": g("artigo"), "glossario": g("dscGlossario"), "raw_len": len(t)}
if __name__ == '__main__':
    out = {}
    for tabela, codes in (("A", [10948,10949,11979,12194,12196,14097,14098,14226,14227,14228,14229,14942,14943,14944,14945,12091,5560,14684,14686,12195,9647]), ("C", [1268])):
        for c in codes:
            ps = parents(c, tabela)
            chain = [{"codigo": p, **{k: v for k, v in item(p, tabela).items() if k == "nome"}} for p in ps if p != c]
            out[f"{tabela}{c}"] = {"codigo": c, "tabela": tabela, **item(c, tabela), "pais": chain}
            print(tabela, c, out[f"{tabela}{c}"]["nome"], "<-", " > ".join(f'{p["codigo"]} {p.get("nome")}' for p in chain), flush=True)
    json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
