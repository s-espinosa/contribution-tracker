import json
import sys
from os import path
from github import Github

# https://api.github.com/orgs/{org_name}/members
# https://api.github.com/orgs/{org_name}/members/member
# https://api.github.com/orgs/{org_name}/repos
# https://api.github.com/repos/{org_name}/{repo_name}/git/commits
# https://api.github.com/repos/{org_name}/{repo_name}/contributors
# https://api.github.com/repos/{org_name}/{repo_name}/collaborators
# https://api.github.com/repos/{org_name}/{repo_name}/collaborators/{collaborator_name}

users_file = open('users.json', 'r')
global_users = json.loads(users_file.read())

def repo_stats(repo):
    emails = {}
    contribs = {}
    for contributor in repo.get_contributors():
        login = contributor.login.lower()
        if login not in contribs:
            contribs[login] = {
                'name': contributor.name,
                'authored': {
                    'add': 0,
                    'del': 0,
                    'total': 0,
                },
                'co-authored': {
                    'add': 0,
                    'del': 0,
                    'total': 0,
                },
            }
        anon_email = f'{contributor.id}+{login}' \
                     f'@users.noreply.github.com'.lower()
        contribs[login]['emails'] = [anon_email]
        emails[anon_email] = login
        if contributor.email is not None:
            email = contributor.email.lower()
            contribs[login]['emails'].append(email)
            emails[email] = login

    if len(emails) > 0:
        print('known contributors:')
        for email, login in emails.items():
            print(f'  {email}: {login}')

    users = []
    commits = repo.get_commits().reversed
    print(f'processing {commits.totalCount} commits:')
    for commit in commits.reversed:
        print('.', end='', flush=True)
        message = commit.commit.message
        stats = commit.stats
        users.append(commit.committer)
        user = commit.committer

        if user is None:
            continue
        login = user.login.lower()

        if login == 'web-flow':
            # print(message)
            # print('skipping stats since it was a github web merge')
            # if login not in contributors:
            #     contributors[login] = {
            #         'web merges': 0
            #     }
            # contributors[login]['web merges'] += 1
            continue

        # print(f'commit by {user.login}')
        contribs[login]['authored']['add'] += stats.additions
        contribs[login]['authored']['del'] += stats.deletions
        contribs[login]['authored']['total'] += stats.total

        for line in message.split("\n"):
            email = None
            if 'Co-authored-by' in line:
                email = line.split('<')[1].split('>')[0].lower()
                login = None
                if email in emails:
                    if emails[email] == user.login.lower():
                        continue
                else:
                    if email not in global_users:
                        print('found a contributor email that did not match:')
                        print(line)
                        login = input(f'enter github username for {email}: ')
                        emails[email] = login.strip().lower()
                        remember = input('remember for next time? y/n ')
                        remember = remember.strip().lower()
                        if remember == 'y':
                            global_users[email] = login
                            f = open('users.json', 'w')
                            f.write(json.dumps(global_users, sort_keys=True,
                                               indent=2))
                            f.close()
                    emails[email] = global_users[email]
                co_author = emails[email]
                if co_author not in contribs:
                    contribs[co_author] = {
                        'login': co_author,
                        'authored': {
                            'add': 0,
                            'del': 0,
                            'total': 0,
                        },
                        'co-authored': {
                            'add': 0,
                            'del': 0,
                            'total': 0,
                        },
                    }
                contribs[co_author]['co-authored']['add'] += stats.additions
                contribs[co_author]['co-authored']['del'] += stats.deletions
                contribs[co_author]['co-authored']['total'] += stats.total

    details = {
        'archived': repo.archived,
        'contributors': contribs
    }


    return details


if __name__ == '__main__':
    if path.exists('auth.py'):
        from auth import access_token
    else:
        print('create auth.py with the following inside it:')
        print('')
        print('access_token = "<token>"')
        print('')
        print('(replace <token> with an actual personal token created at')
        print('https://github.com/settings/tokens/new and give it full "repo"')
        print('and "admin:org" scopes)')
        sys.exit()

    repo_or_org = input('Enter GitHub Organization or Repo URL, ie "turingschool" or "turingschool/backend-curriculum-site": ')
    repo_or_org = repo_or_org.strip()
    # repo_or_org = "My-Solar-Garden/hardware"

    print(f'Checking {repo_or_org} for access...')

    g = Github(access_token)

    repo = None
    org = None
    stats = {}

    if '/' in repo_or_org:
        print('getting stats for single repo')
        repo = g.get_repo(repo_or_org)
        stats = repo_stats(repo)
    else:
        print('getting stats for organization')
        org = g.get_organization(repo_or_org)
        for repo in org.get_repos():
            stats[repo.name] = repo_stats(repo)

    print('')
    print(json.dumps(stats, sort_keys=True, indent=2))


# contents = repo.get_top_paths()
#
# contents = repo.get_top_referrers()
#
# sha = 'abc123'
# commit = repo.get_commit(sha=sha)

# https://api.github.com/orgs/{org_name}/members
# https://api.github.com/orgs/{org_name}/members/member
# https://api.github.com/orgs/{org_name}/repos
# https://api.github.com/repos/{org_name}/{repo_name}/git/commits
# https://api.github.com/repos/{org_name}/{repo_name}/contributors
# https://api.github.com/repos/{org_name}/{repo_name}/collaborators
# https://api.github.com/repos/{org_name}/{repo_name}/collaborators/{collaborator_name}