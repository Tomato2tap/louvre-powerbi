# -*- coding: utf-8 -*-
"""
Board PHARE 'LoBP_Flagship' — style banque d'investissement clair, MULTI-PAGES :
  • Synthèse Exécutive (sidebar navy + KPI + donuts + tendance + barre + table)
  • Dictionnaire des indicateurs (table filtrable par catégorie)
  • Mode d'emploi (mini-tuto Power BI)
Navigation par boutons (pageNavigator). Réutilise le dataset LoBP_CustomerIntent.Dataset.
Validé contre les schémas officiels (_schemas).
"""
import json, os, uuid, sys, shutil

ROOT    = r"E:\louvre\powerbi"
NAME    = "LoBP_Flagship"
DATASET = "LoBP_CustomerIntent.Dataset"
RPT_DIR = os.path.join(ROOT, NAME + ".Report")
DEF_DIR = os.path.join(RPT_DIR, "definition")
RES_DIR = os.path.join(RPT_DIR, "StaticResources", "RegisteredResources")
PAGES_DIR = os.path.join(DEF_DIR, "pages")
SCHEMAS = os.path.join(ROOT, "..", "_schemas")
MEAS = "_M_Dashboard"
SV = {"report":"3.2.0","page":"2.1.0","pagesMetadata":"1.0.0","versionMetadata":"1.0.0",
      "visualContainer":"2.7.0","pbirProps":"2.0.0"}
def surl(kind,ver,base="report/definition"):
    return f"https://developer.microsoft.com/json-schemas/fabric/item/{base}/{kind}/{ver}/schema.json"
THEME_NAME="LoBP Clair"; THEME_FILE="LoBPClair.json"
def w(path,obj):
    os.makedirs(os.path.dirname(path),exist_ok=True)
    open(path,"w",encoding="utf-8").write(obj if isinstance(obj,str) else json.dumps(obj,ensure_ascii=False,indent=2))

# palette claire premium
PAGEBG="#EFF2F7"; SIDEBAR="#0B2545"; SIDE2="#163A5F"; CARD="#FFFFFF"
TXT="#102A43"; TXT2="#627D98"; LINE="#E4E9F0"; GOLD="#C8A951"; GOLDL="#E3C97A"
NAVY="#0B2545"; GREEN="#2E8B6F"; RED="#C0563B"
DATA_COLORS=["#0B2545","#2A9D8F","#C8A951","#1B4D72","#5B7DB1","#7FB6A8",
             "#E0B651","#3E7C8A","#9FB3C8","#B68A2E","#52708F","#86A0BF"]
def theme_json():
    return {"name":THEME_NAME,"dataColors":DATA_COLORS,"background":CARD,"foreground":TXT,
        "foregroundNeutralSecondary":TXT2,"tableAccent":GOLD,"good":GREEN,"neutral":GOLD,"bad":RED,
        "maximum":"#0B2545","center":"#7FB6A8","minimum":"#EAF0F7",
        "textClasses":{"title":{"color":TXT,"fontFace":"Segoe UI Semibold","fontSize":12},
            "label":{"color":TXT,"fontFace":"Segoe UI"},"callout":{"color":TXT,"fontFace":"Segoe UI Semibold"}}}

def L(v): return {"expr":{"Literal":{"Value":v}}}
def B(b): return L("true" if b else "false")
def N(n): return L(f"{n}D")
def S(t): return L("'"+str(t).replace("'","''")+"'")
def solid(c): return {"solid":{"color":L("'%s'"%c)}}
def prop(d): return [{"properties":d}]
def fld_m(p): return {"Measure":{"Expression":{"SourceRef":{"Entity":MEAS}},"Property":p}}
def fld_c(e,p): return {"Column":{"Expression":{"SourceRef":{"Entity":e}},"Property":p}}
def proj_m(p,disp=None):
    x={"field":fld_m(p),"queryRef":f"{MEAS}.{p}","nativeQueryRef":p}
    if disp:x["displayName"]=disp
    return x
def proj_c(e,p,disp=None):
    x={"field":fld_c(e,p),"queryRef":f"{e}.{p}","nativeQueryRef":p}
    if disp:x["displayName"]=disp
    return x

PAGES=[]; CUR=None
def page(pid,disp):
    global CUR
    CUR={"name":pid,"display":disp,"visuals":[]}; PAGES.append(CUR); return CUR
