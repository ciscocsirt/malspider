#  
#  Copyright (c) 2016-present, Cisco Systems, Inc. All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree. 
#

from django.contrib import admin
from django.db import models

class Page(models.Model):
    class Meta:
        db_table = "page"
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'


    status_code = models.CharField(max_length=10)
    uri = models.CharField(max_length=500)
    referer = models.CharField(max_length=500)
    org_id = models.CharField(max_length=50)
    page_id = models.CharField(max_length=50)
    useragent = models.CharField(max_length=500)
    ssdeep_pagesource = models.CharField(max_length=500)
    ssdeep_screenshot = models.CharField(max_length=500)
    screenshot = models.CharField(max_length=500)
    num_offsite_links = models.CharField(max_length=50)
    num_onsite_links = models.CharField(max_length=50)
    event_time = models.DateField()

class Element(models.Model):
    class Meta:
        db_table = "element"
        verbose_name = 'Element'
        verbose_name_plural = 'Elements'

    domain = models.CharField(max_length=500)
    event_time = models.DateField()
    uri = models.CharField(max_length=500)
    tag_name = models.CharField(max_length=50)
    referer = models.CharField(max_length=500)
    onsite = models.CharField(max_length=25)
    org_id = models.CharField(max_length=50)
    page_id = models.CharField(max_length=50)
    raw = models.TextField()
    attr_width = models.CharField(max_length=50)
    attr_height = models.CharField(max_length=50)
    attr_type = models.CharField(max_length=50)
    attr_text = models.CharField(max_length=50)
    attr_script_type = models.CharField(max_length=50)
    attr_language = models.CharField(max_length=50)
    css_attr_top = models.CharField(max_length=50)
    css_attr_bottom = models.CharField(max_length=50)
    css_attr_left = models.CharField(max_length=50)
    css_attr_right = models.CharField(max_length=50)
    css_attr_visibility = models.CharField(max_length=50)
    css_class = models.CharField(max_length=50)

class Alert(models.Model):
    def __unicode__(self):
        return self.reason + " --> " + self.raw
    class Meta:
        db_table = "alert"
        verbose_name = 'Alert'
        verbose_name_plural = 'Alerts'

    reason = models.CharField(max_length=500)
    uri = models.CharField(max_length=500)
    raw = models.TextField()
    event_time = models.DateTimeField()
    page_id = models.CharField(max_length=50)
    page = models.CharField(max_length=500)
    org_id = models.CharField(max_length=500)

    def get_reason(self):
        return self.reason
    get_reason.short_description = "Alert Reason"

    def get_uri(self):
        return self.uri
    get_uri.short_description = "Requested URI"

    def get_raw(self):
        return self.raw
    get_raw.short_description = "Raw HTML Element"

    def get_time(self):
        return self.event_time
    get_time.short_description = "Alert Date"

    def get_page(self):
        return self.page
    get_page.short_description = "Found on Page"

    def get_org(self):
        return self.org_id
    get_org.short_description = "Organization"

class Organization(models.Model):
    def __unicode__(self):
        return self.org_name

    class Meta:
        db_table = "organization"
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'

    org_name = models.CharField(max_length=500)
    category = models.CharField(max_length=500)
    domain = models.CharField(max_length=500)

    def get_category(self):
        return self.category
    get_category.short_description = "Category"

    def get_org(self):
        return self.org_name
    get_org.short_description = "Organization"

    def get_domain(self):
        return self.domain
    get_domain.short_description = "Domain"

class Whitelist(models.Model):
    def __unicode__(self):
        return self.pattern

    pattern = models.CharField(max_length=500)

    class Meta:
        db_table = "whitelist"
        verbose_name = "Custom Whitelist"
        verbose_name_plural = "Custom Whitelist"

    def get_pattern(self):
        return self.pattern

class EmailAlert(models.Model):
    def __unicode__(self):
        return self.subject
    class Meta:
        db_table = "email_alert"
        verbose_name = 'Email Alert'
        verbose_name_plural = 'Email Alerts'

    subject = models.CharField(max_length=500)
    recipients = models.TextField()
    frequency = models.CharField(max_length=50, choices=[('hourly','hourly'),('daily','daily'), ('weekly','weekly')])

    def get_subject(self):
        return self.subject
    get_subject.short_description = "Email Subject"

    def get_recipients(self):
        return self.recipients
    get_recipients.short_description = "Email Recipient(s), separate with new line"

    def get_frequency(self):
        return self.frequency
    get_frequency.short_description = "Alert Frequency"
