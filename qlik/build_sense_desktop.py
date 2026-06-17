#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_sense_desktop.py
Génère LoBP_CustomerIntent.qvf via Qlik Sense Desktop (Engine local port 9076).
Crée l'app avec 7 feuilles, KPIs, graphiques, filtres — identique au board Power BI.

Prérequis  : Qlik Sense Desktop installé + Engine.exe lancé (port 9076)
             pip install websocket-client
Usage      : python build_sense_desktop.py
Sortie     : %USERPROFILE%\Documents\Qlik\Sense\Apps\LoBP_CustomerIntent.qvf
"""

import json, os, sys, threading, time, uuid, shutil
import websocket

ENGINE_URL  = "ws://localhost:9076/app/"
AUTH_HEADER = ["X-Qlik-User: UserDirectory=WINDOWS;UserId=dedes"]
DATA        = r"E:\louvre\powerbi\data"
QVS         = os.path.join(os.path.dirname(os.path.abspath(__file__)), "LoBP_CustomerIntent.qvs")
APPS_DIR    = os.path.expanduser(r"~\Documents\Qlik\Sense\Apps")
APP_NAME    = "LoBP_CustomerIntent"

# ── EXPRESSIONS ──────────────────────────────────────────────────────────────
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

FMTN = {"qType": 4, "qnDec": 0, "qUseThou": 1}  # 4=fixed
FMTP = {"qType": 8, "qnDec": 1}                  # 8=percentage
FMTK = {"qType": 4, "qnDec": 0}                  # 4=fixed

# ── ENGINE CLIENT ─────────────────────────────────────────────────────────────
class Engine:
    def __init__(self, url):
        self._seq = 0
        self._replies = {}
        self._lock = threading.Lock()
        self.ws = websocket.create_connection(url, header=AUTH_HEADER, timeout=30)
        threading.Thread(target=self._reader, daemon=True).start()
        time.sleep(0.5)

    def _next(self):
        with self._lock:
            self._seq += 1
            return self._seq

    def _reader(self):
        while True:
            try:
                msg = json.loads(self.ws.recv())
                mid = msg.get("id")
                if mid is not None:
                    self._replies[mid] = msg
            except Exception:
                break

    def call(self, handle, method, params=None, timeout=180):
        seq = self._next()
        self.ws.send(json.dumps({
            "jsonrpc": "2.0", "id": seq,
            "handle": handle, "method": method,
            "params": params or []
        }))
        t0 = time.time()
        while time.time() - t0 < timeout:
            if seq in self._replies:
                r = self._replies.pop(seq)
                if "error" in r:
                    raise RuntimeError(f"{method}: {r['error']}")
                return r
            time.sleep(0.05)
        raise TimeoutError(f"{method} timeout")

    def close(self):
        try: self.ws.close()
        except Exception: pass

# ── HELPERS VISUELS ───────────────────────────────────────────────────────────
def _dim(field, label=None):
    return {"qDef": {"qFieldDefs": [field],
                     "qFieldLabels": [label or field.replace("_"," ").strip()]},
            "qNullSuppression": True}

def _meas(expr, label, fmt=None):
    d = {"qDef": expr, "qLabel": label}
    if fmt: d["qNumFormat"] = fmt
    return {"qDef": d, "qSortBy": {"qSortByNumeric": -1}}

def _hc(dims, meas_list):
    return {"qDimensions": dims, "qMeasures": meas_list,
            "qSuppressMissing": True, "qSuppressZero": False,
            "qInitialDataFetch": [{"qTop":0,"qLeft":0,"qHeight":1000,"qWidth":30}]}

def kpi(label, expr, fmt=None):
    return {"qInfo": {"qType": "kpi"}, "visualization": "kpi",
            "title": label, "showTitles": True,
            "qHyperCubeDef": _hc([], [_meas(expr, label, fmt)])}

def chart(vtype, title, dims, meas_list):
    return {"qInfo": {"qType": vtype}, "visualization": vtype,
            "title": title, "showTitles": True,
            "qHyperCubeDef": _hc(dims, meas_list)}

def tbl(title, dims, meas_list):
    return {"qInfo": {"qType": "table"}, "visualization": "table",
            "title": title, "showTitles": True,
            "qHyperCubeDef": _hc(dims, meas_list)}

def filtre(field, label=None):
    return {"qInfo": {"qType": "filterpane"}, "visualization": "filterpane",
            "title": label or field, "showTitles": True,
            "qListObjects": [{"qDef": {"qFieldDefs": [field]},
                              "qInitialDataFetch": [{"qTop":0,"qLeft":0,
                                                     "qHeight":200,"qWidth":1}]}]}

def new_sheet(q, doc_handle, title):
    r = q.call(doc_handle, "CreateObject", [{
        "qInfo": {"qType": "sheet"},
        "qMetaDef": {"title": title},
        "cells": [], "columns": 24, "rows": 12
    }])
    h = r["result"]["qReturn"]["qHandle"]
    print(f"    [OK] Feuille '{title}' [h={h}]")
    return h

def child(q, sheet_h, props):
    r = q.call(sheet_h, "CreateChild", [props])
    return r["result"]["qReturn"]["qHandle"]

# ── SCRIPT LOCAL ──────────────────────────────────────────────────────────────
def local_script():
    with open(QVS, encoding="utf-8") as f:
        return f.read()  # garde lib://DataFiles — connexion créée via CreateConnection


def create_connection(q, doc):
    r = q.call(doc, "CreateConnection", [{
        "qId": "",
        "qName": "DataFiles",
        "qConnectionString": DATA,
        "qType": "folder",
        "qLogOn": 0,
    }])
    conn_id = r.get("result", {}).get("qConnectionId", "")
    print(f"  Connexion 'DataFiles' -> {DATA}  [id={conn_id}]")
    return conn_id

# ── 7 FEUILLES ────────────────────────────────────────────────────────────────
def create_sheets(q, doc):
    print("\n[3/3] Création des 7 feuilles…")

    # 1 — Synthèse Exécutive
    s = new_sheet(q, doc, "Synthèse Exécutive")
    for lbl, expr, fmt in [
        ("Nb Clients",        NB_CLI,   FMTK),
        ("AUM Total",         AUM,      FMTN),
        ("Encours Épargne",   EP_ENC,   FMTN),
        ("Encours Crédit",    CR_ENC,   FMTN),
        ("Collecte Nette",    COL_NET,  FMTN),
        ("Clients Actifs",    NB_ACT,   FMTK),
        ("Clients Sensibles", SENSIB,   FMTK),
        ("Taux Enrôlement",   ENROL_TX, FMTP),
    ]:
        child(q, s, kpi(lbl, expr, fmt))
    child(q, s, chart("piechart","Clients par type",
        [_dim("lib_cd_typ","Type")],[_meas(NB_CLI,"Clients",FMTK)]))
    child(q, s, chart("barchart","Clients par agence",
        [_dim("agc_topz","Agence")],[_meas(NB_CLI,"Clients",FMTK)]))
    child(q, s, chart("linechart","Volume transactions par mois",
        [_dim("AnneeMois","Mois")],[_meas(VOL_TX,"Volume",FMTN)]))
    child(q, s, tbl("Détail clients",
        [_dim("nom_cplt","Client"),_dim("lib_cd_typ","Type"),
         _dim("agc_topz","Agence"),_dim("lib_pay_res","Pays"),
         _dim("lib_cd_risque_pers","Risque")],
        [_meas(AUM,"AUM",FMTN),_meas(EP_ENC,"Épargne",FMTN),_meas(CR_ENC,"Crédit",FMTN)]))
    for f,l in [("lib_cd_typ","Type client"),("agc_topz","Agence"),
                ("lib_pay_res","Pays"),("lib_gr","Groupe risque")]:
        child(q, s, filtre(f, l))

    # 2 — Digital & Adoption
    s = new_sheet(q, doc, "Digital & Adoption")
    for lbl, expr, fmt in [
        ("Nb Clients",         NB_CLI,                                              FMTK),
        ("Clients Enrôlés",    NB_ENROL,                                            FMTK),
        ("Taux Enrôlement",    ENROL_TX,                                            FMTP),
        ("Nb Smartphones",     "Sum(nb_dev_enrol)",                                 FMTK),
        ("Comptes Bloqués",    "Count(DISTINCT {<etat_acc={'B'}>} id_cli)",         FMTK),
        ("Comptes Suspendus",  "Count(DISTINCT {<etat_acc={'S'}>} id_cli)",         FMTK),
    ]:
        child(q, s, kpi(lbl, expr, fmt))
    child(q, s, chart("piechart","Transactions par canal",
        [_dim("TR_canal_ordre","Canal")],[_meas("Count(TR_mnt_evt)","Transactions",FMTK)]))
    child(q, s, chart("linechart","Volume transactions / mois",
        [_dim("AnneeMois","Mois")],[_meas(VOL_TX,"Volume",FMTN)]))
    child(q, s, chart("barchart","Enrôlés par type",
        [_dim("typ_enrol","Type")],[_meas(NB_ENROL,"Enrôlés",FMTK)]))
    child(q, s, tbl("Clients à surveiller",
        [_dim("nom_cplt","Client"),_dim("etat_acc","État accès"),
         _dim("typ_enrol","Type enrôl."),_dim("agc_topz","Agence")],
        [_meas("Sum(nb_dev_enrol)","Appareils",FMTK)]))
    for f,l in [("lib_cd_typ","Type"),("agc_topz","Agence"),
                ("etat_acc","État accès"),("typ_enrol","Type enrôlement")]:
        child(q, s, filtre(f, l))

    # 3 — Risque & Conformité
    s = new_sheet(q, doc, "Risque & Conformité")
    for lbl, expr, fmt in [
        ("Clients Sensibles",  SENSIB,                                                    FMTK),
        ("KYC Rouge",          "Count(DISTINCT {<gelule_global={10}>} id_cli)",           FMTK),
        ("KYC Orange",         "Count(DISTINCT {<gelule_global={5}>} id_cli)",            FMTK),
        ("Tx Sensibles",       "Sum({<TR_Transaction_Sensible={1}>} 1)",                  FMTK),
        ("Vol. Tx Sensibles",  "Sum({<TR_Transaction_Sensible={1}>} TR_mnt_evt)",         FMTN),
        ("Conformité KYC",     KYC_TX,                                                    FMTP),
    ]:
        child(q, s, kpi(lbl, expr, fmt))
    child(q, s, chart("barchart","Clients par niveau risque",
        [_dim("lib_cd_risque_pers","Risque")],[_meas(NB_CLI,"Clients",FMTK)]))
    child(q, s, chart("barchart","Volume tx par couleur pays",
        [_dim("TR_ctrpty_couleur_pays","Couleur pays")],[_meas(VOL_TX,"Volume",FMTN)]))
    child(q, s, chart("barchart","Volume sensible par opération",
        [_dim("TR_lib_evt_lv1","Opération")],
        [_meas("Sum({<TR_Transaction_Sensible={1}>} TR_mnt_evt)","Vol. sensible",FMTN)]))
    child(q, s, tbl("Clients à risque",
        [_dim("nom_cplt","Client"),_dim("lib_cd_risque_pers","Risque"),
         _dim("couleur_pays","Pays couleur"),_dim("agc_topz","Agence")],
        [_meas("Max(gelule_global)","KYC",FMTK),_meas(AUM,"AUM",FMTN)]))
    for f,l in [("lib_cd_typ","Type"),("agc_topz","Agence"),
                ("lib_cd_risque_pers","Niveau risque"),("couleur_pays","Couleur pays")]:
        child(q, s, filtre(f, l))

    # 4 — Commercial & Relation Client
    s = new_sheet(q, doc, "Commercial & Relation Client")
    for lbl, expr, fmt in [
        ("Clients Actifs",  NB_ACT,                                          FMTK),
        ("Prospects",       "Count(DISTINCT {<cli_c_p={'PR'}>} id_cli)",     FMTK),
        ("AUM Total",       AUM,                                             FMTN),
        ("AUM Moyen",       f"{AUM} / {NB_CLI}",                            FMTN),
        ("Taux Actifs",     ACT_TX,                                          FMTP),
        ("Nb Clients",      NB_CLI,                                          FMTK),
    ]:
        child(q, s, kpi(lbl, expr, fmt))
    child(q, s, chart("barchart","Clients par type › groupe",
        [_dim("lib_cd_typ","Type"),_dim("lib_gr","Groupe")],
        [_meas(NB_CLI,"Clients",FMTK)]))
    child(q, s, chart("combochart","AUM & taux actifs par agence",
        [_dim("agc_topz","Agence")],
        [_meas(AUM,"AUM",FMTN),_meas(ACT_TX,"Taux actifs",FMTP)]))
    child(q, s, chart("treemap","Clients par groupe risque",
        [_dim("lib_gr","Groupe")],[_meas(NB_CLI,"Clients",FMTK)]))
    child(q, s, tbl("Portefeuille par conseiller",
        [_dim("nom_cplt","Client"),_dim("lib_cd_typ","Type"),
         _dim("nom_cons","Conseiller"),_dim("agc_topz","Agence"),
         _dim("top_client_actif","Actif")],
        [_meas(AUM,"AUM",FMTN)]))
    for f,l in [("lib_cd_typ","Type client"),("agc_topz","Agence"),
                ("lib_gr","Groupe risque"),("top_client_actif","Actif O/N")]:
        child(q, s, filtre(f, l))

    # 5 — Patrimoine — Épargne & Crédit
    s = new_sheet(q, doc, "Patrimoine — Épargne & Crédit")
    for lbl, expr, fmt in [
        ("Encours Épargne", EP_ENC,  FMTN),
        ("Collecte Brute",  COL_BRT, FMTN),
        ("Décollecte",      DECOL,   FMTN),
        ("Collecte Nette",  COL_NET, FMTN),
        ("Encours Crédit",  CR_ENC,  FMTN),
        ("Capital Impayé",  CAP_IMP, FMTN),
    ]:
        child(q, s, kpi(lbl, expr, fmt))
    child(q, s, chart("barchart","Épargne par famille › fonds",
        [_dim("EP_fam_pdt","Famille"),_dim("EP_lib_fds","Fonds")],
        [_meas(EP_ENC,"Encours",FMTN)]))
    child(q, s, chart("waterfallchart","Cascade collecte nette",
        [_dim("EP_fam_pdt","Famille")],[_meas(COL_NET,"Collecte nette",FMTN)]))
    child(q, s, chart("barchart","Crédit par marché",
        [_dim("CR_Lib_Marche_Simple","Marché")],[_meas(CR_ENC,"Encours",FMTN)]))
    child(q, s, tbl("Fonds — encours",
        [_dim("EP_lib_fds","Fonds"),_dim("EP_fam_pdt","Famille"),
         _dim("EP_lib_mod_gest","Gestion")],
        [_meas("Sum(EP_enc_fds_m)","Encours fonds",FMTN)]))
    for f,l in [("lib_cd_typ","Type"),("agc_topz","Agence"),
                ("EP_fam_pdt","Famille produit"),("EP_lib_mod_gest","Mode gestion")]:
        child(q, s, filtre(f, l))

    # 6 — Crédit & Engagements
    s = new_sheet(q, doc, "Crédit & Engagements")
    for lbl, expr, fmt in [
        ("Encours Crédit",   CR_ENC,                    FMTN),
        ("Nb Crédits",       "Count(DISTINCT num_cnt)", FMTK),
        ("Montant Débloqué", "Sum(CR_mnt_dblq)",        FMTN),
        ("Capital Impayé",   CAP_IMP,                   FMTN),
        ("Taux Impayés",     IMP_TX,                    FMTP),
        ("Couverture Gar.",  COV_TX,                    FMTP),
    ]:
        child(q, s, kpi(lbl, expr, fmt))
    child(q, s, chart("barchart","Encours par type › marché",
        [_dim("CR_lib_typ_prt","Type prêt"),_dim("CR_lib_typ_mar","Marché")],
        [_meas(CR_ENC,"Encours",FMTN)]))
    child(q, s, chart("combochart","Encours & taux impayés par marché",
        [_dim("CR_lib_typ_mar","Marché")],
        [_meas(CR_ENC,"Encours",FMTN),_meas(IMP_TX,"Taux impayés",FMTP)]))
    child(q, s, chart("piechart","Répartition IFRS9",
        [_dim("CR_Lib_Bucket_Credit","Bucket")],[_meas(CR_ENC,"Encours",FMTN)]))
    child(q, s, tbl("Détail crédits",
        [_dim("CR_lib_typ_prt","Type prêt"),_dim("CR_lib_typ_mar","Marché"),
         _dim("CR_lib_cd_etat_creance","État")],
        [_meas("Sum(CR_mnt_nom)","Nominal",FMTN),
         _meas(CR_ENC,"Encours",FMTN),
         _meas("Avg({<CR_ltv_act={'>0'}>} CR_ltv_act)","LTV moy.",FMTP),
         _meas(PROV,"Provisions",FMTN),
         _meas("Sum(GA_mnt_gar)","Garanties",FMTN)]))
    for f,l in [("lib_cd_typ","Type"),("agc_topz","Agence"),
                ("CR_lib_typ_mar","Marché"),("CR_lib_cd_etat_creance","État créance")]:
        child(q, s, filtre(f, l))

    # 7 — Analyse Avancée 360°
    s = new_sheet(q, doc, "Analyse Avancée 360°")
    child(q, s, {
        "qInfo": {"qType": "pivot-table"}, "visualization": "pivot-table",
        "title": "Croisé AUM par type × groupe", "showTitles": True,
        "qHyperCubeDef": {
            "qDimensions": [_dim("lib_cd_typ","Type"),_dim("lib_gr","Groupe")],
            "qMeasures": [_meas(AUM,"AUM",FMTN)],
            "qMode": "P",
            "qInitialDataFetch": [{"qTop":0,"qLeft":0,"qHeight":50,"qWidth":20}]
        }
    })
    child(q, s, {
        "qInfo": {"qType": "scatterplot"}, "visualization": "scatterplot",
        "title": "Clients : AUM vs Épargne (taille = Crédit)", "showTitles": True,
        "qHyperCubeDef": {
            "qDimensions": [_dim("nom_cplt","Client")],
            "qMeasures": [_meas(AUM,"AUM",FMTN),
                          _meas(EP_ENC,"Épargne",FMTN),
                          _meas(CR_ENC,"Crédit (taille)",FMTN)],
            "qMode": "S",
            "qInitialDataFetch": [{"qTop":0,"qLeft":0,"qHeight":500,"qWidth":10}]
        }
    })
    child(q, s, kpi("Conformité KYC", KYC_TX, FMTP))
    child(q, s, chart("waterfallchart","Cascade collecte nette / famille",
        [_dim("EP_fam_pdt","Famille")],[_meas(COL_NET,"Collecte nette",FMTN)]))
    child(q, s, chart("barchart","Volume par opération & canal",
        [_dim("TR_lib_evt_lv1","Opération"),_dim("TR_canal_ordre","Canal")],
        [_meas(VOL_TX,"Volume",FMTN)]))
    child(q, s, chart("barchart","Entonnoir — clients par risque",
        [_dim("lib_cd_risque_pers","Risque")],[_meas(NB_CLI,"Clients",FMTK)]))
    for f,l in [("lib_cd_typ","Type"),("agc_topz","Agence"),
                ("lib_pay_res","Pays"),("lib_cd_risque_pers","Risque")]:
        child(q, s, filtre(f, l))

    print("  7 feuilles créées.")


# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    print("[1/3] Lecture du script QVS...")
    script = local_script()

    # Supprimer app précédente si présente
    existing = os.path.join(APPS_DIR, f"{APP_NAME}.qvf")
    if os.path.exists(existing):
        os.remove(existing)
        print(f"  App précédente supprimée.")

    print(f"[2/3] Connexion au moteur ({ENGINE_URL})...")
    try:
        g = Engine(ENGINE_URL)
    except Exception as e:
        sys.exit(f"[ERR] Connexion impossible : {e}")

    # Créer l'app
    print(f"  CreateApp '{APP_NAME}'...")
    try:
        r = g.call(-1, "CreateApp", [APP_NAME])
        app_id = r["result"]["qAppId"]
        print(f"  App ID : {app_id}")
    except Exception as e:
        sys.exit(f"[ERR] CreateApp : {e}")

    # Ouvrir l'app dans la même connexion
    r = g.call(-1, "OpenDoc", [app_id])
    doc = r["result"]["qReturn"]["qHandle"]
    print(f"  Doc handle : {doc}")

    # Créer la connexion dossier DataFiles
    create_connection(g, doc)

    # Injecter le script
    print("  SetScript...")
    g.call(doc, "SetScript", [script])

    # Reload
    print("  DoReload (30-90 s)...")
    r = g.call(doc, "DoReload", [0, False, False], timeout=300)
    ok = r.get("result", {}).get("qReturn", False)
    print(f"  Reload : {'[OK]' if ok else '[ECHEC]'}")
    if not ok:
        try:
            log_r = g.call(doc, "GetReloadLog")
            tail = log_r.get("result", {}).get("qReturn", "")[-2000:]
            print("  --- RELOAD LOG (fin) ---")
            print(tail.encode("ascii", errors="replace").decode())
            print("  --- FIN LOG ---")
        except Exception:
            pass

    # Feuilles
    create_sheets(g, doc)

    # Sauvegarde
    print("\n  DoSave...")
    g.call(doc, "DoSave")
    g.close()

    # Copie dans le dossier du projet
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "LoBP_CustomerIntent.qvf")
    if os.path.exists(existing):
        shutil.copy2(existing, dst)
        print(f"\n[OK] Copie dans : {dst}")
    else:
        for f in os.listdir(APPS_DIR):
            if f.endswith(".qvf"):
                shutil.copy2(os.path.join(APPS_DIR, f), dst)
                print(f"\n[OK] Copie ({f}) -> {dst}")
                break

    print(f"\n  Ouvrir dans Qlik Sense Desktop : {APP_NAME}")
    print(f"  Importer dans Qlik Cloud       : Accueil -> Creer -> Importer")


if __name__ == "__main__":
    main()
