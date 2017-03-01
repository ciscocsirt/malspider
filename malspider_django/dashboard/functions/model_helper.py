#  
#  Copyright (c) 2016-present, Cisco Systems, Inc. All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree. 
#

from dashboard.models import Page
from dashboard.models import Element
from dashboard.models import Alert
from dashboard.models import Organization
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.db.models import Count

class ModelQuery:
    @staticmethod
    def get_all_organizations():
        all_orgs = Organization.objects.all()
        return all_orgs

    @staticmethod
    def get_org_by_id(org_id):
        try:
            org_obj = Organization.objects.get(id=org_id)
            return org_obj
        except:
            return None

    @staticmethod
    def get_pages_by_org(org_id):
        all_pages = Page.objects.filter(org_id=org_id).values('uri').distinct()
        return all_pages

    @staticmethod
    def get_alerts_by_org(org_id):
        all_alerts = Alert.objects.filter(org_id=org_id).values('page','reason','uri','raw').distinct()
        return all_alerts

    @staticmethod
    def get_alert_by_id(alert_id):
        return Alert.objects.filter(id=alert_id).first()

    @staticmethod
    def get_page_by_id(page_id):
        if page_id:
            page_obj = Pages.objects(id=ObjectId(page_id))
            if page_obj and len(page_obj) == 1:
                return page_obj[0]
        return None

    @staticmethod
    def get_elems_by_page_obj(page_obj):
        if page_obj and 'uri' in page_obj:
            return Elements.objects(referer=page_obj.uri)

        return None

    @staticmethod
    def get_num_unique_alerts():
        all_alerts = ModelQuery.get_alerts_by_timeframe('all_time')
        if all_alerts is not None:
            return len(list(all_alerts))
        return 0

    @staticmethod
    def get_num_alerts_by_reason():
        num_alerts = Alert.objects.values('reason').annotate(num_alerts=Count('reason')).order_by('-num_alerts')[:10]
        return num_alerts

    @staticmethod
    def get_top_offenders():
        offenders = Alert.objects.filter(org_id=1592).select_related()
        return offenders

    @staticmethod
    def get_alerts_by_timeframe(time_frame="last_24_hours"):
        dt = datetime.now()
        if time_frame == "all_time":
            dt = dt - relativedelta(years=25)
        elif time_frame == "last_90_days":
            dt = dt - timedelta(days=90)
        elif time_frame == "last_30_days":
            dt = dt - timedelta(days=30)
        elif time_frame == "last_7_days":
            dt = dt - timedelta(days=7)
        elif time_frame == "last_3_days":
            dt = dt - timedelta(days=3)
        else:
            dt = dt - timedelta(days=1)

        dt = dt.strftime('%d-%m-%Y %H:%M:%S')

        sql = """Select id, GROUP_CONCAT(DISTINCT(id) SEPARATOR '\n') alert_ids, GROUP_CONCAT(DISTINCT(reason) SEPARATOR '\n') reasons, GROUP_CONCAT(DISTINCT(uri) SEPARATOR '\n') uris, GROUP_CONCAT(DISTINCT(raw) SEPARATOR '\n') raws from alert WHERE event_time >= STR_TO_DATE('{0}','{1}') GROUP BY reason, page""".format(dt,"%%d-%%m-%%Y %%H:%%i:%%s")

        alerts = Alert.objects.raw(sql)

        return alerts
