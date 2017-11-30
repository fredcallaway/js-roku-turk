const express = require('express')
const path = require('path')
const PORT = process.env.PORT || 5000
const uri = 'mongodb://heroku_c7z5dkq0:bka4iihnu3eueq3as4347qtr1p@ds125146.mlab.com:25146/heroku_c7z5dkq0'

var bodyParser = require('body-parser');

var MongoClient = require('mongodb').MongoClient
var utils = require('./utils.js')

async function main() {
  // Use connect method to connect to the server
  console.log('Connecting to database.')
  var db = await MongoClient.connect(uri)
    .then(function(db) {
      console.log("Connected successfully to server");
      return db
    })
    .catch(err => {
      console.log(err.stack);
    })

  express()
    .use(express.static(path.join(__dirname, 'public')))
    .use(bodyParser.json())
    .use('/jsPsych', express.static(__dirname + "/jsPsych"))
    .set('views', path.join(__dirname, 'views'))
    .set('view engine', 'ejs')
    .get('/', (req, res) => res.render('pages/go_no_go', {cond: 2}))
    .post('/experiment-data', (req, res) => {
      console.log('body', req.body);
      db.collection('test').insertOne({'data': req.body})
        .then((x) => {
          db.close();
          res.end()
        })
        .catch((err) => console.log(err.stack))
    })
    .listen(PORT, () => console.log(`Listening on ${ PORT }`))  

}

main();
