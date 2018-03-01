# Contributing

## Overview

This guide will show you how to submit issues, suggestions, feature requests,
and wiki corrections to the PokeAlarm team.

* [Before You Begin](#before-you-begin)
* [Introduction](#introduction)
* [Submitting an Issue](#submitting-an-issue)
* [Submitting a Pull Request](#submitting-a-pull-request)
* [Submitting a change to the to the readthedocs](#submitting-a-change-to-the-readthedocs)

## Before You Begin

If you're trying to troubleshoot an issue that you're having that may not be a
issue needing to be fixed within PokeAlarm itself, try visiting the PokeAlarm
[#troubleshooting](https://discord.gg/S2BKC7p) channel on Discord.

## Introduction

There are two ways to submit information to the PokeAlarm Github, each with
its own template to be used.
* An [Issue](https://github.com/PokeAlarm/PokeAlarm/issues) can be submitted to
  draw attention to a bug that needs to be fixed, to request a new feature, or
  to give suggestions.
* If you know how to implement fix or a change that you'd like to see, you can
  submit a [Pull Request](https://github.com/PokeAlarm/PokeAlarm/pulls).

## Submitting an Issue

1. From within the master branch of PokeAlarm, click on the Issues tab.
2. Click on the green button labeled "New issue".
3. Create a relevant title for your submission.
4. There are two templates preloaded into the Issue submission box - one for
   bugs and user issues and the other for enhancements and suggestions. All
   submissions do require the use of a template in order to be considered.
   Make sure to address only one issue per submission. Copy the applicable
   template and remove the one that you do not need.
5. Click on "Submit new issue" button when finished.

## Submitting a Pull Request

Pull Requests (PRs) are submitted through the `dev` branch of PokeAlarm to be
tested prior to being included in periodic patches merged to the Master branch.
All coding to be considered must meet PEP 8 standards for Python and should
be checked using [Flake8](http://flake8.pycqa.org/en/latest/index.html).

Our development team utilizes Travis CI for automated testing. Travis CI is a
continuous integration service that checks for issues when PRs are first opened
and when commits are added to them. Feedback on PRs will typically be given
within 4 days from the date of the initial submission, excluding holidays. If
changes are requested, please comment on the PR when those changes have been
completed.

Please keep your PR up to date so that we can pull it without conflicts. For
clean git histories, use `rebase` instead of merging. To do this:

```
git fetch origin
git rebase -i origin/dev
(comment out all the commits that aren't related to yours)
(handle any conflicts that arise from rebase)
git push <personal_remote> <branch_name>
```

## Submitting a change to the readthedocs

Submissions for changes to the readthedocs are to be made through Pull Requests
on the [PokeAlarm](https://github.com/PokeAlarm/PokeAlarm) repository, all the
readthedocs files are inside `docs` folder.

The Wiki consists of files written using
[Markdown](https://help.github.com/articles/basic-writing-and-formatting-syntax/)
or [reStructuredText](http://docutils.sourceforge.net/docs/user/rst/quickref.html),
saved with the `.md`/`.rst` file extension.

1. From within the Master branch of the PokeAlarm repo, click on the **Branch**
   dropdown and choose `dev` from the menu.
2. Once the dev branch page loads, click the `New Pull Request` button.
3. Add a title for your request and include some information about your
   submission in the textbox.
4. Upload a new or updated file and click `Create Pull Request`.
