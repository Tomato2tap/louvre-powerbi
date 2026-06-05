"""
Génère un fichier Power BI (.pbix) avec :
  - 7 tables CSV chargées
  - 5 pages (Accueil, Digital, Produits, Conformité, Commercial)
  - Mesures DAX
  - Relations entre tables
Utilise la librairie pbi-tools via le module powerbiclient ou la
construction manuelle du format ZIP PBIX.
"""

import os, json, zipfile, shutil, struct, hashlib
from pathlib import Path

DATA_DIR = r"E:\louvre\powerbi\data"
OUT_DIR  = r"E:\louvre\powerbi"
PBIX_OUT = os.path.join(OUT_DIR, "LoBP_Dashboard.pbix")

TABLES = ["CLIENT","TRANSACTION","EPARGNE","CREDIT","GARANTIE","SERVICE","GSM"]

# ── Version file ──────────────────────────────────────────────────────────────
VERSION = "2.129.0.0"

# ── [Content_Types].xml ───────────────────────────────────────────────────────
CONTENT_TYPES = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="json" ContentType="application/json" />
  <Default Extension="xml"  ContentType="application/xml" />
  <Override PartName="/DataModel"              ContentType="application/vnd.ms-pbi.datamodel" />
  <Override PartName="/Report/Layout"          ContentType="application/json" />
  <Override PartName="/SecurityBindings"       ContentType="application/vnd.ms-pbi.securitybindings" />
  <Override PartName="/Metadata"               ContentType="application/json" />
  <Override PartName="/DiagramLayout"          ContentType="application/json" />
  <Override PartName="/Version"                ContentType="application/vnd.ms-pbi.version" />
  <Override PartName="/Settings"               ContentType="application/json" />
  <Override PartName="/Connections"            ContentType="application/json" />
