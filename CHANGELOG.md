# Changelog

## Unreleased

### Added

- Comanda idempotentă `uv run manage.py seed_demo_data` pentru datasetul mock
  comun al echipei.
- Modelul `ItineraryConstraint` și migrarea `0004_itineraryconstraint`.
- Calcularea balances din `Expense` și `ExpenseShare`.
- Construirea contextului de itinerary din `Itinerary` și `ItineraryItem`.
- Generarea de tokenuri read-only aleatorii, cu stocare hash-uită și afișare
  o singură dată la creare.

### Changed

- UI-ul folosește date din PostgreSQL pentru trip, participanți, destinații,
  activități, itinerar, cheltuieli și balances.
- Linkurile read-only sunt validate în baza de date și verifică revocarea și
  expirarea.
- Datele mock nu mai sunt încărcate din `web/demo_data.py`.

### Removed

- `web/demo_data.py`, care conținea dicționarele statice ale prototipului.

### Upgrade notes

După actualizare, aplicați migrațiile și recreați datasetul mock doar dacă aveți
o bază locală nouă:

```sh
uv run manage.py migrate
uv run manage.py seed_demo_data
```
