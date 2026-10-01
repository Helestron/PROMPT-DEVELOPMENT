# Acesso aos autos pelo e-SAJ do TJAL — 2º grau e origem

Referência da Fase 1 do SKILL.md.

**Porta de entrada do e-SAJ de 2º grau (informada pelo gabinete em 01/10/2026):**

```
https://www2.tjal.jus.br/cposg5/open.do?gateway=true
```

É a entrada do gabinete para a consulta de 2º grau. **Toda consulta de 2º grau começa por essa
URL**, na sessão autenticada do Chrome. O parâmetro `gateway=true` indica o acesso pela porta de
usuário interno; na primeira execução, confirme e registre no caderno de bordo o que ela libera
em relação à consulta pública (`/cposg5/open.do` sem o parâmetro) — em especial a pasta digital
e os feitos em segredo de justiça — e não troque de entrada no meio do lote.

As rotas do 1º grau (`/cpopg/`) foram **validadas em execução real** no skill de origem
(`lote-minutas-esaj`, 08–09/2026). As rotas internas do 2º grau a partir da entrada (URL de
pesquisa e link da pasta digital) devem ser registradas em `config/gabinete.json >
esaj.rotas_validadas` na primeira execução, com a data — descubra-as na própria página, nunca as
monte de memória.

## 1. O que baixar em cada classe

O processo no 2º grau raramente basta sozinho. Baixe:

| Classe | Autos do 2º grau (`cposg5`) | Autos de origem (`cpopg`) |
|---|---|---|
| Apelação criminal, RESE, embargos infringentes | sempre | sempre que a pasta do 2º grau não trouxer a íntegra da ação penal (sentença, provas, interrogatório, mídias); no RESE, verifique se o recurso subiu em **sequencial** vinculado ao principal (RITJAL, arts. 322 e 327; Código de Normas da CGJ/AL, arts. 797 e 798 — `referencias/cgj_normas_integral.txt`) |
| Habeas corpus, MS criminal, correição parcial | sempre (foro `0000`) | a ação penal ou o inquérito de origem indicado na inicial, para conferir a decisão impugnada e o andamento real |
| Agravo em execução | sempre | a execução tramita no SEEU (CNJ), fora do e-SAJ: trabalhe com as peças trasladadas e registre a limitação |
| Revisão criminal | sempre | a ação penal transitada (sentença, acórdão, certidão de trânsito) |
| Embargos de declaração | o acórdão embargado e o voto condutor | quando a omissão alegada depender de prova da origem |

O número CNJ diz o caminho: foro `0000` é feito originário do Tribunal; foro diverso é recurso que
conserva o número da ação de origem (`scripts/cnj.py` informa `originario_2grau`). Para HC, o
número da origem está na inicial e nas informações da autoridade coatora.

## 2. Consulta e capa

1º grau (validado):

```
https://www2.tjal.jus.br/cpopg/search.do?conversationId=&cbPesquisa=NUMPROC&dadosConsulta.localPesquisa.cdLocal=-1&dadosConsulta.tipoNuProcesso=UNIFICADO&numeroDigitoAnoUnificado=NNNNNNN-DD.AAAA&foroNumeroUnificado=FFFF&dadosConsulta.valorConsultaNuUnificado=NNNNNNNDDAAAA802FFFF&dadosConsulta.valorConsulta=
```

2º grau: abra `https://www2.tjal.jus.br/cposg5/open.do?gateway=true`, confira que a sessão está
autenticada (sem tela de login e com o usuário identificado), pesquise pelo número unificado na
própria tela e **registre a URL de resultado efetivamente gerada** em
`rotas_validadas.consulta_2grau_search` (e o link da pasta em `rotas_validadas.pasta_2grau`).
Nas execuções seguintes, use as URLs registradas, sempre na sessão aberta pela entrada `gateway`.
Se a pesquisa por URL direta perder a autenticação, volte à entrada e pesquise pela tela.

Dados de cadastro úteis: nos processos criminais, o sistema registra a data da infração, do
recebimento da denúncia ou queixa, da prisão e da sentença (RITJAL, art. 83, parágrafo único) —
use-os para **pré-conferir** a prescrição, sempre confirmados nos autos antes de entrar no JSON
de `prescricao.py`. A prioridade registrada no cadastro (art. 74, parágrafo único) orienta a
ordem do lote.

