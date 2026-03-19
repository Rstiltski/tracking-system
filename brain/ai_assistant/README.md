# Autonomous AI Agent Architecture

This module contains the upgraded cognitive mechanisms for the tracking system, operating on advanced autonomous agent principles. This elevates the AI from a standard generative system to a sophisticated, goal-oriented agentic architecture.

## Core Paradigms Implemented

### 1. The ReAct Loop (Reasoning + Acting)
The AI executing tasks through a structured Think -> Act -> Observe -> Iterate loop. Instead of immediate single-turn generation, the `ThinkingBrain` leverages a `.scratchpad.json` to process intermediate variables before committing to an action pathway.

### 2. RAISE Memory Framework
Memory (`memory_manager.py`) is fully stateful and segmented:
*   **Short-Term Context:** A sliding window of active UI and conversational state.
*   **Working Memory (The Scratchpad):** An isolated buffer for partial logic and calculations.
*   **Long-Term Decisions (`decisions.log`):** A robust file-driven database of the agent's historic actions. Relevance retrieval uses **Semantic Entity Extracting** matching over pure keyword frequency.
*   **Reflexion:** Linguistic self-evaluation logs are appended for error correction.

### 3. LATS (Language Agent Tree Search)
The `TaskDecomposer` engine doesn't just produce deterministic linear checklists. Each `TaskNode` supports:
*   Alternative Branches
*   Probability Scoring
*   Self-Healing Anomaly Recovery Strategies

### 4. Hierarchical MAS (Multi-Agent System)
Task trees use `assigned_agent_role` parameters, classifying nodes for "Generalist", "Researcher", or "Coder" delegation. This shifts the tracking app towards a parallel execution topology.

## Development Directives
- **Never bypass the Memory Manager:** All persistent state decisions must route through `log_decision`.
- **Entities over Keywords:** When designing prompts, prioritize explicit entity extraction to aid long-term retrieval.
- **Maintain the Buffer:** Heavy computations should write to the Scratchpad before attempting final intent resolution.
