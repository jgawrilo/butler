var socket;


var server = "https://localhost:5000/"

// NAME CALL
d3.select("#save_name").on("click",function(){
    var endpoint = server + "name/"
    var name = d3.select("#name").node().value;
    console.log(name);
    $.get(endpoint, {"name":name}, function(response) {
        var response = JSON.parse(response);
        console.log(response);
        console.log("Probably lock the name in so it's uneditable?...")
    });
});

// EXPORT CALL
d3.select("#export").on("click",function(){
    var endpoint = server + "save_export/"
    $.get(endpoint, function(response) {
        var response = JSON.parse(response);
        console.log(response);
        console.log("Tell the user where data has been saved...")
    });
});

// CLEAR CALL
d3.select("#clear").on("click",function(){
    var endpoint = server + "clear/"
    $.get(endpoint, function(response) {
        var response = JSON.parse(response);
        console.log(response);
        console.log("Remove everythng from the UI...Prompt them for a new name?")
    });
});

// RELOAD
d3.select("#reload").on("click",function(){
    var endpoint = server + "reload/"
    var name = d3.select("#name").node().value;
    $.get(endpoint, {"name":name}, function(response) {
        var response = JSON.parse(response);
        console.log(response);
        console.log("Either show what files already exist or prompt for the file...")
    });
});

// UNLIKE...in this case it's always a zero we send back
function unlike(id){
    var endpoint = server + "unlike/"
    $.get(endpoint, {"id":id,"response":0}, function(response) {
        var response = JSON.parse(response);
        console.log(response);
        console.log("Either show what files already exist or prompt for the file...")
    });
}

// ANSWER PROMPT...in this case it's always a zero we send back
function answerPrompt(id,answer){
    var endpoint = server + "answer/"
    $.get(endpoint, {"id":id,"response":answer}, function(response) {
        var response = JSON.parse(response);
        console.log(response);
        console.log("Remove the prompt from the UI...")
    });
}

var chart = Highcharts.chart('container', {
    chart: {
        type: 'scatter',
        zoomType: 'xy'
    },
    title: {
        text: ''
    },
    xAxis: {
        title: {
            enabled: true,
            text: ''
        },
        startOnTick: true,
        endOnTick: true,
        showLastLabel: true
    },
    yAxis: {
        title: {
            text: ''
        }
    },
    legend: {
        layout: 'vertical',
        align: 'left',
        verticalAlign: 'top',
        x: 100,
        y: 70,
        floating: true,
        backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF',
        borderWidth: 1
    },
    plotOptions: {
        scatter: {
            marker: {
                radius: 5,
                states: {
                    hover: {
                        enabled: true,
                        lineColor: 'rgb(100,100,100)'
                    }
                }
            },
            states: {
                hover: {
                    marker: {
                        enabled: false
                    }
                }
            },
            tooltip: {
                headerFormat: '<b>{point.key}</b><br>',
                pointFormat: ''
            },
            events: {
                    click: function(event) {
                        alert('x: ' + event.chartX + ', y: ' + event.chartY);
                }
            }
        }
    },
    series: [{}]
});

function receiveGoogleSearch(data){
    d3.select("#google_results").append("div").text(data.query).append("input").attr("type","checkbox").attr("id","i"+data.id)
    .property('checked', true).on("change",function(){
        unlike(this.id);
    });
}

function receivePrompt(data){
    if(data.image_url){
        d3.select("#prompts").append("div").attr("id","d"+data.id).text(data.question).append("img").attr("src",data.image_url);
    }
    else{
        d3.select("#prompts").append("div").attr("id","d"+data.id).append("a").attr("href",data.page_url)
        .attr("target","_blank").text(data.question);
    }
    d3.select("#d" + data.id).append("button").attr("id",data.id).attr("type","button").classed("btn btn-success",true).text("Yes")
    .on("click",function(){
        answerPrompt(this.id,1);
        d3.select("#d"+data.id).remove();
    });
    d3.select("#d" + data.id).append("button").attr("id",data.id).attr("type","button").classed("btn btn-danger",true).text("No")
    .on("click",function(){
        answerPrompt(this.id,0);
        d3.select("#d"+data.id).remove();
    });
}


