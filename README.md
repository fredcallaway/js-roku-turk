

# Prep

## The language: Node.js
Node.js is a server-side version of JavaScript. NPM is the standard package manager for Node. You can install both [here](https://nodejs.org/en/download/).

## The platform: Heroku
Herkou is a cloud application platform with a generous free tier. Sign up [here](https://signup.heroku.com/). Then follow the setup instructions [here](https://devcenter.heroku.com/articles/getting-started-with-nodejs#set-up). **Don't continue to the next page!**

Now we can create a Heroku app based on the example experiment in this repo

    cd experiment
    herkou create
    git push heroku master
    heroku ps:scale web=1
    heroku open

## The Database: MongoDB with mLab
We'll store our data in a MongoDB database. We can set one up easily with Heroku. Unfortunately, you need to verify your account to sign up, and that involves giving Heroku a credit/debit card number. I'm *pretty* sure that they won't ever charge you if you don't sign up for a non-free plan.

To go this route, try running the following commands. The last line prints the location of the database.  

    heroku addons:create mongolab
    heroku addons:create mongolab
    heroku config:get MONGODB_URI

Alternatively, I am told that you can sign up for an mLab database directly [here](https://mlab.com/). However, it's not quite as easy as going through Heroku.


    heroku create
    git push heroku master
    heroku open

# JS development
jsPsych
http://docs.jspsych.org/

package management
http://dontkry.com/posts/code/using-npm-on-the-client-side.html
http://wesbos.com/javascript-modules/


# Data Analysis

    heroku addons:open mongolab

# ToDo
- consent
