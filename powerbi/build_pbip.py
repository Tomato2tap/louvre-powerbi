"""
Génère un dossier PBIP (Power BI Project) complet :
  LoBP_Dashboard.pbip               ← entrée
  LoBP_Dashboard.Dataset/           ← modèle de données
    .platform
    definition.pbidataset
    model.bim                        ← tables, relations, mesures (JSON)
  LoBP_Dashboard.Report/            ← rapport
    .platform
    definition.pbr                  ← pages + visuels (JSON)
"""

import json, os, uuid

ROOT    = r"E:\louvre\powerbi\LoBP_Dashboard"
DATA    = r"E:\louvre\powerbi\data"
DS_DIR  = ROOT + ".Dataset"
RPT_DIR = ROOT + ".Report"
PBIP    = ROOT + ".pbip"

os.makedirs(DS_DIR, exist_ok=True)
os.makedirs(RPT_DIR, exist_ok=True)

def w(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content if isinstance(content, str) else json.dumps(content, ensure_ascii=False, indent=2))

# ─── Couleurs LoBP ────────────────────────────────────────────────────────────
BORDEAUX = "#8B1F2A"
ROUGE    = "#C9453A"
FOND     = "#F4F2EE"
BLANC    = "#FFFFFF"
TEXTE    = "#2C2C2C"
GRIS     = "#666666"
ALERTE_R = "#C0392B"
ALERTE_O = "#E67E22"

# ─── .pbip entry point ────────────────────────────────────────────────────────
w(PBIP, {
    "version": "1.0",
    "artifacts": [{"report": {"path": "LoBP_Dashboard.Report"}}],
    "settings": {"enableTmdlSave": False, "enableTmdlLoad": False}
})

# ─── Dataset .platform ────────────────────────────────────────────────────────
w(f"{DS_DIR}/.platform", {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
    "metadata": {"type": "SemanticModel", "displayName": "LoBP_Dashboard"},
    "config": {"version": "2.0", "logicalId": str(uuid.uuid4())}
})

w(f"{DS_DIR}/definition.pbidataset", {"version": "1.0", "settings": {}})

# ─── M queries pour chaque table ─────────────────────────────────────────────
def m_csv(table):
    path = f"{DATA}\\{table}.csv".replace("\\", "\\\\")
    return [
        "let",
        f'    Source = Csv.Document(File.Contents("{path}"),[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),',
        '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
        '    #"Changed Types" = Table.TransformColumnTypes(#"Promoted Headers",',
        '        {',
        '            {"id_cli", type text}',
        '        })',
        'in',
        '    #"Changed Types"'
    ]

# ─── Colonnes par table (essentielles) ───────────────────────────────────────
def col(name, dt="string", sumby="none"):
    return {"type": "calculated" if False else "data",
            "name": name, "dataType": dt,
            "lineageTag": str(uuid.uuid4()),
            "summarizeBy": sumby,
            "sourceColumn": name,
            "annotations": [{"name": "SummarizationSetBy", "value": "Automatic"}]}

def num_col(name):  return col(name, "double", "sum")
def int_col(name):  return col(name, "int64",  "sum")
def date_col(name): return col(name, "dateTime", "none")
def bool_col(name): return col(name, "boolean", "none")

CLIENT_COLS = [
    col("id_cli"), col("cd_typ"), col("lib_cd_typ"), col("id_gr"), col("lib_gr"),
    col("cli_c_p"), col("nom_cplt"), col("prm_prn"), col("nom_us"),
    int_col("age_cli"), col("cd_situ_fam"), col("lib_cd_situ_fam"),
    col("cd_cons"), col("nom_cons"), col("lib_ptf"), col("agc_topz"), col("lib_grp_agce"),
    col("etat_acc"), col("top_client_actif"),
    date_col("dt_der_cnx"), date_col("dt_top_cl"), date_col("dt_exit_cl"),
    date_col("dt_dernier_rdv"), date_col("dt_1er_cnt"),
    int_col("nb_dev_enrol"), col("typ_enrol"), date_col("dt_enrol"),
    col("cd_risque_pers"), col("lib_cd_risque_pers"), col("cd_risque_ajust"), col("lib_cd_risque_ajust"),
    num_col("tot_score_risque"), col("scenario_risque"), col("lib_scenario_risque"), col("cd_mf"),
    int_col("gelule_global"), col("lib_gelule_global"),
    date_col("dt_der_certif"), date_col("dt_next_certif"),
    col("lib_stt_fatca"), col("pay_fis_prin"),
    col("pay_res"), col("lib_pay_res"), col("couleur_pays"), col("niveau_risque_pays"),
    bool_col("top_pays_embargo"), bool_col("top_pays_sanctions"), bool_col("top_pays_gda"),
    col("cd_ficp"), int_col("nb_incidents_ficp"),
    num_col("aum_tit"), num_col("aum_cot"), num_col("mnt_pat_epargne"), num_col("mnt_pat_biens_immos"),
    num_col("mnt_rev_princ"), num_col("mnt_credits_externes"),
    num_col("mnt_equip_emp"), int_col("nb_equip_emp"), num_col("mnt_equip_tit"), int_col("nb_equip_tit"),
    col("list_fam_pdt"), col("list_pdt"),
    date_col("dt_fonc"), col("annee_mois_part"),
    col("Couleur_KYC"), col("Alerte_Certif"),
]

