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
from dashboard.models import Organization
from dashboard.models import Alert
from django.core.management.base import BaseCommand, CommandError
from dashboard.functions.scrapy_manager import ScrapyManager

class Command(BaseCommand):
    help = 'Cancels any outstanding or hung jobs and starts crawling sites found in the Organizations collection.'

    def handle(self, *args, **options):
        SM = ScrapyManager("malspider", "full_domain", "http://0.0.0.0:6802")
        SM.cancel_all_jobs()
        orgs = Organization.objects.all()
        for org in orgs:
            print "Scheduling job for ", org.domain
            SM.schedule_job(org.id, org.domain)
