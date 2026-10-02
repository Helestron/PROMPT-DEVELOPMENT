# saj_sg5.ps1 — primitivas de automação do SAJ/SG5 (Segundo Grau) para o skill
# gabinete-lessa-criminal-tjal. Derivado do saj_auto.ps1 (SAJ/PG5, validado em 23-24/08/2026).
# PowerShell 5.1. O script NUNCA digita senha e NUNCA aciona controles de assinatura, de
# liberação nos autos ou de registro de voto em sessão: os termos vedados são bloqueados
# mesmo que solicitados. Todo modo que age sobre o SG5 exige -Operacao (matriz A/B/C).
# Operações de nível B (movimentação visível nos autos) exigem autorização de lote do dia,
# registrada em autorizacao_nivel_b.json; as de nível C são recusadas.
param(
  [Parameter(Mandatory=$true)][ValidateSet('Verificar','Ativar','Arvore','Clique','CliqueXY','Rolar','Texto','Teclas','ColarRtf','Captura','ConverterRtf','Janelas','Esperar','CopiarSelecao')]
  [string]$Modo,
  [string]$Janela = 'Sistema de Automa|SAJ',  # regex sobre o título da janela
  [string]$Processo = 'sajsg5*',  # identity gate: padrão -like do nome do processo dono da janela
  [string]$Operacao,            # rótulo semântico da ação (config/gabinete.json > operacoes)
  [string]$NumeroProcesso,      # número CNJ a que a ação se refere (obrigatório no nível B)
  [int]$Segundos = 30,          # Esperar: tempo máximo
  [string]$Nome,                # nome (UIA Name) do controle alvo
  [string]$Valor,               # texto para -Modo Texto
  [string]$Teclas,              # sequência SendKeys para -Modo Teclas
  [string]$Arquivo,             # RTF de entrada (ColarRtf) / PNG de saída (Captura) / DOCX (ConverterRtf)
  [string]$Saida,               # arquivo de saída (Arvore, ConverterRtf)
  [int]$X = -1,                 # CliqueXY: coordenada X relativa à janela
  [int]$Y = -1,                 # CliqueXY: coordenada Y relativa à janela
  [switch]$Duplo,               # CliqueXY: clique duplo
  [switch]$Shift,               # CliqueXY: segura Shift durante o clique (estende seleção)
  [switch]$Direito,             # CliqueXY: clique com o botão direito (menu de contexto)
  [int]$Delta = 0,              # Rolar: cliques da roda (+ para cima, - para baixo)
  [switch]$Substituir,          # ColarRtf: Ctrl+A antes de colar (NUNCA no editor do SAJ: Ctrl+A = Abrir)
  [switch]$Ensaio               # dry-run: registra a ação no log sem executar clique/tecla
)

$ErrorActionPreference = 'Stop'
# Termos de controles e textos vedados (nível C e credenciais). Específicos de propósito: "vista",
# "baixa" e "cancelar" isolados bloqueariam a vista à PGJ e a baixa para retratação (nível B) e o
# botão Cancelar dos diálogos, que é saída segura.
$VEDADOS = 'assin|liberar|libera nos autos|certific|senha|token|\bpin\b|\bvotar\b|registrar voto|proferir voto|' +
           'confirmar voto|lan[çc]ar voto|pedir vista|pedido de vista|suspei[çc]|impediment|excluir|remover documento|' +
           'apagar|deletar|cancelar documento|redistribu|arquivar|arquivamento|baixa definitiva|baixar (o )?processo|' +
           'baixar (os )?autos|dar baixa|tr[âa]nsito em julgado|alterar (o )?cadastro|alterar partes'
# Modos que agem sobre o SG5 (clique, tecla, texto, cópia): sempre com -Operacao da matriz.
$MODOS_ACAO = @('Clique','CliqueXY','Rolar','Texto','Teclas','ColarRtf','CopiarSelecao')
$BASE = Split-Path -Parent $MyInvocation.MyCommand.Path
$CONFIG = Join-Path (Split-Path -Parent $BASE) 'config\gabinete.json'
# Pasta de estado (log, autorizacao de nivel B, PARAR.txt): por padrao, a do script; se a pasta do
# skill for somente leitura, defina a variavel de ambiente GABINETE_TRABALHO com a pasta de trabalho.
$TRABALHO = if ($env:GABINETE_TRABALHO) { $env:GABINETE_TRABALHO } else { $BASE }

