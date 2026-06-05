import csv, random, os
from datetime import date, timedelta

random.seed(42)
OUT = r"E:\louvre\powerbi\data"
os.makedirs(OUT, exist_ok=True)

def d(start="2015-01-01", end="2026-05-01"):
    s = date.fromisoformat(start); e = date.fromisoformat(end)
    return (s + timedelta(days=random.randint(0,(e-s).days))).isoformat()

def amt(lo, hi, dec=2): return round(random.uniform(lo, hi), dec)

NOMS    = ["MARTIN","DUPONT","BERNARD","PETIT","LEROY","ROBERT","SIMON","LAURENT","MICHEL","GARCIA",
           "DAVID","BERTRAND","MOREAU","THOMAS","LECLERC","FONTAINE","HENRY","ROUSSEAU","BLANC","GUERIN"]
PRENOMS = ["Jean","Marie","Pierre","Sophie","François","Claire","Nicolas","Anne","Paul","Isabelle",
           "Louis","Catherine","Philippe","Julie","Marc","Nathalie","Henri","Céline","Antoine","Laure"]
AGENCES = ["PARIS 1","PARIS 8","PARIS 16","LYON PRESTIGE","BORDEAUX PGP","MARSEILLE","NICE","LILLE","TOULOUSE","GENEVE"]
CONSEILS= [("C001","LAMBERT","Thomas"),("C002","ROUSSEL","Caroline"),("C003","FAURE","Philippe"),
           ("C004","MORIN","Anne"),("C005","GIRARD","Olivier")]
PAYS_OK = ["FR","GB","DE","CH","BE","LU","NL","US","IT","ES"]
PAYS_RISK=["RU","SY","KP","IR","BY"]
PAYS_MED=["AE","CN","BR","IN","ZA"]

