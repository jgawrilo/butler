var prefs = {};


/*
content-security-policy:script-src https://localhost:5000/twitter https://connect.facebook.net https://cm.g.doubleclick.net https://ssl.google-analytics.com https://graph.facebook.com https://twitter.com 'unsafe-eval' https://localhost:5000/twitter https://*.twimg.com https://api.twitter.com https://analytics.twitter.com https://publish.twitter.com https://ton.twitter.com https://syndication.twitter.com 'nonce-AfJMtMky8CLOfw3f4eMgNg==' https://www.google.com https://t.tellapart.com https://platform.twitter.com https://www.google-analytics.com 'self'; frame-ancestors 'self'; font-src https://twitter.com https://*.twimg.com data: https://ton.twitter.com https://fonts.gstatic.com https://maxcdn.bootstrapcdn.com https://netdna.bootstrapcdn.com 'self'; media-src https://twitter.com https://*.twimg.com https://ton.twitter.com blob: 'self'; connect-src https://localhost:5000/twitter https://graph.facebook.com https://*.giphy.com https://*.twimg.com https://api.twitter.com https://pay.twitter.com https://analytics.twitter.com https://*.twprobe.net https://media.riffsy.com https://embed.periscope.tv https://upload.twitter.com 'self'; style-src https://fonts.googleapis.com https://twitter.com https://*.twimg.com https://translate.googleapis.com https://ton.twitter.com 'unsafe-inline' https://platform.twitter.com https://maxcdn.bootstrapcdn.com https://netdna.bootstrapcdn.com 'self'; object-src https://twitter.com https://pbs.twimg.com; default-src 'self'; frame-src https://staticxx.facebook.com https://twitter.com https://*.twimg.com https://5415703.fls.doubleclick.net https://player.vimeo.com https://pay.twitter.com https://www.facebook.com https://ton.twitter.com https://syndication.twitter.com https://vine.co twitter: https://www.youtube.com https://platform.twitter.com https://upload.twitter.com https://s-static.ak.facebook.com https://4337974.fls.doubleclick.net 'self' https://donate.twitter.com; img-src https://graph.facebook.com https://*.giphy.com https://twitter.com https://*.twimg.com https://ad.doubleclick.net data: https://lumiere-a.akamaihd.net https://fbcdn-profile-a.akamaihd.net https://www.facebook.com https://ton.twitter.com https://*.fbcdn.net https://syndication.twitter.com https://media.riffsy.com https://www.google.com https://stats.g.doubleclick.net https://api.mapbox.com https://www.google-analytics.com blob: 'self'; report-uri https://twitter.com/i/csp_report?a=NVQWGYLXFVZXO2LGOQ%3D%3D%3D%3D%3D%3D&ro=false;
*/
chrome.webRequest.onHeadersReceived.addListener(function(details){
  for(var i = 0; i < details.responseHeaders.length; ++i)
        if(details.responseHeaders[i].name.toLowerCase() == 'content-security-policy'){
            details.responseHeaders[i].value = "script-src https://localhost:5000/twitter https://connect.facebook.net https://cm.g.doubleclick.net https://ssl.google-analytics.com https://graph.facebook.com https://twitter.com 'unsafe-eval' https://localhost:5000/twitter https://*.twimg.com https://api.twitter.com https://analytics.twitter.com https://publish.twitter.com https://ton.twitter.com https://syndication.twitter.com 'nonce-AfJMtMky8CLOfw3f4eMgNg==' https://www.google.com https://t.tellapart.com https://platform.twitter.com https://www.google-analytics.com 'self'; frame-ancestors 'self'; font-src https://twitter.com https://*.twimg.com data: https://ton.twitter.com https://fonts.gstatic.com https://maxcdn.bootstrapcdn.com https://netdna.bootstrapcdn.com 'self'; media-src https://twitter.com https://*.twimg.com https://ton.twitter.com blob: 'self'; connect-src https://localhost:5000/twitter https://graph.facebook.com https://*.giphy.com https://*.twimg.com https://api.twitter.com https://pay.twitter.com https://analytics.twitter.com https://*.twprobe.net https://media.riffsy.com https://embed.periscope.tv https://upload.twitter.com 'self'; style-src https://fonts.googleapis.com https://twitter.com https://*.twimg.com https://translate.googleapis.com https://ton.twitter.com 'unsafe-inline' https://platform.twitter.com https://maxcdn.bootstrapcdn.com https://netdna.bootstrapcdn.com 'self'; object-src https://twitter.com https://pbs.twimg.com; default-src 'self'; frame-src https://staticxx.facebook.com https://twitter.com https://*.twimg.com https://5415703.fls.doubleclick.net https://player.vimeo.com https://pay.twitter.com https://www.facebook.com https://ton.twitter.com https://syndication.twitter.com https://vine.co twitter: https://www.youtube.com https://platform.twitter.com https://upload.twitter.com https://s-static.ak.facebook.com https://4337974.fls.doubleclick.net 'self' https://donate.twitter.com; img-src https://graph.facebook.com https://*.giphy.com https://twitter.com https://*.twimg.com https://ad.doubleclick.net data: https://lumiere-a.akamaihd.net https://fbcdn-profile-a.akamaihd.net https://www.facebook.com https://ton.twitter.com https://*.fbcdn.net https://syndication.twitter.com https://media.riffsy.com https://www.google.com https://stats.g.doubleclick.net https://api.mapbox.com https://www.google-analytics.com blob: 'self'; report-uri https://twitter.com/i/csp_report?a=NVQWGYLXFVZXO2LGOQ%3D%3D%3D%3D%3D%3D&ro=false;";
        }
    return {responseHeaders:details.responseHeaders};
},
{urls: ["*://twitter.com/*"]},["responseHeaders","blocking"]);

chrome.storage.local.get({callback: 'https://localhost:5000/browser_action/', key: 'chrome'}, function(o) { prefs = o; });

chrome.storage.onChanged.addListener(function(changes) {
    for (key in changes) {
        prefs[key] = changes[key].newValue;
    }
});

function log(url, title, favicon){
    var data = {
        url: url, time: Date.now(),
        title: title, key: prefs.key
    };
    $.post( prefs.callback, data );
}

chrome.tabs.onActivated.addListener(function (activeInfo) {
    chrome.tabs.get(activeInfo.tabId, function(tab) {
        if (tab.status === "complete" && tab.active) {
            chrome.windows.get(tab.windowId, {populate: false}, function(window) {
                if (window.focused) {
                    log(tab.url, tab.title, tab.favIconUrl || null);
                }
            });
        }
    });
});

chrome.tabs.onUpdated.addListener(function (tabId, changeInfo, tab) {
    if (changeInfo.status === "complete" && tab.active) {
        chrome.windows.get(tab.windowId, {populate: false}, function(window) {
            if (window.focused) {
                log(tab.url, tab.title, tab.favIconUrl || null);
            }
        });
    }
});

chrome.windows.onFocusChanged.addListener(function (windowId) {
    if (windowId == chrome.windows.WINDOW_ID_NONE) {
        log(null, null, null);
    } else {
        chrome.windows.get(windowId, {populate: true}, function(window) {
            if (window.focused) {
                chrome.tabs.query({active: true, windowId: windowId}, function (tabs) {
                    if (tabs[0].status === "complete") {
                        log(tabs[0].url, tabs[0].title, tabs[0].favIconUrl || null);
                    }
                });
            }
        });
    }
});
