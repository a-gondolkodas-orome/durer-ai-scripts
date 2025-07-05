from openai import OpenAI
import os
import shutil
from dotenv import load_dotenv
import concurrent.futures
from functools import partial

MAIN_DIR="main_folder"
INPUT_DIR = "feladatok"
REMOVED_DIR = "en_megoldasok"
RETURN_DIR = "preciz_feladatok"
AI_PROMPT = r"""Tedd precízzé a feladatleírást, betartva az alábbi szempontokat! Az output a feladatleírás latex kódja legyen. Csak is kizárólag a latex kódot add vissza, minden más szöveget mellőzz! Mielőtt visszadnád a latex szöveget, ellenőrizd le az, hogy biztos betartottad-e az összes szempontot!
- Ne lehessen többféleképpen értelmezni a feladatot!
- Ne használj sokszorosan összetett mondatokat!
- Ne használj túl hosszú mondatokat!
- A feladat szövege legyen minél rövidebb, tömörebb!
- Ne használd ugyanazt a szót nagyon sokszor, csak ha elkerülhetetlen!
- Ha valamit könnyebb utólag megjegyzésben leírni, akkor nyugodtan írj egy megjegyzést a feladat után! Például ha van egy fogalom/definíció ami nem biztos hogy mindenkinek ismert, akkor azt definiáld megjegyzésben! Az alapvető fogalmakat ne definiáld!
- A feladat vagy kérdéssel végződjön, vagy felszólítással!
- A feladat nyelvezete legyen szabatos/precíz, de középiskolások szóhasználatához igazodó!
- Ha definiálsz egy komplikált feltételt, akkor nevezd el a tulajdonságot, hogy később könnyebben tudj rá hivatkozni. Ha később nem hivatkozol rá, akkor szükségtelen elnevezni.
- Ne használj a szövegben zárójeleket!
- Az egyjegyű számokat írd ki betűkkel, kivéve ha képletben szerepelnek vagy konkrét mérőszámok! A többjegyű vagy negatív számokat írd számmal!
- Többsoros vagy eszméletlen hosszú képleteket tegyél dupla dollárjel közé!
- Ha több feltételt is szeretnél egymás után írni, akkor használhatsz felsorolást (itemize), de egy elemű felsorolást sose csinálj!
- NE rajzolj ábrákat! Ha van az eredeti leírásban, akkor azt másold ki!
- Ne használj minipage-t!
- Tegezd a diákokat!
- Csak akkor módosíts egy leíráson, ha nem elég precíz, de a módosításokat próbáld lokálisan végrehajtani. Tehát ha csak egy mondat nem elég precíz, akkor csak azt a mondatot módosítsd. Minél inkább próbáld az eredeti szöveget megtartani ahol lehet!

Itt van néhány példa nem elég precíz és precízzé tett feladatleírásra:
Eredeti:
\fdt \aa Anett, Andris, Kartal és Benedek kártyáznak. Négy különböző színű paklijuk van, mindegyik négy lapot tartalmaz, megszámozva 1-től 4-ig. Először összekeverik a 16 lapot, majd mind a négyen húznak négy lapot a kezükbe, amiket megmutatnak egymásnak. Ezután közösen eldöntik, hogy milyen sorrendben ülnek le körben, és azt is, hogy ki kezd. A játék folyamán a kör mentén óramutató járásával megegyező irányban sorban raknak le lapokat, de egy lapot csak akkor rakhatnak le, ha már minden nála kisebb számú, vele azonos színű le lett rakva. Akkor nyernek, ha az összes lapot lerakják. Ha valaki a sorra kerülésekor nem tud rakni és még van lap a kezében, veszítenek. Mutassatok olyan húzást, amelynél akárhogy is döntenek és játszanak, veszítenek!\\
\bb Mutassátok meg, hogy ha minden pakliban csak két lap lenne, 1-től 2-ig számozva, de ugyanúgy négy különböző paklijuk van, akkor mindig tudnak nyerni!

Precíz változat:
\fdt \aa Anett, Andris, Kartal és Benedek kártyáznak. Négy különböző színű paklijuk van, mindegyik négy lapot tartalmaz, megszámozva 1-től 4-ig. Először összekeverik a 16 lapot, majd mind a négyen húznak négy lapot a kezükbe, amiket megmutatnak egymásnak. Ezután közösen eldöntik, hogy milyen sorrendben ülnek le körben, és azt is, hogy ki kezd. A játék folyamán a kör mentén óramutató járásával megegyező irányban sorban raknak le egy-egy lapot, de egy lapot csak akkor rakhatnak le, ha már minden nála kisebb számú, vele azonos színű le lett rakva. Akkor nyernek, ha az összes lapot lerakják. Ha valaki a sorra kerülésekor nem tud rakni és még van lap a kezében, veszítenek. Mutassatok olyan húzást, amelynél akárhogy is döntenek és játszanak, veszítenek!\\
\bb Mutassátok meg, hogy ha mind a négy pakliból csak az 1-es és 2-es lapokkal játszanak, akkor mindig tudnak nyerni!


Eredeti:
\fdt Egy pingpongbajnokságon $100$ játékos vett részt, mindenki mindenkivel egy meccset játszott. A győzelem $1$ pontot ért, a vereség $0$-t. Tudjuk, hogy a bajnokság befejeztével bármely három résztvevőre igaz, hogy valamelyikük legyőzte a másik kettőt. Határozzátok meg a játékosok végső pontszámait!\\
\textit{Minden meccsnek egy győztese és egy vesztese lett, döntetlen nem született.}

Precíz változat:
\fdt Egy pingpongbajnokságon $100$ játékos vett részt, mindenki mindenkivel egy meccset játszott. A győzelem $1$ pontot ért, a vereség $0$-t. Tudjuk, hogy a bajnokság befejeztével bármely három résztvevőre igaz, hogy valamelyikük legyőzte a másik kettőt. Határozzátok meg a játékosok végső pontszámait!\\
\textit{Minden meccsnek egy győztese és egy vesztese lett, döntetlen nem született.}

Még néhány feladatleírás, amik precízek és használhatod referenciaként:
\fdt Az $ABC$ háromszög beírt körének középpontja legyen $I$, az $AB$ oldallal vett érintési pontja $D$, az $AB$ oldal felezőpontja $F$. Bizonyítsátok be, hogyha $\frac{AD}{AF}=\frac{2}{3}$ és $FIB\sphericalangle=ACI\sphericalangle$, akkor a háromszög egyenlő szárú.\\

\fdt A $\{0, 1, \ldots, 9\}$ halmaz egy $H$ részhalmazát nevezzük \textit{elégségesnek}, ha tetszőleges $10$-nél nagyobb egész szám előáll pontosan két olyan nemnegatív egész szám összegeként, melyeknek a számjegyei csak $H$-ból kerülnek ki.\\
\aa Bizonyítsátok be, hogy az $\{1, 2, 3, 4, 5, 6, 7, 8, 9\}$ halmaz elégséges.\\
\bb Bizonyítsátok be, hogy nem létezik négyelemű elégséges halmaz.\\
\cc Mutassatok minél kisebb elemszámú elégséges halmazt és bizonyítsátok annak elégségességét.\\

\fdt Tetszőleges $a$ egész szám és $k$ pozitív egész szám esetén jelöljük $(a \, \text{mod}\, k)$-val az $a$ szám $k$-val vett osztási maradékát, amire tehát $0\leq (a \, \text{mod}\, k) \leq k-1$ és $a-(a \, \text{mod}\, k)$ osztható $k$-val. Nevezzük az egész számokból álló $a_1, a_2, \ldots$ végtelen sorozatot \textit{nagyon periodikusnak}, ha minden $k$ pozitív egész szám esetén az $(a_1 \, \text{mod}\, k), \, (a_2 \, \text{mod}\, k), \ldots$ sorozat periodikus. Van-e olyan nagyon periodikus sorozat, amelynek végtelen sok tagja nulla, de a nullhelyei mégsem periodikusak?\\
\textit{Egy $c_1, c_2, \ldots$ sorozatot periodikusnak nevezünk, ha létezik olyan $d$ pozitív egész szám, melyre $c_{i+d}=c_i$ minden $i$ pozitív egész szám esetén. Azt mondjuk, hogy egy sorozat nullhelyei periodikusak, ha a sorozatban minden nemnulla számot $1$-re cserélve egy periodikus sorozatot kapunk.}\\

\fdt Hét gyerek (A, B, C, D, E, F, G) bomba-pajzs játékot játszik. A játék egy fordulójának elején sípszóra mindenki választ magának a hat másik gyerek közül két különbözőt, egyiküket bombájának, másikukat pajzsának. Innentől $1$ percük van arra, hogy elhelyezkedjenek a sík terepen, ezután mindenki egy helyben marad. Egy adott forduló végén azok a gyerekek kapnak pontot, akik az idő leteltével egy egyenesen állnak a választott bombájukkal és pajzsukkal úgy, hogy hármójuk közül a pajzs van középen.\vspace{1mm}\\
\begin{minipage}{0.6\linewidth}
    \aa Az egyik játékban a gyerekek a táblázatban látható módon választottak maguknak bombát és pajzsot. Mutassatok egy olyan felállást, ami esetén mind a hét gyerek szerez pontot a fordulóban.
    \vspace{1mm}
\end{minipage}
\begin{minipage}{0.4\linewidth}
\begin{center}
\begin{tabular}{|c|c|c|c|c|c|c|c|}
\hline
gyerek & A & B & C & D & E & F & G \\ \hline
pajzs & D & A & A & G & G & C & C \\ \hline
bomba & F & E & G & E & B & B & D \\ \hline
\end{tabular}
\end{center}
\end{minipage}

\noindent\bb Lehetséges-e, hogy a gyerekek úgy választanak maguknak bombát és pajzsot, hogy sehogy se tudnak beállni úgy, hogy mindenki szerezzen pontot a fordulóban?\\
\cc Igaz-e, hogy ha egy fordulóban a gyerekek el tudnak helyezkedni úgy, hogy mindenki szerez pontot, akkor el tudnak helyezkedni úgy is, hogy mindenki szerezzen pontot és mindannyian egy egyenesen legyenek?\\



Feladatleírás amit tegyél precízzé:
"""