# ── CLIENT ──────────────────────────────────────────────────────────────────
clients = []
for i in range(1, 61):
    cid = f"CLI{i:05d}"
    nom = random.choice(NOMS); prn = random.choice(PRENOMS)
    typ = random.choices(["P","P","P","E","S"],[5,5,5,2,1])[0]
    ccp = random.choices(["CL","CL","CT","PR"],[6,6,1,2])[0]
    agc,cnom,cprn = random.choice(CONSEILS)
    aum = amt(50000, 8000000) if ccp in("CL","CT") else 0
    gel = random.choices([0,5,10],[6,2,1])[0]
    risq = random.choices(["A+","B","C","D","E","F"],[4,4,3,2,1,1])[0]
    pays_res = random.choices(PAYS_OK+PAYS_MED+PAYS_RISK,[10]*10+[3]*5+[1]*5)[0]
    embargo = 1 if pays_res in PAYS_RISK else 0
    sanctions = 1 if pays_res in PAYS_RISK else 0
    gda = 1 if pays_res in ["RU","BY"] else 0
    couleur = "rouge" if pays_res in PAYS_RISK else ("orange" if pays_res in PAYS_MED else "vert")
    enrol = random.randint(0,3) if ccp in ("CL","CT") else 0
    etat = random.choices(["O","O","B","S"],[8,8,1,1])[0]
    actif = "O" if ccp=="CL" and random.random()>0.25 else "N"
    next_certif = d("2025-01-01","2027-12-31")
    der_rdv = d("2024-01-01","2026-05-01") if ccp=="CL" else ""
    clients.append({
        "id_cli":cid,"cd_typ":typ,"lib_cd_typ":{"P":"Personne physique","E":"Entreprise individuelle","S":"Société","A":"Association","I":"Inst. Financière"}[typ],
        "id_gr":f"GR{random.randint(1,20):03d}","lib_gr":f"Groupe {random.randint(1,5)}",
        "cli_c_p":ccp,"nom_cplt":f"{nom} {prn}","prm_prn":prn,"nom_us":nom,
        "age_cli":random.randint(30,80) if typ=="P" else "","cd_situ_fam":random.choice(["M","C","D","V","P"]) if typ=="P" else "",
        "lib_cd_situ_fam":{"M":"Marié(e)","C":"Célibataire","D":"Divorcé(e)","V":"Veuf/Veuve","P":"Pacsé(e)"}.get(random.choice(["M","C","D","V","P"]),""),
        "cd_cons":agc,"nom_cons":cnom,"prm_cons":cprn,"lib_ptf":f"PTF-{agc}",
        "agc_topz":random.choice(AGENCES),"lib_grp_agce":f"GRP-{random.randint(1,5)}",
        "etat_acc":etat,"top_client_actif":actif,
        "dt_der_cnx":d("2025-01-01","2026-05-01") if enrol>0 else "",
        "dt_top_cl":d("2015-01-01","2023-01-01") if ccp=="CL" else "",
        "dt_exit_cl":"","dt_dernier_rdv":der_rdv,"dt_1er_cnt":d("2010-01-01","2022-01-01") if ccp=="CL" else "",
        "nb_dev_enrol":enrol,"typ_enrol":"MOBILE" if enrol>0 else "","dt_enrol":d("2020-01-01","2025-06-01") if enrol>0 else "",
        "cd_risque_pers":risq,"lib_cd_risque_pers":{"A+":"Solvable","B":"Solvable","C":"Correct","D":"Sensible","E":"Douteux","F":"Contentieux"}[risq],
        "cd_risque_ajust":risq,"lib_cd_risque_ajust":{"A+":"Solvable","B":"Solvable","C":"Correct","D":"Sensible","E":"Douteux","F":"Contentieux"}[risq],
        "tot_score_risque":random.randint(10,100),"scenario_risque":random.choice(["SCN001","SCN002","SCN003"]),"lib_scenario_risque":random.choice(["Standard","Renforcé","Simplifié"]),
        "cd_mf":random.choice(["","PPEF","PPEP",""]),
        "gelule_global":gel,"lib_gelule_global":{"0":"Vert","5":"Orange","10":"Rouge"}[str(gel)],
        "kyc_idt":random.choice([0,5,10]),"kyc_adr":random.choice([0,5,10]),
        "dt_der_certif":d("2022-01-01","2025-01-01"),"dt_next_certif":next_certif,
        "lib_stt_fatca":random.choice(["Non concerné","Identifié","Certifié","Récalcitrant"]),
        "pay_fis_prin":random.choices(["FR","US","CH","UK",""],[6,1,1,1,3])[0],
        "pay_res":pays_res,"lib_pay_res":{"FR":"France","GB":"Royaume-Uni","DE":"Allemagne","CH":"Suisse","BE":"Belgique","LU":"Luxembourg","NL":"Pays-Bas","US":"États-Unis","IT":"Italie","ES":"Espagne","RU":"Russie","SY":"Syrie","KP":"Corée du Nord","IR":"Iran","BY":"Biélorussie","AE":"Émirats Arabes","CN":"Chine","BR":"Brésil","IN":"Inde","ZA":"Afrique du Sud"}.get(pays_res,pays_res),
        "couleur_pays":couleur,"niveau_risque_pays":{"vert":"Faible","orange":"Moyen","rouge":"Élevé"}[couleur],
        "top_pays_embargo":embargo,"top_pays_sanctions":sanctions,"top_pays_gda":gda,"top_pays_gafi":0,"top_pays_etnc":0,"top_pays_pthr":0,
        "cd_ficp":"" if random.random()>0.05 else "FICP","nb_incidents_ficp":0 if random.random()>0.05 else random.randint(1,3),
        "aum_tit":round(aum,2),"aum_cot":round(aum*0.3,2) if random.random()>0.5 else 0,
        "mnt_pat_epargne":round(aum*0.6,2),"mnt_pat_biens_immos":round(aum*0.4,2),
        "mnt_rev_princ":round(amt(2000,30000),2),"mnt_credits_externes":round(amt(0,500000),2),
        "mnt_equip_emp":round(amt(0,2000000),2),"nb_equip_emp":random.randint(0,3),
        "mnt_equip_tit":round(aum*0.6,2),"nb_equip_tit":random.randint(0,5),
        "mnt_equip_cau":0,"mnt_equip_coe":0,
        "list_fam_pdt":random.choice(["epargne;credit","epargne","credit","epargne;credit;service","service"]),
        "list_pdt":random.choice(["AV;PEA;IMM","AV;LIVRET","IMM;CONSO","PEA;CTO;AV","CARTE;CC"]),
        "dt_fonc":"2026-05-31","annee_mois_part":"2026-05"
    })

