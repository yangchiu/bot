# Filter organization members javascript action

Get list of users belong to a specific organization from an input user list.

## Inputs

## `token`

**Required** Github token.

## `organization`

**Required**

## `usernames`

**Required**

## Example usage

```
steps:
  - name: Get Longhorn Members
    uses: longhorn/bot/filter-org-members-action@master
    id: longhorn-members
    with:
      token: ${{ secrets.CUSTOM_GITHUB_TOKEN }}
      organization: longhorn
      usernames: ${{ github.event.issue.assignees.*.login }}
```
