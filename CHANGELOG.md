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
- Autentificare: `/register/` (cont nou), `/login/` (email + parolă) și
  `/logout/` (POST, butonul „Sign out” din header).
- Formularele de pe linkul de invitație (`/join/<token>/`) creează contul sau
  autentifică utilizatorul și îl adaugă ca participant dacă invitația e activă.
- Crearea unei excursii (`/trips/new/`, 4 pași): nume (obligatoriu), descriere
  și destinație (opționale), datele de plecare și întoarcere (durata rezultă din
  ele), bugetul total, moneda și numărul de persoane. Primii trei pași sunt
  validați și ținuți în sesiune; excursia se salvează la pasul de buget, cu
  utilizatorul logat ca organizator și participant.
  `budget_per_person` = buget total / persoane. Destinația dată la creare devine
  `final_destination` (o `Destination` aprobată).
- Pasul 4, invitații (FR-06): invitație pe email (câte un token per persoană,
  email trimis prin backend-ul de mail configurat), anularea unei invitații și
  linkul de grup, cu „New link” care îl revocă pe cel vechi. Ca la linkul
  read-only, tokenul brut al linkului de grup e afișat o singură dată și se
  păstrează doar hash-ul (nici în sesiune).
- Teste: `NewTripTests` și `InviteStepTests` în `web/tests.py`.

### Changed

- Toate paginile cer utilizator autentificat (`LoginRequiredMiddleware`), cu
  excepția login, register, invitații și linkuri read-only.
- Lista de pe `/` arată doar excursiile la care participă utilizatorul logat
  (R-04), cu numele excursiei; fără excursii apare un mesaj gol.
- Pașii de creare sunt acum `basics`, `when`, `budget`, `invite`.
- Linkul de invitație (`/join/<token>/`) afișează excursia invitației, nu primul
  trip din bază; un link revocat sau inexistent duce la `/join/expired/`.
- Header-ul afișează utilizatorul logat, nu organizatorul primului trip.
- UI-ul folosește date din PostgreSQL pentru trip, participanți, destinații,
  activități, itinerar, cheltuieli și balances.
- Linkurile read-only sunt validate în baza de date și verifică revocarea și
  expirarea.
- Datele mock nu mai sunt încărcate din `web/demo_data.py`.

### Fixed

- `settings.py` citește acum `.env`, la fel ca `docker compose`. Înainte,
  Django folosea parola implicită `trip_sync` în timp ce containerul era creat
  cu parola din `.env`, iar `migrate` eșua cu „password authentication failed”.
- `new_trip_when.html` avea sintaxa de template stricată (`{% if %}` rupt pe
  mai multe linii), iar pașii din `ui_data` nu aveau template-uri, deci fluxul
  de creare crăpa după primul pas.

### Removed

- `web/demo_data.py`, care conținea dicționarele statice ale prototipului.

### Upgrade notes

După actualizare, aplicați migrațiile și recreați datasetul mock doar dacă aveți
o bază locală nouă:

```sh
uv run manage.py migrate
uv run manage.py seed_demo_data
```
