# Board 7 — Analyse Avancée 360°

**Objectif** : **explorer librement** les données via une vitrine de visuels variés (croisements, distributions, géographie).
**Public** : analystes, data, contrôle de gestion.

## Visuels
| Visuel | Type | Lecture |
|--------|------|---------|
| **Tableau croisé dynamique** | matrice (pivotTable) | AUM par **Type client × Groupe de risque**, avec sous-totaux lignes/colonnes |
| **Nuage de bulles** | scatter | Chaque **client** positionné : X = AUM, Y = Épargne, taille = Crédit → repère les profils atypiques |
| **Jauge** | gauge | **Taux de conformité KYC** d'un coup d'œil |
| **Carte** | filledMap | **AUM par pays** (géolocalisation) — nécessite les cartes Bing activées |
| **Cascade** | waterfall | Contribution de chaque famille à la **collecte nette** |
| **Ruban** | ribbon | **Volume par opération & canal** avec classement qui évolue |
| **Entonnoir** | funnel | **Clients par niveau de risque** |

## Filtres
Type client · Agence (globaux) · Pays · Niveau de risque.

## Lecture / insights
- La **matrice** sert d'analyse croisée rapide (exportable) : où se concentre l'AUM ?
- Les **bulles** détectent les clients déséquilibrés (gros crédit / faible épargne, ou inverse).
- La **carte** visualise l'exposition géographique du patrimoine.
- Page idéale pour l'**ad-hoc** : tous les visuels réagissent au cross-filtering et aux filtres globaux.

> ⚠️ Si la **carte** reste grise : activer « Cartes et cartes choroplèthes » (Fichier → Options → Sécurité, et paramètre admin du tenant pour la version en ligne).
