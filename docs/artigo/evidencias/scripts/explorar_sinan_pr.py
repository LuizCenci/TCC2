# Script exploratório (fora do pipeline). Gera os números de docs/artigo/04-sinan-exploracao-pr-2023-2024.md
# Uso: python -I explorar_sinan_pr.py <pasta com VIOLBR23.dbf e VIOLBR24.dbf>
# Requer pandas e dbfread; DBC->DBF convertido antes com pyreaddbc.dbc2dbf.
import sys, pandas as pd
from dbfread import DBF
R = sys.argv[1]
def load(y):
    df = pd.DataFrame(iter(DBF(f"{R}/VIOLBR{y}.dbf", encoding="latin-1", char_decode_errors="replace")))
    df = df[(df.SG_UF_NOT.astype(str)=="41") | (df.SG_UF.astype(str)=="41") | (df.SG_UF_OCOR.astype(str)=="41")].copy()
    df["ANO_ARQ"] = "20"+y
    return df
df = pd.concat([load("23"), load("24")])
for c in df.columns:
    if df[c].dtype==object: df[c]=df[c].fillna("").astype(str).str.strip()
def vc(s): return s.value_counts(dropna=False).to_dict()
P = lambda *a: print(*a)
P("== universo por recorte UF ==")
for y,g in df.groupby("ANO_ARQ"):
    P(y, "notif_PR", (g.SG_UF_NOT=="41").sum(), "resid_PR", (g.SG_UF=="41").sum(), "ocor_PR", (g.SG_UF_OCOR=="41").sum())
n = df[df.SG_UF_NOT=="41"]
P("NU_ANO", vc(n.NU_ANO)); P("TP_NOT", vc(n.TP_NOT)); P("ID_AGRAVO", vc(n.ID_AGRAVO))
P("CS_SEXO por ano", n.groupby("ANO_ARQ").CS_SEXO.value_counts().to_dict())
P("LES_AUTOP", n.groupby("ANO_ARQ").LES_AUTOP.value_counts().to_dict())
f = n[(n.CS_SEXO=="F")]
fi = f[f.LES_AUTOP!="1"]
P("== F nao autoprovocada por ano", fi.ANO_ARQ.value_counts().to_dict(), "F total", f.ANO_ARQ.value_counts().to_dict())
P("DT_OCOR ano", fi.DT_OCOR.str[:4].value_counts().head(8).to_dict())
P("DT_OCOR sample", fi.DT_OCOR.head(3).tolist(), fi.DT_NOTIFIC.head(3).tolist())
def fill(col): 
    s = fi[col]; return round(100*(s!="").mean(),1)
for col in ["DT_OCOR","ID_MN_OCOR","ID_MN_RESI","NU_IDADE_N","CS_RACA","CS_ESCOL_N","LOCAL_OCOR","OUT_VEZES","AUTOR_SEXO","AUTOR_ALCO","VIOL_MOTIV","CICL_VID","ORIENT_SEX","IDENT_GEN","HORA_OCOR","CS_GESTANT","SIT_CONJUG","ATEND_MULH","DELEG_MULH","MPU","ENC_DEAM","ENC_MPU","REL_CONJ","VIOL_FISIC","DT_ENCERRA","CLASSI_FIN","EVOLUCAO","NDUPLIC"]:
    s=fi[col]; P(f"FILL {col}: nonempty={fill(col)}% ignorado9={round(100*s.isin(['9','99','09']).mean(),1)}% top={s.value_counts().head(6).to_dict()}")
