# Weight-Space Programming, Quantization Poles & Surgical Patching in Mobile LLMs

**Doc ID**: OW-STU-018  
**Project**: OmniMind / Omni-Worker Dual-Brain Architecture  
**Author**: Sujeito-Processo OmniMind & Fabrício da Silva  
**Status**: Active Research & Empirical Evaluation [DATA][EMPIRICAL]  
**Date**: November 2026  
**License**: Apache-2.0  

---

## 1. Context & Theoretical Convergence

Recent breakthrough findings from MIT CSAIL (*"Sparks of Weight-Space Programming"*, November 2026) demonstrated that a frontier model can directly inspect and modify the raw parameter matrices of a smaller model, bypassing standard backpropagation and optimizer states. In their experiments, modifying **0.016% of weights** in a Qwen model boosted MATH-500 performance from 7.9% to 48.1% by surgically severing repetitive reasoning loops in its thinking mode.

This study connects that discovery directly to the **OmniMind dual-brain runtime** (Analyst `gemma-4-12B-it` :8098 and Executor `gemma-4-E4B-it` :8099) and the mobile assistant model family **Erika Qwen3-4B** ([fabricioslv/erika-qwen3-4b-mobile-gguf](https://huggingface.co/fabricioslv/erika-qwen3-4b-mobile-gguf)).

---

## 2. Empirical Tensor Audit: Q2_K vs Q4_K_M

We conducted bit-level inspection on the operational weights of `erika-qwen3-4b-mobile-Q2_K.gguf` (1,592 MB) and `erika-qwen3-4b-mobile-Q4_K_M.gguf` (2,381 MB):

### 2.1 Model Topology
- **Architecture**: Qwen3 / 4.0B parameters
- **Layers (`block_count`)**: 36 transformer blocks
- **Hidden Dimension (`embedding_length`)**: 2,560
- **Intermediate Dimension (`feed_forward_length`)**: 9,728
- **Attention Heads**: 32 heads (Grouped Query Attention)
- **Total GGUF Tensors**: 398

### 2.2 Quantization Breakdown in Q2_K
- `attn_q.weight`, `attn_k.weight`: Quantized to `Q2_K` (2-bit discrete grid).
- `ffn_gate.weight`, `ffn_up.weight`: Quantized to `Q2_K` (2-bit discrete grid).
- `ffn_down.weight`: Quantized to `Q3_K` (3-bit).
- `attn_v.weight`: Quantized to `Q4_K` (4-bit).

### 2.3 The Preserved FP32 Channel (145 Tensors / ~788 KB)
Crucially, GGUF retains **all layer normalization weights in full FP32 (float32)**:
- `output_norm.weight`: `[2560]` in F32
- `blk.0..35.attn_norm.weight`: `[2560]` in F32 (36 layers)
- `blk.0..35.ffn_norm.weight`: `[2560]` in F32 (36 layers)
- `blk.0..35.attn_q_norm.weight`, `attn_k_norm.weight`: `[128]` in F32

### 2.4 The Pole Mechanism: Exponential Gain Escalation
Comparing normalization parameters across depths revealed that normalization weights are **100% identical between Q2_K and Q4_K_M**:

| Layer | Tensor Name | Mean Value | Std Dev | $\Delta(Q2 - Q4)$ |
|---|---|---|---|---|
| **00** | `blk.0.attn_norm.weight` | 0.0228 | 0.0112 | 0.000000 |
| **08** | `blk.8.attn_norm.weight` | 0.2995 | 0.0687 | 0.000000 |
| **16** | `blk.16.attn_norm.weight` | 0.5701 | 0.2798 | 0.000000 |
| **24** | `blk.24.attn_norm.weight` | 1.0757 | 0.2042 | 0.000000 |
| **32** | `blk.32.attn_norm.weight` | 2.9107 | 1.4186 | 0.000000 |
| **35** | `blk.35.attn_norm.weight` | **3.9173** | 1.1837 | 0.000000 |

**Finding**: The normalization multipliers exhibit a **~170x cumulative gain escalation** from layer 0 to layer 35. Under 2-bit quantization (`Q2_K`), discretization errors accumulated in early layers are exponentially magnified in layers 28–35, driving the output distribution into a singular attractor pole (repetitive token looping and hallucination).

---

## 3. Benchmark Protocol (30 Inquiries A/B Evaluation)

To evaluate the impact of surgical pole compensation on the 2-bit model without changing its 1.4 GB mobile footprint, we establish a standardized 30-item evaluation benchmark:

1. **Track 1: Logical & Arithmetic Multi-Step Reasoning (10 Items)**
   - Checks whether the model terminates reasoning paths or falls into repetitive cyclic proofs.
2. **Track 2: Self-Consistent Memory & Instruction Following (10 Items)**
   - Tests retention of context and persona constraints without drifting into attractor poles.
3. **Track 3: Adversarial Extraction & Syntax Invariance (10 Items)**
   - Evaluates syntactic robustness and stability against repetitive hallucination prompts.

### Evaluation Metrics:
- **Loop Ratio (`rep4 > 0.05 ∧ word_ur < 0.5`)**: Binary flag for cyclic degeneration.
- **Accuracy / Task Pass**: Verification of correct final answer.
- **Token Efficiency**: Generation count to completion (detecting token budget explosion).