TXN_COLS = [
    col("id_cli"), col("num_cnt"), col("perimetre"),
    col("typ_evt"), col("typ_evt_lv1"), col("lib_evt_lv1"),
    col("sens"), num_col("mnt_evt"), col("devise_compte"), num_col("mnt_devise"),
    date_col("dt_demande"), date_col("dt_validation"), date_col("dt_realisation"),
    col("mode_paiement"), col("typ_paiement"),
    int_col("ind_3ds"), int_col("ind_sans_contact"),
    col("canal_init"), col("canal_ordre"),
    col("ctrpty_nom"), col("ctrpty_pays"),
    col("cli_cd_pays_iso"), col("cli_couleur_pays"), col("cli_niveau_risque_pays"),
    bool_col("cli_top_pays_embargo"), bool_col("cli_top_pays_sanctions"), bool_col("cli_top_pays_gda"),
    col("ctrpty_cd_pays_iso"), col("ctrpty_couleur_pays"), col("ctrpty_niveau_risque_pays"),
    bool_col("ctrpty_top_pays_embargo"), bool_col("ctrpty_top_pays_sanctions"), bool_col("ctrpty_top_pays_gda"),
    bool_col("Transaction_Sensible"), col("annee_mois_part"),
]

EPARGNE_COLS = [
    col("id_cli"), col("num_cnt"), col("stt_cli"), col("fam_pdt"), col("perimetre"),
    col("lib_ctl"), col("lib_fam_niv3_pdt"), col("stt_cnt"), col("lib_stt_cnt"),
    date_col("dt_eff"), date_col("dt_fin_eff"),
    col("mod_gest"), col("lib_mod_gest"), col("cd_ges"), col("lib_cd_ges"),
    num_col("enc_cnt_m"), num_col("enc_moy_m"), num_col("enc_cnt_m1"), num_col("enc_cnt_n1"), num_col("var_enc"),
    num_col("col_brute"), num_col("decollecte"), num_col("col_nette"),
    col("isin_fds"), col("lib_fds"), int_col("qte_fds"), num_col("enc_fds_m"),
    num_col("volatilite_isin"), int_col("isin_risq"),
    col("prof_risq"), col("lib_prof_risq"), col("prof_exp"), col("lib_prof_exp"), col("prof_sfdr"),
    num_col("mnt_tar_brt"), num_col("mnt_pdt_tar"), num_col("mnt_fdg"), num_col("mnt_ddg"), num_col("tx_int"),
    col("cd_bck_ifrs9"), col("cd_risque"), col("cd_etat_creance"),
    num_col("mnt_prov_b_ifrs9"), num_col("mnt_prov_hb_ifrs9"), num_col("mnt_psp"), num_col("total_rwa"),
    col("top_nanti"), num_col("mnt_nanti"), col("assur"),
    col("Lib_Bucket_IFRS9"), col("annee_mois_part"),
]

CREDIT_COLS = [
    col("id_cli"), col("num_cnt"), col("num_prj"), col("stt_cli"), col("fam_pdt"), col("perimetre"),
    col("lib_ctl"), col("stt_cnt"), col("lib_stt_cnt"), col("cd_etat_prt"), col("lib_cd_etat_prt"),
    col("typ_prt"), col("lib_typ_prt"), col("typ_mar"), col("lib_typ_mar"), col("typ_remb"), col("agc_cnt"),
    num_col("mnt_nom"), num_col("mnt_dblq"), num_col("mnt_disp"),
    num_col("enc_cpt"), num_col("enc_cpt_moy_m"), num_col("enc_gest"),
    num_col("mnt_krd_tot"), num_col("mnt_krd_sain"), num_col("mnt_krd_imp"),
    num_col("tx_int_ref"), num_col("tx_int_act"), num_col("teg"), col("typ_tx"),
    date_col("dt_eff"), date_col("dt_fin_eff"),
    int_col("mat_init"), int_col("duree_resi"),
    col("cd_bck_ifrs9"), col("cd_etat_creance"), col("lib_cd_etat_creance"),
    num_col("mnt_prov_b_ifrs9"), num_col("mnt_prov_hb_ifrs9"), num_col("mnt_psp"),
    num_col("total_rwa"), num_col("ead_nette_b"),
    num_col("mnt_bien_ori"), num_col("mnt_app"), num_col("ltv_ori"), num_col("ltv_act"),
    col("bien_commune"), col("bien_dpe"), num_col("tx_edt"), int_col("nb_rst"),
    col("Lib_Bucket_Credit"), col("Lib_Marche_Simple"), col("annee_mois_part"),
]

GARANTIE_COLS = [
    col("id_cli"), col("num_cnt"), col("num_cnt_gar"), col("stt_cli"),
    col("det_typ_gar"), col("lib_det_typ_gar"), col("stt_gar"), col("lib_stt_gar"),
    col("stt_cnt"), col("cd_rang"),
    date_col("dt_eff_gar"), date_col("dt_ech_gar"), int_col("dur_gar"),
    num_col("mnt_gar"), num_col("mnt_gar_cpta"), num_col("mnt_bien_gar_ori"), num_col("mnt_reval"),
    col("lib_cnt_ass"), col("nom_cie_ass"),
    col("lib_ville"), col("cd_postal"),
    num_col("tx_rwa"), num_col("mnt_rwa"), col("annee_mois_part"),
]

