# OW-AUD-019 — Juíz Avaliador 2: Competição Kaggle Gemma 4 + Comparação SOTA

## 1. Competições Kaggle (fatos verificados)
- Paper Track: writeup ≤3000 palavras, deadline 12/11/2026 23:59 UTC, prêmios $15k Overall + $10k Best New Resource + $10k Best New Application; rubrica 5 critérios (Novelty, Quality, Relevance, Verifiability, Clarity) 0–5, média.
- Main competition: ~120 hidden Python tasks SWE-bench-like, deadline 02/12/2026, prêmios $65k.
- Comunidade: scaffold/capacity factorial (E4B/12B/26B × min/max scaffold × 5 seeds), Qwen 3.6 35B-A3B vs Gemma 4 26B no SWE-bench Lite (48.33% vs 38.67%), failure modes `wrong_logic` (76%), `incomplete_patch` (14%), `no_submission` (10%); Gemma 4 26B falha mais por `no_submission`/`incomplete_patch` por capacidade.
- Modos de falha Gemma 4: repetição "doom loops" (arXiv 2606.13705): E2B 1 neurônio, E4B 3/430080, 31B 1100 neurônios, 26B 3 experts de 3840; formato de tool-calling (function calling vs plain text) determina sucesso (Gemma 4 26B: 40+ erros OpenHands → 9 steps SWE-agent); Ollama tool calls vazios; E4B Tau2 42.2% vs 31B 76.9%.
- Gemma 4 model card: E2B 2.3B/35 camadas, E4B 4.5B/42, 12B 11.95B/48, 31B 30.7B/60; LiveCodeBench v6 80.0/77.1/72.0/52.0/44.0%.

## 2. Comparação SOTA (2024–2026)
- a) Perfis executivos predizendo falhas: nosso Psicodiagnóstico-V (WCST/N-back/IGT/Stroop) é original; literatura recente foca benchmarks comportamentais (SWE-bench, Tau2) e scaffold/capacity, sem psicometria. Gap: falta validação estatística com N maior (atual N=3 Gemma) e comparação com baselines de prompt/scaffold da comunidade.
- b) Estados internos / SVD / MPS / Representation Engineering: nossa captura por camada + eff_rank (12B 114.6 vs E4B 40.3) alinha com arXiv 2606.13705 (per-layer attribution, neuron surgery). Gap: não há intervenção de peso (neuron surgery) nem comparação com probes lineares / SAE; precisamos explicitar método (Roy & Vetterli participation ratio) e limitações (rank~1 basal, fid≡1.0).
- c) Governança metacognitiva: Cascade Reset/Circuit Breakers/consenso tri-state é forte e inédito; gap: efeito binário não significativo (McNemar 16×12, p≈0.45, N=60/braço); precisa escala e ablação de threshold K.
- d) Proxies IIT/PyPhi/GWT: nossa honesty (Φ=0 sistema inteiro, díade {M,R} irredutível, GWT-lite) é rigorosa; gap: não comparar com outros proxies de consciência (information bottleneck, causal emergence) nem com benchmarks de "agent self-monitoring".

## 3. Gaps do `/content/WRITEUP_ESQUELETO.md` vs arquitetura completa
- Falta integrar explicitamente: (i) dual-brain 12B+E4B com peer-swap VRAM e chat-template obrigatório; (ii) captura espectral profunda por camada e trajetória por passo (OMNI_ACT_STEP_EVERY=8) quando MPS escalar falhou (fid≡1.0, omissão de `store.py`); (iii) bateria de refatoração multi-turno com detector precoce `coverage_missing`; (iv) supervisão afetiva L0–L4 (16/16 detecções, 100% worker_degen2, escalonamento CVV/CAPS/SAMU).
- Falta posicionamento competitivo frente a trabalhos da comunidade (scaffold/capacity factorial, Qwen vs Gemma failure taxonomy, neuron surgery) e claim de "Best New Application" (omni_worker como aplicativo).
- Falta seção de "Limitações de generalização" mais forte: N=3 correlações, juízes LLM assimétricos (κ=0.4722), janela ~120 tokens, cascade subpotente.

## 4. Críticas de revisor Sênior DeepMind + blindagem
1. "Correlação N=3 não é evidência" → rotular exploratória, adicionar bootstrap/permutation e, se possível, N maior (rodar 26B-A4B em agent-runs públicos ou incluir E2B).
2. "Degeneração é artefato de protocolo" → já endereçado (format-ablation 0% chat vs 62.5% completion); fortalecer com ablação formato-casado na quantização (§3.2b) e relatar tamanho de efeito + IC.
3. "omni_worker não reporta SWE-bench score" → esclarecer que é aplicação/supervisão, não leaderboard; fornecer métricas internas (10/10 compilação, 0/88 degeneração, 16/16 afeto) e reproducibilidade (testes 455, código público).
4. "IIT claims overreach" → já honesto (Φ=0, GWT-lite); adicionar disclaimer explícito e citar PyPhi 1.2.0.
5. "Novelty vs neuron surgery (arXiv 2606.13705)" → diferenciar: eles editam pesos para loops factuais; nós perfilamos função executiva e governança de agente; citar e comparar.
6. "Clarity/Verifiability" → fornecer tabelas com proveniência (sqlite, SHA256, seeds) e links públicos.

## 5. Recomendações de ação (sem modificar código)
- Finalizar writeup ≤3000 palavras com seções 3.4a–d já presentes; adicionar "Competitive Positioning" e "Reproducibility".
- Criar dataset público (bateria V10 + runs + análise) para Best New Resource.
- Submeter antes de 12/11/2026; considerar arXiv PDF link.
- Manter git read-only conforme regra.
