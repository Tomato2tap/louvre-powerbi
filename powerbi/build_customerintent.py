# -*- coding: utf-8 -*-
"""
Génère le projet Power BI (PBIP) `LoBP_CustomerIntent` — MULTI-VERSIONS.
  - Dataset (TMSL model.bim) typé depuis les CSV
  - Rapport PBIR enhanced : 5 pages/boards métiers, thème premium
Valide chaque JSON contre les schémas officiels (_schemas).
"""
import json, os, uuid, csv, sys, shutil

ROOT      = r"E:\louvre\powerbi"
DATA      = os.path.join(ROOT, "data")
NAME      = "LoBP_CustomerIntent"
DS_DIR    = os.path.join(ROOT, NAME + ".Dataset")
RPT_DIR   = os.path.join(ROOT, NAME + ".Report")
DEF_DIR   = os.path.join(RPT_DIR, "definition")
RES_DIR   = os.path.join(RPT_DIR, "StaticResources", "RegisteredResources")
PAGES_DIR = os.path.join(DEF_DIR, "pages")
SCHEMAS   = os.path.join(ROOT, "..", "_schemas")

SV = {"report":"3.2.0","page":"2.1.0","pagesMetadata":"1.0.0","versionMetadata":"1.0.0",
      "visualContainer":"2.7.0","pbirProps":"2.0.0"}
def surl(kind, ver, base="report/definition"):
    return f"https://developer.microsoft.com/json-schemas/fabric/item/{base}/{kind}/{ver}/schema.json"

MEAS = "_M_Dashboard"
THEME_NAME = "LoBP Premium"; THEME_FILE = "LoBPPremium.json"

def w(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False, indent=2))
def headers(t):
    with open(os.path.join(DATA, t + ".csv"), encoding="utf-8-sig", newline="") as f:
        return next(csv.reader(f))

# ═════ 1) MODEL ══════════════════════════════════════════════════════════════
WANT = {
 "CLIENT": [("id_cli","text"),("cli_c_p","text"),("nom_cplt","text"),("lib_cd_typ","text"),
   ("lib_gr","text"),("agc_topz","text"),("lib_ptf","text"),("nom_cons","text"),
   ("pay_res","text"),("lib_pay_res","text"),("couleur_pays","text"),
   ("lib_cd_risque_pers","text"),("cd_risque_pers","text"),("etat_acc","text"),
   ("top_client_actif","text"),("typ_enrol","text"),("gelule_global","int"),
   ("nb_dev_enrol","int"),("age_cli","int"),
   ("dt_enrol","date"),("dt_der_cnx","date"),("dt_fonc","date"),
   ("aum_tit","number"),("aum_cot","number"),("mnt_pat_epargne","number"),("mnt_rev_princ","number")],
 "TRANSACTION": [("id_cli","text"),("num_cnt","text"),("perimetre","text"),
   ("typ_evt_lv1","text"),("lib_evt_lv1","text"),("sens","text"),("mnt_evt","number"),
   ("devise_compte","text"),("mode_paiement","text"),("canal_ordre","text"),
   ("ctrpty_pays","text"),("ctrpty_couleur_pays","text"),("ind_3ds","int"),
   ("Transaction_Sensible","int"),("dt_realisation","date")],
 "EPARGNE": [("id_cli","text"),("num_cnt","text"),("perimetre","text"),("fam_pdt","text"),
   ("lib_fds","text"),("isin_fds","text"),("lib_mod_gest","text"),
   ("enc_cnt_m","number"),("enc_cnt_n1","number"),("col_brute","number"),
   ("decollecte","number"),("col_nette","number"),("enc_fds_m","number")],
 "CREDIT": [("id_cli","text"),("num_cnt","text"),("perimetre","text"),
   ("Lib_Marche_Simple","text"),("lib_typ_prt","text"),("enc_cpt","number"),
   ("mnt_nom","number"),("mnt_krd_sain","number"),("mnt_krd_imp","number")],
 "GARANTIE": [("id_cli","text"),("num_cnt","text"),("det_typ_gar","text"),
   ("mnt_gar","number"),("mnt_gar_cpta","number")],
 "SERVICE": [("id_cli","text"),("num_cnt","text"),("fam_pdt","text"),("mnt_tar_brt","number")],
 "GSM": [("isin_fds","text"),("Classification_SFDR","text"),("enc_fds_m","number"),("performance_cli","number")],
}
TYPEMAP={"text":"string","number":"double","int":"int64","date":"dateTime","bool":"boolean"}
SUMMAP ={"text":"none","number":"sum","int":"sum","date":"none","bool":"none"}
MTYPE  ={"text":"type text","number":"type number","int":"Int64.Type","date":"type date","bool":"type logical"}

def m_expr(table, cols):
    path=os.path.join(DATA,table+".csv").replace("\\","\\\\")
    tr=", ".join('{"%s", %s}'%(c,MTYPE[t]) for c,t in cols)
    return ["let",
        f'    Source = Csv.Document(File.Contents("{path}"),[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),',
        '    #"Promoted" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
        f'    #"Typed" = Table.TransformColumnTypes(#"Promoted", {{{tr}}}, "en-US")',
        "in",'    #"Typed"']
def column(n,t):
    return {"name":n,"dataType":TYPEMAP[t],"sourceColumn":n,"summarizeBy":SUMMAP[t],
            "lineageTag":str(uuid.uuid4()),"annotations":[{"name":"SummarizationSetBy","value":"Automatic"}]}
