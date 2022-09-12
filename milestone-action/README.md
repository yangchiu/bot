# Get milestone javascript action

Get milestone object from milestone name

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

uses: yangchiu/milestone-action@master
with:
  token: ${{ github.token }}
  repository: ${{ github.repository }}
  milestone_name: v1.4.0