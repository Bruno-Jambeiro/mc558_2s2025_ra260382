import subprocess
import os
import sys
from io import StringIO

# Will be set based on available files
SOURCE_FILE = None
EXEC = None
FILE_TYPE = None
INPUT_DIR = "input"
OUTPUT_DIR = "output"

def detect_all_source_files():
    """Detect all source files to test."""
    # Look for C++ files
    cpp_files = [f for f in os.listdir('.') if f.endswith('.cpp')]
    
    # Look for Python files (excluding tester.py, case-insensitive)
    py_files = [
        f for f in os.listdir('.')
        if f.endswith('.py') and os.path.basename(f).lower() != 'tester.py'
    ]

    all_files = []
    for f in cpp_files:
        all_files.append((f, "cpp"))
    for f in py_files:
        all_files.append((f, "py"))
    
    if not all_files:
        print("Erro: Nenhum arquivo .cpp ou .py encontrado!")
        sys.exit(1)
    
    return all_files


def set_current_file(filename, filetype):
    """Set the current file to test."""
    global SOURCE_FILE, EXEC, FILE_TYPE
    SOURCE_FILE = filename
    FILE_TYPE = filetype
    if filetype == "cpp":
        EXEC = "./a.out"
    else:
        # Use the running Python interpreter for portability on Windows
        EXEC = f"{sys.executable} {filename}"


def detect_source_file():
    """Detect the source file to use based on available files."""
    global SOURCE_FILE, EXEC, FILE_TYPE
    
    # Look for C++ files first
    cpp_files = [f for f in os.listdir('.') if f.endswith('.cpp')]
    if cpp_files:
        SOURCE_FILE = cpp_files[0]  # Use the first one found
        EXEC = "./a.out"
        FILE_TYPE = "cpp"
        return
    
    # Look for Python files (excluding tester.py, case-insensitive)
    py_files = [
        f for f in os.listdir('.')
        if f.endswith('.py') and os.path.basename(f).lower() != 'tester.py'
    ]
    if py_files:
        SOURCE_FILE = py_files[0]  # Use the first one found
        EXEC = f"{sys.executable} {SOURCE_FILE}"
        FILE_TYPE = "py"
        return
    
    print("Erro: Nenhum arquivo .cpp ou .py encontrado!")
    sys.exit(1)


def compile_cpp(benchmark_enabled):
    print("Compilando...", end=" ")
    # use output file a.out explicitly
    cmd = ["g++", "-O2", "-std=c++17", "-o", "a.out", SOURCE_FILE]
    if benchmark_enabled:
        cmd.append("-DBENCHMARK")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("ERRO")
        print(r.stderr)
        sys.exit(1)
    print("OK")


def prepare_execution(benchmark_enabled):
    """Prepare for execution based on file type."""
    if FILE_TYPE == "cpp":
        compile_cpp(benchmark_enabled)
    elif FILE_TYPE == "py":
        print("Arquivo Python detectado - nenhuma compilação necessária")
    else:
        print("Tipo de arquivo não suportado!")
        sys.exit(1)


def run_test(input_path, expected_path, benchmark_enabled):
    with open(input_path, "r") as f_in:
        if FILE_TYPE == "cpp":
            result = subprocess.run("./a.out", stdin=f_in, capture_output=True, text=True)
        elif FILE_TYPE == "py":
            cmd = [sys.executable, SOURCE_FILE]
            if benchmark_enabled:
                cmd.append("--benchmark")
            result = subprocess.run(cmd, stdin=f_in, capture_output=True, text=True)
        else:
            return ("ERROR", "Tipo de arquivo não suportado")
    if result.stderr.strip():
        print("=== STDERR ===", file=sys.stderr)
        print(result.stderr.strip(), file=sys.stderr)
        print("==============", file=sys.stderr)
    if result.returncode != 0:
        return ("RUNTIME ERROR", result.stderr)
    with open(expected_path, "r") as f_exp:
        expected_raw = f_exp.read().strip()
    output_raw = result.stdout.strip()
    # Attempt numeric comparison extracting only float tokens
    def extract_floats(text):
        floats = []
        for tok in text.split():
            try:
                floats.append(float(tok))
            except ValueError:
                continue
        return floats
    exp_nums = extract_floats(expected_raw)
    out_nums = extract_floats(output_raw)
    if exp_nums and out_nums:
        if len(exp_nums) != len(out_nums):
            return ("WA", f"Número de valores diferente.\nEsperado: {expected_raw}\nObtido: {output_raw}")
        for o, e in zip(out_nums, exp_nums):
            erro = abs(o - e)
            margem = 0.01 * abs(e)  # 1% margin
            if erro > margem:
                return ("WA", f"Valor fora da margem de erro de 1%.\nEsperado: {e}\nObtido: {o}\nErro: {erro}\nMargem permitida: {margem}")
        return ("OK", f"Esperado: {exp_nums}\nObtido: {out_nums}")
    # Fallback string compare when no numeric tokens
    if output_raw == expected_raw:
        return ("OK", f"Esperado: {expected_raw}\nObtido: {output_raw}")
    else:
        return ("WA", f"Esperado:\n{expected_raw}\n\nObtido:\n{output_raw}")


