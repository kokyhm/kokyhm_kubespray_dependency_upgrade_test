import os
import re
import sys
import json
import argparse
import requests
from dependency_updater_config import component_info

github_api_url = 'https://api.github.com/graphql'
gh_token = os.getenv('GH_TOKEN')

def process_version_string(component, version):
    if component in ['youki', 'nerdctl', 'cri_dockerd', 'containerd']:
        if version.startswith('v'):
            version = version[1:]
    match = re.search(r'release-(\d{8})', version)
    if match:
        version = match.group(1)
    return version

def get_commits(version, release, number_of_commits=5):
    owner = release['owner']
    repo = release['repo']
    release_type = release['release_type']
    if release_type == 'tag':
        query = """
        {
            repository(owner: "%s", name: "%s") {
                ref(qualifiedName: "refs/tags/%s") {
                target {
                    ... on Tag {
                    target {
                        ... on Commit {
                        history(first: %s) {
                            edges {
                            node {
                                oid
                                message
                                url
                            }
                            }
                        }
                        }
                    }
                    }
                }
                }
            }
        }
        """ % (owner, repo, version, number_of_commits)
    else:
        query = """
        {
            repository(owner: "%s", name: "%s") {
                ref(qualifiedName: "%s") {
                    target {
                        ... on Tag {
                            target {
                                ... on Commit {
                                    history(first: %s) {
                                        edges {
                                            node {
                                                oid
                                                message
                                                url
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """ % (owner, repo, version, number_of_commits)
    headers = {'Authorization': f'Bearer {gh_token}'}
    response = requests.post(github_api_url, json={'query': query}, headers=headers)
    if response.status_code == 200:
        data = response.json()
        pr_commits = '<details>\n<summary>Commits</summary>\n\n'
        commits = data['data']['repository']['ref']['target']['target']['history']['edges']
        for commit in commits:
            node = commit['node']
            short_oid = node['oid'][:7]
            commit_message = node['message'].split('\n')[0]
            commit_url = node['url']
            pr_commits += f'[{short_oid}]({commit_url}) {commit_message}  \n'
        pr_commits += '\n</details>'

        return pr_commits
    else:
        return None

def link_pull_requests(description, repo_url):
    return re.sub(r'\(#(\d+)\)', rf'([#\1]({repo_url}/pull/\1))', description)

def main(component):
    try:
        with open('version_diff.json') as f:
            data = json.load(f)[component]
    except Exception:
        return "err no info"
    release = data['release']
    owner = release['owner']
    repo = release['repo']
    
    if component in ['gvisor_containerd_shim','gvisor_runsc']:
        name = release.get('name')
        release_url = 'https://github.com/google/gvisor/releases/tag/%s' % name
        pr_body = f"""
### {name}

**URL**: [Release]({release_url})

**
        """
        commits = get_commits(name, release)
        if commits:
            pr_body += commits
    else:
        name = release['tagName']
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
**URL**: [Release Notes]({release_url})

#### Description:
{description}
        """
        commits = get_commits(name, release)
        if commits:
            pr_body += commits
    return pr_body.strip()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pull Request body generator')
    parser.add_argument('--component', required=True, help='Specify the component to process')
    args = parser.parse_args()
    
    main(args.component)
