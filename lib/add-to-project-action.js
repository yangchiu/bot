const core = require('@actions/core')
const github = require('@actions/github')

const urlParse = /\/(?<ownerType>orgs|users)\/(?<ownerName>[^/]+)\/projects\/(?<projectNumber>\d+)/

async function addToProject() {
  const projectUrl = core.getInput('project-url', {required: true})
  const contentId = core.getInput('issue-node-id', {required: true})
  const octokit = github.getOctokit(core.getInput('github-token', {required: true}))

  core.debug(`Trying to add issue ${contentId} to project ${projectUrl}`)

  const urlMatch = projectUrl.match(urlParse)
  if (!urlMatch) {
    throw new Error(
      `Invalid project URL: ${projectUrl}. Project URL should match the format <GitHub server domain name>/<orgs-or-users>/<ownerName>/projects/<projectNumber>`,
    )
  }

  const projectOwnerName = urlMatch.groups.ownerName
  const projectNumber = parseInt(urlMatch.groups.projectNumber)
  const ownerTypeQuery = mustGetOwnerTypeQuery(urlMatch.groups.ownerType)

  core.debug(`Project owner: ${projectOwnerName}`)
  core.debug(`Project number: ${projectNumber}`)
  core.debug(`Project owner type: ${ownerTypeQuery}`)

  // First, use the GraphQL API to request the project's node ID.
  const idResp = await octokit.graphql (
    `query getProject($projectOwnerName: String!, $projectNumber: Int!) {
      ${ownerTypeQuery}(login: $projectOwnerName) {
        projectV2(number: $projectNumber) {
          id
        }
      }
    }`,
    {
      projectOwnerName,
      projectNumber,
    },
  )

  const projectId = idResp[ownerTypeQuery]?.projectV2.id
  core.debug(`Project node ID: ${projectId}`)

  // Next, use the GraphQL API to add the issue to the project.
  const addResp = await octokit.graphql (
    `mutation addIssueToProject($input: AddProjectV2ItemByIdInput!) {
      addProjectV2ItemById(input: $input) {
        item {
          id
        }
      }
    }`,
    {
      input: {
        projectId,
        contentId,
      },
    },
  )

  core.setOutput('itemId', addResp.addProjectV2ItemById.item.id)
}

function mustGetOwnerTypeQuery(ownerType) {
  const ownerTypeQuery = ownerType === 'orgs' ? 'organization' : ownerType === 'users' ? 'user' : null

  if (!ownerTypeQuery) {
    throw new Error(`Unsupported ownerType: ${ownerType}. Must be one of 'orgs' or 'users'`)
  }

  return ownerTypeQuery
}

addToProject()