def data_table(name):
    cols=WANT[name]; have=set(headers(name))
    for c,_ in cols:
        if c not in have: sys.exit(f"COLONNE MANQUANTE {name}.{c}")
    return {"name":name,"lineageTag":str(uuid.uuid4()),"columns":[column(c,t) for c,t in cols],
            "partitions":[{"name":name,"mode":"import","source":{"type":"m","expression":m_expr(name,cols)}}]}
def measure(n,e,f=None):
    m={"name":n,"expression":e,"lineageTag":str(uuid.uuid4())}
    if f: m["formatString"]=f
    return m
MEASURES=[
 measure("Nb Clients Totaux",'CALCULATE(DISTINCTCOUNT(CLIENT[id_cli]), CLIENT[cli_c_p] IN {"CL","CT"})',"#,0"),
 measure("Nb Clients Actifs",'CALCULATE(DISTINCTCOUNT(CLIENT[id_cli]), CLIENT[top_client_actif]="O")',"#,0"),
 measure("Nb Prospects",'CALCULATE(DISTINCTCOUNT(CLIENT[id_cli]), CLIENT[cli_c_p]="PR")',"#,0"),
 measure("Nb Clients Enrollés","CALCULATE(DISTINCTCOUNT(CLIENT[id_cli]), CLIENT[nb_dev_enrol]>0)","#,0"),
 measure("Taux Enrollment","DIVIDE([Nb Clients Enrollés],[Nb Clients Totaux],0)","0.0%"),
 measure("Taux Clients Actifs","DIVIDE([Nb Clients Actifs],[Nb Clients Totaux],0)","0.0%"),
 measure("Nb Smartphones","SUM(CLIENT[nb_dev_enrol])","#,0"),
 measure("Nb Comptes Bloqués",'CALCULATE(DISTINCTCOUNT(CLIENT[id_cli]), CLIENT[etat_acc]="B")',"#,0"),
 measure("Nb Comptes Suspendus",'CALCULATE(DISTINCTCOUNT(CLIENT[id_cli]), CLIENT[etat_acc]="S")',"#,0"),
 measure("Nb Agences","DISTINCTCOUNT(CLIENT[agc_topz])","#,0"),
 measure("Nb Pays","DISTINCTCOUNT(CLIENT[pay_res])","#,0"),
 measure("AUM Total","SUM(CLIENT[aum_tit])","#,0 €"),
 measure("AUM Moyen","DIVIDE([AUM Total],[Nb Clients Totaux],0)","#,0 €"),
 measure("Encours Épargne",'CALCULATE(SUM(EPARGNE[enc_cnt_m]), EPARGNE[perimetre]="epargne")',"#,0 €"),
 measure("Encours Fonds","SUM(EPARGNE[enc_fds_m])","#,0 €"),
 measure("Encours Crédit Total","SUM(CREDIT[enc_cpt])","#,0 €"),
 measure("Capital Sain","SUM(CREDIT[mnt_krd_sain])","#,0 €"),
 measure("Capital Impayé","SUM(CREDIT[mnt_krd_imp])","#,0 €"),
 measure("Collecte Brute",'CALCULATE(SUM(EPARGNE[col_brute]), EPARGNE[perimetre]="epargne")',"#,0 €"),
 measure("Décollecte",'CALCULATE(SUM(EPARGNE[decollecte]), EPARGNE[perimetre]="epargne")',"#,0 €"),
 measure("Collecte Nette",'CALCULATE(SUM(EPARGNE[col_nette]), EPARGNE[perimetre]="epargne")',"#,0 €"),
 measure("Volume Transactions","SUM('TRANSACTION'[mnt_evt])","#,0 €"),
 measure("Nb Transactions","COUNTROWS('TRANSACTION')","#,0"),
 measure("Nb Transactions Sensibles","CALCULATE(COUNTROWS('TRANSACTION'), 'TRANSACTION'[Transaction_Sensible]=1)","#,0"),
 measure("Volume Tx Sensibles","CALCULATE(SUM('TRANSACTION'[mnt_evt]), 'TRANSACTION'[Transaction_Sensible]=1)","#,0 €"),
 measure("Clients Sensibles",'CALCULATE(DISTINCTCOUNT(CLIENT[id_cli]), CLIENT[cd_risque_pers] IN {"E","F"})',"#,0"),
 measure("Nb KYC Rouge","CALCULATE(DISTINCTCOUNT(CLIENT[id_cli]), CLIENT[gelule_global]=10)","#,0"),
 measure("Nb KYC Orange","CALCULATE(DISTINCTCOUNT(CLIENT[id_cli]), CLIENT[gelule_global]=5)","#,0"),
 measure("Taux Conformité KYC","DIVIDE(CALCULATE(DISTINCTCOUNT(CLIENT[id_cli]),CLIENT[gelule_global]=0),[Nb Clients Totaux],0)","0.0%"),
 measure("Date Fonctionnelle",'"Données arrêtées au " & FORMAT(MAX(CLIENT[dt_fonc]),"DD/MM/YYYY")'),
]
EMPTY_M=("let\n    Source = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText("
 '"i44FAA==", BinaryEncoding.Base64), Compression.Deflate)), '
 "let _t = ((type nullable text)) in type table [ Column1 = _t ])\nin\n    Source")
