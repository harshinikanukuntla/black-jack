"""Decision-making "brains" for AI players.

An AI player's brain only decides HIT or STAND for a hand that's already
allowed to keep drawing (see Player.can_draw in players.py). It never
needs to re-check the card cap or a total of 21 itself, since the game
loop only ever calls it when a real choice exists. A brain just answers
one question, plus an optional flavor comment.

Two implementations:
  - HeuristicBrain: fast, deterministic, threshold-based, with a
    per-agent "risk_tolerance" personality knob. Needs nothing external
    and always works.
  - OllamaBrain: asks a local open-weight model (via Ollama, through
    LangChain's ChatOllama) to make the call. Used when available. If
    Ollama isn't reachable, the model isn't pulled, or langchain-ollama
    isn't installed, the game falls back to HeuristicBrain instead.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Literal, Protocol

Decision = Literal["hit", "stand"]


class Brain(Protocol):
    """A pluggable hit/stand decision-maker for an AI player."""

    def decide(self, name: str, hand: list[int], total: int, cards_drawn: int, max_cards: int) -> Decision:
        ...

    def comment(self, name: str, decision: Decision, total: int) -> str:
        ...


@dataclass
class HeuristicBrain:
    """Threshold-based decision-making with a personality knob.

    ``risk_tolerance`` shifts the stand threshold: negative values make the
    agent cautious (stands early), positive values make it aggressive
    (keeps hitting for a higher total). Since cards are drawn 2-11 (not a
    standard deck), a small amount of randomness near the threshold keeps
    agents from feeling perfectly robotic.
    """

    risk_tolerance: int = 0

    def decide(self, name: str, hand: list[int], total: int, cards_drawn: int, max_cards: int) -> Decision:
        threshold = 16 + self.risk_tolerance
        if total < threshold:
            return "hit"
        if total == threshold:
            return random.choice(["hit", "stand"])
        return "stand"

    def comment(self, name: str, decision: Decision, total: int) -> str:
        if decision == "hit":
            options = [
                f"{total} isn't enough for me yet. Please deal me another.",
                f"I'll push my luck at {total}. Hit me.",
                f"Sitting at {total}, I want more. Draw again, please.",
            ]
        else:
            options = [
                f"{total} feels safe. I'll stand.",
                f"I'm happy with {total}. I'm standing.",
                f"No need to risk busting from {total}. I'm done.",
            ]
        return random.choice(options)


class BrainUnavailableError(RuntimeError):
    """Raised when an LLM-backed brain cannot be constructed or reached."""


class OllamaBrain:
    """Decision-making powered by a local open-weight model via Ollama.

    Uses LangChain's ``ChatOllama`` integration so the agent's "thinking" is
    a real LLM call rather than a fixed rule. Construction eagerly performs
    a lightweight health-check call so the caller can fall back to
    :class:`HeuristicBrain` immediately if Ollama isn't reachable, instead
    of failing mid-game.
    """

    def __init__(self, personality: str, model: str = "llama3.1:8b",
                 base_url: str = "http://localhost:11434", timeout: float = 8.0) -> None:
        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            from langchain_ollama import ChatOllama
        except ImportError as exc:  # pragma: no cover - depends on optional install
            raise BrainUnavailableError("langchain-ollama is not installed") from exc

        self._SystemMessage = SystemMessage
        self._HumanMessage = HumanMessage
        self.personality = personality
        try:
            self._llm = ChatOllama(model=model, base_url=base_url, temperature=0.5,
                                    num_predict=12, timeout=timeout)
            # Fail fast if the server/model isn't actually reachable.
            self._llm.invoke([HumanMessage(content="Reply with the single word: ready")])
        except Exception as exc:  # noqa: BLE001 - any transport/model error means "unavailable"
            raise BrainUnavailableError(f"Ollama not reachable or model missing: {exc}") from exc

    def _ask(self, system_prompt: str, user_prompt: str) -> str:
        response = self._llm.invoke([
            self._SystemMessage(content=system_prompt),
            self._HumanMessage(content=user_prompt),
        ])
        return str(response.content).strip()

    def decide(self, name: str, hand: list[int], total: int, cards_drawn: int, max_cards: int) -> Decision:
        system_prompt = (
            f"You are {name}, an AI agent playing a simplified blackjack "
            "variant. Cards are drawn uniformly at random between 2 and 11 "
            "(not a standard 52-card deck). Each player may draw at most "
            f"three cards total. Your personality: {self.personality}. "
            "Respond with exactly one word: HIT or STAND."
        )
        user_prompt = (
            f"Your hand so far: {hand} (total {total}), "
            f"you have drawn {cards_drawn} of {max_cards} allowed cards. "
            "Do you want to HIT or STAND?"
        )
        try:
            text = self._ask(system_prompt, user_prompt).lower()
        except Exception:  # noqa: BLE001 - a mid-game failure degrades to a safe default
            return "stand" if total >= 16 else "hit"
        first_word = text.split()[0].strip(".,!:;\"'") if text.split() else ""
        if first_word.startswith("hit"):
            return "hit"
        if first_word.startswith("stand"):
            return "stand"
        return "hit" if "hit" in text else "stand"

    def comment(self, name: str, decision: Decision, total: int) -> str:
        system_prompt = (
            f"You are {name}, an AI blackjack player with this personality: "
            f"{self.personality}. In one short, natural sentence (under 15 "
            "words), explain your decision in character. Don't say your own "
            "name. No preamble."
        )
        user_prompt = f"Your total is {total} and you chose to {decision.upper()}."
        try:
            return self._ask(system_prompt, user_prompt)
        except Exception:  # noqa: BLE001
            return f"({decision} at {total})"


@dataclass
class Personality:
    name: str
    risk_tolerance: int
    description: str


DEFAULT_PERSONALITIES: list[Personality] = [
    Personality(
        "Cautious Cal", risk_tolerance=-3,
        description=(
            "a methodical, numbers-driven retiree who treats every hand like a "
            "spreadsheet to be balanced; he mutters about 'protecting the principal', "
            "is happy to walk away with a modest total, and would rather stand on a "
            "mediocre score than risk busting on a greedy draw"
        ),
    ),
    Personality(
        "Balanced Bailey", risk_tolerance=0,
        description=(
            "a calm, pragmatic poker-night regular who weighs the odds out loud before "
            "deciding, adapts to how the hand is going rather than following a rigid "
            "rule, and treats each draw as a fair coin flip between reward and regret"
        ),
    ),
    Personality(
        "Aggressive Amy", risk_tolerance=3,
        description=(
            "a thrill-seeking high-roller with a 'go big or go home' streak; she talks "
            "trash about playing it safe, chases a big total even when the odds turn "
            "against her, and would rather bust swinging for 21 than stand on anything "
            "she considers boring"
        ),
    ),
]


def personality_for_index(index: int) -> Personality:
    """Return a personality for AI player ``index``, cycling if there are more agents than presets."""
    base = DEFAULT_PERSONALITIES[index % len(DEFAULT_PERSONALITIES)]
    if index < len(DEFAULT_PERSONALITIES):
        return base
    return Personality(f"{base.name} #{index // len(DEFAULT_PERSONALITIES) + 1}",
                        base.risk_tolerance, base.description)


_notice_shown = False


def build_brain(personality: Personality, use_llm: bool, model: str, base_url: str) -> Brain:
    """Build the best available brain for a personality.

    Tries Ollama first when ``use_llm`` is set; falls back to the
    heuristic brain (printing a one-time notice) on any failure so the
    game always runs.
    """
    global _notice_shown
    if use_llm:
        try:
            return OllamaBrain(personality.description, model=model, base_url=base_url)
        except BrainUnavailableError as exc:
            if not _notice_shown:
                print(f"[note] LLM brain unavailable ({exc}); "
                      f"falling back to the built-in heuristic brain for AI agents.\n")
                _notice_shown = True
    return HeuristicBrain(risk_tolerance=personality.risk_tolerance)
