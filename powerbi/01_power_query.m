// ============================================================
// LOUVRE BANQUE PRIVÉE — POWER QUERY (M Language)
// À coller dans Power BI Desktop via :
//   Accueil > Transformer les données > Éditeur avancé
// ============================================================
// Adapter les paramètres de connexion (ServerDB, DatabaseDB)
// selon l'environnement du data warehouse
// ============================================================


// ============================================================
// PARAMÈTRES DE CONNEXION (Accueil > Gérer les paramètres)
// ============================================================
// ServerDB    = "mon-serveur-dw.lobp.fr"
// DatabaseDB  = "DW_LOBP"
// SchemaDW    = "dbo"


// ============================================================
// TABLE : CLIENT
// Clé : id_cli
// Usage : tous les boards — référentiel central client
// ============================================================
let
    Source = Sql.Database(ServerDB, DatabaseDB),
    dbo_CLIENT = Source{[Schema=SchemaDW, Item="CLIENT"]}[Data],

    // Filtres : date fonctionnelle = dernier arrêté
    LastDate = List.Max(dbo_CLIENT[dt_fonc]),
    Filtered = Table.SelectRows(dbo_CLIENT, each [dt_fonc] = LastDate),

    // Sélection des colonnes utiles
    Selected = Table.SelectColumns(Filtered, {
        "id_cli", "cd_typ", "lib_cd_typ", "id_gr", "lib_gr",
        "cli_c_p", "nom_cplt", "cd_civ", "prm_prn", "nom_us",
        "age_cli", "cd_situ_fam", "lib_cd_situ_fam",
        "id_cli_chrg", "cd_cons", "nom_cons", "prm_cons",
        "lib_ptf", "agc_topz", "lib_esp", "lib_grp_agce",
        "etat_acc", "top_client_actif",
        "dt_der_cnx", "dt_top_cl", "dt_exit_cl",
        "dt_dernier_rdv", "dt_1er_cnt",
        "nb_dev_enrol", "typ_enrol", "dt_enrol", "id_cli_web",
        "cd_risque_pers", "cd_risque_ajust",
        "lib_cd_risque_pers", "lib_cd_risque_ajust",
        "tot_score_risque", "scenario_risque", "lib_scenario_risque", "cd_mf",
        "gelule_global", "lib_gelule_global",
        "kyc_idt", "kyc_adr", "dt_der_certif", "dt_next_certif",
        "lib_stt_fatca", "pay_fis_prin",
        "pay_res", "lib_pay_res", "couleur_pays", "niveau_risque_pays",
        "top_pays_embargo", "top_pays_sanctions", "top_pays_gda",
        "top_pays_gafi", "top_pays_etnc", "top_pays_pthr",
        "cd_ficp", "nb_incidents_ficp",
        "aum_tit", "aum_cot", "mnt_pat_epargne", "mnt_pat_biens_immos",
        "mnt_rev_princ", "mnt_credits_externes",
        "mnt_equip_emp", "nb_equip_emp", "mnt_equip_tit", "nb_equip_tit",
        "mnt_equip_cau", "mnt_equip_coe",
        "list_fam_pdt", "list_pdt",
        "dt_fonc", "annee_mois_part"
    }),

    // Typage
    Typed = Table.TransformColumnTypes(Selected, {
        {"id_cli",            type text},
        {"age_cli",           Int64.Type},
        {"nb_dev_enrol",      Int64.Type},
        {"dt_der_cnx",        type date},
        {"dt_enrol",          type date},
        {"dt_top_cl",         type date},
        {"dt_exit_cl",        type date},
        {"dt_dernier_rdv",    type date},
        {"dt_next_certif",    type date},
        {"aum_tit",           type number},
        {"aum_cot",           type number},
        {"mnt_pat_epargne",   type number},
        {"mnt_equip_emp",     type number},
        {"mnt_equip_tit",     type number},
        {"gelule_global",     Int64.Type},
        {"nb_incidents_ficp", Int64.Type},
        {"top_pays_embargo",  type logical},
        {"top_pays_sanctions",type logical},
        {"top_pays_gda",      type logical},
        {"dt_fonc",           type date}
    }),

    // Colonnes calculées
    WithRisqueLabel = Table.AddColumn(Typed, "Couleur_KYC", each
        if [gelule_global] = 10 then "Rouge"
        else if [gelule_global] = 5 then "Orange"
        else "Vert"
    ),

    WithCertifAlerte = Table.AddColumn(WithRisqueLabel, "Alerte_Certif", each
        if [dt_next_certif] <> null and [dt_next_certif] <= Date.AddMonths(Date.From(DateTime.LocalNow()), 3)
        then "À renouveler" else "OK"
    )