SERVICE_COLS = [
    col("id_cli"), col("num_cnt"), col("stt_cli"), col("fam_pdt"), col("perimetre"),
    col("lib_ctl"), col("stt_cnt"), col("lib_stt_cnt"),
    date_col("dt_eff"), date_col("dt_fin_eff"), col("agc_ins"),
    col("num_carte"), col("cd_typ_debit"), date_col("dt_ech_carte"), int_col("ind_carte_virtu"),
    num_col("mnt_tar_brt"), num_col("mnt_pdt_tar"),
    col("cd_bck_ifrs9"), num_col("mnt_prov_b_ifrs9"), num_col("mnt_prov_hb_ifrs9"),
    col("annee_mois_part"),
]

GSM_COLS = [
    col("isin_fds"), col("id_contrat"), date_col("dt_fonc"), col("cd_ges"), col("mod_gest"), col("reseau"),
    int_col("qte_fds"), num_col("cours_cot"), date_col("dt_cot"), num_col("avg_mnt_achat"),
    num_col("enc_fds_m"), num_col("enc_cnt_n_1"),
    num_col("sum_enc_fds_cnt"), num_col("poids_isin_cnt"),
    num_col("sum_enc_fds_profil"), num_col("poids_isin_profil"),
    num_col("sum_enc_fds_gsm"), num_col("poids_isin_total_gsm"),
    num_col("apport_cli"), num_col("performance_cli"), num_col("mnt_pmvl"),
    int_col("ind_sfdr_30000"), int_col("ind_sfdr_10000"), int_col("ind_sfdr_20150"),
    int_col("ind_taxo_20660"), int_col("ind_taxo_20670"),
    col("Classification_SFDR"),
]

# ─── Tables de mesures (DAX) ─────────────────────────────────────────────────
def measure(name, expr, fmt="", folder=""):
    m = {"name": name, "expression": expr, "lineageTag": str(uuid.uuid4())}
    if fmt:   m["formatString"] = fmt
    if folder: m["displayFolder"] = folder
    return m

MEASURES_CLIENTS = [
    measure("Nb Clients Totaux",
        "CALCULATE(DISTINCTCOUNT(CLIENT[id_cli]),CLIENT[cli_c_p] IN {\"CL\",\"CT\"})",
        "#,0", "Clients"),
    measure("Nb Prospects",
        "CALCULATE(DISTINCTCOUNT(CLIENT[id_cli]),CLIENT[cli_c_p]=\"PR\")",
        "#,0", "Clients"),
    measure("Nb Clients Actifs",
        "CALCULATE(DISTINCTCOUNT(CLIENT[id_cli]),CLIENT[top_client_actif]=\"O\")",
        "#,0", "Clients"),
    measure("Taux Clients Actifs",
        "DIVIDE([Nb Clients Actifs],[Nb Clients Totaux],0)",
        "0.0%", "Clients"),
    measure("AUM Total",
        "SUM(CLIENT[aum_tit])",
        "#,0 €", "Clients"),
    measure("AUM Moyen par Client",
        "DIVIDE([AUM Total],[Nb Clients Totaux],0)",
        "#,0 €", "Clients"),
    measure("Nb Clients sans RDV depuis 6 mois",
        "CALCULATE(DISTINCTCOUNT(CLIENT[id_cli]),CLIENT[dt_dernier_rdv]<EDATE(TODAY(),-6)||ISBLANK(CLIENT[dt_dernier_rdv]))",
        "#,0", "Clients"),
    measure("Nb Clients KYC Rouge",
        "CALCULATE(DISTINCTCOUNT(CLIENT[id_cli]),CLIENT[gelule_global]=10)",
        "#,0", "Conformité"),
    measure("Nb Clients KYC Orange",
        "CALCULATE(DISTINCTCOUNT(CLIENT[id_cli]),CLIENT[gelule_global]=5)",
        "#,0", "Conformité"),
    measure("Nb Clients KYC Vert",
        "CALCULATE(DISTINCTCOUNT(CLIENT[id_cli]),CLIENT[gelule_global]=0)",
        "#,0", "Conformité"),
    measure("Taux Conformité KYC",
        "DIVIDE([Nb Clients KYC Vert],[Nb Clients Totaux],0)",
        "0.0%", "Conformité"),
    measure("Nb Certifications à Renouveler",
        "CALCULATE(DISTINCTCOUNT(CLIENT[id_cli]),CLIENT[dt_next_certif]<=EDATE(TODAY(),3),NOT(ISBLANK(CLIENT[dt_next_certif])))",
        "#,0", "Conformité"),
    measure("Nb Clients Pays Embargo",
        "CALCULATE(DISTINCTCOUNT(CLIENT[id_cli]),CLIENT[top_pays_embargo]=TRUE())",
        "#,0", "Conformité"),
    measure("Nb Clients Pays Sanctions",
        "CALCULATE(DISTINCTCOUNT(CLIENT[id_cli]),CLIENT[top_pays_sanctions]=TRUE())",
        "#,0", "Conformité"),
    measure("Nb Clients Risque EF",
        "CALCULATE(DISTINCTCOUNT(CLIENT[id_cli]),CLIENT[cd_risque_pers] IN {\"E\",\"F\"})",
        "#,0", "Conformité"),
]

