# Get milestone javascript action

Get milestone object from milestone name, if the milestone doesn't exist, it would be created automatically.

## Inputs

## `token`

**Required** Github token.

## `repository`

**Required** Github repository to be retrieved.

## `milestone_name`

**Required** Name of the milestone to be retrieved.

## Outputs

## `milestone`

The retrieved milestone object.

## Example usage

uses: longhorn/bot/milestone-action@master
with:
  token: ${{ github.token }}
  repository: ${{ github.repository }}
  milestone_name: v1.4.0