# Kill switch: PARAR.txt ao lado do script ou na pasta de trabalho suspende toda a automacao.
# 'PARAR*' alcança também 'PARAR.txt.txt', nome que o Explorer gera com extensões ocultas.
if (Get-ChildItem -Path @($BASE, $TRABALHO) -Filter 'PARAR*' -File -ErrorAction SilentlyContinue) {
  throw 'Kill switch ativo (PARAR.txt): automacao suspensa pelo usuario.'
}

if ($MODOS_ACAO -contains $Modo -and -not $Operacao) {
  throw "BLOQUEADO: -Modo $Modo exige -Operacao <rotulo da matriz> (config/gabinete.json > operacoes)."
}

# Data ISO 8601 da autorização (AAAA-MM-DDTHH:MM:SS); formato ambíguo (dd/mm x mm/dd) é recusado.
function Ler-DataIso($v, [string]$campo) {
  if ($v -is [datetime]) { return $v }   # PowerShell 7 já converte datas ISO do JSON
  $d = [datetime]::MinValue
  $formatos = [string[]]@('yyyy-MM-ddTHH:mm:ss', 'yyyy-MM-ddTHH:mm', 'yyyy-MM-dd')
  if (-not [datetime]::TryParseExact([string]$v, $formatos, [Globalization.CultureInfo]::InvariantCulture,
      [Globalization.DateTimeStyles]::None, [ref]$d)) {
    throw "BLOQUEADO: '$campo' da autorizacao deve estar em ISO (AAAA-MM-DDTHH:MM:SS): '$v'."
  }
  return $d
}

# Matriz de operações: nível A (automático), B (exige autorização de lote), C (vedado).
if ($Operacao) {
  if (-not (Test-Path $CONFIG)) { throw "Configuracao ausente: $CONFIG" }
  $cfg = Get-Content $CONFIG -Raw -Encoding UTF8 | ConvertFrom-Json
  if ($cfg.operacoes.nivel_c -contains $Operacao) {
    throw "BLOQUEADO: '$Operacao' e operacao de nivel C (vedada a automacao em qualquer hipotese)."
  }
  if ($cfg.operacoes.nivel_b -contains $Operacao) {
    $aut = Join-Path $TRABALHO 'autorizacao_nivel_b.json'
    if (-not (Test-Path $aut)) { throw "BLOQUEADO: '$Operacao' (nivel B) sem autorizacao_nivel_b.json." }
    $a = Get-Content $aut -Raw -Encoding UTF8 | ConvertFrom-Json
    if (-not $a.texto_literal) { throw 'BLOQUEADO: autorizacao de nivel B sem o texto literal da ordem do usuario.' }
    $concedida = Ler-DataIso $a.concedida_em 'concedida_em'
    $validade = Ler-DataIso $a.valida_ate 'valida_ate'
    $agora = Get-Date
    # A autorização vale, no máximo, até o fim do dia em que foi concedida (SKILL.md, Fase 5).
    if ($concedida.Date -ne $agora.Date) { throw "BLOQUEADO: autorizacao de nivel B concedida em outro dia ($($a.concedida_em))." }
    if ($validade -gt $concedida.Date.AddDays(1)) { throw "BLOQUEADO: validade alem do dia da concessao ($($a.valida_ate))." }
    if ($agora -gt $validade) { throw "BLOQUEADO: autorizacao de nivel B expirada em $($a.valida_ate)." }
    if (-not ($a.operacoes -contains $Operacao)) { throw "BLOQUEADO: '$Operacao' nao consta da autorizacao do lote." }
    if (-not $NumeroProcesso -or -not ($a.processos -contains $NumeroProcesso)) {
      throw "BLOQUEADO: processo '$NumeroProcesso' nao consta da autorizacao do lote para '$Operacao'."
    }
  } elseif (-not ($cfg.operacoes.nivel_a -contains $Operacao)) {
    throw "BLOQUEADO: operacao '$Operacao' fora da matriz (classifique-a em config/gabinete.json antes de usar)."
  }
}


