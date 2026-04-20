# Criar tarefas agendadas para o Bling Integration
# Execute este script como Administrador:
#   Clique direito > "Executar como administrador"

$BASE = "C:\Users\Lenovo\Desktop\Claude_Cloude_Project\bling_integration"

# --- Tarefa 1: Sync diario + Export Parquet (03:00) ---
$action1  = New-ScheduledTaskAction -Execute "$BASE\sync_diario.bat"
$trigger1 = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 15) -Once -At (Get-Date)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 15)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Highest

Register-ScheduledTask `
    -TaskName   "Bling_SyncDiario" `
    -Description "Sync incremental Bling + Export Parquet (a cada 15 minutos)" `
    -Action     $action1 `
    -Trigger    $trigger1 `
    -Settings   $settings `
    -Principal  $principal `
    -Force

Write-Host "[OK] Bling_SyncDiario criada (a cada 15 minutos)" -ForegroundColor Green

# --- Tarefa 2: Enriquecimento (a cada 1 hora, com 30min de offset) ---
$action2  = New-ScheduledTaskAction -Execute "$BASE\enriquecer.bat"
$trigger2 = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 15) -Once -At (Get-Date).AddMinutes(7)

Register-ScheduledTask `
    -TaskName   "Bling_Enriquecer" `
    -Description "Enriquecimento incremental de pedidos Bling (a cada 15 minutos)" `
    -Action     $action2 `
    -Trigger    $trigger2 `
    -Settings   $settings `
    -Principal  $principal `
    -Force

Write-Host "[OK] Bling_Enriquecer criada (a cada 1 hora, offset 30min)" -ForegroundColor Green

Write-Host ""
Write-Host "Tarefas criadas com sucesso! Verifique no Agendador de Tarefas do Windows." -ForegroundColor Cyan
