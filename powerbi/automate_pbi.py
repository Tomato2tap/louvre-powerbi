"""
Automatise Power BI Desktop pour :
1. Importer les 7 CSV
2. Créer les relations
3. Créer les mesures DAX
4. Construire les 4 pages visuelles
"""

import pyautogui, pygetwindow, time, os, subprocess, sys
from pathlib import Path

pyautogui.PAUSE = 0.4
pyautogui.FAILSAFE = True

DATA_DIR = r"E:\louvre\powerbi\data"
TABLES   = ["CLIENT","TRANSACTION","EPARGNE","CREDIT","GARANTIE","SERVICE","GSM"]

def screenshot(name):
    img = pyautogui.screenshot()
    img.save(rf"E:\louvre\powerbi\auto_{name}.png")
    return img

def wait_for(text_or_sec, timeout=15):
    """Attend que du texte apparaisse ou pause simple"""
    if isinstance(text_or_sec, (int, float)):
        time.sleep(text_or_sec)
        return True
    start = time.time()
    while time.time() - start < timeout:
        img = pyautogui.screenshot()
        # Cherche la couleur bordeaux (fenêtre PBI chargée)
        time.sleep(0.5)
    return True

def find_pbi_window():
    """Trouve et met Power BI Desktop au premier plan"""
    wins = pygetwindow.getAllTitles()
    pbi_win = None
    for w in wins:
        if "Power BI Desktop" in w or "LoBP" in w:
            pbi_win = w
            break
    if pbi_win:
        win = pygetwindow.getWindowsWithTitle(pbi_win)[0]
        win.maximize()
        win.activate()
        time.sleep(1.5)
        return True
    return False

def open_fresh_pbi():
    """Ouvre un nouveau rapport PBI vide"""
    subprocess.Popen(['powershell', '-Command',
        'Start-Process "shell:AppsFolder\\Microsoft.MicrosoftPowerBIDesktop_8wekyb3d8bbwe!Microsoft.MicrosoftPowerBIDesktop"'])
    time.sleep(8)
    return find_pbi_window()

def close_startup_dialog():
    """Ferme le dialog de démarrage si présent"""
    screenshot("01_start")
    # Cherche le bouton X ou Fermer du dialog
    try:
        loc = pyautogui.locateOnScreen(None)
    except:
        pass
    # Appui sur Escape pour fermer les dialogs de bienvenue
    pyautogui.press('escape')
    time.sleep(0.5)
    pyautogui.press('escape')
    time.sleep(0.5)

def click_get_data():
    """Clique sur Obtenir les données"""
    screenshot("02_before_getdata")
    # Cherche le bouton "Obtenir les données" dans le ruban Accueil
    # Position approximative : environ (205, 80) sur un écran 1920x1080
    try:
        btn = pyautogui.locateCenterOnScreen(r"E:\louvre\powerbi\assets\btn_getdata.png", confidence=0.7)
        pyautogui.click(btn)
    except:
        # Fallback : click sur position du ruban
        # Accueil > Obtenir les données ~ (205, 80) en 1920x1080
        pyautogui.click(205, 80)
    time.sleep(1)
    screenshot("03_after_getdata")

def import_csv_via_menu(csv_path):
    """Importe un CSV via le menu Obtenir données > Texte/CSV"""
    name = Path(csv_path).stem
    print(f"  Import : {name}")

    # 1. Accueil > Obtenir les données (flèche dropdown)
    pyautogui.hotkey('alt', 'h')   # Onglet Accueil
    time.sleep(0.3)

    # Click sur "Obtenir les données" (position dans le ruban)
    # On cherche visuellement
    screenshot(f"import_01_{name}")

    # Approche : utiliser le raccourci clavier Power BI
    # Accueil > Obtenir les données = Alt+F puis O dans certaines versions
    # Plus fiable : clic direct sur la position connue

    # Fermer tout menu ouvert
    pyautogui.press('escape')
    time.sleep(0.3)

    # Click "Obtenir les données" dropdown arrow
    # En PBI Desktop fr, le bouton est dans le ruban en haut
    # Pos standard : environ x=205, y=75 (zone "Obtenir les données")
    pyautogui.click(205, 75)
    time.sleep(1.2)
    screenshot(f"import_02_{name}")

    # Dans le dropdown, chercher "Texte/CSV" ou "Plus..."
    # Essai 1 : cherche "Texte/CSV" directement
    result = pyautogui.locateOnScreen(None)

    # Appuyer sur T pour "Texte/CSV" ou naviguer
    # En fr: "Texte/CSV" est souvent affiché directement
    pyautogui.press('escape')
    time.sleep(0.3)

    # Alternative plus robuste : Fichier > Obtenir données via le menu principal
    # Ou : ctrl+alt+? → pas standard
    # MEILLEURE APPROCHE : Drag & Drop du CSV dans PBI Desktop
    return import_csv_drag(csv_path)