# Log JSONL de auditoria: uma linha por acao executada.
function Registrar([hashtable]$d) {
  $d['ts'] = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ss'); $d['modo'] = $Modo; $d['ensaio'] = [bool]$Ensaio
  if ($Operacao) { $d['operacao'] = $Operacao }; if ($NumeroProcesso) { $d['processo'] = $NumeroProcesso }
  ($d | ConvertTo-Json -Compress) | Add-Content -Path (Join-Path $TRABALHO 'saj_log.jsonl') -Encoding utf8
}

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName WindowsBase
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Text;
using System.Collections.Generic;
using System.Runtime.InteropServices;
public class Win32Saj {
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern int GetWindowThreadProcessId(IntPtr h, out int pid);
  // Ativa apenas se o primeiro plano nao pertencer ao mesmo processo: reativar colapsa a selecao
  // do editor e rouba o foco de dialogos filhos (Emissao de Documentos, Consulta de Modelos...).
  public static void AtivarSeNecessario(IntPtr h) {
    IntPtr fg = GetForegroundWindow();
    if (fg == h) return;
    int pidAlvo, pidFg;
    GetWindowThreadProcessId(h, out pidAlvo);
    GetWindowThreadProcessId(fg, out pidFg);
    if (pidFg == pidAlvo) return;
    SetForegroundWindow(h); System.Threading.Thread.Sleep(300);
  }
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT r);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(int f, int x, int y, int d, int i);
  [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte scan, int flags, int extra);
  [DllImport("user32.dll")] static extern bool EnumWindows(EnumProc cb, IntPtr l);
  [DllImport("user32.dll")] static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] static extern bool IsWindowEnabled(IntPtr h);
  delegate bool EnumProc(IntPtr h, IntPtr l);
  public struct RECT { public int Left, Top, Right, Bottom; }
  // Janelas VISIVEIS com titulo, ordem Z (a primeira e a mais ao topo). O SAJ (Delphi)
  // tem MainWindowHandle apontando para a TApplication oculta; o formulario real so aparece aqui.
  public static List<long> JanelasVisiveis(out List<string> titulos) {
    var hs = new List<long>(); var ts = new List<string>();
    EnumWindows((h, l) => {
      if (IsWindowVisible(h)) {
        var t = new StringBuilder(512); GetWindowText(h, t, 512);
        if (t.Length > 0) { hs.Add(h.ToInt64()); ts.Add(t.ToString()); }
      }
      return true;
    }, IntPtr.Zero);
    titulos = ts; return hs;
  }
}
"@

[Win32Saj]::SetProcessDPIAware() | Out-Null   # coordenadas físicas: captura e clique no mesmo sistema

function Get-JanelaSaj([string]$rx) {
  # Identity gate: só devolve janela cujo processo dono corresponde a $Processo (sajsg5*) — nunca "uma janela qualquer".
  $titulos = New-Object 'System.Collections.Generic.List[string]'
  $hs = [Win32Saj]::JanelasVisiveis([ref]$titulos)
  for ($i = 0; $i -lt $hs.Count; $i++) {
    if ($titulos[$i] -match $rx) {
      $wpid = 0
      [Win32Saj]::GetWindowThreadProcessId([IntPtr]$hs[$i], [ref]$wpid) | Out-Null
      $pr = Get-Process -Id $wpid -ErrorAction SilentlyContinue
      if ($pr -and $pr.Name -like $Processo) {
        return [pscustomobject]@{ Handle = [IntPtr]$hs[$i]; Titulo = $titulos[$i] }
      }
    }
  }
  throw "Nenhuma janela do processo $Processo com titulo correspondente a '$rx'. O SAJ/SG5 esta aberto e logado? (acao abortada)"
}

