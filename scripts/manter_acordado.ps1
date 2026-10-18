# Impede a suspensao por inatividade enquanto a coleta Bronze roda; nao altera configuracoes de energia.
# Uso: powershell -NoProfile -File scripts/manter_acordado.ps1 <run_id>
param([Parameter(Mandatory = $true)][string]$RunId)
Add-Type -Namespace Win32 -Name Power -MemberDefinition @'
[System.Runtime.InteropServices.DllImport("kernel32.dll")]
public static extern uint SetThreadExecutionState(uint esFlags);
'@
$ES_CONTINUOUS = [uint32]"0x80000000"; $ES_SYSTEM_REQUIRED = [uint32]"0x00000001"
$log = "work/logs/$RunId.log"
[Win32.Power]::SetThreadExecutionState($ES_CONTINUOUS -bor $ES_SYSTEM_REQUIRED) | Out-Null
try {
    while ($true) {
        if ((Test-Path $log) -and (Select-String -Path $log -Pattern 'WRAPPER (sa.{1,2}da=0|desistiu)' -Quiet)) { break }
        Start-Sleep -Seconds 60
    }
} finally {
    [Win32.Power]::SetThreadExecutionState($ES_CONTINUOUS) | Out-Null
}
