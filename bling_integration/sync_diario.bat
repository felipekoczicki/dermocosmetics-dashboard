@echo off
cd /d C:\Users\Lenovo\Desktop\Claude_Cloude_Project\bling_integration
python run_sync.py --modo incremental >> logs\sync_diario.log 2>&1
python exportar_parquet.py >> logs\sync_diario.log 2>&1
