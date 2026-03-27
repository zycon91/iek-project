# Εγκατάσταση του backend

## Install Dependencies

- πηγαίνουμε στον φάκελο backend

```bash
cd backend
```

- φτιάχνουμε ένα virtual environment

```bash
python -m venv .venv
```

- μπαίνουμε στο virtual environment (άμα δεν μας βάλει αυτόματα)

```bash
.venv/Scripts/activate
```

- κάνουμε install τα dependencies από το requirements.txt

```bash
pip install -r requirements.txt
```

## Docker

- κατεβάζουμε το Docker Desktop (<https://www.docker.com/products/docker-desktop/>)

- ανοίγουμε το app
- στο visual studio code, πηγαίνουμε στον φάκελο που βρίσκονται τα αρχεία του Docker

```bash
cd Docker
```

- τρέχουμε το container

```bash
docker-compose up --build
```

- αφήνουμε το terminal ανοιχτό για να βλέπουμε logs

## DB

- ανοίγω νέο παράθυρο terminal
- πηγαίνουμε στο backend

```bash
cd backend
```

- τρέχουμε το project

```bash
uvicorn main:app --reload
```
