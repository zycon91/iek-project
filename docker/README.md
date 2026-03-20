# Docker Setup

## Εκκίνηση της βάσης δεδομένων

```bash
cd docker
docker compose up -d
```

## Εκκίνηση του backend locally

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Το `.env` στον φάκελο `backend` είναι ήδη σωστά ρυθμισμένο:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/project
```

## Διακοπή της βάσης

```bash
docker compose down
```

Για να διαγράψεις και τα δεδομένα:
```bash
docker compose down -v
```