function Ativar-EGarantirFoco([IntPtr]$h) {
  # AtivarSeNecessario preserva selecao/dialogos; depois, o primeiro plano DEVE ser do SAJ, senao aborta.
  for ($t = 0; $t -lt 3; $t++) {
    [Win32Saj]::AtivarSeNecessario($h)
    $fg = [Win32Saj]::GetForegroundWindow()
    $fgpid = 0; [Win32Saj]::GetWindowThreadProcessId($fg, [ref]$fgpid) | Out-Null
    $pr = Get-Process -Id $fgpid -ErrorAction SilentlyContinue
    if ($pr -and $pr.Name -like $Processo) { return }
    Start-Sleep -Milliseconds 300
  }
  throw 'O primeiro plano nao pertence ao SAJ/SG5; tecla/clique abortado (identity gate).'
}
function Get-ElementoRaiz([string]$rx) {
  $p = Get-JanelaSaj $rx
  return [System.Windows.Automation.AutomationElement]::FromHandle($p.Handle)
}
function Nome-SobPonto([int]$x, [int]$y) {
  # Nome UIA do controle sob o ponto de tela; vazio quando o controle Delphi não se expõe.
  try { return [string][System.Windows.Automation.AutomationElement]::FromPoint((New-Object System.Windows.Point($x, $y))).Current.Name }
  catch { return '' }
}
function Find-Controle($raiz, [string]$nome) {
  if ([string]::IsNullOrWhiteSpace($nome)) { throw 'Informe -Nome (nome exato do controle; rode -Modo Arvore).' }
  $cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $nome)
  $el = $raiz.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $cond)
  if (-not $el) {
    # fallback: varredura por correspondência parcial, insensível a caixa
    $todos = $raiz.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
    foreach ($c in $todos) { if ($c.Current.Name -and $c.Current.Name -match [regex]::Escape($nome)) { return $c } }
    throw "Controle '$nome' nao encontrado. Rode -Modo Arvore e confira o nome exato."
  }
  return $el
}

