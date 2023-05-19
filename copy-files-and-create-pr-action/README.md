# Copy files and create pull request in another repository 

Copy files from the current repository to a location in another repository and create a pull request.

## Inputs

## `source`

**Required** The file(s) to be moved. Uses the same syntax as the cp command.

## `destination_repo`

**Required** The repository to place the file(s) in.

## `destination`

**Required** The destination path in the destination repository to place the file in.

## `destination_base_branch`

The branch into which you want the pull request merged. Default is master.

## `destination_head_branch`

**Required** The branch to create to push the changes and then open the pull request.

## `pull_request_reviewers`

The pull request reviewers.

## `pr_title`

**Required** The PR title.

## `commit_msg`

**Required** The PR commit message.

## Environment Variables

## `API_TOKEN_GITHUB`

**Required** The personal access token used to create the PR.

## Example usage
```
steps:
  - name: Create pull request 
    uses: longhorn/bot/copy-files-and-create-pr-action@master 
    env:
      API_TOKEN_GITHUB: ${{ secrets.API_TOKEN_GITHUB }}
    with:
      source: 'path/source/file'
      destination_repo: 'user-name/repository-name'
      destination: 'path/dest/file'
      destination_base_branch: 'branch-name'
      destination_head_branch: 'branch-name'
      pull_request_reviewers: 'reviewers'
      pr_title: 'pr-title'
      commit_msg: 'commit-msg'
```
