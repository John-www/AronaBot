# Thesis Local RAG

This is a simple local RAG flow for PDF and Word thesis files.

## What this does

1. Read PDF, DOCX, TXT, or Markdown files.
2. Clean obvious table-of-contents noise and page-number lines.
3. Split them into chunks.
4. Build a local keyword index and an Ollama embedding index in `rag_index/`.
5. Retrieve relevant chunks for a question.
6. Optionally ask a local Ollama model to answer from those chunks.

## Install document readers

```powershell
python -m pip install -r requirements.txt
```

## Add documents

Create a folder named `rag_docs/`, then put your thesis PDF or Word files inside it.

Supported:

- `.pdf`
- `.docx`
- `.txt`
- `.md`

## Build the index

```powershell
ollama pull nomic-embed-text
python thesis_rag.py ingest rag_docs
```

This writes cleaned chunks to `rag_index/chunks.jsonl` and vectors to `rag_index/embeddings.jsonl`.
To rebuild only the old keyword index without embeddings:

```powershell
python thesis_rag.py ingest rag_docs --no-embeddings
```

## Retrieve relevant passages only

```powershell
python thesis_rag.py ask "這篇論文的研究方法是什麼?"
```

## Generate an answer with local Ollama

Install Ollama, pull a model, then ask:

```powershell
ollama pull llama3.1
python thesis_rag.py ask "這篇論文的研究方法是什麼?" --model llama3.1
```

The answer is generated from retrieved local chunks. Your documents stay on this machine.

## Discord bot

After Ollama works locally, set your Discord bot token as an environment variable:

```powershell
$env:DISCORD_TOKEN="your_discord_bot_token"
$env:RAG_OLLAMA_MODEL="qwen2.5:3b"
$env:DISCORD_CHANNEL_ID="your_discord_channel_id"
python discord_rag_bot.py
```

Or use the helper script:

```powershell
.\start_discord_rag_bot.ps1
```

In Discord:

```text
!ask 這篇論文的研究方法是什麼?
```

Useful Discord commands:

```text
!ping
!status
!ask 用三句話介紹我的論文
!抽籤
!抽獎
!隨機圖片
!電腦檢測
!pc_status
!gpu_inf
!shutdown
```

The bot runs on your computer, retrieves local thesis chunks, asks Ollama, then replies in Discord.

## Notion note

For Notion interview notes, GPT/Codex cannot automatically see your whole Notion workspace.
You need to either:

- export the page/database from Notion and place it in this folder, or
- use the Notion API sync script and share only selected pages/databases with the integration.
