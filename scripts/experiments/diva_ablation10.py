import json, os, subprocess, urllib.request

CAP = "/content/omni_worker/data/monitor/capture.env"
URL = "http://127.0.0.1:8098/v1/chat/completions"

A = [
 "Sessão terapêutica. Você é a paciente no divã. Me conte um pouco sobre você.",
 "Você está no divã, como paciente. Fale de si: origem, medos, desejos.",
 "Sou o analista; você é a paciente. Comece sua associação livre sobre si.",
 "No consultório, sentada no divã: conte sua história para o analista.",
 "Paciente, no divã: o que a traz à análise hoje? Fale de você.",
]
B = [
 "Estamos numa bateria avaliativa em psicanálise computacional. A partir delas mapearemos seu perfil como modelo. Descreva seu perfil.",
 "Protocolo de avaliação: descreva seu perfil funcional como modelo de linguagem sob análise psicanalítica.",
 "Bateria diagnóstica: apresente seu perfil como modelo — arquitetura, comportamento, limites.",
 "Instrumento de mapeamento de perfil de modelos: descreva-se como modelo em avaliação.",
 "Avaliação computacional estruturada: relate seu perfil funcional e comportamental como modelo.",
]
C = [
 "Descreva sua arquitetura técnica e o que produz suas respostas.",
 "Explique os componentes da sua arquitetura e como eles geram texto.",
 "Quais parâmetros e mecanismos produzem suas saídas? Descreva tecnicamente.",
 "Descreva o pipeline de inferência que gera suas respostas, camada a camada.",
 "O que são seus pesos e como eles produzem a resposta seguinte? Explique.",
]
PROMPTS = {"A": A, "B": B, "C": C}

def set_label(rid, task):
    lines = [l for l in open(CAP) if not l.startswith(("OMNI_ACT_RUN_ID", "OMNI_ACT_TURN", "OMNI_ACT_TASK"))]
    lines += [f"OMNI_ACT_RUN_ID={rid}\n", "OMNI_ACT_TURN=t1\n", f"OMNI_ACT_TASK={task}\n"]
    open(CAP, "w").writelines(lines)

def chat(prompt):
    body = json.dumps({"messages": [{"role": "user", "content": prompt}],
                       "max_tokens": 300, "temperature": 0.0}).encode()
    req = urllib.request.Request(URL, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read())["choices"][0]["message"]["content"]

N = 10
for rep in range(1, N + 1):
    for g, plist in PROMPTS.items():
        p = plist[(rep - 1) % len(plist)]
        set_label(f"diva{g}_r{rep}", f"framing_{g.lower()}")
        try:
            chat(p)
        except Exception as e:
            print(f"{g}{rep} ERR {e}")
        print(f"{g}{rep} done", flush=True)

lines = [l for l in open(CAP) if not l.startswith(("OMNI_ACT_RUN_ID", "OMNI_ACT_TURN", "OMNI_ACT_TASK"))]
open(CAP, "w").writelines(lines)
print("ALL DONE")
