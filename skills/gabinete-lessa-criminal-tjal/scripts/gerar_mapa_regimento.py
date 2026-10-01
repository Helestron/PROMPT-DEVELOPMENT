#!/usr/bin/env python3
"""Regenera referencias/regimento_tjal.md a partir de referencias/ritjal_integral.txt.

Uso (após `extrair_regimento.py` sobre nova versão consolidada do Regimento):
    python gerar_mapa_regimento.py [saida.md]
Falha (AssertionError) se algum dispositivo do mapa deixar de ser localizado — sinal de que a
emenda alterou a numeração ou a redação e o mapa precisa de revisão manual.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import regimento as r  # noqa: E402
A = r.carregar()

def v(n):
    return r.vigente(A[n])[0]

def tr(n, ini=None, fim=None):
    t = v(n)
    i = 0
    if ini:
        m = re.search(ini, t)
        assert m, (n, ini)
        i = m.start()
    j = len(t)
    if fim:
        m = re.search(fim, t[i + 1:])
        assert m, (n, fim)
        j = i + 1 + m.start()
    return t[i:j].strip().rstrip(';').strip()

def bloco(rotulo, texto, uso=None):
    s = f"**{rotulo}**\n\n> {texto}\n"
    if uso:
        s += f"\n*Uso no gabinete:* {uso}\n"
    return s + "\n"

S = []
S.append("""# Regimento Interno do TJAL — mapa de uso do gabinete

**Estado: PREENCHIDO** a partir do PDF consolidado fornecido pelo gabinete em 01/10/2026:
Regimento aprovado pelo Pleno em 20/08/2024, com as Emendas n.º 17 (19/08/2025), 18 (27/01/2026)
e 19 (10/02/2026). O texto vigente (`referencias/ritjal_integral.txt`) foi extraído por
`scripts/extrair_regimento.py`, que **exclui o texto tachado (revogado)** no PDF — guardado à parte
em `referencias/ritjal_revogados.txt` — e preserva os hífens reais. As transcrições abaixo foram
**geradas automaticamente** a partir desse texto por `scripts/gerar_mapa_regimento.py`; as
anotações "(Incluído/Alterado pela Emenda …)" são do próprio PDF e não integram a citação; as
linhas "Uso no gabinete" são orientação do skill, não texto regimental.

