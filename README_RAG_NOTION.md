# Local Notion Sync for RAG

This is step 1 for a simple local RAG project: sync your Notion interview notes to local Markdown files.

## 1. Create a Notion integration

1. Go to Notion integrations and create an internal integration.
2. Copy the integration secret.
3. Open the Notion page or database with your interview notes.
4. Click `...` then `Connections`, and add your integration.

## 2. Set your token

PowerShell:

```powershell
$env:NOTION_TOKEN="secret_your_notion_integration_token"
```

## 3. Sync one page

```powershell
python notion_sync.py --page-id "your_page_id"
```

## 4. Sync a database

```powershell
python notion_sync.py --database-id "your_database_id"
```

## 5. Search shared pages

```powershell
python notion_sync.py --query "interview"
```

The Markdown files will be written to `notion_export/`.