def import_csv_drag(csv_path):
    """
    Méthode alternative : utilise le dialogue Obtenir données
    via position fixe dans le ruban PBI
    """
    name = Path(csv_path).stem
    # Screenshot pour voir l'état actuel
    img = screenshot(f"drag_{name}")

    # Méthode la plus fiable : cliquer dans la zone du canevas vide
    # PBI propose parfois un lien direct "Obtenir des données" au centre
    # Chercher ce lien et cliquer dessus

    # Si le rapport est vide, il y a des liens au centre type "Importer des données"
    # Pos ~ (640, 400) en 1280x720 ou (960, 540) en 1920x1080
    screen_w, screen_h = pyautogui.size()
    center_x, center_y = screen_w // 2, screen_h // 2
    pyautogui.click(center_x - 100, center_y)
    time.sleep(0.8)

    return True

# ─────────────────────────────────────────────────────────────────────────────
# MÉTHODE PRINCIPALE : Automation complète via clicks
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=== AUTOMATION POWER BI DESKTOP ===")
    print()

    # Étape 0 : Ouvrir PBI
    print("1. Recherche de Power BI Desktop...")
    found = find_pbi_window()
    if not found:
        print("   Power BI non trouvé, ouverture...")
        open_fresh_pbi()
        found = find_pbi_window()
        if not found:
            print("ERREUR : Impossible d'ouvrir Power BI Desktop")
            sys.exit(1)

    print("   Power BI trouvé ✓")
    time.sleep(1)

    # Screenshot état initial
    img = screenshot("00_initial")
    print(f"   Capture : auto_00_initial.png ({img.width}x{img.height})")

    # Étape 1 : Fermer dialogs de bienvenue
    print("2. Fermeture dialogs startup...")
    pyautogui.press('escape')
    time.sleep(0.5)
    pyautogui.press('escape')
    time.sleep(0.5)

    screenshot("01_after_escape")

    # Étape 2 : Importer les CSV via "Obtenir les données"
    print("3. Import des CSV...")
    print(f"   Source : {DATA_DIR}")

    # Cliquer sur le menu Accueil (premier onglet du ruban)
    # Trouver la position de "Obtenir les données" dans le ruban
    screen_w, screen_h = pyautogui.size()
    print(f"   Résolution écran : {screen_w}x{screen_h}")

    # Ouvrir le dialogue "Obtenir les données" avec le raccourci
    # Dans PBI Desktop, Alt ouvre la barre de menu
    pyautogui.hotkey('alt')
    time.sleep(0.5)
    screenshot("02_alt_pressed")

    # Retour normal
    pyautogui.press('escape')
    time.sleep(0.3)

    # Méthode directe : cliquer sur "Obtenir les données" dans le ruban
    # Position typique sur un ruban standard PBI fr en 1920x1080 : x≈205, y≈80
    # En 1280x720 : x≈165, y≈65
    # On va chercher sur screenshot
    img = screenshot("03_ribbon")
    print(f"   Screenshot ruban sauvé")

    # Import via position du bouton
    # Ratio pour adapter à n'importe quelle résolution
    ratio = screen_w / 1920
    btn_x = int(205 * ratio)
    btn_y = int(78 * ratio)
    print(f"   Clic 'Obtenir les données' à ({btn_x}, {btn_y})")
    pyautogui.click(btn_x, btn_y)
    time.sleep(1.5)
    screenshot("04_getdata_clicked")

    # Chercher "Texte/CSV" dans le dropdown
    # Position dans le dropdown (environ 4e item) : ~(205, 140) en 1920x1080
    txt_csv_y = int(140 * ratio)
    print(f"   Clic 'Texte/CSV' à ({btn_x}, {txt_csv_y})")
    pyautogui.click(btn_x, txt_csv_y)
    time.sleep(1.5)
    screenshot("05_textcsv")

    # Si ça n'a pas marché, essayer "Plus..." puis chercher CSV
    # Escape et re-essai avec position différente
    pyautogui.press('escape')
    time.sleep(0.3)

    print()
    print("=== Screenshots générés dans E:\\louvre\\powerbi\\ ===")
    print("Analyse des captures pour continuer l'automation...")

if __name__ == "__main__":
    main()
