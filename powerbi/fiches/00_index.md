# Louvre Banque Privée — Fiches explicatives des boards

Rapport Power BI `LoBP_CustomerIntent` — thème sombre premium (teal), 7 boards.
Modèle en étoile centré sur **CLIENT** (relations vers TRANSACTION, EPARGNE, CREDIT, SERVICE, GARANTIE).
Données arrêtées au mois courant (champ `dt_fonc`).

## Sommaire des boards
| # | Board | Public cible | Usage principal |
|---|-------|--------------|-----------------|
| 1 | [Synthèse Exécutive](01_synthese.md) | Direction / COMEX | Vue 360° en un écran |
| 2 | [Digital & Adoption](02_digital.md) | Marketing / Digital / Ops | Enrôlement & usage des canaux |
| 3 | [Risque & Conformité](03_risque.md) | Conformité / LCB-FT / Risque | Clients sensibles, KYC, AML |
| 4 | [Commercial & Relation Client](04_commercial.md) | Conseillers / Direction co. | Segmentation, portefeuille, AUM |
| 5 | [Patrimoine — Épargne & Crédit](05_patrimoine.md) | Gestion privée | Encours, collecte, supports |
| 6 | [Crédit & Engagements](06_credit.md) | Risque crédit / Engagements | Encours, impayés, LTV, garanties |
| 7 | [Analyse Avancée 360°](07_analyse.md) | Analystes / Data | Exploration multi-visuels |

## Interactions communes à tous les boards
- **Filtres globaux synchronisés** : *Type client* et *Agence* se propagent à **toutes les pages** (groupes de synchronisation `g_type` / `g_agence`).
- **Filtres locaux** : 2 slicers spécifiques par board (ex. Pays, État créance…).
- **Cross-filtering** : cliquer un élément (part de donut, barre…) filtre tous les autres visuels de la page.
- **Drill-down** : certains graphes ont une hiérarchie (double-clic / flèches de drill), ex. Pays › Agence.
- **Navigateur de pages** : boutons en haut à droite de chaque board (en plus des onglets en bas).

## Conventions de lecture
- Montants en **unités automatiques** : `K` = milliers, `M` = millions d'euros.
- Couleurs de risque : vert = sain/solvable, orange = sensible, rouge = douteux/contentieux.
- Accent **teal** = mesure clé ; **or** = alerte / point d'attention.

> Les mesures DAX sont regroupées dans la table masquée `_M_Dashboard`. Le rapport est généré par `build_customerintent.py`.
