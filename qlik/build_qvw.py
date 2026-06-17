#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_qvw.py
Génère LoBP_CustomerIntent.qvw via QlikView Desktop (COM automation).
Crée les 7 feuilles, KPIs, graphiques et filtres — identiques aux boards Power BI.

Prérequis :
    1. QlikView Desktop (Personal Edition gratuite)
       → https://www.qlik.com/us/try-or-buy/download-qlikview
    2. pip install pywin32   (déjà installé si vous lisez ce message)

Usage :
    python build_qvw.py
    python build_qvw.py --visible      # Voir QlikView pendant la génération
    python build_qvw.py --no-reload    # Script sans rechargement (test)
    python build_qvw.py --data C:\\autre\\chemin\\data

Sortie :
    qlik/LoBP_CustomerIntent.qvw  (ouvrable dans QlikView Desktop)
"""

import argparse
import os
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
QVS  = os.path.join(ROOT, "LoBP_CustomerIntent.qvs")
OUT  = os.path.join(ROOT, "LoBP_CustomerIntent.qvw")
DATA_DEFAULT = r"E:\louvre\powerbi\data"

# ── EXPRESSIONS (identiques au Power BI / build_qlik_cloud.py) ───────────────
NB_CLI   = "Count(DISTINCT {<cli_c_p={'CL','CT'}>} id_cli)"
NB_ACT   = "Count(DISTINCT {<top_client_actif={'O'}>} id_cli)"
NB_ENROL = "Count(DISTINCT {<nb_dev_enrol={'>0'}>} id_cli)"
AUM      = "Sum(aum_tit)"
EP_ENC   = "Sum({<EP_perimetre={'epargne'}>} EP_enc_cnt_m)"
CR_ENC   = "Sum(CR_enc_cpt)"
COL_NET  = "Sum({<EP_perimetre={'epargne'}>} EP_col_nette)"
COL_BRT  = "Sum({<EP_perimetre={'epargne'}>} EP_col_brute)"
DECOL    = "Sum({<EP_perimetre={'epargne'}>} EP_decollecte)"
CAP_IMP  = "Sum(CR_mnt_krd_imp)"
SENSIB   = "Count(DISTINCT {<cd_risque_pers={'E','F'}>} id_cli)"
ENROL_TX = f"{NB_ENROL} / {NB_CLI}"
ACT_TX   = f"{NB_ACT} / {NB_CLI}"
KYC_TX   = "Count(DISTINCT {<gelule_global={0}>} id_cli) / Count(DISTINCT {<cli_c_p={'CL','CT'}>} id_cli)"
IMP_TX   = "Sum(CR_mnt_krd_imp) / Sum(CR_mnt_krd_tot)"
COV_TX   = "Sum(GA_mnt_gar_cpta) / Sum(CR_enc_cpt)"
VOL_TX   = "Sum(TR_mnt_evt)"
PROV     = "Sum(CR_mnt_prov_b_ifrs9) + Sum(CR_mnt_prov_hb_ifrs9)"

# ── DÉFINITION DES 7 FEUILLES ─────────────────────────────────────────────────
# Chaque feuille : titre, liste de (libellé, expression, format), dimensions filtres
# Formats : "I" = entier, "P" = %, "M" = monétaire
SHEETS_DEF = [
    {
        "title": "Synthèse Exécutive",
        "kpis": [
            ("Nb Clients",        NB_CLI,   "I"),
            ("AUM Total (k€)",    AUM,      "M"),
            ("Encours Épargne",   EP_ENC,   "M"),
            ("Encours Crédit",    CR_ENC,   "M"),
            ("Collecte Nette",    COL_NET,  "M"),
            ("Clients Actifs",    NB_ACT,   "I"),
            ("Clients Sensibles", SENSIB,   "I"),
            ("Taux Enrôlement",   ENROL_TX, "P"),
        ],
        "charts": [
            ("bar",  "Clients par type",          ["lib_cd_typ"],               NB_CLI),
            ("bar",  "Clients par agence",         ["agc_topz"],                 NB_CLI),
            ("pie",  "Répartition par pays",       ["lib_pay_res"],              NB_CLI),
            ("line", "Volume transactions/mois",   ["AnneeMois"],                VOL_TX),
        ],
        "tables": [
            ("Détail clients",
             ["nom_cplt","lib_cd_typ","agc_topz","lib_pay_res","lib_cd_risque_pers"],
             [("AUM", AUM), ("Épargne", EP_ENC), ("Crédit", CR_ENC)]),
        ],
        "filters": ["lib_cd_typ", "agc_topz", "lib_pay_res", "lib_gr"],
    },
    {
        "title": "Digital & Adoption",
        "kpis": [
            ("Nb Clients",         NB_CLI,                                                    "I"),
            ("Clients Enrôlés",    NB_ENROL,                                                  "I"),
            ("Taux Enrôlement",    ENROL_TX,                                                  "P"),
            ("Nb Smartphones",     "Sum(nb_dev_enrol)",                                       "I"),
            ("Comptes Bloqués",    "Count(DISTINCT {<etat_acc={'B'}>} id_cli)",               "I"),
            ("Comptes Suspendus",  "Count(DISTINCT {<etat_acc={'S'}>} id_cli)",               "I"),
        ],
        "charts": [
            ("pie",  "Tx par canal",               ["TR_canal_ordre"],            "Count(TR_mnt_evt)"),
            ("line", "Volume tx / mois",           ["AnneeMois"],                 VOL_TX),
            ("bar",  "Enrôlés par type",           ["typ_enrol"],                 NB_ENROL),
        ],
        "tables": [
            ("Clients à surveiller",
             ["nom_cplt","etat_acc","typ_enrol","agc_topz","lib_cd_risque_pers"],
             [("Appareils", "Sum(nb_dev_enrol)")]),
        ],
        "filters": ["lib_cd_typ", "agc_topz", "etat_acc", "typ_enrol"],
    },
    {
        "title": "Risque & Conformité",
        "kpis": [
            ("Clients Sensibles",   SENSIB,                                                    "I"),
            ("KYC Rouge",           "Count(DISTINCT {<gelule_global={10}>} id_cli)",           "I"),
            ("KYC Orange",          "Count(DISTINCT {<gelule_global={5}>} id_cli)",            "I"),
            ("Tx Sensibles",        "Sum({<TR_Transaction_Sensible={1}>} 1)",                  "I"),
            ("Vol. Tx Sensibles",   "Sum({<TR_Transaction_Sensible={1}>} TR_mnt_evt)",         "M"),
            ("Conformité KYC",      KYC_TX,                                                    "P"),
        ],
        "charts": [
            ("bar", "Clients par niveau risque",     ["lib_cd_risque_pers"],     NB_CLI),
            ("bar", "Vol. tx par couleur pays",      ["TR_ctrpty_couleur_pays"], VOL_TX),
            ("bar", "Vol. sensible par opération",   ["TR_lib_evt_lv1"],
             "Sum({<TR_Transaction_Sensible={1}>} TR_mnt_evt)"),
        ],
        "tables": [
            ("Clients à risque",
             ["nom_cplt","lib_cd_risque_pers","couleur_pays","agc_topz"],
             [("KYC", "Max(gelule_global)"), ("AUM", AUM)]),
        ],
        "filters": ["lib_cd_typ", "agc_topz", "lib_cd_risque_pers", "couleur_pays"],
    },
    {
        "title": "Commercial & Relation Client",
        "kpis": [
            ("Clients Actifs",  NB_ACT,                                          "I"),
            ("Prospects",       "Count(DISTINCT {<cli_c_p={'PR'}>} id_cli)",     "I"),
            ("AUM Total",       AUM,                                             "M"),
            ("AUM Moyen",       f"{AUM} / {NB_CLI}",                            "M"),
            ("Taux Actifs",     ACT_TX,                                          "P"),
            ("Nb Clients",      NB_CLI,                                          "I"),
        ],
        "charts": [
            ("bar",     "Clients par type › groupe",    ["lib_cd_typ","lib_gr"],  NB_CLI),
            ("combo",   "AUM & taux actifs par agence", ["agc_topz"],             AUM),
            ("treemap", "Clients par groupe risque",    ["lib_gr"],               NB_CLI),
        ],
        "tables": [
            ("Portefeuille par conseiller",
             ["nom_cplt","lib_cd_typ","nom_cons","agc_topz","top_client_actif"],
             [("AUM", AUM)]),
        ],
        "filters": ["lib_cd_typ", "agc_topz", "lib_gr", "top_client_actif"],
    },
    {
        "title": "Patrimoine — Épargne & Crédit",
        "kpis": [
            ("Encours Épargne",  EP_ENC,  "M"),
            ("Collecte Brute",   COL_BRT, "M"),
            ("Décollecte",       DECOL,   "M"),
            ("Collecte Nette",   COL_NET, "M"),
            ("Encours Crédit",   CR_ENC,  "M"),
            ("Capital Impayé",   CAP_IMP, "M"),
        ],
        "charts": [
            ("bar",       "Épargne par famille › fonds",  ["EP_fam_pdt","EP_lib_fds"], EP_ENC),
            ("waterfall", "Cascade collecte nette",       ["EP_fam_pdt"],              COL_NET),
            ("bar",       "Crédit par marché",            ["CR_Lib_Marche_Simple"],    CR_ENC),
        ],
        "tables": [
            ("Fonds — encours",
             ["EP_lib_fds","EP_fam_pdt","EP_lib_mod_gest"],
             [("Encours fonds", "Sum(EP_enc_fds_m)")]),
        ],
        "filters": ["lib_cd_typ", "agc_topz", "EP_fam_pdt", "EP_lib_mod_gest"],
    },
    {
        "title": "Crédit & Engagements",
        "kpis": [
            ("Encours Crédit",    CR_ENC,                   "M"),
            ("Nb Crédits",        "Count(DISTINCT num_cnt)", "I"),
            ("Montant Débloqué",  "Sum(CR_mnt_dblq)",       "M"),
            ("Capital Impayé",    CAP_IMP,                  "M"),
            ("Taux Impayés",      IMP_TX,                   "P"),
            ("Couverture Gar.",   COV_TX,                   "P"),
        ],
        "charts": [
            ("bar",   "Encours par type › marché",     ["CR_lib_typ_prt","CR_lib_typ_mar"], CR_ENC),
            ("combo", "Encours & tx impayés/marché",   ["CR_lib_typ_mar"],                  CR_ENC),
            ("pie",   "Répartition IFRS9",             ["CR_Lib_Bucket_Credit"],            CR_ENC),
        ],
        "tables": [
            ("Détail crédits",
             ["CR_lib_typ_prt","CR_lib_typ_mar","CR_lib_cd_etat_creance"],
             [("Nominal", "Sum(CR_mnt_nom)"), ("Encours", CR_ENC),
              ("LTV moy.", "Avg({<CR_ltv_act={'>0'}>} CR_ltv_act)"),
              ("Provisions", PROV), ("Garanties", "Sum(GA_mnt_gar)")]),
        ],
        "filters": ["lib_cd_typ", "agc_topz", "CR_lib_typ_mar", "CR_lib_cd_etat_creance"],
    },
    {
        "title": "Analyse Avancée 360°",
        "kpis": [
            ("Conformité KYC", KYC_TX, "P"),
        ],
        "charts": [
            ("pivot",     "Croisé AUM type × groupe",       ["lib_cd_typ","lib_gr"],         AUM),
            ("scatter",   "Clients AUM vs Épargne",         ["nom_cplt"],                    AUM),
            ("waterfall", "Cascade collecte / famille",     ["EP_fam_pdt"],                  COL_NET),
            ("bar",       "Volume par opération & canal",   ["TR_lib_evt_lv1","TR_canal_ordre"], VOL_TX),
            ("bar",       "Entonnoir risque client",        ["lib_cd_risque_pers"],           NB_CLI),
        ],
        "tables": [],
        "filters": ["lib_cd_typ", "agc_topz", "lib_pay_res", "lib_cd_risque_pers"],
    },
]

# ── FORMATAGE QV ──────────────────────────────────────────────────────────────
FMT_INT  = "#,##0"
FMT_PCT  = "0.0%"
FMT_MNY  = "#,##0 €"

def _fmt(code):
    return {"I": FMT_INT, "P": FMT_PCT, "M": FMT_MNY}.get(code, FMT_INT)

# ── WRAPPERS COM (abstractions sur IQVDocument) ───────────────────────────────

def add_kpi_text(doc, sheet, label, expr, fmt_code, pos):
    """Ajoute un TextObject KPI (label + valeur) sur la feuille."""
    x, y, w, h = pos  # position en unités QV (1/1000 de la taille de la feuille)
    try:
        obj = doc.GetSheet(sheet).AddTextObject(x, y, w, h)
        obj.SetCaption(label)
        # Expression dans la propriété Text
        props = obj.GetProperties()
        props.Text = f"='{label}' & Chr(10) & Num({expr}, '{_fmt(fmt_code)}')"
        obj.SetProperties(props)
    except Exception as e:
        print(f"      ⚠ KPI '{label}' : {e}")


def add_chart(doc, sheet_name, chart_type, title, dims, expr, pos):
    """Crée un graphique (bar, pie, line, combo, waterfall, treemap, scatter, pivot)."""
    x, y, w, h = pos
    qv_type_map = {
        "bar":       0,   # BarChart
        "line":      1,   # LineChart
        "pie":       5,   # PieChart
        "scatter":   7,   # ScatterChart
        "pivot":     10,  # PivotTable
        "waterfall": 12,  # WaterfallChart
        "combo":     6,   # ComboChart
        "treemap":   13,  # TreeMap
    }
    try:
        sheet = doc.GetSheet(sheet_name)
        chart = sheet.AddChartObject(x, y, w, h)
        props = chart.GetProperties()
        props.ChartType = qv_type_map.get(chart_type, 0)
        props.Caption = title

        # Dimensions
        for i, dim in enumerate(dims):
            d = props.GetDimension(i)
            d.FieldName = dim
            d.Label     = dim.replace("_"," ").replace("lib ","").strip()

        # Expression / mesure
        e = props.GetExpression(0)
        e.Definition = expr
        e.Label      = title

        chart.SetProperties(props)
    except Exception as e:
        print(f"      ⚠ Chart '{title}' : {e}")


def add_table(doc, sheet_name, title, dims, measures, pos):
    """Crée une StraightTable avec dimensions + mesures."""
    x, y, w, h = pos
    try:
        sheet = doc.GetSheet(sheet_name)
        tbl = sheet.AddChartObject(x, y, w, h)
        props = tbl.GetProperties()
        props.ChartType = 11  # StraightTable
        props.Caption   = title

        for i, dim in enumerate(dims):
            d = props.GetDimension(i)
            d.FieldName = dim
            d.Label     = dim.replace("_"," ").strip()

        for i, (lbl, expr) in enumerate(measures):
            e = props.GetExpression(i)
            e.Definition = expr
            e.Label      = lbl

        tbl.SetProperties(props)
    except Exception as e:
        print(f"      ⚠ Table '{title}' : {e}")


def add_listbox(doc, sheet_name, field, pos):
    """Ajoute un filtre (ListBox) pour un champ."""
    x, y, w, h = pos
    try:
        sheet = doc.GetSheet(sheet_name)
        lb = sheet.AddListObject(x, y, w, h, field)
        props = lb.GetProperties()
        props.Caption = field.replace("_"," ").strip()
        lb.SetProperties(props)
    except Exception as e:
        print(f"      ⚠ Filtre '{field}' : {e}")


# ── POSITIONNEMENT AUTO ───────────────────────────────────────────────────────
def layout(n_kpis, n_charts, n_tables, n_filters):
    """
    Retourne des positions (x,y,w,h) en unités QV [0..40000 × 0..30000]
    pour chaque type d'objet, en grille automatique.
    """
    kpi_w, kpi_h = 5000, 4000
    positions = {"kpis": [], "charts": [], "tables": [], "filters": []}

    # KPIs : 1ère ligne, jusqu'à 4 par rangée
    for i in range(n_kpis):
        col, row = i % 4, i // 4
        positions["kpis"].append((col * kpi_w, row * kpi_h, kpi_w, kpi_h))

    # Charts : 2 par ligne sous les KPIs
    kpi_rows = ((n_kpis - 1) // 4 + 1) if n_kpis else 0
    chart_y0 = kpi_rows * kpi_h + 500
    ch_w, ch_h = 19000, 9000
    for i in range(n_charts):
        col, row = i % 2, i // 2
        positions["charts"].append((col * (ch_w + 500), chart_y0 + row * (ch_h + 500), ch_w, ch_h))

    # Tables : sous les charts
    ch_rows = ((n_charts - 1) // 2 + 1) if n_charts else 0
    tbl_y0 = chart_y0 + ch_rows * (ch_h + 500)
    for i in range(n_tables):
        positions["tables"].append((0, tbl_y0 + i * 10000, 38000, 9000))

    # Filtres : colonne droite
    for i in range(n_filters):
        positions["filters"].append((39000, i * 5000, 9000, 4500))

    return positions


# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="Génère LoBP_CustomerIntent.qvw")
    ap.add_argument("--visible",   action="store_true", help="Afficher QlikView pendant la génération")
    ap.add_argument("--no-reload", action="store_true", help="Poser le script sans recharger les données")
    ap.add_argument("--data",      default=DATA_DEFAULT, help="Chemin vers les CSV")
    ap.add_argument("--out",       default=OUT,          help="Chemin de sortie .qvw")
    args = ap.parse_args()

    # ── Lecture du script QVS et adaptation locale ───────────────────────────
    if not os.path.exists(QVS):
        sys.exit(f"Script introuvable : {QVS}\nLancer d'abord gen_load_script.py ou utiliser LoBP_CustomerIntent.qvs")

    with open(QVS, encoding="utf-8") as f:
        script = f.read()

    # Adapte le chemin pour mode local (Desktop)
    data_path = args.data.replace("\\", "\\\\")
    script = (script
              .replace("SET vPath = 'lib://DataFiles';",
                       f"SET vPath = '{data_path}';")
              .replace("$(vPath)/", "$(vPath)\\\\"))

    # ── Connexion QlikView COM ────────────────────────────────────────────────
    print("Connexion à QlikView Desktop...")
    try:
        import win32com.client
    except ImportError:
        sys.exit("ERREUR : pip install pywin32")

    try:
        qv = win32com.client.Dispatch("QlikTech.QlikView")
    except Exception as e:
        print(f"\n✗ QlikView Desktop non trouvé : {e}")
        print("\nTélécharger QlikView Desktop Personal Edition (gratuit) :")
        print("  https://www.qlik.com/us/try-or-buy/download-qlikview")
        print("\nAprès installation, relancer ce script.")
        sys.exit(1)

    qv.Visible = args.visible

    # ── Nouveau document ──────────────────────────────────────────────────────
    print(f"Création du document : {args.out}")
    try:
        doc = qv.NewDoc(args.out)
    except Exception:
        # Fallback : ouvre un doc vierge et sauvegarde ensuite
        doc = qv.ActiveDocument or qv.OpenDoc("")

    # ── Script ───────────────────────────────────────────────────────────────
    print("Positionnement du script de chargement...")
    doc.SetScript(script)

    # ── Variables mesures ────────────────────────────────────────────────────
    print("Ajout des variables mesures...")
    vars_to_set = [
        ("vNB_CLI",   NB_CLI),
        ("vNB_ACT",   NB_ACT),
        ("vNB_ENROL", NB_ENROL),
        ("vAUM",      AUM),
        ("vEP_ENC",   EP_ENC),
        ("vCR_ENC",   CR_ENC),
        ("vCOL_NET",  COL_NET),
        ("vCOL_BRT",  COL_BRT),
        ("vDECOL",    DECOL),
        ("vCAP_IMP",  CAP_IMP),
        ("vSENSIB",   SENSIB),
        ("vENROL_TX", ENROL_TX),
        ("vACT_TX",   ACT_TX),
        ("vKYC_TX",   KYC_TX),
        ("vIMP_TX",   IMP_TX),
        ("vCOV_TX",   COV_TX),
        ("vVOL_TX",   VOL_TX),
        ("vPROV",     PROV),
    ]
    for name, expr in vars_to_set:
        try:
            v = doc.GetVariableByName(name)
            if v is None:
                v = doc.AddVariable(name)
            v.SetContent(expr, True)
        except Exception as e:
            print(f"  ⚠ Variable {name} : {e}")

    # ── Rechargement ─────────────────────────────────────────────────────────
    if not args.no_reload:
        print("Rechargement des données (peut prendre 30-60 s)...")
        ok = doc.Reload()
        print(f"  Reload : {'OK' if ok else 'ECHEC — vérifier le chemin des CSV'}")
    else:
        print("(Rechargement ignoré — mode --no-reload)")

    # ── 7 feuilles ───────────────────────────────────────────────────────────
    print("\nCréation des 7 feuilles...")

    # Renommer la feuille 1 déjà existante
    try:
        sheets = doc.GetSheets()
        if sheets.Count >= 1:
            sheets.Item(0).SetName(SHEETS_DEF[0]["title"])
    except Exception as e:
        print(f"  ⚠ Renommage feuille 1 : {e}")

    for i, sdef in enumerate(SHEETS_DEF):
        title = sdef["title"]
        print(f"  [{i+1}/7] {title}")

        # Ajouter la feuille (sauf la première déjà renommée)
        if i > 0:
            try:
                doc.AddSheet(title)
            except Exception as e:
                print(f"    ⚠ AddSheet : {e}")

        pos = layout(len(sdef["kpis"]), len(sdef["charts"]),
                     len(sdef.get("tables", [])), len(sdef["filters"]))

        # KPIs
        for j, (lbl, expr, fmt) in enumerate(sdef["kpis"]):
            if j < len(pos["kpis"]):
                add_kpi_text(doc, title, lbl, expr, fmt, pos["kpis"][j])

        # Graphiques
        for j, chart_def in enumerate(sdef["charts"]):
            if j < len(pos["charts"]):
                if len(chart_def) == 4:
                    ctype, ctitle, dims, expr = chart_def
                else:
                    ctype, ctitle, dims, expr = chart_def[0], chart_def[1], chart_def[2], chart_def[3]
                add_chart(doc, title, ctype, ctitle, dims, expr, pos["charts"][j])

        # Tables
        for j, (tlbl, tdims, tmeas) in enumerate(sdef.get("tables", [])):
            if j < len(pos["tables"]):
                add_table(doc, title, tlbl, tdims, tmeas, pos["tables"][j])

        # Filtres (ListBox)
        for j, field in enumerate(sdef["filters"]):
            if j < len(pos["filters"]):
                add_listbox(doc, title, field, pos["filters"][j])

    # ── Sauvegarde ───────────────────────────────────────────────────────────
    print(f"\nSauvegarde → {args.out}")
    try:
        doc.SaveAs(args.out)
    except Exception:
        try:
            doc.Save()
        except Exception as e:
            print(f"  ⚠ Save : {e}")

    if not args.visible:
        try:
            qv.Quit()
        except Exception:
            pass

    print(f"\n✓ Fichier créé : {args.out}")
    print("  Ouvrir dans QlikView Desktop pour finaliser la mise en page.")


if __name__ == "__main__":
    main()
