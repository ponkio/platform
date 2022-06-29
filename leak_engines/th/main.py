import subprocess
import sys
import json 
import base64
from unittest.result import STDERR_LINE
from urllib import request 
import pymongo
import asyncio
import datetime

async def run_trufflehog(clone_details):
    repo = clone_details['clone_url']
    cmd = f'trufflehog --cleanup --json {repo}'
    print(cmd)
    proc = await asyncio.create_subprocess_shell(cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    
    # Could be optimized
    stdout, stderr = await proc.communicate()

    if not stderr:
        ss_repo_id = base64.b64encode(repo.encode('utf-8')).decode('utf-8')
        truffle_results = {
            'repo': repo,        
            'ss_repo_id':ss_repo_id,
            'trufflehog_report': list(map(json.loads, stdout.decode('utf-8').split('\n')[:-1])),
            'last_scanned': datetime.datetime.utcnow()
        }

        if not le_th_col.find_one({'ss_repo_id':ss_repo_id}):
            try:
                le_th_col.insert_one(truffle_results)
            except Exception as err:
                print("Unable to write repo to DB :: ", err)
        else:
            try:
                le_th_col.replace_one({'ss_repo_id':ss_repo_id}, 
                    truffle_results, 
                    upsert=True)
            except Exception as err:
                print("Unable to write repo to DB :: ", err)   
    else:
        print(stderr)

    return

async def main(repo_list):
    tasks = [run_trufflehog(repo) for repo in repo_list]
    return await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        mongo = pymongo.MongoClient("mongodb://localhost:27017/")
        ss_plat_db = mongo['ss_platform']
        le_th_col = ss_plat_db['le_trufflehog']
        pub_github_col = ss_plat_db['pub_github_repos']
    except Exception as err:
        print("Unable to connect to mongo DB :: ", err)
    #print(list(pub_github_col.find({}, {'_id':0,'clone_url':1}))[1:2])
    asyncio.run(main(list(pub_github_col.find({}, {'_id':0,'clone_url':1}))[1:5]))

    
    


#print(json.dumps(run_trufflehog(sys.argv[1])))