from openai import OpenAI
import os
import shutil
from dotenv import load_dotenv


MAIN_DIR="Fő mappa"
FILES_DIR = "hu_megoldasok"
REMOVED_DIR = "en_megoldasok"
RETURN_DIR = "dontoK"
AI_PROMPT = "Egy matekverseny feladatát szeretném angolra fordítani. Bemásolok a feladatot kérlek fordítsd át, a neveknek a kézenfekvő angol verzióját add meg. Válaszként csak a fordítás szövegét add meg. Always keep latex formatting in the text, e.g. \textit{...}. You can delete the comments (lines beginning with %), but leave the figures unchanged. The problem:\n"
AI_MODEL="anthropic/claude-sonnet-4"

FILES_DIR=f"{MAIN_DIR}/{FILES_DIR}"
REMOVED_DIR=f"{MAIN_DIR}/{REMOVED_DIR}"
RETURN_DIR=f"{MAIN_DIR}/{RETURN_DIR}"
load_dotenv()

files = [
    file for file in os.listdir(FILES_DIR)
    if os.path.isfile(f"{FILES_DIR}/{file}")
]
removed_files = [
    file for file in os.listdir(REMOVED_DIR)
    if os.path.isfile(f"{REMOVED_DIR}/{file}")
]
needed_files = list(set(files).difference(set(removed_files)))


os.makedirs(RETURN_DIR, exist_ok=True)
for file_name in needed_files:
    if file_name[-4:]==".tex":
        with open(f"{FILES_DIR}/{file_name}", "r", encoding="utf-8") as file:
            file_list = file.readlines()
            text = ""
            for i in range(len(file_list)):
                text += file_list[i]

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_APIKEY"),
        )
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "<YOUR_SITE_URL>",  # Optional. Site URL for rankings on openrouter.ai.
                "X-Title": "<YOUR_SITE_NAME>",  # Optional. Site title for rankings on openrouter.ai.
            },
            model=AI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": AI_PROMPT + text,
                }
            ],
        )
        translated_text = completion.choices[0].message.content

        with open(f"{RETURN_DIR}/{file_name}", "w", encoding="utf-8") as outfile:
            outfile.write(translated_text)

for file_name in removed_files:
    shutil.copyfile(f"{REMOVED_DIR}/{file_name}", f"{RETURN_DIR}/{file_name}")