function receiveUpdatedRelatedTerms(data) {
    var text = d3.select("#terms").selectAll("div")
    .data(data.terms);

    text.attr("class", "term");
    text.enter().append("div").attr("class","term").merge(text).text(function(d){return d.term});
    text.exit().remove();
}

      socket = io();


      /*
        msg...

        {
          "data": [
            {
              "view_count": 0,
              "viewed": false,
              "classification": "stalker",
              "url": "http://radaris.com/p/Justin/Gawrilow/",
              "x": -25.022685308108056,
              "view_time_seconds": null,
              "relevance_score": 0.5,
              "id": "page0",
              "screen_shot_url": "screenshots/page0.png",
              "y": -4.1526364226371735
            },
            {
              "view_count": 0,
              "viewed": false,
              "classification": "social",
              "url": "https://registry.theknot.com/hilary-swab-justin-gawrilow-may-2013-dc/433269",
              "x": 8.1685664154107211,
              "view_time_seconds": null,
              "relevance_score": 0.5,
              "id": "page1",
              "screen_shot_url": "screenshots/page1.png",
              "y": 16.396648225978826
            },
            {
              "view_count": 0,
              "viewed": false,
              "classification": "stalker",
              "url": "http://www.whitepages.com/name/Justin-Gawrilow",
              "x": 3.5129311595610337,
              "view_time_seconds": null,
              "relevance_score": 0.5,
              "id": "page2",
              "screen_shot_url": "screenshots/page2.png",
              "y": 7.5799368681373824
            },
            {
              "view_count": 0,
              "viewed": false,
              "classification": "articles",
              "url": "https://www.intelius.com/people/Justin-Gawrilow/Washington-DC/0ca4fh5qkz1",
              "x": 13.341187733136218,
              "view_time_seconds": null,
              "relevance_score": 0.5,
              "id": "page3",
              "screen_shot_url": "screenshots/page3.png",
              "y": -19.823948671478973
            }
          ]
        }
      */
      socket.on('page_update', function(msg){
        console.log("Received Page Update (from google search)...remember each of these need like/unlike checkboxes too!")
        msg = JSON.parse(msg);
        console.log(msg);
        var data = [];
        for (var i=0; i < msg.data.length; i++){
            data[i] = {"name":msg.data[i].url,"x":msg.data[i].x,"y":msg.data[i].y};
        }
        chart.series[0].update({name: 'Pages',
                color: 'rgba(234, 43, 34, .75)',
                data: data
            }, true); //true / false to redraw
      });

      /*
        msg...

        {
          "terms": [
            {
              "count": 19,
              "term": "Google",
              "id":"t12",
              "classification":"name",
              "relevance_score":0.0
            },
            {
              "count": 18,
              "term": "first",
              "id":"t13",
              "classification":"number",
              "relevance_score":0.5
            },
            {
              "count": 15,
              "term": "5",
              "id":"t14",
              "classification":"number",
              "relevance_score":0.2
            },
            {
              "count": 11,
              "term": "Virginia Dental Care",
              "id":"t15",
              "classification":"business",
              "relevance_score":0.2
            },
            {
              "count": 8,
              "term": "Chuzhin",
              "id":"t16",
              "classification":"number",
              "relevance_score":0.8
            },
            ...
            ...
          ]
        }
      */
      socket.on('terms', function(msg){
        console.log("Received Updated Related Terms...remember each of these need like/unlike checkboxes too!")
        msg = JSON.parse(msg);
        console.log(msg);
        receiveUpdatedRelatedTerms(msg);
      });

      /*
        msg...

        {
            "url":"https://registry.theknot.com/hilary-swab-justin-gawrilow-may-2013-dc/433269",
            "screen_shot_url":"screenshots/p44.png",
            "view_time_seconds":15,
            "view_count":1,
            "classification":"news",
            "viewed":false,
            "id":"page44",
            "x":14.534,
            "y":19.345,
            "relevance_score":0.0
        }
      */
      socket.on('new_page', function(msg){
        console.log("Received New Page of Note Hit...remember each of these need like/unlike checkboxes too!");
        msg = JSON.parse(msg);
        console.log(msg);
        d3.select("#visited_pages").insert("div",":first-child").attr("id",msg.id).text(msg.url + " " + msg.view_count)
        .append("img").attr("src",msg.screen_shot_url).style("width","200px").style("height","100px");
      });

      /*
        msg...

        {
            "question":"Is this picture of interest?",
            "id":"q20",
            "image_url":"https://lh3.googleusercontent.com/-8kuDJO1frwY/AAAAAAAAAAI/AAAAAAAAATk/G8U8sX7PvcU/s120-p-rw-no/photo.jpg",
            "page_url":None
        }
      */
      socket.on('prompt', function(msg){
        console.log("Received Prompt");
        msg = JSON.parse(msg);
        console.log(msg);
        receivePrompt(msg);
      });

      /*
        msg...
        {
            "url":https://www.google.com/search?q=justin+gawrilow&espv=2",
            "query":"justin+gawrilow",
            "id":"g7"
        }
      */
      socket.on('google_search', function(msg){
        console.log("Received Google Search Page Hit...remember each of these need like/unlike checkboxes too!");
        msg = JSON.parse(msg);
        console.log(msg);
        receiveGoogleSearch(msg);
      });

      /*
        msg...

        {
            "id":"sm19"
            "site":"Instagram",
            "url":"https://www.instagram.com/juddydotg/",
            "account":"juddydotg",
            "image_url":"https://instagram.fphl1-1.fna.fbcdn.net/t51.2885-19/11371180_804405839674055_1031223292_a.jpg",
            "name":"Justin Gawrilow",
            "profile_snippet":"Fitter, happier, more productive",
            "relevance_score":0.0
        }
      */
      socket.on('social_media', function(msg){
        console.log("Received Social Media Page Hit...remember each of these need like/unlike checkboxes too!");
        msg = JSON.parse(msg);
        console.log(msg);
        d3.select("#social_media").append("a").attr("href",msg.url)
        .attr("target","_blank").text(msg.site + "(" + msg.account + ")")
        .append("img").attr("src",msg.image_url);
      });

