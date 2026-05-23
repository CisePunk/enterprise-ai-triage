# Enterprise AI Triage

Versione inglese: [README.md](README.md)

Enterprise AI Triage è una piccola applicazione web pensata per velocizzare i processi di un help desk strutturato. L'operatore inserisce le informazioni iniziali del ticket; il sistema applica automaticamente regole di triage per classificare la richiesta, stimare il rischio e indirizzarla al team corretto.

Il progetto adotta un'architettura chiara, scalabile e facilmente riprogrammabile in base alle esigenze dell'organizzazione. Il workflow tiene conto fin dall'inizio di compliance, security, controllo dei costi e ownership operativa.

L'obiettivo è integrare l'automazione dentro un processo operativo tracciabile: il ticket resta scritto da una persona, mentre categoria, risk score, escalation, raccomandazione e motivazione vengono prodotti dal backend in modo coerente e verificabile.

## Cosa fa

L'applicazione permette di inserire i dati di partenza del ticket:

- titolo
- descrizione
- priorità
- impatto business
- area tecnica

Da questi dati il backend calcola automaticamente:

- categoria
- risk score da 1 a 5
- team di escalation
- raccomandazione operativa
- motivazione
- provider usato

Categorie supportate:

- `Incident`
- `Service Request`
- `Security Risk`
- `AI Use Case`
- `Governance Issue`

Team di escalation supportati:

- `Support`
- `DevOps`
- `Security`
- `Business Owner`
- `AI Governance`

La dashboard mostra KPI sintetici, distribuzioni per priorità/categoria/escalation e registro dei ticket.

## A cosa serve

Ogni richiesta viene classificata, valutata, indirizzata al team corretto e salvata con una motivazione leggibile. In questo modo l'help desk può ridurre il tempo speso nel primo smistamento e mantenere traccia delle decisioni prese.

## Principi di design

- AI come supporto all'indirizzamento corretto del case e all'attivazione del percorso più adatto: change management, intervento tecnico, security review o governance.
- Routing e risk scoring basati su criteri leggibili.
- Motivazione della classificazione salvata insieme al ticket.
- Output limitato a valori controllati, per evitare categorie libere o ambigue.
- Provider AI separato dal resto dell'applicazione, così si può cambiare motore LLM senza riscrivere il workflow operativo.
- Costi e token LLM trattati come dati operativi.
- Sicurezza e governance prioritizzate rispetto alla semplice automazione.

## Architettura

```text
React frontend
    |
    v
FastAPI backend
    |
    v
Triage provider interface
    |
    v
Mock enterprise rules provider
    |
    v
SQLite persistence
```

Il provider attuale è locale e deterministico:

```text
mock-enterprise-rules-v1
```

Sono presenti placeholder per provider OpenAI, Anthropic e Mistral. Frontend e database non dipendono da un vendor specifico.

## Governance

Il sistema tratta la classificazione come workflow governato:

- output limitato a categorie note
- risk score limitato a `1-5`
- escalation esplicita e revisionabile
- motivazione salvata
- provider salvato
- nessuna chiamata LLM esterna nella versione corrente
- stesso formato di risposta anche con provider futuri

Le richieste con segnali di sicurezza hanno priorità sugli use case AI. Per esempio, se un ticket parla di un assistente AI che espone dati cliente, il sistema lo indirizza verso una valutazione security prima di trattarlo come proposta di automazione.

## Setup locale

Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

URL:

- Backend: `http://127.0.0.1:8000`
- API docs: `http://127.0.0.1:8000/docs`
- Frontend: `http://127.0.0.1:5173`

## Documentazione

- [docs/full-walkthrough-en.md](docs/full-walkthrough-en.md)
- [docs/full-walkthrough-it.md](docs/full-walkthrough-it.md)
- [docs/llm-cost-control.md](docs/llm-cost-control.md)
- [docs/security-cve-review.md](docs/security-cve-review.md)

## Stato del progetto

È un prototipo, non un sistema production-ready.

Prima di un uso reale servirebbero autenticazione, RBAC, tenant isolation, HTTPS, gestione secret, audit log immutabili, storage production-grade e integrazioni ITSM.

Il progetto è pensato per mostrare AI adoption pragmatica: prima governance e operations, poi automazione.
