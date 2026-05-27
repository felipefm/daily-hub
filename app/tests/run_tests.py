#!/usr/bin/env python3
"""
Script auxiliar para executar testes do Daily-HUB com opções amigáveis.

Uso:
    python run_tests.py                          # Executa todos os testes
    python run_tests.py -q                       # Modo rápido (quiet)
    python run_tests.py -v                       # Modo verbose (muito detalhado)
    python run_tests.py -c                       # Com cobertura de código
    python run_tests.py -c -v                    # Cobertura + verbose
    python run_tests.py TestTasks                # Apenas classe específica
    python run_tests.py TestTasks::test_create   # Apenas teste específico
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime

def print_header():
    """Imprime cabeçalho bonito."""
    print("\n" + "=" * 80)
    print("  🧪 TESTES - DAILY-HUB  |  Suite de Testes Abrangente")
    print("=" * 80 + "\n")

def print_summary(result):
    """Imprime resumo da execução."""
    print("\n" + "=" * 80)
    if result == 0:
        print("  ✅ TODOS OS TESTES PASSARAM COM SUCESSO!")
    else:
        print("  ❌ ALGUNS TESTES FALHARAM - Veja os logs acima")
    print("=" * 80 + "\n")

def main():
    print_header()
    
    # Muda para diretório de testes
    test_dir = Path(__file__).parent
    os.chdir(test_dir)
    
    # Constrói comando pytest
    cmd = ["pytest", "test_suite.py"]
    
    # Processa argumentos
    args = sys.argv[1:]
    
    # Defaults
    verbose = True
    
    for arg in args:
        if arg == "-q":
            cmd.append("--tb=no")
            cmd.append("-q")
            verbose = False
        elif arg == "-v":
            cmd.extend(["-vv", "-s"])
        elif arg == "-c":
            cmd.extend(["--cov=.", "--cov-report=html"])
        elif arg == "-h" or arg == "--help":
            print(__doc__)
            return 0
        else:
            # Assume que é um nome de teste/classe
            cmd.append(f"::{arg}" if "::" not in arg else arg)
    
    # Adiciona verbose padrão se nenhuma flag foi usada
    if verbose and "-q" not in args and "-v" not in args:
        cmd.append("-v")
    
    # Adiciona tb short por padrão
    if "--tb" not in " ".join(cmd):
        cmd.append("--tb=short")
    
    # Imprime comando executado
    print(f"📋 Executando: {' '.join(cmd)}\n")
    print(f"📁 Diretório: {test_dir}\n")
    print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    print("-" * 80 + "\n")
    
    # Executa testes
    result = subprocess.run(cmd)
    
    # Imprime resumo
    print_summary(result.returncode)
    
    # Localiza arquivo de log
    log_dir = test_dir / "logs"
    if log_dir.exists():
        latest_log = sorted(log_dir.glob("test_results_*.log"))[-1] if list(log_dir.glob("test_results_*.log")) else None
        if latest_log:
            print(f"📝 Log salvo em: {latest_log}\n")
            print(f"💡 Dica: grep '✅ SUCESSO' {latest_log}  # Ver testes que passaram")
            print(f"💡 Dica: grep '❌ ERRO' {latest_log}     # Ver testes que falharam\n")
    
    # Se cobertura foi gerada
    if "-c" in args:
        coverage_dir = test_dir / "htmlcov" / "index.html"
        if coverage_dir.exists():
            print(f"📊 Relatório de cobertura: {coverage_dir}\n")
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
