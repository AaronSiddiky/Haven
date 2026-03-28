# Haven

Autonomous agent for the visually impaired — powered by OpenClaw.

## Project Structure

```
haven/
├── apps/
│   ├── web/              # Web application (dashboard, settings, user management)
│   ├── voice-agent/      # Voice-based conversational agent
│   └── backend/
│       ├── api/          # REST/WebSocket API server
│       └── openclaw/     # OpenClaw integration layer
├── packages/
│   └── shared/           # Shared types, utilities, and constants
├── docs/                 # Documentation
└── scripts/              # Dev and deployment scripts
```

## Getting Started

```bash
# Install dependencies
npm install

# Start development
npm run dev
```

## License

MIT