with open(f"{OUT}/CLIENT.csv","w",newline="",encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=clients[0].keys()); w.writeheader(); w.writerows(clients)
print("CLIENT.csv OK")

# ── TRANSACTION ──────────────────────────────────────────────────────────────
cids = [c["id_cli"] for c in clients]
EVT_TYPES  = [("VRT","Virement"),("PAI","Paiement carte"),("RET","Retrait"),("PRE","Prélèvement"),("CHQ","Chèque")]
CANAUX     = ["WEB","MOBILE","IOS","ANDROID","AGENCE","SVI"]
PAYS_LISTE = PAYS_OK+PAYS_MED+PAYS_RISK

transactions = []
for j in range(1,251):
    cid   = random.choice(cids)
    cli   = next(c for c in clients if c["id_cli"]==cid)
    evt,lev1 = random.choice(EVT_TYPES)
    canal = random.choices(CANAUX,[2,4,3,1,1,1])[0]
    cpays = random.choices(PAYS_LISTE,[10]*10+[2]*5+[1]*5)[0]
    cemb  = 1 if cpays in PAYS_RISK else 0
    csan  = 1 if cpays in PAYS_RISK else 0
    cgda  = 1 if cpays in ["RU","BY"] else 0
    ccol  = "rouge" if cpays in PAYS_RISK else ("orange" if cpays in PAYS_MED else "vert")
    mnt   = amt(50,150000) if evt=="VRT" else (amt(5,5000) if evt=="PAI" else amt(20,1500))
    dt    = d("2025-01-01","2026-05-31")
    transactions.append({
        "id_cli":cid,"num_cnt":f"CNT{random.randint(1,200):06d}","perimetre":"service",
        "typ_evt":evt,"typ_evt_lv1":evt,"val_evt_lv1":evt,"lib_evt_lv1":lev1,
        "typ_evt_lv2":"","val_evt_lv2":"",
        "sens":random.choice(["D","C"]),"mnt_evt":round(mnt,2),"devise_compte":"EUR",
        "mnt_devise":round(mnt,2),"devise_operation":"EUR",
        "dt_demande":dt,"dt_validation":dt,"dt_realisation":dt,
        "mode_paiement":random.choice(["CB","VRT","CHQ","PRE"]),"typ_paiement":random.choice(["SEPA","INST","NORM"]),
        "ind_3ds":1 if evt=="PAI" and random.random()>0.3 else 0,
        "ind_sans_contact":1 if evt=="PAI" and random.random()>0.5 else 0,
        "ind_saisie_pin":1 if evt=="PAI" and random.random()>0.5 else 0,
        "canal_init":canal,"canal_ordre":canal,
        "ctrpty_nom":random.choice(["AMAZON","CARREFOUR","EDF","SNCF","BNP","SG","AXA","LVMH","AIRBUS","TOTAL"]),
        "ctrpty_pays":cpays,"ctrpty_bnq_bic":f"BIC{cpays}XXX",
        "cli_cd_pays_iso":cli["pay_res"],"cli_couleur_pays":cli["couleur_pays"],
        "cli_niveau_risque_pays":cli["niveau_risque_pays"],
        "cli_top_pays_embargo":cli["top_pays_embargo"],"cli_top_pays_sanctions":cli["top_pays_sanctions"],
        "cli_top_pays_gda":cli["top_pays_gda"],"cli_top_pays_gafi":0,"cli_top_pays_etnc":0,"cli_top_pays_pthr":0,
        "ctrpty_cd_pays_iso":cpays,"ctrpty_couleur_pays":ccol,
        "ctrpty_niveau_risque_pays":{"rouge":"Élevé","orange":"Moyen","vert":"Faible"}[ccol],
        "ctrpty_top_pays_embargo":cemb,"ctrpty_top_pays_sanctions":csan,"ctrpty_top_pays_gda":cgda,"ctrpty_top_pays_gafi":0,
        "ctrpty_bnq_cd_pays_iso":cpays,"ctrpty_bnq_couleur_pays":ccol,
        "ctrpty_bnq_top_pays_embargo":cemb,"ctrpty_bnq_top_pays_sanctions":csan,
        "Transaction_Sensible":1 if (cli["top_pays_embargo"] or cemb or csan or cgda) else 0,
        "annee_mois_part":"2026-05"
    })