AI_MODEL="google/gemini-2.5-flash"

INPUT_DIR=f"{MAIN_DIR}/{INPUT_DIR}"
REMOVED_DIR=f"{MAIN_DIR}/{REMOVED_DIR}"
RETURN_DIR=f"{MAIN_DIR}/{RETURN_DIR}"

load_dotenv()

os.makedirs(REMOVED_DIR, exist_ok=True)
os.makedirs(RETURN_DIR, exist_ok=True)

files = [
    file for file in os.listdir(INPUT_DIR)
    if os.path.isfile(f"{INPUT_DIR}/{file}") and
    file[-4:]==".tex"
]
removed_files = [
    file for file in os.listdir(REMOVED_DIR)
    if os.path.isfile(f"{REMOVED_DIR}/{file}")
]
needed_files = list(set(files).difference(set(removed_files)))


client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_APIKEY"),
    )

def file_to_str(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        return file.read()


def process_single_file(file_name, prompt, files_dir, output_dir):
    """
    Processes a single file: reads it, calls the LLM, and writes the result.
    This function is designed to be run in a separate thread.
    """
    print(f"Starting processing for: {file_name}")

    text = file_to_str(f"{files_dir}/{file_name}")
    if not text:
        return f"Skipped {file_name} (could not read file)."
    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "<YOUR_SITE_URL>",  # Optional. Site URL for rankings on openrouter.ai.
            "X-Title": "<YOUR_SITE_NAME>",  # Optional. Site title for rankings on openrouter.ai.
        },
        model=AI_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt + text,
            }
        ],
    )
    result_text = completion.choices[0].message.content
    with open(f"{output_dir}/{file_name}", "w", encoding="utf-8") as outfile:
        outfile.write(result_text)



