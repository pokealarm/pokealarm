# Docker

## Overview

* [Prerequisites](#prerequisites)
* [Introduction](#introduction)
* [Setup](#setup)
  * [Cloning the repo](#cloning-the-repo)
  * [Configuring](#configuring)
  * [Launching PokeAlarm](#launching-pokealarm)
  * [Stopping PokeAlarm](#stopping-pokealarm)
  * [pdating PokeAlarm](#updating-pokealarm)
  * [Changing some PokeAlarm values](#changing-some-pokealarm-values)

## Prerequisites

This guide assumes:

1) You have [Docker](https://docs.docker.com/) installed and running on your machine
2) You have [Docker Compose](https://docs.docker.com/compose/) installed and running on your machine
3) You have [Git](https://git-scm.com/downloads) installed and running on your machine
4) You have read and understood the [Alarms](../configuration/alarms) wiki

Please familiarize yourself with all of the above before proceeding.

## Introduction

By leveraging [Docker](https://docs.docker.com/), we can run PokeAlarm
instances without the need of installing Python, pip or other tools related to it.

This means that you don't have to go through the hassle of managing python and
its multiple versions if you don't feel comfortable doing it, or for any
other reason.

## Setup

### Cloning the repo

The first thing that you need to do is to clone the PokeAlarm repository in
the directory you'd like:

```
git clone https://github.com/PokeAlarm/PokeAlarm.git
```

### Configuring 

Copy the `docker-compose.yml.example` file and rename it to `docker-compose.yml`. Configure PA according 
to the "normal" wiki and comment out the lines in the compose file of the config files 
(alarms, filters, geofence, rules) you are actually using.

### Launching PokeAlarm

We can launch a PokeAlarm container by just executing:

```
docker-compose up -d && docker-compose logs -f
```

If it's the first time you are executing that command, docker will build the PokeAlarm image first. 
That may take a while so be patient. 

When a locally built image is available, docker will launch one docker container named `pokealarm`
in a detached mode (`-d`) and start a second command (`docker-compose logs -f`) to 
see logs from the container. You can always check the current state of the container by running 
`docker-compose ps`.


### Stopping PokeAlarm

Simply execute `docker-compose down`.


### Updating PokeAlarm

Just run `git pull` to update PokeAlarm and make sure to build and restart the container afterwards:

```
docker-compose build --no-cache && docker-compose down && docker-compose up -d && docker-compose logs -f
```

### Changing some PokeAlarm values

Some config values can not be changed via the config.ini due to the docker setup.

#### Port 
To change the default port (`4000`) of PokeAlarm, change the *left* side of the portnumber in the 
docker-compose.yml file.

#### File Settings
If you want to change the name or path of a config file, change it in the docker-compose.yml instead 
in the config.ini. The *left* side of the colon is the path on your host machine.