with open(f"{OUT}/TRANSACTION.csv","w",newline="",encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=transactions[0].keys()); w.writeheader(); w.writerows(transactions)
print("TRANSACTION.csv OK")

# ── EPARGNE ──────────────────────────────────────────────────────────────────
FAM_EPS = [("AV","Assurance Vie"),("PEA","PEA"),("CTO","Compte Titres"),("LIV","Livret"),("PER","PER")]
ISINS   = ["FR0010135103","FR0007475915","LU0389812933","FR0010827956","IE00B4L5Y983",
           "FR0013412285","LU0533033667","FR0010315770","FR0011269588","LU0256624742"]
GESTS   = [("150","BPE Dynamique Premium"),("151","BPE Diversification Premium"),("0","Libre"),("2","Gestion Mandat")]

epargne = []
for k in range(1,91):
    cid  = random.choice(cids)
    fam,lib_fam = random.choice(FAM_EPS)
    isin = random.choice(ISINS)
    enc  = amt(5000, 500000)
    enc_n1 = enc * random.uniform(0.85,1.15)
    var  = enc - enc_n1
    col  = amt(0, enc*0.2)
    dec  = -amt(0, enc*0.1)
    bkt  = random.choices(["B1","B2","B3"],[7,2,1])[0]
    mod,lib_mod = random.choice(GESTS)
    epargne.append({
        "id_cli":cid,"num_cnt":f"EPS{k:06d}","stt_cli":"TIT",
        "fam_pdt":fam,"perimetre":"epargne","lib_ctl":lib_fam,
        "lib_fam_niv3_pdt":lib_fam,"stt_cnt":"0","lib_stt_cnt":"Normal",
        "dt_eff":d("2010-01-01","2023-01-01"),"dt_fin_eff":d("2030-01-01","2040-01-01"),
        "mod_gest":mod,"lib_mod_gest":lib_mod,"cd_ges":mod,"lib_cd_ges":lib_mod,
        "enc_cnt_m":round(enc,2),"enc_moy_m":round(enc*0.98,2),"enc_cnt_m1":round(enc*0.99,2),
        "enc_cnt_n1":round(enc_n1,2),"var_enc":round(var,2),
        "col_brute":round(col,2),"decollecte":round(dec,2),"col_nette":round(col+dec,2),
        "isin_fds":isin,"lib_fds":f"Fonds {isin[:8]}","qte_fds":random.randint(10,5000),
        "enc_fds_m":round(enc,2),"volatilite_isin":round(amt(0.02,0.25),4),"isin_risq":random.randint(1,7),
        "prof_risq":random.choice(["CONS","EQUI","DYNA"]),"lib_prof_risq":random.choice(["Conservateur","Équilibré","Dynamique"]),
        "prof_exp":random.choice(["INVB","INVI","INVE"]),"lib_prof_exp":random.choice(["Basique","Informé","Expérimenté"]),
        "prof_sfdr":random.choice(["ART8","ART9","NC"]),
        "mnt_tar_brt":round(enc*0.008,2),"mnt_pdt_tar":round(enc*0.007,2),
        "mnt_fdg":round(enc*0.005,2),"mnt_ddg":round(enc*0.002,2),"tx_int":round(amt(0.005,0.035),4),
        "cd_bck_ifrs9":bkt,"cd_risque":random.choice(["01","02","10"]),"cd_etat_creance":"01",
        "mnt_prov_b_ifrs9":round(enc*0.01 if bkt!="B1" else 0,2),
        "mnt_prov_hb_ifrs9":round(enc*0.005 if bkt=="B3" else 0,2),
        "mnt_dot":0,"mnt_rep":0,"mnt_psp":0,"total_rwa":round(enc*0.08,2),
        "top_nanti":random.choice([0,0,1]),"mnt_nanti":0,"assur":"CNP" if fam=="AV" else "",
        "Lib_Bucket_IFRS9":{"B1":"Sain","B2":"Sensible","B3":"Douteux/Contentieux"}[bkt],
        "annee_mois_part":"2026-05"
    })

