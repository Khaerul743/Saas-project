# Agent Playground

Halaman playground untuk testing AI agents sebelum deploy ke production.

## Fitur

### 🎯 **Quick Test**
- Test agent yang sudah dibuat dengan chat interface yang simple
- Switch antara multiple agents dengan mudah
- Real-time chat dengan simulated responses

### 🔗 **Share & Demo**
- Generate shareable link untuk testing
- Share dengan client/stakeholder untuk approval
- Custom message untuk recipient
- Share options (allow feedback, show agent info)

### 🚀 **Deploy**
- Deploy agent langsung dari playground
- One-click deployment ke production
- Status tracking untuk deployment

## Struktur File

```
app/playground/
├── page.tsx                    # Main playground page
├── loading.tsx                 # Loading state
├── test/[agentId]/page.tsx     # Shareable test page
└── README.md                   # Documentation

components/playground/
├── playground-header.tsx       # Header dengan deploy/share buttons
├── agent-selector.tsx          # Sidebar untuk pilih agent
├── chat-interface.tsx          # Chat UI untuk testing
└── share-modal.tsx             # Modal untuk share functionality

lib/api/
└── playground.ts               # API service untuk playground
```

## User Flow

1. **User buka `/playground`**
2. **Pilih agent** dari sidebar
3. **Chat dengan agent** untuk testing
4. **Share link** (optional) ke stakeholder
5. **Deploy** kalau sudah approve

## API Endpoints

- `POST /playground/test` - Test agent dengan message
- `POST /playground/share` - Generate shareable link
- `GET /playground/scenarios/{agentId}` - Get test scenarios
- `POST /playground/batch-test/{agentId}` - Run batch test
- `GET /playground/history/{agentId}` - Get test history
- `POST /playground/deploy/{agentId}` - Deploy agent

## Komponen Utama

### PlaygroundHeader
- Display selected agent info
- Deploy dan Share buttons
- Status indicators

### AgentSelector
- List semua available agents
- Agent info (name, description, platform, status)
- Click untuk select agent

### ChatInterface
- Real-time chat UI
- Message history
- Input dengan send button
- Reset chat functionality
- Loading states

### ShareModal
- Generate shareable link
- Custom message input
- Share options
- Copy link functionality

## Fitur Advanced (Future)

- **Scenario Testing** - Pre-defined test scenarios
- **Batch Testing** - Test multiple prompts sekaligus
- **Performance Metrics** - Response time, token usage
- **Quality Scoring** - Rate response quality
- **Export Results** - Save test results
- **Team Collaboration** - Share dengan team members
