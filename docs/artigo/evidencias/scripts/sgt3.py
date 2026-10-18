import re, html, sys
from sgt import call
for termo, tab in (("Feminic","A"),("Mulher","A"),("Maria da Penha","A"),("Maria da Penha","C"),("Medidas Protetivas","C")):
    t = call("pesquisarItemPublicoWS", f"<tipoTabela>{tab}</tipoTabela><tipoPesquisa>N</tipoPesquisa><valorPesquisa>{termo}</valorPesquisa>")
    items = re.findall(r"<cod_item[^>]*>(\d+)</cod_item>.*?<nome[^>]*>(.*?)</nome>", t, re.S)
    print(f"== {tab} '{termo}':", [(int(c), html.unescape(n).strip()) for c, n in items])
