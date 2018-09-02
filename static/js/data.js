//data.js
//require the Elasticsearch librray
const elasticsearch = require('elasticsearch');
// instantiate an Elasticsearch client
const client = new elasticsearch.Client({
   hosts: [ 'http://localhost:9200']
});
// ping the client to be sure Elasticsearch is up
client.ping({
     requestTimeout: 30000,
 }, function(error) {
 // at this point, eastic search is down, please check your Elasticsearch service
     if (error) {
         console.error('Elasticsearch cluster is down!');
     } else {
         console.log('Everything is ok');
     }
 });

//require Express
const express = require( 'express' );
// instanciate an instance of express and hold the value in a constant called app_1
const app_     = express();
//require the body-parser library. will be used for parsing body requests
const bodyParser = require('body-parser')
//require the path library
const path    = require( 'path' );

// use the bodyparser as a middleware
app_.use(bodyParser.json())
// set port for the app_1 to listen on
app_.set( 'port', process.env.PORT || 3001 );
// set path to serve static files
app_.use( express.static( path.join( __dirname, 'public' )));
// enable CORS
app_.use(function(req, res, next) {
  res.header("Access-Control-Allow-Origin", "*");
  res.header('Access-Control-Allow-Methods', 'PUT, GET, POST, DELETE, OPTIONS');
  res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
  next();
});

// defined the base route and return with an HTML file called tempate.html
app_.get('/', function(req, res){
  res.sendFile('template.html', {
     root: path.join( __dirname, 'views' )
   });
})

// define the /search route that should return elastic search results
app_.get('/search', function (req, res){
  // declare the query object to search elastic search and return only 200 results from the first result found.
  // also match any data where the name is like the query string sent in
  let body = {
    size: 200,
    from: 0,
    query: {
      match: {
          name: req.query['q']
      }
    }
  }
  // perform the actual search passing in the index, the search query and the type
  client.search({index:'scotch.io-tutorial',  body:body, type:'cities_list'})
  .then(results => {
    res.send(results.hits.hits);
  })
  .catch(err=>{
    console.log(err)
    res.send([]);
  });

})
// listen on the specified port
app_ .listen( app_.get( 'port' ), function(){
  console.log( 'Express server listening on port ' + app_.get( 'port' ));
} );

//template.html
// create a new Vue instance
var app = new Vue({
    el: '#app',
    // declare the data for the component (An array that houses the results and a query that holds the current search string)
    data: {
        results: [],
        query: ''
    },
    // declare methods in this Vue component. here only one method which performs the search is defined
    methods: {
        // make an axios request to the server with the current search query
        search: function() {
            axios.get("http://127.0.0.1:3001/search?q=" + this.query)
                .then(response => {
                    this.results = response.data;

                })
        }
    },
    // declare Vue watchers
    watch: {
        // watch for change in the query string and recall the search method
        query: function() {
            this.search();
        }
    }

})