in
    WithCertifAlerte


// ============================================================
// TABLE : TRANSACTION
// Clé : id_cli (→ CLIENT), num_cnt
// Usage : Board Conformité (AML, pays risque, volumes)
// ============================================================
let
    Source = Sql.Database(ServerDB, DatabaseDB),
    dbo_TRANSACTION = Source{[Schema=SchemaDW, Item="TRANSACTION"]}[Data],

    Selected = Table.SelectColumns(dbo_TRANSACTION, {
        "id_cli", "num_cnt", "perimetre",
        "typ_evt", "typ_evt_lv1", "val_evt_lv1", "lib_evt_lv1",
        "typ_evt_lv2", "val_evt_lv2",
        "sens", "mnt_evt", "devise_compte", "mnt_devise", "devise_operation",
        "dt_demande", "dt_validation", "dt_realisation",
        "mode_paiement", "typ_paiement",
        "ind_3ds", "ind_sans_contact", "ind_saisie_pin",
        "canal_init", "canal_ordre",
        "ctrpty_nom", "ctrpty_pays", "ctrpty_bnq_bic",
        "cli_cd_pays_iso", "cli_couleur_pays", "cli_niveau_risque_pays",
        "cli_top_pays_embargo", "cli_top_pays_sanctions",
        "cli_top_pays_gda", "cli_top_pays_gafi",
        "cli_top_pays_etnc", "cli_top_pays_pthr",
        "ctrpty_cd_pays_iso", "ctrpty_couleur_pays", "ctrpty_niveau_risque_pays",
        "ctrpty_top_pays_embargo", "ctrpty_top_pays_sanctions",
        "ctrpty_top_pays_gda", "ctrpty_top_pays_gafi",
        "ctrpty_bnq_cd_pays_iso", "ctrpty_bnq_couleur_pays",
        "ctrpty_bnq_top_pays_embargo", "ctrpty_bnq_top_pays_sanctions",
        "annee_mois_part"
    }),

    Typed = Table.TransformColumnTypes(Selected, {
        {"id_cli",                   type text},
        {"mnt_evt",                  type number},
        {"mnt_devise",               type number},
        {"dt_demande",               type date},
        {"dt_validation",            type date},
        {"dt_realisation",           type date},
        {"ind_3ds",                  Int64.Type},
        {"ind_sans_contact",         Int64.Type},
        {"cli_top_pays_embargo",     type logical},
        {"cli_top_pays_sanctions",   type logical},
        {"cli_top_pays_gda",         type logical},
        {"ctrpty_top_pays_embargo",  type logical},
        {"ctrpty_top_pays_sanctions",type logical}
    }),

    // Colonne : transaction sensible (tout pays à risque impliqué)
    WithSensible = Table.AddColumn(Typed, "Transaction_Sensible", each
        [cli_top_pays_embargo] = true
        or [cli_top_pays_sanctions] = true
        or [ctrpty_top_pays_embargo] = true
        or [ctrpty_top_pays_sanctions] = true
        or [ctrpty_top_pays_gda] = true
    )

in
    WithSensible