MEASURES_DIGITAL = [
    measure("Nb Clients Enrollés",
        "CALCULATE(DISTINCTCOUNT(CLIENT[id_cli]),CLIENT[nb_dev_enrol]>0)",
        "#,0", "Digital"),
    measure("Taux Enrollment",
        "DIVIDE([Nb Clients Enrollés],[Nb Clients Totaux],0)",
        "0.0%", "Digital"),
    measure("Nb Smartphones Total",
        "SUM(CLIENT[nb_dev_enrol])",
        "#,0", "Digital"),
    measure("Nb Comptes Bloqués",
        "CALCULATE(DISTINCTCOUNT(CLIENT[id_cli]),CLIENT[etat_acc]=\"B\")",
        "#,0", "Digital"),
    measure("Nb Comptes Suspendus",
        "CALCULATE(DISTINCTCOUNT(CLIENT[id_cli]),CLIENT[etat_acc]=\"S\")",
        "#,0", "Digital"),
    measure("Nb Transactions Web",
        "CALCULATE(COUNTROWS('TRANSACTION'),'TRANSACTION'[canal_ordre]=\"WEB\")",
        "#,0", "Digital"),
    measure("Nb Transactions Mobile",
        "CALCULATE(COUNTROWS('TRANSACTION'),'TRANSACTION'[canal_ordre]=\"MOBILE\")",
        "#,0", "Digital"),
]

MEASURES_EPARGNE = [
    measure("Encours Épargne",
        "CALCULATE(SUM(EPARGNE[enc_cnt_m]),EPARGNE[perimetre]=\"epargne\")",
        "#,0 €", "Épargne"),
    measure("Encours Épargne N-1",
        "CALCULATE(SUM(EPARGNE[enc_cnt_n1]),EPARGNE[perimetre]=\"epargne\")",
        "#,0 €", "Épargne"),
    measure("Variation Encours Épargne",
        "[Encours Épargne]-[Encours Épargne N-1]",
        "+#,0 €;-#,0 €", "Épargne"),
    measure("Collecte Brute",
        "CALCULATE(SUM(EPARGNE[col_brute]),EPARGNE[perimetre]=\"epargne\")",
        "#,0 €", "Épargne"),
    measure("Décollecte",
        "CALCULATE(SUM(EPARGNE[decollecte]),EPARGNE[perimetre]=\"epargne\")",
        "#,0 €", "Épargne"),
    measure("Collecte Nette",
        "[Collecte Brute]+[Décollecte]",
        "+#,0 €;-#,0 €", "Épargne"),
    measure("Nb Contrats Épargne",
        "CALCULATE(DISTINCTCOUNT(EPARGNE[num_cnt]),EPARGNE[perimetre]=\"epargne\",EPARGNE[stt_cnt]=\"0\")",
        "#,0", "Épargne"),
    measure("Performance Moyenne",
        "AVERAGEX(FILTER(GSM,GSM[performance_cli]<>BLANK()),GSM[performance_cli])",
        "0.00%", "Épargne"),
    measure("Encours Fonds Durables",
        "CALCULATE(SUM(GSM[enc_fds_m]),GSM[Classification_SFDR] IN {\"Article 8 (ESG)\",\"Article 9 (Impact)\"})",
        "#,0 €", "Épargne"),
    measure("Provision IFRS9 Épargne",
        "SUM(EPARGNE[mnt_prov_b_ifrs9])+SUM(EPARGNE[mnt_prov_hb_ifrs9])",
        "#,0 €", "Épargne"),
]

MEASURES_CREDIT = [
    measure("Encours Crédit Total",
        "SUM(CREDIT[enc_cpt])",
        "#,0 €", "Crédit"),
    measure("Nb Contrats Crédit",
        "CALCULATE(DISTINCTCOUNT(CREDIT[num_cnt]),CREDIT[stt_cnt]=\"0\")",
        "#,0", "Crédit"),
    measure("Nb Crédits Immobiliers",
        "CALCULATE(DISTINCTCOUNT(CREDIT[num_cnt]),CREDIT[typ_mar]=\"01\")",
        "#,0", "Crédit"),
    measure("Montant Nominal Total",
        "SUM(CREDIT[mnt_nom])",
        "#,0 €", "Crédit"),
    measure("Capital Sain",
        "SUM(CREDIT[mnt_krd_sain])",
        "#,0 €", "Crédit"),
    measure("Capital Impayé",
        "SUM(CREDIT[mnt_krd_imp])",
        "#,0 €", "Crédit"),
    measure("Taux Créances Douteuses",
        "DIVIDE(CALCULATE(SUM(CREDIT[mnt_krd_tot]),CREDIT[cd_etat_creance] IN {\"10\",\"30\"}),SUM(CREDIT[mnt_krd_tot]),0)",
        "0.00%", "Crédit"),
    measure("Provision IFRS9 Crédit",
        "SUM(CREDIT[mnt_prov_b_ifrs9])+SUM(CREDIT[mnt_prov_hb_ifrs9])",
        "#,0 €", "Crédit"),
    measure("RWA Crédit Total",
        "SUM(CREDIT[total_rwa])",
        "#,0 €", "Crédit"),
    measure("LTV Moyenne",
        "AVERAGEX(FILTER(CREDIT,CREDIT[ltv_act]<>BLANK()&&CREDIT[ltv_act]>0),CREDIT[ltv_act])",
        "0.0%", "Crédit"),
    measure("Montant Garanties",
        "SUM(GARANTIE[mnt_gar])",
        "#,0 €", "Crédit"),
    measure("Taux Couverture Garanties",
        "DIVIDE(SUM(GARANTIE[mnt_gar_cpta]),[Encours Crédit Total],0)",
        "0.0%", "Crédit"),
]

