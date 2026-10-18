#!/usr/bin/env python3
"""
EverReach Sora Prompt Generator
Generates video ad scripts for each awareness level using OpenAI
"""

import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SORA_CORE = """format 9:16 vertical
duration 55 to 60 seconds
style natural phone camera ugc modern clean high contrast
main character late 20s to late 30s founder operator consultant vibe
setting home office coworking space
editing quick jump cuts with overlays
end card EverReach start with 1 person try it free"""

AWARENESS_CONFIGS = {
    "unaware": {
        "code": "UA",
        "goal": "Make the invisible problem visible without naming follow-up directly",
        "product_reveal": "Last 8-10 seconds only",
        "modules": ["pattern_interrupt", "emotional_insight", "micro_habit", "soft_reveal"],
        "predicted_cpc": "$0.40-$0.80",
        "predicted_cac": "$25-$45",
        "angles": [
            {"belief": "too_busy", "hook": "timing as enemy", "frame": "drift/distance"},
            {"belief": "too_busy", "hook": "one minute habit", "frame": "daily reps"},
            {"belief": "revenue_loss", "hook": "asset maintenance", "frame": "network decay"}
        ]
    },
    "problem_aware": {
        "code": "PA",
        "goal": "Make the pain personal and urgent, name the follow-up problem",
        "product_reveal": "Last 15 seconds",
        "modules": ["pain_articulation", "cost_of_inaction", "relationship_decay_frame"],
        "predicted_cpc": "$0.50-$1.00",
        "predicted_cac": "$20-$35",
        "angles": [
            {"belief": "too_busy", "hook": "relationships decay", "frame": "time passing"},
            {"belief": "too_busy", "hook": "your network is not small", "frame": "system problem"},
            {"belief": "cringe_ai", "hook": "not salesy", "frame": "authentic connection"}
        ]
    },
    "solution_aware": {
        "code": "SA",
        "goal": "Position EverReach as the simplest solution in the category",
        "product_reveal": "Middle and end",
        "modules": ["category_comparison", "mechanism_reveal", "willpower_vs_system"],
        "predicted_cpc": "$0.60-$1.20",
        "predicted_cac": "$18-$30",
        "angles": [
            {"belief": "hate_crm", "hook": "CRMs store not action", "frame": "daily list"},
            {"belief": "too_busy", "hook": "system not willpower", "frame": "automated habit"},
            {"belief": "already_organized", "hook": "reminders not enough", "frame": "needs words"}
        ]
    },
    "product_aware": {
        "code": "PROD",
        "goal": "Handle objections and demonstrate the product clearly",
        "product_reveal": "Throughout",
        "modules": ["full_demo", "objection_handling", "listicals"],
        "predicted_cpc": "$0.80-$1.50",
        "predicted_cac": "$15-$25",
        "angles": [
            {"belief": "all", "hook": "10 objections answered", "frame": "rapid fire"},
            {"belief": "too_busy", "hook": "60 second demo", "frame": "workflow"},
            {"belief": "hate_crm", "hook": "anti-CRM listical", "frame": "5 reasons"}
        ]
    },
    "most_aware": {
        "code": "MA",
        "goal": "Direct CTA with proof and risk reversal for retargeting",
        "product_reveal": "Immediate",
        "modules": ["proof_compilation", "risk_reversal", "direct_cta"],
        "predicted_cpc": "$0.30-$0.60",
        "predicted_cac": "$12-$20",
        "angles": [
            {"belief": "all", "hook": "you have seen this", "frame": "reminder"},
            {"belief": "revenue_loss", "hook": "results montage", "frame": "proof"},
            {"belief": "all", "hook": "risk reversal", "frame": "nothing to lose"}
        ]
    }
}

def generate_sora_prompt(awareness_level: str, angle: dict, variation_num: int) -> dict:
    """Generate a single Sora prompt using OpenAI"""
    
    config = AWARENESS_CONFIGS[awareness_level]
    
    system_prompt = f"""You are an expert video ad scriptwriter for Sora AI video generation.
You write scripts for EverReach - an AI-powered relationship intelligence tool that:
- Shows who to reach out to (warmth score)
- Generates message drafts
- Takes 60 seconds to use daily
- Prevents relationship decay

RULES FOR VOICEOVER:
- NO punctuation (no periods, commas, quotes)
- NO emojis
- Natural spoken cadence
- 55-60 second total duration
- End with CTA: "start with 1 person"

AWARENESS LEVEL: {awareness_level.upper()}
GOAL: {config['goal']}
PRODUCT REVEAL: {config['product_reveal']}
PREDICTED CPC: {config['predicted_cpc']}
PREDICTED CAC: {config['predicted_cac']}"""

    user_prompt = f"""Generate a complete Sora video prompt for EverReach.

ANGLE:
- Belief cluster: {angle['belief']}
- Hook style: {angle['hook']}
- Frame: {angle['frame']}

Output in this EXACT format:

PROMPT_ID: ER-{config['code']}-{angle['belief'].upper()[:4]}-{variation_num:03d}

SCENE_PLAN:
1. [beat description] [duration]s
2. [beat description] [duration]s
(continue for 5-7 scenes totaling 55-60s)

ON_SCREEN_TEXT:
- [text beat 1]
- [text beat 2]
- [text beat 3]
- [text beat 4]

VOICEOVER:
[Full voiceover script with no punctuation - should match scene timing]

HYPOTHESIS:
[One sentence on why this should work]"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.8,
        max_tokens=1000
    )
    
    content = response.choices[0].message.content
    
    return {
        "awareness_level": awareness_level,
        "belief": angle['belief'],
        "hook": angle['hook'],
        "frame": angle['frame'],
        "variation": variation_num,
        "predicted_cpc": config['predicted_cpc'],
        "predicted_cac": config['predicted_cac'],
        "sora_core": SORA_CORE,
        "generated_content": content
    }

def main():
    all_generations = []
    
    for level, config in AWARENESS_CONFIGS.items():
        print(f"\n{'='*60}")
        print(f"Generating {level.upper()} level prompts...")
        print(f"Predicted CPC: {config['predicted_cpc']} | CAC: {config['predicted_cac']}")
        print(f"{'='*60}")
        
        for i, angle in enumerate(config['angles'], 1):
            print(f"  [{i}/3] {angle['hook']} ({angle['belief']})...")
            
            try:
                result = generate_sora_prompt(level, angle, i)
                all_generations.append(result)
                print(f"       ✓ Generated")
            except Exception as e:
                print(f"       ✗ Error: {e}")
                all_generations.append({
                    "awareness_level": level,
                    "belief": angle['belief'],
                    "error": str(e)
                })
    
    # Save results
    output_path = os.path.join(os.path.dirname(__file__), "..", "generations", "test_generations.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(all_generations, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Generated {len(all_generations)} prompts")
    print(f"Saved to: {output_path}")
    print(f"{'='*60}")
    
    return all_generations

if __name__ == "__main__":
    main()
