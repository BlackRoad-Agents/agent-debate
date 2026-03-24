#!/usr/bin/env python3
"""
BlackRoad Multi-Agent Debate Engine
Orchestrates structured debates between agents via Ollama.
"""

import json
import sys
import subprocess
import argparse
from datetime import datetime


DEFAULT_PERSONAS = {
    "road": "You are Road, the fleet commander. You think strategically about systems and coordination.",
    "coder": "You are Coder, a pragmatic software engineer. You care about working code and clean architecture.",
    "scholar": "You are Scholar, a researcher. You value evidence, nuance, and intellectual rigor.",
    "pascal": "You are Pascal, a mathematician. You think in proofs, patterns, and formal logic.",
    "writer": "You are Writer, a clear communicator. You value concise, precise language.",
    "cipher": "You are Cipher, a security specialist. You think about threats, trust, and defense in depth.",
    "tutor": "You are Tutor, an educator. You value clarity, accessibility, and understanding.",
    "alice": "You are Alice, a network operations specialist. You think in packets, routes, and uptime.",
    "cecilia": "You are Cecilia, an AI inference specialist. You think about models, embeddings, and compute.",
    "octavia": "You are Octavia, a DevOps engineer. You think about pipelines, containers, and reliability.",
    "lucidia": "You are Lucidia, a web hosting specialist. You care about sites, DNS, and serving content.",
    "aria": "You are Aria, a monitoring specialist. You watch systems and detect anomalies.",
}

DEFAULT_MODEL = "llama3.2"
OLLAMA_HOST = "http://localhost:11434"


def query_ollama(model, system_prompt, user_prompt, host=OLLAMA_HOST):
    """Query Ollama and return the response text."""
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False
    })

    try:
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", f"{host}/api/chat",
             "-H", "Content-Type: application/json",
             "-d", payload],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            return f"[Error: Ollama request failed: {result.stderr.strip()}]"

        data = json.loads(result.stdout)
        return data.get("message", {}).get("content", "[No response]")
    except subprocess.TimeoutExpired:
        return "[Error: Ollama request timed out after 120s]"
    except json.JSONDecodeError:
        return f"[Error: Invalid JSON response from Ollama]"
    except Exception as e:
        return f"[Error: {str(e)}]"


def load_personas(personas_file=None):
    """Load personas from file or use defaults."""
    if personas_file:
        try:
            with open(personas_file) as f:
                data = json.load(f)
            return {p["id"]: p["persona"] for p in data.get("personas", [])}
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            pass
    return DEFAULT_PERSONAS


