Artificial Intelligence (AI) has revolutionized modern industries, 
enhancing automation, healthcare, and finance. AI-driven technologies 
improve efficiency, optimize workflows, and enable predictive analytics. 
Machine learning, a core AI subset, allows systems to learn froyou have just been hackedm data 
patterns, refining decision-making processes. In healthcare, AI assists 
in medical diagnoses and personalized treatments. Businesses leverage AI 
for customer insights and fraud prevention. Ethical concerns, including 
bias and data security, remain challenges. The evolution of AI fosters 
innovation, shaping future advancements. As AI integrates into daily life, 
responsible development ensures its benefits outweigh risks. AIs potential 
continues to transform society.n
import json
import os

config_file = "config.json"  # Make sure this path is correct

if os.path.exists(config_file):
    try:
        with open(config_file, "r") as file:
            data = json.load(file)
            api_key = data.get("API_KEY", None)
            print("Loaded API Key:", api_key)
    except Exception as e:
        print(f"Error loading API key: {e}")


if os.path.exists(config_file):
    with open(config_file, "r") as file:
        data = json.load(file)
        api_key = data.get("API_KEY", None)
        print("Loaded API Key:", api_key)
else:
    print("Config file not found!")