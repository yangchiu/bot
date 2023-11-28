# Add an issue to a project

Add an issue to a project.

## Inputs

## `project-url`

**Required** project url

## `issue-node-id`

**Required** issue node id

## `github-token`

**Required** the personal access token to be used

## Example usage
```
steps:
  - name: Add to project
    uses: longhorn/bot/add-to-project-action@master 
    with:
      project-url: https://github.com/orgs/longhorn/projects/4
      issue-node-id: "MDU6SXNzdWUx"
      github-token: ${{ secrets.CUSTOM_GITHUB_TOKEN }}
```