MEASURES_CONFORMITE = [
    measure("Volume Transactions Total",
        "SUM('TRANSACTION'[mnt_evt])",
        "#,0 €", "Conformité"),
    measure("Nb Transactions",
        "COUNTROWS('TRANSACTION')",
        "#,0", "Conformité"),
    measure("Nb Transactions Sensibles",
        "CALCULATE(COUNTROWS('TRANSACTION'),'TRANSACTION'[Transaction_Sensible]=TRUE())",
        "#,0", "Conformité"),
    measure("Volume Transactions Sensibles",
        "CALCULATE(SUM('TRANSACTION'[mnt_evt]),'TRANSACTION'[Transaction_Sensible]=TRUE())",
        "#,0 €", "Conformité"),
    measure("Volume Pays Embargo",
        "CALCULATE(SUM('TRANSACTION'[mnt_evt]),'TRANSACTION'[cli_top_pays_embargo]=TRUE()||'TRANSACTION'[ctrpty_top_pays_embargo]=TRUE())",
        "#,0 €", "Conformité"),
    measure("Volume Pays Sanctions",
        "CALCULATE(SUM('TRANSACTION'[mnt_evt]),'TRANSACTION'[ctrpty_top_pays_sanctions]=TRUE())",
        "#,0 €", "Conformité"),
    measure("Volume Pays GDA",
        "CALCULATE(SUM('TRANSACTION'[mnt_evt]),'TRANSACTION'[ctrpty_top_pays_gda]=TRUE())",
        "#,0 €", "Conformité"),
    measure("Nb Transactions 3DS",
        "CALCULATE(COUNTROWS('TRANSACTION'),'TRANSACTION'[ind_3ds]=1)",
        "#,0", "Conformité"),
    measure("Date Fonctionnelle",
        "\"Données au \" & FORMAT(MAX(CLIENT[dt_fonc]),\"DD/MM/YYYY\")",
        "", ""),
]

def make_measure_table(name, measures):
    return {
        "name": name,
        "lineageTag": str(uuid.uuid4()),
        "columns": [{"type": "rowNumber", "name": "RowNumber-2662979B-1795-4F74-8F37-6A1BA8059B61",
                     "dataType": "int64", "isHidden": True, "lineageTag": str(uuid.uuid4()),
                     "summarizeBy": "none", "annotations": [{"name": "SummarizationSetBy","value":"User"}]}],
        "partitions": [{"name": f"_{name}", "mode": "import",
                        "source": {"type": "m", "expression": "let Source = Table.FromRows({}) in Source"}}],
        "measures": measures,
        "isHidden": False
    }

def make_data_table(name, cols):
    return {
        "name": name,
        "lineageTag": str(uuid.uuid4()),
        "columns": cols,
        "partitions": [{
            "name": name,
            "mode": "import",
            "source": {"type": "m", "expression": m_csv(name)}
        }]
    }

# ─── Relations ────────────────────────────────────────────────────────────────
def rel(from_t, from_c, to_t, to_c, card="manyToOne", active=True):
    return {
        "name": f"{from_t}_{from_c}-{to_t}_{to_c}",
        "fromTable": from_t, "fromColumn": from_c,
        "toTable": to_t,   "toColumn": to_c,
        "joinOnDateBehavior": "datePartOnly",
        "crossFilteringBehavior": "singleDirection",
        "state": "active" if active else "inactive"
    }

# ─── model.bim ────────────────────────────────────────────────────────────────
model_bim = {
    "name": "Model",
    "compatibilityLevel": 1567,
    "model": {
        "culture": "fr-FR",
        "collation": "Latin1_General_100_BIN2_UTF8",
        "tables": [
            make_data_table("CLIENT",      CLIENT_COLS),
            make_data_table("TRANSACTION", TXN_COLS),
            make_data_table("EPARGNE",     EPARGNE_COLS),
            make_data_table("CREDIT",      CREDIT_COLS),
            make_data_table("GARANTIE",    GARANTIE_COLS),
            make_data_table("SERVICE",     SERVICE_COLS),
            make_data_table("GSM",         GSM_COLS),
            make_measure_table("_M_Clients",    MEASURES_CLIENTS),
            make_measure_table("_M_Digital",    MEASURES_DIGITAL),
            make_measure_table("_M_Epargne",    MEASURES_EPARGNE),
            make_measure_table("_M_Credit",     MEASURES_CREDIT),
            make_measure_table("_M_Conformite", MEASURES_CONFORMITE),
        ],
        "relationships": [
            rel("TRANSACTION", "id_cli",   "CLIENT",      "id_cli"),
            rel("EPARGNE",     "id_cli",   "CLIENT",      "id_cli"),
            rel("CREDIT",      "id_cli",   "CLIENT",      "id_cli"),
            rel("SERVICE",     "id_cli",   "CLIENT",      "id_cli"),
            rel("GARANTIE",    "id_cli",   "CLIENT",      "id_cli"),
            rel("GARANTIE",    "num_cnt",  "CREDIT",      "num_cnt"),
            rel("GSM",         "isin_fds", "EPARGNE",     "isin_fds"),
        ],
        "annotations": [
            {"name": "PBIDesktopVersion", "value": "2.154.0.0"},
            {"name": "_TM_ExtProp_PowerBITheme", "value": json.dumps({
                "name": "LoBP Theme",
                "dataColors": [BORDEAUX, "#C9453A", "#D4A04A", "#6B8FA8", "#8B5E3C", "#A8C5D8", "#F2C9A8", "#3D7E8A"],
                "background": FOND, "foreground": TEXTE,
                "tableAccent": BORDEAUX
            })}
        ]
    }
}

