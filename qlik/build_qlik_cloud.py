#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_qlik_cloud.py
Construit le board "Louvre Banque Privée" dans Qlik Cloud.
Réplique les 7 pages Power BI avec les mêmes mesures.

Prérequis :
    pip install websocket-client requests

Usage :
    python build_qlik_cloud.py --key VOTRE_PAT
    ou : set QLIK_API_KEY=xxx && python build_qlik_cloud.py

Étapes :
    --upload  : envoie les 7 CSV vers DataFiles
    --reload  : pose le script + recharge les données
    --sheets  : crée les 7 feuilles avec visuels
    (sans flag = fait tout)
"""

import argparse, json, os, re, sys, time, threading, uuid
import requests

try:
    import websocket
except ImportError:
    sys.exit("pip install websocket-client")

# ── CONFIG ────────────────────────────────────────────────────────────────────
TENANT  = "dvbtsxlwvjd3p96.fr.qlikcloud.com"
APP_ID  = "d718adab-b489-4543-8200-d11c052021b4"
DATA    = r"E:\louvre\powerbi\data"
QVS     = os.path.join(os.path.dirname(__file__), "10_load_louvre_csv.qvs")
TABLES  = ["CLIENT","TRANSACTION","EPARGNE","CREDIT","GARANTIE","SERVICE","GSM"]

# ── LOAD SCRIPT (lit le .qvs et adapte le chemin pour Cloud) ─────────────────
def cloud_script():
    with open(QVS, encoding="utf-8") as f:
        s = f.read()
    # Remplace le vPath local par la connexion DataFiles Cloud
    s = re.sub(r"SET vPath\s*=\s*'[^']*';", "SET vPath = 'lib://DataFiles';", s)
    # Change le séparateur \ → / dans les FROM
    s = re.sub(r"\[\$\(vPath\)\\\\?(\w+\.csv)\]", r"[$(vPath)/\1]", s)
    return s

# ── ENGINE API CLIENT ─────────────────────────────────────────────────────────
class QlikCloud:
    def __init__(self, tenant, app_id, api_key):
        self.tenant, self.app_id, self.api_key = tenant, app_id, api_key
        self._seq = 0
        self._replies: dict = {}
        self._lock = threading.Lock()
        self.ws = None
        self.doc = None

    def _next(self):
        with self._lock:
            self._seq += 1
            return self._seq

    def connect(self):
        hdr = [f"Authorization: Bearer {self.api_key}"]
        url = f"wss://{self.tenant}/app/{self.app_id}"
        print(f"  WebSocket → {url}")
        self.ws = websocket.create_connection(url, header=hdr, timeout=30)
        threading.Thread(target=self._reader, daemon=True).start()
        time.sleep(0.8)
        r = self.call(-1, "OpenDoc", [self.app_id])
        self.doc = r["result"]["qReturn"]["qHandle"]
        print(f"  Doc handle : {self.doc}")

    def _reader(self):
        while True:
            try:
                msg = json.loads(self.ws.recv())
                mid = msg.get("id")
                if mid is not None:
                    self._replies[mid] = msg
            except Exception:
                break

    def call(self, handle, method, params=None, timeout=120):
        seq = self._next()
        payload = {"jsonrpc": "2.0", "id": seq, "handle": handle,
                   "method": method, "params": params or []}
        self.ws.send(json.dumps(payload))
        t0 = time.time()
        while time.time() - t0 < timeout:
            if seq in self._replies:
                r = self._replies.pop(seq)
                if "error" in r:
                    raise RuntimeError(f"{method}: {r['error']}")
                return r
            time.sleep(0.05)
        raise TimeoutError(f"{method} n'a pas répondu dans {timeout}s")

    def d(self, method, params=None, timeout=120):
        return self.call(self.doc, method, params, timeout)

    def child(self, sheet_h, props):
        r = self.call(sheet_h, "CreateChild", [props])
        return r["result"]["qReturn"]["qHandle"]

    def close(self):
        if self.ws:
            try: self.ws.close()
            except Exception: pass


# ── UPLOAD CSV → DataFiles ────────────────────────────────────────────────────
def upload_csvs(api_key):
    print("\n[1/3] Upload des CSV vers Qlik Cloud DataFiles…")
    base = f"https://{TENANT}/api/v1/data-files"
    hdr  = {"Authorization": f"Bearer {api_key}"}

    # Récupère les fichiers existants
    existing = {}
    r = requests.get(base, headers=hdr, params={"limit": 100})
    if r.ok:
        for f in r.json().get("data", []):
            existing[f["name"]] = f["id"]

    for t in TABLES:
        path = os.path.join(DATA, f"{t}.csv")
        fname = f"{t}.csv"
        with open(path, "rb") as f:
            fdata = f.read()

        if fname in existing:
            fid = existing[fname]
            r2 = requests.put(f"{base}/{fid}", headers=hdr,
                              files={"data": (fname, fdata, "text/csv")},
                              data={"name": fname})
            verb = "MAJ "
        else:
            r2 = requests.post(base, headers=hdr,
                               files={"data": (fname, fdata, "text/csv")},
                               data={"name": fname})
            verb = "Ajout"

        status = "OK" if r2.status_code in (200, 201, 204) else f"ERR {r2.status_code}"
        print(f"  {verb} {fname:<22} {status}")
        if r2.status_code not in (200, 201, 204):
            print(f"       {r2.text[:200]}")

    print("  Upload terminé.")


# ── SCRIPT + RELOAD ───────────────────────────────────────────────────────────
def setup_reload(q):
    print("\n[2/3] Script + rechargement des données…")
    script = cloud_script()
    q.d("SetScript", [script])
    print("  Script positionné.")
    print("  DoReload en cours (peut prendre 30-60s)…")
    r = q.d("DoReload", [0, False, False], timeout=300)
    ok = r.get("result", {}).get("qReturn", False)
    print(f"  Reload : {'OK' if ok else 'ECHEC — voir Data Load Editor'}")
    q.d("DoSave")
    print("  App sauvegardée.")


# ── HELPERS VISUELS ───────────────────────────────────────────────────────────
def _dim(field, label=None):
    return {"qDef": {"qFieldDefs": [field], "qFieldLabels": [label or field]},
            "qNullSuppression": True}

def _meas(expr, label, fmt=None):
    d = {"qDef": expr, "qLabel": label}
    if fmt:
        d["qNumFormat"] = fmt
    return {"qDef": d, "qSortBy": {"qSortByNumeric": -1}}

FMTN = {"qType": "F", "qnDec": 0, "qUseThou": 1}   # nombre entier avec milliers
FMTP = {"qType": "P", "qnDec": 1}                   # pourcentage 1 déc.
FMTK = {"qType": "F", "qnDec": 0}                   # entier sans milliers

def _hc(dims, meas_list, mode="S"):
    return {"qDimensions": dims, "qMeasures": meas_list, "qMode": mode,
            "qSuppressMissing": True, "qSuppressZero": False,
            "qInitialDataFetch": [{"qTop": 0, "qLeft": 0, "qHeight": 1000, "qWidth": 30}]}

def kpi(label, expr, fmt=None):
    return {"qInfo": {"qType": "kpi"}, "visualization": "kpi",
            "title": label, "showTitles": True,
            "qHyperCubeDef": _hc([], [_meas(expr, label, fmt)])}

def chart(vtype, title, dims, meas_list):
    return {"qInfo": {"qType": vtype}, "visualization": vtype,
            "title": title, "showTitles": True,
            "qHyperCubeDef": _hc(dims, meas_list)}

def pivot(title, dims, cols, meas_list):
    obj = {"qInfo": {"qType": "pivot-table"}, "visualization": "pivot-table",
           "title": title, "showTitles": True,
           "qHyperCubeDef": _hc(dims + cols, meas_list, mode="P")}
    # marque les colonnes en pivot
    for i in range(len(cols)):
        obj["qHyperCubeDef"]["qDimensions"][len(dims) + i]["qOtherTotalSpec"] = {}
    return obj

def tbl(title, dims, meas_list):
    return {"qInfo": {"qType": "table"}, "visualization": "table",
            "title": title, "showTitles": True,
            "qHyperCubeDef": _hc(dims, meas_list)}

def filtre(field, label):
    return {"qInfo": {"qType": "filterpane"}, "visualization": "filterpane",
            "title": label, "showTitles": True,
            "qListObjects": [{"qDef": {"qFieldDefs": [field]},
                              "qInitialDataFetch": [{"qTop": 0,"qLeft": 0,
                                                     "qHeight": 200,"qWidth": 1}]}]}

def new_sheet(q, title):
    r = q.d("CreateGenericObject", [{"qInfo": {"qType": "sheet"},
                                      "qMetaDef": {"title": title},
                                      "cells": [], "columns": 24, "rows": 12}])
    h = r["result"]["qReturn"]["qHandle"]
    print(f"    Feuille '{title}' [h={h}]")
    return h


# ── 7 FEUILLES ────────────────────────────────────────────────────────────────
# Expressions avec les vrais noms de champs préfixés du modèle étoile
NB_CLI   = "Count(DISTINCT {<cli_c_p={'CL','CT'}>} id_cli)"
NB_ACT   = "Count(DISTINCT {<top_client_actif={'O'}>} id_cli)"
NB_ENROL = "Count(DISTINCT {<nb_dev_enrol={'>0'}>} id_cli)"
AUM      = "Sum(aum_tit)"
EP_ENC   = "Sum({<EP_perimetre={'epargne'}>} EP_enc_cnt_m)"
CR_ENC   = "Sum(CR_enc_cpt)"
COL_NET  = "Sum({<EP_perimetre={'epargne'}>} EP_col_nette)"
SENSIB   = "Count(DISTINCT {<cd_risque_pers={'E','F'}>} id_cli)"
ENROL_TX = f"{NB_ENROL} / {NB_CLI}"
ACT_TX   = f"{NB_ACT} / {NB_CLI}"
KYC_TX   = "Count(DISTINCT {<gelule_global={0}>} id_cli) / Count(DISTINCT {<cli_c_p={'CL','CT'}>} id_cli)"

def create_sheets(q):
    print("\n[3/3] Création des 7 feuilles…")

    # ── 1. Synthèse Exécutive ──────────────────────────────────────────────
    s = new_sheet(q, "Synthèse Exécutive")
    for lbl, expr, fmt in [
        ("Nb Clients",      NB_CLI,                            FMTK),
        ("AUM Total",       AUM,                               FMTN),
        ("Encours Épargne", EP_ENC,                            FMTN),
        ("Encours Crédit",  CR_ENC,                            FMTN),
        ("Collecte Nette",  COL_NET,                           FMTN),
        ("Clients Actifs",  NB_ACT,                            FMTK),
        ("Clients Sensibles", SENSIB,                          FMTK),
        ("Taux Enrôlement", ENROL_TX,                          FMTP),
    ]:
        q.child(s, kpi(lbl, expr, fmt))

    q.child(s, chart("piechart", "Clients par pays › agence",
        [_dim("lib_pay_res","Pays"), _dim("agc_topz","Agence")],
        [_meas(NB_CLI, "Clients", FMTK)]))

    q.child(s, chart("linechart", "Volume transactions par opération & canal",
        [_dim("TR_lib_evt_lv1","Opération"), _dim("TR_canal_ordre","Canal")],
        [_meas("Sum(TR_mnt_evt)", "Volume", FMTN)]))

    q.child(s, tbl("Détail clients — patrimoine & risque",
        [_dim("nom_cplt","Client"), _dim("lib_cd_typ","Type"),
         _dim("lib_pay_res","Pays"), _dim("agc_topz","Agence"),
         _dim("lib_cd_risque_pers","Risque")],
        [_meas(AUM, "AUM", FMTN),
         _meas(EP_ENC, "Épargne", FMTN),
         _meas(CR_ENC, "Crédit", FMTN)]))

    for f, l in [("lib_cd_typ","Type client"),("agc_topz","Agence"),
                 ("lib_pay_res","Pays"),("lib_gr","Groupe risque")]:
        q.child(s, filtre(f, l))

    # ── 2. Digital & Adoption ──────────────────────────────────────────────
    s = new_sheet(q, "Digital & Adoption")
    for lbl, expr, fmt in [
        ("Nb Clients",        NB_CLI,                                      FMTK),
        ("Clients Enrôlés",   NB_ENROL,                                    FMTK),
        ("Nb Smartphones",    "Sum(nb_dev_enrol)",                         FMTK),
        ("Taux Enrôlement",   ENROL_TX,                                    FMTP),
        ("Comptes Bloqués",   "Count(DISTINCT {<etat_acc={'B'}>} id_cli)", FMTK),
        ("Comptes Suspendus", "Count(DISTINCT {<etat_acc={'S'}>} id_cli)", FMTK),
    ]:
        q.child(s, kpi(lbl, expr, fmt))

    q.child(s, chart("piechart", "Transactions par canal",
        [_dim("TR_canal_ordre","Canal")],
        [_meas("Count(TR_mnt_evt)", "Transactions", FMTK)]))

    q.child(s, chart("linechart", "Tendance — volume transactions par mois",
        [_dim("AnneeMois","Mois")],
        [_meas("Sum(TR_mnt_evt)", "Volume", FMTN)]))

    q.child(s, chart("barchart", "Clients enrôlés par type d'enrôlement",
        [_dim("typ_enrol","Type")],
        [_meas(NB_ENROL, "Enrôlés", FMTK)]))

    q.child(s, tbl("Clients à surveiller (accès & enrôlement)",
        [_dim("nom_cplt","Client"), _dim("etat_acc","État accès"),
         _dim("typ_enrol","Type enrôl."), _dim("agc_topz","Agence"),
         _dim("lib_cd_risque_pers","Risque")],
        [_meas("Sum(nb_dev_enrol)", "Appareils", FMTK)]))

    for f, l in [("lib_cd_typ","Type client"),("agc_topz","Agence"),
                 ("etat_acc","État accès"),("typ_enrol","Type enrôlement")]:
        q.child(s, filtre(f, l))

    # ── 3. Risque & Conformité ─────────────────────────────────────────────
    s = new_sheet(q, "Risque & Conformité")
    for lbl, expr, fmt in [
        ("Clients Sensibles",   SENSIB,                                          FMTK),
        ("KYC Rouge",           "Count(DISTINCT {<gelule_global={10}>} id_cli)", FMTK),
        ("KYC Orange",          "Count(DISTINCT {<gelule_global={5}>} id_cli)",  FMTK),
        ("Tx Sensibles",        "Sum({<TR_Transaction_Sensible={1}>} 1)",        FMTK),
        ("Vol. Tx Sensibles",   "Sum({<TR_Transaction_Sensible={1}>} TR_mnt_evt)", FMTN),
        ("Conformité KYC",      KYC_TX,                                          FMTP),
    ]:
        q.child(s, kpi(lbl, expr, fmt))

    q.child(s, chart("barchart", "Entonnoir du risque client",
        [_dim("lib_cd_risque_pers","Risque")],
        [_meas(NB_CLI, "Clients", FMTK)]))

    q.child(s, chart("barchart", "Volume tx par couleur pays (contrepartie)",
        [_dim("TR_ctrpty_couleur_pays","Couleur pays")],
        [_meas("Sum(TR_mnt_evt)", "Volume", FMTN)]))

    q.child(s, chart("barchart", "Volume sensible par opération",
        [_dim("TR_lib_evt_lv1","Opération")],
        [_meas("Sum({<TR_Transaction_Sensible={1}>} TR_mnt_evt)", "Vol. sensible", FMTN)]))

    q.child(s, tbl("Clients à risque — KYC & conformité",
        [_dim("nom_cplt","Client"), _dim("lib_cd_risque_pers","Risque"),
         _dim("couleur_pays","Pays (couleur)"), _dim("agc_topz","Agence")],
        [_meas("Max(gelule_global)", "KYC", FMTK),
         _meas(AUM, "AUM", FMTN)]))

    for f, l in [("lib_cd_typ","Type client"),("agc_topz","Agence"),
                 ("lib_cd_risque_pers","Niveau risque"),("couleur_pays","Couleur pays")]:
        q.child(s, filtre(f, l))

    # ── 4. Commercial & Relation Client ────────────────────────────────────
    s = new_sheet(q, "Commercial & Relation Client")
    for lbl, expr, fmt in [
        ("Clients Actifs",  NB_ACT,                       FMTK),
        ("Prospects",       "Count(DISTINCT {<cli_c_p={'PR'}>} id_cli)", FMTK),
        ("AUM Total",       AUM,                          FMTN),
        ("AUM Moyen",       f"{AUM} / {NB_CLI}",          FMTN),
        ("Taux Actifs",     ACT_TX,                       FMTP),
        ("Nb Clients",      NB_CLI,                       FMTK),
    ]:
        q.child(s, kpi(lbl, expr, fmt))

    q.child(s, chart("barchart", "Clients par type › groupe (drill-down)",
        [_dim("lib_cd_typ","Type"), _dim("lib_gr","Groupe")],
        [_meas(NB_CLI, "Clients", FMTK)]))

    q.child(s, chart("combochart", "AUM & taux actifs par agence",
        [_dim("agc_topz","Agence")],
        [_meas(AUM, "AUM", FMTN),
         _meas(ACT_TX, "Taux actifs", FMTP)]))

    q.child(s, chart("treemap", "Clients par groupe de risque",
        [_dim("lib_gr","Groupe")],
        [_meas(NB_CLI, "Clients", FMTK)]))

    q.child(s, tbl("Portefeuille clients par conseiller",
        [_dim("nom_cplt","Client"), _dim("lib_cd_typ","Type"),
         _dim("nom_cons","Conseiller"), _dim("agc_topz","Agence"),
         _dim("top_client_actif","Actif")],
        [_meas(AUM, "AUM", FMTN)]))

    for f, l in [("lib_cd_typ","Type client"),("agc_topz","Agence"),
                 ("lib_gr","Groupe risque"),("top_client_actif","Actif O/N")]:
        q.child(s, filtre(f, l))

    # ── 5. Patrimoine — Épargne & Crédit ───────────────────────────────────
    s = new_sheet(q, "Patrimoine — Épargne & Crédit")
    COL_BRT = "Sum({<EP_perimetre={'epargne'}>} EP_col_brute)"
    DECOL   = "Sum({<EP_perimetre={'epargne'}>} EP_decollecte)"
    CAP_IMP = "Sum(CR_mnt_krd_imp)"
    for lbl, expr, fmt in [
        ("Encours Épargne",  EP_ENC,   FMTN),
        ("Collecte Brute",   COL_BRT,  FMTN),
        ("Décollecte",       DECOL,    FMTN),
        ("Collecte Nette",   COL_NET,  FMTN),
        ("Encours Crédit",   CR_ENC,   FMTN),
        ("Capital Impayé",   CAP_IMP,  FMTN),
    ]:
        q.child(s, kpi(lbl, expr, fmt))

    q.child(s, chart("barchart", "Encours épargne par famille › fonds (drill-down)",
        [_dim("EP_fam_pdt","Famille"), _dim("EP_lib_fds","Fonds")],
        [_meas(EP_ENC, "Encours", FMTN)]))

    q.child(s, chart("waterfallchart", "Cascade collecte nette par famille",
        [_dim("EP_fam_pdt","Famille")],
        [_meas(COL_NET, "Collecte nette", FMTN)]))

    q.child(s, chart("barchart", "Encours crédit par marché",
        [_dim("CR_Lib_Marche_Simple","Marché")],
        [_meas(CR_ENC, "Encours", FMTN)]))

    q.child(s, tbl("Fonds — encours par support",
        [_dim("EP_lib_fds","Fonds"), _dim("EP_fam_pdt","Famille"),
         _dim("EP_lib_mod_gest","Gestion")],
        [_meas("Sum(EP_enc_fds_m)", "Encours fonds", FMTN)]))

    for f, l in [("lib_cd_typ","Type client"),("agc_topz","Agence"),
                 ("EP_fam_pdt","Famille produit"),("EP_lib_mod_gest","Mode gestion")]:
        q.child(s, filtre(f, l))

    # ── 6. Crédit & Engagements ────────────────────────────────────────────
    s = new_sheet(q, "Crédit & Engagements")
    IMP_TX  = "Sum(CR_mnt_krd_imp) / Sum(CR_mnt_krd_tot)"
    COV_TX  = "Sum(GA_mnt_gar_cpta) / Sum(CR_enc_cpt)"
    for lbl, expr, fmt in [
        ("Encours Crédit",   CR_ENC,                     FMTN),
        ("Nb Crédits",       "Count(DISTINCT num_cnt)",  FMTK),
        ("Montant Débloqué", "Sum(CR_mnt_dblq)",         FMTN),
        ("Capital Impayé",   CAP_IMP,                    FMTN),
        ("Taux Impayés",     IMP_TX,                     FMTP),
        ("Couverture Gar.",  COV_TX,                     FMTP),
    ]:
        q.child(s, kpi(lbl, expr, fmt))

    q.child(s, chart("barchart", "Encours par type de prêt › marché (drill-down)",
        [_dim("CR_lib_typ_prt","Type prêt"), _dim("CR_lib_typ_mar","Marché")],
        [_meas(CR_ENC, "Encours", FMTN)]))

    q.child(s, chart("combochart", "Encours & taux impayés par marché",
        [_dim("CR_lib_typ_mar","Marché")],
        [_meas(CR_ENC, "Encours", FMTN),
         _meas(IMP_TX, "Taux impayés", FMTP)]))

    q.child(s, chart("piechart", "Répartition par bucket IFRS9",
        [_dim("CR_Lib_Bucket_Credit","Bucket")],
        [_meas(CR_ENC, "Encours", FMTN)]))

    q.child(s, tbl("Détail crédits — engagement, LTV, provisions & garanties",
        [_dim("CR_lib_typ_prt","Type prêt"), _dim("CR_lib_typ_mar","Marché"),
         _dim("CR_lib_cd_etat_creance","État")],
        [_meas("Sum(CR_mnt_nom)", "Nominal", FMTN),
         _meas(CR_ENC, "Encours", FMTN),
         _meas("Avg({<CR_ltv_act={'>0'}>} CR_ltv_act)", "LTV moy.", FMTP),
         _meas("Sum(CR_mnt_prov_b_ifrs9)+Sum(CR_mnt_prov_hb_ifrs9)", "Provisions", FMTN),
         _meas("Sum(GA_mnt_gar)", "Garanties", FMTN)]))

    for f, l in [("lib_cd_typ","Type client"),("agc_topz","Agence"),
                 ("CR_lib_typ_mar","Marché"),("CR_lib_cd_etat_creance","État créance")]:
        q.child(s, filtre(f, l))

    # ── 7. Analyse Avancée 360° ────────────────────────────────────────────
    s = new_sheet(q, "Analyse Avancée 360°")

    # Tableau croisé pivot : AUM par type × groupe
    q.child(s, {
        "qInfo": {"qType": "pivot-table"}, "visualization": "pivot-table",
        "title": "Tableau croisé — AUM par type & groupe de risque",
        "showTitles": True,
        "qHyperCubeDef": {
            "qDimensions": [_dim("lib_cd_typ","Type"), _dim("lib_gr","Groupe")],
            "qMeasures": [_meas(AUM, "AUM", FMTN)],
            "qMode": "P",
            "qInitialDataFetch": [{"qTop": 0,"qLeft": 0,"qHeight": 50,"qWidth": 20}]
        }
    })

    # Scatter : AUM vs Épargne, taille = Crédit
    q.child(s, {
        "qInfo": {"qType": "scatterplot"}, "visualization": "scatterplot",
        "title": "Clients : AUM vs Épargne (taille = Crédit)",
        "showTitles": True,
        "qHyperCubeDef": {
            "qDimensions": [_dim("nom_cplt","Client")],
            "qMeasures": [_meas(AUM, "AUM", FMTN),
                          _meas(EP_ENC, "Épargne", FMTN),
                          _meas(CR_ENC, "Crédit (taille)", FMTN)],
            "qMode": "S",
            "qInitialDataFetch": [{"qTop": 0,"qLeft": 0,"qHeight": 500,"qWidth": 10}]
        }
    })

    # Jauge : conformité KYC
    q.child(s, kpi("Taux Conformité KYC", KYC_TX, FMTP))

    # Cascade : collecte nette
    q.child(s, chart("waterfallchart", "Cascade — collecte nette par famille",
        [_dim("EP_fam_pdt","Famille")],
        [_meas(COL_NET, "Collecte nette", FMTN)]))

    # Ruban : volume par opération & canal
    q.child(s, chart("barchart", "Volume par opération & canal",
        [_dim("TR_lib_evt_lv1","Opération"), _dim("TR_canal_ordre","Canal")],
        [_meas("Sum(TR_mnt_evt)", "Volume", FMTN)]))

    # Entonnoir : clients par niveau de risque
    q.child(s, chart("barchart", "Entonnoir — clients par niveau de risque",
        [_dim("lib_cd_risque_pers","Risque")],
        [_meas(NB_CLI, "Clients", FMTK)]))

    for f, l in [("lib_cd_typ","Type client"),("agc_topz","Agence"),
                 ("lib_pay_res","Pays"),("lib_cd_risque_pers","Risque")]:
        q.child(s, filtre(f, l))

    q.d("DoSave")
    print("\n  7 feuilles créées et app sauvegardée.")


# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="Build Qlik Cloud board — Louvre Banque Privée")
    ap.add_argument("--key",    default=os.environ.get("QLIK_API_KEY", ""),
                    help="Personal Access Token Qlik Cloud")
    ap.add_argument("--upload",  action="store_true", help="Upload CSVs")
    ap.add_argument("--reload",  action="store_true", help="Set script + reload")
    ap.add_argument("--sheets",  action="store_true", help="Créer les feuilles")
    args = ap.parse_args()

    if not args.key:
        sys.exit("ERREUR : Fournir --key TOKEN  ou  set QLIK_API_KEY=xxx")

    do_all = not any([args.upload, args.reload, args.sheets])

    if do_all or args.upload:
        upload_csvs(args.key)

    q = QlikCloud(TENANT, APP_ID, args.key)
    try:
        print("\nConnexion à Qlik Cloud Engine API…")
        q.connect()
        if do_all or args.reload:
            setup_reload(q)
        if do_all or args.sheets:
            create_sheets(q)
    finally:
        q.close()

    print("\n✓ Board Louvre Banque Privée — COMPLET")
    print(f"  Ouvrir : https://{TENANT}/sense/app/{APP_ID}/overview")


if __name__ == "__main__":
    main()
