# testar_acesso.ps1 — teste de acesso SOMENTE LEITURA ao SAJ/SG5 (Fase 0 do skill).
# Não clica, não digita, não altera nada no sistema: apenas localiza o processo e a janela do SG5,
# lista as janelas SAJ visíveis (modais pendentes), captura a tela principal e confere a lotação
# contra config/gabinete.json. O teste do e-SAJ de 2º grau é feito pelo navegador (SKILL.md, 0.1).
# Uso: powershell -ExecutionPolicy Bypass -File scripts\testar_acesso.ps1
param([string]$Saida = (Join-Path (Get-Location) '_teste_acesso.json'))

$ErrorActionPreference = 'Continue'
$BASE = Split-Path -Parent $MyInvocation.MyCommand.Path
$SAJ = Join-Path $BASE 'saj_sg5.ps1'
$CONFIG = Join-Path (Split-Path -Parent $BASE) 'config\gabinete.json'
$cfg = Get-Content $CONFIG -Raw -Encoding UTF8 | ConvertFrom-Json
$r = [ordered]@{ ts = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ss'); maquina = $env:COMPUTERNAME; usuario_windows = $env:USERNAME }

# 1. Processo e janela do SG5
$verif = & powershell -NoProfile -ExecutionPolicy Bypass -File $SAJ -Modo Verificar -Processo $cfg.saj_sg5.processo_regex 2>&1 | Out-String
$r.sg5_verificar = $verif.Trim()
$r.sg5_aberto = ($verif -match 'SAJSG5=aberto')
if ($verif -match 'Executavel:\s*(.+)') { $r.sg5_executavel = $Matches[1].Trim() }
if ($verif -match 'Janela=(.+)') { $r.sg5_janela = $Matches[1].Trim() }

# 2. Janelas SAJ visíveis (modais "Aviso"/"Erro" pendentes bloqueiam a automação)
$r.sg5_janelas = (& powershell -NoProfile -ExecutionPolicy Bypass -File $SAJ -Modo Janelas 2>&1 | Out-String).Trim()

# 3. Captura da janela principal (para a Rodada de Descoberta: título, lotação, usuário)
if ($r.sg5_aberto) {
  $png = Join-Path (Split-Path -Parent $Saida) ('_teste_sg5_' + (Get-Date).ToString('yyyyMMdd_HHmmss') + '.png')
  $cap = & powershell -NoProfile -ExecutionPolicy Bypass -File $SAJ -Modo Captura -Processo $cfg.saj_sg5.processo_regex -Arquivo $png 2>&1 | Out-String
  $r.sg5_captura = if (Test-Path $png) { $png } else { 'falhou: ' + $cap.Trim() }
}

# 4. Lotação: só confere se a configuração já tiver o padrão confirmado
$lot = [string]$cfg.gabinete.lotacao_esperada_regex
if ($lot -and $lot -notmatch '^A_CONFIRMAR') {
  $r.sg5_lotacao_confere = [bool]($r.sg5_janela -match $lot)
} else {
  $r.sg5_lotacao_confere = 'pendente: preencher gabinete.lotacao_esperada_regex com o que a captura mostrar'
}

# 5. Navegador: apenas presença do Chrome (o login no e-SAJ é conferido pela página, não por aqui)
$r.chrome_em_execucao = [bool](Get-Process -Name chrome -ErrorAction SilentlyContinue)
$r.esaj_2grau_entrada = $cfg.esaj.entrada_2grau
$TRABALHO = if ($env:GABINETE_TRABALHO) { $env:GABINETE_TRABALHO } else { $BASE }
$r.pasta_de_estado = $TRABALHO
$r.kill_switch_ativo = (Test-Path (Join-Path $BASE 'PARAR.txt')) -or (Test-Path (Join-Path $TRABALHO 'PARAR.txt'))

($r | ConvertTo-Json -Depth 4) | Out-File -FilePath $Saida -Encoding utf8
$r.GetEnumerator() | ForEach-Object { '{0,-22} {1}' -f $_.Key, $_.Value }
"Relatorio gravado em $Saida"
if (-not $r.sg5_aberto) { exit 1 }