// ============================================================
// TABLE : EPARGNE
// Clé : id_cli (→ CLIENT), num_cnt, isin_fds (→ GSM)
// Usage : Board Épargne & Performance, Board Produits
// ============================================================
let
    Source = Sql.Database(ServerDB, DatabaseDB),
    dbo_EPARGNE = Source{[Schema=SchemaDW, Item="EPARGNE"]}[Data],

    Selected = Table.SelectColumns(dbo_EPARGNE, {
        "id_cli", "num_cnt", "stt_cli", "fam_pdt", "perimetre",
        "lib_ctl", "lib_fam_niv3_pdt", "stt_cnt", "lib_stt_cnt",
        "dt_eff", "dt_fin_eff",
        "mod_gest", "lib_mod_gest", "cd_ges", "lib_cd_ges",
        "enc_cnt_m", "enc_moy_m", "enc_cnt_m1", "enc_cnt_n1", "var_enc",
        "col_brute", "decollecte", "col_nette",
        "isin_fds", "lib_fds", "qte_fds", "enc_fds_m",
        "volatilite_isin", "isin_risq",
        "prof_risq", "lib_prof_risq", "prof_exp", "lib_prof_exp", "prof_sfdr",
        "mnt_tar_brt", "mnt_pdt_tar", "mnt_fdg", "mnt_ddg", "tx_int",
        "cd_bck_ifrs9", "cd_risque", "cd_etat_creance",
        "mnt_prov_b_ifrs9", "mnt_prov_hb_ifrs9",
        "mnt_dot", "mnt_rep", "mnt_psp",
        "total_rwa", "top_nanti", "mnt_nanti", "assur",
        "annee_mois_part"
    }),

    Typed = Table.TransformColumnTypes(Selected, {
        {"id_cli",           type text},
        {"enc_cnt_m",        type number},
        {"enc_cnt_n1",       type number},
        {"var_enc",          type number},
        {"col_brute",        type number},
        {"decollecte",       type number},
        {"col_nette",        type number},
        {"enc_fds_m",        type number},
        {"volatilite_isin",  type number},
        {"isin_risq",        Int64.Type},   // note 1 à 7
        {"mnt_prov_b_ifrs9", type number},
        {"mnt_prov_hb_ifrs9",type number},
        {"total_rwa",        type number},
        {"dt_eff",           type date},
        {"dt_fin_eff",       type date}
    }),

    // Label bucket IFRS9 lisible
    WithBucketLabel = Table.AddColumn(Typed, "Lib_Bucket_IFRS9", each
        if [cd_bck_ifrs9] = "B1" then "Sain"
        else if [cd_bck_ifrs9] = "B2" then "Sensible"
        else if [cd_bck_ifrs9] = "B3" then "Douteux/Contentieux"
        else "N/A"
    )

in
    WithBucketLabel


