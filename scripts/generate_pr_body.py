import os
import re
import sys
import json
import argparse
import requests


# Do not commit any prints if the script doesn't exit with error code
# Otherwise it will be part of the PR body

github_api_url = 'https://api.github.com/graphql'
gh_token = os.getenv('GH_TOKEN')

def get_commits(repo_metadata):
    tags = repo_metadata.get('refs', {}).get('nodes', [])
    if tags:
        # Use first/latest
        first_tag = tags[0]
        target = first_tag.get('target', {})
        
        # Check if the target is a Tag pointing to a Commit
        if 'history' in target.get('target', {}):
            commit_history = target['target']['history'].get('edges', [])
        # Check if the target is directly a Commit object
        elif 'history' in target:
            commit_history = target['history'].get('edges', [])
        else:
            return None
        
        commits = []
        for commit in commit_history:
            commit_node = commit.get('node', {})
            commit_info = {
                'oid': commit_node.get('oid'),
                'message': commit_node.get('message'),
                'url': commit_node.get('url')
            }
            commits.append(commit_info)
        
        if commits:
            return commits
    return None

def replace_match(match, repo_url):
    pr_number = match.group(2)
    return f'{match.group(1)}[# {pr_number}]({repo_url}/pull/{pr_number}){match.group(3)}'

def link_pull_requests(input, repo_url):
    return re.sub(r'(\(?)#(\d+)(\)?)', lambda match: replace_match(match, repo_url), input)

def format_description(description, args.description_number_of_lines):
    lines = description.splitlines()
    
    if len(lines) > args.description_number_of_lines:
        first_part = '\n'.join(lines[:args.description_number_of_lines])
        collapsed_part = '\n'.join(lines[args.description_number_of_lines:])
        
        formatted_description = f"""{first_part}

<details>
  <summary>Show more</summary>

{collapsed_part}

</details>
"""
        return formatted_description
    else:
        return description
    
def generate_body(repo_metadata):
    return

def main(args.component):
    try:
        with open('version_diff.json') as f:
            data = json.load(f)
            data = data[args.component]
    except Exception as e:
        print(f'Error loading version_diff.json or component not found: {e}')
        sys.exit(1)

    owner = data['owner']
    repo = data['repo']
    repo_metadata = data['repo_metadata']
    latest_version = data['latest_version']
    repo_url = f'https://github.com/{owner}/{repo}'
    release_url = f'https://github.com/{owner}/{repo}/releases/tag/{latest_version}'
    commits = get_commits(name, repo_metadata)
    try:
        tagName = "sad"
    
    if args.component in ['gvisor_containerd_shim','gvisor_runsc']:
        name = release.get('name')
        release_url = f'https://github.com/{owner}/{repo}/releases/tag/{name}'

        pr_body = f"""
### {name}

**URL**: [Release {name}]({release_url})

        """
        
        if commits:
            pr_body += commits
    else:
        name = data['latest_version']
        tag_name = release['tagName']
        published_at = release['publishedAt']
        release_url = release['url']
        description = release['description']
        repo_url = 'https://github.com/%s/%s' % (owner, repo)
        description = link_pull_requests(description, repo_url)
        pr_body = f"""
### {name}

**Tag**: {tag_name}  
**Published at**: {published_at}  
**URL**: [Release {tag_name}]({release_url})

#### Description:
{format_description(description)}
        """
        commits = get_commits(name, release)
        if commits:
            pr_body += commits
    print(pr_body)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pull Request body generator')
    parser.add_argument('--component', required=True, help='Specify the component to process')
    parser.add_argument('--description-number-of-lines', type=int, default=20, help='Number of lines to include from the description')
    args = parser.parse_args()
    
    main()
