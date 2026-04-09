"""
Intrinsic Drive — Entropy-based dynamic temperature regulation (§3.3).

Implements the full mathematical pipeline from the paper:
  1. Embed recent W_t thoughts via the LTM embedding API
  2. Maintain K cluster centers as online running averages
  3. Compute cosine distance from h_t to each center C_k
  4. Apply softmax with temperature τ → probability distribution p(x_k)
  5. Compute Shannon entropy H(W) = -Σ p log p
  6. Dynamic temperature: T_gen = T_base + α * exp(-β * H(W))
"""
from __future__ import annotations

import math
from typing import List, Optional

import numpy as np


class EntropyDrive:
    """
    Maintains semantic cluster centers and computes dynamic generator temperature.

    Cluster centers are updated online as an exponential moving average, avoiding
    the need for a full K-means re-fit each tick.
    """

    def __init__(
        self,
        K: int = 5,
        tau: float = 0.5,
        T_base: float = 0.7,
        alpha: float = 1.3,
        beta: float = 2.0,
        entropy_window: int = 10,
        ema_decay: float = 0.5,
    ) -> None:
        self.K = K
        self.tau = tau
        self.T_base = T_base
        self.alpha = alpha
        self.beta = beta
        self.entropy_window = entropy_window
        self.ema_decay = ema_decay

        # Cluster centers: shape (K, embedding_dim), None until initialized
        self._centers: Optional[np.ndarray] = None
        # Latest thought embedding (used for single-tick entropy computation)
        self._last_embedding: Optional[np.ndarray] = None

        # Diagnostics exposed to UI
        self.last_entropy: float = math.log(K)  # max entropy initially
        self.last_T_gen: float = T_base

    # ── Public API ────────────────────────────────────────────────────────────

    def update(self, thought_embedding: List[float]) -> None:
        """Register the embedding of the latest winning thought W_t."""
        h = _normalize(np.array(thought_embedding, dtype=np.float32))
        self._last_embedding = h
        self._update_centers(h)

    def compute_T_gen(self) -> float:
        """
        Compute entropy H(W) and derive dynamic generator temperature T_gen.

        Returns T_base when fewer than K thoughts have been observed
        (not enough data to form meaningful clusters).
        """
        if self._last_embedding is None or self._centers is None:
            self.last_entropy = math.log(max(self.K, 1))
            self.last_T_gen = self.T_base
            return self.T_base

        H = self._compute_entropy()
        self.last_entropy = H
        T_gen = self.T_base + self.alpha * math.exp(-self.beta * H)
        self.last_T_gen = round(min(T_gen, 2.0), 4)
        return self.last_T_gen

    # ── Internal ──────────────────────────────────────────────────────────────

    def _update_centers(self, h: np.ndarray) -> None:
        """Online EMA update of cluster centers."""
        if self._centers is None:
            # Initialize: assign h to first center, spread randomly
            dim = h.shape[0]
            centers = np.random.randn(self.K, dim).astype(np.float32)
            centers[0] = h
            self._centers = np.array([_normalize(c) for c in centers])
            return

        # Find nearest center and update it via EMA
        dists = _cosine_distances(h, self._centers)
        nearest = int(np.argmin(dists))
        self._centers[nearest] = _normalize(
            self.ema_decay * self._centers[nearest] + (1 - self.ema_decay) * h
        )

    def _compute_entropy(self) -> float:
        """Shannon entropy over softmax-weighted distances to cluster centers.

        Uses the current winning thought embedding against all K cluster centers.
        Softmax with temperature τ converts distances to a probability distribution;
        Shannon entropy H(W) measures how spread the thought is across clusters.
        """
        h_t = self._last_embedding
        distances = _cosine_distances(h_t, self._centers)  # shape (K,)

        # Softmax with scaling temperature τ (eq. 2 in paper)
        scaled = -distances / self.tau
        scaled -= scaled.max()  # numerical stability
        exp_vals = np.exp(scaled)
        p = exp_vals / exp_vals.sum()

        # Shannon entropy H(W) = -Σ p log p (eq. 3)
        eps = 1e-12
        H = -float(np.sum(p * np.log(p + eps)))
        return H


# ── Helpers ───────────────────────────────────────────────────────────────────

def _normalize(v: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(v)
    return v / norm if norm > 1e-12 else v


def _cosine_distances(h: np.ndarray, centers: np.ndarray) -> np.ndarray:
    """Compute d_{t,k} = 1 - cosine_similarity(h, C_k) for all k."""
    # h: (d,), centers: (K, d)
    dots = centers @ h  # (K,)
    center_norms = np.linalg.norm(centers, axis=1)
    h_norm = np.linalg.norm(h)
    denom = center_norms * h_norm + 1e-12
    cosine_sims = dots / denom
    return 1.0 - cosine_sims  # (K,)