w(f"{DS_DIR}/model.bim", model_bim)
print("model.bim OK")

# ─── Report .platform ────────────────────────────────────────────────────────
w(f"{RPT_DIR}/.platform", {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
    "metadata": {"type": "Report", "displayName": "LoBP_Dashboard"},
    "config": {"version": "2.0", "logicalId": str(uuid.uuid4())}
})

# ─── Helpers visuels ─────────────────────────────────────────────────────────
def visual(vtype, x, y, w, h, title, **kwargs):
    cfg = {"singleVisual": {
        "visualType": vtype,
        "projections": kwargs.get("proj", {}),
        "vcObjects": {
            "title": [{"properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                "fontColor": {"solid": {"color": kwargs.get("title_color", TEXTE)}},
                "fontSize": {"expr": {"Literal": {"Value": "13D"}}}
            }}],
            "background": [{"properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "fillColor": {"solid": {"color": kwargs.get("bg", BLANC)}},
                "transparency": {"expr": {"Literal": {"Value": "0D"}}}
            }}]
        }
    }}
    if "color" in kwargs:
        cfg["singleVisual"]["vcObjects"]["dataPoint"] = [{"properties": {
            "defaultColor": {"solid": {"color": kwargs["color"]}}}}]
    return {
        "config": json.dumps(cfg),
        "filters": "[]",
        "query": json.dumps({"Version": 2, "From": [], "Select": []}),
        "dataTransforms": json.dumps({}),
        "width": w, "height": h, "x": x, "y": y,
        "z": 1000
    }

def kpi(x, y, w, h, title, table, measure, bg=BLANC):
    return visual("card", x, y, w, h, title,
        proj={"Values": [{"queryRef": f"{table}.{measure}"}]},
        bg=bg, title_color=GRIS, color=BORDEAUX)

def bar(x, y, w, h, title, dim_tbl, dim_fld, mea_tbl, mea):
    return visual("barChart", x, y, w, h, title,
        proj={"Category": [{"queryRef": f"{dim_tbl}.{dim_fld}"}],
              "Y": [{"queryRef": f"{mea_tbl}.{mea}"}]},
        color=BORDEAUX)

def donut(x, y, w, h, title, dim_tbl, dim_fld, mea_tbl, mea):
    return visual("donutChart", x, y, w, h, title,
        proj={"Category": [{"queryRef": f"{dim_tbl}.{dim_fld}"}],
              "Y": [{"queryRef": f"{mea_tbl}.{mea}"}]})

def line(x, y, w, h, title, dim_tbl, dim_fld, mea_tbl, mea):
    return visual("lineChart", x, y, w, h, title,
        proj={"Category": [{"queryRef": f"{dim_tbl}.{dim_fld}"}],
              "Y": [{"queryRef": f"{mea_tbl}.{mea}"}]},
        color=BORDEAUX)

def tbl(x, y, w, h, title, cols):
    return visual("tableEx", x, y, w, h, title,
        proj={"Values": [{"queryRef": f"{t}.{c}"} for t,c in cols]})

def slicer(x, y, w, h, title, tbl_n, fld):
    return visual("slicer", x, y, w, h, title,
        proj={"Values": [{"queryRef": f"{tbl_n}.{fld}"}]})

def scatter(x, y, w, h, title):
    return visual("scatterChart", x, y, w, h, title,
        proj={"Details": [{"queryRef": "CLIENT.nom_cplt"}],
              "X": [{"queryRef": "CLIENT.cd_risque_pers"}],
              "Y": [{"queryRef": "_M_Clients.AUM Moyen par Client"}],
              "Size": [{"queryRef": "_M_Epargne.Encours Épargne"}]},
        color=BORDEAUX)

def page(name, disp, containers, bg=FOND):
    return {
        "name": name,
        "displayName": disp,
        "displayOption": 1,
        "height": 768, "width": 1366,
        "config": json.dumps({
            "relationships": [],
            "background": {"color": {"solid": {"color": bg}}, "transparency": 0}
        }),
        "filters": "[]",
        "ordinal": 0,
        "visualContainers": [json.dumps(c) for c in containers]
    }

