# js-roku-turk
This guide will (hopefully) help you set up an online experiment using JavaScript, Heroku and Mechanical Turk. The experiment can be viewed [here](https://pacific-temple-83648.herokuapp.com/).


## Preliminaries
We have to install some stuff before we can begin. Remember, nothing good comes easy.

### The language: Node.js
Node.js is a server-side version of JavaScript. NPM is the standard package manager for Node. You can install both [here](https://nodejs.org/en/download/).

### The platform: Heroku
Herkou is a cloud application platform with a generous free tier. We'll use it to host our experiment.

1. Sign up [here](https://signup.heroku.com/).
2. Download the Heroku Command Line Interface (CLI). You have a few options  
    - `brew install heroku/brew/heroku`  
    - `sudo snap install heroku`  
    - `wget -qO- https://cli-assets.heroku.com/install-ubuntu.sh | sh`  
    - GUI (not commandline) installers for [mac](https://cli-assets.heroku.com/heroku-cli/channels/stable/heroku-cli.pkg) and [windows](https://cli-assets.heroku.com/heroku-cli/channels/stable/heroku-cli-x64.exe)
    - [Problems?](https://devcenter.heroku.com/articles/heroku-cli#download-and-install)

### The crowd: MTurk
MTurk is a crowdsourcing platform through which you can recruit hundreds of participants in a matter of hours. I'll assume you already have an account and a system for creating HITs.

One quick note: If you post HITs programmatically (e.g. with the AWS CLI), I strongly suggest using an IAM access key with access only to mturk rather than a root key (the default). I once put a root key in a public github repo and within 12 hours, a bot found it and burned through a few thousand dollars on EC2 instances. *Never again.*


## Initializing the heroku application
With the prereqs out of the way, we can create a new experiment with the following commands. Feel free to replace `my-sweet-experiment` with whatever you like. Note that the public url that you'll send participants to will be https://my-sweet-experiment.herokuapp.com/

    git clone https://github.com/fredcallaway/js-roku-turk my-sweet-experiment
    cd my-sweet-experiment
    touch .env
    heroku create my-sweet-experiment
    npm install
    git subtree push --prefix experiment heroku master
    heroku open

If all goes according to plan, the final command `heroku open` will open a new tab in your browser where you'll see a welcome screen titled "My Sweet Experiment".

If you're curious about the `git subtree` command, this is a
[trick](https://coderwall.com/p/ssxp5q/heroku-deployment-without-the-app-being-at-the-repo-root-in-a-subfolder) we use to embed a heroku project within a larger repository which might contain data and analysis scripts.

## Developing your experiment
Pushing the experiment to heroku takes a while, and it would be a pain if you had to do this every time you wanted to test a change. To view the experiment locally, make sure you are in the `experiment/` directory and run:

    heroku local web

This command starts a local heroku server process, just like the one on heroku's servers that manages the public experiment website. You can now view the experiment at http://localhost:4000 .


TODO: directory layout, JsPsych, go_no_go.js example


## Setting up a MongoDB database
Note: You can temporarily skip this step if you just want to *experiment* with the code on your own computer.

We'll store our data in a MongoDB database operated by [mLab](https://mlab.com/). It's easy to set up a database using the Heroku add-on system. Unfortunately, using (most) add-ons requires you to verify your account by [adding a credit card](https://dashboard.heroku.com/account/billing). My understanding is that you won't be charged if you don't sign up for a paid service (e.g. by accidentally exceeding the free-tier usage limits).

> Heroku needs to be able to reliably identify and contact our users in the event of an issue. We have found that having a credit card on file provides the most reliable way of obtaining verified contact information. Account verification also helps us with abuse prevention. [(source)](https://devcenter.heroku.com/articles/account-verification)

After you verify your account, you can create a database with the following commands.

    heroku addons:create mongolab
    heroku config:get MONGODB_URI -s >> .env  # for local usage


#### But I don't want to give them my credit card
I am told that you can [sign with mLab directly](https://mlab.com/) without a credit card. I haven't tried this, but I know one person who says it worked flawlessly and another person who had difficulties. If you go this route, you need to add the database uri to the heroku config with the command:

    heroku config:set MONGODB_URI:mongodb://longstringoflettersandnumbers9332





<!-- 
1. Have an idea for an awesome experiment.
2. Bang your head on your keyboard for a few hours/weeks.
3. Citations.
 -->
Links:
- http://docs.jspsych.org/

# Deploying your experiment

    git subtree push --prefix experiment heroku master
    git push heroku `git subtree split --prefix output master`:master --force

# Fetching and processing data

    heroku addons:open mongolab