def vis(name,vtype,x,y,ww,hh,qstate=None,objects=None,vco=None,z=0,sync=None):
    v={"$schema":surl("visualContainer",SV["visualContainer"]),"name":name,
       "position":{"x":x,"y":y,"z":z,"width":ww,"height":hh,"tabOrder":z},
       "visual":{"visualType":vtype,"drillFilterOtherVisuals":True}}
    if qstate is not None: v["visual"]["query"]={"queryState":qstate}
    if objects: v["visual"]["objects"]=objects
    if vco: v["visual"]["visualContainerObjects"]=vco
    if sync: v["visual"]["syncGroup"]={"groupName":sync,"fieldChanges":True,"filterChanges":True}
    CUR["visuals"].append(v); return v

def box(title=None,bg=CARD,tcolor=TXT,talign="left",radius=14,shadow=True,border=True):
    vco={"background":prop({"show":B(True),"color":solid(bg),"transparency":N(0)}),
         "visualHeader":prop({"show":B(False)}),
         "border":prop({"show":B(border),"color":solid(LINE),"radius":N(radius)})}
    if shadow: vco["dropShadow"]=prop({"show":B(True),"color":solid("#9FB0C8"),"preset":S("BottomRight"),
                                       "shadowBlur":N(16),"transparency":N(78)})
    if title is not None:
        vco["title"]=prop({"show":B(True),"text":S(title),"fontColor":solid(tcolor),"fontSize":N(11),
                           "bold":B(True),"alignment":S(talign),"fontFamily":S("Segoe UI Semibold")})
    return vco

def kpi(name,x,y,ww,hh,mname,label,z):
    vco={"background":prop({"show":B(True),"color":solid(CARD),"transparency":N(0)}),
         "border":prop({"show":B(True),"color":solid(LINE),"radius":N(14)}),
         "visualHeader":prop({"show":B(False)}),
         "dropShadow":prop({"show":B(True),"color":solid("#9FB0C8"),"preset":S("BottomRight"),
                            "shadowBlur":N(16),"transparency":N(76)}),
         "title":prop({"show":B(True),"text":S(label),"fontColor":solid(TXT2),"fontSize":N(10),
                       "bold":B(True),"alignment":S("left"),"fontFamily":S("Segoe UI Semibold")})}
    objs={"labels":prop({"color":solid(NAVY),"fontSize":N(26),"bold":B(True),
                         "labelDisplayUnits":N(0),"fontFamily":S("Segoe UI Semibold")}),
          "categoryLabels":prop({"show":B(False)})}
    vis(name,"card",x,y,ww,hh,{"Values":{"projections":[proj_m(mname,label)]}},objects=objs,vco=vco,z=z)

def slicer(name,x,y,ww,hh,entity,col,label,sync=None,z=0):
    objs={"data":prop({"mode":S("Dropdown")}),
          "header":prop({"show":B(True),"text":S(label),"fontColor":solid("#FFFFFF"),
                         "fontSize":N(9),"bold":B(True),"fontFamily":S("Segoe UI Semibold")}),
          "items":prop({"fontColor":solid("#DCE6F2"),"background":solid(SIDE2),"fontSize":N(9)})}
    vco={"background":prop({"show":B(True),"color":solid(SIDE2),"transparency":N(0)}),
         "border":prop({"show":B(True),"color":solid("#21507F"),"radius":N(8)}),
         "visualHeader":prop({"show":B(False)})}
    vis(name,"slicer",x,y,ww,hh,{"Values":{"projections":[proj_c(entity,col,label)]}},
        objects=objs,vco=vco,z=z,sync=sync)

def textcard(name,x,y,ww,hh,mname,label,color,size,z,bold=True,align="left",show_val=False,val_color=GOLD,vsize=10):
    vco={"background":prop({"show":B(False)}),"border":prop({"show":B(False)}),
         "visualHeader":prop({"show":B(False)}),
         "title":prop({"show":B(True),"text":S(label),"fontColor":solid(color),"fontSize":N(size),
                       "bold":B(bold),"alignment":S(align),"fontFamily":S("Segoe UI Semibold")})}
    objs={"labels":prop({"show":B(show_val),"color":solid(val_color),"fontSize":N(vsize),
                         "labelDisplayUnits":N(0),"fontFamily":S("Segoe UI")}),
          "categoryLabels":prop({"show":B(False)})}
    vis(name,"card",x,y,ww,hh,{"Values":{"projections":[proj_m(mname,"")]}},objects=objs,vco=vco,z=z)

