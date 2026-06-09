# Board 2 — Digital & Adoption

**Objectif** : suivre l'**adoption digitale** et l'usage des canaux, repérer les comptes à problème.
**Public** : marketing digital, équipes opérations/relation client.

## Indicateurs
| KPI | Mesure | Définition |
|-----|--------|------------|
| Clients | `Nb Clients Totaux` | Base clients active |
| Enrôlés | `Nb Clients Enrollés` | Clients avec ≥ 1 terminal de confiance |
| Smartphones | `Nb Smartphones` | Total terminaux enrôlés (`nb_dev_enrol`) |
| Taux enrôl. | `Taux Enrollment` | Enrôlés / total |
| Bloqués | `Nb Comptes Bloqués` | Accès digital bloqué (`etat_acc = B`) — **opérationnel** |
| Suspendus | `Nb Comptes Suspendus` | Accès suspendu (`etat_acc = S`) |

## Visuels
- **Donut « Transactions par canal »** : poids de chaque canal (Mobile, iOS, Web, Android, Agence, SVI).
- **Aire « Tendance — volume des transactions par mois »** : évolution temporelle du volume (axe = `dt_realisation`).
- **Colonnes « Clients enrôlés par type d'enrôlement »**.
- **Table « Clients à surveiller »** : nom, état accès, type enrôl., nb appareils, agence, risque.

## Filtres
Type client · Agence (globaux) · État accès · Type d'enrôlement.

## Lecture / insights
- Suivre la **bascule vers le mobile** (Mobile + iOS + Android vs Web/Agence).
- Le couple **Bloqués/Suspendus** signale un risque opérationnel ou de fraude à traiter.
- Un faible taux d'enrôlement sur une agence = action commerciale digitale à mener.
