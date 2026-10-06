Demo Link:https://crewai-debateproject.onrender.com
# CrewAI Debate Project

This repository contains a **multi-agent debate simulation** built using **CrewAI**, where two debater agents argue for and against a motion, and a judge agent evaluates the arguments to decide the winner.

---

## 🏗 Project Structure


<img width="1024" height="1536" alt="image" src="https://github.com/user-attachments/assets/0f32589c-01ab-4c7f-a759-c825d92c7d26" />


main.py → crew.py → Debate.crew()

Crew = [
  Task(propose by debater),
  Task(oppose by debater),
  Task(decide by judge)
]

Execution Order:
1️⃣ Debater (for)   → output/propose.md  
2️⃣ Debater (against) → output/oppose.md  
3️⃣ Judge evaluates  → output/decide.md  

→ Console prints final decision (result.raw)

debate_project/
│
├── config/
│ ├── agents.yaml # Agent definitions (roles, LLM models, backstory)
│ ├── tasks.yaml # Task definitions for each agent (propose, oppose, decide)
│
├── debate/
│ ├── crew.py # Crew runtime script for local execution
│ ├── crew/
│ ├── init.py
│ ├── debate.py # CrewBase class defining agents, tasks, and crew orchestration
│
├── output/
│ ├── propose.md # Generated argument in favor
│ ├── oppose.md # Generated argument against
│ ├── decide.md # Judge’s final verdict
│
├── main.py # Entry point to run the crew
└── requirements.txt



---

## ⚙️ Installation

1. Clone the repository:
```bash
git clone https://github.com/prasanna14200/crewai_debateproject.git
cd crewai-debate

2.Create a virtual environment:
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows

3.Install dependencies:


pip install -r requirements.txt

Set environment variables (for OpenAI or Anthropic API keys):

export OPENAI_API_KEY="your_openai_key"
export ANTHROPIC_API_KEY="your_anthropic_key"
or use opensource models for no cost.



🚀 Running the Debate Crew

crewai run



🧠 How It Works

Agents & Tasks

Agents are defined in agents.yaml (Debater, Judge).

Tasks are defined in tasks.yaml (Propose, Oppose, Decide).

CrewBase

debate.py connects the YAML configuration to CrewAI agents and tasks.

Crew Execution Engine

Executes tasks sequentially: Propose → Oppose → Decide.

Saves outputs to markdown files and prints the final verdict.

📈 Real-Time Use Cases

AI debating research (simulating reasoning & argumentation)

Multi-agent evaluation pipelines (content moderation, automated QA)

Automated red teaming & critique workflows

📝 Notes

Change the motion dynamically by editing inputs in crew.py or main.py.

Swap LLM models in agents.yaml without touching the code.

Verbose logs can be enabled for debugging agent reasoning.



# Debate Crew

Welcome to the Debate Crew project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ crewai run
```
This command initializes the debate Crew, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

## Understanding Your Crew

The debate Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the Debate Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)


📫 Contact

Created by prasanna
Email: prasannaprasanna14200@gmail.com

Let's create wonders together with the power and simplicity of crewAI.