def donut(name,x,y,ww,hh,title,dim_e,dim_c,mname,z):
    objs={"legend":prop({"show":B(True),"position":S("Right"),"fontSize":N(9),"labelColor":solid(TXT2),"showTitle":B(False)}),
          "labels":prop({"show":B(True),"labelStyle":S("Percent of total"),"fontSize":N(9),"color":solid(TXT)}),
          "slices":prop({"innerRadiusRatio":N(55)})}
    vis(name,"donutChart",x,y,ww,hh,
        {"Category":{"projections":[proj_c(dim_e,dim_c,"Cat")]},"Y":{"projections":[proj_m(mname,"Val")]}},
        objects=objs,vco=box(title=title),z=z)

def hbar(name,x,y,ww,hh,title,dim_e,dim_c,mname,z):
    objs={"legend":prop({"show":B(False)}),
          "categoryAxis":prop({"show":B(True),"fontSize":N(9),"labelColor":solid(TXT),"titleShow":B(False),"gridlineShow":B(False)}),
          "valueAxis":prop({"show":B(False)}),
          "labels":prop({"show":B(True),"color":solid(TXT),"fontSize":N(9),"bold":B(True),"labelDisplayUnits":N(0)})}
    vis(name,"clusteredBarChart",x,y,ww,hh,
        {"Category":{"projections":[proj_c(dim_e,dim_c,"Cat")]},"Y":{"projections":[proj_m(mname,"Val")]}},
        objects=objs,vco=box(title=title),z=z)

def area(name,x,y,ww,hh,title,dim_e,dim_c,mname,z):
    objs={"legend":prop({"show":B(False)}),
          "categoryAxis":prop({"show":B(True),"fontSize":N(9),"labelColor":solid(TXT2),"titleShow":B(False),"gridlineShow":B(False)}),
          "valueAxis":prop({"show":B(True),"fontSize":N(9),"labelColor":solid(TXT2),"titleShow":B(False),
                            "gridlineShow":B(True),"gridlineColor":solid(LINE),"gridlineStyle":S("dotted")})}
    vis(name,"areaChart",x,y,ww,hh,
        {"Category":{"projections":[proj_c(dim_e,dim_c,"Date")]},"Y":{"projections":[proj_m(mname,"Val")]}},
        objects=objs,vco=box(title=title),z=z)

def table(name,x,y,ww,hh,title,cols,z):
    objs={"columnHeaders":prop({"fontColor":solid("#FFFFFF"),"backColor":solid(NAVY),"bold":B(True),
                                "fontSize":N(10),"alignment":S("Left"),"fontFamily":S("Segoe UI Semibold")}),
          "values":prop({"fontColor":solid(TXT),"backColor":solid(CARD),"backColorSecondary":solid("#F4F7FB"),
                         "fontSize":N(10),"fontFamily":S("Segoe UI"),"wordWrap":B(True)}),
          "grid":prop({"gridVertical":B(False),"gridHorizontal":B(True),"gridHorizontalColor":solid(LINE),
                       "rowPadding":N(5),"outlineColor":solid(LINE)})}
    vis(name,"tableEx",x,y,ww,hh,{"Values":{"projections":cols}},objects=objs,vco=box(title=title),z=z)

def topnav(x,y,ww,hh):
    objs={"shape":prop({"roundedCornerRadius":N(8)}),
          "fill":prop({"show":B(True),"fillColorSelected":solid(NAVY),"fillColorUnselected":solid(CARD),"transparency":N(0)}),
          "text":prop({"fontColor":solid(NAVY),"fontColorSelected":solid("#FFFFFF"),"fontSize":N(10),"bold":B(True),"fontFamily":S("Segoe UI Semibold")}),
          "outline":prop({"show":B(True),"lineColor":solid(LINE),"weight":N(1)})}
    vis("nav","pageNavigator",x,y,ww,hh,qstate=None,objects=objs,z=2)

