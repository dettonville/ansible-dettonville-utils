# dettonville.utils.git_pacp

**Perform git operations including: 'clone', 'pull', 'acp', and 'pacp' (pull, add, commit and push).**

Version added: 1.0.0

-   [Synopsis](https://github.com/dettonville/ansible.utils/blob/main/docs/dettonville.utils.git_pacp.md#synopsis)
-   [Parameters](https://github.com/dettonville/ansible.utils/blob/main/docs/dettonville.utils.git_pacp.md#parameters)
-   [Notes](https://github.com/dettonville/ansible.utils/blob/main/docs/dettonville.utils.git_pacp.md#notes)
-   [Examples](https://github.com/dettonville/ansible.utils/blob/main/docs/dettonville.utils.git_pacp.md#examples)
-   [Return Values](https://github.com/dettonville/ansible.utils/blob/main/docs/dettonville.utils.git_pacp.md#return-values)
-   [Status](https://github.com/dettonville/ansible.utils/blob/main/docs/dettonville.utils.git_pacp.md#status)

## [Synopsis](https://github.com/dettonville/ansible.utils/blob/main/docs/dettonville.utils.git_pacp.md#synopsis)

- Perform git operations including: 'clone', 'pull', 'acp', and 'pacp' (pull, add, commit and push).

## [Parameters](https://github.com/dettonville/ansible.utils/blob/main/docs/dettonville.utils.git_pacp.md#parameters)

| Parameter | Choices | Default | Configuration | Comments |
| --- | --- | --- | --- | --- |
| **path** raw / required |  |  |  | Folder path where git repo C(.git/) is located.
| **action** | [ 'clone', 'pull', 'pacp', 'acp' ] | 'pacp' |  | Git operation to perform - 'clone', 'pull', 'pacp'(Pull + Add + Commit + Push), or 'acp' (Add + Commit + Push)
| **comment** |  |  |  | Git commit comment. Same as C(git commit -m).<br>Required if action performs commit (e.g., if action in ['pacp', 'acp'])
| **add** |  | ["."] |  | List of files under C(path) to be staged. Same as C(git add .).<br>File globs not accepted, such as C(./*) or C(*).
| **user** |  |  |  | Git username for https operations.
| **token** |  |  |  | Git API token for https operations.
| **branch** |  | 'main' |  | Git branch where perform git push.
| **push_option** |  |  |  | Git push options. Same as C(git --push-option=option).
| **mode** | ['ssh', 'https', 'local']  |  |  | Git mode to perform operations. Either over ssh, https or local.<br>If not specified, the mode will be set to the scheme implied by the URL.
| **url** |  |  |  | Git repo URL.
| **ssh_params** |  |  |  | Dictionary containing SSH parameters.
| **executable** |  |  |  | Path to git executable to use. If not supplied, the normal mechanism for resolving binary paths will be used.
| **remote** |  |  |  | Local system alias for git remote PUSH and PULL repository operations.
| **user_name** |  |  |  | Explicit git local user name. Nice to have for remote operations.
| **user_email** |  |  |  | Explicit git local email address. Nice to have for remote operations.
| **logging_level** | ['NOTSET', 'DEBUG', 'INFO', 'ERROR']  | 'INFO' |  | Parameter used to define the level of troubleshooting output.


## [Examples](https://github.com/dettonville/ansible.utils/blob/main/docs/dettonville.utils.git_pacp.md#examples)

```yaml
- name: "Perform git pull/add/commit/push"
  git_pacp:
    url: "{{ __test_git_repo_url }}"
    path: "{{ __test_git_repo_dir }}"
    branch: "{{ __test_git_repo_branch }}"
    comment: "{{ __git_comment }}"
    ssh_params: "{{ __test_git_ssh_params }}"
  register: git_pacp_result

- name: "Perform git pull/add/commit/push"
  git_pacp:
    action: pacp
    url: "{{ __test_git_repo_url }}"
    path: "{{ __test_git_repo_dir }}"
    branch: "{{ __test_git_repo_branch }}"
    comment: "{{ __git_comment }}"
    ssh_params: "{{ __test_git_ssh_params }}"
  register: git_pacp_result

- name: "Pull latest repo changes into {{ __test_git_repo_dir }}"
  git_pacp:
    action: pull
    path: "{{ __test_git_repo_dir }}"
    branch: "{{ __test_git_repo_branch }}"
    url: "{{ __test_git_repo_url }}"
    ssh_params: "{{ __test_git_ssh_params }}"
  register: git_pull_result

- name: "Perform git add/commit/push"
  git_pacp:
    action: acp
    url: "{{ __test_git_repo_url }}"
    path: "{{ __test_git_repo_dir }}"
    branch: "{{ __test_git_repo_branch }}"
    comment: "{{ __git_comment }}"
    ssh_params: "{{ __test_git_ssh_params }}"
  register: git_pacp_result

- name: SSH | add/commit/push file1.
  git_pacp:
    path: /Users/git/git_pacp
    branch: master
    comment: Add file1.
    add: [ file1 ]
    remote: dev_test
    mode: ssh
    url: "git@gitlab.com:networkAutomation/git_test_module.git"
    user_name: ansible
    user_email: ansible@dettonville.org

- name: HTTPS | add/commit/push all file changes
  git_pacp:
    user: dettonville
    token: mytoken
    path: /Users/git/git_pacp
    branch: master
    comment: Add file1.
    remote: origin
    add: [ '.' ]
    url: "https://gitlab.com/networkAutomation/git_test_module.git"

- name: SSH with private key | add file1.
  git_pacp:
    path: /Users/git/git_pacp
    branch: master
    comment: Add file1.
    add: [ file1  ]
    remote: dev_test
    mode: ssh
    url: "git@gitlab.com:networkAutomation/git_test_module.git"
    ssh_params:
      accept_hostkey: true
      key_file: '~/.ssh/id_rsa'
      ssh_opts: '-o UserKnownHostsFile={{ remote_tmp_dir }}/known_hosts'

- name: LOCAL | push on local repo.
  git_pacp:
    path: "~/test_directory/repo"
    branch: master
    comment: Add file1.
    add: [ file1 ]
    mode: local
    url: /Users/mytestuser/test_directory/repo.git

```


## [Status](https://github.com/dettonville/ansible.utils/blob/main/docs/dettonville.utils.git_pacp.md#status)


### [Authors](https://github.com/dettonville/ansible.utils/blob/main/docs/dettonville.utils.git_pacp.md#authors)

-   Lee Johnson (@lj020326)