// ============================================================
// TABLE : CREDIT
// Clé : id_cli (→ CLIENT), num_cnt, num_prj
// Usage : Board Crédit & Garanties
// ============================================================
let
    Source = Sql.Database(ServerDB, DatabaseDB),
    dbo_CREDIT = Source{[Schema=SchemaDW, Item="CREDIT"]}[Data],

    Selected = Table.SelectColumns(dbo_CREDIT, {
        "id_cli", "num_cnt", "num_prj", "stt_cli",
        "fam_pdt", "perimetre", "lib_ctl", "stt_cnt", "lib_stt_cnt",
        "cd_etat_prt", "lib_cd_etat_prt", "typ_prt", "lib_typ_prt",
        "typ_mar", "lib_typ_mar", "typ_remb", "agc_cnt",
        "mnt_nom", "mnt_dblq", "mnt_nom_proj", "mnt_dblq_proj", "mnt_disp",
        "enc_cpt", "enc_cpt_moy_m", "enc_gest",
        "mnt_krd_tot", "mnt_krd_sain", "mnt_krd_imp",
        "mnt_ifa_tot", "mnt_ifa_sain", "mnt_ifa_imp",
        "tx_int_ref", "tx_int_ini", "tx_int_act", "teg", "typ_tx",
        "dt_eff", "dt_fin_init", "dt_fin_eff", "mat_init", "mat_reelle", "duree_resi",
        "cd_bck_ifrs9", "cd_risque", "cd_etat_creance", "lib_cd_etat_creance",
        "mnt_prov_b_ifrs9", "mnt_prov_hb_ifrs9",
        "mnt_dot", "mnt_rep", "mnt_psp",
        "total_rwa", "ead_nette_b", "ead_nette_hb",
        "rwa_collateralized_b", "rwa_guaranteed_b", "rwa_unguaranteed",
        "cd_nat", "cd_res", "mnt_bien_ori", "mnt_app",
        "ltv_ori", "ltv_act", "bien_commune", "cd_postal", "bien_dpe",
        "cd_incident", "lib_cd_incident", "nb_ficp", "tx_edt", "nb_rst",
        "annee_mois_part"
    }),

    Typed = Table.TransformColumnTypes(Selected, {
        {"id_cli",           type text},
        {"num_cnt",          type text},
        {"mnt_nom",          type number},
        {"mnt_dblq",         type number},
        {"enc_cpt",          type number},
        {"enc_gest",         type number},
        {"mnt_krd_tot",      type number},
        {"mnt_krd_sain",     type number},
        {"mnt_krd_imp",      type number},
        {"tx_int_act",       type number},
        {"teg",              type number},
        {"ltv_ori",          type number},
        {"ltv_act",          type number},
        {"tx_edt",           type number},
        {"mat_init",         Int64.Type},
        {"duree_resi",       Int64.Type},
        {"mnt_prov_b_ifrs9", type number},
        {"mnt_prov_hb_ifrs9",type number},
        {"total_rwa",        type number},
        {"dt_eff",           type date},
        {"dt_fin_eff",       type date}
    }),

    WithBucketLabel = Table.AddColumn(Typed, "Lib_Bucket_Credit", each
        if [cd_bck_ifrs9] = "B1" then "Sain"
        else if [cd_bck_ifrs9] = "B2" then "Sensible"
        else if [cd_bck_ifrs9] = "B3" then "Douteux/Contentieux"
        else "N/A"
    ),

    WithTypeMarche = Table.AddColumn(WithBucketLabel, "Lib_Marche_Simple", each
        if [typ_mar] = "01" then "Immobilier"
        else if [typ_mar] = "02" then "Équipement Familial"
        else if [typ_mar] = "03" then "Professionnel"
        else if [typ_mar] = "04" then "Collectivités"
        else "Autre"
    )

in
    WithTypeMarche


// ============================================================
// TABLE : GARANTIE
// Clé : id_cli + num_cnt (→ CREDIT.num_cnt via num_cnt_prt)
// Usage : Board Crédit & Garanties
// ============================================================
let
    Source = Sql.Database(ServerDB, DatabaseDB),
    dbo_GARANTIE = Source{[Schema=SchemaDW, Item="GARANTIE"]}[Data],

    Renamed = Table.RenameColumns(dbo_GARANTIE, {{"num_cnt_prt", "num_cnt"}}),

    Selected = Table.SelectColumns(Renamed, {
        "id_cli", "num_cnt", "num_cnt_gar", "stt_cli",
        "det_typ_gar", "lib_det_typ_gar",
        "stt_gar", "lib_stt_gar", "stt_cnt", "cd_rang",
        "dt_eff_gar", "dt_ech_gar", "dur_gar",
        "mnt_gar", "mnt_gar_cpta", "mnt_bien_gar_ori", "mnt_reval", "vlr_reval_act", "dt_reval",
        "num_cnt_ass", "lib_cnt_ass", "nom_cie_ass",
        "lib_ville", "cd_postal",
        "tx_rwa", "mnt_rwa",
        "annee_mois_part"
    }),

    Typed = Table.TransformColumnTypes(Selected, {
        {"id_cli",         type text},
        {"mnt_gar",        type number},
        {"mnt_gar_cpta",   type number},
        {"mnt_reval",      type number},
        {"mnt_rwa",        type number},
        {"tx_rwa",         type number},
        {"dt_eff_gar",     type date},
        {"dt_ech_gar",     type date},
        {"dt_reval",       type date}
    })

