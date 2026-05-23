# Enterprise AI Triage - Walkthrough Tecnico

Questo documento descrive Enterprise AI Triage dal punto di vista tecnico e operativo.

Enterprise AI Triage è pensato per velocizzare il primo smistamento dei ticket in un help desk strutturato. L'operatore inserisce le informazioni iniziali del case; il backend applica regole di triage per classificare la richiesta, stimare il rischio e indicare il team o il percorso operativo più adatto.

L'architettura separa l'inserimento del ticket dalla classificazione automatica. Questo permette di mantenere un processo tracciabile, con motivazione salvata, risk score controllato, provider identificabile e possibilità di cambiare motore LLM senza riscrivere il workflow operativo.

## Contesto del problema

In molte aziende le richieste arrivano da canali diversi e con livelli di dettaglio molto variabili:

- incidenti di produzione
- richieste di servizio
- accessi e onboarding
- rischi di sicurezza
- proposte di automazione con AI
- temi di governance, compliance o audit

Ogni ticket viene validato, classificato, valutato, indirizzato al team corretto e salvato con una motivazione leggibile. Il risultato aiuta il primo livello di supporto a ridurre il tempo di smistamento e a mantenere traccia delle decisioni prese.

## Principi di design

Le scelte sono guidate da principi pratici:

- l'AI supporta l'indirizzamento corretto del case e l'attivazione del percorso operativo più adatto
- le categorie e i team di escalation sono controllati
- il rischio è espresso con uno score semplice, da 1 a 5
- la motivazione della classificazione viene salvata
- il provider usato viene tracciato
- il provider può essere sostituito senza riscrivere il workflow operativo
- token e costi vanno trattati come metriche operative quando si useranno veri LLM
- sicurezza e governance hanno precedenza rispetto alla semplice automazione

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

### Frontend

Il frontend React è una dashboard operativa. Gestisce:

- form di inserimento ticket
- indicatori sintetici
- distribuzioni per priorità, categoria ed escalation
- registro dei ticket

Non contiene logica di classificazione. Invia dati strutturati al backend e mostra il risultato.

### Backend

Il backend FastAPI gestisce il workflow applicativo:

- validazione del payload
- chiamata al provider di triage
- salvataggio del ticket e del risultato
- aggregazioni per la dashboard

I modelli Pydantic definiscono il contratto tra API, provider e persistenza.

### Provider di triage

Il contratto del provider è volutamente stretto:

```python
class TriageProvider:
    def classify(self, ticket: TicketCreate) -> TriageResult:
        ...
```

Oggi il provider attivo è:

```text
mock-enterprise-rules-v1
```

È locale, deterministico e non invia dati a servizi esterni. Questo è utile per demo, test e prime valutazioni, perché evita costi, variabilità e problemi di data exposure.

Nel codice sono presenti placeholder per OpenAI, Anthropic e Mistral. La scelta importante è che l'interfaccia resta la stessa: il resto dell'applicazione non deve sapere quale modello o vendor c'è dietro.

### Persistenza

SQLite viene usato per avere persistenza reale senza introdurre infrastruttura esterna.

In produzione il passaggio naturale sarebbe verso PostgreSQL o un database relazionale gestito, con migrazioni, policy di retention, backup e isolamento tra tenant o organizzazioni.

## Modello dati

Il ticket in ingresso contiene:

- titolo
- descrizione
- priorità
- impatto sul business
- area tecnica

Il risultato del triage contiene:

- categoria
- risk score
- team di escalation
- raccomandazione operativa
- provider
- motivazione

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

Questi valori controllati evitano che un output libero o ambiguo finisca direttamente nel routing operativo.

## Flusso end-to-end

1. L'utente inserisce un ticket dalla UI.
2. FastAPI valida i dati con Pydantic.
3. Il backend chiama `provider.classify(ticket)`.
4. Il provider restituisce un `TriageResult` con schema controllato.
5. Il repository salva input originale e risultato del triage.
6. La dashboard legge KPI e registro ticket.

Il flusso è lineare e conserva le informazioni necessarie per capire in seguito perché una richiesta è stata classificata e indirizzata in un certo modo.

## Logica di classificazione

Il provider mock unisce:

- titolo
- descrizione
- impatto business
- area tecnica

in un unico testo lowercase. Poi applica gruppi di keyword in un ordine preciso.

La sicurezza viene controllata per prima:

```text
security, vulnerability, breach, phishing, cve, iam, zero trust
```

Poi la governance:

```text
policy, compliance, gdpr, risk committee, audit, governance, approval
```

Poi i casi d'uso AI:

```text
ai, llm, model, prompt, rag, copilot, automation use case
```

Poi incidenti e service request:

```text
down, outage, broken, incident, failed, latency, degraded
request, access, provision, new user, onboarding, change
```

Il fallback è:

```text
Service Request
```

L'ordine è importante. Se una richiesta segnala che un assistente AI espone dati cliente, il sistema la indirizza prima verso una valutazione security e solo dopo, se opportuno, verso il percorso di automazione.

