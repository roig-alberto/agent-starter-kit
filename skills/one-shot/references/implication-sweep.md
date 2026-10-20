# Implication sweep (step 2)

This is the checklist weak sessions skip. Walk EVERY line and answer "yes, load the skill" or "no".

| Does the change... | Then |
|---|---|
| touch the DB schema? | `backend-patterns` migration discipline (additive order, committed migrations); prove it with `testing` on a throwaway database |
| add or change a secret or env var? | `security` (not in this kit) (bundle coverage, .env.example, never plaintext) |
| add a service, port, volume, or image? | `portability` FIRST, then `fleet-ops`; sync the rebuild files |
| create new state that must survive? | backup coverage (`backups-and-alerts` (not in this kit)), or it is lost on a host move |
| expose anything new? | `security` (not in this kit) (tunnel plus Access only) |
| notify the user? | Web Push (`pwa-patterns`) in the app; `backups-and-alerts` (not in this kit) for infra alerts on Telegram |
| change UI or UX? | the **design-path fork** below |
| contain domain logic? | it goes in `lib/` as pure functions with tests (`testing`) |

## Design-path fork (when the change adds UI)

- **A tweak to an existing screen:** **match the existing screens** (the tokens, spacing, and components
  already there). Load `frontend-interaction-patterns` for gestures and drag-and-drop.
- **A NEW screen or a major visual surface:** ASK the user with AskUserQuestion, one question, **no
  default, presenting both options equally**:
  - **In-house:** load `frontend-design` and derive the design from the app's DESIGN_TOKENS.md.
  - **Claude Design Agent** (external): write a mini design brief and reuse the token-export prompt from
    the design step of `new-app` (the same `ui/inbox/<feature-slug>/` folder with the `input-` and
    `output-` convention). PAUSE for its wireframes. The wireframes are then the exact spec, built
    pixel-close, as `new-app` describes.
- **Always request hi-fi STATIC wireframes, one frame per screen state, never an interactive or clickable
  prototype.** It is a standing user rule; the exact wording lives in `frontend-design`.
- Never silently invent a new visual direction on an app that has one.

**Exit:** a short implications list in your reply ("schema: yes - new table + migration; secrets: no;
design path: match-existing; ...") BEFORE writing code.
