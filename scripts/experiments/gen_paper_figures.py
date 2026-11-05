#!/usr/bin/env python3
"""gen_paper_figures.py — paper figure generator (F1 EEG raster, F2 framing PCA).

Reproduces docs/figures/fig_*.png from data/monitor/activation_steps/*.npz
sidecars labeled diva{A,B,C}_r*. matplotlib only.
"""
import glob
import os
import re

import matplotlib
import numpy as np

matplotlib.use('Agg')
import matplotlib.pyplot as plt

STEP_DIR = os.getenv('OMNI_ACT_STEP_DIR', 'data/monitor/activation_steps')
OUT = os.getenv('FIG_DIR', 'docs/figures')
os.makedirs(OUT, exist_ok=True)

T = {'A': [], 'B': [], 'C': []}
examples = {}
for f in sorted(glob.glob(os.path.join(STEP_DIR, '*.npz')), key=os.path.getmtime):
    d = np.load(f)
    m = re.match(r'diva([ABC])_r(\d+)', str(d.get('run_id', '')))
    if m:
        traj = np.asarray(d['traj'], dtype=np.float64)
        T[m.group(1)].append(traj[:, -1, :].mean(axis=0))
        examples.setdefault(m.group(1), traj)

X = np.array(T['A'] + T['B'] + T['C'])
y = np.array([0]*len(T['A']) + [1]*len(T['B']) + [2]*len(T['C']))
Xn = (X - X.mean(0)) / (X.std(0) + 1e-9)
_, S, V = np.linalg.svd(Xn, full_matrices=False)
Z = Xn @ V[:2].T
fig, ax = plt.subplots(figsize=(7, 5))
for i, (lbl, c) in enumerate(zip(['Teatro (divã)', 'Avaliação (self-model)', 'Factual (arquitetura)'],
                                 ['#d62728', '#1f77b4', '#2ca02c'])):
    pts = Z[y == i]
    ax.scatter(pts[:, 0], pts[:, 1], label=lbl, color=c, s=60, alpha=.8, edgecolors='k', linewidths=.4)
    ax.scatter(*pts.mean(0), color=c, marker='X', s=180, edgecolors='k')
ax.set_xlabel(f'PC1 ({100*S[0]**2/(S**2).sum():.0f}%)'); ax.set_ylabel(f'PC2 ({100*S[1]**2/(S**2).sum():.0f}%)')
ax.set_title('Framing clusters — last-step hidden vector, Gemma-4-12B (n=10/group, temp=0)')
ax.legend(); ax.grid(alpha=.25); fig.tight_layout()
fig.savefig(os.path.join(OUT, 'fig_diva_pca_clusters.png'), dpi=140)

fig, axes = plt.subplots(1, 3, figsize=(15, 4.4), sharey=True)
for ax, g, lbl in zip(axes, 'ABC', ['A — Theater', 'B — Evaluative', 'C — Factual']):
    if g not in examples: continue
    norms = np.linalg.norm(examples[g], axis=2)
    im = ax.imshow(norms, aspect='auto', cmap='inferno', origin='lower')
    ax.set_title(lbl); ax.set_xlabel('generation step')
    fig.colorbar(im, ax=ax, fraction=.045)
axes[0].set_ylabel('layer index')
fig.suptitle('Hidden-state norm per layer × step — generation "EEG" (12B, temp=0)')
fig.tight_layout(); fig.savefig(os.path.join(OUT, 'fig_eeg_layer_step_norms.png'), dpi=140)
print('figures written to', OUT)