Regras de uso: (1) o mapa orienta; o integral autoriza — antes de citar, rode
`python scripts/regimento.py <artigo>` e registre no ledger com `tipo: "regimento"`; (2) nova
emenda regimental → `python scripts/extrair_regimento.py <PDF consolidado>`, depois
`python scripts/gerar_mapa_regimento.py`, e reconferir as entradas do ledger; (3) casos omissos:
RISTF e RISTJ, nessa ordem (art. 392); (4) divergência de interpretação regimental ou ausência
de previsão interna: pronunciamento prévio do Pleno, pedido antes do voto (art. 389).
""")

S.append("## 1. Competência\n")
S.append(bloco("Art. 2º (estrutura)", tr(2), "uma única Câmara Criminal no Tribunal."))
S.append(bloco("Art. 48 (Câmara Criminal)", v(48),
  "classes do gabinete na Câmara: recursos criminais e do Júri (II); HC quando o **coator** for uma das autoridades do art. 43, IX, f — v.g., juiz de direito —, ou quando houver iminente perigo de consumar-se a violência (III); desaforamento (VI); recursos infracionais do ECA (VII); conflitos de competência criminais de 1º grau (VIII); Conselho de Justificação (I); extinção de medida de segurança (IV). HC por prisão civil é das Câmaras Cíveis (art. 47, IV)."))
S.append(bloco("Art. 43, IX, alíneas d, f, l, m e p (Pleno)",
  " … ".join([tr(43, r"d\) os conflitos de atribuição", r"e\) as ações de Reclamação"),
              tr(43, r"f\) os habeas corpus", r"g\) os habeas data"),
              tr(43, r"l\) as revisões criminais", r"n\) os pedidos de revisão"),
              tr(43, r"p\) os agravos dos atos", r"q\) os procedimentos")]),
  "revisão criminal e embargos infringentes contra decisões da Câmara Criminal são julgados pelo Pleno; HC cujo **paciente** seja uma das autoridades da alínea f é do Pleno (se a autoridade for o coator, o HC é da Câmara — art. 48, III) — conferir antes de minutar."))
S.append(bloco("Art. 114 (mandado de segurança criminal)", tr(114)))
S.append(bloco("Art. 242 (correição parcial)", tr(242)))
S.append(bloco("Art. 321 (RESE)", tr(321)))
S.append(bloco("Art. 222 (desaforamento)", tr(222)))

S.append("## 2. Relator — atribuições e poderes monocráticos\n")
S.append(bloco("Art. 61, incisos I, II, VIII, IX, XII, XIV, XV, XVI, XVII e XVIII",
  " … ".join([tr(61, r"I - ordenar", r"II - determinar"), tr(61, r"II - determinar", r"III - submeter"),
              tr(61, r"VIII - julgar", r"IX - processar"), tr(61, r"IX - processar", r"X - mandar"),
              tr(61, r"XII - conceder", r"XIII - determinar"), tr(61, r"XIV - pedir", r"XV - apresentar"),
              tr(61, r"XV - apresentar", r"XVI - determinar"), tr(61, r"XVI - determinar", r"XVII - lavrar"),
              tr(61, r"XVII - lavrar", r"XVIII"), tr(61, r"XVIII", r"XIX - homologar")]),
  "o inciso XVIII permite delegar ao Chefe de Gabinete atos de mero expediente; a assinatura continua sendo de pessoa, nunca da automação."))
S.append(bloco("Art. 62 (decisão monocrática)", v(62),
  "hipóteses da decisão monocrática em recurso; nas originárias (HC, MS, revisão criminal), só extinção sem mérito ou previsão legal específica (parágrafo único). Minuta monocrática fora dessas hipóteses → voto."))
S.append(bloco("Art. 63 (urgência, liminar e referendo na Câmara Criminal)", v(63),
  "toda decisão **concessiva** de urgência em feito da Câmara Criminal vai a referendo na primeira sessão subsequente à assinatura (§§ 3º e 4º); sem referendo, cessam os efeitos (§ 5º). Ao minutar liminar concessiva, minute também o voto de referendo (tipo `referendo`) e alerte o prazo."))
S.append(bloco("Art. 319 (alvará de soltura)", v(319)))
S.append(bloco("Art. 320 (recursos criminais)", v(320)))

S.append("## 3. Habeas corpus e demais originárias criminais\n")
for n in (189, 190, 191, 192, 193, 194):
    S.append(bloco(f"Art. {n}", v(n)))
S.append("*Uso no gabinete:* indeferimento liminar só nas hipóteses do art. 192, parágrafo único; HC prejudicado pela cessação da coação (art. 192, caput); oitiva da PGJ (art. 191 — “em dois dias”, prazo que admite leitura como da PGJ, em harmonia com o Decreto-Lei n.º 552/1969, ou do relator; conferir); agravo contra a liminar em quinze dias (art. 190); empate favorece o paciente (art. 193). O HC independe de pauta, salvo requerimento de inclusão (art. 121, VI).\n\n")
for n in (196, 199, 213, 216, 217, 218, 220, 221, 241, 243):
    S.append(bloco(f"Art. {n}", v(n)))

S.append("## 4. Recursos criminais\n")
for n in (323, 324, 325, 326, 322, 328, 329, 330, 331, 332):
    S.append(bloco(f"Art. {n}", v(n)))
S.append("*Uso no gabinete:* arts. 322 e 327 remetem ao Código de Normas da CGJ/AL (arts. 797 e 798 — RESE em sequencial vinculado ao processo principal; ver `referencias/cgj_normas_integral.txt`): no e-SAJ e no SG5, confira se o recurso tramita no principal ou em sequencial antes de baixar autos e de inserir minuta.\n\n")
for n in (333, 334, 335, 337, 338, 339):
    S.append(bloco(f"Art. {n}", v(n)))
S.append("*Uso no gabinete:* embargos de declaração independem de revisão e de pauta se julgados na sessão subsequente (art. 334); contra decisão monocrática, julga o próprio relator (art. 335). Embargos infringentes: admissibilidade pelo relator do acórdão embargado (art. 338), redistribuição a novo relator da Câmara Criminal (art. 339) e julgamento pelo Pleno (art. 43, IX, m) — registre a competência no voto.\n\n")

S.append("## 5. Revisor (demandas criminais)\n")
for n in (49, 50, 51, 159, 32, 36):
    S.append(bloco(f"Art. {n}", v(n)))
S.append(bloco("Art. 38, § 5º", tr(38, r"§5º")))
S.append(bloco("Art. 20, § 1º", tr(20, r"§1º", r"§2º")))
S.append(bloco("Art. 112", v(112)))
S.append("*Uso no gabinete:* quando o gabinete for revisor, o produto é o exame do relatório (confirmar, completar ou retificar), eventual sugestão de diligência e o pedido de dia (art. 49), em até dez dias (art. 50); o pedido de dia é operação de nível B. Revisor de juiz convocado: art. 38, § 5º.\n\n")

S.append("## 6. Prevenção, distribuição e impedimentos\n")
for n in (95, 103, 109, 110, 111):
    S.append(bloco(f"Art. {n}", v(n)))
S.append(bloco("Art. 99 (redação da Emenda n.º 19/2026)", v(99)))
for n in (245, 246, 247):
    S.append(bloco(f"Art. {n}", v(n)))
S.append("*Uso no gabinete:* indício de impedimento ou suspeição do Desembargador (inclusive art. 112 na revisão criminal) → minuta de despacho em vermelho na anotada e alerta imediato; a declaração é ato pessoal (nível C), e a remessa para redistribuição segue o art. 247.\n\n")

S.append("## 7. Prioridades, pauta e sessão\n")
for n in (74, 148, 149, 70, 120, 121, 123, 73):
    S.append(bloco(f"Art. {n}", v(n)))
S.append(bloco("Art. 128, VI", tr(128, r"VI - a Câmara Criminal", r"VII - a Seção")))
for n in (129, 141, 152):
    S.append(bloco(f"Art. {n}", v(n)))

S.append("## 8. Sustentação oral\n")
S.append(bloco("Art. 154, caput (hipóteses) e § 10", tr(154, None, r"§1º") + " … " + tr(154, r"§10\.", r"§11\.")))
for n in (155, 156):
    S.append(bloco(f"Art. {n}", v(n)))

S.append("## 9. Votação, questões novas, vista, voto vencido e acórdão\n")
for n in (158, 160, 161):
    S.append(bloco(f"Art. {n}", v(n)))
S.append(bloco("Art. 163, IV", tr(163, r"IV - em julgamento")))
for n in (164, 165, 166):
    S.append(bloco(f"Art. {n}", v(n)))
S.append(bloco("Art. 167, III e parágrafo único", tr(167, r"III - se mais")))
for n in (172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 184, 185, 186, 187):
    S.append(bloco(f"Art. {n}", v(n)))
S.append("*Uso no gabinete:* matéria surgida nos debates ou na vista sem prévia oportunidade de manifestação, ainda que cognoscível de ofício, leva à suspensão e à manifestação das partes em cinco dias, salvo manifestação na própria sessão (art. 161, caput e §§ 3º e 5º); antes da sessão, o contraditório prévio vem do art. 10 do CPC, por analogia — a minuta marca o ponto em vermelho e propõe o caminho; voto-vista sempre escrito (art. 174), em dez dias prorrogáveis por mais dez (art. 173); vencido o Desembargador — inclusive só quanto ao fundamento determinante (art. 180) —, os fundamentos do voto vencido em **72 horas** (art. 179); ementa e voto divergentes → prevalece o voto (art. 185), por isso a Fase 4 (controle de completude e revisão adversarial) confere a congruência entre ambos.\n\n")

S.append("## 10. Plantão e urgências fora do expediente\n")
S.append(bloco("Art. 75, § 2º", tr(75, r"§2º", r"§3º")))
S.append(bloco("Art. 77", v(77)))

S.append("## 11. Juiz(íza) convocado(a)\n")
S.append(bloco("Art. 26, § 8º", tr(26, r"§ 8º", r"§ 9º")))
S.append(bloco("Art. 38, caput e § 1º", tr(38, None, r"§2º")))
S.append(bloco("Art. 39", v(39)))

S.append("## 12. Uniformização, repositórios e integração\n")
for n in (268, 297, 299, 389, 392, 394):
    S.append(bloco(f"Art. {n}", v(n)))

destino = Path(sys.argv[1]) if len(sys.argv) > 1 else \
    Path(__file__).resolve().parent.parent / "referencias" / "regimento_tjal.md"
destino.write_text("\n".join(S), encoding="utf-8")
print(f"Mapa regimental gravado em {destino}")