switch ($Modo) {
  'Verificar' {
    $proc = Get-Process -Name $Processo -ErrorAction SilentlyContinue
    if (-not $proc) {
      $saj = Get-Process | Where-Object { $_.Name -like 'saj*' } | Select-Object -ExpandProperty Name -Unique
      Write-Output ("SAJSG5=ausente | processos SAJ ativos: " + ($saj -join ', ') + " (ajuste -Processo se o nome diferir)"); exit 1
    }
    Write-Output ("Executavel: " + (($proc | Select-Object -First 1).Path))
    try { $j = Get-JanelaSaj $Janela; Write-Output ("SAJSG5=aberto | Janela=$($j.Titulo)") }
    catch { Write-Output 'SAJSG5=processo ativo, janela principal nao localizada (login pendente?)'; exit 1 }
  }
  'Ativar' {
    $p = Get-JanelaSaj $Janela
    Registrar @{ janela = $p.Titulo }
    if ($Ensaio) { Write-Output ('ENSAIO: ativacao de {0} nao executada' -f $p.Titulo); break }
    [Win32Saj]::ShowWindow($p.Handle, 9) | Out-Null   # SW_RESTORE
    [Win32Saj]::SetForegroundWindow($p.Handle) | Out-Null
    Write-Output "Ativada: $($p.Titulo)"
  }
  'CliqueXY' {
    if ($X -lt 0 -or $Y -lt 0) { throw 'Informe -X e -Y (coordenadas relativas a janela).' }
    $p = Get-JanelaSaj $Janela
    if (-not $Ensaio) { Ativar-EGarantirFoco $p.Handle }
    $r = New-Object Win32Saj+RECT; [Win32Saj]::GetWindowRect($p.Handle, [ref]$r) | Out-Null
    $ax = $r.Left + $X; $ay = $r.Top + $Y
    # Se a UI Automation der nome ao controle sob o ponto, o nome passa pelo bloqueio; controles
    # Delphi sem nome dependem da captura conferida antes do clique (saj_sg5_operacoes.md, item 3).
    $sob = Nome-SobPonto $ax $ay
    if ($sob -match $VEDADOS) { throw "BLOQUEADO: o controle sob o ponto ('$sob') e vedado." }
    Registrar @{ janela = $p.Titulo; x = $X; y = $Y; controle = $sob; duplo = [bool]$Duplo; direito = [bool]$Direito; shift = [bool]$Shift }
    if ($Ensaio) { Write-Output ('ENSAIO: clique em ({0},{1}) rel. a {2} [{3}] nao executado' -f $X, $Y, $p.Titulo, $sob); break }
    [Win32Saj]::SetCursorPos($ax, $ay) | Out-Null; Start-Sleep -Milliseconds 250
    if ($Shift) { [Win32Saj]::keybd_event(0x10,0,0,0); Start-Sleep -Milliseconds 80 }
    $down = 2; $up = 4
    if ($Direito) { $down = 8; $up = 16 }
    [Win32Saj]::mouse_event($down,0,0,0,0); Start-Sleep -Milliseconds 60; [Win32Saj]::mouse_event($up,0,0,0,0)
    if ($Duplo) { Start-Sleep -Milliseconds 120; [Win32Saj]::mouse_event(2,0,0,0,0); Start-Sleep -Milliseconds 60; [Win32Saj]::mouse_event(4,0,0,0,0) }
    if ($Shift) { Start-Sleep -Milliseconds 80; [Win32Saj]::keybd_event(0x10,0,2,0) }
    Write-Output "Clique em ($X,$Y) rel. a '$($p.Titulo)' (tela: $ax,$ay)"
  }
  'Rolar' {
    if ($X -lt 0 -or $Y -lt 0 -or $Delta -eq 0) { throw 'Informe -X, -Y (posição sobre a área a rolar) e -Delta (≠0).' }
    $p = Get-JanelaSaj $Janela
    Registrar @{ janela = $p.Titulo; x = $X; y = $Y; delta = $Delta }
    if ($Ensaio) { Write-Output ('ENSAIO: rolagem de {0} em ({1},{2}) nao executada' -f $Delta, $X, $Y); break }
    Ativar-EGarantirFoco $p.Handle
    $r = New-Object Win32Saj+RECT; [Win32Saj]::GetWindowRect($p.Handle, [ref]$r) | Out-Null
    [Win32Saj]::SetCursorPos($r.Left + $X, $r.Top + $Y) | Out-Null; Start-Sleep -Milliseconds 200
    $passos = [Math]::Abs($Delta); $sinal = [Math]::Sign($Delta)
    for ($i = 0; $i -lt $passos; $i++) {
      [Win32Saj]::mouse_event(0x0800, 0, 0, 120 * $sinal, 0)   # MOUSEEVENTF_WHEEL
      Start-Sleep -Milliseconds 120
    }
    Write-Output "Rolagem de $Delta clique(s) em ($X,$Y) rel. a '$($p.Titulo)'"
  }
  'Arvore' {
    $raiz = Get-ElementoRaiz $Janela
    $linhas = New-Object System.Collections.Generic.List[string]
    function Caminhar($el, $nivel) {
      if ($nivel -gt 12) { return }
      $c = $el.Current
      $linhas.Add(('  ' * $nivel) + "[$($c.ControlType.ProgrammaticName -replace 'ControlType.','')] '$($c.Name)' cls='$($c.ClassName)' id='$($c.AutomationId)'")
      $filhos = $el.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)
      foreach ($f in $filhos) { Caminhar $f ($nivel + 1) }
    }
    Caminhar $raiz 0
    if ($Saida) { $linhas | Out-File -FilePath $Saida -Encoding utf8; Write-Output "Arvore gravada em $Saida ($($linhas.Count) controles)" }
    else { $linhas | Select-Object -First 400 }
  }
  'Clique' {
    if ($Nome -match $VEDADOS) { throw "BLOQUEADO: '$Nome' corresponde a controle vedado (assinatura/liberacao/credencial). Teto = finalizar sem assinar." }
    $p = Get-JanelaSaj $Janela
    $raiz = [System.Windows.Automation.AutomationElement]::FromHandle($p.Handle)
    $el = Find-Controle $raiz $Nome
    # A busca admite correspondencia parcial: o nome REAL do controle encontrado tambem passa pelo bloqueio.
    if ($el.Current.Name -match $VEDADOS) { throw "BLOQUEADO: o controle encontrado ('$($el.Current.Name)') e vedado." }
    Registrar @{ janela = $p.Titulo; controle = $el.Current.Name }
    if ($Ensaio) { Write-Output ("ENSAIO: clique em '{0}' nao executado" -f $el.Current.Name); break }
    $inv = $null
    if ($el.TryGetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern, [ref]$inv)) { $inv.Invoke() }
    else {
      $sel = $null
      if ($el.TryGetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern, [ref]$sel)) { $sel.Select() }
      else {
        Ativar-EGarantirFoco $p.Handle
        $pt = $el.GetClickablePoint()
        [Win32Saj]::SetCursorPos([int]$pt.X, [int]$pt.Y) | Out-Null; Start-Sleep -Milliseconds 200
        [Win32Saj]::mouse_event(2,0,0,0,0); [Win32Saj]::mouse_event(4,0,0,0,0)
      }
    }
    Write-Output "Acionado: '$($el.Current.Name)' [$($el.Current.ControlType.ProgrammaticName)]"
  }
  'Texto' {
    if ($Valor -match '^\s*$') { throw 'Valor vazio.' }
    if ($Valor -match $VEDADOS) { throw 'BLOQUEADO: texto contem termo vedado (credencial/assinatura).' }
    $p = Get-JanelaSaj $Janela
    $raiz = [System.Windows.Automation.AutomationElement]::FromHandle($p.Handle)
    $el = Find-Controle $raiz $Nome
    if ($el.Current.Name -match $VEDADOS) { throw "BLOQUEADO: o campo encontrado ('$($el.Current.Name)') e vedado." }
    Registrar @{ janela = $p.Titulo; campo = $el.Current.Name; caracteres = $Valor.Length }
    if ($Ensaio) { Write-Output ("ENSAIO: texto em '{0}' nao inserido" -f $el.Current.Name); break }
    $vp = $null
    if ($el.TryGetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern, [ref]$vp)) { $vp.SetValue($Valor) }
    else {
      $el.SetFocus(); Start-Sleep -Milliseconds 300
      Ativar-EGarantirFoco $p.Handle
      # Literal para o SendKeys: + ^ % ~ ( ) { } [ ] entre chaves ("50%" não vira Alt+5+0).
      [System.Windows.Forms.SendKeys]::SendWait([regex]::Replace($Valor, '[+^%~(){}\[\]]', '{$0}'))
    }
    Write-Output "Texto inserido em '$($el.Current.Name)'"
  }
  'Teclas' {
    if ($Teclas -match $VEDADOS) { throw 'BLOQUEADO: sequência vedada.' }
    $p = Get-JanelaSaj $Janela
    Registrar @{ janela = $p.Titulo; teclas = $Teclas }
    if ($Ensaio) { Write-Output ('ENSAIO: teclas {0} nao enviadas' -f $Teclas); break }
    Ativar-EGarantirFoco $p.Handle
    [System.Windows.Forms.SendKeys]::SendWait($Teclas)
    Write-Output "Teclas enviadas: $Teclas"
  }
  'ColarRtf' {
    # Carrega o RTF no clipboard (formato RTF + texto simples) e cola com Ctrl+V na janela alvo.
    if (-not (Test-Path $Arquivo)) { throw "RTF nao encontrado: $Arquivo" }
    $rtf = [System.IO.File]::ReadAllText($Arquivo)
    $txt = $rtf -replace '\\[a-z]+-?\d*[ ]?','' -replace '[{}]',''
    $dado = New-Object System.Windows.Forms.DataObject
    $dado.SetData([System.Windows.Forms.DataFormats]::Rtf, $rtf)
    $dado.SetData([System.Windows.Forms.DataFormats]::Text, $txt)
    $p = Get-JanelaSaj $Janela
    Registrar @{ janela = $p.Titulo; arquivo = $Arquivo; substituir = [bool]$Substituir }
    if ($Ensaio) { Write-Output ('ENSAIO: ColarRtf de {0} nao executado' -f $Arquivo); break }
    [System.Windows.Forms.Clipboard]::SetDataObject($dado, $true)
    Ativar-EGarantirFoco $p.Handle
    if ($Substituir) { [System.Windows.Forms.SendKeys]::SendWait('^a'); Start-Sleep -Milliseconds 200 }
    [System.Windows.Forms.SendKeys]::SendWait('^v')
    Start-Sleep -Milliseconds 800
    [System.Windows.Forms.Clipboard]::Clear()   # não deixar conteúdo de minuta no clipboard
    Write-Output "RTF colado na janela '$($p.Titulo)' (clipboard limpo)"
  }
  'Captura' {
    $p = Get-JanelaSaj $Janela
    [Win32Saj]::AtivarSeNecessario($p.Handle)
    $r = New-Object Win32Saj+RECT; [Win32Saj]::GetWindowRect($p.Handle, [ref]$r) | Out-Null
    $w = $r.Right - $r.Left; $h = $r.Bottom - $r.Top
    $bmp = New-Object System.Drawing.Bitmap($w, $h)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($r.Left, $r.Top, 0, 0, (New-Object System.Drawing.Size($w, $h)))
    $bmp.Save($Arquivo, [System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $bmp.Dispose()
    Write-Output "Captura salva em $Arquivo"
  }
  'Janelas' {
    # Enumera janelas visiveis (ordem Z) com o processo dono: localiza modais ("Aviso", "Erro")
    # que bloqueiam a entrada sem aparecer na captura da janela principal.
    $titulos = New-Object 'System.Collections.Generic.List[string]'
    $hs = [Win32Saj]::JanelasVisiveis([ref]$titulos)
    for ($i = 0; $i -lt $hs.Count; $i++) {
      $wpid = 0; [Win32Saj]::GetWindowThreadProcessId([IntPtr]$hs[$i], [ref]$wpid) | Out-Null
      $pr = Get-Process -Id $wpid -ErrorAction SilentlyContinue
      if ($pr -and $pr.Name -like 'saj*') { Write-Output ("{0,-3} {1,-14} {2}" -f $i, $pr.Name, $titulos[$i]) }
    }
  }
  'Esperar' {
    # Aguarda (sem clicar) a janela cujo titulo corresponda a -Janela, ate -Segundos.
    $limite = (Get-Date).AddSeconds($Segundos)
    while ((Get-Date) -lt $limite) {
      try { $j = Get-JanelaSaj $Janela; Write-Output "Disponivel: $($j.Titulo)"; exit 0 } catch { Start-Sleep -Milliseconds 700 }
    }
    Write-Output "Tempo esgotado ($Segundos s) aguardando '$Janela'"; exit 1
  }
  'CopiarSelecao' {
    # Copia (Ctrl+C) a selecao corrente -- grade da fila, dados do processo, texto do editor --
    # e devolve o texto. Somente leitura: nada e alterado no SAJ. O clipboard e limpo ao final.
    $p = Get-JanelaSaj $Janela
    Registrar @{ janela = $p.Titulo }
    if ($Ensaio) { Write-Output 'ENSAIO: copia nao executada'; break }
    Ativar-EGarantirFoco $p.Handle
    [System.Windows.Forms.Clipboard]::Clear()
    [System.Windows.Forms.SendKeys]::SendWait('^c'); Start-Sleep -Milliseconds 500
    $t = [System.Windows.Forms.Clipboard]::GetText()
    [System.Windows.Forms.Clipboard]::Clear()
    if ($Saida) { $t | Out-File -FilePath $Saida -Encoding utf8; Write-Output "Texto copiado para $Saida ($($t.Length) caracteres)" }
    else { Write-Output $t }
  }
  'ConverterRtf' {
    # DOCX (versao limpa) -> RTF via Word COM; fallback: soffice, se instalado.
    if (-not (Test-Path $Arquivo)) { throw "DOCX nao encontrado: $Arquivo" }
    try {
      $word = New-Object -ComObject Word.Application
      $word.Visible = $false
      $doc = $word.Documents.Open((Resolve-Path $Arquivo).Path, $false, $true)
      $doc.SaveAs([ref]$Saida, [ref]6)   # 6 = wdFormatRTF
      $doc.Close($false); $word.Quit()
      Write-Output "RTF gerado em $Saida (Word COM)"
    } catch {
      $so = Get-Command soffice -ErrorAction SilentlyContinue
      if (-not $so) { throw "Word COM falhou ($($_.Exception.Message)) e soffice ausente." }
      & $so.Source --headless --convert-to rtf --outdir (Split-Path $Saida) $Arquivo
      Write-Output "RTF gerado via soffice"
    }
  }
}