## Risk Score

Il rischio parte da `1`.

La priorità aggiunge:

```text
Low      +0
Medium   +1
High     +2
Critical +3
```

Un segnale di impatto business o produzione aggiunge `+1` se nel testo compaiono:

```text
revenue, customer, production, sla, regulatory, blocked
```

Le categorie `Security Risk` e `Governance Issue` aggiungono un ulteriore `+1`.

Il risultato viene limitato a `5`.

Lo score serve a produrre un segnale comprensibile, stabile e utile per routing e dashboard.

## Escalation

La logica di escalation segue categoria e priorità:

```text
Security Risk      -> Security
Governance Issue   -> AI Governance
AI Use Case        -> Business Owner or AI Governance
High/Critical Incident -> DevOps
Default            -> Support
```

Per gli AI use case, se il testo contiene termini come:

```text
roi, business, process
```

l'escalation va al `Business Owner`. In caso contrario va ad `AI Governance`.

Questa distinzione è realistica: alcune idee AI vanno prima qualificate dal business, altre devono passare da governance e valutazione del rischio prima ancora della fase di design.

## Raccomandazioni operative

Le raccomandazioni sono scritte in stile service management, non in stile generico da assistente AI.

Esempi:

- per un incidente: aprire un bridge, confermare blast radius, assegnare ownership e comunicare rispetto agli SLA
- per una service request: validare scope, approval path e workflow di fulfillment
- per un rischio di sicurezza: avviare triage security, preservare evidenze, valutare esposizione e contenimento
- per un caso d'uso AI: chiarire outcome business, sensibilità dei dati, fattibilità e metriche di successo
- per governance o rischio alto: documentare criteri decisionali, mitigazioni o risk acceptance

Il punto è aiutare la prossima azione operativa, non produrre una risposta elegante.

## API

Il backend espone:

- `GET /health`
- `POST /tickets`
- `POST /triage/preview`
- `GET /tickets`
- `GET /dashboard`

`POST /triage/preview` classifica senza salvare. `POST /tickets` classifica e persiste.

La dashboard restituisce:

- numero totale di ticket
- rischio medio
- numero di ticket ad alto rischio
- conteggi per priorità
- conteggi per categoria
- conteggi per escalation

## Architettura LLM-agnostic

Il contratto chiave è:

```text
TicketCreate -> TriageResult
```

Un provider LLM futuro deve rispettare lo stesso schema del provider mock. Non dovrebbe introdurre dipendenze dirette nel frontend, nel repository o nella dashboard.

Quando verranno aggiunti provider reali, ogni classificazione dovrebbe registrare:

- provider
- modello
- versione prompt
- token in input
- token in output
- costo stimato
- latenza
- esito policy
- livello di sensibilità dati

Questo rende l'uso dell'AI misurabile e governabile. Senza questi dati, il costo dei modelli e il rischio operativo restano nascosti.

## Vincoli enterprise considerati

Il prototipo considera alcuni vincoli tipici:

- ownership chiara tra IT, business, security e governance
- rischio di esporre dati sensibili verso provider esterni
- necessità di audit delle raccomandazioni automatiche
- risk score limitato e revisionabile
- evitamento del lock-in su un singolo provider
- controllo futuro di token e costi
- review delle dipendenze e remediation CVE
- percorso credibile da SQLite locale a storage di produzione

## Security e CVE Review

Sono state controllate le dipendenze frontend e l'ambiente Python backend.

Stato dopo remediation:

```text
Frontend npm audit: 0 known vulnerabilities
Backend pip-audit after remediation: 0 known vulnerabilities
```

Durante la review è stato trovato un problema sul tool locale:

```text
pip 26.0.1
```

CVEs riportate:

- `CVE-2026-3219`
- `CVE-2026-6357`

La remediation è stata l'upgrade di `pip` a `26.1.1`, seguito da una nuova scansione senza vulnerabilità note.

Anche se `pip` non è codice applicativo, resta parte della superficie di build e delivery. In un contesto enterprise va gestito, non ignorato.

## Hardening per produzione

Prima di un uso reale servirebbero:

- autenticazione e RBAC
- isolamento tenant
- HTTPS e gestione sicura dei secret
- database production-grade
- migrazioni
- audit log immutabili
- backup e retention
- rilevamento PII e secret
- LLM gateway con redaction, policy check e validazione output
- dependency scanning in CI e SBOM
- integrazione con ServiceNow o Jira Service Management
- integrazione con strumenti di escalation come PagerDuty o Opsgenie

## Esecuzione locale

Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

URL default:

- Backend: `http://127.0.0.1:8000`
- API docs: `http://127.0.0.1:8000/docs`
- Frontend: `http://127.0.0.1:5173`

## Lettura del progetto

Il valore del progetto è nel modo in cui il workflow tiene insieme automazione, help desk, security, governance, service delivery e impatto business.

È una base piccola ma leggibile per discutere come introdurre automazione AI dentro un processo operativo controllato.
