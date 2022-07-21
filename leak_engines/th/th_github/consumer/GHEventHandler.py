# force update
import pymongo
import base64
import shutil
import subprocess
import json
import logging
from time import sleep
import uuid

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

class EventHandler:
    def __init__(self):
        
        self._mongo = pymongo.MongoClient('mongodb://localhost:27017/')
        self.__ss_plat_db = self._mongo['ss_platform']
        self.__le_trufflehog_col = self.__ss_plat_db['le_trufflehog']


    
    def _stream_stdout(self, process):
        go = process.poll() is None
        for result in process.stdout:
            result = json.loads(result.decode('utf-8'))
            #if result.get('error') != None:
            self.__le_trufflehog_col.insert_one(result)
            print("[+]Added result to collection")
        return go

    def run_trufflehog(self, repo, prev_commit):
        print(repo)
        cmd = f"trufflehog --json git --since-commit={prev_commit} {repo}"
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while self._stream_stdout(process):
            #pass
            sleep(0.1)
    ## This gets called on_message
    def handle_event(self,event):
        print("[~] Handling incoming event")
        #logging.debug(event)
        event = json.loads(event.decode('utf-8'))
        prev_commit = event['payload'].get('before')
        event_branch = event.get('ref')
        repo_url = event.get('repo_url')

        self.run_trufflehog(repo_url, prev_commit)


        #pygit_repo = self.g.get_repo(event['repo_name'])

    

