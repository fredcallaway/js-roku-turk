
// Replace this with the output of:
// heroku config:get MONGODB_URI
var uri = process.env.MONGODB_URI;

const express = require('express');
const path = require('path');
const PORT = process.env.PORT || 5000;

async function main() {
  console.log('Connecting to database...')
  
  var db = await require('mongodb').MongoClient.connect(uri)
    .then(function(db) {
      console.log('Sucess!');
      return db
    })
    .catch(err => {
      console.log(err.stack);
      console.log('Continuing experiment without a database.')
      // In a real exeriment, you would ask the worker to 
      // email you reporting the erro and return
      // the HIT.
    })

  var params = {
    condition: 2,
    images: require('fs').readdirSync('public/img/').map(x => 'img/'+x)
  }

  express()
    .use(express.static(path.join(__dirname, 'public')))
    .use(require('body-parser').json())
    .set('views', path.join(__dirname, 'views'))
    .set('view engine', 'ejs')
    
    .get('/', (req, res) => res.render('pages/go_no_go', {
      PARAMS: JSON.stringify(params)
    }))
    
    .post('/experiment-data', (req, res) => {
      if (db) {
        db.collection('test').insertOne({'data': req.body})
          .then((x) => {
            db.close();
            res.end()
          })
          .catch((err) => console.log(err.stack))
      }
      else console.log('No connection to database.')
    })

    .listen(PORT, () => console.log(`Listening on ${ PORT }`))  

}

main();
