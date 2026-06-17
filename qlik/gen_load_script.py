# -*- coding: utf-8 -*-
"""
Genere un script de chargement Qlik Sense PROPRE a partir des CSV Louvre.
Objectif : modele en etoile sans cle synthetique ni reference circulaire.

Regles de liaison (champs gardes NON prefixes = cles de liaison) :
  CLIENT      : table maitre  -> tous champs non prefixes (id_cli = cle)
  TRANSACTION : -> CLIENT par id_cli            (prefixe TR_ sur le reste, y compris num_cnt)
  EPARGNE     : -> CLIENT par id_cli, -> GSM par isin_fds  (prefixe EP_ sur le reste)
  SERVICE     : -> CLIENT par id_cli            (prefixe SV_ sur le reste)
  CREDIT      : -> CLIENT par id_cli, -> GARANTIE par num_cnt (garde id_cli + num_cnt)
  GARANTIE    : -> CREDIT par num_cnt SEULEMENT (prefixe GA_, y compris id_cli, pour casser la boucle CLIENT-CREDIT-GARANTIE)
  GSM         : -> EPARGNE par isin_fds         (prefixe GS_ sur le reste)
"""
import csv, os, io

DATA = os.path.join(os.path.dirname(__file__), "..", "powerbi", "data")
OUT  = os.path.join(os.path.dirname(__file__), "10_load_louvre_csv.qvs")

# Pour chaque table : abbrev de prefixe + set des champs gardes NON prefixes (liaisons)
TABLES = {
    "CLIENT":      ("",   None),                       # None = tout garder tel quel
    "TRANSACTION": ("TR", {"id_cli"}),
    "EPARGNE":     ("EP", {"id_cli", "isin_fds"}),
    "SERVICE":     ("SV", {"id_cli"}),
    "CREDIT":      ("CR", {"id_cli", "num_cnt"}),
    "GARANTIE":    ("GA", {"num_cnt"}),
    "GSM":         ("GS", {"isin_fds"}),
}

def header(path):
    with io.open(path, "r", encoding="utf-8-sig", newline="") as f:
        return next(csv.reader(f))

def field_lines(cols, prefix, keep):
    out = []
    for c in cols:
        c = c.strip()
        if not c:
            continue
        if prefix == "" or (keep and c in keep):
            out.append(f"    [{c}]")
        else:
            out.append(f"    [{c}] AS [{prefix}_{c}]")
    return ",\n".join(out)

def main():
    parts = []
    parts.append("""// ============================================================
// LOUVRE BANQUE PRIVEE - CHARGEMENT CSV (modele etoile propre)
// Genere par gen_load_script.py - NE PAS editer a la main
// Cibles : Qlik Sense Desktop OU Qlik Cloud
// ============================================================

// --- Variables d'interpretation alignees sur les CSV (decimale '.', dates ISO) ---
SET ThousandSep=',';
SET DecimalSep='.';
SET MoneyThousandSep=' ';
SET MoneyDecimalSep=',';
SET MoneyFormat='# ##0 €';
SET DateFormat='YYYY-MM-DD';
SET TimestampFormat='YYYY-MM-DD hh:mm:ss';

// --- Chemin des donnees ---
// Desktop : mettre le dossier local (ex: 'E:\\louvre\\powerbi\\data')
// Cloud   : remplacer par la connexion espace, ex: 'lib://DataFiles'
SET vPath = 'E:\\louvre\\powerbi\\data';

""")

    fmt = "(txt, utf8, embedded labels, delimiter is ',', msq)"
    for tbl, (prefix, keep) in TABLES.items():
        path = os.path.join(DATA, tbl + ".csv")
        cols = header(path)
        body = field_lines(cols, prefix, keep)
        parts.append(f"""// ------------------------------------------------------------
[{tbl}]:
LOAD
{body}
FROM [$(vPath)\\{tbl}.csv]
{fmt};

""")

    # Calendrier derive des dates CLIENT/transactions pour les axes temporels
    parts.append("""// ------------------------------------------------------------
// CALENDRIER (axe temps a partir des dates de transactions)
[CALENDRIER]:
LOAD DISTINCT
    Date(Floor([TR_dt_realisation]))                         AS [Date],
    Year([TR_dt_realisation])                                AS [Annee],
    Num(Month([TR_dt_realisation]),'00')                     AS [MoisNum],
    Date(MonthStart([TR_dt_realisation]),'YYYY-MM')          AS [AnneeMois]
RESIDENT [TRANSACTION]
WHERE Len(Trim([TR_dt_realisation])) > 0;

// FIN DU SCRIPT
""")

    with io.open(OUT, "w", encoding="utf-8") as f:
        f.write("".join(parts))
    print("Ecrit :", os.path.abspath(OUT))

if __name__ == "__main__":
    main()
