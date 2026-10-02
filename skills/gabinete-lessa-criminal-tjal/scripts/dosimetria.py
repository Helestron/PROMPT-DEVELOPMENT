#!/usr/bin/env python3
"""Conferência aritmética da dosimetria trifásica (arts. 59 e 68 do CP).

O script NÃO escolhe frações nem valora circunstâncias: reproduz, com exatidão, a conta que
a sentença ou o voto afirma ter feito, a partir dos critérios declarados no texto, e acusa
divergências. A escolha e a fundamentação dos critérios são do julgador.

Entrada: JSON (arquivo ou stdin) no formato abaixo. Penas em dias (1 ano = 360 dias e
1 mês = 30 dias, convenção da prática forense). As frações de dia são desprezadas (art. 11 do
CP) ao fim de cada etapa — pena-base, cada incidência da 2ª fase e cada causa da 3ª fase —,
como a decisão faz ao exprimir cada pena intermediária em dias; o mesmo vale para a multa.
Na 3ª fase, "tipo" é "aumento" ou "diminuicao"; a fração de diminuição é menor que 1.

{
  "processo": "0000000-00.0000.8.02.0000",
  "reu": "J. S.",
  "crime": "art. 33, caput, da Lei n.º 11.343/2006",
  "culposo": false,
  "pena_min": "5a", "pena_max": "15a",
  "multa_min": 500, "multa_max": 1500,
  "fase1": {"criterio": "1/8_intervalo" | "1/6_minimo" | "fixo",
            "desfavoraveis": 2, "acrescimo_fixo": "0a"},
  "fase2": {"agravantes": 1, "atenuantes": 0, "fracao": "1/6",
            "modo": "sucessivo" | "somado", "sumula231": true},
  "fase3": [{"tipo": "diminuicao", "fracao": "2/3", "fundamento": "art. 33, § 4º"},
            {"tipo": "aumento", "fracao": "1/6", "fundamento": "art. 40, VI"}],
  "afirmado": {"pena_final": "1a8m", "multa_final": 166},
  "reincidente": false,
  "circunstancias_favoraveis": true
}

Saída: memória de cálculo passo a passo + conclusão (CONFERE / DIVERGE) + sugestão do
quadro legal do regime (art. 33, § 2º, do CP) e da substituição (art. 44 do CP),
sempre como apoio, nunca como decisão.
"""
import json
import re
import sys
from fractions import Fraction

ANO, MES = 360, 30


def dias(txt) -> Fraction:
    """'5a', '1a8m', '2a3m10d', '45d' ou número de dias -> Fraction de dias."""
    if isinstance(txt, (int, float)):
        return Fraction(txt)
    t = str(txt).replace(" ", "").lower()
    if not t or t == "0":
        return Fraction(0)
    m = re.fullmatch(r"(?:(\d+)a)?(?:(\d+)m)?(?:(\d+)d)?", t)
    if not m or not any(m.groups()):
        raise ValueError(f"pena em formato inválido: {txt!r} (use 5a, 1a8m, 2a3m10d)")
    a, me, d = (int(g or 0) for g in m.groups())
    return Fraction(a * ANO + me * MES + d)


def fmt(q: Fraction) -> str:
    total = int(q)  # art. 11 do CP: desprezam-se as frações de dia
    a, r = divmod(total, ANO)
    me, d = divmod(r, MES)
    partes = []
    if a:
        partes.append(f"{a} ano{'s' if a > 1 else ''}")
    if me:
        partes.append(f"{me} {'meses' if me > 1 else 'mês'}")
    if d:
        partes.append(f"{d} dia{'s' if d > 1 else ''}")
    return " e ".join([", ".join(partes[:-1]), partes[-1]] if len(partes) > 1 else partes) or "0 dia"


def fr(txt) -> Fraction:
    return Fraction(str(txt))


def inteiro(q: Fraction) -> Fraction:
    """Despreza a fração de dia (art. 11 do CP) ou de dia-multa."""
    return Fraction(int(q))


