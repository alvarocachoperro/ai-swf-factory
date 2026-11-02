import os
from openai import OpenAI
from dotenv import load_dotenv

# Cargamos variables de entorno (por si usas un fichero .env con tu API Key)
load_dotenv()

# Inicializamos el cliente de OpenAI (puedes cambiar la base URL si usas Ollama/local o Anthropic)
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # Ollama no pide key real pero el SDK exige un string
)


def read_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def run_agent():
    print("🤖 [AI Agent] Leyendo especificaciones y código fuente...")

    # 1. Leemos la tarea y el código actual del mock_repo
    task_description = read_file("task.md")
    current_code = read_file("mock_repo/src/Calculator.java")

    # 2. Definimos el Prompt del Sistema (las directrices del rol de la IA)
    system_prompt = (
        "Eres un ingeniero de software senior experto en refactorización y desarrollo backend. "
        "Tu objetivo es leer una tarea de desarrollo y el código actual de un fichero, "
        "y devolver únicamente el código actualizado y completo cumpliendo con los requisitos, "
        "sin explicaciones adicionales, en un bloque de código limpio."
    )

    user_prompt = f"""
    ESTA ES LA TAREA A REALIZAR:
    {task_description}

    ESTE ES EL CÓDIGO ACTUAL (Calculator.java):
    {current_code}

    Por favor, genera la versión actualizada completa de Calculator.java aplicando los cambios requeridos.
    """

    print("🧠 [AI Agent] Analizando y generando la propuesta con el LLM...")

    # 3. Llamada al modelo
    response = client.chat.completions.create(
        model="qwen2.5-coder:7b",  # O el modelo que prefieras usar
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1  # Baja temperatura para que sea más determinista y técnico
    )

    proposed_code = response.choices[0].message.content

    # Limpiamos los bloques de código markdown si los trae la respuesta
    proposed_code = proposed_code.replace("```java", "").replace("```", "").strip()

    # 4. Guardamos la propuesta en un fichero temporal o directamente sobreescribimos (por ahora lo guardamos como propuesta)
    output_path = "mock_repo/src/Calculator.java"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(proposed_code)

    print(f"✅ [AI Agent] ¡Propuesta aplicada en {output_path}!")


if __name__ == "__main__":
    run_agent()