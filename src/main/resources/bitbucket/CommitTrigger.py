#
# Copyright 2019 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#


import sys
import json
import requests

def getFileChangesForCommitId(commit_id):
    url_path= "%srest/api/1.0/projects/%s/commits/%s/changes" % (server['url'],repo_full_name,commit_id)
    response = requests.get(url_path, auth=(server['username'], server['password']), headers={}, verify=False)
    if response.status_code == 200:
        changes = json.loads(response.content)
        return [v['path']['name'] for v in changes['values']]

def getFileChanges(old_commit_id, commits):
    if bool(old_commit_id):
        result=[]
        for commit in commits["values"]:
            commit_id = commit["id"]
            if commit_id == old_commit_id:
                break;
            result = result + getFileChangesForCommitId(commit_id)
        return ','.join(result)
    else:
        return ','.join(getFileChangesForCommitId(commits["values"][0]["id"]))

url_path= "%srest/api/1.0/projects/%s/commits?limit=100&until=refs/heads/%s" % (server['url'],repo_full_name,branchName)
response = requests.get(url_path, auth=(server['username'], server['password']), headers={}, verify=False)

if response.status_code != 200:
    if response.status_code == 404 and triggerOnInitialPublish:
        print "Repository '%s' not found in bitbucket. Ignoring." % (repo_full_name)

        if not triggerState:
            branch = commitId = triggerState = 'unknown'
    else:
        print "Failed to fetch branch information from Bitbucket server %s" % server['url']
        response.content
    sys.exit(1)
else:
    commits = json.loads(response.content)

    # build a map of the commit ids for each branch
    newCommit = {}
    commitId = commits["values"][0]["id"]
    newCommit[branchName] = commitId
    commitMsg = commits["values"][0]["message"]

    # trigger state is perisisted as json
    newTriggerState = json.dumps(newCommit)

    if triggerState != newTriggerState:
        oldCommitId =''
        if len(triggerState) != 0:
            oldCommitId = json.loads(triggerState)[branchName]

        fileChanges = getFileChanges(oldCommitId, commits)

        triggerState = newTriggerState

        print("Bitbucket triggered release for %s-%s" % (branchName, commitId))
