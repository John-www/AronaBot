import argparse
import json
import os
import re
import time
from pathlib import Path
from urllib import error, request


NOTION_VERSION = "2022-06-28"
DEFAULT_OUTPUT_DIR = "notion_export"


class NotionClient:
    def __init__(self, token):
        if not token:
            raise ValueError("Missing NOTION_TOKEN. Set it in your environment first.")
        self.token = token

    def post(self, path, payload):
        return self._request("POST", path, payload)

    def get(self, path):
        return self._request("GET", path)

    def _request(self, method, path, payload=None):
        url = f"https://api.notion.com/v1/{path.lstrip('/')}"
        body = None
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")

        req = request.Request(
            url,
            data=body,
            method=method,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Notion-Version": NOTION_VERSION,
                "Content-Type": "application/json",
            },
        )

        try:
            with request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Notion API error {exc.code}: {detail}") from exc


def plain_text(rich_text):
    return "".join(part.get("plain_text", "") for part in rich_text or [])


def slugify(value):
    value = value.strip() or "untitled"
    value = re.sub(r"[^\w\s.-]", "", value, flags=re.UNICODE)
    value = re.sub(r"\s+", "-", value)
    return value[:80].strip(".-") or "untitled"


def page_title(page):
    props = page.get("properties", {})
    for prop in props.values():
        if prop.get("type") == "title":
            title = plain_text(prop.get("title"))
            if title:
                return title
    return page.get("id", "untitled")


def block_to_markdown(block):
    block_type = block.get("type")
    data = block.get(block_type, {})

    if block_type == "paragraph":
        return plain_text(data.get("rich_text"))
    if block_type == "heading_1":
        return f"# {plain_text(data.get('rich_text'))}"
    if block_type == "heading_2":
        return f"## {plain_text(data.get('rich_text'))}"
    if block_type == "heading_3":
        return f"### {plain_text(data.get('rich_text'))}"
    if block_type == "bulleted_list_item":
        return f"- {plain_text(data.get('rich_text'))}"
    if block_type == "numbered_list_item":
        return f"1. {plain_text(data.get('rich_text'))}"
    if block_type == "to_do":
        checked = "x" if data.get("checked") else " "
        return f"- [{checked}] {plain_text(data.get('rich_text'))}"
    if block_type == "quote":
        text = plain_text(data.get("rich_text"))
        return "\n".join(f"> {line}" for line in text.splitlines())
    if block_type == "code":
        language = data.get("language") or ""
        text = plain_text(data.get("rich_text"))
        return f"```{language}\n{text}\n```"
    if block_type == "divider":
        return "---"
    if block_type == "child_page":
        return f"## {data.get('title', 'Child page')}"

    return ""


def paginated(client, path, payload=None):
    start_cursor = None
    while True:
        current_payload = dict(payload or {})
        if start_cursor:
            current_payload["start_cursor"] = start_cursor

        if payload is None:
            suffix = path
            if start_cursor:
                separator = "&" if "?" in suffix else "?"
                suffix = f"{suffix}{separator}start_cursor={start_cursor}"
            response = client.get(suffix)
        else:
            response = client.post(path, current_payload)

        yield from response.get("results", [])
        if not response.get("has_more"):
            break
        start_cursor = response.get("next_cursor")


def fetch_blocks(client, block_id, depth=0):
    lines = []
    blocks = paginated(client, f"blocks/{block_id}/children?page_size=100")
    for block in blocks:
        markdown = block_to_markdown(block)
        if markdown:
            lines.append(markdown)

        if block.get("has_children") and depth < 5:
            child_lines = fetch_blocks(client, block["id"], depth + 1)
            if child_lines:
                lines.append(child_lines)

    return "\n\n".join(lines)


def search_pages(client, query):
    payload = {
        "query": query,
        "filter": {"value": "page", "property": "object"},
        "page_size": 25,
    }
    return list(paginated(client, "search", payload))


def database_pages(client, database_id):
    return list(paginated(client, f"databases/{database_id}/query", {"page_size": 100}))


def write_page(client, page, output_dir):
    title = page_title(page)
    body = fetch_blocks(client, page["id"])
    filename = f"{slugify(title)}-{page['id'].replace('-', '')[:8]}.md"
    path = output_dir / filename
    metadata = {
        "id": page["id"],
        "title": title,
        "url": page.get("url"),
        "last_edited_time": page.get("last_edited_time"),
    }
    content = [
        "---",
        json.dumps(metadata, ensure_ascii=False, indent=2),
        "---",
        "",
        f"# {title}",
        "",
        body,
        "",
    ]
    path.write_text("\n".join(content), encoding="utf-8")
    return path


def sync_pages(client, pages, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for page in pages:
        written.append(write_page(client, page, output_dir))
        time.sleep(0.35)
    return written


def main():
    parser = argparse.ArgumentParser(description="Sync Notion pages to local Markdown files.")
    parser.add_argument("--page-id", help="A shared Notion page id to sync.")
    parser.add_argument("--database-id", help="A shared Notion database id to query and sync.")
    parser.add_argument("--query", help="Search shared Notion pages by title/content.")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_DIR, help="Output directory.")
    args = parser.parse_args()

    selected = [args.page_id, args.database_id, args.query]
    if sum(bool(item) for item in selected) != 1:
        parser.error("Choose exactly one of --page-id, --database-id, or --query.")

    client = NotionClient(os.getenv("NOTION_TOKEN"))
    output_dir = Path(args.output)

    if args.page_id:
        page = client.get(f"pages/{args.page_id}")
        pages = [page]
    elif args.database_id:
        pages = database_pages(client, args.database_id)
    else:
        pages = search_pages(client, args.query)

    written = sync_pages(client, pages, output_dir)
    print(f"Synced {len(written)} page(s) to {output_dir.resolve()}")
    for path in written:
        print(f"- {path}")


if __name__ == "__main__":
    main()
