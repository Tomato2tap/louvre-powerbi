# Board 6 — Crédit & Engagements

**Objectif** : piloter le **portefeuille de crédit** : encours, qualité (impayés/IFRS9), risque (LTV, TEG) et **couverture par garanties**.
**Public** : risque crédit, engagements, direction financière.

## Indicateurs
| KPI | Mesure | Définition |
|-----|--------|------------|
| Encours Crédit | `Encours Crédit Total` | Capital restant dû (`enc_cpt`) |
| Nb Crédits | `Nb Crédits` | Nombre de contrats de prêt distincts |
| Débloqué | `Montant Débloqué` | Capital effectivement versé (`mnt_dblq`) |
| Capital Impayé | `Capital Impayé` | Part impayée (`mnt_krd_imp`) — **alerte** |
| Taux Impayés | `Taux Impayés` | Impayé / capital restant dû total |
| Couverture Gar. | `Taux Couverture Garanties` | Garanties comptables / encours crédit |

Mesures complémentaires disponibles : `Montant Nominal`, `Reste à Débloquer`, `LTV Moyenne` (Prêt/Valeur du bien), `TEG Moyen`, `Provisions IFRS9 Crédit`, `RWA Crédit`, `Montant Garanties`.

## Visuels
- **Colonnes « Encours par type de prêt › marché »** : structure du portefeuille ; **drill-down** Type → Marché.
- **Combo « Encours (barres) & taux d'impayés (ligne) par marché »** : volume vs qualité sur deux axes — repère les marchés volumineux **et** dégradés.
- **Donut « Répartition par bucket IFRS9 »** : Sain / Sensible / Douteux-Contentieux.
- **Table « Détail crédits »** : type prêt, marché, état créance, nominal, encours, **LTV moyenne**, provisions, garanties.

## Filtres
Type client · Agence (globaux) · Marché (`lib_typ_mar`) · État créance (Sain / Sensible / Douteux / Contentieux).

## Lecture / insights
- Le **combo** met en évidence un marché à fort encours mais **taux d'impayés élevé** = exposition prioritaire.
- Le **donut IFRS9** donne la photo de la qualité ; surveiller la part « Douteux/Contentieux ».
- Croiser **LTV moyenne** et **couverture garanties** : un encours élevé avec faible couverture = risque de perte en cas de défaut.
- `Provisions IFRS9` et `RWA Crédit` permettent le lien avec le pilotage prudentiel.
