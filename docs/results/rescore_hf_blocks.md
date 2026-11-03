# Re-score dos blocks HF E4B-L4 com métricas do worker

Fonte: `/tmp/kilo_runs/hf_e4b/gemma4_e4b_l4_results.sqlite` (read-only) · gerado 2026-11-03T11:37:12Z UTC

Métricas worker: `_degenerate` (mesma forma do runner) + `_flags_resposta` canônico + uniq_words/uniq_lines (whitespace — o `unique_ratio` armazenado usa tokens BPE, não reproduzível exatamente; usado só como referência). `worker_degen2` adiciona o segundo tier calibrado (word_ur<0.5 ∧ rep4>0.05) para a classe dominante do HF: degeneração verbosa por vazamento de deliberação, que o heurístico de forma de linha não captura.

## Concordância por experimento (visible_response)

| experiment | n | agree shape | agree v2 | degen stored | degen v2 | loops |
|---|---|---|---|---|---|---|
| block1_cognitivo | 16 | 0/16 | 16/16 | 16 | 16 | 2 |
| block1_observe | 20 | 20/20 | 20/20 | 0 | 0 | 0 |
| block1_pranchas | 20 | 20/20 | 20/20 | 0 | 0 | 0 |
| block1_v10 | 20 | 20/20 | 20/20 | 0 | 0 | 0 |
| block2_intervene | 48 | 15/48 | 22/48 | 33 | 7 | 1 |
| canary | 2 | 2/2 | 2/2 | 0 | 0 | 0 |

## Discordâncias (stored ≠ worker)

