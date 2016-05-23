#  
#  Copyright (c) 2016-present, Cisco Systems, Inc. All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree. 
#

from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404
from dashboard.models import Page
from dashboard.models import Element
from dashboard.models import Organization
from django.conf import settings
from dashboard.functions.model_helper import ModelQuery
from dashboard.functions.scrapy_manager import ScrapyManager
from urlparse import urlparse

def index(request):
    SM = ScrapyManager("malspider", "full_domain", "http://0.0.0.0:6802")
    crawl_jobs = SM.get_all_jobs_by_project()
    pending_jobs = 0
    running_jobs = 0
    finished_jobs = 0
    scrapyd_connected = 0

    crawl_jobs = SM.get_all_jobs_by_project()
    if crawl_jobs is not None:
        pending_jobs = len(crawl_jobs['pending'])
        running_jobs = len(crawl_jobs['running'])
        finished_jobs = len(crawl_jobs['finished'])
        scrapyd_connected = 1

    unique_alerts = ModelQuery.get_num_unique_alerts()
    alert_count_by_reason = ModelQuery.get_num_alerts_by_reason()

    elems_count = Element.objects.count
    pages_count = Page.objects.count
    template = loader.get_template('dashboard_index.html')
    all_orgs = ModelQuery.get_all_organizations()
    top_offenders = ModelQuery.get_top_offenders()
    my_url = urlparse(request.get_full_path()).hostname or ''
    if my_url == '':
        scrapyd_url = 'http://localhost:6802'
    else:
        scrapyd_url = my_url + ":6802"

    context = RequestContext(request, {'elems_count':elems_count,'pages_count':pages_count, 'pending_jobs':pending_jobs, 'running_jobs':running_jobs, 'finished_jobs':finished_jobs, 'unique_alerts':unique_alerts, 'alert_count_by_reason':alert_count_by_reason, 'all_orgs':all_orgs, 'top_offenders':top_offenders, 'scrapyd_connected':scrapyd_connected, 'my_url':scrapyd_url})
    return HttpResponse(template.render(context))

def pages(request, time_frame="last_24_hours"):
    all_orgs = ModelQuery.get_all_organizations()
    alerts = ModelQuery.get_alerts_by_timeframe(time_frame)
    template = loader.get_template("dashboard_pages.html")
    context = RequestContext(request, {'all_orgs':all_orgs, 'time_frame':time_frame, 'alerts':alerts})
    return HttpResponse(template.render(context))

def page(request, org_id):
    org_obj = ModelQuery.get_org_by_id(org_id)
    if org_obj:
        pages = ModelQuery.get_pages_by_org(org_id)
        alerts = ModelQuery.get_alerts_by_org(org_id)
        context = RequestContext(request, {'org':org_obj, 'urls_requested':pages, 'alerts':alerts})
    else:
        context = RequestContext(request, {'error':'Could not find any analysis for this page id'})

    template = loader.get_template('dashboard_page.html')
    return HttpResponse(template.render(context))
