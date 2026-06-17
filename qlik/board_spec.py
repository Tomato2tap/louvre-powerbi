# -*- coding: utf-8 -*-
"""
Specification des boards Louvre Banque Privee pour Qlik Sense.
Mesures / dimensions remappees sur le MODELE PROPRE (prefixes EP_/CR_/TR_/GA_/GS_).
Consomme par build_app.py via l'Engine API.
"""

# ---- Palette charte LoBP (bordeaux/or) ----
PALETTE = {
    "primary":   "#8B1F2A",  # bordeaux fonce
    "secondary": "#C9453A",  # rouge chaud
    "accent1":   "#D4A04A",  # or / caramel
    "accent2":   "#6B8FA8",  # bleu gris
    "bg":        "#F4F2EE",  # beige clair
    "card":      "#FFFFFF",
    "text":      "#2C2C2C",
    "text2":     "#666666",
    "red":       "#C0392B",
    "orange":    "#E67E22",
    "green":     "#27AE60",
}

# ---- MASTER MEASURES : (titre, expression, format) ----
# Formats Qlik : '#,##0' entier ; '0.0%' pourcentage ; '# ##0 €' money
MEASURES = [
    # CLIENTS (table CLIENT, champs non prefixes)
    ("Nb Clients Totaux",      "Count(DISTINCT {<cli_c_p={'CL','CT'}>} id_cli)", "#,##0"),
    ("Nb Clients Actifs",      "Count(DISTINCT {<top_client_actif={'O'}>} id_cli)", "#,##0"),
    ("Nb Clients Enrollés",    "Count(DISTINCT {<nb_dev_enrol={\">0\"}>} id_cli)", "#,##0"),
    ("Taux Enrollment",        "Count(DISTINCT {<nb_dev_enrol={\">0\"}>} id_cli) / Count(DISTINCT id_cli)", "0.0%"),
    ("Nb Smartphones Enrollés","Sum(nb_dev_enrol)", "#,##0"),
    ("Nb Comptes Bloqués",     "Count(DISTINCT {<etat_acc={'B'}>} id_cli)", "#,##0"),
    ("Nb Clients KYC Rouge",   "Count(DISTINCT {<gelule_global={10}>} id_cli)", "#,##0"),
    ("Nb Clients Risque Élevé","Count(DISTINCT {<cd_risque_pers={'E','F'}>} id_cli)", "#,##0"),
    ("AUM Total",              "Sum(aum_tit)", "# ##0 €"),
    ("AUM Moyen par Client",   "Sum(aum_tit) / Count(DISTINCT id_cli)", "# ##0 €"),
    ("Patrimoine Épargne",     "Sum(mnt_pat_epargne)", "# ##0 €"),

    # EPARGNE (prefixe EP_)
    ("Encours Épargne Total",  "Sum(EP_enc_cnt_m)", "# ##0 €"),
    ("Encours Épargne N-1",    "Sum(EP_enc_cnt_n1)", "# ##0 €"),
    ("Collecte Brute",         "Sum(EP_col_brute)", "# ##0 €"),
    ("Collecte Nette",         "Sum(EP_col_nette)", "# ##0 €"),
    ("Nb Contrats Épargne",    "Count(DISTINCT EP_num_cnt)", "#,##0"),

    # CREDIT (id_cli + num_cnt non prefixes, reste CR_)
    ("Encours Crédit Total",   "Sum(CR_enc_cpt)", "# ##0 €"),
    ("Nb Contrats Crédit",     "Count(DISTINCT num_cnt)", "#,##0"),
    ("Montant Débloqué Total", "Sum(CR_mnt_dblq)", "# ##0 €"),
    ("LTV Moyenne Actuelle",   "Avg(CR_ltv_act)", "0.0%"),
    ("Provisions IFRS9 Crédit","Sum(CR_mnt_prov_b_ifrs9)", "# ##0 €"),

    # GARANTIES (prefixe GA_)
    ("Montant Garanties Total","Sum(GA_mnt_gar)", "# ##0 €"),

    # TRANSACTIONS (id_cli non prefixe, reste TR_)
    ("Volume Total Transactions", "Sum(TR_mnt_evt)", "# ##0 €"),
    ("Nb Transactions",           "Count(TR_mnt_evt)", "#,##0"),
    ("Volume Pays Sanctions",     "Sum({<TR_cli_top_pays_sanctions={1}>} TR_mnt_evt) + Sum({<TR_ctrpty_top_pays_sanctions={1}>} TR_mnt_evt)", "# ##0 €"),
    ("Volume Pays GDA",           "Sum({<TR_ctrpty_top_pays_gda={1}>} TR_mnt_evt)", "# ##0 €"),

    # GSM / fonds (prefixe GS_)
    ("Performance Moy. Portefeuille", "Avg(GS_performance_cli)", "0.00%"),
    ("Encours Fonds Durables SFDR",   "Sum({<GS_ind_sfdr_30000={1}>} GS_enc_fds_m)", "# ##0 €"),
]

# ---- MASTER DIMENSIONS : (titre, champ) ----
DIMENSIONS = [
    ("Type de client",      "lib_cd_typ"),
    ("Statut compte",       "etat_acc"),
    ("Risque personne",     "lib_cd_risque_pers"),
    ("Couleur pays",        "couleur_pays"),
    ("Agence",              "agc_topz"),
    ("Portefeuille",        "lib_ptf"),
    ("Conseiller",          "nom_cons"),
    ("Canal connexion",     "typ_enrol"),
    ("Type événement",      "TR_lib_evt_lv1"),
    ("Pays contrepartie",   "TR_ctrpty_pays"),
    ("Type prêt",           "CR_lib_typ_prt"),
    ("Famille produit",     "EP_lib_fam_niv3_pdt"),
    ("Fonds (ISIN)",        "EP_lib_fds"),
]

APP_NAME = "Louvre Banque Privée — Demo"
DATA_PATH = r"E:\louvre\powerbi\data"
