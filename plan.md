```markdown
# Detailed Implementation Plan for Web Simulator for Diagrams.net

This plan details all the dependent files, changes, and integrations required to build a fully featured diagramming simulator with real-time collaboration using Next.js for the frontend and Python Django (with Channels) for the backend.

---

## 1. Overall Architecture

- **Frontend:**  
  – Built using Next.js (React).  
  – New components for Canvas, Toolbar, Shape Library Sidebar, Properties Panel, and File Management.  
  – State management via custom hooks (`useDiagram`, `useCollaboration`).  
  – Responsive, modern, minimal flat design using pure CSS with typography, spacing, and color adjustments.
  
- **Backend:**  
  – Implemented with Python Django.  
  – REST API endpoints for saving/loading diagrams and version history.  
  – Real-time collaboration via Django Channels (WebSocket) integration.  
  – Uses a database for persisting diagrams; no external API keys required.

---

## 2. File Structure & New Components

### Frontend (Next.js)
- **New Folder:** `src/components/diagram/`
  - **Canvas.tsx:** Main drawing area using an HTML `<canvas>` element.
  - **Toolbar.tsx:** Top toolbar with buttons for selection, shape tools (rectangle, circle, line, etc.), text, and connector.
  - **ShapeSidebar.tsx:** Left sidebar with categorized shapes (basic, flowchart, UML, etc.) and a search bar.
  - **PropertiesPanel.tsx:** Right panel for modifying shape properties (color, border, text, rotation, etc.).
  - **FileManagement.tsx:** Menu or header component to create, open, save, export diagrams, and view version history.
  
- **New Hooks:**
  - **useDiagram.ts (in src/hooks/):**  
    – Manages diagram state (shapes list, active tool, selected shape).  
    – Provides functions to add, update, delete shapes and trigger canvas re-render.  
    – Implements error handling for state updates.
    
  - **useCollaboration.ts (in src/hooks/):**  
    – Establishes a WebSocket connection with the Django backend for real-time collaboration.  
    – Listens for broadcast messages and updates diagram state.  
    – Handles connection errors and auto-reconnect logic.

- **New API Helpers:**
  - **api.ts (in src/lib/):**  
    – Contains functions (e.g., `saveDiagram()`, `loadDiagram()`, `getVersionHistory()`) using the fetch API to interact with Django REST endpoints.  
    – Wraps each call in try/catch with error fallback.

- **New Page:**
  - **page.tsx (in src/app/diagram/):**  
    – Main simulator page that composes the UI layout:
      - Header/FileManagement menu at the top.
      - Left: Shape Library Sidebar.
      - Center: Canvas Area.
      - Right: Properties Panel.
      - Top on canvas: Toolbar component.
    – Uses CSS Grid/flex layouts to maintain a modern, responsive interface.
    – Implements error boundaries to catch UI errors.

- **Global Styles:**
  - **globals.css (in src/app/):**  
    – Add style rules for classes like `.simulator-container`, `.toolbar`, `.canvas-area`, `.sidebar`, and `.property-panel`.
    – Include responsive media queries to support mobile devices and tablets.
    – Ensure accessible typography, colors, and spacing.

### Backend (Python Django)

- **Project Folder:** `django_backend/`
  - **Models (models.py):**  
    – Create a `Diagram` model (fields: id, user, diagramJSON, version, timestamp).
    – Optionally, a `DiagramVersion` model for version control.
    
  - **Views (views.py):**  
    – REST endpoints: `/api/diagrams/save`, `/api/diagrams/load`, `/api/diagrams/history`.  
    – Use Django REST Framework for input validation and error handling.
    
  - **WebSocket Integration:**  
    – Configure Django Channels for a WebSocket endpoint (e.g., `ws://<host>/ws/diagrams/`) to broadcast real-time changes.
    – Implement consumers to handle join/leave events and diagram update messages.
    
  - **Error Handling & Testing:**  
    – Each API endpoint and WebSocket consumer must catch exceptions and return meaningful HTTP error responses.
    – Validate endpoints using curl commands (see testing section).

---

## 3. Step-by-Step Changes Per File

### A. Frontend Files

1. **src/app/globals.css**
   - Add new CSS classes:
     - `.simulator-container`: overall page layout.
     - `.toolbar`: styling for top tool controls.
     - `.canvas-area`: white or light-color background, grid lines toggle, responsive sizing.
     - `.sidebar` and `.property-panel`: fixed widths, collapsible behavior on mobile.
   - Add media queries for mobile responsiveness.

2. **src/app/diagram/page.tsx**
   - Set up a layout using a combination of `<header>`, `<aside>`, `<main>`, and `<section>` elements.
   - Import and include the following components:
     - `<FileManagement />` (header).
     - `<Toolbar />` (integrated within canvas area or as a top overlay).
     - `<ShapeSidebar />` (left panel).
     - `<Canvas />` (center).
     - `<PropertiesPanel />` (right panel).
   - Implement a parent container with error boundaries to catch component crashes.
   
3. **src/components/diagram/Canvas.tsx**
   - Render an HTML `<canvas>` element and use React’s `useRef` to manage its context.
   - Implement mouse event callbacks (`onMouseDown`, `onMouseMove`, `onMouseUp`) to draw shapes.
   - Use `useEffect` to adjust for devicePixelRatio.
   - Catch errors if the canvas or its context fails and display a fallback message.

4. **src/components/diagram/Toolbar.tsx**
   - Render a div with several `<button>` elements labeled “Select”, “Rectangle”, “Circle”, “Line”, “Text”, “Connector”.
   - Update the active tool state using onClick events through `useDiagram` hook.
   - Style buttons with clear text labels, padding, and a modern flat color scheme.