with open(f"{OUT}/EPARGNE.csv","w",newline="",encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=epargne[0].keys()); w.writeheader(); w.writerows(epargne)
print("EPARGNE.csv OK")

# ── CREDIT ───────────────────────────────────────────────────────────────────
MARCHES = [("01","Immobilier"),("02","Équipement Familial"),("03","Professionnel")]
credits = []
for l in range(1,71):
    cid   = random.choice(cids)
    mar,lib_mar = random.choices(MARCHES,[5,3,2])[0]
    mnt   = amt(50000,800000) if mar=="01" else amt(5000,80000)
    dblq  = mnt * random.uniform(0.7,1.0)
    enc   = dblq * random.uniform(0.3,0.95)
    sain  = enc * random.uniform(0.8,1.0)
    imp   = enc - sain
    bkt   = random.choices(["B1","B2","B3"],[6,3,1])[0]
    tx    = round(amt(0.01,0.045),4)
    ltv_o = round(amt(0.5,0.9),2)
    ltv_a = round(ltv_o * random.uniform(0.7,1.0),2)
    credits.append({
        "id_cli":cid,"num_cnt":f"CRD{l:06d}","num_prj":f"PRJ{l:06d}","stt_cli":"EMP",
        "fam_pdt":"credit","perimetre":"credit","lib_ctl":lib_mar,
        "stt_cnt":random.choices(["0","8","9"],[8,1,1])[0],"lib_stt_cnt":random.choice(["Normal","Contentieux","Clos"]),
        "cd_etat_prt":random.choices(["16","10","99"],[7,2,1])[0],
        "lib_cd_etat_prt":random.choice(["En remboursement","En franchise","Clôturé"]),
        "typ_prt":f"P{random.randint(100,999)}","lib_typ_prt":random.choice(["Prêt Immobilier","Prêt Perso","Prêt Pro"]),
        "typ_mar":mar,"lib_typ_mar":lib_mar,"typ_remb":random.choice(["Amort","In Fine"]),
        "agc_cnt":random.choice(AGENCES),
        "mnt_nom":round(mnt,2),"mnt_dblq":round(dblq,2),"mnt_nom_proj":round(mnt,2),"mnt_dblq_proj":round(dblq,2),
        "mnt_disp":round(mnt-dblq,2),"enc_cpt":round(enc,2),"enc_cpt_moy_m":round(enc*0.99,2),"enc_gest":round(enc*1.01,2),
        "mnt_krd_tot":round(enc,2),"mnt_krd_sain":round(sain,2),"mnt_krd_imp":round(imp,2),
        "mnt_ifa_tot":round(enc*tx/12,2),"mnt_ifa_sain":round(sain*tx/12,2),"mnt_ifa_imp":round(imp*tx/12,2),
        "tx_int_ref":tx,"tx_int_ini":tx,"tx_int_act":tx,"teg":round(tx*1.1,4),
        "typ_tx":random.choice(["F","F","R"]),"dt_eff":d("2015-01-01","2023-01-01"),
        "dt_fin_init":d("2030-01-01","2050-01-01"),"dt_fin_eff":d("2030-01-01","2050-01-01"),
        "mat_init":random.choice([10,15,20,25]),"mat_reelle":random.choice([10,15,20,25]),
        "duree_resi":random.randint(365,7300),
        "cd_bck_ifrs9":bkt,"cd_risque":random.choice(["01","02","10"]),
        "cd_etat_creance":random.choices(["01","10","30"],[8,1,1])[0],
        "lib_cd_etat_creance":random.choice(["Sain","Douteux","Contentieux"]),
        "mnt_prov_b_ifrs9":round(enc*0.02 if bkt!="B1" else enc*0.001,2),
        "mnt_prov_hb_ifrs9":round(enc*0.01 if bkt=="B3" else 0,2),
        "mnt_dot":0,"mnt_rep":0,"mnt_psp":0,
        "total_rwa":round(enc*0.35,2),"ead_nette_b":round(enc,2),"ead_nette_hb":round(mnt-dblq,2),
        "rwa_collateralized_b":round(enc*0.2,2),"rwa_guaranteed_b":round(enc*0.1,2),"rwa_unguaranteed":round(enc*0.05,2),
        "cd_nat":"01","cd_res":"01","mnt_bien_ori":round(mnt*1.2,2),"mnt_app":round(mnt*0.2,2),
        "ltv_ori":ltv_o,"ltv_act":ltv_a,"bien_commune":random.choice(["PARIS","LYON","BORDEAUX","MARSEILLE","NICE"]),
        "cd_postal":random.choice(["75001","69001","33000","13001","06000"]),
        "bien_dpe":random.choice(["A","B","C","D","E","F","G"]),
        "cd_incident":"00","lib_cd_incident":"Normal","nb_ficp":0,
        "tx_edt":round(amt(0.1,0.45),2),"nb_rst":random.choices([0,1,2],[8,1,1])[0],
        "Lib_Bucket_Credit":{"B1":"Sain","B2":"Sensible","B3":"Douteux/Contentieux"}[bkt],
        "Lib_Marche_Simple":lib_mar,
        "annee_mois_part":"2026-05"
    })

