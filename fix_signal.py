
path = 'f:/Bhrikutimandap/store/models.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Target the PREVIOUSLY patched version (or the original if script failed? No, script succeeded)
# The previous script replaced it with:
# defaults={'company_name': instance.company}

target = "defaults={'company_name': instance.company}"
replacement = "defaults={'company_name': instance.company or ''}"

if target in content:
    new_content = content.replace(target, replacement)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Signal patched (v2).")
else:
    print("Target not found. Check file content.")
