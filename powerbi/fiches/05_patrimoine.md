# Board 5 — Patrimoine : Épargne & Crédit

**Objectif** : suivre les **encours d'épargne, la collecte** et les supports d'investissement.
**Public** : gestion privée, pilotage produit.

## Indicateurs
| KPI | Mesure | Définition |
|-----|--------|------------|
| Encours Épargne | `Encours Épargne` | Encours contrats épargne du mois |
| Collecte Brute | `Collecte Brute` | Entrées brutes |
| Décollecte | `Décollecte` | Sorties (valeur négative) |
| Collecte Nette | `Collecte Nette` | Brute + décollecte |
| Encours Crédit | `Encours Crédit Total` | Capital restant dû |
| Capital Impayé | `Capital Impayé` | Part impayée des crédits — **alerte** |

## Visuels
- **Colonnes « Encours épargne par famille › fonds »** : poids des familles produit ; **drill-down** Famille → Fonds.
- **Cascade « Collecte nette par famille »** : contribution (positive/négative) de chaque famille au flux net.
- **Barres « Encours crédit par marché »** : répartition immobilier / conso / etc.
- **Table « Fonds — encours par support »** : fonds, famille, mode de gestion, encours fonds.

## Filtres
Type client · Agence (globaux) · Famille produit · Mode de gestion (Libre / Mandat).

## Lecture / insights
- La **cascade** identifie immédiatement les familles en décollecte (barres rouges) à redresser.
- Croiser **mode de gestion** (mandat vs libre) avec l'encours = pilotage de l'offre gérée.
- Surveiller le ratio **Capital impayé / Encours crédit** comme signal de qualité du portefeuille.