with open(f"{OUT}/CREDIT.csv","w",newline="",encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=credits[0].keys()); w.writeheader(); w.writerows(credits)
print("CREDIT.csv OK")

# ── GARANTIE ─────────────────────────────────────────────────────────────────
garanties = []
for crd in random.sample(credits, 50):
    mnt_gar = crd["mnt_nom"] * random.uniform(0.8,1.2)
    garanties.append({
        "id_cli":crd["id_cli"],"num_cnt":crd["num_cnt"],"num_cnt_gar":f"GAR{random.randint(1,9999):06d}","stt_cli":"EMP",
        "det_typ_gar":random.choice(["01","06","02"]),"lib_det_typ_gar":random.choice(["Immeuble","Assurance Vie","Véhicule"]),
        "stt_gar":random.choice(["EN_COURS","LEVEE"]),"lib_stt_gar":random.choice(["En cours","Levée"]),
        "stt_cnt":"0","cd_rang":random.choice(["1","2"]),
        "dt_eff_gar":d("2015-01-01","2023-01-01"),"dt_ech_gar":d("2030-01-01","2050-01-01"),
        "dur_gar":random.randint(10,30),
        "mnt_gar":round(mnt_gar,2),"mnt_gar_cpta":round(mnt_gar*0.9,2),
        "mnt_bien_gar_ori":round(mnt_gar*1.2,2),"mnt_reval":round(mnt_gar*random.uniform(0.9,1.3),2),
        "vlr_reval_act":round(random.uniform(90,130),2),"dt_reval":d("2023-01-01","2026-01-01"),
        "num_cnt_ass":f"ASS{random.randint(1,999):06d}","lib_cnt_ass":random.choice(["Credit Logement","Caution CNP","Hypothèque"]),
        "nom_cie_ass":random.choice(["Crédit Logement","CNP","SACCEF","CAMCA"]),
        "lib_ville":random.choice(["Paris","Lyon","Bordeaux","Marseille"]),"cd_postal":random.choice(["75001","69001","33000","13001"]),
        "tx_rwa":round(amt(0.2,0.5),2),"mnt_rwa":round(mnt_gar*0.3,2),
        "annee_mois_part":"2026-05"
    })

with open(f"{OUT}/GARANTIE.csv","w",newline="",encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=garanties[0].keys()); w.writeheader(); w.writerows(garanties)
print("GARANTIE.csv OK")

# ── SERVICE ───────────────────────────────────────────────────────────────────
SERVICES_FAM = [("carte","Carte Bancaire"),("compte_courant","Compte Courant"),("chequier","Chéquier")]
services = []
for m in range(1,91):
    cid = random.choice(cids)
    fam,lib = random.choice(SERVICES_FAM)
    bkt = random.choices(["B1","B2"],[9,1])[0]
    services.append({
        "id_cli":cid,"num_cnt":f"SVC{m:06d}","stt_cli":"TIT","fam_pdt":fam,"perimetre":"service",
        "lib_ctl":lib,"stt_cnt":"0","lib_stt_cnt":"Normal",
        "dt_eff":d("2015-01-01","2024-01-01"),"dt_fin_eff":d("2026-01-01","2028-01-01"),
        "agc_ins":random.choice(AGENCES),
        "num_carte":f"4{random.randint(100,999)}{random.randint(1000,9999)}{random.randint(1000,9999)}{random.randint(1000,9999)}" if fam=="carte" else "",
        "cd_typ_debit":random.choice(["DIF","IMM"]) if fam=="carte" else "","dt_ech_carte":d("2026-01-01","2030-01-01") if fam=="carte" else "",
        "ind_carte_virtu":random.choice([0,1]) if fam=="carte" else 0,
        "mnt_tar_brt":round(amt(0,200),2),"mnt_pdt_tar":round(amt(0,180),2),
        "cd_bck_ifrs9":bkt,"mnt_prov_b_ifrs9":0,"mnt_prov_hb_ifrs9":0,
        "annee_mois_part":"2026-05"
    })