def measures_table():
    return {"name":MEAS,"lineageTag":str(uuid.uuid4()),"isHidden":True,
        "columns":[{"name":"Column1","dataType":"string","sourceColumn":"Column1","isHidden":True,
            "summarizeBy":"none","lineageTag":str(uuid.uuid4()),
            "annotations":[{"name":"SummarizationSetBy","value":"Automatic"}]}],
        "partitions":[{"name":MEAS,"mode":"import","source":{"type":"m","expression":EMPTY_M}}],
        "measures":MEASURES}
def rel(ft,fc,tt,tc,active=True):
    r={"name":str(uuid.uuid4()),"fromTable":ft,"fromColumn":fc,"toTable":tt,"toColumn":tc,
       "crossFilteringBehavior":"oneDirection"}
    if not active: r["isActive"]=False
    return r
def build_model():
    return {"name":"Model","compatibilityLevel":1600,"model":{
        "culture":"fr-FR","collation":"Latin1_General_100_BIN2_UTF8",
        "dataAccessOptions":{"legacyRedirects":True,"returnErrorValuesAsNull":True},
        "defaultPowerBIDataSourceVersion":"powerBI_V3","sourceQueryCulture":"en-US",
        "tables":[data_table(t) for t in ["CLIENT","TRANSACTION","EPARGNE","CREDIT","GARANTIE","SERVICE","GSM"]]+[measures_table()],
        "relationships":[rel("TRANSACTION","id_cli","CLIENT","id_cli"),rel("EPARGNE","id_cli","CLIENT","id_cli"),
            rel("CREDIT","id_cli","CLIENT","id_cli"),rel("SERVICE","id_cli","CLIENT","id_cli"),
            rel("GARANTIE","id_cli","CLIENT","id_cli",active=False),rel("GARANTIE","num_cnt","CREDIT","num_cnt")],
        "annotations":[{"name":"PBI_QueryOrder","value":json.dumps(["CLIENT","TRANSACTION","EPARGNE","CREDIT","GARANTIE","SERVICE","GSM"])}],
    }}

# ═════ 2) PALETTE / THÈME ════════════════════════════════════════════════════
# --- THÈME SOMBRE PREMIUM (teal) ---
PAGEBG="#0E1621"   # fond de page
PANEL ="#19222F"   # fond des graphes / tables
KPIBG ="#1E2A3A"   # fond des cartes KPI
TXT   ="#E6ECF3"   # texte clair
TXT2  ="#94A3B8"   # texte secondaire
LINE  ="#2A3850"   # bordures / gridlines
WHITE ="#FFFFFF"; INK=TXT; GREY=TXT2; CARD=PANEL   # alias rétro-compat
TEAL  ="#2DD4BF"; CYAN="#38BDF8"; GOLD="#E0C56E"; GOLDL="#E0C56E"
HEADBG="#11304A"   # entête table
DATA_COLORS=["#2DD4BF","#38BDF8","#5EEAD4","#22D3EE","#0EA5A4","#7DD3FC",
             "#34D399","#E0C56E","#F472B6","#A78BFA","#60A5FA","#FB923C"]
