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

    console.log(`unable to find milestone ${milestoneName}, create a new one`);
    const create_response = await octokit.request(`POST /repos/${repository}/milestones`, {
      title: milestoneName
    });
    if (create_response.status === 201) {
      console.log(`Create new milestone: ${inspect(create_response.data)}`);
      core.setOutput('data', create_response.data);
      return;
    }

    throw Error(`unable to find/create milestone ${milestoneName}: ${inspect(create_response)}`);

  } catch (error) {

    core.setFailed(error.message);

  }

}

run();