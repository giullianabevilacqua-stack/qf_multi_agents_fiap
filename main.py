"""
Quantum Finance — Ponto de Entrada Principal (Terminal)

Como executar:
  # Interface web interativa (recomendado para demo/vídeo):
  cd quantum_finance   # pasta raiz do projeto (onde este main.py está)
  adk web
  # Acesse http://localhost:8000 e selecione o agente: quantum_finance

  # Terminal interativo:
  python main.py
"""

import os
import sys
import asyncio

# Garante que o pacote quantum_finance seja encontrado
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from quantum_finance.agents.lead_advisor import root_agent

APP_NAME = "quantum_finance"
USER_ID = "cliente_quantum"


async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
    )

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    print("\n" + "═" * 60)
    print("  💼  QUANTUM FINANCE — Consultor Financeiro IA")
    print("  Powered by Google ADK + Gemini 2.0 Flash")
    print("  FIAP MBA — Intelligent Multi Agents")
    print("═" * 60)
    print("  Digite 'sair' para encerrar.\n")

    async def enviar(mensagem: str) -> str:
        content = types.Content(
            role="user",
            parts=[types.Part(text=mensagem)],
        )
        resposta = ""
        async for evento in runner.run_async(
            user_id=USER_ID,
            session_id=session.id,
            new_message=content,
        ):
            if evento.is_final_response():
                if evento.content and evento.content.parts:
                    resposta = evento.content.parts[0].text
        return resposta

    # Boas-vindas automáticas
    boas_vindas = await enviar(
        "Olá! Apresente-se brevemente como consultor da Quantum Finance "
        "e explique como pode ajudar o cliente hoje."
    )
    print(f"🤖 Quantum Finance:\n{boas_vindas}\n")

    while True:
        try:
            entrada = input("👤 Você: ").strip()
            if not entrada:
                continue
            if entrada.lower() in ("sair", "exit", "quit"):
                print("\n👋 Obrigado por usar a Quantum Finance. Até logo!\n")
                break

            print("\n⏳ Processando...\n")
            resposta = await enviar(entrada)
            print(f"🤖 Quantum Finance:\n{resposta}\n")
            print("─" * 60)

        except KeyboardInterrupt:
            print("\n\n👋 Sessão encerrada. Até logo!\n")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())