Com `get_page_text`, extraia da capa: classe, assunto, partes (réu preso? — a capa costuma sinalizar),
relator, revisor, órgão julgador, movimentações, incidentes, processos apensos e vinculados,
**situação de pauta** (incluído em pauta, sessão designada, adiado, retirado) e o `processo.codigo`.
As movimentações são o mapa da fase: leia-as antes dos autos.

## 3. Download da pasta digital — rota programática

Na sessão autenticada (Chrome), via `javascript_tool`. **1º grau — rota validada:**

```js
// cd = processo.codigo, extraído da URL show.do da capa
// 1. ticket: o endpoint devolve, como texto, a URL do visualizador da pasta
const u = (await (await fetch('/cpopg/abrirPastaDigital.do?processo.codigo=' + cd
        + '&acessibilidade=true', {credentials: 'include'})).text()).trim();
// 2. parâmetros de cada peça, extraídos do HTML do visualizador
const h = await (await fetch(u, {credentials: 'include'})).text();
const params = [...h.matchAll(/"parametros":"((?:[^"\\]|\\.)*)"/g)]
        .map(m => JSON.parse('"' + m[1] + '"'));
// 3. download peça a peça
for (const p of params) {
  const blob = await (await fetch('/pastadigital/getPDF.do?' + p, {credentials: 'include'})).blob();
  // salvar o blob (ver "Resiliência")
}
```

**2º grau — descobrir e registrar** (a pasta digital é componente comum da Softplan, e os passos
2 e 3 tendem a ser idênticos; o passo 1 deve ser confirmado):

```js
// na página do processo aberta a partir da entrada gateway
const links = [...document.querySelectorAll('a')].map(a => a.href)
        .filter(h => /pasta|abrirPasta/i.test(h));
// abra o link encontrado (ou o equivalente /cposg5/... de rotas_validadas.pasta_2grau);
// se devolver a URL do visualizador como texto, siga o passo 1 acima; se devolver o próprio
// visualizador, aplique diretamente os passos 2 e 3. Registre a rota confirmada.
```

**Rotas mortas no 1º grau** (não insista): `salvarDocumentoPreparado.do` (HTTP 500) e
`recuperaPdfsImpressao.action` (HTTP 404). Se o 2º grau revelar outras, registre-as aqui.

**Resiliência**: 4 retentativas por peça com espera progressiva; até 4 requisições simultâneas;
teto de 40 s por espera assíncrona; quando a saída da ferramenta for o canal de transporte, blob
único precedido de manifesto JSON de 16.384 bytes (número, tamanhos, falhas) e sanitização dos
caracteres de query string antes de retornar, ou o filtro bloqueia com "[BLOCKED]"; nenhum
parâmetro de sessão trafega pela saída. Rodando localmente (Claude Code), salve direto em
`_autos/<numero>/` e dispense blob e manifesto. Carregue as ferramentas do Chrome em **chamada
única** de ToolSearch.

**Rota subsidiária** (interface): "Selecionar todas" → "Baixar PDF" → "Arquivo único" →
"Continuar" → aguardar "O documento foi gerado" → "Salvar o documento". O visualizador costuma
ficar inutilizável para automação de interface após o primeiro uso na sessão.

**Mídias** (interrogatório, depoimentos em audiência gravada): registre a existência, as fls. e o
link; não é possível transcrevê-las sem acesso ao arquivo. Se a prova oral decisiva estiver só em
mídia, a minuta marca em vermelho `[Conferir: depoimento em mídia de fls. X não transcrito]`.

## 4. Texto e OCR

`pdftotext -layout`; vazio (autos por imagem), `pdftoppm -r 150 -png` + `tesseract <img> stdout`
— sem parâmetro de idioma quando o pacote `por` não estiver instalado (com o parâmetro ausente do
sistema, o tesseract não produz saída alguma). Numere as fls. pela paginação da pasta digital, que
é a que o magistrado vê.

## 5. Sessão do e-SAJ

1. Verifique ativamente — abra `https://www2.tjal.jus.br/cposg5/open.do?gateway=true` e confira se
   há tela de login ou usuário identificado; no 1º grau, abra uma `show.do` — em vez de perguntar.
2. Estado persistente em `_estado.json`, por processo e etapa; retomada idempotente.
3. Sinais de expiração ("Não foi possível validar o seu acesso", tela de login): pare de imediato.
4. Uma única mensagem objetiva pedindo novo login; retome do ponto exato.
5. Mantenha a sessão viva com consulta leve periódica durante fases longas.

O login com certificado digital é ato do titular: **nunca** digite senha, PIN ou token.
