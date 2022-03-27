import github
from github import Github
import pymongo
from datetime import datetime
import time
'''
https://api.github.com/events
- public api events on github
    - maybe write logic to use this somehow
'''
g = Github(per_page=100)

try:
    mongo = pymongo.MongoClient("mongodb://localhost:27017/")
    ss_plat_db = mongo['ss_platform']
except Exception as err:
    print("Unable to connect to mongo DB :: ", err)

# returns num seconds till next run
def check_rate_limit():
    rate_limit = g.get_rate_limit().raw_data
    if rate_limit['core']['remaining'] > 10:
        return ("continue", 0)
    else:
        current_time = time.time()
        rl_reset_time = rate_limit['core']['reset']
        # if (wait_time := (rl_reset_time - current_time)) > 0:
        #     print(f"Rate limit is reached, sleeping for: {wait_time:.2f}s")
        #     time.sleep(rl_reset_time)
        return ("wait", (rl_reset_time - current_time))

def populate_public_repos(since_repo_id):
    wait_sec = check_rate_limit()[1]
    if wait_sec > 0:
        print(f"Rate limit is reached, sleeping for: {wait_sec:.2f}s")
        time.sleep(wait_sec)
        
    pub_repo_collection = ss_plat_db['pub_github_repos']
    processed_repo_count = int()
    current_repo_id = int()
    try:
        for repo in g.get_repos(since_repo_id,'all'):
            wait_sec = check_rate_limit()[1]
            current_repo_id = repo.id

            if wait_sec > 0:
                print(f"Current repo count: {processed_repo_count}")
                print(f"Rate limit hit on repo id: {repo.id}\nSleeping for: {wait_sec}s")
                time.sleep(wait_sec + 30)
                print(f"Resuming on repo: {current_repo_id}")
        
            new_public_repo = {}

            new_public_repo['name'] = repo.full_name
            new_public_repo['clone_url'] = repo.clone_url
            new_public_repo['github_id'] = repo.id
            new_public_repo['discovered_at'] = datetime.utcnow()
            new_public_repo['last_discovered'] = datetime.utcnow()
            new_public_repo['owner_name'] = repo.owner.name

            if not pub_repo_collection.find_one({'github_id':repo.id}):
                try:
                    pub_repo_collection.insert_one(new_public_repo)
                except Exception as err:
                    print("Unable to write repo to DB :: ", err)
            else:
                try:
                    del new_public_repo['discovered_at']
                    pub_repo_collection.update_one({'github_id':repo.id}, 
                        {'$set':new_public_repo}, 
                        upsert=True)
                except Exception as err:
                    print("Unable to write repo to DB :: ", err)      

            processed_repo_count += 1
    except github.GithubException as err:
        print(f"Caught github error on repo: {current_repo_id}:\n{err}")
        populate_public_repos(current_repo_id)
                   