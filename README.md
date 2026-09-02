# READFLIX — AI Library Assistant

An end-to-end Retrieval-Augmented Generation (RAG) assistant for READFLIX Library that answers questions about membership, pricing, timings, seating, facilities, rules, and other library policies using a curated knowledge base.

The system combines **LangGraph, LangChain, Qdrant, OpenAI, FastAPI, Guardrails AI, DeepEval, Docker, and observability tooling** to provide grounded responses with retrieval, reranking, security checks, persistent conversation state, and automated RAG evaluation.

---

## Overview

READFLIX AI is designed as a domain-specific knowledge assistant rather than a generic chatbot.

Instead of relying only on the language model's pretrained knowledge, the system retrieves relevant information from the READFLIX knowledge base and uses that information as context for answer generation.

### Core flow

```text
User Question
      │
      ▼
Input Guardrails
      │
      ▼
Query Processing / Planner
      │
      ▼
Qdrant Retrieval
      │
      ▼
Reranking
      │
      ▼
Relevant Context
      │
      ▼
LLM Generation
      │
      ▼
Output / Safety Validation
      │
      ▼
Final Grounded Response
