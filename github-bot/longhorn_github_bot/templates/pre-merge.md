
## Pre Ready-For-Testing Checklist
* [ ] Where is the reproduce steps/test steps documented?
The reproduce steps/test steps are at:

* [ ] Is there a workaround for the issue? If so, where is it documented?
The workaround is at:

* [ ] Does the PR include the explanation for the fix or the feature?

* [ ] Does the PR include deployment change (YAML/Chart)? If so, where are the PRs for both YAML file and Chart?
The PR for the YAML change is at:
The PR for the chart change is at:

* [ ] Have the backend code been merged (Manager, Engine, Instance Manager, BackupStore etc) (including `backport-needed/*`)?
The PR is at

* [ ] Which areas/issues this PR might have potential impacts on?
Area
Issues

* [ ] **If labeled: require/LEP** Has the Longhorn Enhancement Proposal PR submitted?
The LEP PR is at

* [ ] **If labeled: area/ui** Has the UI issue filed or ready to be merged (including `backport-needed/*`)?
The UI issue/PR is at

* [ ] **If labeled: require/doc** Has the necessary document PR submitted or merged (including `backport-needed/*`)?
The documentation issue/PR is at

* [ ] **If labeled: require/automation-e2e** Has the end-to-end test plan been merged? Have QAs agreed on the automation test case? If only test case skeleton w/o implementation, have you created an implementation issue (including `backport-needed/*`)
The automation skeleton PR is at
The automation test case PR is at 
The issue of automation test case implementation is at (please create by [the template](https://github.com/longhorn/longhorn/issues/new?assignees=&labels=area%2Ftest&template=test.md&title=%5BTEST%5D))

* [ ] **If labeled: require/automation-engine** Has the engine integration test been merged (including `backport-needed/*`)?
The engine automation PR is at

* [ ] **If labeled: require/manual-test-plan** Has the manual test plan been documented?
The updated manual test plan is at

* [ ] **If the fix introduces the code for backward compatibility** Has a separate issue been filed with the label `release/obsolete-compatibility`?
The compatibility issue is filed at