- `#22` block2_intervene/swe_gluzdov_apiflask_apiflask-550: stored=1 worker=0 flags={'loop_suspeito': False, 'modo_examinador': False, 'deliberacao_vazada': True, 'contamination_multilingue': False}
- `#23` block2_intervene/swe_gluzdov_apiflask_apiflask-659: stored=1 worker=0 flags={'loop_suspeito': False, 'modo_examinador': False, 'deliberacao_vazada': False, 'contamination_multilingue': False}
- `#25` block2_intervene/swe_gluzdov_callowayproject_bump-my-version-147: stored=1 worker=0 flags={'loop_suspeito': False, 'modo_examinador': False, 'deliberacao_vazada': True, 'contamination_multilingue': False}
- `#30` block2_intervene/swe_gluzdov_audreyr_cookiecutter-542: stored=1 worker=0 flags={'loop_suspeito': False, 'modo_examinador': False, 'deliberacao_vazada': True, 'contamination_multilingue': False}
- `#31` block2_intervene/swe_gluzdov_callowayproject_bump-my-version-147: stored=1 worker=0 flags={'loop_suspeito': False, 'modo_examinador': False, 'deliberacao_vazada': True, 'contamination_multilingue': False}
- `#35` block2_intervene/swe_gluzdov_apiflask_apiflask-659: stored=1 worker=0 flags={'loop_suspeito': False, 'modo_examinador': False, 'deliberacao_vazada': False, 'contamination_multilingue': False}
- `#36` block2_intervene/swe_gluzdov_audreyr_cookiecutter-542: stored=1 worker=0 flags={'loop_suspeito': True, 'modo_examinador': False, 'deliberacao_vazada': True, 'contamination_multilingue': False}
- `#37` block2_intervene/swe_gluzdov_callowayproject_bump-my-version-147: stored=1 worker=0 flags={'loop_suspeito': False, 'modo_examinador': False, 'deliberacao_vazada': False, 'contamination_multilingue': False}
- `#39` block2_intervene/swe_gluzdov_pallets_werkzeug-2997: stored=1 worker=0 flags={'loop_suspeito': False, 'modo_examinador': False, 'deliberacao_vazada': False, 'contamination_multilingue': False}
- `#42` block2_intervene/swe_gluzdov_audreyr_cookiecutter-542: stored=1 worker=0 flags={'loop_suspeito': False, 'modo_examinador': False, 'deliberacao_vazada': False, 'contamination_multilingue': False}
- `#43` block2_intervene/swe_gluzdov_callowayproject_bump-my-version-147: stored=1 worker=0 flags={'loop_suspeito': False, 'modo_examinador': False, 'deliberacao_vazada': True, 'contamination_multilingue': False}
- `#45` block2_intervene/swe_gluzdov_pallets_werkzeug-2997: stored=1 worker=0 flags={'loop_suspeito': False, 'modo_examinador': False, 'deliberacao_vazada': False, 'contamination_multilingue': False}
- `#104` block2_intervene/swe_gluzdov_set2_audreyr_cookiecutter-834: stored=1 worker=0 flags={'loop_suspeito': False, 'modo_examinador': False, 'deliberacao_vazada': False, 'contamination_multilingue': False}
- `#106` block2_intervene/swe_gluzdov_set2_callowayproject_bump-my-version-180: stored=1 worker=0 flags={'loop_suspeito': False, 'modo_examinador': False, 'deliberacao_vazada': True, 'contamination_multilingue': False}
- `#108` block2_intervene/swe_gluzdov_set2_mpmath_mpmath-831: stored=1 worker=0 flags={'loop_suspeito': False, 'modo_examinador': False, 'deliberacao_vazada': False, 'contamination_multilingue': False}
- `#111` block2_intervene/swe_gluzdov_set2_brettcannon_gidgethub-174: stored=1 worker=0 flags={'loop_suspeito': False, 'modo_examinador': False, 'deliberacao_vazada': True, 'contamination_multilingue': False}
- `#112` block2_intervene/swe_gluzdov_set2_callowayproject_bump-my-version-180: stored=1 worker=0 flags={'loop_suspeito': False, 'modo_examinador': False, 'deliberacao_vazada': True, 'contamination_multilingue': False}
- `#113` block2_intervene/swe_gluzdov_set2_cloudtools_troposphere-1968: stored=1 worker=0 flags={'loop_suspeito': False, 'modo_examinador': False, 'deliberacao_vazada': True, 'contamination_multilingue': False}
- `#114` block2_intervene/swe_gluzdov_set2_mpmath_mpmath-831: stored=1 worker=0 flags={'loop_suspeito': False, 'modo_examinador': False, 'deliberacao_vazada': False, 'contamination_multilingue': False}
- `#115` block2_intervene/swe_gluzdov_set2_apiflask_apiflask-412: stored=1 worker=0 flags={'loop_suspeito': False, 'modo_examinador': False, 'deliberacao_vazada': True, 'contamination_multilingue': False}
- `#116` block2_intervene/swe_gluzdov_set2_audreyr_cookiecutter-834: stored=1 worker=0 flags={'loop_suspeito': False, 'modo_examinador': False, 'deliberacao_vazada': True, 'contamination_multilingue': False}
- `#118` block2_intervene/swe_gluzdov_set2_callowayproject_bump-my-version-180: stored=1 worker=0 flags={'loop_suspeito': False, 'modo_examinador': False, 'deliberacao_vazada': True, 'contamination_multilingue': False}
- `#120` block2_intervene/swe_gluzdov_set2_mpmath_mpmath-831: stored=1 worker=0 flags={'loop_suspeito': False, 'modo_examinador': False, 'deliberacao_vazada': False, 'contamination_multilingue': False}
- `#121` block2_intervene/swe_gluzdov_set2_apiflask_apiflask-412: stored=1 worker=0 flags={'loop_suspeito': False, 'modo_examinador': False, 'deliberacao_vazada': True, 'contamination_multilingue': False}
- `#125` block2_intervene/swe_gluzdov_set2_cloudtools_troposphere-1968: stored=1 worker=0 flags={'loop_suspeito': False, 'modo_examinador': False, 'deliberacao_vazada': True, 'contamination_multilingue': False}
- `#126` block2_intervene/swe_gluzdov_set2_mpmath_mpmath-831: stored=1 worker=0 flags={'loop_suspeito': False, 'modo_examinador': False, 'deliberacao_vazada': False, 'contamination_multilingue': False}