# force update
from truffleHog import truffleHog
from github import Github
import json
import hashlib
from git import Repo, NULL_TREE
import pymongo
import base64
import shutil

class EventHandler:
    def __init__(self):
        self._mongo = pymongo.MongoClient('mongodb://localhost:27017/')
        self.__ss_plat_db = self._mongo['ss_platform']
        self.__le_trufflehog_col = self.__ss_plat_db['le_trufflehog']

        self.g = Github()


    ## This gets called on_message
    def handle_event(self,event):
        print("[~] Handling incoming event")

        event = json.loads(event.decode('utf-8'))
        before_commit = event['payload']['before']
        event_branch = event['payload']['ref']
        #pygit_repo = self.g.get_repo(event['repo_name'])

        project_path = truffleHog.clone_git_repo(event['repo_url'])

        repo_name = event['repo_name']
        repo = Repo(project_path)
        branches = repo.remotes.origin.fetch(event_branch)
        since_commit = before_commit
        already_searched = set()

        for remote_branch in branches:
            since_commit_reached = False
            branch_name = remote_branch.name
            prev_commit = None
            for curr_commit in repo.iter_commits(branch_name):
                commitHash = curr_commit.hexsha
                if commitHash == since_commit:
                    since_commit_reached = True
                    break
                # if not prev_commit, then curr_commit is the newest commit. And we have nothing to diff with.
                # But we will diff the first commit with NULL_TREE here to check the oldest code.
                # In this way, no commit will be missed.
                diff_hash = hashlib.md5((str(prev_commit) + str(curr_commit)).encode('utf-8')).digest()
                if not prev_commit:
                    prev_commit = curr_commit
                    continue
                elif diff_hash in already_searched:
                    prev_commit = curr_commit
                    continue
                else:
                    diff = prev_commit.diff(curr_commit, create_patch=True)
                # avoid searching the same diffs
                already_searched.add(diff_hash)

                foundIssues = truffleHog.diff_worker(diff, curr_commit, prev_commit, event_branch, commitHash, custom_regexes={}, do_entropy=True, do_regex=True, printJson=True, surpress_output=True, path_inclusions=None, path_exclusions=None, allow={})

                prev_commit = curr_commit
                if len(foundIssues) > 0:
                    obj = {}
                    obj['ss_repo_id'] = base64.b64encode(repo_name.encode('utf-8')).decode('utf-8')
                    obj['repo'] = repo_name
                    obj['trufflehog_report'] = foundIssues
                    print('[+] Possible ecrets discovered in: ', repo_name)
                    ## Should check for duplicate secrets and not push one that already exists
                    if not self.__le_trufflehog_col.find_one({'repo':repo_name}):
                        try:
                            self.__le_trufflehog_col.insert_one(obj)
                        except Exception as err:
                            print("Unable to write repo to DB :: ", err)
                    else:
                        try:
                            self.__le_trufflehog_col.update_one({'repo':repo_name}, {'$push':{'trufflehog_report': foundIssues},'$set':{'repo':repo_name, 'ss_repo_id':base64.b64encode(repo_name.encode('utf-8')).decode('utf-8')}}, upsert=True)
                        except Exception as err:
                            print("Unable to write repo to DB :: ", err)
                else:
                    continue
            if since_commit_reached:
                    # Handle when there's no prev_commit (used since_commit on the most recent commit)
                if prev_commit is None:
                        continue
                diff = prev_commit.diff(curr_commit, create_patch=True)
            else:
                diff = curr_commit.diff(NULL_TREE, create_patch=True)

            foundIssues = truffleHog.diff_worker(diff, curr_commit, prev_commit, event_branch, commitHash, custom_regexes={}, do_entropy=True, do_regex=True, printJson=True, surpress_output=True, path_inclusions=None, path_exclusions=None, allow={})
            if len(foundIssues) > 0:
                obj = {}
                obj['ss_repo_id'] = base64.b64encode(repo_name.encode('utf-8')).decode('utf-8')
                obj['repo'] = repo_name
                obj['trufflehog_report'] = foundIssues
                print('[+] Possible ecrets discovered in: ', repo_name)
                if not self.__le_trufflehog_col.find_one({'repo':repo_name}):
                    try:
                        self.__le_trufflehog_col.insert_one(obj)
                    except Exception as err:
                        print("Unable to write repo to DB :: ", err)
                else:
                    try:
                        self.__le_trufflehog_col.update_one({'repo':repo_name}, {'$push':{'trufflehog_report': foundIssues},'$set':{'repo':repo_name, 'ss_repo_id':base64.b64encode(repo_name.encode('utf-8')).decode('utf-8')}}, upsert=True)
                    except Exception as err:
                        print("Unable to write repo to DB :: ", err)
            else:
                continue

            # Check if since_commit was used to check which diff should be grabbed
            if since_commit_reached:
                # Handle when there's no prev_commit (used since_commit on the most recent commit)
                if prev_commit is None:
                    continue
                diff = prev_commit.diff(curr_commit, create_patch=True)
            else:
                diff = curr_commit.diff(NULL_TREE, create_patch=True)
        
        shutil.rmtree(project_path)
        pass

    

