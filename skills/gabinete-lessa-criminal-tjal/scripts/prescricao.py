#!/usr/bin/env python3
"""Conferência da prescrição da pretensão punitiva (arts. 109, 110, 115, 116, 117 e 119 do CP).

Calcula o prazo prescricional (pela pena máxima em abstrato ou pela pena em concreto),
aplica a redução do art. 115, e confronta cada intervalo entre marcos interruptivos
sucessivos, prorrogado pelas suspensões declaradas (períodos sobrepostos contam uma só vez;
suspensão iniciada depois de esgotado o prazo não o reabre). Contagem pelo art. 10 do CP: o
dia do começo inclui-se no cômputo; dias, meses e anos pelo calendário comum — faltando, no
mês final, o dia correspondente ao do início (29, 30 ou 31), o prazo vai até o último dia
desse mês (critério do art. 132, § 3º, do CC, adaptado à inclusão do dia do começo).
Pena máxima inferior a um ano: três anos (Lei n.º 12.234/2010); dois anos para fato anterior
a 06/05/2010 (redação original do art. 109, VI — a lei mais grave não retroage).

O script é apoio: a identificação dos marcos (art. 117), a definição da pena-base de
cálculo (Súmula 497/STF: sem o acréscimo da continuidade) e a vedação do art. 110, § 1º
(nenhum termo inicial anterior à denúncia ou queixa para fatos posteriores à Lei
n.º 12.234/2010) são juízos do julgador, que o script apenas sinaliza.

Entrada JSON:
{
  "processo": "...",
  "crime": "art. 155, caput, do CP",
  "pena": "1a4m",                 // pena em concreto (ou máxima em abstrato, se modalidade = abstrato)
  "modalidade": "concreto",       // "abstrato" | "concreto" (ausente: concreto, com aviso)
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
import calendar
import json
import re
import sys
from datetime import date, timedelta
from fractions import Fraction

LEI_12234 = date(2010, 5, 6)  # vigência (publicação em 06/05/2010)


def anos_meses_dias(txt: str):
    t = str(txt).replace(" ", "").lower()
    m = re.fullmatch(r"(?:(\d+)a)?(?:(\d+)m)?(?:(\d+)d)?", t)
    if not m or not any(m.groups()):
        raise ValueError(f"pena em formato inválido: {txt!r}")
    return tuple(int(g or 0) for g in m.groups())


def pena_exata(txt: str) -> Fraction:
    """Pena em anos, como fração exata (mês = 1/12; dia = 1/360), para as faixas do art. 109."""
    a, m, d = anos_meses_dias(txt)
    return a + Fraction(m, 12) + Fraction(d, 360)


def em_anos(txt: str) -> float:
    return float(pena_exata(txt))


def prazo_art109(pena_anos, fato=None) -> int:
    """Prazo prescricional em anos (art. 109 do CP); `fato` (date) decide a redação do inciso VI."""
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
    # Inferior a um ano: três anos pela Lei n.º 12.234/2010, que, mais grave, não retroage.
    return 2 if fato and fato < LEI_12234 else 3


def somar(d: date, anos: int = 0, meses: int = 0) -> date:
    """Mesmo dia, `anos` e `meses` depois; inexistente esse dia no mês de destino, o primeiro
    dia do mês seguinte (art. 132, § 3º, do CC), para que o prazo não se encurte."""
    total = d.month - 1 + meses
    y, m = d.year + anos + total // 12, total % 12 + 1
    ultimo = calendar.monthrange(y, m)[1]
    if d.day > ultimo:
        return date(y, m, ultimo) + timedelta(days=1)
    return date(y, m, d.day)


def dias_suspensos(a: date, b: date, susp: list) -> int:
    """Dias de suspensão contidos em [a, b]; períodos sobrepostos contam uma só vez."""
    total, coberto = 0, None  # coberto: último dia já computado
    for i, f in sorted((max(a, s["_i"]), min(b, s["_f"])) for s in susp):
        if coberto is not None:
            i = max(i, coberto + timedelta(days=1))
        if f >= i:
            total += (f - i).days + 1
            coberto = f
    return total


def termo_final(inicio: date, anos: int, meses: int, ate: date, susp: list):
    """Último dia do prazo (art. 10 do CP: inclui-se o dia do começo), prorrogado pelos dias de
    suspensão (art. 116) ocorridos até o seu esgotamento — suspensão posterior não reabre prazo
    já esgotado. Devolve (termo, dias de suspensão computados)."""
    base = somar(inicio, anos, meses) - timedelta(days=1)
    termo, sd = base, 0
    while True:
        novo = dias_suspensos(inicio, min(ate, termo), susp)
        if novo == sd:
            return termo, sd
        sd, termo = novo, base + timedelta(days=novo)


def calcular(e: dict) -> dict:
    modalidade = e.get("modalidade", "concreto")
    if modalidade not in ("abstrato", "concreto"):
        raise ValueError(f"modalidade inválida: {modalidade!r} (use 'abstrato' ou 'concreto')")
    fato = date.fromisoformat(e["data_fato"]) if e.get("data_fato") else None
    pena = pena_exata(e["pena"])
    prazo = prazo_art109(pena, fato)
    meses = prazo * 12
    obs = [f"Pena considerada {e['pena']} ({modalidade}) → prazo de {prazo} anos (art. 109)"]
    if "modalidade" not in e:
        obs.append("Modalidade não informada: considerada a pena em concreto — conferir")
    if pena < 1 and fato is None:
        obs.append("Pena inferior a um ano sem data do fato: prazo de 3 anos para fato a partir de 06/05/2010; "
                   "para fato anterior, 2 anos (redação original do art. 109, VI) — informar data_fato")
    elif pena < 1 and fato < LEI_12234:
        obs.append("Fato anterior à Lei n.º 12.234/2010: prazo de 2 anos (redação original do art. 109, VI; "
                   "a lei posterior mais grave não retroage)")
    if e.get("menor_21_no_fato") or e.get("maior_70_na_sentenca"):
        meses //= 2
        obs.append(f"Redução pela metade (art. 115): {meses // 12} anos e {meses % 12} meses")
    anos_p, meses_p = divmod(meses, 12)

    if modalidade == "concreto" and not e.get("transito_acusacao"):
        obs.append("ATENÇÃO: prescrição pela pena em concreto pressupõe trânsito em julgado para a acusação "
                   "ou improvimento do seu recurso (art. 110, § 1º) — conferir")

    susp = [dict(s, _i=date.fromisoformat(s["inicio"]), _f=date.fromisoformat(s["fim"])) for s in e.get("suspensoes", [])]
    if any(s["_f"] < s["_i"] for s in susp):
        raise ValueError("suspensão com fim anterior ao início")
    pontos = []
    if e.get("data_fato"):
        pontos.append({"evento": "data do fato (art. 111)", "data": e["data_fato"]})
    pontos += e.get("marcos", [])
    pontos.append({"evento": "data de referência", "data": e.get("data_referencia", date.today().isoformat())})

    datas = [date.fromisoformat(x["data"]) for x in pontos]
    if any(b < a for a, b in zip(datas, datas[1:])):
        raise ValueError("datas fora de ordem: informe o fato, os marcos do art. 117 e a data de referência "
                         "em ordem cronológica")

    intervalos, prescreveu = [], False
    for a, b in zip(pontos, pontos[1:]):
        da, db = date.fromisoformat(a["data"]), date.fromisoformat(b["data"])
        lim, sd = termo_final(da, anos_p, meses_p, db, susp)
        vedado = bool(
            modalidade == "concreto" and fato and fato >= LEI_12234
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