in
    Typed


// ============================================================
// TABLE : SERVICE
// Clé : id_cli (→ CLIENT), num_cnt
// Usage : Board Produits (cartes, chéquiers, découverts)
// ============================================================
let
    Source = Sql.Database(ServerDB, DatabaseDB),
    dbo_SERVICE = Source{[Schema=SchemaDW, Item="SERVICE"]}[Data],

    Selected = Table.SelectColumns(dbo_SERVICE, {
        "id_cli", "num_cnt", "stt_cli", "fam_pdt", "perimetre",
        "lib_ctl", "stt_cnt", "lib_stt_cnt",
        "dt_eff", "dt_fin_eff", "agc_ins",
        "num_carte", "cd_typ_debit", "dt_ech_carte", "ind_carte_virtu",
        "mnt_tar_brt", "mnt_pdt_tar",
        "cd_bck_ifrs9", "mnt_prov_b_ifrs9", "mnt_prov_hb_ifrs9",
        "annee_mois_part"
    }),

    Typed = Table.TransformColumnTypes(Selected, {
        {"id_cli",           type text},
        {"mnt_pdt_tar",      type number},
        {"mnt_prov_b_ifrs9", type number},
        {"mnt_prov_hb_ifrs9",type number},
        {"dt_eff",           type date},
        {"dt_fin_eff",       type date},
        {"dt_ech_carte",     type date}
    })

in
    Typed


// ============================================================
// TABLE : GSM (positions ISIN)
// Clé : isin_fds (→ EPARGNE.isin_fds), id_contrat
// Usage : Board Épargne — SFDR, taxonomie verte, performance
// ============================================================
let
    Source = Sql.Database(ServerDB, DatabaseDB),
    dbo_GSM = Source{[Schema=SchemaDW, Item="GSM"]}[Data],

    Selected = Table.SelectColumns(dbo_GSM, {
        "isin_fds", "id_contrat", "dt_fonc", "cd_ges", "mod_gest", "reseau",
        "qte_fds", "cours_cot", "dt_cot", "avg_mnt_achat",
        "enc_fds_m", "enc_cnt_n_1",
        "sum_enc_fds_cnt", "poids_isin_cnt",
        "sum_enc_fds_profil", "poids_isin_profil",
        "sum_enc_fds_gsm", "poids_isin_total_gsm",
        "apport_cli", "performance_cli", "mnt_pmvl",
        "ind_sfdr_30000", "ind_sfdr_30010", "ind_sfdr_30020",
        "ind_sfdr_30060", "ind_sfdr_30100", "ind_sfdr_30140",
        "ind_sfdr_10040", "ind_sfdr_00050", "ind_sfdr_20150",
        "ind_taxo_20660", "ind_taxo_20670", "ind_taxo_20680",
        "ind_taxo_20690", "ind_taxo_20700", "ind_taxo_20710"
    }),

    Typed = Table.TransformColumnTypes(Selected, {
        {"isin_fds",         type text},
        {"enc_fds_m",        type number},
        {"enc_cnt_n_1",      type number},
        {"performance_cli",  type number},
        {"mnt_pmvl",         type number},
        {"poids_isin_cnt",   type number},
        {"dt_cot",           type date},
        {"dt_fonc",          type date}
    }),

    // Colonne SFDR Article (8, 9, ou Non classifié)
    WithSFDR = Table.AddColumn(Typed, "Classification_SFDR", each
        if [ind_sfdr_30000] = 1 then "Article 9 (Impact)"
        else if [ind_sfdr_10000] = 1 then "Article 8 (ESG)"
        else "Non classifié"
    )

in
    WithSFDR
