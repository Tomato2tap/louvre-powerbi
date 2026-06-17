# -*- coding: utf-8 -*-
"""
Construit l'app Qlik Sense "Louvre Banque Privee" via l'Engine API.
Etapes : connecte -> cree/ouvre app -> injecte script CSV -> reload
         -> cree master measures + dimensions -> sauvegarde.
Les feuilles/visualisations sont ajoutees par build_sheets.py (iteratif).

Usage :
    python build_app.py            # pipeline complet (sans feuilles)
    python build_app.py --reload   # re-set script + reload seulement
"""
import os
import sys
import re

from engine import QlikEngine, GLOBAL_HANDLE
import board_spec as spec

HERE = os.path.dirname(__file__)
SCRIPT_FILE = os.path.join(HERE, "10_load_louvre_csv.qvs")


def num_format(fmt):
    """Mappe un format texte -> FieldAttributes Qlik."""
    if fmt == "#,##0":
        return {"qType": "I", "qnDec": 0, "qFmt": "#,##0", "qThou": " ", "qDec": ","}
    if fmt.endswith("%"):
        return {"qType": "F", "qnDec": 1, "qFmt": fmt, "qDec": ","}
    if "€" in fmt:
        return {"qType": "M", "qnDec": 0, "qFmt": "# ##0 €", "qThou": " ", "qDec": ","}
    return {"qType": "U", "qFmt": fmt}


def open_or_create_app(eng, name):
    docs = eng.call("GetDocList").get("qDocList", [])
    for d in docs:
        if d.get("qDocName") == name or d.get("qDocName") == name + ".qvf":
            print("  App existante -> OpenDoc")
            r = eng.call("OpenDoc", GLOBAL_HANDLE, {"qDocName": d["qDocId"]})
            return r["qReturn"]["qHandle"], d["qDocId"]
    print("  Creation app...")
    r = eng.call("CreateApp", GLOBAL_HANDLE, {"qAppName": name})
    app_id = r.get("qAppId") or r.get("qDocId")
    o = eng.call("OpenDoc", GLOBAL_HANDLE, {"qDocName": app_id})
    return o["qReturn"]["qHandle"], app_id


def load_script_text():
    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        txt = f.read()
    # force le chemin local des CSV
    txt = re.sub(r"SET vPath = '.*?';",
                 "SET vPath = '%s';" % spec.DATA_PATH.replace("\\", "\\\\"),
                 txt, count=1)
    return txt


def set_script_and_reload(eng, app):
    print("  SetScript...")
    eng.call("SetScript", app, {"qScript": load_script_text()})
    print("  DoReload...")
    res = eng.call("DoReloadEx", app, {"qMode": 0, "qPartial": False, "qDebug": False})
    ok = res.get("qResult", {}).get("qSuccess", res.get("qSuccess"))
    print("  Reload success:", ok)
    return ok


def create_measures(eng, app):
    created = 0
    for title, expr, fmt in spec.MEASURES:
        prop = {
            "qInfo": {"qType": "measure"},
            "qMeasure": {"qLabel": title, "qDef": expr, "qNumFormat": num_format(fmt)},
            "qMetaDef": {"title": title, "tags": ["LoBP"]},
        }
        try:
            eng.call("CreateMeasure", app, {"qProp": prop})
            created += 1
        except Exception as e:
            print("    [KO mesure]", title, "->", e)
    print(f"  Mesures creees : {created}/{len(spec.MEASURES)}")


def create_dimensions(eng, app):
    created = 0
    for title, field in spec.DIMENSIONS:
        prop = {
            "qInfo": {"qType": "dimension"},
            "qDim": {"qGrouping": "N", "qFieldDefs": [field],
                     "qFieldLabels": [title], "title": title},
            "qMetaDef": {"title": title, "tags": ["LoBP"]},
        }
        try:
            eng.call("CreateDimension", app, {"qProp": prop})
            created += 1
        except Exception as e:
            print("    [KO dim]", title, "->", e)
    print(f"  Dimensions creees : {created}/{len(spec.DIMENSIONS)}")


def main():
    reload_only = "--reload" in sys.argv
    print("Connexion moteur...")
    eng = QlikEngine().connect()
    print("  ok:", eng.url)
    print("Ouverture/creation app:", spec.APP_NAME)
    app, app_id = open_or_create_app(eng, spec.APP_NAME)
    print("  app handle:", app, "id:", app_id)

    ok = set_script_and_reload(eng, app)
    if not reload_only and ok:
        create_dimensions(eng, app)
        create_measures(eng, app)

    print("Sauvegarde...")
    eng.call("DoSave", app, {})
    print("OK. App:", app_id)
    eng.close()


if __name__ == "__main__":
    main()