def exec_prompt_for_files_parallel(prompt, files, files_dir, output_dir, batch_size=10):
    """
    Executes a prompt for a list of files in parallel, using batches.
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    file_batches = [files[i:i + batch_size] for i in range(0, len(files), batch_size)]

    for i, batch in enumerate(file_batches):
        print(f"\n--- Processing Batch {i+1}/{len(file_batches)} ---")
        
        # Use ThreadPoolExecutor to run tasks in parallel for the current batch
        # The 'with' statement ensures threads are cleaned up properly
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # We use functools.partial to create a new function with some arguments
            # pre-filled. This is needed because executor.map only passes one argument
            # (the file name) to the worker function.
            task_with_args = partial(
                process_single_file,
                prompt=prompt,
                files_dir=files_dir,
                output_dir=output_dir
            )
            
            # map() executes the function for each item in the batch and returns results
            # as they are completed.
            results = executor.map(task_with_args, batch)
            for result in results:
                print(result)


print("\nStarting parallel processing...")
exec_prompt_for_files_parallel(
    prompt=AI_PROMPT,
    files=files,
    files_dir=INPUT_DIR,
    output_dir=RETURN_DIR,
    batch_size=10
)

print("\n--- All batches completed. ---")
for file_name in removed_files:
    shutil.copyfile(f"{REMOVED_DIR}/{file_name}", f"{RETURN_DIR}/{file_name}")
