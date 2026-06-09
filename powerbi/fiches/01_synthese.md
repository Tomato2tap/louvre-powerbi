# Board 1 — Synthèse Exécutive

**Objectif** : donner à la direction une **vue 360° de l'activité en un seul écran** (patrimoine, activité, conformité, digital).
**Public** : COMEX, direction d'agence.

## Indicateurs (cartes KPI, colonne gauche)
| KPI | Mesure | Définition |
|-----|--------|------------|
| Clients | `Nb Clients Totaux` | Clients actifs (relation `CL` ou `CT`) — hors prospects |
| AUM Total | `AUM Total` | Encours sous gestion des titulaires (`aum_tit`) |
| Encours Épargne | `Encours Épargne` | Encours contrats épargne du mois |
| Encours Crédit | `Encours Crédit Total` | Capital restant dû crédits |
| Collecte Nette | `Collecte Nette` | Collecte brute − décollecte |
| Clients Actifs | `Nb Clients Actifs` | Clients avec activité (`top_client_actif = O`) |
| Clients Sensibles | `Clients Sensibles` | Risque E (douteux) ou F (contentieux) — **alerte** |
| Taux Enrôlement | `Taux Enrollment` | % clients ayant ≥ 1 terminal enrôlé |

## Visuels
- **Donut « Clients par pays › agence »** : répartition géographique de la clientèle ; **drill-down** Pays → Agence (double-clic).
- **Aires empilées « Volume des transactions par opération et canal »** : poids de chaque type d'opération, décomposé par canal.
- **Table « Détail clients »** : nom, type, pays, agence, risque + AUM / Épargne / Crédit par client.

## Filtres
Type client · Agence (globaux) · Pays · Groupe de risque.

## Lecture / insights
- Repérer la concentration du patrimoine (un pays/agence pèse-t-il trop ?).
- Croiser **Clients Sensibles** (alerte) avec l'AUM : un client à risque mais à fort encours = priorité.
- La table triable sert de point d'entrée pour identifier les clients à fort potentiel ou à surveiller.