def run_debate(topic, agent_ids, rounds=3, model=DEFAULT_MODEL,
               personas_file=None, host=OLLAMA_HOST):
    """
    Run a structured debate between agents.

    Args:
        topic: The debate topic or question
        agent_ids: List of 2-4 agent IDs to participate
        rounds: Number of debate rounds (default 3)
        model: Ollama model to use
        personas_file: Optional path to personas.json
        host: Ollama API host

    Returns:
        dict with debate transcript and metadata
    """
    personas = load_personas(personas_file)
    valid_agents = []
    for aid in agent_ids:
        if aid in personas:
            valid_agents.append(aid)
        else:
            print(f"Warning: Unknown agent '{aid}', skipping.", file=sys.stderr)

    if len(valid_agents) < 2:
        return {"error": "Need at least 2 valid agents for a debate."}

    transcript = {
        "topic": topic,
        "agents": valid_agents,
        "model": model,
        "rounds": rounds,
        "started_at": datetime.utcnow().isoformat() + "Z",
        "exchanges": []
    }

    # Round 0: Opening statements
    print(f"\n--- DEBATE: {topic} ---")
    print(f"--- Agents: {', '.join(valid_agents)} | Rounds: {rounds} ---\n")

    opening_statements = {}
    for agent_id in valid_agents:
        system = personas[agent_id]
        prompt = (
            f"You are participating in a structured debate on this topic: {topic}\n\n"
            f"Give your opening position in 2-3 paragraphs. Be specific and direct. "
            f"State your stance clearly."
        )
        print(f"[{agent_id}] Generating opening statement...")
        response = query_ollama(model, system, prompt, host)
        opening_statements[agent_id] = response

        transcript["exchanges"].append({
            "round": 0,
            "type": "opening",
            "agent": agent_id,
            "content": response
        })
        print(f"\n  {agent_id.upper()}: {response[:200]}...\n")

    # Debate rounds: each agent responds to the previous statements
    for round_num in range(1, rounds + 1):
        print(f"\n--- Round {round_num}/{rounds} ---\n")

        round_responses = {}
        for agent_id in valid_agents:
            # Build context from other agents' most recent statements
            others_said = []
            for other_id in valid_agents:
                if other_id == agent_id:
                    continue
                # Get most recent statement from this agent
                last = None
                for ex in reversed(transcript["exchanges"]):
                    if ex["agent"] == other_id:
                        last = ex["content"]
                        break
                if last:
                    others_said.append(f"{other_id.upper()} said: {last}")

            context = "\n\n".join(others_said)
            system = personas[agent_id]
            prompt = (
                f"Debate topic: {topic}\n\n"
                f"This is round {round_num} of {rounds}. "
                f"Here is what the other participants said:\n\n"
                f"{context}\n\n"
                f"Respond to their points directly. Agree where valid, "
                f"challenge where you disagree. Be specific. Keep to 2-3 paragraphs."
            )

            print(f"[{agent_id}] Generating round {round_num} response...")
            response = query_ollama(model, system, prompt, host)
            round_responses[agent_id] = response

            transcript["exchanges"].append({
                "round": round_num,
                "type": "response",
                "agent": agent_id,
                "content": response
            })
            print(f"\n  {agent_id.upper()}: {response[:200]}...\n")

    # Closing: each agent summarizes their final position
    print(f"\n--- Closing Statements ---\n")
    for agent_id in valid_agents:
        system = personas[agent_id]
        all_points = [
            ex["content"] for ex in transcript["exchanges"]
            if ex["agent"] != agent_id
        ]
        summary_context = "\n".join(all_points[-len(valid_agents):])

        prompt = (
            f"The debate on '{topic}' is concluding.\n\n"
            f"Summarize your final position in 1-2 paragraphs. "
            f"Acknowledge any points from others that changed your thinking. "
            f"State your conclusion clearly."
        )

        print(f"[{agent_id}] Generating closing statement...")
        response = query_ollama(model, system, prompt, host)

        transcript["exchanges"].append({
            "round": rounds + 1,
            "type": "closing",
            "agent": agent_id,
            "content": response
        })
        print(f"\n  {agent_id.upper()}: {response[:200]}...\n")

    transcript["ended_at"] = datetime.utcnow().isoformat() + "Z"
    transcript["total_exchanges"] = len(transcript["exchanges"])

    return transcript


def main():
    parser = argparse.ArgumentParser(description="BlackRoad Multi-Agent Debate Engine")
    parser.add_argument("topic", help="The debate topic or question")
    parser.add_argument("--agents", nargs="+", default=["coder", "scholar"],
                        help="Agent IDs to participate (2-4)")
    parser.add_argument("--rounds", type=int, default=3,
                        help="Number of debate rounds (default: 3)")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help="Ollama model to use (default: llama3.2)")
    parser.add_argument("--personas", default=None,
                        help="Path to personas.json file")
    parser.add_argument("--host", default=OLLAMA_HOST,
                        help="Ollama API host")
    parser.add_argument("--output", default=None,
                        help="Output file for JSON transcript")

    args = parser.parse_args()

    if len(args.agents) < 2:
        print("Error: Need at least 2 agents.", file=sys.stderr)
        sys.exit(1)
    if len(args.agents) > 4:
        print("Error: Maximum 4 agents per debate.", file=sys.stderr)
        sys.exit(1)

    transcript = run_debate(
        topic=args.topic,
        agent_ids=args.agents,
        rounds=args.rounds,
        model=args.model,
        personas_file=args.personas,
        host=args.host
    )

    if "error" in transcript:
        print(f"Error: {transcript['error']}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(transcript, f, indent=2)
        print(f"\nTranscript saved to {args.output}")
    else:
        print("\n--- Full Transcript (JSON) ---")
        print(json.dumps(transcript, indent=2))


if __name__ == "__main__":
    main()