mo = fi.ID_MN_OCOR
P("ocor em PR", round(100*mo.str.startswith("41").mean(),1), "len", mo.str.len().value_counts().to_dict())
P("mun ocor distintos PR por ano", fi[mo.str.startswith('41')].groupby('ANO_ARQ').ID_MN_OCOR.nunique().to_dict())
P("mun notif distintos", fi.groupby('ANO_ARQ').ID_MUNICIP.nunique().to_dict())
P("ocor==resid", round(100*(fi.ID_MN_OCOR==fi.ID_MN_RESI).mean(),1), "ocor==notif", round(100*(fi.ID_MN_OCOR==fi.ID_MUNICIP).mean(),1))
c = fi[mo.str.startswith('41')].groupby(['ANO_ARQ','ID_MN_OCOR']).size()
P("celulas mun-ano <5", (c<5).sum(), "de", len(c), " <10", (c<10).sum())
P("top mun ocor", fi.ID_MN_OCOR.value_counts().head(10).to_dict())
age = fi.NU_IDADE_N.astype(int)  # 4xxx = anos; <4000 = horas/dias/meses (menor de 1 ano)
yrs = (age-4000).where(age>=4000, 0)
P("faixas etarias", pd.cut(yrs,[-1,9,17,29,59,200]).value_counts().sort_index().to_dict())
for col in ["VIOL_FISIC","VIOL_PSICO","VIOL_SEXU","VIOL_NEGLI","VIOL_FINAN","VIOL_TORT","VIOL_OUTR","REL_CONJ","REL_EXCON","REL_NAMO","REL_EXNAM","REL_PAI","REL_PAD","REL_MAE","REL_FILHO","REL_IRMAO","REL_CONHEC","REL_DESCO","REL_OUTROS","ATEND_MULH","DELEG_MULH","DELEG","MPU","DEFEN_PUBL","REDE_SAU","ASSIST_SOC","CONS_TUTEL","INFAN_JUV"]:
    s=fi[col]; P(f"SIM {col}: sim={round(100*(s=='1').mean(),1)}% nao={round(100*(s=='2').mean(),1)}% ign={round(100*(s=='9').mean(),1)}% vazio={round(100*(s=='').mean(),1)}% NA8={round(100*(s=='8').mean(),1)}")
for col in ["LOCAL_OCOR","CS_RACA","OUT_VEZES","AUTOR_SEXO","CICL_VID","VIOL_MOTIV"]:
    P("DIST", col, (fi[col].value_counts(normalize=True)*100).round(1).to_dict())
P("por ano F nao-auto: fis/psico/sex %", fi.groupby('ANO_ARQ')[['VIOL_FISIC','VIOL_PSICO','VIOL_SEXU']].agg(lambda s: round(100*(s=='1').mean(),1)).to_dict())
P("mes notif", fi.groupby('ANO_ARQ').DT_NOTIFIC.apply(lambda s: s.str[5:7].value_counts().sort_index().to_dict()).to_dict() if fi.DT_NOTIFIC.str.contains('-').any() else fi.DT_NOTIFIC.head(2).tolist())
ad = fi[(age>=4018)&(age<4130)]
P("adultas por ano", ad.ANO_ARQ.value_counts().sort_index().to_dict(), "idade cod<4000", (age<4000).sum())
P("menores 0-17", ((age<4018)).sum())
y = lambda c: round(100*(ad[c]=='1').mean(),1)
P({c:y(c) for c in ["VIOL_FISIC","VIOL_PSICO","VIOL_SEXU","VIOL_FINAN","REL_CONJ","REL_EXCON","REL_NAMO","REL_EXNAM","DELEG_MULH","DELEG","ATEND_MULH","MPU","DEFEN_PUBL","OUT_VEZES","AG_FORCA","AG_CORTE","AG_FOGO","AG_AMEACA"]})
P("parceiro/ex qualquer", round(100*ad[["REL_CONJ","REL_EXCON","REL_NAMO","REL_EXNAM"]].eq('1').any(axis=1).mean(),1))
P("local residencia", round(100*(ad.LOCAL_OCOR=='01').mean(),1), "sexismo", round(100*(ad.VIOL_MOTIV=='01').mean(),1), "motiv ign/88", round(100*ad.VIOL_MOTIV.isin(['99','88']).mean(),1))
P("autor masc", round(100*(ad.AUTOR_SEXO=='1').mean(),1))
P("raca", (ad.CS_RACA.value_counts(normalize=True)*100).round(1).to_dict())
c = ad[ad.ID_MN_OCOR.str.startswith('41')].groupby(['ANO_ARQ','ID_MN_OCOR']).size()
P("adultas mun-ano celulas", len(c), "<5", (c<5).sum(), "<10",(c<10).sum())
top = ad.ID_MN_OCOR.value_counts(); P("top5 share", round(100*top.head(5).sum()/top.sum(),1), "curitiba share", round(100*top.get('410690',0)/top.sum(),1))
P("auto-F por ano", f[f.LES_AUTOP=='1'].ANO_ARQ.value_counts().sort_index().to_dict(), "LES_AUTOP 9/vazio F", f[f.LES_AUTOP.isin(['9',''])].shape[0])
