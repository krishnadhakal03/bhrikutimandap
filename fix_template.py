import os

file_path = r'f:\Bhrikutimandap\templates\store\home.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the template syntax errors
content = content.replace("sort_price=='low_to_high'", "sort_price == 'low_to_high'")
content = content.replace("sort_price=='high_to_low'", "sort_price == 'high_to_low'")
content = content.replace("agent_id|add:\"0\"", "request.GET.agent")
content = content.replace("agent.id|add:\"0\"", "agent.id|stringformat:'s'")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Template syntax fixed!")
