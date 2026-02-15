"""Coring scorer for Sentient System.

Provides a -10.0..+10.0 scoring API with demographic multipliers and emotion adjustments.

Usage:
    from brain.invariants.scorer import Scorer, Emotion
    s = Scorer()
    score = s.score(invariants=['M-001', 'L-002'], demographic='invoices.py', emotion=Emotion.ANXIOUS)
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
import os
import yaml


def _load_config_file(path: str) -> Optional[ScorerConfig]:
    try:
        if not os.path.exists(path):
            return None
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        multipliers = data.get('multipliers', {})
        base_weights = data.get('base_weights', {})
        harvest_threshold = data.get('harvest_threshold', 7.0)
        return ScorerConfig(multipliers=multipliers, base_weights=base_weights, harvest_threshold=harvest_threshold)
    except Exception:
        return None


def _save_config_file(cfg: ScorerConfig, path: str) -> None:
    data = {
        'multipliers': cfg.multipliers,
        'base_weights': cfg.base_weights,
        'harvest_threshold': cfg.harvest_threshold,
    }
    ddir = os.path.dirname(path)
    if ddir and not os.path.exists(ddir):
        os.makedirs(ddir, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f)


class Emotion(str, Enum):
    NEUTRAL = "neutral"
    ANXIOUS = "anxious"
    CURIOUS = "curious"
    CAUTIOUS = "cautious"


@dataclass
class ScorerConfig:
    multipliers: Dict[str, float]
    base_weights: Dict[str, float]
    harvest_threshold: float = 7.0


class Scorer:
    def __init__(self, config: Optional[ScorerConfig] = None):
        default_multipliers = {
            'invoices.py': 1.7,
            'payments.py': 1.6,
            'customers.py': 1.5,
            'jobs.py': 1.5,
            'accounting': 1.5,
            'tests': 1.2,
            'css': 0.3,
            'docs': 0.3,
        }

        default_weights = {
            'M-001': 10.0,
            'M-002': 9.5,
            'M-003': 10.0,
            'M-004': 9.0,
            'M-005': 8.0,
            'M-006': 8.5,
            'L-001': 9.5,
            'L-002': 9.0,
            'L-003': 8.5,
            'L-004': 7.5,
            'L-005': 7.0,
            'I-001': 9.0,
            'I-002': 8.5,
            'I-003': 6.0,
            'I-004': 9.0,
            'E-001': 7.5,
            'E-002': 7.0,
            'E-003': 6.0,
            'E-004': 6.5,
            'E-005': 8.0,
            'T-001': 5.0,
            'T-002': 4.5,
            'T-003': 5.0,
            'T-004': 4.0,
        }

        if config is None:
            # try to load config/scorer.yaml if present
            cfg = None
            try:
                cfg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'scorer.yaml'))
                cfg = _load_config_file(cfg_path)
            except Exception:
                cfg = None

            config = cfg or ScorerConfig(multipliers=default_multipliers, base_weights=default_weights)

        self.config = config

    def score(self, *, invariants: List[str], demographic: Optional[str] = None, emotion: Emotion = Emotion.NEUTRAL, confidence: float = 0.9) -> float:
        """Compute a coring score for a candidate change.

        invariants: list of invariant codes satisfied (e.g. ['M-001']) or violated (prefix with '-' to represent violation).
        demographic: file or domain string to apply multiplier
        emotion: current emotional state
        confidence: 0..1 LLM confidence
        """
        total = 0.0
        for inv in invariants:
            if not inv:
                continue
            negate = False
            key = inv
            if inv.startswith('-'):
                negate = True
                key = inv[1:]
            w = self.config.base_weights.get(key, 0.0)
            total += -w if negate else w

        multiplier = 1.0
        if demographic:
            mult = self.config.multipliers.get(demographic)
            if mult is None:
                for k, v in self.config.multipliers.items():
                    if demographic.startswith(k):
                        mult = v
                        break
            if mult:
                multiplier = mult

        total *= multiplier

        total = self._apply_emotion_adjustment(total, emotion, confidence)

        total = max(min(total, 10.0), -10.0)
        return float(total)

    def _apply_emotion_adjustment(self, score: float, emotion: Emotion, confidence: float) -> float:
        if emotion == Emotion.NEUTRAL:
            return score * (0.9 + 0.1 * confidence)

        if emotion == Emotion.ANXIOUS:
            penalty = -3.0 if confidence < 0.85 else 0.0
            scale = 0.3 + 0.7 * confidence
            return score * scale + penalty

        if emotion == Emotion.CAUTIOUS:
            if score > 0:
                return score * (0.6 + 0.4 * confidence)
            return score * (1.2 - 0.2 * confidence)

        if emotion == Emotion.CURIOUS:
            if score > 0:
                return score * (1.0 + 0.6 * (1.0 - confidence))
            return score * (0.9 + 0.1 * confidence)

        return score

    def will_harvest(self, score: float) -> bool:
        return score >= float(self.config.harvest_threshold)

    def reload_from_file(self, path: Optional[str] = None) -> bool:
        """Reload scorer config from YAML file path. If path is None, uses default config/scorer.yaml.

        Returns True if reload succeeded and config replaced, False otherwise.
        """
        try:
            if path is None:
                path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'scorer.yaml'))
            cfg = _load_config_file(path)
            if not cfg:
                return False
            self.config = cfg
            return True
        except Exception:
            return False

    def save_to_file(self, path: Optional[str] = None) -> bool:
        """Save current scorer config to YAML file. If path not provided, writes to config/scorer.yaml."""
        try:
            if path is None:
                path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'scorer.yaml'))
            _save_config_file(self.config, path)
            return True
        except Exception:
            return False


__all__ = ["Scorer", "ScorerConfig", "Emotion"]
