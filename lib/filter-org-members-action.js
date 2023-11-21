const core = require('@actions/core')
const github = require('@actions/github')

run()

async function run() {

    try {

        const api = github.getOctokit(core.getInput("token", { required: true }), {})

        const organization = core.getInput("organization")
        const usernames = core.getInput("usernames").split(",").map(s => s.trim())

        console.log(`Will check if input users belong to org ${organization}`)

        const query = `query($cursor: String, $org: String!, $userLogins: [String!], $username: String!)  {
            user(login: $username) {
                id
            }
            organization(login: $org) {
                teams (first:1, userLogins: $userLogins, after: $cursor) {
                    nodes {
                        name
                    }
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                }
            }
        }`

        let members = []

        for (let username of usernames) {

            // Check if the user exists, If user doesn't exist graphql will throw an exception
            try {
                data = await api.graphql(query, {
                    "org": organization,
                    "userLogins": [username],
                    "username": username
                })
                console.log(`${username} query result is ${JSON.stringify(data)}`)

                // If user doesn't belong to the org, teams array will be empty
                if (data.organization.teams.nodes.length > 0) {
                    members.push(username)
                }

            } catch (error) {
                console.log(error)
            }

        }

        core.setOutput("members", members)

    } catch (error) {
        console.log(error)
        core.setFailed(error.message)
    }
}
