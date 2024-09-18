import os
import re
import json
import argparse
import requests
from dependency_updater_config import component_info

github_api_url = "https://api.github.com/graphql"
gh_token = os.getenv('GH_TOKEN')

def process_version_string(component, version):
    if component in ['youki', 'nerdctl', 'cri_dockerd', 'containerd']:
        if version.startswith('v'):
            version = version[1:]
    match = re.search(r'release-(\d{8})', version)
    if match:
        version = match.group(1)
    return version

def get_commits(release, repo_version, number_of_commits=5):
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
        """ % (owner, repo, repo_version, number_of_commits)
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
        """ % (owner, repo, repo_version, number_of_commits)
    headers = {"Authorization": f"Bearer {gh_token}"}
    response = requests.post(github_api_url, json={'query': query}, headers=headers)
    if response.status_code == 200:
        data = response.json()
        pr_commits = "<details>\n<summary>Commits</summary>\n\n"
        commits = data["data"]["repository"]["ref"]["target"]["target"]["history"]["edges"]
        for commit in commits:
            node = commit["node"]
            short_oid = node['oid'][:7]
            commit_message = node['message'].split("\n")[0]
            commit_url = node['url']
            pr_commits += f"[{short_oid}]({commit_url}) {commit_message}  \n"
        pr_commits += "\n</details>"

        return pr_commits
    else:
        return None

def link_pull_requests(description, repo_url):
    return re.sub(r'\(#(\d+)\)', rf'([#\1]({repo_url}/pull/\1))', description)

def main(component, current_version, latest_version, release):
    repo_url = "https://github.com/%s/%s" % (release['owner'], release['repo'])
    if component in ['gvisor_containerd_shim','gvisor_runsc']:
        name = release.get('name')
        repo_version = release.get('repo_version', 'release-20240826.0')
        url = "https://github.com/google/gvisor/releases/tag/%s" % repo_version
        pr_body = f"""
        ### {name}
        
        **URL**: [Release]({url})

        **
        """
        commits = get_commits(name, release)
        if commits:
            pr_body += commits
    else:
        name = release.get('tagName')
        tag_name = release.get('tagName')
        published_at = release.get('publishedAt')
        url = release.get('url')
        description = release.get('description')
        description = link_pull_requests(description, repo_url)
        pr_body = f"""
        ### {name}

        **Tag**: {tag_name}  
        **Published at**: {published_at}  
        **URL**: [Release Notes]({url})

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
    parser.add_argument('--current_version', required=True, help='Specify the current version')
    parser.add_argument('--latest_version', required=True, help='Specify the latest version')
    parser.add_argument('--release', required=True, help='Release json from Github GraphQL')
    args = parser.parse_args()
    release = json.loads(args.release)

    main(args.component, args.current_version, args.latest_version, release)
