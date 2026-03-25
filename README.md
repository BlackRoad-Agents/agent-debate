<!-- BlackRoad SEO Enhanced -->

# agent deuate

> Part of **[BlackRoad OS](https://blackroad.io)** — Sovereign Computing for Everyone

[![BlackRoad OS](https://img.shields.io/badge/BlackRoad-OS-ff1d6c?style=for-the-badge)](https://blackroad.io)
[![BlackRoad-Agents](https://img.shields.io/badge/Org-BlackRoad-Agents-2979ff?style=for-the-badge)](https://github.com/BlackRoad-Agents)

**agent deuate** is part of the **BlackRoad OS** ecosystem — a sovereign, distributed operating system built on edge computing, local AI, and mesh networking by **BlackRoad OS, Inc.**

### BlackRoad Ecosystem
| Org | Focus |
|---|---|
| [BlackRoad OS](https://github.com/BlackRoad-OS) | Core platform |
| [BlackRoad OS, Inc.](https://github.com/BlackRoad-OS-Inc) | Corporate |
| [BlackRoad AI](https://github.com/BlackRoad-AI) | AI/ML |
| [BlackRoad Hardware](https://github.com/BlackRoad-Hardware) | Edge hardware |
| [BlackRoad Security](https://github.com/BlackRoad-Security) | Cybersecurity |
| [BlackRoad Quantum](https://github.com/BlackRoad-Quantum) | Quantum computing |
| [BlackRoad Agents](https://github.com/BlackRoad-Agents) | AI agents |
| [BlackRoad Network](https://github.com/BlackRoad-Network) | Mesh networking |

**Website**: [blackroad.io](https://blackroad.io) | **Chat**: [chat.blackroad.io](https://chat.blackroad.io) | **Search**: [search.blackroad.io](https://search.blackroad.io)

---


Multi-agent debate engine for BlackRoad OS. Orchestrates structured debates between 2-4 agents via Ollama.

## What This Is

A Python script that takes a topic and a set of agent IDs, then runs a structured multi-round debate. Each agent generates an opening statement, responds to other agents' points across N rounds, and delivers a closing statement. The full transcript is output as structured JSON.

## Requirements

- Python 3.6+
- Ollama running locally (or specify --host)
- curl (for Ollama API calls)

## Usage

```bash
# Basic debate between two agents
python3 debate.py "Should we use microservices or a monolith?" --agents coder scholar

# Four agents, 5 rounds
python3 debate.py "Is sovereign infrastructure worth the maintenance cost?" \
  --agents road coder cipher alice --rounds 5

# Save transcript to file
python3 debate.py "PostgreSQL vs SQLite for edge nodes" \
  --agents coder octavia --output debate-output.json

# Use custom model and personas
python3 debate.py "Best approach to fleet monitoring" \
  --agents aria cecilia --model mistral --personas ../agent-personas/personas.json
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `topic` | (required) | The debate topic or question |
| `--agents` | coder scholar | 2-4 agent IDs to participate |
| `--rounds` | 3 | Number of debate rounds |
| `--model` | llama3.2 | Ollama model name |
| `--personas` | (built-in) | Path to personas.json for system prompts |
| `--host` | http://localhost:11434 | Ollama API endpoint |
| `--output` | stdout | Output file for JSON transcript |

## Debate Structure

1. Opening statements (each agent states their position)
2. N rounds of responses (agents respond to each other's points)
3. Closing statements (agents summarize final positions)

## Output Format

```json
{
  "topic": "Should we use microservices or a monolith?",
  "agents": ["coder", "scholar"],
  "model": "llama3.2",
  "rounds": 3,
  "started_at": "2026-03-23T12:00:00Z",
  "ended_at": "2026-03-23T12:05:00Z",
  "total_exchanges": 8,
  "exchanges": [
    {"round": 0, "type": "opening", "agent": "coder", "content": "..."},
    {"round": 1, "type": "response", "agent": "scholar", "content": "..."}
  ]
}
```

Part of BlackRoad-Agents. Remember the Road. Pave Tomorrow. Incorporated 2025.
