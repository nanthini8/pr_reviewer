import sys
import os
from typing import Any, Dict, List
from mcp.server.fastmcp import FastMCP
from github_utils import fetch_pr_changes
from notion_client import Client
from dotenv import load_dotenv

class PRAnalyzer:
    def __init__(self):
        load_dotenv()
        self.mcp = FastMCP("github_pr_analyzer")
        print("MCP Server initialized", file=sys.stderr)  # By default print() writes to sys.stdout.
        self._init_notion()
        self._register_tools()

    def _init_notion(self):
        """ Initialize Notion client with API key and page ID """
        try:
            self.notion_api_key = os.getenv('NOTION_API_KEY')
            self.notion_page_id = os.getenv('NOTION_PAGE_ID')

            if not self.notion_api_key or not self.notion_page_id:
                raise ValueError("Notion API key or page ID is missing.")
            
            self.notion = Client(auth=self.notion_api_key)
            print(f"Notion client initialized successfully", file=sys.stderr)
        except Exception as e:
            print(f"Error initializing Notion client: {e}")
            sys.exit(1)

    def _register_tools(self):
        """ Register MCP tools for PR analysis """
        @self.mcp.tool()
        async def fetch_pr(repo_owner: str, repo_name: str, pr_number: int) -> Dict[str, Any]:
            """ Fetch changes from a pull request in a GitHub repository. """
            print(f"Fetching PR #{pr_number} from {repo_owner}/{repo_name}", file=sys.stderr)
            try:
                pr_info = fetch_pr_changes(repo_owner, repo_name, pr_number)
                if pr_info is None:
                    print("No changes found in the pull request.")
                    return {}
                return pr_info
            except Exception as e:
                return {'status': 'error', 'message': str(e)}
        
        @self.mcp.tool()
        async def create_notion_page(title: str, content: str) -> str:
            """ Create a Notion page with the PR details. """
            print(f"Creating Notion page: {title}", file=sys.stderr)
            try:
                self.notion.pages.create(
                    parent={"type": "page_id", "page_id": self.notion_page_id},
                    properties={"title": [{"text": {"content": title}}]},
                    children=[{
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{
                                "type": "text",
                                "text": {"content": content}
                            }]
                        }
                    }]
                )
                print(f"Notion page '{title}' created successfully!", file=sys.stderr)
                return "Notion page created successfully."
            except Exception as e:
                return f"Error creating Notion page: {str(e)}"

    def run(self):
        """ Start the MCP server. """
        try:
            print("Running MCP Server for GitHub PR Analysis...", file=sys.stderr)  # Output for errors or logs
            # self.mcp.run(transport="stdio")   # Starts MCP in standard I/O mode
            self.mcp.run()  # Default http
            print("MCP Server is running.")
        except Exception as e:
            print(f"Error running MCP server: {e}")

# Ensure the script runs only if it's the main module
if __name__ == "__main__":
    analyzer = PRAnalyzer()
    analyzer.run()
    