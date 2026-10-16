# tri_sync

Collaborative planner for trips

## Instalare

Instalați [uv](https://docs.astral.sh/uv/getting-started/installation/). Python nu trebuie instalat separat: uv descarcă automat o versiune compatibilă (≥ 3.13) dacă nu găsește una.

## Rulare

```sh
uv run manage.py migrate     # creează/actualizează baza de date (db.sqlite3)
uv run manage.py runserver   # pornește serverul pe http://127.0.0.1:8000
```

`uv run` creează și actualizează automat `.venv` cu dependențele din `pyproject.toml`, deci nu e nevoie să activați mediul virtual.

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
