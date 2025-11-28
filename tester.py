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
    
    # Look for Python files (excluding tester.py)
    py_files = [f for f in os.listdir('.') if f.endswith('.py') and f != 'tester.py']
    
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
        EXEC = f"python3 {filename}"


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
    
    # Look for Python files
    py_files = [f for f in os.listdir('.') if f.endswith('.py') and f != 'tester.py']
    if py_files:
        SOURCE_FILE = py_files[0]  # Use the first one found
        EXEC = f"python3 {SOURCE_FILE}"
        FILE_TYPE = "py"
        return
    
    print("Erro: Nenhum arquivo .cpp ou .py encontrado!")
    sys.exit(1)


def compile_cpp(benchmark_enabled):
    print("Compilando...", end=" ")

    cmd = ["g++", "-O2", "-std=c++17", SOURCE_FILE]

    # adiciona flag -DBENCHMARK se habilitado
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


def run_test(input_path, expected_path):
    # roda o programa
    with open(input_path, "r") as f_in:
        if FILE_TYPE == "cpp":
            result = subprocess.run(EXEC, stdin=f_in, capture_output=True, text=True)
        elif FILE_TYPE == "py":
            result = subprocess.run(["python3", SOURCE_FILE], stdin=f_in, capture_output=True, text=True)
        else:
            return ("ERROR", "Tipo de arquivo não suportado")

    # Output stderr to stderr (will be captured by main function)
    if result.stderr.strip():
        print("=== STDERR ===", file=sys.stderr)
        print(result.stderr.strip(), file=sys.stderr)
        print("==============", file=sys.stderr)

    if result.returncode != 0:
        return ("RUNTIME ERROR", result.stderr)

    # lê referência
    with open(expected_path, "r") as f_exp:
        expected = f_exp.read().strip()

    output = result.stdout.strip()

    # tentativa: comparar doubles com margem de 1%
    try:
        out_vals = [float(x) for x in output.split()]
        exp_vals = [float(x) for x in expected.split()]

        if len(out_vals) != len(exp_vals):
            return ("WA", f"Número de valores diferente.\nEsperado: {expected}\nObtido: {output}")

        for o, e in zip(out_vals, exp_vals):
            erro = abs(o - e)
            margem = 0.01 * abs(e)

            if erro > margem:
                return ("WA",
                        f"Valor fora da margem de erro de 1%.\n"
                        f"Esperado: {e}\nObtido: {o}\n"
                        f"Erro: {erro}\nMargem permitida: {margem}")

        return ("OK", f"Esperado: {expected}\nObtido: {output}")

    except ValueError:
        # fallback: comparação literal
        if output == expected:
            return ("OK", f"Esperado: {expected}\nObtido: {output}")
        else:
            return ("WA", f"Esperado:\n{expected}\n\nObtido:\n{output}")


def run_tests_for_file(source_file, file_type, benchmark_enabled, output_buffer):
    """Run all tests for a specific source file and write results to buffer."""
    set_current_file(source_file, file_type)
    
    output_buffer.write(f"=== TESTING {source_file} ({file_type.upper()}) ===\n")
    output_buffer.write(f"SOURCE_FILE = {SOURCE_FILE} ({FILE_TYPE.upper()})\n\n")
    
    # Prepare execution
    try:
        prepare_execution(benchmark_enabled)
        output_buffer.write("Preparação concluída com sucesso.\n\n")
    except SystemExit:
        output_buffer.write("ERRO na preparação do arquivo.\n\n")
        return
    
    # Get test files
    files = sorted(f for f in os.listdir(INPUT_DIR) if f.endswith(".in"))
    if not files:
        output_buffer.write("Nenhum arquivo .in encontrado.\n")
        return
    
    output_buffer.write(f"Testando {len(files)} casos...\n\n")
    
    # Run tests
    for fname in files:
        in_path = os.path.join(INPUT_DIR, fname)
        out_path = os.path.join(OUTPUT_DIR, fname.replace(".in", ".out"))
        
        if not os.path.exists(out_path):
            output_buffer.write(f"{fname}: ARQUIVO {out_path} NÃO ENCONTRADO\n")
            continue
        
        output_buffer.write(f"--- Rodando {fname} ---\n")
        
        # Capture stderr separately for this test
        original_stderr = sys.stderr
        stderr_buffer = StringIO()
        sys.stderr = stderr_buffer
        
        try:
            status, msg = run_test(in_path, out_path)
        finally:
            sys.stderr = original_stderr
            stderr_content = stderr_buffer.getvalue()
        
        if status == "OK":
            output_buffer.write(f"{fname}: ✔ OK\n")
            if msg:  # Show output even when OK
                output_buffer.write(f"{msg}\n")
        else:
            output_buffer.write(f"{fname}: ✘ {status}\n")
            output_buffer.write(f"{msg}\n")
            output_buffer.write("-" * 40 + "\n")
        
        # Add stderr content if present
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
    
    # Ask for benchmark mode (applies to all C++ files)
    ans = input("Benchmark mode for C++ files? (y/n): ").strip().lower()
    benchmark_enabled = (ans == "y")
    
    # Test each file
    for source_file, file_type in all_source_files:
        print(f"\n{'='*60}")
        print(f"TESTING {source_file} ({file_type.upper()})")
        print('='*60)
        
        # Create output buffer
        output_buffer = StringIO()
        
        # Run tests for this file
        current_benchmark = benchmark_enabled if file_type == "cpp" else False
        run_tests_for_file(source_file, file_type, current_benchmark, output_buffer)
        
        # Write results to file
        output_filename = f"tests{os.path.splitext(source_file)[0]}.txt"
        with open(output_filename, 'w') as f:
            f.write(output_buffer.getvalue())
        
        print(f"Resultados salvos em: {output_filename}")
        
        # Also print summary to console
        results = output_buffer.getvalue()
        print("\nResumo dos testes:")
        for line in results.split('\n'):
            if ': ✔ OK' in line or ': ✘' in line:
                print(f"  {line}")
    
    print(f"\n{'='*60}")
    print("TODOS OS TESTES CONCLUÍDOS")
    print('='*60)


if __name__ == "__main__":
    main()
