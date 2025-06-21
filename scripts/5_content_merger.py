import json
import re
from pathlib import Path

jan_2025_contents = ['2025-01/README.md', 'development-tools.md', 'vscode.md', 'uv.md', 'npx.md', 'unicode.md', 'devtools.md', 'css-selectors.md', 'json.md', 'bash.md', 'spreadsheets.md', 'sqlite.md', 'git.md', 'deployment-tools.md', 'markdown.md', 'image-compression.md', 'github-pages.md', 'colab.md', 'vercel.md', 'github-actions.md', 'docker.md', 'ngrok.md', 'cors.md', 'rest-apis.md', 'fastapi.md', 'llamafile.md', 'large-language-models.md', 'prompt-engineering.md', 'tds-ta-instructions.md', 'tds-gpt-reviewer.md', 'llm-sentiment-analysis.md', 'llm-text-extraction.md', 'base64-encoding.md', 'vision-models.md', 'embeddings.md', 'topic-modeling.md', 'vector-databases.md', 'function-calling.md', 'retrieval-augmented-generation.md', 'data-sourcing.md', 'scraping-with-excel.md', 'scraping-with-google-sheets.md', 'bbc-weather-api-with-python.md', 'scraping-imdb-with-javascript.md', 'nominatim-api-with-python.md', 'wikipedia-data-with-python.md', 'scraping-pdfs-with-tabula.md', 'convert-pdfs-to-markdown.md', 'llm-website-scraping.md', 'llm-video-screen-scraping.md', 'scheduled-scraping-with-github-actions.md', 'scraping-emarketer.md', 'scraping-live-sessions.md', 'data-preparation.md', 'data-cleansing-in-excel.md', 'data-transformation-in-excel.md', 'splitting-text-in-excel.md', 'data-aggregation-in-excel.md', 'data-preparation-in-the-shell.md', 'data-preparation-in-the-editor.md', 'cleaning-data-with-openrefine.md', 'profiling-data-with-python.md', 'parsing-json.md', 'transforming-images.md', 'extracting-audio-and-transcripts.md', 'data-analysis.md', 'correlation-with-excel.md', 'regression-with-excel.md', 'forecasting-with-excel.md', 'outlier-detection-with-excel.md', 'data-analysis-with-python.md', 'data-analysis-with-sql.md', 'data-analysis-with-duckdb.md', 'geospatial-analysis-with-excel.md', 'geospatial-analysis-with-python.md', 'geospatial-analysis-with-qgis.md', 'network-analysis-in-python.md', 'visualizing-machine-learning.md', 'data-visualization.md', 'visualizing-forecasts-with-excel.md', 'visualizing-animated-data-with-powerpoint.md', 'visualizing-animated-data-with-flourish.md', 'visualizing-network-data-with-kumu.md', 'visualizing-charts-with-excel.md', 'data-visualization-with-seaborn.md', 'actor-network-visualization.md', 'rawgraphs.md', 'data-storytelling.md', 'marimo.md', 'google-charts.md', 'google-data-studio.md', 'narratives-with-excel.md', 'narratives-with-comics.md', 'project-1.md', 'project-2.md', 'live-sessions.md', 'live-session-2025-01-15.md', 'live-session-2025-01-16.md', 'live-session-2025-01-17.md', 'live-session-2025-01-20.md', 'live-session-2025-01-21.md', 'live-session-2025-01-22.md', 'live-session-2025-01-23.md', 'live-session-2025-01-28.md', 'live-session-2025-01-29.md', 'live-session-2025-01-30.md', 'live-session-2025-01-31.md', 'live-session-2025-02-01.md', 'live-session-2025-02-04.md', 'live-session-2025-02-06.md', 'live-session-2025-02-07.md']

sidebar_file = "../raw-data/cloned/2025-01/_sidebar.md"
base_url = "https://tds.s-anand.net/#/"
pattern = re.compile(r"\[([^\]]+)\]\((?:\.\./)?(.+?\.md)\)")

data = {"course": []}
current = None
root = Path("../raw-data/cloned")  # cloned directory

for line in Path(sidebar_file).read_text(encoding="utf-8").splitlines():
    match = pattern.search(line)
    if not match:
        continue

    title, file_path = match.groups()
    file_path = Path(file_path.strip()).name
    if f"2025-01/{file_path}" not in jan_2025_contents and file_path not in jan_2025_contents:
        continue
    
    content_path = (root / "2025-01" / file_path) if file_path == "README.md" else (root / file_path)


    try:
        content = content_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        content = ""

    entry = {
        "title": title,
        "file": Path(file_path).name,
        "url": base_url + Path(file_path).stem,
        "content": content
    }

    if line.startswith("- "):  # top level
        current = entry
        current["subsections"] = []
        data["course"].append(current)
    elif line.startswith("  - ") and current:  # subsection
        current["subsections"].append(entry)

with open("../raw-data/course.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("✅ Done. Output saved to course.json")

