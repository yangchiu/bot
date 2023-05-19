# Copy files and create pull request in another repository 

Copy files from the current repository to a location in another repository and create a pull request.

## Inputs

## `source_folder` ./k8s/.

**Required** 

## `destination_repo`

**Required** 

## `destination_folder`

**Required**

## `destination_base_branch`

## `destination_head_branch`

**Required**

## `user_email`

**Required**

## `user_name`

**Required**

## `pull_request_reviewers`

## `pr_title`

**Required**

## `commit_msg`

**Required**

## Environment Variables

## `API_TOKEN_GITHUB`

**Required** 

## Example usage
```
steps:
  - name: Create pull request 
    uses: longhorn/bot/copy-files-and-create-pr-action@master 
    env:
      API_TOKEN_GITHUB: ${{ secrets.API_TOKEN_GITHUB }}
    with:
      source_folder: 'source-folder'
      destination_repo: 'user-name/repository-name'
      destination_folder: 'folder-name'
      destination_base_branch: 'branch-name'
      destination_head_branch: 'branch-name'
      user_email: 'user-name@example.com'
      user_name: 'user-name'
      pull_request_reviewers: 'reviewers'
      pr_title: 'pr-title'
      commit_msg: 'commit-msg'
```