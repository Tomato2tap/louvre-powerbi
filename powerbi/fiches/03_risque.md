# Board 3 — Risque & Conformité

**Objectif** : surveiller les **risques clients et la conformité LCB-FT/KYC**, prioriser les contrôles.
**Public** : conformité, LCB-FT, contrôle interne, risque.

## Indicateurs
| KPI | Mesure | Définition |
|-----|--------|------------|
| Clients sensibles | `Clients Sensibles` | Cotation E (douteux) ou F (contentieux) |
| KYC rouge | `Nb KYC Rouge` | `gelule_global = 10` — donnée à régulariser **obligatoirement** |
| KYC orange | `Nb KYC Orange` | `gelule_global = 5` — à mettre à jour |
| Tx sensibles | `Nb Transactions Sensibles` | Transactions marquées sensibles |
| Vol. sensible | `Volume Tx Sensibles` | Montant des transactions sensibles |
| Conformité KYC | `Taux Conformité KYC` | % clients KYC vert (`gelule_global = 0`) |

## Visuels
- **Entonnoir « Risque client »** : volumétrie par niveau (Solvable → Contentieux), du plus large au plus critique.
- **Barres « Volume par couleur pays (contrepartie) »** : exposition aux pays vert/orange/rouge.
- **Colonnes « Volume sensible par opération »** : quels types d'opérations concentrent le risque.
- **Table « Clients à risque »** : nom, risque, couleur pays, KYC, agence, AUM.

## Filtres
Type client · Agence (globaux) · Niveau de risque · Couleur pays.

## Lecture / insights
- Prioriser les **KYC rouge** à fort AUM (table triée par AUM).
- Les transactions vers pays **rouge/orange** (contrepartie) = revue AML.
- Le **taux de conformité KYC** est l'indicateur de pilotage réglementaire global.
