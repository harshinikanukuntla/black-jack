#!/usr/bin/env python3
"""CLI entry point for the simplified AI-agent Blackjack game."""

from __future__ import annotations

import argparse
import sys

from game import Game


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Play blackjack against three AI agents and a dealer.")
    parser.add_argument("--agents", type=int, default=3, help="Number of AI agent players (default: 3).")
    parser.add_argument("--name", default=None,
                         help="Your player name. If omitted, you'll be asked for it interactively.")
    parser.add_argument("--no-llm", action="store_true",
                         help="Skip Ollama entirely and use the built-in heuristic brain for AI agents.")
    parser.add_argument("--model", default="llama3.1:8b", help="Ollama model tag to use for AI decisions.")
    parser.add_argument("--ollama-url", default="http://localhost:11434", help="Ollama server base URL.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed, for reproducible card draws.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.seed is not None:
        import random
        random.seed(args.seed)

    if args.agents < 1:
        print("error: --agents must be at least 1", file=sys.stderr)
        return 1

    player_name = args.name
    if player_name is None:
        try:
            player_name = input("What's your name? ").strip() or "You"
        except (EOFError, KeyboardInterrupt):
            print("\nGame interrupted. Goodbye!")
            return 130

    game = Game(
        human_name=player_name,
        num_agents=args.agents,
        use_llm=not args.no_llm,
        model=args.model,
        base_url=args.ollama_url,
    )
    try:
        game.run()
    except (EOFError, KeyboardInterrupt):
        print("\nGame interrupted. Goodbye!")
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
