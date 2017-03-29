#  
#  Copyright (c) 2016-present, Cisco Systems, Inc. All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree. 
#

import json
import csv
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.middleware import get_user
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render, render_to_response
from dashboard.models import Page
from dashboard.models import Element
from dashboard.models import Alert
from dashboard.models import Organization
from dashboard.models import Whitelist
from django.conf import settings
from dashboard.functions.model_helper import ModelQuery
from dashboard.functions.scrapy_manager import ScrapyManager
from urlparse import urlparse
from .forms import LoginForm
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def login_view(request):
    msg = None
    if request.method == "POST":
        form = LoginForm(request.POST) 
        if form.is_valid():
            uname = form.cleaned_data['username']
            pwd = form.cleaned_data['password']
            user = authenticate(username=uname, password=pwd)
            if user:
                login(request,user)
                return HttpResponseRedirect("/") 
            else:
                msg = "Authentication Failed!"
    else:
        form = LoginForm()

    template = loader.get_template("dashboard_login.html")
    return HttpResponse(template.render({'form': form, 'msg':msg}, request))

def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/login/")

def index(request, org_id=None):
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

    org_obj = ModelQuery.get_org_by_id(org_id)
    jobid = None
    scan_domain = None
    error = None
    if org_obj:
        output = SM.schedule_job(org_id,org_obj.domain)
        if 'jobid' in output:
            jobid = output['jobid']
            scan_domain = org_obj.domain
    elif org_obj is None and org_id is not None:
        error = "Error: Invalid Organization ID!"

    context = RequestContext(request, {'elems_count':elems_count,'pages_count':pages_count, 'pending_jobs':pending_jobs, 'running_jobs':running_jobs, 'finished_jobs':finished_jobs, 'unique_alerts':unique_alerts, 'alert_count_by_reason':alert_count_by_reason, 'all_orgs':all_orgs, 'top_offenders':top_offenders, 'scrapyd_connected':scrapyd_connected, 'jobid':jobid,'scan_domain':scan_domain, 'error':error})
    return HttpResponse(template.render(context))

def daemon(request, jobid=None):
    SM = ScrapyManager("malspider", "full_domain", "http://0.0.0.0:6802")
    crawl_jobs = SM.get_all_jobs_by_project()
    pending_jobs = []
    running_jobs = []
    finished_jobs = []
    scrapyd_connected = []

    crawl_jobs = SM.get_all_jobs_by_project()
    if crawl_jobs is not None:
        pending_jobs = crawl_jobs['pending']
        running_jobs = crawl_jobs['running']
        finished_jobs = crawl_jobs['finished']
        scrapyd_connected = 1

    context = RequestContext(request, {'finished_jobs':finished_jobs, 'pending_jobs':pending_jobs, 'running_jobs':running_jobs, 'status':scrapyd_connected, 'jobid':jobid})
    template = loader.get_template("dashboard_daemon.html")
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

# false positive view
def fp_view(request):
    if request.method == "GET":
        return HttpResponse(json.dumps({"Invalid Request"}, content_type="application/json"))
    else:
	alert_ids = request.POST.get("alert_ids")
	whitelist_pattern = request.POST.get("whitelist_pattern")
        count = 0
	my_alert = ""
	if alert_ids:
		alert_ids = alert_ids.split("\r\n")
		for alert_id in alert_ids:
			if request.POST.get("remove") == "remove_all":
				alert = Alert.objects.filter(id=alert_id).first()
				if alert:
					alert_uri = alert.uri
					alert_one = Alert.objects.filter(id=alert_id).delete()
					alert_two = Alert.objects.filter(uri=alert_uri).delete()
					wlp = Whitelist(pattern=alert_uri)
					wlp.save()
			else:
				Alert.objects.filter(id=alert_id).delete()
	if whitelist_pattern:
		try:
			wlp = Whitelist(pattern=whitelist_pattern)
			wlp.save()
		except:
			pass
		

			
	response_data = {"msg":"ok"}
        return HttpResponse(json.dumps(response_data), content_type="application/json")


def alert_export_view(request,time_frame="last_24_hours"):
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="malspider_alerts.csv"'

    writer = csv.writer(response)
    writer.writerow(['alert_reason', 'source_page','requested_resource','raw_html'])

    alerts = ModelQuery.get_alerts_by_timeframe(time_frame)
    for alert in alerts:
        writer.writerow([alert.reason,alert.page, alert.uri, unicode(alert.raw).encode("utf-8")])

    return response
