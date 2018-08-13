#!/usr/bin/env python3

import csv
import json
import argparse

from slackclient import SlackClient


def get_args():
    parser = argparse.ArgumentParser(description='Command line options for this script')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-l', '--list', action='store_true', help='Create a CSV list of all Slack channels')
    group.add_argument('-r', '--rename', action='store_true', help='Rename Slack channels based on a CSV')
    parser.add_argument('-t', '--token', help='Stores the Slack API token needed to run this script')
    parser.add_argument('-f', '--file', default="Channel List.csv", help='Specify the name of the file to be used')

    return parser.parse_args()

def create_csv(filename):
    # Write the title row of the CSV
    data_to_file = open(filename, 'w', newline='')
    csv_writer = csv.writer(data_to_file, delimiter=',')
    return csv_writer


def append_csv():
    # Append data to the rows of the CSV
    data_to_file = open(get_csv(), 'a', newline='')
    csv_append = csv.writer(data_to_file, delimiter=',')
    return csv_append


def get_user(slackClient, creator_id):
    # Making a second call to the API to determine the name and email of the channel creator

    user_info_raw = slackClient.api_call('users.info', user=creator_id)
    user_data = user_info_raw['user']['profile']

    return user_data


def list_channels(slackClient):

    channel_list_raw = slackClient.api_call('channels.list', exclude_archived=True)
    slack_channel_data = channel_list_raw['channels']
    length_data = len(slack_channel_data)

    create_csv().writerow(['Channel ID', 'Channel Name', 'New Channel Name', 'Creator', 'Email','Members', 'Purpose', 'Topic'])

    for i in range(0, length_data):
        # Here's where we get the fields we want to push into the CSV
        channel_id = slack_channel_data[i]['id']
        channel_name = slack_channel_data[i]['name']
        members = slack_channel_data[i]['num_members']
        purpose = slack_channel_data[i]['purpose']['value']
        topic = slack_channel_data[i]['topic']['value']
        creator_id = slack_channel_data[i]['creator']

        user_data = get_user(slackClient, creator_id)
        creator_name = user_data['real_name']
        creator_email = user_data['email']

        print(f'Writing channel with ID {channel_id} and named {channel_name} to {get_csv()}')
        append_csv().writerow([channel_id, channel_name, '', creator_name, creator_email, members, purpose, topic])


def rename_channels(slackClient, channelcsv):

    # For information on the channels.rename method, see this Slack API doc https://api.slack.com/methods/channels.rename
    with open(channelcsv, newline='') as csvfile:

        reader = csv.DictReader(csvfile)
        for row in reader:
            print(f"Renaming channel with ID {row['Channel ID']} from {row['Channel Name']} to {row['New Channel Name']}")
            slackClient.api_call(
                'channels.rename',
                channel=row['Channel ID'],
                name=row['New Channel Name'],
                validate=True
            )


def main():
    args = get_args()

    if args.token == None:
        print("Please pass the Slack API token to this app with the '-t' flag")
    else:
        slackClient = SlackClient(args.token)
        
        if args.list:
            print('Downloading Slack channel list into', get_csv())
            list_channels(slackClient)
        elif args.rename:
            print('Renaming Slack channels according to', get_csv())
            rename_channels(slackClient, args.)


main()
