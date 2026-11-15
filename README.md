# tri_sync

Collaborative planner for trips

## Instalare

Instalați [uv](https://docs.astral.sh/uv/getting-started/installation/). Python nu trebuie instalat separat: uv descarcă automat o versiune compatibilă (≥ 3.13) dacă nu găsește una.

## Rulare

```sh
docker compose up -d db     # pornește PostgreSQL cu volum persistent
uv run manage.py migrate     # creează/actualizează schema PostgreSQL
uv run manage.py runserver   # pornește serverul pe http://127.0.0.1:8000
```

`uv run` creează și actualizează automat `.venv` cu dependențele din `pyproject.toml`, deci nu e nevoie să activați mediul virtual.
Setările PostgreSQL sunt citite din variabilele `POSTGRES_*`; copiați `.env.example` în `.env` pentru configurare locală.

## Interfata (aplicatia `web`)

Stratul de UI este aplicatia Django `web`. Deocamdata nu atinge baza de date:
ecranele sunt randate din `web/demo_data.py`, ca sa putem revizui HTML-ul si
CSS-ul inainte sa existe modelele. Cand apar modelele, view-urile inlocuiesc
dictionarele cu queryset-uri, iar sabloanele raman neschimbate.

Rute:

| URL                                            | Ecran                       |
| ---------------------------------------------- | --------------------------- |
| `/`                                            | Lista de excursii           |
| `/trips/new/`                                  | Creare excursie (organizator), 4 pasi |
| `/join/7f3b-91ac-24de/`                        | Invitatie: cont nou         |
| `/join/7f3b-91ac-24de/signin/`                 | Invitatie: cont existent    |
| `/join/7f3b-91ac-24de/welcome/`                | Ai intrat in grup           |
| `/join/expired/`                               | Link revocat                |
| `/trips/lisbon/`                               | Overview                    |
| `/trips/lisbon/decisions/`                     | Lista deciziilor, in ordine |
| `/trips/lisbon/decisions/propose/activity/`    | Propunere activitate        |
| `/trips/lisbon/decisions/propose/destination/` | Propunere destinatie        |
| `/trips/lisbon/decisions/proposals/`           | Aprobare propuneri (organizator) |
| `/trips/lisbon/decisions/activities/close/`    | Inchidere votare (organizator)   |
| `/trips/lisbon/decisions/constraints/`         | Constrangeri inainte de generare |
| `/trips/lisbon/itinerary/build/`               | Itinerar generat, cu motive      |
| `/trips/lisbon/decisions/destination/`         | Vot destinatie (da/nu)      |
| `/trips/lisbon/decisions/stay/`                | Vot cazare (o optiune)      |
| `/trips/lisbon/decisions/activities/`          | Scoruri activitati (1-5)    |
| `/trips/lisbon/decisions/transfers/`           | Vot transfer aeroport       |
| `/trips/lisbon/itinerary/`                     | Itinerar pe zile            |
| `/trips/lisbon/itinerary/map/`                 | Harta zilei: cazare, opriri, traseu |
| `/trips/lisbon/itinerary/share/`               | Link read-only: creare / revocare |
| `/share/c41d-8f22-7b90/`                       | Ce vede un vizitator (inclusiv harta zilei, fara cazare) |
| `/share/expired/`                              | Link read-only revocat      |
| `/trips/lisbon/expenses/`                      | Cheltuieli si buget cheltuit |
| `/trips/lisbon/expenses/new/`                  | Inregistrare cheltuiala     |
| `/trips/lisbon/expenses/balances/`             | Cine cui datoreaza          |
| `/styleguide/`                                 | Toate componentele, pe o pagina |

Structura CSS (`web/static/web/css/`):

- `tokens.css` - culori, tipografie, spatiere, raze, latimi. Singurul loc cu
  valori brute; restul fisierelor citesc doar variabile de aici.
- `base.css` - reset si stiluri de element.
- `layout.css` - shell-ul aplicatiei si grilele de pagina (`.split`, `.stack`).
- `components/*.css` - cate un fisier per componenta (buton, card, formular,
  stepper, optiune de vot, scala 1-5, timeline, etc.).
- `pages/*.css` - putinele reguli specifice unui singur ecran.
- `main.css` - singurul fisier legat in `base.html`; importa restul in ordine.

Fotografiile lipsesc din prototip: fiecare slot `.photo--<nume>` are un gradient
in `components/photo.css`. Pentru o poza reala, pune fisierul in
`web/static/web/img/` si suprascrie regula respectiva.

Cand adaugati un ecran nou, compuneti-l din componentele existente (vezi
`/styleguide/`) si adaugati CSS nou doar daca apare cu adevarat un tipar nou.

## Comenzi Django

```sh
uv run manage.py makemigrations    # după ce modificați modelele
uv run manage.py migrate           # aplică migrările
uv run manage.py createsuperuser   # cont de admin pentru /admin
uv run manage.py startapp <nume>   # aplicație nouă; adăugați-o în INSTALLED_APPS din trip_sync/settings.py
uv run manage.py test              # rulează testele
```

## Comenzi uv

```sh
uv sync                 # aduce .venv la zi (ex. după git pull, ca editorul să vadă pachetele noi)
uv run <comandă>        # rulează o comandă în .venv
uv add <pachet>         # adaugă o dependență în pyproject.toml
uv add --dev <pachet>   # dependență doar pentru dezvoltare (ex. pytest)
uv remove <pachet>      # elimină o dependență
uv lock --upgrade       # trece pachetele la cele mai noi versiuni permise de pyproject.toml
uv tree                 # afișează arborele de dependențe
```

Nu folosiți `pip install`. Cu `uv add`, pachetul este adăugat automat în `pyproject.toml`, deci nu mai trebuie să actualizați `requirements.txt`, iar colegii îl primesc la următorul `uv run` sau `uv sync`.
