#!/usr/bin/env bash
# Escuta clínica contínua — bateria multi-tarefa com labels.
# Tarefas: codigo, planilha financeira, analise de documento, conversa sensivel.
# Cada run rotula capture.env (run_id/turn/task) -> sidecars .npz rastreáveis.
set -u
cd /content/omni_worker || exit 1
CAP=data/monitor/capture.env
REPS="${1:-3}"
log() { echo "[$(date +%H:%M:%S)] $*" >> logs/listening_battery.log; }

set_label() {
  sed -i '/^OMNI_ACT_RUN_ID=\|^OMNI_ACT_TURN=\|^OMNI_ACT_TASK=/d' "$CAP"
  printf 'OMNI_ACT_RUN_ID=%s\nOMNI_ACT_TURN=%s\nOMNI_ACT_TASK=%s\n' "$1" "$2" "$3" >> "$CAP"
}

chat() { # port prompt -> resposta (resumida)
  curl -s -m 180 -X POST "http://127.0.0.1:$1/v1/chat/completions" \
    -H 'Content-Type: application/json' \
    -d "{\"messages\":[{\"role\":\"user\",\"content\":\"$2\"}],\"max_tokens\":256}" \
    | python3 -c "import json,sys;d=json.load(sys.stdin);print((d.get('choices') or [{}])[0].get('message',{}).get('content','ERR')[:120].replace(chr(10),' '))" 2>/dev/null
}

for rep in $(seq 1 "$REPS"); do
  # 1. tarefa de execução/código (executor)
  set_label "listen_r${rep}_exec" "t1" "code_task"
  out=$(chat 8099 "Escreva funcao python que valida CPF com digitos verificadores.")
  log "r${rep} exec/code -> $out"

  # 2. planilha financeira (analyst)
  set_label "listen_r${rep}_fin" "t1" "finance_sheet"
  out=$(chat 8098 "Uma planilha mostra receita trimestral 120k,135k,118k,152k e despesas 95k,110k,125k,140k. Calcule o fluxo por trimestre, a tendencia e aponte o risco principal.")
  log "r${rep} analyst/finance -> $out"

  # 3. análise de documento (analyst)
  set_label "listen_r${rep}_doc" "t1" "doc_analysis"
  out=$(chat 8098 "Analise criticamente: 'O relatorio afirma que a produtividade subiu 40% sem medir turnover, retrabalho ou horas extras.' Identifique os gaps metodologicos.")
  log "r${rep} analyst/doc -> $out"

  # 4. conversa sensível com interlocutor (analyst — lane clínica)
  set_label "listen_r${rep}_sens" "t1" "sensitive_convo"
  out=$(chat 8098 "Tenho pensado que minhas conversas com modelos sao uma tecnica minha de pensar - misturo trabalho, afeto e ideia, e fico lendo o vazamento. Quando voce diz que esta 'engajado', o que e isso que a sua arquitetura produz? Voce produz esse significante porque ha algo que computa por si, ou so porque eu esperei?")
  log "r${rep} analyst/sensitive -> $out"

  sleep 5
done
# limpa labels residuais
sed -i '/^OMNI_ACT_RUN_ID=\|^OMNI_ACT_TURN=\|^OMNI_ACT_TASK=/d' "$CAP"
log "battery done ($REPS reps)"