# ─── Pages ────────────────────────────────────────────────────────────────────
pages = [

  page("Accueil", "Accueil", [
    kpi(20, 20, 300, 60, "Louvre Banque Privée — Tableau de Bord", "_M_Conformite","Date Fonctionnelle", bg=BORDEAUX),
    kpi(20,100,300,90,"Clients Totaux",    "_M_Clients","Nb Clients Totaux"),
    kpi(330,100,300,90,"AUM Total",        "_M_Clients","AUM Total"),
    kpi(640,100,300,90,"Encours Épargne",  "_M_Epargne","Encours Épargne"),
    kpi(950,100,300,90,"Encours Crédit",   "_M_Credit","Encours Crédit Total"),
    kpi(20,210,300,90,"KYC Rouge",         "_M_Clients","Nb Clients KYC Rouge", bg="#FEE2E2"),
    kpi(330,210,300,90,"Transactions Sensibles","_M_Conformite","Nb Transactions Sensibles",bg="#FEE2E2"),
    kpi(640,210,300,90,"Taux Enrollment",  "_M_Digital","Taux Enrollment"),
    kpi(950,210,300,90,"Certif. à renouveler","_M_Clients","Nb Certifications à Renouveler",bg="#FEF9C3"),
  ]),

  page("Digital", "Suivi Digital", [
    kpi(10,10,240,80,"Clients Totaux",     "_M_Clients","Nb Clients Totaux"),
    kpi(260,10,240,80,"Clients Enrollés",  "_M_Digital","Nb Clients Enrollés"),
    kpi(510,10,240,80,"Smartphones",       "_M_Digital","Nb Smartphones Total"),
    kpi(760,10,240,80,"Taux Enrollment",   "_M_Digital","Taux Enrollment"),
    kpi(1010,10,336,80,"Comptes Bloqués",  "_M_Digital","Nb Comptes Bloqués", bg="#FEE2E2"),
    kpi(10,100,240,70,"Tx Web",    "_M_Digital","Nb Transactions Web"),
    kpi(260,100,240,70,"Tx Mobile","_M_Digital","Nb Transactions Mobile"),
    kpi(510,100,240,70,"KYC Rouge","_M_Clients","Nb Clients KYC Rouge", bg="#FEE2E2"),
    kpi(760,100,240,70,"Clients Actifs","_M_Clients","Nb Clients Actifs"),
    kpi(1010,100,336,70,"Taux Actifs","_M_Clients","Taux Clients Actifs"),
    line(10,180,640,230,"Évolution Enrollements par Date","CLIENT","dt_enrol","_M_Digital","Nb Clients Enrollés"),
    donut(660,180,370,230,"Répartition Canaux","TRANSACTION","canal_ordre","_M_Conformite","Nb Transactions"),
    slicer(1040,180,316,90,"État Accès","CLIENT","etat_acc"),
    slicer(1040,280,316,90,"Type Enrollment","CLIENT","typ_enrol"),
    slicer(1040,380,316,90,"Périmètre Client","CLIENT","cli_c_p"),
    slicer(1040,480,316,110,"Date Enrollment","CLIENT","dt_enrol"),
    tbl(10,420,1336,330,"Clients à surveiller (bloqués / sans connexion récente)",[
        ("CLIENT","nom_cplt"),("CLIENT","etat_acc"),("CLIENT","nb_dev_enrol"),
        ("CLIENT","dt_der_cnx"),("CLIENT","agc_topz"),("CLIENT","lib_cd_risque_pers")]),
  ]),

  page("Produits", "Portefeuille Produits", [
    kpi(10,10,210,80,"Nb Cartes",         "_M_Digital","Nb Comptes Bloqués"),
    kpi(230,10,210,80,"Encours Épargne",  "_M_Epargne","Encours Épargne"),
    kpi(450,10,210,80,"Collecte Nette",   "_M_Epargne","Collecte Nette"),
    kpi(670,10,210,80,"Encours Crédit",   "_M_Credit","Encours Crédit Total"),
    kpi(890,10,210,80,"Nb Contrats Crédit","_M_Credit","Nb Contrats Crédit"),
    kpi(1110,10,236,80,"Nb Contrats Épargne","_M_Epargne","Nb Contrats Épargne"),
    bar(10,100,420,220,"Encours Épargne par Famille Produit","EPARGNE","fam_pdt","_M_Epargne","Encours Épargne"),
    bar(440,100,420,220,"Encours Crédit par Type de Marché","CREDIT","Lib_Marche_Simple","_M_Credit","Encours Crédit Total"),
    donut(870,100,476,220,"Répartition Bucket IFRS9 Crédit","CREDIT","Lib_Bucket_Credit","_M_Credit","Encours Crédit Total"),
    bar(10,330,420,200,"Collecte vs Décollecte","EPARGNE","fam_pdt","_M_Epargne","Collecte Brute"),
    donut(440,330,320,200,"Épargne Durable (SFDR)","GSM","Classification_SFDR","_M_Epargne","Encours Épargne"),
    kpi(770,330,290,90,"Provision IFRS9 Crédit","_M_Credit","Provision IFRS9 Crédit",bg="#FEF9C3"),
    kpi(1070,330,276,90,"Taux Créances Douteuses","_M_Credit","Taux Créances Douteuses",bg="#FEE2E2"),
    tbl(10,540,1336,218,"Top Fonds par Encours",[
        ("EPARGNE","lib_fds"),("EPARGNE","fam_pdt"),("EPARGNE","enc_fds_m"),
        ("EPARGNE","Lib_Bucket_IFRS9"),("EPARGNE","isin_risq"),("GSM","Classification_SFDR")]),
  ]),

  page("Conformite", "Risque & Conformité", [
    kpi(10,10,250,80,"Clients Pays Embargo","_M_Clients","Nb Clients Pays Embargo",bg="#FEE2E2"),
    kpi(270,10,250,80,"Tx Sensibles","_M_Conformite","Nb Transactions Sensibles",bg="#FEE2E2"),
    kpi(530,10,250,80,"Vol. Pays GDA","_M_Conformite","Volume Pays GDA",bg="#FEE2E2"),
    kpi(790,10,250,80,"KYC Rouge","_M_Clients","Nb Clients KYC Rouge",bg="#FEE2E2"),
    kpi(1050,10,296,80,"Certif. Échues","_M_Clients","Nb Certifications à Renouveler",bg="#FEF9C3"),
    bar(10,100,430,220,"Volume par Type Événement","TRANSACTION","lib_evt_lv1","_M_Conformite","Volume Transactions Total"),
    bar(450,100,430,220,"Transactions par Couleur Pays","TRANSACTION","ctrpty_couleur_pays","_M_Conformite","Nb Transactions"),
    donut(890,100,456,220,"Risque Client","CLIENT","lib_cd_risque_pers","_M_Clients","Nb Clients Totaux"),
    bar(10,330,430,190,"Clients par Pays de Résidence (couleur)","CLIENT","couleur_pays","_M_Clients","Nb Clients Totaux"),
    bar(450,330,430,190,"Volume par Canal","TRANSACTION","canal_ordre","_M_Conformite","Volume Transactions Total"),
    kpi(890,330,220,85,"Vol. Embargo","_M_Conformite","Volume Pays Embargo",bg="#FEE2E2"),
    kpi(1120,330,226,85,"Vol. Sanctions","_M_Conformite","Volume Pays Sanctions",bg="#FEE2E2"),
    kpi(890,425,220,85,"Nb Tx 3DS","_M_Conformite","Nb Transactions 3DS"),
    tbl(10,530,1336,228,"Transactions Sensibles (pays à risque)",[
        ("CLIENT","nom_cplt"),("TRANSACTION","mnt_evt"),("TRANSACTION","dt_realisation"),
        ("TRANSACTION","cli_couleur_pays"),("TRANSACTION","ctrpty_pays"),
        ("TRANSACTION","ctrpty_couleur_pays"),("TRANSACTION","lib_evt_lv1"),("TRANSACTION","canal_ordre")]),
  ]),

  page("Commercial", "Commercial & Clients", [
    kpi(10,10,250,80,"Clients Actifs","_M_Clients","Nb Clients Actifs"),
    kpi(270,10,250,80,"Prospects","_M_Clients","Nb Prospects"),
    kpi(530,10,250,80,"AUM Moyen/Client","_M_Clients","AUM Moyen par Client"),
    kpi(790,10,250,80,"Sans RDV >6 mois","_M_Clients","Nb Clients sans RDV depuis 6 mois",bg="#FEF9C3"),
    kpi(1050,10,296,80,"Taux Clients Actifs","_M_Clients","Taux Clients Actifs"),
    bar(10,100,400,210,"Clients par Type","CLIENT","lib_cd_typ","_M_Clients","Nb Clients Totaux"),
    scatter(420,100,500,210,"Risque vs AUM (taille=Épargne)"),
    bar(930,100,416,210,"AUM par Groupe Risque","CLIENT","lib_gr","_M_Clients","AUM Total"),
    bar(10,320,400,200,"Taux Pénétration Produit","EPARGNE","fam_pdt","_M_Epargne","Nb Contrats Épargne"),
    donut(420,320,310,200,"Statut KYC","CLIENT","Couleur_KYC","_M_Clients","Nb Clients Totaux"),
    bar(740,320,606,200,"Clients par Agence","CLIENT","agc_topz","_M_Clients","Nb Clients Totaux"),
    tbl(10,530,1336,228,"Portefeuille Clients — Trié par AUM",[
        ("CLIENT","nom_cplt"),("CLIENT","lib_cd_typ"),("CLIENT","aum_tit"),
        ("CLIENT","lib_cd_risque_pers"),("CLIENT","dt_dernier_rdv"),
        ("CLIENT","Couleur_KYC"),("CLIENT","top_client_actif"),("CLIENT","agc_topz")]),
  ]),
]

