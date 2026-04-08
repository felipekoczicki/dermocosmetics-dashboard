# Criar tarefas agendadas para o Bling Integration
# Execute este script como Administrador:
#   Clique direito > "Executar como administrador"

$BASE = "C:\Users\Lenovo\Desktop\Claude_Cloude_Project\bling_integration"

# --- Tarefa 1: Sync diario + Export Parquet (03:00) ---
$action1  = New-ScheduledTaskAction -Execute "$BASE\sync_diario.bat"
$trigger1 = New-ScheduledTaskTrigger -Daily -At "03:00AM"
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 2)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Highest

Register-ScheduledTask `
    -TaskName   "Bling_SyncDiario" `
    -Description "Sync incremental Bling + Export Parquet (roda as 03h)" `
    -Action     $action1 `
    -Trigger    $trigger1 `
    -Settings   $settings `
    -Principal  $principal `
    -Force

Write-Host "[OK] Bling_SyncDiario criada (03:00 diario)" -ForegroundColor Green

# --- Tarefa 2: Enriquecimento (04:00) ---
$action2  = New-ScheduledTaskAction -Execute "$BASE\enriquecer.bat"
$trigger2 = New-ScheduledTaskTrigger -Daily -At "04:00AM"

Register-ScheduledTask `
    -TaskName   "Bling_Enriquecer" `
    -Description "Enriquecimento incremental de pedidos Bling (roda as 04h)" `
    -Action     $action2 `
    -Trigger    $trigger2 `
    -Settings   $settings `
    -Principal  $principal `
    -Force

Write-Host "[OK] Bling_Enriquecer criada (04:00 diario)" -ForegroundColor Green

Write-Host ""
Write-Host "Tarefas criadas com sucesso! Verifique no Agendador de Tarefas do Windows." -ForegroundColor Cyan
