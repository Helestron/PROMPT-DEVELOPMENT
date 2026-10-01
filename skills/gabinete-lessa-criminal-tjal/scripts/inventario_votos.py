#!/usr/bin/env python3
"""Inventário SOMENTE LEITURA da pasta ou drive compartilhado de votos de outros gabinetes.

Percorre a pasta (local, unidade de rede, OneDrive/Google Drive sincronizado), identifica
cada documento de voto, extrai os números CNJ, o relator, o tipo de peça e a sessão
indicada, calcula o hash SHA-256 e compara com o inventário anterior para apontar o que é
NOVO, ALTERADO (voto reescrito após a revisão) ou INALTERADO.

Garantias: abre arquivos apenas para leitura ('rb'); nunca grava, move, renomeia ou apaga
nada na pasta compartilhada. O inventário é gravado na pasta de trabalho do gabinete.

Uso:
    python inventario_votos.py "<pasta compartilhada>" --saida <pasta_trabalho>/_inventario_revisao.json
                               [--desde AAAA-MM-DD] [--gabinete-proprio "Lessa"]
"""
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cnj  # noqa: E402
from conferir_citacoes import texto_de  # noqa: E402

EXTENSOES = {".docx", ".doc", ".rtf", ".odt", ".pdf", ".txt"}
RELATOR = re.compile(r"Relator(?:a)?\s*[:\-–]?\s*(?:o\s+|a\s+)?(?:Des(?:embargador)?(?:a)?\.?\s+)([A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç\.\s]{3,80}?)(?:\n|$|,|;)", re.I)
TIPOS = [("voto-vista", r"voto[\s-]+vista"), ("voto divergente", r"voto\s+divergente"),
         ("declaração de voto", r"declara[çc][ãa]o\s+de\s+voto"), ("ementa", r"^\s*ementa"),
         ("relatório e voto", r"relat[óo]rio.*\bvoto\b"), ("voto", r"\bvoto\b"), ("relatório", r"relat[óo]rio")]
SESSAO = re.compile(r"sess[ãa]o\s+(?:virtual\s+|presencial\s+|ordin[áa]ria\s+|extraordin[áa]ria\s+)*(?:de|do dia|realizada em)?\s*(\d{1,2}/\d{1,2}/\d{4})", re.I)


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 16), b""):
            h.update(bloco)
    return h.hexdigest()


def classificar(texto: str) -> str:
    inicio = texto[:3000].lower()
    for nome, padrao in TIPOS:
        if re.search(padrao, inicio, re.M | re.S):
            return nome
    return "indeterminado"


def main(argv):
    if not argv:
        print(__doc__); return 2
    pasta = Path(argv[0])
    if not pasta.is_dir():
        print(json.dumps({"erro": f"pasta inacessível: {pasta}"}, ensure_ascii=False)); return 1
    saida = Path(argv[argv.index("--saida") + 1]) if "--saida" in argv else Path("_inventario_revisao.json")
    desde = datetime.fromisoformat(argv[argv.index("--desde") + 1]) if "--desde" in argv else None
    proprio = argv[argv.index("--gabinete-proprio") + 1].lower() if "--gabinete-proprio" in argv else None
    anterior = {}
    if saida.exists():
        anterior = {i["caminho"]: i for i in json.loads(saida.read_text(encoding="utf-8")).get("itens", [])}

    itens = []
    for arq in sorted(p for p in pasta.rglob("*") if p.is_file() and p.suffix.lower() in EXTENSOES):
        if arq.name.startswith(("~$", ".")):
            continue  # arquivos temporários de edição em curso
        mtime = datetime.fromtimestamp(arq.stat().st_mtime)
        if desde and mtime < desde:
            continue
        item = {"caminho": str(arq), "arquivo": arq.name, "modificado": mtime.isoformat(timespec="seconds"),
                "sha256": sha256(arq)}
        try:
            texto = texto_de(arq)
        except Exception as exc:  # noqa: BLE001 — registra e segue: falha de um arquivo não trava o inventário
            item.update(situacao="ILEGIVEL", erro=str(exc)); itens.append(item); continue
        numeros = cnj.extrair(texto)
        rel = RELATOR.search(texto)
        ses = SESSAO.search(texto)
        item.update(
            processos=[{"numero": n, "valido": cnj.analisar(n)["valido"]} for n in numeros],
            relator=rel.group(1).strip() if rel else None,
            tipo=classificar(texto),
            sessao=ses.group(1) if ses else None,
            palavras=len(texto.split()),
        )
        if proprio and item["relator"] and proprio in item["relator"].lower():
            item["proprio_gabinete"] = True
        ant = anterior.get(str(arq))
        if not ant:
            item["situacao"] = "NOVO"
        elif ant.get("sha256") != item["sha256"]:
            item["situacao"] = "ALTERADO"
            item["revisao_anterior"] = ant.get("revisado_em")
        else:
            item["situacao"] = "INALTERADO"
            item["revisado_em"] = ant.get("revisado_em")
        itens.append(item)

    resultado = {"pasta": str(pasta), "gerado_em": datetime.now().isoformat(timespec="seconds"),
                 "total": len(itens),
                 "novos": sum(i.get("situacao") == "NOVO" for i in itens),
                 "alterados": sum(i.get("situacao") == "ALTERADO" for i in itens),
                 "itens": itens}
    saida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in resultado.items() if k != "itens"}, ensure_ascii=False))
    for i in itens:
        if i.get("situacao") in ("NOVO", "ALTERADO", "ILEGIVEL"):
            nums = ", ".join(p["numero"] for p in i.get("processos", [])) or "sem número"
            print(f"{i['situacao']:<10} {i.get('tipo', '-'):<20} {nums:<28} {i.get('relator') or '-'} | {i['arquivo']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
