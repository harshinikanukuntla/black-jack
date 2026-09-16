# Blackjack with AI Agents

A simplified Blackjack game that runs in the terminal. You play against three AI agents, each with a different personality, and a dealer who also plays a hand. Cards aren't drawn from a real deck, a card is just a random number between 2 and 11, and everyone (you included) can draw at most three cards.

The AI agents make their own hit or stand decisions using a local LLM (Llama 3.1 via Ollama, called through LangChain), and fall back to a rule based decision if the LLM isn't available. Either way the game always runs to completion.

## What this covers from the assignment

| Requirement | How it's handled |
|---|---|
| CLI Python app, at least 3 AI agents | `main.py` is the entry point, 3 AI agents by default (`--agents` to change it) |
| Any AI framework and LLM | LangChain, calling a local Llama 3.1 model through Ollama |
| Given `draw_card()` function (random 2 to 11) | Used as is in `cards.py`, untouched |
| One AI dealer agent | `Dealer` class in `dealer.py`, the only one that calls `draw_card()` |
| Each player can draw up to 3 cards | Enforced in `Player.can_draw` / `Player.add_card` in `players.py` |
| Players ask the dealer to draw, they can't draw themselves | Every draw goes through `Dealer.draw_for()`, nothing else touches `draw_card()` |
| Winner is highest total under 21 after all turns | `Game._announce_winner()` in `game.py` |
| Runs entirely in the terminal | No GUI anywhere, plain `input()`/`print()` |
| AI agents simulate decision making | `brains.py`, each agent decides hit or stand based on its hand and personality |
| User interacts naturally ("deal me the next card") | `nlp.py` parses free text like "hit me", "deal me another", "I'll stand" |
| Clearly shows outcome and winner | Final table and winner announcement printed at the end of every game |

One thing I added beyond the spec: the dealer also plays its own hand at the end (standard "hit until 17" rule, not AI driven, since real dealers follow a fixed rule rather than making a judgment call) and competes for the win alongside everyone else.

## Requirements

- Python 3.12 or newer
- Optional: [Ollama](https://ollama.com) if you want the real LLM brain instead of the fallback

## Running it

This project uses `uv`, but plain pip works too.

With uv:
```bash
uv sync
uv run python3 main.py
```

With pip:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

You'll be asked for your name at the start. If you'd rather skip that prompt, pass `--name` directly.

Useful flags:
```bash
python3 main.py --no-llm            # skip Ollama entirely, use the rule based brain
python3 main.py --agents 5          # play with 5 AI agents instead of 3
python3 main.py --seed 7            # same card sequence every run, handy for testing
python3 main.py --name Alex         # skip the interactive name prompt
```

## Playing

When it's your turn, just type what you'd naturally say: "hit me", "deal me the next card", "I'll stand", "stay", "no more". No need to type exact commands.

## Using the real LLM instead of the fallback

The game works fine without this, it just uses simpler rule based logic for the AI agents. To get the actual LLM making decisions:

```bash
brew install ollama
brew services start ollama
ollama pull llama3.1:8b
```

Then run the game normally, no extra flag needed. If Ollama isn't reachable for any reason, the game prints a short note and keeps going on the fallback brain instead of crashing.

## Tests

```bash
uv run python -m unittest discover -s tests -v
```

26 tests, covering the three card cap, bust detection, natural language parsing, the fallback brain's decision logic, the dealer's fixed rule, and full game runs including ties and everyone busting.

## Files

```
main.py       entry point, command line flags, asks for your name
cards.py      the given draw_card() function
dealer.py     the dealer agent, draws cards for everyone, plays its own hand
brains.py     hit/stand decision logic, LLM based and rule based
players.py    player state, hand, bust check, three card limit
nlp.py        turns free text like "hit me" into a hit/stand decision
game.py       runs the turns, enforces the rules, decides the winner
tests/        unit tests
```
