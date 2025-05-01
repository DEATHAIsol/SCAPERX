import os
import subprocess
import re
import time
import json

# ✅ List of X usernames to scan
usernames = [
    "BarackObama",
    "realDonaldTrump",
    "elonmusk",
    "USNavy",
    "CENTCOM",
    "BlackRock",
    "GoldmanSachs",
    "business",
    "BBCWorld",
    "DeptofDefense",
    "UN",
    "BillGates",
    "SpaceX",
    "Google",
    "FBI",
    "CIA",
    "NSAGov",
    "DeptofDefense",
    "dfat",
    "StateDept",
    "IMFNews",
    "WHO",
    "NATO",
    "SecretService",
    "Forbes",
    "NYtimes",
    "DOJCrimDiv",
    "USAttorneys",
    "CivilRights",
    "TheJusticeDept"
]

# Max tweets per user to scan
MAX_TWEETS = 1000

# Output files
output_file = "mentions_report.txt"
inactive_file = "inactive_mentions.txt"
active_file = "active_mentions.txt"

# Scrape tweets and extract @mentions + tweet URLs
def get_user_mentions_with_urls(username):
    print(f"\n🔍 Scraping tweets by @{username}...")
    command = f"snscrape --max-results {MAX_TWEETS} --jsonl twitter-user {username}"
    try:
        tweets_json = subprocess.check_output(command, shell=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to scrape @{username}: {e}")
        return {}

    mentions_with_urls = {}

    for line in tweets_json.strip().split('\n'):
        tweet = json.loads(line)
        tweet_id = tweet.get('id')
        tweet_content = tweet.get('content', '')
        tweet_url = f"https://x.com/{username}/status/{tweet_id}"

        mentions = re.findall(r"@(\w+)", tweet_content)
        for mention in mentions:
            full_handle = f"@{mention}"
            if full_handle not in mentions_with_urls:
                mentions_with_urls[full_handle] = []
            mentions_with_urls[full_handle].append(tweet_url)

    return mentions_with_urls

# Check if a username is tied to an active X account
def is_account_active(username):
    command = f"snscrape twitter-user {username}"
    try:
        _ = subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL, text=True)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    all_mentions = {}
    checked_mentions = {}

    inactive_mentions = set()
    active_mentions = set()

    # Gather and write mentions
    with open(output_file, "w") as f:
        for username in usernames:
            user_mentions = get_user_mentions_with_urls(username)

            if user_mentions:
                f.write(f"\nMentions by @{username}:\n")
                for mention, urls in sorted(user_mentions.items()):
                    f.write(f"  {mention} ({len(urls)} times)\n")
                    for url in urls:
                        f.write(f"    ↳ {url}\n")
                all_mentions.update(user_mentions)
            else:
                f.write(f"\n@{username} had no mentions or failed to scrape.\n")

    print("\n🧪 Validating mentioned accounts...\n")

    # Check if each mentioned account is active
    for mention in sorted(all_mentions.keys()):
        clean_username = mention.lstrip("@")

        if clean_username in checked_mentions:
            continue

        if is_account_active(clean_username):
            print(f"✅ @{clean_username} is active.")
            active_mentions.add(mention)
            checked_mentions[clean_username] = True
        else:
            print(f"❌ @{clean_username} is inactive or does not exist.")
            inactive_mentions.add(mention)
            checked_mentions[clean_username] = False

        time.sleep(1.5)  # delay to avoid rate-limiting

    # Write inactive mentions
    with open(inactive_file, "w") as f:
        f.write("Inactive or invalid mentions:\n")
        for mention in sorted(inactive_mentions):
            f.write(f"{mention}\n")

    # Write active mentions
    with open(active_file, "w") as f:
        f.write("Active mentions:\n")
        for mention in sorted(active_mentions):
            f.write(f"{mention}\n")

    print(f"\n✅ Done.")
    print(f"• Mentions with tweet URLs: '{output_file}'")
    print(f"• Active accounts: '{active_file}'")
    print(f"• Inactive accounts: '{inactive_file}'")

if __name__ == "__main__":
    main()
