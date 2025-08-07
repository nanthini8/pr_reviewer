import os
import requests
from dotenv import load_dotenv
import sys

# Load environment variables from .env file
load_dotenv()
github_token = os.getenv('GIT_TOKEN')

def fetch_pr_changes(repo_owner: str, repo_name: str, pr_number: int) -> list:
    """ Fetch changes from a pull request in a GitHub repository. 
    Args:
        repo_owner (str): The owner of the repository.
        repo_name (str): The name of the repository.
        pr_number (int): The pull request number.
    Returns:           
        list: A list of changes in the pull request.
    """

    pr_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}"
    files_url = f"{pr_url}/files"
    headers = {
        'Authorization': f'token {github_token}',
    }

    try:
        print("Request",requests)

        # Fetch the PR metadata
        pr_response = requests.get(pr_url, headers=headers)
        print("PR Response:", pr_response, file=sys.stderr)
        pr_response.raise_for_status()   # Method from requests library, checks status code of response, if status code is not 200, it raises an HTTPError
        pr_data = pr_response.json()

        # Fetch the files changed in the PR
        files_response = requests.get(files_url, headers=headers)
        files_response.raise_for_status()
        files_data = files_response.json()

        print("PR Data:", pr_data, file=sys.stderr)
        print("Files Data:", files_data, file=sys.stderr)
    
        # Combine PR metadata and files data
        changes = []
        for file in files_data:
            change = {
                'filename': file['filename'],
                'status': file['status'],
                'additions': file['additions'],
                'deletions': file['deletions'],
                'changes': file['changes'],
                'patch': file.get('patch', ''),
                'raw_url': file.get('raw_url', ''),
                'content_url': file.get('contents_url', ''),
            }
            changes.append(change)

        # Add PR metadata
        pr_info = {
            'title': pr_data['title'],
            'description': pr_data['body'],
            'author': pr_data['user']['login'],
            'created_at': pr_data['created_at'],
            'updated_at': pr_data['updated_at'],
            'state': pr_data['state'],
            'total_changes': len(changes),
            'changes': changes
        }

        print(f"Successfully fetched PR changes!", file=sys.stderr)
        return pr_info

    except Exception as e:
        print(f"Error fetching PR changes: {e}", file=sys.stderr)
        return None
