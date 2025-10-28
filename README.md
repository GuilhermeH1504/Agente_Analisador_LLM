# Agente_Analisador_LLM
Sistema de analise de curriculos

**AI Recruiter** é uma aplicação inteligente desenvolvida em Python que utiliza **LLMs (Large Language Models)** para **analisar currículos automaticamente**, identificar **pontos fortes e fracos**, e gerar uma **avaliação detalhada do candidato**.

O projeto demonstra o uso prático de **Inteligência Artificial aplicada a RH**, combinando processamento de linguagem natural com integração via **LangChain** e **LangGraph**.
---
## 🚀 Funcionalidades

- 📄 **Leitura automática de currículos em PDF**
- 🧠 **Análise inteligente de conteúdo** usando LLMs
- 💬 **Geração de feedback detalhado** sobre habilidades e pontos de melhoria
- 🧩 **Integração com LangChain e LangGraph**
- ⚙️ **Arquitetura modular e escalável**
- 🧾 **Resultados exibidos de forma clara e didática**
---
## 🧠 Tecnologias Utilizadas

| Categoria | Tecnologias |
|------------|--------------|
| Linguagem | Python 3.11+ |
| IA / LLM | LangChain, LangGraph, Groq |
| Leitura de PDF | PyMuPDF (fitz) |
| Ambiente | Virtualenv ou venv |
| Banco de Dados (opcional) | SQLModel / SQLite |

---

## 📂 Estrutura do Projeto

```
AI-Recruiter/
│
├── data/                     # Pasta com currículos em PDF
├── tools/                    # Funções auxiliares (ex: leitura, parsing)
├── ai_recruiter.py           # Lógica principal da IA
├── requirements.txt          # Dependências do projeto
├── README.md                 # Documentação do projeto
└── main.py                   # Ponto de entrada do sistema
```

---

## ⚙️ Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seuusuario/AI-Recruiter.git
   cd AI-Recruiter
   ```

2. Crie e ative o ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate     # Linux/Mac
   venv\Scripts\activate        # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure sua **API Key** (Groq ou OpenAI, dependendo do LLM usado):
   ```bash
   export GROQ_API_KEY="sua_chave_aqui"
   ```
   ou no Windows:
   ```bash
   set GROQ_API_KEY="sua_chave_aqui"
   ```

---

## ▶️ Como Usar

1. Coloque os currículos em PDF dentro da pasta `data/`.
2. Execute o projeto:
   ```bash
   python main.py
   ```
3. O AI Recruiter fará:
   - Leitura automática dos currículos
   - Interpretação dos dados
   - Geração de uma análise inteligente

4. O resultado será exibido no terminal e salvo no arquivo `resultado.txt` (opcional).

---

## 💡 Exemplo de Saída

```
Análise de Currículo – Guilherme Henrique Souza Faria

Pontos Fortes:
• Experiência com Python e SQLModel
• Conhecimento em LLMs e LangChain
• Capacidade de automação de processos

Pontos de Melhoria:
• Maior aprofundamento em engenharia de prompts
• Aprimorar documentação técnica em projetos abertos

Avaliação Geral:
Candidato com ótimo potencial para áreas de IA e automação.
```
---
## 🧩 Próximos Passos

- [ ] Criar uma interface web com FastAPI
- [ ] Integrar banco de dados SQLModel para armazenar análises
- [ ] Adicionar análise comparativa entre candidatos
- [ ] Implementar busca de vagas compatíveis via IA

---

## 👨‍💻 Desenvolvido por

**Guilherme Henrique Souza Faria**
💼 Desenvolvedor Python | Focado em IA, Automação e LLMs
📧 [adicione seu e-mail profissional ou LinkedIn aqui]

---

## ⭐ Contribuição

Se quiser contribuir com o projeto:
1. Faça um fork
2. Crie uma branch: `git checkout -b feature-nome`
3. Envie um pull request 🚀

---

## 📜 Licença

Este projeto é distribuído sob a licença MIT.
Sinta-se livre para usar, estudar e aprimorar.

