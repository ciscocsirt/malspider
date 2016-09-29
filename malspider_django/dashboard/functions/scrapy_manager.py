#  
#  Copyright (c) 2016-present, Cisco Systems, Inc. All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree. 
#

import os
import sys
import urllib
import urllib2
import json

class ScrapyManager():
    def __init__(self, project_name, spider_name, scrapyd_url):
        self.project_name = project_name
        self.spider_name = spider_name
        self.scrapyd_url = scrapyd_url

    def get_projects(self):
        response = urllib2.urlopen(self.scrapyd_url+"/listprojects.json")
        json_data = json.load(response)
        if json_data and 'projects' in json_data:
            return json_data['projects']
        else:
            return None

    def get_outstanding_jobs_by_project(self):
        response = urllib2.urlopen(self.scrapyd_url+"/listjobs.json?project="+self.project_name)
        try:
            json_data = json.load(response)
        except:
            return None

        all_jobs = []
        if json_data and 'running' in json_data:
            for job in json_data['running']:
                if 'id' in job:
                    all_jobs.append(job['id'])

        if json_data and 'pending' in json_data:
            for job in json_data['pending']:
                if 'id' in job:
                    all_jobs.append(job['id'])

        return all_jobs

    def get_all_jobs_by_project(self):
        try:
            response = urllib2.urlopen(self.scrapyd_url+"/listjobs.json?project="+self.project_name)
            json_data = json.load(response)
            return json_data
        except:
            return None

    def cancel_job(self, job_id):
        data = {
                "project":self.project_name,
                "job":job_id,
        }
        req = urllib2.Request(self.scrapyd_url+"/cancel.json", urllib.urlencode(data))
        response = urllib2.urlopen(req)
        json_data = json.load(response)
        return json_data

    def cancel_all_jobs(self):
        print "Canceling all outstanding jobs"
        jobs = self.get_outstanding_jobs_by_project()
        for job in jobs:
            result = self.cancel_job(job)
            if result and 'status' in result and result['status'] == 'ok':
                print "canceled job ", job, " for project '", self.project_name, "'"
            else:
                print "could not cancel job ", job, " for project '", project, "'"

    def schedule_job(self, org_id, domain):
        if "www." in domain:
            allowed_domains = domain + "," + domain[4:]
            start_urls = 'https://' + domain + ',https://' + domain[4:] + ',http://' + domain + ',http://' + domain[4:] 
        else:
            allowed_domains = domain + ",www." + domain
            start_urls = 'https://www.' + domain + ',https://' + domain + ',http://' + domain + ',http://www.' + domain

        params = {}
        params['spider'] = self.spider_name
        params['project'] = self.project_name
        params['allowed_domains']  = allowed_domains
        params['start_urls'] = start_urls
        params['org'] = org_id
        params['domain'] = domain
        req  = urllib2.Request(self.scrapyd_url+"/schedule.json", urllib.urlencode(params))
        response = urllib2.urlopen(req)
        return json.load(response)
