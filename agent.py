import os
import subprocess
from openai import OpenAI

# Inicializamos el cliente apuntando a Ollama local
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)


def read_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def compile_and_test() -> tuple[bool, str]:
    """Compila y ejecuta los tests de Java para validar el código generado."""
    print("🛡️ [Guardián] Validando compilación y tests...")

    try:
        # 1. Compilar las clases dentro del mock_repo
        compile_process = subprocess.run(
            ["javac", "src/com/factory/mock/Calculator.java", "src/com/factory/mock/CalculatorTest.java"],
            cwd="mock_repo",
            capture_output=True,
            text=True
        )

        if compile_process.returncode != 0:
            error_msg = f"ERROR DE COMPILACIÓN:\n{compile_process.stderr}"
            return False, error_msg

        # 2. Ejecutar el test unitario
        run_process = subprocess.run(
            ["java", "-cp", "src", "com.factory.mock.CalculatorTest"],
            cwd="mock_repo",
            capture_output=True,
            text=True
        )

        if run_process.returncode != 0:
            error_msg = f"ERROR EN LOS TESTS:\n{run_process.stderr}\n{run_process.stdout}"
            return False, error_msg

        return True, "¡Compilación y tests exitosos!"

    except Exception as e:
        return False, f"Excepción ejecutando comandos del sistema: {str(e)}"


def run_agent():
    print("🤖 [AI Agent Local] Iniciando ciclo de la Factoría...")

    task_description = read_file("mock_repo/task.md")
    current_code = read_file("mock_repo/src/com/factory/mock/Calculator.java")

    system_prompt = (
        "Eres un ingeniero de software senior experto en desarrollo backend en Java. "
        "Tu objetivo es leer una tarea y el código actual, y devolver únicamente el código "
        "actualizado y completo cumpliendo con los requisitos, sin explicaciones adicionales, "
        "en un bloque de código limpio."
    )

    user_prompt = f"""
    ESTA ES LA TAREA A REALIZAR:
    {task_description}

    ESTE ES EL CÓDIGO ACTUAL (Calculator.java):
    {current_code}

    Por favor, genera la versión actualizada completa de Calculator.java aplicando los cambios requeridos.
    """

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        print(f"🧠 [Intento {attempt}/{max_retries}] Generando código con el LLM local...")

        response = client.chat.completions.create(
            model="qwen2.5:1.5b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1
        )

        proposed_code = response.choices[0].message.content
        proposed_code = proposed_code.replace("```java", "").replace("```", "").strip()

        output_path = "mock_repo/src/com/factory/mock/Calculator.java"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(proposed_code)

        # Ejecutamos el Guardián de Calidad
        success, message = compile_and_test()

        if success:
            print(f"✅ [Éxito] {message}")
            break
        else:
            print(f"❌ [Falló la validación]:\n{message}")
            if attempt < max_retries:
                print("🔄 Reintentando enviando el error al agente para corrección...")
                # Alimentamos el feedback del error al prompt del usuario para el siguiente intento
                user_prompt += f"\n\nATENCIÓN: Tu intento anterior falló con este error de compilación/test:\n{message}\nPor favor, corrígelo."
            else:
                print("🚨 Se han agotado los intentos máximos sin pasar la validación.")


if __name__ == "__main__":
    run_agent()