def theme_json():
    return {"name":THEME_NAME,"dataColors":DATA_COLORS,"background":PAGEBG,"foreground":TXT,
        "foregroundNeutralSecondary":TXT2,"tableAccent":TEAL,"good":"#34D399","neutral":"#E0C56E","bad":"#F87171",
        "maximum":"#2DD4BF","center":"#1F6F6A","minimum":"#16323A",
        "textClasses":{"title":{"color":TXT,"fontFace":"Segoe UI Semibold","fontSize":12},
            "header":{"color":TXT,"fontFace":"Segoe UI Semibold","fontSize":12},
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

# ═════ 3) BUILDERS DE VISUELS ════════════════════════════════════════════════
PAGES=[]   # list of dicts {name, display, visuals:[...]}
def card_box(title=None, talign="left"):
    vco={"background":prop({"show":B(True),"color":solid(CARD),"transparency":N(0)}),
         "border":prop({"show":B(True),"color":solid(LINE),"radius":N(10)}),
         "visualHeader":prop({"show":B(False)}),
         "dropShadow":prop({"show":B(True),"color":solid("#0F1C3F"),"preset":S("BottomRight"),
                            "shadowBlur":N(8),"transparency":N(82)})}
    if title is not None:
        vco["title"]=prop({"show":B(True),"text":S(title),"fontColor":solid(INK),"fontSize":N(12),
                           "bold":B(True),"alignment":S(talign),"fontFamily":S("Segoe UI Semibold")})
    return vco

def vis(page, name, vtype, x,y,ww,hh, qstate=None, objects=None, vco=None, z=0, sync=None):
    v={"$schema":surl("visualContainer",SV["visualContainer"]),"name":name,
       "position":{"x":x,"y":y,"z":z,"width":ww,"height":hh,"tabOrder":z},
       "visual":{"visualType":vtype,"drillFilterOtherVisuals":True}}
    if qstate is not None: v["visual"]["query"]={"queryState":qstate}
    if objects:v["visual"]["objects"]=objects
    if vco:v["visual"]["visualContainerObjects"]=vco
    if sync:v["visual"]["syncGroup"]={"groupName":sync,"fieldChanges":True,"filterChanges":True}
    page["visuals"].append(v)
    return v

def kpi(page, name, x,y,ww,hh, mname, label, cardbg, accent, valsize=20, z=0):
    vco={"background":prop({"show":B(True),"color":solid(KPIBG),"transparency":N(0)}),
         "border":prop({"show":B(True),"color":solid(LINE),"radius":N(12)}),
         "visualHeader":prop({"show":B(False)}),
         "dropShadow":prop({"show":B(True),"color":solid("#000000"),"preset":S("BottomRight"),
                            "shadowBlur":N(12),"transparency":N(68)}),
         "title":prop({"show":B(True),"text":S(label),"fontColor":solid(accent),"fontSize":N(9),
                       "bold":B(True),"alignment":S("left"),"fontFamily":S("Segoe UI Semibold")})}
    objs={"labels":prop({"color":solid(WHITE),"fontSize":N(valsize),"bold":B(True),
                         "labelDisplayUnits":N(0),"fontFamily":S("Segoe UI Semibold")}),
          "categoryLabels":prop({"show":B(False)})}
    vis(page,name,"card",x,y,ww,hh,{"Values":{"projections":[proj_m(mname,label)]}},objects=objs,vco=vco,z=z)

def header(page, x,y,ww,hh, title, cardbg, z=0):
    vco={"background":prop({"show":B(False)}),
         "border":prop({"show":B(False)}),
         "visualHeader":prop({"show":B(False)}),
         "title":prop({"show":B(True),"text":S(title),"fontColor":solid(WHITE),"fontSize":N(22),
                       "bold":B(True),"alignment":S("left"),"fontFamily":S("Segoe UI Light")})}
    objs={"labels":prop({"color":solid(TEAL),"fontSize":N(10),"labelDisplayUnits":N(0),"fontFamily":S("Segoe UI")}),
          "categoryLabels":prop({"show":B(False)})}
    vis(page,"header","card",x,y,ww,hh,{"Values":{"projections":[proj_m("Date Fonctionnelle","")]}},objects=objs,vco=vco,z=z)

CARTESIAN={"clusteredColumnChart","clusteredBarChart","stackedColumnChart","stackedBarChart",
           "lineChart","areaChart","stackedAreaChart","ribbonChart","waterfallChart",
           "lineClusteredColumnComboChart","lineStackedColumnComboChart","hundredPercentStackedColumnChart",
           "hundredPercentStackedBarChart","scatterChart"}
ROUND={"donutChart","pieChart","treemap","funnel"}
def chart(page, name, vtype, x,y,ww,hh, title, roles, legend="Right", z=0):
    qs={role:{"projections":(p if isinstance(p,list) else [p])} for role,p in roles.items()}
    objs={}
    if vtype in ROUND:
        objs["legend"]=prop({"show":B(vtype in("donutChart","pieChart")),"position":S(legend),
                             "fontSize":N(9),"labelColor":solid(INK)})
        objs["labels"]=prop({"show":B(True),"fontSize":N(8),"color":solid(INK)})
        if vtype=="donutChart": objs["slices"]=prop({"innerRadiusRatio":N(58)})
    elif vtype=="gauge":
        objs["dataLabels"]=prop({"show":B(True),"fontSize":N(16),"color":solid(INK),"bold":B(True)})
    elif vtype in CARTESIAN:
        objs["legend"]=prop({"show":B(("Series" in roles) or vtype.endswith("ComboChart")),
                             "position":S("Top"),"fontSize":N(9),"labelColor":solid(INK)})
        objs["categoryAxis"]=prop({"show":B(True),"fontSize":N(9),"labelColor":solid(GREY),
                                   "titleShow":B(False),"gridlineShow":B(False)})
        objs["valueAxis"]=prop({"show":B(True),"fontSize":N(9),"labelColor":solid(GREY),
                                "titleShow":B(False),"gridlineColor":solid(LINE)})
    vis(page,name,vtype,x,y,ww,hh,qs,objects=objs,vco=card_box(title=title),z=z)

def matrix(page, name, x,y,ww,hh, title, rows, columns, values, z=0):
    qs={"Rows":{"projections":rows},"Columns":{"projections":columns},"Values":{"projections":values}}
    objs={"columnHeaders":prop({"fontColor":solid(WHITE),"backColor":solid(HEADBG),"bold":B(True),
                                "fontSize":N(10),"fontFamily":S("Segoe UI Semibold")}),
          "rowHeaders":prop({"fontColor":solid(TXT),"backColor":solid(KPIBG),"bold":B(True),"fontSize":N(10)}),
          "values":prop({"fontColor":solid(TXT),"backColor":solid(PANEL),"backColorSecondary":solid("#202C3D"),
                         "fontSize":N(10),"fontFamily":S("Segoe UI")}),
          "subTotals":prop({"rowSubtotals":B(True),"columnSubtotals":B(True)}),
          "grid":prop({"gridVertical":B(True),"gridVerticalColor":solid(LINE),
                       "gridHorizontal":B(True),"gridHorizontalColor":solid(LINE),"rowPadding":N(3)})}
    vis(page,name,"pivotTable",x,y,ww,hh,qs,objects=objs,vco=card_box(title=title),z=z)

def multirow(page, name, x,y,ww,hh, title, values, z=0):
    objs={"dataLabels":prop({"color":solid(INK),"fontSize":N(18),"bold":B(True)}),
          "categoryLabels":prop({"show":B(True),"color":solid(GREY),"fontSize":N(9)}),
          "cardTitle":prop({"color":solid(INK)})}
    vis(page,name,"multiRowCard",x,y,ww,hh,{"Values":{"projections":values}},objects=objs,vco=card_box(title=title),z=z)

def table(page, name, x,y,ww,hh, title, cols, z=0):
    objs={"columnHeaders":prop({"fontColor":solid(WHITE),"backColor":solid(HEADBG),"bold":B(True),
                                "fontSize":N(10),"alignment":S("Left"),"fontFamily":S("Segoe UI Semibold")}),
          "values":prop({"fontColor":solid(TXT),"backColor":solid(PANEL),"backColorSecondary":solid("#202C3D"),
                         "fontSize":N(10),"fontFamily":S("Segoe UI")}),
          "grid":prop({"gridVertical":B(False),"gridHorizontal":B(True),"gridHorizontalColor":solid(LINE),
                       "rowPadding":N(4),"outlineColor":solid(LINE)})}
    qs={"Values":{"projections":cols}}
    vis(page,name,"tableEx",x,y,ww,hh,qs,objects=objs,vco=card_box(title=title),z=z)

def slicer(page, name, x,y,ww,hh, entity, col, label, sync=None, z=0):
    objs={"data":prop({"mode":S("Dropdown")}),
          "header":prop({"show":B(True),"text":S(label),"fontColor":solid(INK),
                         "fontSize":N(9),"bold":B(True),"fontFamily":S("Segoe UI Semibold")}),
          "items":prop({"fontColor":solid(INK),"fontSize":N(9)})}
    vco={"background":prop({"show":B(True),"color":solid(PANEL),"transparency":N(0)}),
         "border":prop({"show":B(True),"color":solid(LINE),"radius":N(8)}),
         "visualHeader":prop({"show":B(False)})}
    vis(page,name,"slicer",x,y,ww,hh,{"Values":{"projections":[proj_c(entity,col,label)]}},
        objects=objs,vco=vco,z=z,sync=sync)

def nav(page, x,y,ww,hh, z=0):
    objs={"shape":prop({"roundedCornerRadius":N(8)}),
          "fill":prop({"show":B(True),"fillColorSelected":solid(TEAL),"fillColorUnselected":solid(PANEL),
                       "transparency":N(0)}),
          "text":prop({"fontColor":solid(TXT),"fontColorSelected":solid("#0E1621"),
                       "fontSize":N(10),"bold":B(True)})}
    vis(page,"nav","pageNavigator",x,y,ww,hh,qstate=None,objects=objs,z=z)

def filterbar(page, extra):
    # 2 slicers globaux synchronisés + 2 spécifiques
    sw=300; gap=16; x0=16; y=66; h=44
    slicer(page,"slType",x0,y,sw,h,"CLIENT","lib_cd_typ","Type client",sync="g_type",z=90)
    slicer(page,"slAgc", x0+(sw+gap),y,sw,h,"CLIENT","agc_topz","Agence",sync="g_agence",z=91)
    for i,(e,c,l) in enumerate(extra[:2]):
        slicer(page,f"slX{i}",x0+(sw+gap)*(2+i),y,sw,h,e,c,l,z=92+i)

def new_page(pid, display):
    p={"name":pid,"display":display,"visuals":[]}; PAGES.append(p); return p

# ═════ 4) DÉFINITION DES 6 BOARDS ════════════════════════════════════════════
# Gabarit commun : header (à gauche) + navigateur de pages (à droite) + barre de filtres
HEAD_W=980; CY=118   # contenu sous la barre de filtres
def shell(pg, display, cardbg, extra_slicers):
    header(pg,16,12,HEAD_W,46,f"LOUVRE BANQUE PRIVÉE   |   {display}",cardbg,z=1)
    nav(pg,16+HEAD_W+12,12,1248-HEAD_W-12,46,z=2)
    filterbar(pg, extra_slicers)

# --- Board 1 : Synthèse Exécutive (colonne KPI + 2 graphes + table) ----------
NAVY="#16213E"
p=new_page("Synthese","Synthèse Exécutive")
shell(p,"Synthèse Exécutive",NAVY,[("CLIENT","lib_pay_res","Pays"),("CLIENT","lib_gr","Groupe risque")])
exec_kpis=[("Nb Clients Totaux","CLIENTS"),("AUM Total","AUM TOTAL"),("Encours Épargne","ENCOURS ÉPARGNE"),
   ("Encours Crédit Total","ENCOURS CRÉDIT"),("Collecte Nette","COLLECTE NETTE"),("Nb Clients Actifs","CLIENTS ACTIFS"),
   ("Clients Sensibles","CLIENTS SENSIBLES"),("Taux Enrollment","TAUX ENRÔLEMENT")]
ky=CY
for i,(m,l) in enumerate(exec_kpis):
    kpi(p,f"k{i}",16,ky,208,64,m,l,NAVY,GOLD if l in("AUM TOTAL","CLIENTS SENSIBLES") else TEAL,z=10+i); ky+=73
chart(p,"donutPays","donutChart",234,CY,420,276,"Clients par pays › agence (drill-down)",
      {"Category":[proj_c("CLIENT","lib_pay_res","Pays"),proj_c("CLIENT","agc_topz","Agence")],
       "Y":proj_m("Nb Clients Totaux","Clients")},z=20)
chart(p,"areaCanal","stackedAreaChart",662,CY,602,276,"Volume des transactions par opération et canal",
      {"Category":proj_c("TRANSACTION","lib_evt_lv1","Opération"),"Series":proj_c("TRANSACTION","canal_ordre","Canal"),
       "Y":proj_m("Volume Transactions","Volume")},z=21)
table(p,"tbl",234,402,1030,300,"Détail clients — patrimoine & risque",
      [proj_c("CLIENT","nom_cplt","Client"),proj_c("CLIENT","lib_cd_typ","Type"),proj_c("CLIENT","lib_pay_res","Pays"),
       proj_c("CLIENT","agc_topz","Agence"),proj_c("CLIENT","lib_cd_risque_pers","Risque"),
       proj_m("AUM Total","AUM"),proj_m("Encours Épargne","Épargne"),proj_m("Encours Crédit Total","Crédit")],z=22)

# --- Gabarit générique : 6 KPI + 3 graphes + table --------------------------
def board(pid, display, cardbg, accent, extra, kpis, charts, tbl):
    pg=new_page(pid, display)
    shell(pg, display, cardbg, extra)
    n=len(kpis); gap=10; x0=16; cw=(1248-gap*(n-1))//n
    for i,(m,l) in enumerate(kpis):
        kpi(pg,f"k{i}",x0+i*(cw+gap),CY,cw,74,m,l,cardbg,accent,valsize=18,z=10+i)
    cy=CY+86; cw3=(1248-2*12)//3; ch=246
    for i,c in enumerate(charts):
        vtype,title,roles=c[0],c[1],c[2]
        legend=c[3] if len(c)>3 else "Right"
        chart(pg,f"c{i}",vtype,16+i*(cw3+12),cy,cw3,ch,title,roles,legend=legend,z=20+i)
    table(pg,"tbl",16,cy+ch+8,1248,702-(cy+ch+8),tbl[0],tbl[1],z=40)
    return pg

# --- Board 2 : Digital & Adoption (teal / cyan)
board("Digital","Digital & Adoption","#134E4A","#5EEAD4",
  [("CLIENT","etat_acc","État accès"),("CLIENT","typ_enrol","Type enrôlement")],
  [("Nb Clients Totaux","CLIENTS"),("Nb Clients Enrollés","ENRÔLÉS"),("Nb Smartphones","SMARTPHONES"),
   ("Taux Enrollment","TAUX ENRÔL."),("Nb Comptes Bloqués","BLOQUÉS"),("Nb Comptes Suspendus","SUSPENDUS")],
  [("donutChart","Transactions par canal",
     {"Category":proj_c("TRANSACTION","canal_ordre","Canal"),"Y":proj_m("Nb Transactions","Transactions")}),
   ("areaChart","Tendance — volume des transactions par mois",
     {"Category":proj_c("TRANSACTION","dt_realisation","Date"),"Y":proj_m("Volume Transactions","Volume")}),
   ("clusteredColumnChart","Clients enrôlés par type d'enrôlement",
     {"Category":proj_c("CLIENT","typ_enrol","Type"),"Y":proj_m("Nb Clients Enrollés","Enrôlés")})],
  ("Clients à surveiller (accès & enrôlement)",
   [proj_c("CLIENT","nom_cplt","Client"),proj_c("CLIENT","etat_acc","État accès"),
    proj_c("CLIENT","typ_enrol","Type enrôl."),proj_c("CLIENT","nb_dev_enrol","Appareils"),
    proj_c("CLIENT","agc_topz","Agence"),proj_c("CLIENT","lib_cd_risque_pers","Risque")]))

# --- Board 3 : Risque & Conformité (bordeaux / ambre)
board("Risque","Risque & Conformité","#4A1D24","#E8B04B",
  [("CLIENT","lib_cd_risque_pers","Niveau de risque"),("CLIENT","couleur_pays","Couleur pays")],
  [("Clients Sensibles","CLIENTS SENSIBLES"),("Nb KYC Rouge","KYC ROUGE"),("Nb KYC Orange","KYC ORANGE"),
   ("Nb Transactions Sensibles","TX SENSIBLES"),("Volume Tx Sensibles","VOL. SENSIBLE"),("Taux Conformité KYC","CONFORMITÉ KYC")],
  [("funnel","Entonnoir du risque client",
     {"Category":proj_c("CLIENT","lib_cd_risque_pers","Risque"),"Y":proj_m("Nb Clients Totaux","Clients")}),
   ("clusteredBarChart","Volume transactions par couleur pays (contrepartie)",
     {"Category":proj_c("TRANSACTION","ctrpty_couleur_pays","Pays contrepartie"),"Y":proj_m("Volume Transactions","Volume")}),
   ("clusteredColumnChart","Volume sensible par opération",
     {"Category":proj_c("TRANSACTION","lib_evt_lv1","Opération"),"Y":proj_m("Volume Tx Sensibles","Vol. sensible")})],
  ("Clients à risque — KYC & conformité",
   [proj_c("CLIENT","nom_cplt","Client"),proj_c("CLIENT","lib_cd_risque_pers","Risque"),
    proj_c("CLIENT","couleur_pays","Pays (couleur)"),proj_c("CLIENT","gelule_global","KYC"),
    proj_c("CLIENT","agc_topz","Agence"),proj_m("AUM Total","AUM")]))

# --- Board 4 : Commercial & Relation Client (vert / or)
board("Commercial","Commercial & Relation Client","#14392B","#D9B85C",
  [("CLIENT","lib_gr","Groupe risque"),("CLIENT","top_client_actif","Actif")],
  [("Nb Clients Actifs","CLIENTS ACTIFS"),("Nb Prospects","PROSPECTS"),("AUM Total","AUM TOTAL"),
   ("AUM Moyen","AUM MOYEN"),("Taux Clients Actifs","TAUX ACTIFS"),("Nb Clients Totaux","CLIENTS")],
  [("clusteredColumnChart","Clients par type › groupe (drill-down)",
     {"Category":[proj_c("CLIENT","lib_cd_typ","Type"),proj_c("CLIENT","lib_gr","Groupe")],
      "Y":proj_m("Nb Clients Totaux","Clients")}),
   ("lineClusteredColumnComboChart","AUM (barres) & taux d'actifs (ligne) par agence",
     {"Category":proj_c("CLIENT","agc_topz","Agence"),"Y":proj_m("AUM Total","AUM"),
      "Y2":proj_m("Taux Clients Actifs","Taux actifs")}),
   ("treemap","Clients par groupe de risque",
     {"Group":proj_c("CLIENT","lib_gr","Groupe"),"Values":proj_m("Nb Clients Totaux","Clients")})],
  ("Portefeuille clients par conseiller",
   [proj_c("CLIENT","nom_cplt","Client"),proj_c("CLIENT","lib_cd_typ","Type"),
    proj_c("CLIENT","nom_cons","Conseiller"),proj_c("CLIENT","agc_topz","Agence"),
    proj_c("CLIENT","top_client_actif","Actif"),proj_m("AUM Total","AUM")]))

# --- Board 5 : Patrimoine — Épargne & Crédit (indigo / bleu)
board("Patrimoine","Patrimoine — Épargne & Crédit","#1E2A4A","#7FB0E0",
  [("EPARGNE","fam_pdt","Famille produit"),("EPARGNE","lib_mod_gest","Mode gestion")],
  [("Encours Épargne","ENCOURS ÉPARGNE"),("Collecte Brute","COLLECTE BRUTE"),("Décollecte","DÉCOLLECTE"),
   ("Collecte Nette","COLLECTE NETTE"),("Encours Crédit Total","ENCOURS CRÉDIT"),("Capital Impayé","CAPITAL IMPAYÉ")],
  [("clusteredColumnChart","Encours épargne par famille › fonds (drill-down)",
     {"Category":[proj_c("EPARGNE","fam_pdt","Famille"),proj_c("EPARGNE","lib_fds","Fonds")],
      "Y":proj_m("Encours Épargne","Encours")}),
   ("waterfallChart","Cascade de la collecte nette par famille",
     {"Category":proj_c("EPARGNE","fam_pdt","Famille"),"Y":proj_m("Collecte Nette","Collecte nette")}),
   ("clusteredBarChart","Encours crédit par marché",
     {"Category":proj_c("CREDIT","Lib_Marche_Simple","Marché"),"Y":proj_m("Encours Crédit Total","Encours")})],
  ("Fonds — encours par support",
   [proj_c("EPARGNE","lib_fds","Fonds"),proj_c("EPARGNE","fam_pdt","Famille"),
    proj_c("EPARGNE","lib_mod_gest","Gestion"),proj_m("Encours Fonds","Encours fonds")]))

# --- Board 6 : Analyse Avancée 360° (vitrine de visuels audacieux)
SLATE="#0F2A43"
p6=new_page("Analyse","Analyse Avancée 360°")
shell(p6,"Analyse Avancée 360°",SLATE,[("CLIENT","lib_pay_res","Pays"),("CLIENT","lib_cd_risque_pers","Risque")])
matrix(p6,"mx",16,CY,405,276,"Tableau croisé — AUM par type & groupe de risque",
       rows=[proj_c("CLIENT","lib_cd_typ","Type")],columns=[proj_c("CLIENT","lib_gr","Groupe")],
       values=[proj_m("AUM Total","AUM")],z=10)
chart(p6,"scatter","scatterChart",433,CY,405,276,"Clients : AUM vs Épargne (taille = Crédit)",
      {"Category":proj_c("CLIENT","nom_cplt","Client"),"X":proj_m("AUM Total","AUM"),
       "Y":proj_m("Encours Épargne","Épargne"),"Size":proj_m("Encours Crédit Total","Crédit")},z=11)
chart(p6,"gauge","gauge",850,CY,414,132,"Taux de conformité KYC",
      {"Y":proj_m("Taux Conformité KYC","Conformité")},z=12)
chart(p6,"tm","filledMap",850,CY+140,414,136,"Carte — AUM par pays",
      {"Category":proj_c("CLIENT","lib_pay_res","Pays"),"Y":proj_m("AUM Total","AUM")},z=13)
chart(p6,"wf","waterfallChart",16,404,405,298,"Cascade — collecte nette par famille",
      {"Category":proj_c("EPARGNE","fam_pdt","Famille"),"Y":proj_m("Collecte Nette","Collecte nette")},z=14)
chart(p6,"ribbon","ribbonChart",433,404,405,298,"Ruban — volume par opération & canal",
      {"Category":proj_c("TRANSACTION","lib_evt_lv1","Opération"),"Series":proj_c("TRANSACTION","canal_ordre","Canal"),
       "Y":proj_m("Volume Transactions","Volume")},z=15)
chart(p6,"funnel","funnel",850,404,414,298,"Entonnoir — clients par niveau de risque",
      {"Category":proj_c("CLIENT","lib_cd_risque_pers","Risque"),"Y":proj_m("Nb Clients Totaux","Clients")},z=16)

# ═════ 5) ÉCRITURE ═══════════════════════════════════════════════════════════
def write_all():
    # nettoyage : ancien layout + anciennes pages/visuels
    for pth in [os.path.join(RPT_DIR,"definition.pbr"),os.path.join(DS_DIR,"definition.pbidataset")]:
        if os.path.exists(pth): os.remove(pth)
    if os.path.isdir(PAGES_DIR): shutil.rmtree(PAGES_DIR)
    # supprime un éventuel dossier TMDL (incompatible avec model.bim TMSL dans le même PBIP)
    if os.path.isdir(os.path.join(DS_DIR,"definition")): shutil.rmtree(os.path.join(DS_DIR,"definition"))
    # caches Power BI obsolètes
    for c in [".pbi","cache.abf"]:
        cp=os.path.join(DS_DIR,c)
        if os.path.isdir(cp): shutil.rmtree(cp)
        elif os.path.isfile(cp): os.remove(cp)
    # Dataset
    w(os.path.join(DS_DIR,"model.bim"), build_model())
    w(os.path.join(DS_DIR,"definition.pbism"),{
      "$schema":"https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
      "version":"4.0","settings":{}})
    w(os.path.join(DS_DIR,".platform"),{
      "$schema":"https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
      "metadata":{"type":"SemanticModel","displayName":NAME},"config":{"version":"2.0","logicalId":str(uuid.uuid4())}})
    # Report shell
    w(os.path.join(RPT_DIR,"definition.pbir"),{
      "$schema":surl("definitionProperties",SV["pbirProps"],base="report"),
      "version":"4.0","datasetReference":{"byPath":{"path":f"../{NAME}.Dataset"}}})
    w(os.path.join(RPT_DIR,".platform"),{
      "$schema":"https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
      "metadata":{"type":"Report","displayName":NAME},"config":{"version":"2.0","logicalId":str(uuid.uuid4())}})
    w(os.path.join(ROOT,NAME+".pbip"),{
      "version":"1.0","artifacts":[{"report":{"path":NAME+".Report"}}],"settings":{"enableAutoRecovery":True}})
    w(os.path.join(RES_DIR,THEME_FILE), theme_json())
    # PBIR
    w(os.path.join(DEF_DIR,"version.json"),{"$schema":surl("versionMetadata",SV["versionMetadata"]),"version":"2.0.0"})
    rv={"visual":SV["visualContainer"],"page":SV["page"],"report":SV["report"]}
    w(os.path.join(DEF_DIR,"report.json"),{
      "$schema":surl("report",SV["report"]),
      "themeCollection":{"baseTheme":{"name":"CY24SU06","reportVersionAtImport":rv,"type":"SharedResources"},
        "customTheme":{"name":THEME_NAME,"reportVersionAtImport":rv,"type":"RegisteredResources"}},
      "resourcePackages":[{"name":"RegisteredResources","type":"RegisteredResources",
        "items":[{"name":THEME_NAME,"path":THEME_FILE,"type":"CustomTheme"}]}]})
    w(os.path.join(PAGES_DIR,"pages.json"),{
      "$schema":surl("pagesMetadata",SV["pagesMetadata"]),
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

write_all()
print("FICHIERS ÉCRITS :",len(PAGES),"pages,",sum(len(p['visuals']) for p in PAGES),"visuels")

# ═════ 6) VALIDATION ═════════════════════════════════════════════════════════
try:
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT7
    import jsonschema
    from urllib.parse import urljoin
except Exception as e:
    print("jsonschema indisponible:",e); sys.exit(0)
def fix_refs(node,base):
    if isinstance(node,dict):
        for k,val in list(node.items()):
            if k=="$ref" and isinstance(val,str) and not val.startswith("#") and not val.startswith("http"):
                node[k]=urljoin(base,val)
            else: fix_refs(val,base)
    elif isinstance(node,list):
        for it in node: fix_refs(it,base)
resources=[]
for dp,_,fs in os.walk(SCHEMAS):
    for fn in fs:
        if not fn.endswith(".json"): continue
        fp=os.path.join(dp,fn)
        try: doc=json.load(open(fp,encoding="utf-8"))
        except Exception: continue
        rel_=os.path.relpath(fp,SCHEMAS).replace("\\","/")
        pu="https://developer.microsoft.com/json-schemas/"+rel_
        base=doc.get("$id") or pu; fix_refs(doc,base)
        r=Resource.from_contents(doc,default_specification=DRAFT7)
        for u in {pu,base}: resources.append((u,r))
registry=Registry().with_resources(resources)
def validate(path):
    doc=json.load(open(path,encoding="utf-8")); sid=doc.get("$schema")
    if not sid: return None
    v=jsonschema.Draft7Validator({"$ref":sid},registry=registry)
    errs=sorted(v.iter_errors(doc),key=lambda e:list(e.path))
    return "\n".join(f"   [{'/'.join(map(str,e.path))}] {e.message}" for e in errs[:6]) if errs else None
targets=[os.path.join(DEF_DIR,"version.json"),os.path.join(DEF_DIR,"report.json"),
         os.path.join(PAGES_DIR,"pages.json"),os.path.join(RPT_DIR,"definition.pbir")]
for pg in PAGES:
    pdir=os.path.join(PAGES_DIR,pg["name"]); targets.append(os.path.join(pdir,"page.json"))
    for v in pg["visuals"]: targets.append(os.path.join(pdir,"visuals",v["name"],"visual.json"))
print("=== VALIDATION ===")
nerr=0
for t in targets:
    r=validate(t)
    if r: nerr+=1; print("X",os.path.relpath(t,RPT_DIR),"\n",r)
print(("%d erreur(s)"%nerr) if nerr else "TOUT VALIDE ("+str(len(targets))+" fichiers)")
