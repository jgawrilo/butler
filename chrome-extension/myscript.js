console.log("Loaded myscript.js...");
console.log(window.location.href);

var waitForVideo = setInterval (checkForElement, 1000);

function checkForElement () {
    if (window.location.href.startsWith("https://www.instagram.com")) {

    console.log("Instagram!!");
    var insta_button = document.getElementById("jjdog");
    if (insta_button == null) {
        var header = document.getElementsByClassName("_jxp6f")[0];
        console.log(header);
        var button = document.createElement("button");
        button.setAttribute("id","jjdog");
        button.setAttribute("class","_ah57t _84y62 _rmr7s");
        button.style.background = "#f038e6";
        button.textContent = "Butler";
        button.onclick = function(x){
            var handle = window.location.href.split("https://www.instagram.com/")[1].replace("/","");
            console.log(handle);
            $.get("https://localhost:5000/instagram?handle="+handle,function(resp){
                console.log(resp);
            });
        };
        header.appendChild(button);
    }

    }
}

var count = 0;
var socket;
function getParameterByName(name, url) {
    if (!url) {
      url = window.location.href;
    }
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

function placeEntitySearch() {
    var header = document.getElementById("hdtb-msb");
    var subDiv = header.getElementsByTagName("div")[0];

    var entityTab = document.createElement("div");
    entityTab.setAttribute("class","hdtb-mitem hdtb-imb")
    var entityLink = document.createElement("a");
    entityLink.setAttribute("class","q qs");
    entityLink.setAttribute("href","http://espn.com");
    entityLink.innerHTML = "Entities";
    entityTab.appendChild(entityLink);
    subDiv.insertBefore(entityTab,subDiv.firstChild);
}

function displayDarkResults(data){
    console.log(data);
    document.getElementById("resultStats").innerHTML = document.getElementById("resultStats").innerHTML + ", " + data.size + " Dark Web results";
    for(var i=0; i < data.results.length; i++){
        placeFakeResult(data.results[i]);
    }
}

function changeSearchResults(){
    var tests = document.getElementsByClassName("st");
        for(var i=0; i < tests.length; i++){
            var btn = document.createElement("div")
            //btn.setAttribute("style","height:200px");
            var t = document.createTextNode("CLICK ME");
            btn.appendChild(t);
            var a = tests[i].appendChild(btn);
        }
}

function connectToSocket(test){
    socket = io.connect('http://localhost:3000');
        socket.on("connect",function(){
            console.log("connected to socket...");
            socket.emit("google_link",{"data":test});
        });
        socket.on("dark_search",function(data){
            console.log(data);
            if(count == 0) {
                displayDarkResults(data);
            }
            count++;
        });
}

function placeFakeResult(result){
    console.log(result);
    var resultBucket = document.getElementById("rso");
    var nid = resultBucket.getElementsByClassName("_NId")[0];
    var srg = nid.getElementsByClassName("srg")[0];

    var g_fakeResult = document.createElement("div");
    g_fakeResult.setAttribute("class","g");

    var rc_fakeResult = document.createElement("div");
    rc_fakeResult.setAttribute("class","rc");
    g_fakeResult.appendChild(rc_fakeResult);
    
    var h3_fakeResult = document.createElement("h3");
    h3_fakeResult.setAttribute("class","r");
    rc_fakeResult.appendChild(h3_fakeResult);

    var a_fakeResult = document.createElement("a");
    a_fakeResult.setAttribute("href",result.url);
    a_fakeResult.setAttribute("style","color:black")

    var title = result.title;
    if (title == ""){
        title = result.domain;
    }
    a_fakeResult.innerHTML = title;
    h3_fakeResult.appendChild(a_fakeResult);

    var s_fakeresult = document.createElement("div");
    s_fakeresult.setAttribute("class","s");

    rc_fakeResult.appendChild(s_fakeresult);

    var div_fakeresult = document.createElement("div");
    s_fakeresult.appendChild(div_fakeresult);
    
    var div_f_kv = document.createElement("div");
    div_f_kv.setAttribute("class", "f kb _SWb");
    div_fakeresult.appendChild(div_f_kv);

    var cite_fr = document.createElement("cite");
    cite_fr.setAttribute("class","_Rm bc");
    cite_fr.innerHTML = result.url;
    div_f_kv.appendChild(cite_fr);

    var span_guy = document.createElement("span");
    span_guy.setAttribute("class","st")
    span_guy.innerHTML = result.text;
    div_fakeresult.appendChild(span_guy);

    //<span class="st">

    srg.insertBefore(g_fakeResult,srg.firstChild);

    // <div class="g"><!--m--><div class="rc" data-hveid="34" data-ved="0ahUKEwjZv5uT4oDRAhXL5YMKHVe4DQwQFQgiKAEwAQ"><h3 class="r"><a href="http://www.dipf.de/en/about-us/staff/gawrilow-caterina" onmousedown="return rwt(this,'','','','2','AFQjCNFQODUlhlSARvkQDXjNkxYd4y80Og','seK0YLsMHMShehXCNuFZQA','0ahUKEwjZv5uT4oDRAhXL5YMKHVe4DQwQFggjMAE','','',event)">Gawrilow — German Institute for International Educational Research</a></h3><div class="s"><div><div class="f kv _SWb" style="white-space:nowrap"><cite class="_Rm bc">www.dipf.de › Home › About us › Staff</cite><div class="action-menu ab_ctl"><a class="_Fmb ab_button" href="#" id="am-b1" aria-label="Result details" aria-expanded="false" aria-haspopup="true" role="button" jsaction="m.tdd;keydown:m.hbke;keypress:m.mskpe" data-ved="0ahUKEwjZv5uT4oDRAhXL5YMKHVe4DQwQ7B0IJTAB"><span class="mn-dwn-arw"></span></a><div class="action-menu-panel ab_dropdown" role="menu" tabindex="-1" jsaction="keydown:m.hdke;mouseover:m.hdhne;mouseout:m.hdhue" data-ved="0ahUKEwjZv5uT4oDRAhXL5YMKHVe4DQwQqR8IJjAB"><ol><li class="action-menu-item ab_dropdownitem" role="menuitem"><a class="fl" href="http://webcache.googleusercontent.com/search?q=cache:-Mx5wMIRZl8J:www.dipf.de/en/about-us/staff/gawrilow-caterina+&amp;cd=2&amp;hl=en&amp;ct=clnk&amp;gl=us" onmousedown="return rwt(this,'','','','2','AFQjCNE13CIXuXY3tyDf64P9XFady6-LnA','zLnxRB8Omf5Rvn4XKlcwWA','0ahUKEwjZv5uT4oDRAhXL5YMKHVe4DQwQIAgnMAE','','',event)">Cached</a></li></ol></div></div></div><span class="st">Persönliche Seite Caterina <em>Gawrilow</em>. ... Prof. Dr. Caterina <em>Gawrilow</em>. Function: Associated researcher. <em>Gawrilow</em>@dipf.de&nbsp;...<div>CLICK ME</div></span></div></div></div><!--n--></div>
}

if (document.title.indexOf("YouTube") != -1 ) {
    console.log("YouTube!!!");

    var header = document.getElementById("watch-headline-title");
    
    var entityTab = document.createElement("div");
    entityTab.setAttribute("class","hdtb-mitem hdtb-imb")
    var entityLink = document.createElement("a");
    entityLink.setAttribute("class","q qs");

    var video = window.location.href.split("v=")[1]
    entityLink.setAttribute("href","http://127.0.0.1:8000/polls?video=" + video);
    entityLink.setAttribute("target","_blank")
    entityLink.innerHTML = "Entities";
    entityTab.appendChild(entityLink);
    header.insertBefore(entityTab,header.firstChild);
}

//ProfileHeaderCard-name

else if (window.location.href.startsWith("https://twitter.com/")) {

    setTimeout(function(){
        console.log("Twitter!!");
    var header = document.getElementsByClassName("ProfileHeaderCard")[0];
    console.log(header);
    var button = document.createElement("button");

    button.setAttribute("class","user-actions-follow-button btn");
    button.setAttribute("type","button");
    button.style.background = "#f038e6";
    button.textContent = "Butler";
    button.onclick = function(x){
        var handle = window.location.href.split("https://twitter.com/")[1].replace("/","");
        console.log(handle);
        $.get("https://localhost:5000/instagram?handle="+handle);
    };
    //header.appendChild(button);
    header.insertBefore(button, header.childNodes[0]);

},
1000);
}


else if (window.location.href.startsWith("https://www.google.com/search") ||
    window.location.href.startsWith("https://www.google.com/webhp") ) {

    console.log(getParameterByName("q",window.location.href));
    //Creating Elements
    setTimeout(function(){

        //placeEntitySearch();

        //var div = document.createElement("div")
        //div.setAttribute("style","height:200px;border-width:5px");
        //document.getElementById("topstuff").appendChild(div);

        var resultLinks = document.getElementsByClassName("r");
        var test = "justin";
        for(var i=0; i < resultLinks.length; i++){
            var a = resultLinks[i].getElementsByTagName("a");
            console.log(a[0].textContent);
            console.log(a[0].href);
            //$.post("http://localhost:8080",{"url":a[0].href},function(x){});
            //socket.emit("google_link",{"link":a[0].href});
        }
        connectToSocket(test);

        // changeSearchResults();

        
        
    },3000);
    
}