def run_tests_for_file(source_file, file_type, benchmark_enabled, output_buffer):
    if os.path.basename(source_file).lower() == 'tester.py':
        return
    set_current_file(source_file, file_type)
    ft_display = (FILE_TYPE or '').upper()
    output_buffer.write(f"=== TESTING {source_file} ({ft_display}) ===\n")
    output_buffer.write(f"SOURCE_FILE = {SOURCE_FILE} ({ft_display})\n\n")
    try:
        prepare_execution(benchmark_enabled)
        output_buffer.write("Preparação concluída com sucesso.\n\n")
    except SystemExit:
        output_buffer.write("ERRO na preparação do arquivo.\n\n")
        return
    files = sorted(f for f in os.listdir(INPUT_DIR) if f.endswith(".in"))
    if not files:
        output_buffer.write("Nenhum arquivo .in encontrado.\n")
        return
    output_buffer.write(f"Testando {len(files)} casos...\n\n")
    for fname in files:
        in_path = os.path.join(INPUT_DIR, fname)
        out_path = os.path.join(OUTPUT_DIR, fname.replace(".in", ".out"))
        if not os.path.exists(out_path):
            output_buffer.write(f"{fname}: ARQUIVO {out_path} NÃO ENCONTRADO\n")
            continue
        output_buffer.write(f"--- Rodando {fname} ---\n")
        original_stderr = sys.stderr
        stderr_buffer = StringIO()
        sys.stderr = stderr_buffer
        try:
            status, msg = run_test(in_path, out_path, benchmark_enabled)
        finally:
            sys.stderr = original_stderr
            stderr_content = stderr_buffer.getvalue()
        if status == "OK":
            output_buffer.write(f"{fname}: ✔ OK\n")
            if msg:
                output_buffer.write(f"{msg}\n")
        else:
            output_buffer.write(f"{fname}: ✘ {status}\n")
            output_buffer.write(f"{msg}\n")
            output_buffer.write("-" * 40 + "\n")
        if stderr_content.strip():
            output_buffer.write("=== STDERR ===\n")
            output_buffer.write(stderr_content)
            output_buffer.write("==============\n")
        output_buffer.write("\n")


def main():
    all_source_files = detect_all_source_files()
    
    print(f"Encontrados {len(all_source_files)} arquivos para testar:")
    for filename, filetype in all_source_files:
        print(f"  - {filename} ({filetype.upper()})")
    print()
    
    ans = input("Benchmark mode? (y/n): ").strip().lower()
    benchmark_enabled = (ans == "y")
    
    for source_file, file_type in all_source_files:
        if os.path.basename(source_file).lower() == 'tester.py':
            continue

        print(f"\n{'='*60}")
        print(f"TESTING {source_file} ({file_type.upper()})")
        print('='*60)
        
        output_buffer = StringIO()
        
        current_benchmark = benchmark_enabled  # agora aplica também para Python
        run_tests_for_file(source_file, file_type, current_benchmark, output_buffer)
        
        output_filename = f"tests{os.path.splitext(source_file)[0]}.txt"
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(output_buffer.getvalue())
        
        print(f"Resultados salvos em: {output_filename}")
        
        print("\nResumo dos testes:")
        results = output_buffer.getvalue()
        for line in results.split('\n'):
            if ': ✔ OK' in line or ': ✘' in line:
                print(f"  {line}")
    
    print(f"\n{'='*60}")
    print("TODOS OS TESTES CONCLUÍDOS")
    print('='*60)


if __name__ == "__main__":
    main()