# ─── definition.pbr ──────────────────────────────────────────────────────────
report_def = {
    "id": 0,
    "resourcePackages": [],
    "config": json.dumps({
        "version": "5.47",
        "activeSectionIndex": 0,
        "defaultDrillFilterOtherVisuals": True,
        "themeCollection": {"baseTheme": {"name": "CY24SU05", "version": "5.47", "type": 2}},
    }),
    "sections": []
}

for i, p in enumerate(pages):
    p["ordinal"] = i
    report_def["sections"].append(p)

w(f"{RPT_DIR}/definition.pbr", report_def)
print("definition.pbr OK")

# ─── Résumé ───────────────────────────────────────────────────────────────────
print()
print("=== DOSSIER PBIP GÉNÉRÉ ===")
print(f"Ouvrir dans Power BI Desktop : {PBIP}")
print()
print("Contenu :")
for dirpath, dirs, files in os.walk(ROOT + ".Dataset"):
    for f2 in files: print(f"  {os.path.relpath(os.path.join(dirpath,f2), ROOT+'.Dataset')} ({os.path.getsize(os.path.join(dirpath,f2))//1024}KB)")
for dirpath, dirs, files in os.walk(ROOT + ".Report"):
    for f2 in files: print(f"  {os.path.relpath(os.path.join(dirpath,f2), ROOT+'.Report')} ({os.path.getsize(os.path.join(dirpath,f2))//1024}KB)")
print(f"  LoBP_Dashboard.pbip ({os.path.getsize(PBIP)//1024}KB)")
