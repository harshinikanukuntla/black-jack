# Blackjack — AI Agent Table

A terminal-based, simplified Blackjack game. You play against **three AI
agent players** with distinct personalities and **one AI dealer**, who also
plays its own hand. Runs entirely in the CLI on Python 3.12+.

## Rules (simplified)

- A "card" is a random integer between 2 and 11 (not a standard 52-card deck).
- **Only the dealer can draw cards.** Every player — you and each AI agent —
  must *ask the dealer* to draw on their behalf.
- Every hand (you, each AI agent, and the dealer) may draw **up to three
  cards**.
- Turn order: you, then each AI agent in turn, then the dealer plays last.
- The dealer's own hand follows the standard fixed blackjack rule (hit while
  total < 17, else stand) rather than a personality — real dealers play by
  rule, not judgment.
- Busting (total > 21) eliminates a hand from winning.
- After every hand has finished, whoever has the **highest total ≤ 21**
  wins. Ties are announced as a push; if everyone busts, there's no winner.

## How the AI agents "decide"

Each AI agent's hit/stand choice is delegated to a pluggable **brain**
(`blackjack/brains.py`):

- **`OllamaBrain`** (used when available): asks a real, locally-hosted
  open-weight LLM via [Ollama](https://ollama.com), through
  [LangChain](https://python.langchain.com)'s `ChatOllama` integration. Each
  agent gets its own personality baked into its system prompt (see below),
  so the same hand can produce different decisions per agent.
- **`HeuristicBrain`** (automatic fallback): a deterministic, threshold-based
  policy with a per-agent "risk tolerance" knob, used when Ollama isn't
  installed, isn't running, or the model isn't pulled. The game always
  prints a one-time note when it falls back, and then plays a complete game
  either way — there's no hard dependency on a live model.

Regardless of which brain is used, the **game engine never trusts the brain
to enforce rules**. Turn order, the three-card cap, arithmetic totals, bust
detection, and winner determination are all deterministic Python — a brain
only ever answers "hit or stand?" for a single decision.

The three default personalities:

| Agent | Personality |
|---|---|
| Cautious Cal | risk-averse, stops early rather than risk busting |
| Balanced Bailey | weighs risk and reward evenly |
| Aggressive Amy | bold, keeps drawing to chase a higher score |

## Why LangChain (and not AutoGen / CrewAI / n8n)

Blackjack has rules that must be enforced by code, not agent judgment: turn
order, the three-card cap, and correct arithmetic. AutoGen and CrewAI are
built for open-ended multi-agent collaboration on loosely-structured tasks,
which fights against that need for strict, deterministic control. n8n is a
visual workflow tool meant to run as an external service — the wrong shape
for a Python CLI app. LangChain is used narrowly here, only at the single
seam where an LLM call actually adds value: "given this hand, hit or
stand?" — everything else stays plain, testable Python.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt   # optional: only needed for the LLM brain
```

### Enabling the real LLM brain (optional)

The game works out of the box with the heuristic brain. To use a real
local LLM instead:

```bash
brew install ollama
brew services start ollama
ollama pull llama3.1:8b
```

Verify it's reachable: `curl http://localhost:11434/api/version`.

## Running the game

```bash
python3 main.py
```

Options:

```bash
python3 main.py --agents 4              # play with 4 AI agents instead of 3
python3 main.py --no-llm                # force the heuristic brain, skip Ollama entirely
python3 main.py --model mistral:7b      # use a different Ollama model tag
python3 main.py --seed 7                # reproducible card draws, for testing
```

During your turn, respond naturally — e.g. `hit me`, `deal me the next
card`, `I'll stand`, `stay`, `no more`.

## Running the tests

```bash
python3 -m unittest discover -s tests -v
```

26 tests cover card range, hand/bust logic, the three-card cap, natural
language intent parsing, the heuristic brain's threshold behavior, the
dealer's fixed play rule, winner/tie/no-winner determination, and a full
end-to-end game run.

## Project layout

```
main.py                 CLI entry point (argparse)
blackjack/
  cards.py               the given draw_card() primitive
  dealer.py               the AI dealer agent: services draw requests, plays its own hand
  brains.py               pluggable hit/stand decision-making (Ollama + heuristic fallback)
  players.py               Player / HumanPlayer / AIPlayer, three-card cap, bust logic
  nlp.py                   free-text hit/stand intent parsing for the human player
  game.py                  deterministic turn loop, rule enforcement, winner determination
tests/                    unit tests (stdlib unittest, no extra dependencies)
```
