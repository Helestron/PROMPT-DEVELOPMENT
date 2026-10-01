#!/usr/bin/env python3
"""Conferência da prescrição da pretensão punitiva (arts. 109, 110, 115, 116, 117 e 119 do CP).

Calcula o prazo prescricional (pela pena máxima em abstrato ou pela pena em concreto),
aplica a redução do art. 115, e confronta cada intervalo entre marcos interruptivos
sucessivos, descontadas as suspensões declaradas. Contagem pelo art. 10 do CP: o dia do
começo inclui-se no cômputo; dias, meses e anos pelo calendário comum.

O script é apoio: a identificação dos marcos (art. 117), a definição da pena-base de
cálculo (Súmula 497/STF: sem o acréscimo da continuidade) e a vedação do art. 110, § 1º
(nenhum termo inicial anterior à denúncia ou queixa para fatos posteriores à Lei
n.º 12.234/2010) são juízos do julgador, que o script apenas sinaliza.

Entrada JSON:
{
  "processo": "...",
  "crime": "art. 155, caput, do CP",
  "pena": "1a4m",                 // pena em concreto (ou máxima em abstrato, se modalidade = abstrato)
  "modalidade": "concreto",       // "abstrato" | "concreto"
  "transito_acusacao": true,      // necessário para a retroativa/intercorrente pela pena em concreto
  "menor_21_no_fato": false, "maior_70_na_sentenca": false,
  "data_fato": "2019-03-10",
  "marcos": [                      // em ordem cronológica (art. 117)
     {"evento": "recebimento da denúncia", "data": "2019-08-01"},
     {"evento": "publicação da sentença condenatória", "data": "2023-02-15"}
  ],
  "suspensoes": [{"inicio": "2020-01-01", "fim": "2020-06-30", "fundamento": "art. 366 do CPP"}],
  "data_referencia": "2026-10-01"  // hoje, ou data do julgamento pretendido
}
"""
import json
import re
import sys
from datetime import date, timedelta

LEI_12234 = date(2010, 5, 6)  # vigência (publicação em 06/05/2010)


def anos_meses_dias(txt: str):
    t = str(txt).replace(" ", "").lower()
    m = re.fullmatch(r"(?:(\d+)a)?(?:(\d+)m)?(?:(\d+)d)?", t)
    if not m or not any(m.groups()):
        raise ValueError(f"pena em formato inválido: {txt!r}")
    return tuple(int(g or 0) for g in m.groups())


def em_anos(txt: str) -> float:
    a, m, d = anos_meses_dias(txt)
    return a + m / 12 + d / 360


def prazo_art109(pena_anos: float) -> int:
    """Prazo prescricional em anos (art. 109 do CP)."""
    if pena_anos > 12:
        return 20
    if pena_anos > 8:
        return 16
    if pena_anos > 4:
        return 12
    if pena_anos > 2:
        return 8
    if pena_anos >= 1:
        return 4
    return 3  # inferior a 1 ano (redação da Lei n.º 12.234/2010)


def somar(d: date, anos: int = 0, meses: int = 0) -> date:
    total = d.month - 1 + meses
    y, m = d.year + anos + total // 12, total % 12 + 1
    ultimo = [31, 29 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 28,
              31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
    return date(y, m, min(d.day, ultimo))


def limite(inicio: date, anos: int, meses: int, suspenso: int) -> date:
    """Último dia do prazo (art. 10 do CP: inclui-se o dia do começo) + dias de suspensão."""
    return somar(inicio, anos, meses) - timedelta(days=1) + timedelta(days=suspenso)


def dias_suspensos(a: date, b: date, susp: list) -> int:
    total = 0
    for s in susp:
        i, f = max(a, s["_i"]), min(b, s["_f"])
        if f >= i:
            total += (f - i).days + 1
    return total


def calcular(e: dict) -> dict:
    pena_anos = em_anos(e["pena"])
    prazo = prazo_art109(pena_anos)
    meses = prazo * 12
    obs = [f"Pena considerada {e['pena']} ({e.get('modalidade', 'concreto')}) → prazo de {prazo} anos (art. 109)"]
    if e.get("menor_21_no_fato") or e.get("maior_70_na_sentenca"):
        meses //= 2
        obs.append(f"Redução pela metade (art. 115): {meses // 12} anos e {meses % 12} meses")
    anos_p, meses_p = divmod(meses, 12)

    if e.get("modalidade") == "concreto" and not e.get("transito_acusacao"):
        obs.append("ATENÇÃO: prescrição pela pena em concreto pressupõe trânsito em julgado para a acusação "
                   "ou improvimento do seu recurso (art. 110, § 1º) — conferir")

    susp = [dict(s, _i=date.fromisoformat(s["inicio"]), _f=date.fromisoformat(s["fim"])) for s in e.get("suspensoes", [])]
    pontos = []
    if e.get("data_fato"):
        pontos.append({"evento": "data do fato (art. 111)", "data": e["data_fato"]})
    pontos += e.get("marcos", [])
    pontos.append({"evento": "data de referência", "data": e.get("data_referencia", date.today().isoformat())})

    intervalos, prescreveu = [], False
    fato = date.fromisoformat(e["data_fato"]) if e.get("data_fato") else None
    for a, b in zip(pontos, pontos[1:]):
        da, db = date.fromisoformat(a["data"]), date.fromisoformat(b["data"])
        sd = dias_suspensos(da, db, susp)
        lim = limite(da, anos_p, meses_p, sd)
        vedado = (
            e.get("modalidade") == "concreto" and fato and fato >= LEI_12234
            and a["evento"].startswith("data do fato")
        )
        consumada = db > lim and not vedado
        prescreveu |= consumada
        intervalos.append({
            "de": f"{a['evento']} ({da.isoformat()})",
            "ate": f"{b['evento']} ({db.isoformat()})",
            "dias_suspensos": sd,
            "termo_final_prazo": lim.isoformat(),
            "consumada": consumada,
            "observacao": ("intervalo inaplicável à pena em concreto: fato posterior à Lei n.º 12.234/2010 "
                           "(art. 110, § 1º)") if vedado else "",
        })
    return {
        "processo": e.get("processo"),
        "crime": e.get("crime"),
        "prazo_anos": anos_p, "prazo_meses_adicionais": meses_p,
        "observacoes": obs,
        "intervalos": intervalos,
        "conclusao": "PRESCRICAO_CONSUMADA" if prescreveu else "NAO_CONSUMADA",
        "aviso": "Apoio aritmético. Marcos, pena de cálculo e incidência de causas suspensivas são juízo do julgador "
                 "(matéria de ordem pública — art. 61 do CPP).",
    }


def main(argv):
    src = open(argv[0], encoding="utf-8") if argv and argv[0] != "-" else sys.stdin
    entrada = json.load(src)
    lote = entrada if isinstance(entrada, list) else [entrada]
    saida = [calcular(e) for e in lote]
    print(json.dumps(saida if isinstance(entrada, list) else saida[0], ensure_ascii=False, indent=2))
    return 1 if any(s["conclusao"] == "PRESCRICAO_CONSUMADA" for s in saida) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
