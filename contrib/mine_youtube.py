#! /usr/bin/python

import youtube
import ultrajson as json
import argparse
import sys
import codecs

if __name__ == "__main__":

    handle = sys.argv[1]
    save_loc = sys.argv[2]
    print handle

    key = "AIzaSyBue6ZPN4l4qPXmBtONTIb1WeD-DyWp1_A"

    # Create client with dev key
    client = youtube.YTClient(key)
    # For each video
    for video_id in [handle]:

        with codecs.open(save_loc + handle + "_youtube.json","w") as out:
            # Grab video info based on id
            video_info = client.get_video_info(vid_id)
            print "VIDEO ID --> ", vid_id, ""
            out.write(json.dumps(video_info) + "\n")

            # Grab top level comments, replies, and commenting user id's for a video.
            # Some 'some_replies' will be duplicates of the replies in top_level_comments.
            top_level_comments, some_replies, commenting_user_ids = client.get_video_data(vid_id)

            print "COMMENTS --> ", json.dumps(top_level_comments), "\n\n"
            out.write(json.dumps(top_level_comments) + "\n")

            print "SOME REPLIES --> ", json.dumps(some_replies), "\n\n"
            out.write(json.dumps(some_replies) + "\n")

            print "USER/CHANNEL IDS --> ", commenting_user_ids, "\n\n"

            # Get activities for all users.  Note that this might take a while.
            for uid in commenting_user_ids:
                if uid:
                    print "USER ID --> ", uid, "\n\n"
                    user_activities = client.get_all_activities_for_channel(uid)
                    out.write(json.dumps(user_activities) + "\n")