SW=232; MX=252; MW=1264-MX
def sidebar(filters=False, cat=False):
    vis("panel","card",0,0,SW,720,{"Values":{"projections":[proj_m("Date Fonctionnelle","")]}},
        objects={"labels":prop({"show":B(False)}),"categoryLabels":prop({"show":B(False)})},
        vco={"background":prop({"show":B(True),"color":solid(SIDEBAR),"transparency":N(0)}),
             "border":prop({"show":B(False)}),"visualHeader":prop({"show":B(False)})},z=0)
    textcard("brand", 18,26,196,34,"AUM Total","LOUVRE","#FFFFFF",20,z=5)
    textcard("brand2",18,62,196,22,"AUM Total","BANQUE PRIVÉE","#C8A951",11,z=5)
    textcard("datec", 18,90,196,20,"Date Fonctionnelle","",GOLDL,8,z=5,show_val=True,val_color=GOLDL,vsize=9)
    if filters:
        textcard("flt",18,134,196,18,"AUM Total","PANNEAU DE FILTRES","#8FB0CF",9,z=5)
        sl=[("slType","CLIENT","lib_cd_typ","Type de client","g_type"),
            ("slAgc","CLIENT","agc_topz","Agence","g_agence"),
            ("slPays","CLIENT","lib_pay_res","Pays",None),
            ("slGr","CLIENT","lib_gr","Groupe de risque",None),
            ("slRisk","CLIENT","lib_cd_risque_pers","Niveau de risque",None)]
        yy=158
        for i,(n,e,c,lab,sy) in enumerate(sl):
            slicer(n,18,yy,196,64,e,c,lab,sync=sy,z=6+i); yy+=72
    if cat:
        textcard("flt",18,134,196,18,"AUM Total","FILTRER PAR CATÉGORIE","#8FB0CF",9,z=5)
        slicer("slCat",18,158,196,300,"Dictionnaire","Catégorie","Catégorie",z=6)
    textcard("sign",18,676,196,30,"AUM Total","Synthèse Exécutive — Direction","#6E8BAA",9,z=5)

# ───────── PAGE 1 : Synthèse ─────────
page("Synthese","Synthèse")
sidebar(filters=True)
topnav(MX,14,MW,34)
kpis=[("kA","AUM Total","AUM TOTAL (€)"),("kB","Nb Clients Totaux","CLIENTS"),
      ("kC","Encours Épargne","ENCOURS ÉPARGNE"),("kD","Encours Crédit Total","ENCOURS CRÉDIT")]
kw=(MW-3*16)//4
for i,(n,m,l) in enumerate(kpis): kpi(n,MX+i*(kw+16),60,kw,88,m,l,z=10+i)
donut("dPays",MX,158,300,242,"Clients par pays","CLIENT","lib_pay_res","Nb Clients Totaux",z=20)
donut("dRisk",MX+316,158,300,242,"Risque client","CLIENT","lib_cd_risque_pers","Nb Clients Totaux",z=21)
area("trend",MX+632,158,MW-632,242,"Volume des transactions / mois","TRANSACTION","dt_realisation","Volume Transactions",z=22)
hbar("barAgc",MX,410,360,298,"AUM par agence","CLIENT","agc_topz","AUM Total",z=30)
table("tbl",MX+376,410,MW-376,298,"Détail clients",
      [proj_c("CLIENT","nom_cplt","Client"),proj_c("CLIENT","lib_cd_typ","Type"),
       proj_c("CLIENT","lib_pay_res","Pays"),proj_c("CLIENT","lib_cd_risque_pers","Risque"),
       proj_m("AUM Total","AUM"),proj_m("Encours Épargne","Épargne"),proj_m("Encours Crédit Total","Crédit")],z=31)

# ───────── PAGE 2 : Dictionnaire ─────────
page("Dictionnaire","Dictionnaire")
sidebar(cat=True)
topnav(MX,14,MW,34)
textcard("dicoTitle",MX,58,MW,28,"AUM Total","Dictionnaire des indicateurs","#0B2545",16,z=9)
table("dicoTbl",MX,92,MW,612,"Indicateurs & définitions",
      [proj_c("Dictionnaire","Catégorie","Catégorie"),proj_c("Dictionnaire","Terme","Terme"),
       proj_c("Dictionnaire","Définition","Définition")],z=10)

# ───────── PAGE 3 : Mode d'emploi ─────────
page("ModeEmploi","Mode d'emploi")
sidebar()
topnav(MX,14,MW,34)
textcard("tutoTitle",MX,58,MW,28,"AUM Total","Mode d'emploi — comment lire ce tableau de bord","#0B2545",16,z=9)
table("tutoTbl",MX,92,MW,612,"Prise en main en 8 étapes",
      [proj_c("Tutoriel","Étape","Étape"),proj_c("Tutoriel","Action","Action"),
       proj_c("Tutoriel","Détail","Détail")],z=10)

# ════════════ ÉCRITURE ═══════════════════════════════════════════════════════
if os.path.isdir(DEF_DIR): shutil.rmtree(DEF_DIR)
w(os.path.join(RPT_DIR,".platform"),{
  "$schema":"https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
  "metadata":{"type":"Report","displayName":NAME},"config":{"version":"2.0","logicalId":str(uuid.uuid4())}})
w(os.path.join(RPT_DIR,"definition.pbir"),{
  "$schema":surl("definitionProperties",SV["pbirProps"],base="report"),
  "version":"4.0","datasetReference":{"byPath":{"path":f"../{DATASET}"}}})
