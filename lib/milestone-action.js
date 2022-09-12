const core = require('@actions/core');
const github = require('@actions/github');
const { inspect } = require("util");

async function run() {

  try {

    const repository = core.getInput('repository');
    console.log(`Get Repository: ${repository}`);

    const milestoneName = core.getInput('milestone_name');
    console.log(`Get Milestone Name: ${milestoneName}`);

    const token = core.getInput('token');
    const octokit = github.getOctokit(token);
    console.log(`Get token and configured`);

    const response = await octokit.request(`GET /repos/${repository}/milestones`);
    for (const milestone of response.data) {
      if (milestone.title === milestoneName) {
        console.log(`Found ${inspect(milestone)} for ${milestoneName}`);
        core.setOutput('data', milestone);
        return;
      }
    }

    throw Error(`unable to find milestone ${milestoneName}`)

  } catch (error) {

    core.setFailed(error.message);

  }

}

run();