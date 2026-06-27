$ErrorActionPreference = "Stop"

Set-Location -Path $PSScriptRoot

$pythonExe = "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

if (-not $env:DISCORD_TOKEN) {
    $token = Read-Host "Paste Discord bot token for this session"
    $env:DISCORD_TOKEN = $token
}

if (-not $env:RAG_OLLAMA_MODEL) {
    $env:RAG_OLLAMA_MODEL = "qwen2.5:3b"
}

$currentChannelId = $env:DISCORD_CHANNEL_ID
$channelId = Read-Host "Discord channel ID to answer in (current: $currentChannelId, blank = keep, all = no restriction)"
if ($channelId -eq "all") {
    Remove-Item Env:DISCORD_CHANNEL_ID -ErrorAction SilentlyContinue
} elseif ($channelId) {
    $env:DISCORD_CHANNEL_ID = $channelId
}

& $pythonExe .\discord_rag_bot.py