with open(f"{OUT}/SERVICE.csv","w",newline="",encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=services[0].keys()); w.writeheader(); w.writerows(services)
print("SERVICE.csv OK")

# ── GSM ───────────────────────────────────────────────────────────────────────
gsm = []
for isin in ISINS:
    for ep in [e for e in epargne if e["isin_fds"]==isin][:5]:
        sfdr = random.choices(["Article 9 (Impact)","Article 8 (ESG)","Non classifié"],[1,3,6])[0]
        gsm.append({
            "isin_fds":isin,"id_contrat":ep["num_cnt"],"dt_fonc":"2026-05-31",
            "cd_ges":ep["cd_ges"],"mod_gest":ep["mod_gest"],"reseau":"LBP",
            "qte_fds":ep["qte_fds"],"cours_cot":round(amt(10,500),2),"dt_cot":"2026-05-30","avg_mnt_achat":round(amt(50,400),2),
            "enc_fds_m":ep["enc_fds_m"],"enc_cnt_n_1":ep["enc_cnt_n1"],
            "sum_enc_fds_cnt":ep["enc_fds_m"],"poids_isin_cnt":round(random.uniform(0.05,0.35),4),
            "sum_enc_fds_profil":round(ep["enc_fds_m"]*5,2),"poids_isin_profil":round(random.uniform(0.1,0.4),4),
            "sum_enc_fds_gsm":round(ep["enc_fds_m"]*20,2),"poids_isin_total_gsm":round(random.uniform(0.02,0.15),4),
            "apport_cli":round(ep["enc_fds_m"]*0.8,2),"performance_cli":round(amt(-0.05,0.15),4),"mnt_pmvl":round(amt(-10000,50000),2),
            "ind_sfdr_30000":1 if sfdr=="Article 9 (Impact)" else 0,
            "ind_sfdr_10000":1 if sfdr in ("Article 8 (ESG)","Article 9 (Impact)") else 0,
            "ind_sfdr_20150":random.choice([0,1]),"ind_sfdr_30010":random.choice([0,1]),
            "ind_sfdr_30020":random.choice([0,1]),"ind_sfdr_30060":random.choice([0,1]),
            "ind_sfdr_30100":random.choice([0,1]),"ind_sfdr_30140":random.choice([0,1]),
            "ind_sfdr_10040":random.choice([0,1]),"ind_sfdr_00050":random.choice([0,1]),
            "ind_taxo_20660":random.choice([0,1]),"ind_taxo_20670":random.choice([0,1]),
            "ind_taxo_20680":random.choice([0,1]),"ind_taxo_20690":random.choice([0,1]),
            "ind_taxo_20700":random.choice([0,1]),"ind_taxo_20710":random.choice([0,1]),
            "Classification_SFDR":sfdr
        })

with open(f"{OUT}/GSM.csv","w",newline="",encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=gsm[0].keys()); w.writeheader(); w.writerows(gsm)
print("GSM.csv OK")

print(f"\nTous les CSV sont dans : {OUT}")
print(f"CLIENT : {len(clients)} lignes")
print(f"TRANSACTION : {len(transactions)} lignes")
print(f"EPARGNE : {len(epargne)} lignes")
print(f"CREDIT : {len(credits)} lignes")
print(f"GARANTIE : {len(garanties)} lignes")
print(f"SERVICE : {len(services)} lignes")
print(f"GSM : {len(gsm)} lignes")
