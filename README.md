# js-roku-turk
This guide will (hopefully) help you set up an online experiment using JavaScript, Heroku and Mechanical Turk.

## Preliminaries
We have to install some stuff before we can begin. Remember, nothing good comes easy.

### The language: Node.js
Node.js is a server-side version of JavaScript. NPM is the standard package manager for Node. You can install both [here](https://nodejs.org/en/download/).

### The platform: Heroku
Herkou is a cloud application platform with a generous free tier. Sign up [here](https://signup.heroku.com/). Then follow the setup instructions [here](https://devcenter.heroku.com/articles/getting-started-with-nodejs#set-up). **Don't continue to the next page!**

Now we can create a Heroku app based on the example experiment in this repo

    cd experiment
    herkou create
    git push heroku master
    heroku ps:scale web=1
    heroku open

### The Database: MongoDB with mLab
We'll store our data in a MongoDB database. We can set one up easily with Heroku. Unfortunately, you need to verify your account to sign up, and that involves giving Heroku a credit/debit card number. I'm *pretty* sure that they won't ever charge you if you don't sign up for a non-free plan.

To go this route, try running the following commands. The last line prints the location of the database.  

    heroku addons:create mongolab
    heroku addons:create mongolab
    heroku config:get MONGODB_URI

Alternatively, I am told that you can sign up for an mLab database directly [here](https://mlab.com/). However, it's not quite as easy as going through Heroku.

# Developing your experiment
1. Have an idea for an awesome experiment.
2. Bang your head on your keyboard for a few hours/weeks.
3. Citations.

Links:
- http://docs.jspsych.org/

# Deploying your experiment

    git subtree push --prefix experiment heroku master
    git push heroku `git subtree split --prefix output master`:master --force

# Fetching and processing data

    heroku addons:open mongolab
