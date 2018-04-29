# Contributing

## Table of Contents

* [Reporting Issues](#reporting-issues):
  * [Support or Bugs](#support-or-bugs)
  * [Feature Requests](#feature-requests)
* [Contibuting Changes](#contributing-changes):
  * [Updating Wiki](#updating-wiki)
  * [Submitting PRs](#submitting-prs)

## Reporting Issues

If you have a quick support question, PA's Discord is the best place for
quick turnaround.

If you would like to request a feature, report a suspected bug, or
didn't find a solution to your support question you should open an Issue
on our Github page.

### Support or Bugs
If you believe you've found a bug or need help setting up or configuring
PA, please copy and paste the below template for your bug.

We'll generally respond within a day, but garentee a response within 4
days. Requests for more information that are not responsed to within 7
days will be closed.

```
## Troubleshooting Checklist
<!-- Mark items as completed with a single 'x' inside them, ex: [x] --->
- [ ] My Scanner install is at the most recent version.
- [ ] My PokeAlarm install is at the most recent version.
- [ ] I've already checked the
 [FAQ](https://github.com/RocketMap/PokeAlarm/wiki/faq) and the
 [Wiki](https://github.com/RocketMap/PokeAlarm/wiki) already.

## Problem Description
<!--  Please leave a detailed description of the issue experienced  --->


## Environment
Operating System: ` YOUR OPERATING SYSTEM HERE `
Python Version: ` (obtained from `python -V`) `
PokeAlarm Branch: ` ex: master, dev, other `
PokeAlarm Version: ` (`git rev-parse HEAD` inside PA folder) `
Scanner used: `TYPE/FORK OF SCANNER HERE`


## PokeAlarm Setup:
<!-- Please include links to the following configuration files --->
<!-- Feel free to use HasteBin or a similar service  -->
<!-- Make sure to remove or censor any personal info or API keys -->
Your config file: <!-- LINK TO CONFIG.INI GOES HERE --->
Your filters file: <!-- LINK TO FILTERS.JSON GOES HERE --->
Your alarms file:  <!-- LINK TO ALARMS.JSON GOES HERE --->


## Log Output
<!-- If your issue occurs in the output, provide a link here --->
<!-- Please provide the ENTIRE log - minus any personal info --->

```

### Feature Requests

If you have a suggestion or would like to request a feature, please
use Github. Using Discord is NOT a good alternative - it's often
infeasible for us to read every message, but using Github garentees we
we will see and process your request.

Please copy and paste the following for requests:
```
## Description
<!--  Describe the feature you would like to see added to PokeAlarm --->

## Why is this enhancement necessary or useful?
<!--  Describe why this enhancement is necessary or useful to users --->

## How can this enhancement be accomplished?
<!-- Provide anything relevant such as links to helpful libraries --->

```

## Contributing Changes

PA is more than happy to accept PRs from the community. We ask that you
please keep PRs as small as possible and restricting to a single
feature to keep our development quick.

Please submit all PR's to the 'dev' branch - this branch is our beta
branch, and is periodically merged into master via 'Patches'. After a
patch, the 'dev' branch is reset back to the master and work begins a
new.

We'll garentee an intial review of your PR within 4 days of submission.
In return, we ask that you respond to feedback and keep the PR rebased
within at least once every 7 days. Please make sure to rebase and not
just merge - see this
[article](https://www.atlassian.com/git/tutorials/merging-vs-rebasing)
for differences.

For additional questions, please feel free to use the #beta channel in
Discord.

### Updating Wiki

If you are not a techincal user but you would like to improve our
documentation, feel free to use the 'Edit on Github' button to quickly
submit PRs to a specific page on the wiki.

### Submitting PRs

When submitting a change, your code will need to pass our Travic CI
(Continous Integration) testing.

When submitting a PR, please use the following template:
```
## Description
<!-- In detail, describe what your PR adds to PokeAlarm -->

## Type of Change
<!-- Place a single 'x' into the correct box, ex: [x] -->
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (would cause existing functionality to change)

## Motivation and Context
<!---
 Why is this change required? What problem does it solve?
 If it fixes an open issue, please link to the issue here.
-->

## How Has This Been Tested?
<!---
 Please describe in detail how you tested your changes. Make sure to
 describe what tests you have performed, your testing environment,
 and if you have used this in a production setting. Please add
 screenshots if appropriate.
-->

## Wiki Update
<!--
 Does this feature require an update to the wiki? If so, please submit
 the required change to https://github.com/RocketMap/PokeAlarmWiki.
 If your feature requires a wiki update, you may submit it for review
 but it will not be accepted until the wiki update is complete.
--->
- [ ] This change requires an update to the Wiki.
- [ ] This change does not require an update to the Wiki.
```