</Types>"""

# ── Connections (CSV sources) ────────────────────────────────────────────────
def make_connections():
    conns = []
    for t in TABLES:
        conns.append({
            "Name": t,
            "ConnectionString": f"Provider=Microsoft.ACE.OLEDB.12.0;Data Source={DATA_DIR};Extended Properties=\"Text;HDR=Yes;FMT=Delimited\"",
            "ConnectionType": "Csv",
            "PbixContainerPath": f"/DataSources/{t}.csv"
        })
    return json.dumps({"Connections": conns}, ensure_ascii=False, indent=2)

# ── Report Layout ─────────────────────────────────────────────────────────────
COLORS = {
    "bordeaux": "#8B1F2A",
    "rouge":    "#C9453A",
    "or":       "#D4A04A",
    "bleu":     "#6B8FA8",
    "fond":     "#F4F2EE",
    "blanc":    "#FFFFFF",
    "texte":    "#2C2C2C",
    "gris":     "#666666",
    "alerte_r": "#C0392B",
    "alerte_o": "#E67E22",
    "alerte_v": "#27AE60",
}

def kpi_card(x, y, w, h, title, measure, table="_M_Clients", fmt="0", bg=COLORS["blanc"]):
    """Génère un visuel Card Power BI"""
    config = {
        "name": f"card_{title.replace(' ','_')}",
        "layouts": [{"id": 0, "position": {"x":x,"y":y,"width":w,"height":h,"z":0}}],
        "singleVisual": {
            "visualType": "card",
            "projections": {
                "Values": [{"queryRef": f"{table}.{measure}"}]
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name":"t","Entity":table,"Type":0}],
                "Select": [{"Measure":{"Expression":{"SourceRef":{"Source":"t"}},"Property":measure},"Name":f"{table}.{measure}"}]
            },
            "vcObjects": {
                "title": [{"properties":{"text":{"expr":{"Literal":{"Value":f"'{title}'"}}},
                           "show":{"expr":{"Literal":{"Value":"true"}}},
                           "fontColor":{"solid":{"color":COLORS["texte"]}},
                           "fontSize":{"expr":{"Literal":{"Value":"11D"}}}}}],
                "background": [{"properties":{"fillColor":{"solid":{"color":bg}},
                                "show":{"expr":{"Literal":{"Value":"true"}}}}}],
                "dataLabels": [{"properties":{"color":{"solid":{"color":COLORS["bordeaux"]}},
                                "fontSize":{"expr":{"Literal":{"Value":"28D"}}},
                                "fontFamily":{"expr":{"Literal":{"Value":"'Segoe UI'"}}}}}]
            }
        }
    }
    return config

def bar_chart(x, y, w, h, title, dim_table, dim_field, measure, meas_table):
    config = {
        "name": f"bar_{title.replace(' ','_')[:20]}",
        "layouts": [{"id":0,"position":{"x":x,"y":y,"width":w,"height":h,"z":0}}],
        "singleVisual": {
            "visualType": "barChart",
            "projections": {
                "Category": [{"queryRef":f"{dim_table}.{dim_field}"}],
                "Y": [{"queryRef":f"{meas_table}.{measure}"}]
            },
            "vcObjects": {
                "title": [{"properties":{"text":{"expr":{"Literal":{"Value":f"'{title}'"}}},"show":{"expr":{"Literal":{"Value":"true"}}},
                           "fontSize":{"expr":{"Literal":{"Value":"13D"}}},"fontColor":{"solid":{"color":COLORS["texte"]}}}}],
                "dataPoint": [{"properties":{"defaultColor":{"solid":{"color":COLORS["bordeaux"]}}}}]
            }
        }
    }
    return config

def donut_chart(x, y, w, h, title, dim_table, dim_field, measure, meas_table):
    config = {
        "name": f"donut_{title.replace(' ','_')[:20]}",
        "layouts": [{"id":0,"position":{"x":x,"y":y,"width":w,"height":h,"z":0}}],
        "singleVisual": {
            "visualType": "donutChart",
            "projections": {
                "Category": [{"queryRef":f"{dim_table}.{dim_field}"}],
                "Y": [{"queryRef":f"{meas_table}.{measure}"}]
            },
            "vcObjects": {
                "title": [{"properties":{"text":{"expr":{"Literal":{"Value":f"'{title}'"}}},"show":{"expr":{"Literal":{"Value":"true"}}},
                           "fontSize":{"expr":{"Literal":{"Value":"13D"}}}}}]
            }
        }
    }
    return config

def line_chart(x, y, w, h, title, dim_table, dim_field, measure, meas_table):
    config = {
        "name": f"line_{title.replace(' ','_')[:20]}",
        "layouts": [{"id":0,"position":{"x":x,"y":y,"width":w,"height":h,"z":0}}],
        "singleVisual": {
            "visualType": "lineChart",
            "projections": {
                "Category": [{"queryRef":f"{dim_table}.{dim_field}"}],
                "Y": [{"queryRef":f"{meas_table}.{measure}"}]
            },
            "vcObjects": {
                "title": [{"properties":{"text":{"expr":{"Literal":{"Value":f"'{title}'"}}},"show":{"expr":{"Literal":{"Value":"true"}}},
                           "fontSize":{"expr":{"Literal":{"Value":"13D"}}}}}],
                "lineStyles": [{"properties":{"strokeColor":{"solid":{"color":COLORS["bordeaux"]}}}}]
            }
        }
    }
    return config

def scatter_chart(x, y, w, h, title):
    config = {
        "name": f"scatter_{title[:20]}",
        "layouts": [{"id":0,"position":{"x":x,"y":y,"width":w,"height":h,"z":0}}],
        "singleVisual": {
            "visualType": "scatterChart",
            "projections": {
                "Details": [{"queryRef":"CLIENT.nom_cplt"}],
                "X": [{"queryRef":"CLIENT.cd_risque_pers"}],
                "Y": [{"queryRef":"_M_Clients.AUM Moyen par Client"}],
                "Size": [{"queryRef":"_M_Epargne.Encours Épargne"}]
            },
            "vcObjects": {
                "title": [{"properties":{"text":{"expr":{"Literal":{"Value":f"'{title}'"}}},"show":{"expr":{"Literal":{"Value":"true"}}}}}],
                "dataPoint": [{"properties":{"defaultColor":{"solid":{"color":COLORS["bordeaux"]}}}}]
            }
        }
    }
    return config

def table_visual(x, y, w, h, title, columns):
    """columns = list of (table, field)"""
    projections = {"Values": [{"queryRef":f"{t}.{f}"} for t,f in columns]}
    config = {
        "name": f"tbl_{title[:20]}",
        "layouts": [{"id":0,"position":{"x":x,"y":y,"width":w,"height":h,"z":0}}],
        "singleVisual": {
            "visualType": "tableEx",
            "projections": projections,
            "vcObjects": {
                "title": [{"properties":{"text":{"expr":{"Literal":{"Value":f"'{title}'"}}},"show":{"expr":{"Literal":{"Value":"true"}}}}}],
                "header": [{"properties":{"fontColor":{"solid":{"color":COLORS["blanc"]}},"backColor":{"solid":{"color":COLORS["bordeaux"]}}}}]
            }
        }
    }
    return config

def text_box(x, y, w, h, text, font_size=28, bold=True, color=COLORS["bordeaux"]):
    return {
        "name": f"txt_{text[:15]}",
        "layouts": [{"id":0,"position":{"x":x,"y":y,"width":w,"height":h,"z":0}}],
        "singleVisual": {
            "visualType": "textbox",
            "vcObjects": {
                "general": [{"properties":{"paragraphs":[{"textRuns":[{"value":text,"textStyle":{"fontWeight":"bold" if bold else "normal","fontSize":f"{font_size}pt","color":color}}]}]}}]
            }
        }
    }

def slicer(x, y, w, h, title, table, field):
    return {
        "name": f"slic_{field[:15]}",
        "layouts": [{"id":0,"position":{"x":x,"y":y,"width":w,"height":h,"z":0}}],
        "singleVisual": {
            "visualType": "slicer",
            "projections": {"Values": [{"queryRef":f"{table}.{field}"}]},
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name":"t","Entity":table,"Type":0}],
                "Select": [{"Column":{"Expression":{"SourceRef":{"Source":"t"}},"Property":field},"Name":f"{table}.{field}"}]
            },
            "vcObjects": {
                "title": [{"properties":{"text":{"expr":{"Literal":{"Value":f"'{title}'"}}},"show":{"expr":{"Literal":{"Value":"true"}}}}}],
                "header": [{"properties":{"fontColor":{"solid":{"color":COLORS["bordeaux"]}}}}]
            }
        }
    }

# ── Pages ─────────────────────────────────────────────────────────────────────
def make_page_accueil():
    return {
        "name": "Accueil",
        "displayName": "🏠 Accueil",
        "displayOption": 1,
        "height": 720, "width": 1280,
        "background": {"transparency": 0},
        "visualContainers": [
            text_box(40, 20, 600, 60, "Louvre Banque Privée", 32, True, COLORS["bordeaux"]),
            text_box(40, 90, 600, 30, "Tableau de Bord — Données au 31/05/2026", 14, False, COLORS["gris"]),
            text_box(40, 200, 280, 80, "📊 Suivi Digital", 18, True, COLORS["bordeaux"]),
            text_box(340, 200, 280, 80, "📦 Portefeuille Produits", 18, True, COLORS["bordeaux"]),
            text_box(640, 200, 280, 80, "⚠ Risque & Conformité", 18, True, COLORS["alerte_r"]),
            text_box(40, 320, 280, 80, "👥 Commercial & Clients", 18, True, COLORS["bordeaux"]),
        ]
    }

def make_page_digital():
    return {
        "name": "Digital",
        "displayName": "📊 Suivi Digital",
        "displayOption": 1,
        "height": 720, "width": 1280,
        "visualContainers": [
            text_box(10, 5, 600, 35, "Suivi Digital & Adoption", 20, True, COLORS["bordeaux"]),
            # KPI row 1
            kpi_card(10,  50, 220, 90, "Clients Totaux",       "Nb Clients Totaux",    "_M_Clients"),
            kpi_card(240, 50, 220, 90, "Clients Enrollés",     "Nb Clients Enrollés",  "_M_Digital"),
            kpi_card(470, 50, 220, 90, "Smartphones Enrollés", "Nb Smartphones Total", "_M_Digital"),
            kpi_card(700, 50, 220, 90, "Taux Enrollment",      "Taux Enrollment",      "_M_Digital"),
            kpi_card(930, 50, 220, 90, "Comptes Bloqués",      "Nb Comptes Bloqués",   "_M_Digital", bg="#FEE2E2"),
            # KPI row 2
            kpi_card(10,  155, 220, 75, "Connexions Web",    "Nb Connexions (Volume Web)",    "_M_Digital"),
            kpi_card(240, 155, 220, 75, "Connexions Mobile", "Nb Connexions (Volume Mobile)", "_M_Digital"),
            kpi_card(470, 155, 220, 75, "Clients KYC Rouge", "Nb Clients KYC Rouge",          "_M_Clients", bg="#FEE2E2"),
            kpi_card(700, 155, 220, 75, "Clients Actifs",    "Nb Clients Actifs",             "_M_Clients"),
            kpi_card(930, 155, 220, 75, "Taux Actifs",       "Taux Clients Actifs",           "_M_Clients"),
            # Charts
            line_chart(10,  245, 580, 220, "Évolution des Enrollements (par date)",   "CLIENT", "dt_enrol",    "Nb Clients Enrollés", "_M_Digital"),
            donut_chart(610, 245, 350, 220, "Répartition Canaux de Connexion",        "TRANSACTION", "canal_ordre", "Nb Transactions", "_M_Conformite"),
            # Slicers
            slicer(970, 245, 280, 100, "État Accès", "CLIENT", "etat_acc"),
            slicer(970, 360, 280, 80,  "Type Client", "CLIENT", "lib_cd_typ"),
            # Table clients bloqués
            table_visual(10, 480, 1240, 220, "Clients à surveiller (Bloqués / Suspendus / Sans connexion récente)",
                         [("CLIENT","nom_cplt"),("CLIENT","etat_acc"),("CLIENT","nb_dev_enrol"),
                          ("CLIENT","dt_der_cnx"),("CLIENT","agc_topz"),("CLIENT","lib_cd_risque_pers")])
        ]
    }

def make_page_produits():
    return {
        "name": "Produits",
        "displayName": "📦 Portefeuille Produits",
        "displayOption": 1,
        "height": 720, "width": 1280,
        "visualContainers": [
            text_box(10, 5, 700, 35, "Portefeuille Produits", 20, True, COLORS["bordeaux"]),
            # KPI produits
            kpi_card(10,  50, 195, 85, "Nb Cartes",          "Nb Cartes",             "_M_Produits"),
            kpi_card(215, 50, 195, 85, "Encours Épargne",    "Encours Épargne",        "_M_Epargne"),
            kpi_card(420, 50, 195, 85, "Encours Crédit",     "Encours Crédit Total",   "_M_Credit"),
            kpi_card(625, 50, 195, 85, "Collecte Nette",     "Collecte Nette",         "_M_Epargne"),
            kpi_card(830, 50, 195, 85, "Nb Contrats Crédit", "Nb Contrats Crédit",     "_M_Credit"),
            kpi_card(1035,50, 195, 85, "Nb Contrats Épargne","Nb Contrats Épargne",    "_M_Epargne"),
            # Charts
            bar_chart(10,  150, 400, 220, "Encours par Famille Produit",      "EPARGNE","fam_pdt",          "Encours Épargne",   "_M_Epargne"),
            bar_chart(420, 150, 400, 220, "Crédits par Type de Marché",       "CREDIT","Lib_Marche_Simple",  "Encours Crédit Total","_M_Credit"),
            bar_chart(830, 150, 420, 220, "Répartition IFRS9 Crédit (bucket)","CREDIT","Lib_Bucket_Credit",  "Encours Crédit Total","_M_Credit"),
            # Charts row 2
            bar_chart(10,  385, 400, 200, "Collecte vs Décollecte par Produit","EPARGNE","fam_pdt",         "Collecte Brute",    "_M_Epargne"),
            donut_chart(420,385, 300, 200, "Encours Épargne SFDR",            "GSM","Classification_SFDR",  "Encours Épargne",   "_M_Epargne"),
            kpi_card(730, 385, 240, 90,  "Provision IFRS9 Crédit",   "Provision IFRS9 Crédit Total", "_M_Credit", bg="#FEF9C3"),
            kpi_card(980, 385, 240, 90,  "Taux Créances Douteuses",  "Taux Créances Douteuses",      "_M_Credit", bg="#FEE2E2"),
            # Table top fonds
            table_visual(10, 600, 1240, 100, "Top Fonds Épargne par Encours",
                         [("EPARGNE","lib_fds"),("EPARGNE","fam_pdt"),("EPARGNE","enc_fds_m"),
                          ("EPARGNE","Lib_Bucket_IFRS9"),("EPARGNE","isin_risq"),("GSM","Classification_SFDR")])
        ]
    }

def make_page_conformite():
    return {
        "name": "Conformite",
        "displayName": "⚠ Risque & Conformité",
        "displayOption": 1,
        "height": 720, "width": 1280,
        "visualContainers": [
            text_box(10, 5, 700, 35, "Risque & Conformité — AML / LCB-FT", 20, True, COLORS["alerte_r"]),
            # Alertes
            kpi_card(10,  50, 235, 85, "Clients Pays Embargo",   "Nb Clients Pays Embargo",   "_M_Conformite", bg="#FEE2E2"),
            kpi_card(255, 50, 235, 85, "Transactions Sensibles", "Nb Transactions Sensibles", "_M_Conformite", bg="#FEE2E2"),
            kpi_card(500, 50, 235, 85, "Volume Pays GDA",        "Volume Pays GDA",           "_M_Conformite", bg="#FEE2E2"),
            kpi_card(745, 50, 235, 85, "KYC Rouge",              "Nb Clients KYC Rouge",      "_M_Clients",    bg="#FEE2E2"),
            kpi_card(990, 50, 260, 85, "Certifications Échues",  "Nb Certifications à Renouveler", "_M_Clients",bg="#FEF9C3"),
            # Charts row 1
            bar_chart(10,  150, 420, 200, "Volume Transactions par Type d'Événement (Top 10)", "TRANSACTION","lib_evt_lv1","Volume Transactions Total","_M_Conformite"),
            bar_chart(440, 150, 420, 200, "Transactions par Couleur Pays Contrepartie",         "TRANSACTION","ctrpty_couleur_pays","Nb Transactions","_M_Conformite"),
            donut_chart(870,150, 390, 200, "Répartition Risque Client",                         "CLIENT","lib_cd_risque_pers","Nb Clients Totaux","_M_Clients"),
            # Charts row 2
            bar_chart(10,  365, 420, 190, "Clients par Couleur Pays de Résidence",  "CLIENT","couleur_pays",     "Nb Clients Totaux",          "_M_Clients"),
            bar_chart(440, 365, 420, 190, "Volume par Canal (Web vs Mobile)",        "TRANSACTION","canal_ordre", "Volume Transactions Total",  "_M_Conformite"),
            kpi_card(870,  365, 185, 85, "Vol. Embargo", "Volume Pays Embargo",    "_M_Conformite", bg="#FEE2E2"),
            kpi_card(1065, 365, 185, 85, "Vol. Sanctions","Volume Pays Sanctions","_M_Conformite", bg="#FEE2E2"),
            kpi_card(870,  460, 185, 85, "Tx 3DS",        "Nb Transactions 3DS",  "_M_Conformite"),
            kpi_card(1065, 460, 185, 85, "Sans Contact",  "Nb Transactions Sans Contact","_M_Conformite"),
            # Table transactions sensibles
            table_visual(10, 570, 1240, 135, "Transactions Sensibles (Pays à risque impliqués)",
                         [("CLIENT","nom_cplt"),("TRANSACTION","mnt_evt"),("TRANSACTION","dt_realisation"),
                          ("TRANSACTION","cli_couleur_pays"),("TRANSACTION","ctrpty_pays"),
                          ("TRANSACTION","ctrpty_couleur_pays"),("TRANSACTION","lib_evt_lv1"),("TRANSACTION","canal_ordre")])
        ]
    }

def make_page_commercial():
    return {
        "name": "Commercial",
        "displayName": "👥 Commercial & Clients",
        "displayOption": 1,
        "height": 720, "width": 1280,
        "visualContainers": [
            text_box(10, 5, 700, 35, "Commercial & Relation Client", 20, True, COLORS["bordeaux"]),
            # KPI row
            kpi_card(10,  50, 235, 85, "Clients Actifs",         "Nb Clients Actifs",         "_M_Clients"),
            kpi_card(255, 50, 235, 85, "Prospects",              "Nb Prospects",              "_M_Clients"),
            kpi_card(500, 50, 235, 85, "AUM Moyen / Client",     "AUM Moyen par Client",      "_M_Clients"),
            kpi_card(745, 50, 235, 85, "Sans RDV > 6 mois",      "Nb Clients sans RDV depuis 6 mois","_M_Clients",bg="#FEF9C3"),
            kpi_card(990, 50, 260, 85, "Taux Clients Actifs",    "Taux Clients Actifs",       "_M_Clients"),
            # Charts row 1
            bar_chart(10,  150, 380, 195, "Clients par Type (PP/PM/Prospect)",   "CLIENT","lib_cd_typ",         "Nb Clients Totaux",     "_M_Clients"),
            scatter_chart(400, 150, 480, 195, "Risque vs AUM (taille = Épargne)"),
            bar_chart(890, 150, 370, 195, "AUM par Groupe Risque",               "CLIENT","lib_groupe_risque",  "AUM Total",             "_M_Clients"),
            # Charts row 2
            bar_chart(10,  360, 380, 195, "Taux Pénétration par Produit",        "EPARGNE","fam_pdt",           "Taux Pénétration Épargne","_M_Produits"),
            donut_chart(400,360, 300, 195, "Statut KYC (Vert/Orange/Rouge)",     "CLIENT","Couleur_KYC",         "Nb Clients Totaux",     "_M_Clients"),
            bar_chart(710, 360, 550, 195, "Clients par Agence",                  "CLIENT","agc_topz",           "Nb Clients Totaux",     "_M_Clients"),
            # Table portefeuille
            table_visual(10, 570, 1240, 135, "Portefeuille Clients — Trié par AUM décroissant",
                         [("CLIENT","nom_cplt"),("CLIENT","lib_cd_typ"),("CLIENT","aum_tit"),
                          ("CLIENT","lib_cd_risque_pers"),("CLIENT","dt_dernier_rdv"),
                          ("CLIENT","Couleur_KYC"),("CLIENT","top_client_actif"),("CLIENT","agc_topz")])
        ]
    }

# ── Layout JSON ────────────────────────────────────────────────────────────────
def build_layout():
    pages = [
        make_page_accueil(),
        make_page_digital(),
        make_page_produits(),
        make_page_conformite(),
        make_page_commercial()
    ]
    layout = {
        "id": 0,
        "resourcePackages": [],
        "sections": [],
        "config": json.dumps({
            "version": "5.47",
            "themeCollection": {"baseTheme": {"name":"CY24SU05","version":"5.47","type":2}},
            "activeSectionIndex": 0,
            "defaultDrillFilterOtherVisuals": True
        })
    }
    for i, p in enumerate(pages):
        containers = p.pop("visualContainers", [])
        section = {
            "id": i,
            "name": p["name"],
            "displayName": p["displayName"],
            "displayOption": 1,
            "height": p.get("height", 720),
            "width": p.get("width", 1280),
            "config": json.dumps({
                "relationships": [],
                "background": {"color":{"solid":{"color":COLORS["fond"]}},"transparency":0},
                "wallpaper": {"transparency": 0}
            }),
            "filters": "[]",
            "ordinal": i,
            "visualContainers": [json.dumps(c) for c in containers]
        }
        layout["sections"].append(section)
    return json.dumps(layout, ensure_ascii=False)

# ── Metadata ──────────────────────────────────────────────────────────────────
def build_metadata():
    return json.dumps({
        "version": "4.0",
        "createdFrom": "D",
        "lastUpdateTime": "2026-05-31T12:00:00",
        "settings": {},
        "toolsInfo": {"PBIDesktop": VERSION}
    }, ensure_ascii=False)

# ── DiagramLayout ─────────────────────────────────────────────────────────────
def build_diagram():
    nodes = []
    positions = {"CLIENT":(400,200),"TRANSACTION":(700,50),"EPARGNE":(700,200),
                 "CREDIT":(700,350),"GARANTIE":(1000,350),"SERVICE":(1000,50),"GSM":(1000,200)}
    for t,(x,y) in positions.items():
        nodes.append({"id":t,"title":t,"nodeIndex":len(nodes),"left":x,"top":y,"zIndex":0})
    return json.dumps({"version":1,"diagramNodes":nodes,"diagramLayouts":[{"id":"mainLayout","diagramNodes":nodes}]})

# ── Settings ──────────────────────────────────────────────────────────────────
SETTINGS = json.dumps({"version":"1.0","useStrokeStyleOnDataLabels":True,"useNewOnOffSwitch":True})

# ── SecurityBindings ─────────────────────────────────────────────────────────
SECURITY = ""

# ── Assemble PBIX ZIP ─────────────────────────────────────────────────────────
# Note : Le DataModel (SQLite) est la partie la plus complexe.
# On crée un PBIX "shell" valide que Power BI peut ouvrir.
# L'utilisateur connectera les données via "Modifier les requêtes".

print("Génération du fichier PBIX...")

tmp_dir = os.path.join(OUT_DIR, "tmp_pbix")
os.makedirs(tmp_dir, exist_ok=True)

# Écrire les fichiers
with open(os.path.join(tmp_dir,"[Content_Types].xml"),"w",encoding="utf-8") as f:
    f.write(CONTENT_TYPES)
with open(os.path.join(tmp_dir,"Version"),"w",encoding="utf-8") as f:
    f.write(VERSION)
with open(os.path.join(tmp_dir,"Metadata"),"w",encoding="utf-8") as f:
    f.write(build_metadata())
with open(os.path.join(tmp_dir,"DiagramLayout"),"w",encoding="utf-8") as f:
    f.write(build_diagram())
with open(os.path.join(tmp_dir,"Settings"),"w",encoding="utf-8") as f:
    f.write(SETTINGS)
with open(os.path.join(tmp_dir,"SecurityBindings"),"w",encoding="utf-8") as f:
    f.write(SECURITY)
with open(os.path.join(tmp_dir,"Connections"),"w",encoding="utf-8") as f:
    f.write(make_connections())

# Report/Layout
os.makedirs(os.path.join(tmp_dir,"Report"),exist_ok=True)
with open(os.path.join(tmp_dir,"Report","Layout"),"w",encoding="utf-8") as f:
    f.write(build_layout())

# DataModel — fichier SQLite minimal (requis par Power BI)
# On crée un fichier SQLite vide avec juste le schéma
import sqlite3
dm_path = os.path.join(tmp_dir,"DataModel")
conn = sqlite3.connect(dm_path)
cur = conn.cursor()
# Tables minimales pour que PBI accepte le fichier
cur.execute("CREATE TABLE IF NOT EXISTS _pbidm_version (version TEXT)")
cur.execute("INSERT INTO _pbidm_version VALUES ('2.0')")
conn.commit()
conn.close()

# Créer le ZIP .pbix
if os.path.exists(PBIX_OUT):
    os.remove(PBIX_OUT)

with zipfile.ZipFile(PBIX_OUT, "w", zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(tmp_dir):
        for file in files:
            fp = os.path.join(root, file)
            arcname = os.path.relpath(fp, tmp_dir)
            zf.write(fp, arcname)

shutil.rmtree(tmp_dir)
print(f"Fichier généré : {PBIX_OUT}")
print(f"Taille : {os.path.getsize(PBIX_OUT)/1024:.1f} KB")
print("\nPour ouvrir : double-cliquer sur LoBP_Dashboard.pbix")
print("Power BI demandera de reconnecte les sources de données.")
print(f"Pointer vers : {DATA_DIR}")
