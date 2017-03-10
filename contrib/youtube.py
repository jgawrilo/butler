#!/usr/bin/env python

from apiclient.discovery import build
from apiclient.errors import HttpError

class YTClient(object):

    def __init__(self, developer_key):
        YOUTUBE_API_SERVICE_NAME = "youtube"
        YOUTUBE_API_VERSION = "v3"
        self.youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, 
            developerKey=developer_key)

    def get_playlist_info(self, pid):
        response = self.youtube.playlists().list(
        part="id,snippet,contentDetails,status,player,localizations",
        id=pid,
        maxResults=20
        ).execute()
        return response

    def get_videos_from_playlist(self, pid):
        response = self.youtube.playlistItems().list(
        part="id,snippet,contentDetails,status",
        playlistId=pid,
        maxResults=20
        ).execute()
        return response

    def get_video_info(self, vid):
        response = self.youtube.videos().list(
        part="id,snippet,contentDetails,statistics",
        id=vid,
        maxResults=20
        ).execute()
        return response

    def get_commentThreads_for_video(self, vid, pageToken):
        if pageToken:
            return self.youtube.commentThreads().list(
            part="id,snippet,replies",
            videoId=vid,
            maxResults=20,
            pageToken=pageToken,
            ).execute()
        else:
            return self.youtube.commentThreads().list(
            part="id,snippet,replies",
            videoId=vid,
            maxResults=20,
            ).execute()

    def get_all_commentThreads_for_video(self, vid):
        try:
            data = []
            go = True
            pageToken = None
            while go:
                response = self.get_commentThreads_for_video(vid,pageToken)
                data.append(response)
                if not "nextPageToken" in response:   
                    go = False
                else:
                    pageToken=response["nextPageToken"]
            return data

        # This happened - not sure why, but move on.
        except HttpError, e:
          print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
          return data

    def get_video_data(self,vid):
        user_ids = set()
        some_replies = []
        top_level_comments = self.get_all_commentThreads_for_video(vid)
        comment_ids_needed = self.check_comments(top_level_comments)
        for comment in comment_ids_needed:
            some_replies = self.get_all_comment(comment)
        for response in top_level_comments:
            for comment in response.get("items",[]):
                user_ids.add(comment["snippet"]["topLevelComment"]["snippet"].get("authorChannelId",{"value":None})["value"])
                if "replies" in comment:
                    for reply in comment.get("comments",[]):
                        user_ids.add(reply["snippet"].get("authorChannelId",{"value":None})["value"])

        return top_level_comments, some_replies, user_ids

    def check_comments(self, comments):
        comment_ids_needed = []
        for comment_call in comments:
            for comment in comment_call.get("items", []):  
                total_snagged = 0
                total_replies = comment["snippet"]["totalReplyCount"]
                if "replies" in comment:
                    total_snagged = len(comment["replies"]["comments"])
                if total_snagged != total_replies:
                    comment_ids_needed.append(comment["id"])
        return comment_ids_needed

    def get_channels_from_comments(self, comments):
        channels = set()
        for comment_call in comments:
            for comment in comment_call.get("items", []):  
                if "authorChannelId" in comment["snippet"]["topLevelComment"]["snippet"]:
                    channels.add(comment["snippet"]["topLevelComment"]["snippet"]["authorChannelId"]["value"])
                if "replies" in comment:
                    for reply in comment["replies"]["comments"]:
                        if "authorChannelId" in reply["snippet"]:
                            channels.add(reply["snippet"]["authorChannelId"]["value"])

        return channels

    def get_comment(self, cid, pageToken):
        if pageToken:
            return self.youtube.comments().list(
            part="id,snippet",
            parentId=cid,
            maxResults=20,
            pageToken=pageToken
            ).execute()
        else:
            return self.youtube.comments().list(
            part="id,snippet",
            parentId=cid,
            maxResults=20
            ).execute()

    def get_all_comment(self, cid):
        data = []
        go = True
        pageToken = None
        while go:
            response = self.get_comment(cid,pageToken)
            data.append(response)
            if not "nextPageToken" in response:
                go = False
            else:
                pageToken=response["nextPageToken"]
        return data

    def get_activities_for_channel(self,cid,pageToken):
        if pageToken:
            return self.youtube.activities().list(
            part="id,snippet,contentDetails",
            channelId=cid,
            maxResults=20,
            pageToken=pageToken
            ).execute()
        else:
            return self.youtube.activities().list(
            part="id,snippet,contentDetails",
            channelId=cid,
            maxResults=20
            ).execute()

    def get_all_activities_for_channel(self,cid):
        data = []
        go = True
        pageToken = None
        while go:
            response = self.get_activities_for_channel(cid,pageToken)
            data.append(response)
            if not "nextPageToken" in response:
                go = False
            else:
                pageToken = response["nextPageToken"]
        return data