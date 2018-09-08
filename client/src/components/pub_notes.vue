<template>

  <!--<head>-->
    <!--<meta charset="UTF-8">-->
    <!--<link rel="shortcut icon" href=" url_for('static', filename='favicon.ico')">-->
    <!--block title-->

    <!--endblock-->

    <!--include 'base_htmls/html_dependencies.html'-->

  <!--</head>-->
  <body id="BODY_BASE">
  <div class="container" id="myDIV1">
    <div class="row">
      <div class="">
        <h1><i class="fas fa-spinner fa-pulse"></i> Processing...</h1>
        <p>Please wait. This will take a few minutes</p>
      </div>
      <div class="animationload">
        <div class="osahanloading"></div>
      </div>
    </div>
  </div>

  <br><br><br>
  <p id="mm" ></p>
  <nav class="navbar navbar-expand-lg navbar-light bg-light fixed-top" style="background-color: #e3f2fd;" id="navbar">

    <div class="container">

      <div class="navbar-header">

        <a href="/" class="navbar-brand bounce" title="Home"><i class="far fa-sticky-note"></i>   Note-it™</a>
      </div>

      <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div id="navbarSupportedContent" class="collapse navbar-collapse">

        <ul class="navbar-nav mr-auto">
          <li class="nav-item active"><a href=" url_for('notes.notes')" class="nav-link"><i class="far fa-clone"></i> Shared Notes</a></li>
          <li class="nav-item active"><a href=" url_for('home3')" class="nav-link"><i class="fas fa-users"></i></a></li>
        </ul>

        if session['email']

        <ul class="nav navbar-nav navbar-right justify-content-end ml-auto">
          <li class="nav-item active"><a href=" url_for('notes.user_notes')" class="nav-link"><i class="fas fa-sticky-note"></i></a></li>
        </ul>

        <ul class="nav navbar-nav navbar-right justify-content-end">
          <li class="nav-item active"><a href=" url_for('users.user_page', user_id=session['email'])" class="nav-link"><i class="fas fa-user-circle"></i></a></li>
        </ul>

        <ul class="nav navbar-nav navbar-right justify-content-end ">
          <li class="nav-item active"><a href=" url_for('home4')" class="nav-link"><i class="fab fa-rocketchat"></i></a></li>
        </ul>

        <ul class="nav navbar-nav navbar-right justify-content-end ">
          <li class="nav-item active"><a href=" url_for('users.logout_user')" class="nav-link"><i class="fas fa-sign-out-alt"></i>    Log out</a></li>
        </ul>

        else

        <ul class="nav navbar-nav navbar-right justify-content-end ml-auto">
          <li class="nav-item active"><a href=" url_for('users.register_user')" class="nav-link"><i class="fas fa-user-plus"></i>   Sign up</a></li>
        </ul>

        <ul class="nav navbar-nav navbar-right justify-content-end">
          <li class="nav-item active"><a href=" url_for('users.login_user')" class="nav-link"><i class="fas fa-sign-in-alt"></i> Log in</a></li>
        </ul>

        endif

      </div>

    </div>

  </nav>
  <div class="content container" id="wrapper">
    <div class="content">

      <h1><i class="far fa-clone"></i> Public Notes <small class="text-muted">shared notes</small></h1>

    </div>

    <hr class="my-4">

    <div class="list-group">


      <form class="form-row my-2 my-lg-0" method="POST">
        <div class="col">
          if form
          <input class="form-control mr-sm-2" type="search" placeholder="Search Author name, title and content!" aria-label="Search" id="Search_note" name="Search_note" value=" form" v-model="query">
          else
          <input class="form-control mr-sm-2" type="search" placeholder="Search Author name, title and content!" aria-label="Search" id="Search_note" name="Search_note" value=" form" v-model="query">
          endif

        </div>
        <button class="btn btn-outline-success my-2 my-sm-0" type="submit">Search</button>
      </form>

      <br>

      if notes == [] or notes == None

      <div class="alert alert-primary" role="alert">
        <i class="far fa-frown"></i> There are no shared notes.
      </div>

      endif

      for note in notes

      <a href=" url_for('notes.note', note_id=note._id)" class="list-group-item list-group-item-action flex-column align-items-start">
        <div class="d-flex w-100 justify-content-between">
          <h2 class="mb-1"><i class="fas fa-sticky-note"></i>  note.title</h2>
          <p class="list-group-item-text">Author:  note.author_nickname</p>
        </div>

        <div class="d-flex w-100 justify-content-between">
          <p class="mb-1"></p>
          <p class="list-group-item-text">Created date:  note.created_date.strftime("%Y-%m-%d at %H:%M")</p>
        </div>

      </a>

      endfor

    </div>
  </div>

  <br><br><br><br><br><br><br><br><br><br><br><br><br><br>

  <footer class="container-fluid bg-4 text-center footer">

    <div class="footer-size jumbotron">

      <p></p>

      <p id="demo"></p>

      <h7><span class="glyphicon glyphicon-console"></span> Made by <a href="https://www.jetbrains.com/pycharm/">Pycharm</a>
        and
        <a href="http://flask.pocoo.org/">Flask</a> and <i class="fab fa-python"></i> <a href="https://www.python.org/">Python</a></h7>


    </div>

  </footer>

  </body>
</template>
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>

<!--<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.0.12/css/all.css" integrity="sha384-G0fIWCsCzJIMAVNQPfjH08cyYaUtMwjJwqiRKxxE/rx96Uroj1BtIQ6MLJuheaO9" crossorigin="anonymous">-->
<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.1.0/css/all.css" integrity="sha384-lKuwvrZot6UHsBSfcMvOkWwlCMgc0TaWr+30HWe3a4ltaBwTZhyTEggF5tJv8tbt" crossorigin="anonymous">

<script src="{{ url_for('static', filename='js/bootstrap-notify.min.js') }}"></script>
<!--<script src="{{ url_for('static', filename='js/UPMJS.js') }}"></script>-->

<!--<meta name="viewport" content="width=device-width, initial-scale=1.0">-->
<meta name="viewport" content="initial-scale=2">

<!--<script src="http://vjs.zencdn.net/5.10.4/video.min.js"></script>-->

<!--&lt;!&ndash; If you'd like to support IE8 (for Video.js versions prior to v7) &ndash;&gt;-->
<!--<script src="http://vjs.zencdn.net/5.10.4/video.js"></script>-->

<link href="https://vjs.zencdn.net/7.0.0/video-js.css" rel="stylesheet">
<script src="https://vjs.zencdn.net/7.0.0/video.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/vue"></script>
<style type="text/css">
  .vjs-default-skin .vjs-play-progress,
  .vjs-default-skin .vjs-volume-level { background-color: #3b6073 }
</style>

<script>
  import axios from 'axios';

  export default {
    name: 'Ping',
    data() {
      return {
        'mm': '',
      };
    },
    methods: {
      getMessage() {
        const path = 'http://localhost:4990/ping';
        axios.get(path)
          .then((res) => {
            this.mm = res.data;
          })
          .catch((error) => {
            // eslint-disable-next-line
            console.error(error);
          });
      },
    },
    created() {
      this.getMessage();
    },
  };
  function myFunction() {
          $('#BODY_BASE').hide();
          var x = document.getElementById("myDIV1");
          if (x.style.display === "none") {
              x.style.display = "block";
          } else {
              x.style.display = "none";
      }
  }
  $(document).ready(function() {
     $('#myDIV1').hide();
  });

    var myVar = setInterval(myTimer, 1000);

  function myTimer() {
      var d = new Date();
      document.getElementById("demo").innerHTML = d.toLocaleTimeString();
  }
</script>

