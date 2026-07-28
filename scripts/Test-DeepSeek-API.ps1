$ErrorActionPreference = "Stop"

$InstallDir = "D:\Backup\Documents\EC"
$PythonExe = "D:\Backup\Documents\EC.venv\Scripts\python.exe"
$env:DEEPTUTOR_HOME = $InstallDir

$Code = @'
import json
from pathlib import Path

from openai import OpenAI

install_dir = Path(r"D:\Backup\Documents\EC")
catalog_path = install_dir / "data" / "user" / "settings" / "model_catalog.json"
catalog = json.loads(catalog_path.read_text(encoding="utf-8-sig"))

llm = catalog["services"]["llm"]
profile = next((p for p in llm["profiles"] if p["id"] == llm["active_profile_id"]), llm["profiles"][0])
model = next((m for m in profile["models"] if m["id"] == llm["active_model_id"]), profile["models"][0])["model"]
api_key = profile.get("api_key") or ""

if not api_key:
    raise SystemExit("DeepSeek API Key is not configured. Run scripts\\Set-DeepSeek-API-Key.ps1 first.")

client = OpenAI(api_key=api_key, base_url=profile["base_url"])

first = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": "Reply exactly: DeepSeek API connection OK."}],
    stream=False,
    extra_body={"thinking": {"type": "disabled"}},
)
print(first.choices[0].message.content.strip())

second = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "user",
            "content": "Briefly explain the difference between an RCD and an RCBO for an Australian Certificate III Electrotechnology student.",
        }
    ],
    stream=False,
    extra_body={"thinking": {"type": "disabled"}},
)
print("---")
print(second.choices[0].message.content.strip())
'@

$Code | & $PythonExe -
exit $LASTEXITCODE