5. **src/components/diagram/ShapeSidebar.tsx**
   - Include an `<input>` field for the search bar.
   - List shape categories (Basic, Flowchart, UML, Network, Org Chart, Mind Map, Wireframe, Gantt, ER, BPMN).
   - Render each shape as a clickable text item (e.g., “Rectangle”, “Ellipse”).
   - On click, dispatch an action to add the shape via `useDiagram` hook.
   - Handle empty or no-results cases gracefully.

6. **src/components/diagram/PropertiesPanel.tsx**
   - Display properties for a selected shape (color fill, border style, text content, rotation, etc.).
   - Render form controls (color picker, number input for border thickness, dropdown for arrow style).
   - Validate inputs and update the canvas state in real time.
   - Use accessible form labels and clear error messages if values are invalid.

7. **src/components/diagram/FileManagement.tsx**
   - Render a header menu with options: New Diagram, Open, Save, Export, and Version History.
   - Integrate modals or alert dialogs (reuse `<AlertDialog>` from `src/components/ui/alert-dialog.tsx`) for user confirmations.
   - Hook up buttons to API calls from `src/lib/api.ts` for saving/loading diagrams.
   - Display progress messages or error alerts on failed operations.

8. **src/hooks/useDiagram.ts**
   - Create a custom hook managing:
     - Active diagram state (array of shapes with their properties).
     - Active tool selection.
     - Selected shape for property editing.
   - Provide functions like `addShape()`, `updateShape()`, and `deleteShape()`.
   - Include try/catch blocks to handle state update errors.
   - Optionally sync state with localStorage as a fallback.

9. **src/hooks/useCollaboration.ts**
   - Initiate a WebSocket connection to the Django backend endpoint.
   - Listen for “diagram_update” messages and merge remote changes with local state.
   - Implement reconnection logic on disconnection.
   - Log errors and display a non-intrusive error banner if connectivity fails.

10. **src/lib/api.ts**
    - Create helper functions:
      - `async function saveDiagram(diagramData: object): Promise<any> { … }`
      - `async function loadDiagram(diagramId: string): Promise<any> { … }`
      - `async function getVersionHistory(diagramId: string): Promise<any> { … }`
    - Use `fetch` with proper headers (Content-Type: application/json) and error handling (try/catch, HTTP status code checks).

### B. Backend Files (Python Django)

1. **django_backend/simulator/models.py**
   - Define a `Diagram` model with fields: `id`, `user` (ForeignKey), `diagram_json` (TextField), `version` (IntegerField), `timestamp` (DateTimeField).
   - Optionally, create a separate `DiagramVersion` model for tracking version history.

2. **django_backend/simulator/views.py**
   - Implement REST endpoints:
     - `POST /api/diagrams/save` to save/update the diagram.
     - `GET /api/diagrams/load` to retrieve a diagram by ID.
     - `GET /api/diagrams/history` to fetch version history.
   - Use Django REST Framework for input validation and return JSON responses with proper HTTP status codes.
   - Wrap each view in try/except blocks and return error messages in case of exceptions.

3. **django_backend/simulator/consumers.py**
   - Create a Channels consumer for diagram collaboration:
     - Listen for messages from connected clients.
     - Broadcast updates to all clients in the same diagram room.
     - Handle disconnects and errors gracefully.

4. **Django Channels Configuration**
   - Update `routing.py` to include a WebSocket route (e.g., `ws/diagrams/`).
   - Ensure proper authentication and error messaging on connection failures.

5. **Testing Django Endpoints**
   - Use curl commands to test endpoints, for example:
     ```bash
     curl -X POST http://localhost:8000/api/diagrams/save \
       -H "Content-Type: application/json" \
       -d '{"diagram_json": "{...}", "version": 1}' -w "\nHTTP: %{http_code}\n"
     ```
   - Verify that file creation and JSON responses return accurate status codes and messages.

---

## 4. Integration & UI/UX Considerations

- **UI Layout:**  
  – A grid layout ensuring the File Management menu is accessible at the top; the Shape Sidebar (left) and Properties Panel (right) flank the Canvas area.  
  – Toolbar buttons use clear text labels (no icon libraries) with consistent padding, margins, and flat color themes.

- **Real-time Collaboration:**  
  – The useCollaboration hook updates the UI in real time, with visual indicators (e.g., a subtle banner or badge) showing when multiple users are editing.
  
- **Accessibility:**  
  – Keyboard shortcuts integrated in `useDiagram` for common actions.  
  – Semantic HTML elements and ARIA roles in all interactive controls.
  
- **Mobile Compatibility:**  
  – Responsive layouts via CSS media queries in globals.css and collapsible side panels for small screens.
  
- **Error Handling:**  
  – Every component and API call is wrapped in try/catch blocks with fallback UI components (using existing alert-dialog components) to inform users of errors.
  
- **Cloud Integration & Storage:**  
  – Diagram data is stored in the Django backend database with endpoints for saving and version control.
  
---

## 5. Summary

- The simulator is structured as a Next.js application with new components for canvas, toolbar, shape sidebar, property panel, and file management.  
- Custom hooks manage diagram state and real-time collaboration via WebSockets connected to a Django backend using Channels.  
- Global CSS, responsive design, and accessible UI elements ensure a modern, intuitive interface without external icon libraries.  
- The Django backend provides REST endpoints for file operations and uses channels for live updates, with robust error handling in both front- and back-end.  
- API helper functions and thorough testing (e.g., via curl commands) guarantee secure, reliable saving and loading of diagram data.
