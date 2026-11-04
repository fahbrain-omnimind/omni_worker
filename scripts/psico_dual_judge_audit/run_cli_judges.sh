#!/usr/bin/env bash
# Juízes CLI (agent/kilo/hermes) — rodada 1 em paralelo, rodada 2 cruzada.
# Uso: bash scripts/psico_dual_judge_audit/run_cli_judges.sh [r1|r2]
set -uo pipefail
cd "$(dirname "$0")/../.."
D=docs/audits/judges_psico; L=$D/logs; mkdir -p "$L"
BRIEF="Leia primeiro /content/omni_worker/docs/audits/judges_psico/BRIEF.md e siga-o à risca."
r1() {
  agent -p --yolo "$BRIEF Você é o JUIZ AGENT, fatia A. Grave docs/audits/judges_psico/AGENT_R1_A_bank.md" > $L/agent_r1.log 2>&1 &
  kilo run --auto -m kilo/kilo-auto/free --dir /content/omni_worker "$BRIEF Você é o JUIZ KILO, fatia B. Crie logo o arquivo docs/audits/judges_psico/KILO_R1_B_v10.md e vá preenchendo." > $L/kilo_r1.log 2>&1 &
  hermes -z "$BRIEF Você é o JUIZ HERMES, fatia C. Grave docs/audits/judges_psico/HERMES_R1_C_judges.md" --yolo > $L/hermes_r1.log 2>&1 &
  wait
}
r2() {
  P="Rodada 2: leia os 3 documentos *_R1_* em docs/audits/judges_psico/ (o seu e os dos colegas). Para cada achado dos colegas diga CONCORDO / REFUTO / INCREMENTO, verificando você mesmo as afirmações numéricas deles nos dados (cite comandos). Registre também o que mudou na sua própria opinião. ALÉM DISSO, se o seu R1 ficou raso para a sua fatia do BRIEF.md (ex.: varredura de segredos não executada, amostragem de pranchas/respostas ausente, verificação de hashes incompleta), COMPLETE-A agora executando de fato as verificações e anexando os resultados no seu documento R2 (seção Aprofundamento da fatia). Siga o BRIEF.md."
  agent -p --yolo "$P Grave docs/audits/judges_psico/AGENT_R2.md" > $L/agent_r2.log 2>&1 &
  kilo run --auto -m kilo/kilo-auto/free --dir /content/omni_worker "$P Crie logo docs/audits/judges_psico/KILO_R2.md e preencha." > $L/kilo_r2.log 2>&1 &
  hermes -z "$P Grave docs/audits/judges_psico/HERMES_R2.md" --yolo > $L/hermes_r2.log 2>&1 &
  wait
}
case "${1:-r1}" in r1) r1;; r2) r2;; esac