w(os.path.join(ROOT,NAME+".pbip"),{
  "version":"1.0","artifacts":[{"report":{"path":NAME+".Report"}}],"settings":{"enableAutoRecovery":True}})
w(os.path.join(RES_DIR,THEME_FILE),theme_json())
w(os.path.join(DEF_DIR,"version.json"),{"$schema":surl("versionMetadata",SV["versionMetadata"]),"version":"2.0.0"})
rv={"visual":SV["visualContainer"],"page":SV["page"],"report":SV["report"]}
w(os.path.join(DEF_DIR,"report.json"),{
  "$schema":surl("report",SV["report"]),
  "themeCollection":{"baseTheme":{"name":"CY24SU06","reportVersionAtImport":rv,"type":"SharedResources"},
    "customTheme":{"name":THEME_NAME,"reportVersionAtImport":rv,"type":"RegisteredResources"}},
  "resourcePackages":[{"name":"RegisteredResources","type":"RegisteredResources",
    "items":[{"name":THEME_NAME,"path":THEME_FILE,"type":"CustomTheme"}]}]})
w(os.path.join(PAGES_DIR,"pages.json"),{"$schema":surl("pagesMetadata",SV["pagesMetadata"]),
  "pageOrder":[p["name"] for p in PAGES],"activePageName":PAGES[0]["name"]})
for pg in PAGES:
    pdir=os.path.join(PAGES_DIR,pg["name"])
    w(os.path.join(pdir,"page.json"),{
      "$schema":surl("page",SV["page"]),"name":pg["name"],"displayName":pg["display"],
      "displayOption":"FitToPage","height":720,"width":1280,
      "objects":{"background":prop({"color":solid(PAGEBG),"transparency":N(0)}),
                 "outspace":prop({"color":solid(PAGEBG),"transparency":N(0)})}})
    for v in pg["visuals"]:
        w(os.path.join(pdir,"visuals",v["name"],"visual.json"),v)
print("FLAGSHIP :",len(PAGES),"pages,",sum(len(p['visuals']) for p in PAGES),"visuels")

# ════════════ VALIDATION ═════════════════════════════════════════════════════
try:
    from referencing import Registry,Resource
    from referencing.jsonschema import DRAFT7
    import jsonschema
    from urllib.parse import urljoin
except Exception as e:
    print("jsonschema indisponible:",e); sys.exit(0)
def fix(node,base):
    if isinstance(node,dict):
        for k,val in list(node.items()):
            if k=="$ref" and isinstance(val,str) and not val.startswith("#") and not val.startswith("http"):
                node[k]=urljoin(base,val)
            else: fix(val,base)
    elif isinstance(node,list):
        for it in node: fix(it,base)
res=[]
for dp,_,fs in os.walk(SCHEMAS):
    for fn in fs:
        if not fn.endswith(".json"): continue
        fp=os.path.join(dp,fn)
        try: doc=json.load(open(fp,encoding="utf-8"))
        except Exception: continue
        rel=os.path.relpath(fp,SCHEMAS).replace("\\","/")
        pu="https://developer.microsoft.com/json-schemas/"+rel
        base=doc.get("$id") or pu; fix(doc,base)
        r=Resource.from_contents(doc,default_specification=DRAFT7)
        for u in {pu,base}: res.append((u,r))
reg=Registry().with_resources(res)
def val(path):
    doc=json.load(open(path,encoding="utf-8")); sid=doc.get("$schema")
    if not sid: return None
    v=jsonschema.Draft7Validator({"$ref":sid},registry=reg)
    e=sorted(v.iter_errors(doc),key=lambda e:list(e.path))
    return "\n".join(f"   [{'/'.join(map(str,x.path))}] {x.message}" for x in e[:6]) if e else None
tg=[os.path.join(DEF_DIR,"version.json"),os.path.join(DEF_DIR,"report.json"),
    os.path.join(PAGES_DIR,"pages.json"),os.path.join(RPT_DIR,"definition.pbir")]
for pg in PAGES:
    pd=os.path.join(PAGES_DIR,pg["name"]); tg.append(os.path.join(pd,"page.json"))
    tg+=[os.path.join(pd,"visuals",v["name"],"visual.json") for v in pg["visuals"]]
n=0
for t in tg:
    r=val(t)
    if r: n+=1; print("X",os.path.relpath(t,RPT_DIR),"\n",r)
print(("%d erreur(s)"%n) if n else "TOUT VALIDE ("+str(len(tg))+" fichiers)")
