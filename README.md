# Diagram Collaboration Simulator

An in-progress web diagramming simulator using a Next.js frontend and a Django backend scaffold, with planned real-time collaboration through Django Channels/WebSockets.

> The repository name is historical. The actual project plan and source structure are focused on a diagrams.net-style simulator rather than a font demo.

## Intended architecture

### Frontend
- Next.js 15 / React 19 / TypeScript
- diagram canvas and drawing tools
- toolbar, shape library, properties panel, and file-management UI
- client-side diagram state and collaboration hooks

### Backend
- Python / Django
- Django REST Framework-style API structure
- Django Channels / WebSocket collaboration design
- persistence for diagrams and version history

## Project status

The repository contains the implementation plan, a phase tracker, a Next.js application, and a Django backend scaffold. The included `TODO.md` still marks most functional phases as incomplete, so this repository should be treated as **work in progress**, not a finished collaborative diagramming product.

## Local frontend development

```bash
npm install
npm run dev
```

The frontend development script runs Next.js on port 8000.

## Planning documents

- `plan.md` — intended architecture and implementation plan
- `TODO.md` — phase-by-phase implementation tracker

## Public availability

Only the code currently present in this repository is public. Future/unfinished capabilities described in the plan should not be interpreted as completed features.