def causa_fase3(c: dict):
    """Valida a causa da 3ª fase e devolve (tipo normalizado, fração)."""
    tipo = str(c.get("tipo", "")).strip().lower().replace("ç", "c").replace("ã", "a")
    if tipo not in ("aumento", "diminuicao"):
        raise ValueError(f"tipo da 3ª fase inválido: {c.get('tipo')!r} (use 'aumento' ou 'diminuicao')")
    f = fr(c["fracao"])
    if f <= 0 or (tipo == "diminuicao" and f >= 1):
        raise ValueError(f"fração inválida para {tipo}: {c['fracao']} (diminuição exige 0 < fração < 1)")
    return tipo, f


def calcular(e: dict) -> dict:
    memoria = []
    pmin, pmax = dias(e["pena_min"]), dias(e["pena_max"])
    intervalo = pmax - pmin

    # 1ª fase — art. 59
    f1 = e.get("fase1", {})
    n = int(f1.get("desfavoraveis", 0))
    crit = f1.get("criterio", "1/8_intervalo")
    if crit == "1/8_intervalo":
        passo = intervalo / 8
        desc = f"1/8 do intervalo ({fmt(intervalo)}) = {fmt(passo)} por circunstância"
    elif crit == "1/6_minimo":
        passo = pmin / 6
        desc = f"1/6 da mínima = {fmt(passo)} por circunstância"
    elif crit == "fixo":
        passo = dias(f1.get("acrescimo_fixo", 0))
        desc = f"acréscimo fixo declarado de {fmt(passo)} por circunstância"
    else:
        raise ValueError(f"critério da 1ª fase desconhecido: {crit}")
    base = inteiro(min(pmin + passo * n, pmax))
    memoria.append(f"1ª fase: mínima {fmt(pmin)}; {n} circunstância(s) desfavorável(is); {desc}; pena-base {fmt(base)}")

    # 2ª fase — arts. 61 a 66 (compensação simples: diferença entre agravantes e atenuantes).
    # "sucessivo": cada fração incide sobre a pena já ajustada; "somado": as frações se somam e
    # incidem uma vez sobre a pena-base. Use o modo que a decisão declarar.
    f2 = e.get("fase2", {})
    ag, at = int(f2.get("agravantes", 0)), int(f2.get("atenuantes", 0))
    fr2 = fr(f2.get("fracao", "1/6"))
    modo = f2.get("modo", "sucessivo")
    if modo not in ("sucessivo", "somado"):
        raise ValueError(f"modo da 2ª fase desconhecido: {modo!r} (use sucessivo ou somado)")
    saldo = ag - at

    def segunda_fase(valor):
        if modo == "somado":
            return inteiro(valor * (1 + fr2 * saldo))
        fator = 1 + fr2 if saldo >= 0 else 1 - fr2
        for _ in range(abs(saldo)):
            valor = inteiro(valor * fator)
        return valor

    inter = segunda_fase(base)
    nota = ""
    if f2.get("sumula231", True) and inter < pmin:
        inter, nota = pmin, " (limitada ao mínimo legal — Súmula 231/STJ, conferir vigência)"
    if inter > pmax:
        inter, nota = pmax, " (limitada ao máximo legal)"
    memoria.append(f"2ª fase: {ag} agravante(s), {at} atenuante(s), fração {fr2} por unidade de saldo "
                   f"(modo {modo}); pena intermediária {fmt(inter)}{nota}")

    # 3ª fase — causas de aumento e diminuição, em cascata (art. 68 do CP)
    pena = inter
    causas = [causa_fase3(c) for c in e.get("fase3", [])]
    for c, (tipo, f) in zip(e.get("fase3", []), causas):
        antes = pena
        pena = inteiro(pena * (1 + f) if tipo == "aumento" else pena * (1 - f))
        memoria.append(f"3ª fase: {tipo} de {f} ({c.get('fundamento', 's/ fundamento')}) sobre {fmt(antes)} = {fmt(pena)}")
    memoria.append(f"Pena definitiva calculada: {fmt(pena)}")

    # Multa — proporcional à privativa: a pena-base ocupa no intervalo de dias-multa a mesma
    # posição relativa que ocupa no intervalo da privativa; 2ª e 3ª fases pelas mesmas frações.
    r = {"memoria": memoria, "pena_final_dias": int(pena), "pena_final": fmt(pena)}
    if "multa_min" in e or "multa_max" in e:
        if "multa_min" not in e or "multa_max" not in e:
            raise ValueError("informe multa_min e multa_max (ou nenhum dos dois)")
        mmin, mmax = Fraction(e["multa_min"]), Fraction(e["multa_max"])
        posicao = (base - pmin) / intervalo if intervalo else Fraction(0)
        mb = inteiro(mmin + (mmax - mmin) * posicao)
        mi = segunda_fase(mb)
        if f2.get("sumula231", True):
            mi = max(mi, mmin)
        mi = min(mi, mmax)
        mf = mi
        for tipo, f in causas:
            mf = inteiro(mf * (1 + f) if tipo == "aumento" else mf * (1 - f))
        r["multa_final"] = int(mf)
        memoria.append(f"Multa proporcional: base {int(mb)}, intermediária {int(mi)}, definitiva {int(mf)} dias-multa")

    # Conferência com o afirmado na decisão
    af = e.get("afirmado", {})
    diverg = []
    if "pena_final" in af and int(dias(af["pena_final"])) != int(pena):
        diverg.append(f"pena afirmada {fmt(dias(af['pena_final']))} ≠ calculada {fmt(pena)}")
    if "multa_final" in af and "multa_final" in r and int(af["multa_final"]) != r["multa_final"]:
        diverg.append(f"multa afirmada {af['multa_final']} ≠ calculada {r['multa_final']}")
    r["conclusao"] = "DIVERGE" if diverg else ("CONFERE" if af else "SEM_AFIRMADO")
    r["divergencias"] = diverg

    # Quadro legal de apoio (não decide): regime (art. 33, § 2º) e substituição (art. 44)
    anos = Fraction(int(pena), ANO)
    reinc = bool(e.get("reincidente", False))
    if anos > 8:
        regime = "fechado (art. 33, § 2º, a)"
    elif anos > 4:
        regime = "fechado (reincidente)" if reinc else "semiaberto (art. 33, § 2º, b)"
    else:
        regime = "semiaberto ou fechado (reincidente — ver Súmula 269/STJ)" if reinc else "aberto (art. 33, § 2º, c)"
    if not e.get("circunstancias_favoraveis", True):
        regime += "; circunstâncias judiciais desfavoráveis podem justificar regime mais gravoso (art. 33, § 3º) — fundamentar"
    r["quadro_regime"] = regime
    if e.get("culposo"):
        r["quadro_art44"] = ("crime culposo: substituição cabível qualquer que seja a pena (art. 44, I) — "
                             "conferir art. 44, II e III")
    elif anos <= 4:
        r["quadro_art44"] = ("quantum compatível com substituição (≤ 4 anos) — conferir violência ou grave "
                             "ameaça, reincidência e art. 44, III")
    else:
        r["quadro_art44"] = "quantum superior a 4 anos — substituição incabível em crime doloso (art. 44, I)"
    r["aviso"] = "Apoio aritmético. Frações, valoração e regime exigem fundamentação concreta do julgador."
    return r


def main(argv):
    src = open(argv[0], encoding="utf-8") if argv and argv[0] != "-" else sys.stdin
    entrada = json.load(src)
    lote = entrada if isinstance(entrada, list) else [entrada]
    saida = [dict(processo=e.get("processo"), reu=e.get("reu"), crime=e.get("crime"), **calcular(e)) for e in lote]
    print(json.dumps(saida if isinstance(entrada, list) else saida[0], ensure_ascii=False, indent=2))
    return 1 if any(s["conclusao"] == "DIVERGE" for s in saida) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
