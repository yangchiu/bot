# Qase Sync composite action

Sync manual test cases between github and qase.

## Inputs

## `project-code`

**Required** Code of project, where to sync test cases.

## `token`

**Required** Qase API token.

## Example usage

```
steps:
  - name: Qase Sync
    uses: longhorn/bot/qase-sync-action@master
    with:
      project-code: ${{ secrets.PROJECT_CODE }}
      token: ${{ secrets.QASE_TOKEN }}
```
