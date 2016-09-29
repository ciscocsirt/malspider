from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from dashboard.models import Page
from dashboard.models import Element
from dashboard.models import Organization
from dashboard.models import Alert
from dashboard.models import Whitelist
from datetime import datetime,timedelta
from urlparse import urlparse
import re
import sys
import os
import glob
from tld import get_tld

from django.db.models import Q

class Command(BaseCommand):
    help = 'Analyzes pages crawled in the last 24 hours and generates alerts.'

    def handle(self, *args, **options):
        A = Analyzer()
        A.generate_alerts(datetime.now() - timedelta(days=1))


class Blacklists(object):
    """ IP/domain blacklist storage and matching. """

    def __init__(self):
        self.blacklists = {}
        self.discover_blacklists()

    def discover_blacklists(self):
        """ Load blacklists from files in configured directory, stores contents
        in memory.
        """
        glob_pattern = os.path.join(settings.BLACKLIST_DIRECTORY, '*.blacklist')
        for fpath in glob.glob(glob_pattern):
            bl_name = os.path.split(fpath)[-1].replace('.blacklist', '')
            with open(fpath) as fd:
                data = fd.read()
                if '\n' in data:
                    data = data.replace('\r', '')
                else:
                    data = data.replace('\r', '\n')
                self.blacklists[bl_name] = set(filter(None, data.split('\n')))
        print "Loaded blacklists: {0}".format(', '.join(self.blacklists.keys()))

    def get_blacklist_names(self):
        return self.blacklists.keys()

    def match(self, address):
        """ Simple exact matcher that generates matching black list names. """
        for bl_name, entries in self.blacklists.items():
            if urlparse(address).netloc in entries:
                yield bl_name
            else:
                try:
                    domain = get_tld(address)
                    if domain in entries:
                        yield bl_name
                except Exception as exc:
                    # This might generate a lot of error messages.
                    pass

class Analyzer(object):
    def __init__(self):
        self.custom_whitelist = set(Whitelist.objects.values_list('pattern', flat=True))
        self.alexa_whitelist = set(line.strip() for line in open(os.path.join(sys.path[0],'alexa-50k-whitelist.csv'), 'r'))
        self.blacklists = None
        if settings.ENABLE_BLACKLISTS:
            self.blacklists = Blacklists()

    def check_whitelist(self, uri):

        if not uri:
            return False

        if any(whitelist_str in uri for whitelist_str in self.custom_whitelist):
            print "in custom whitelist!"
            return True

        parsed_uri = urlparse(uri)
        parsed_domain = '{uri.netloc}'.format(uri=parsed_uri)

        try:
            domain = get_tld(uri)
            if domain in self.alexa_whitelist:
                return True
        except Exception as e:
            print "error: ", str(e)

        return False

    def generate_alerts(self, search_start_time):
        alerts = {}
        #alerts["HIDDEN ELEMENT"] = self.get_hidden_iframes_css(search_start_time)
        alerts["HIDDEN ELEMENT"] = self.get_hidden_iframes(search_start_time)
        alerts["PROFILING SCRIPT"] = self.get_cart_id_injections(search_start_time)
        alerts["SCANBOX FRAMEWORK"] = self.get_scanbox_injections(search_start_time)

        # If we have blacklists enabled, check all elements.
        if self.blacklists:
            for bl_name in self.blacklists.get_blacklist_names():
                alerts["BLACKLIST " + bl_name] = []

            elements = self.get_all_elements(search_start_time)
            for elem in elements.iterator():
                uri = elem.uri
                if not uri:
                    continue
                for bl_name in self.blacklists.match(uri):
                    alerts["BLACKLIST " + bl_name].append(elem)

        for alert in alerts:
            for elem in alerts[alert]:
                if hasattr(elem, 'uri') and (elem.domain == None or not self.check_whitelist(elem.uri)):
                    print "alert for ", elem.raw
                    infected_page = Page.objects.get(Q(event_time__gte=search_start_time),page_id=elem.page_id)                   
                    infected_page_url = ""
                    if infected_page is not None:
                        infected_page_url = infected_page.uri
                    a = Alert(reason=alert, raw=elem.raw, uri=elem.uri, page=infected_page_url, page_id=elem.page_id, org_id=elem.org_id, event_time=elem.event_time)
                    a.save()

        alerts_nocheck = {}
        if settings.ENABLE_EMAIL_ALERTS:
            alerts_nocheck["EMAIL DISCLOSURE"] = self.get_email_disclosures(search_start_time)
            print "here"
        alerts_nocheck["SUSPICIOUS SCRIPT"] = self.get_pastebin_injections(search_start_time)
        alerts_nocheck["WEBSHELL INJECTION"] = self.get_shell_injections(search_start_time)
        alerts_nocheck["VBSCRIPT INJECTION"] = self.get_vbscript_injections(search_start_time)
        alerts_nocheck["EVERCOOKIE SCRIPT"] = self.get_evercookie_scripts(search_start_time)
        alerts_nocheck["CLICKY"] = self.get_clicky(search_start_time)
        
        for alert in alerts_nocheck:
            for elem in alerts_nocheck[alert]:
                print elem.raw
                infected_page = Page.objects.get(Q(event_time__gte=search_start_time),page_id=elem.page_id)                   
                infected_page_url = ""
                if infected_page is not None:
                    infected_page_url = infected_page.uri
                a = Alert(reason=alert, raw=elem.raw, uri=elem.uri, page=infected_page_url, page_id=elem.page_id, org_id=elem.org_id, event_time=elem.event_time)
                a.save()

    def get_all_elements(self, search_start_time):
        return Element.objects.filter(Q(event_time__gte=search_start_time))

    def get_hidden_iframes(self, search_start_time):
        iframes = Element.objects.filter(Q(attr_width='0') | Q(attr_width='1') | Q(attr_height='0') | Q(attr_height='1'), Q(event_time__gte=search_start_time), Q(tag_name="iframe") | Q(tag_name='object') | Q(tag_name='embed')).exclude(uri__isnull=True).exclude(uri='')
        return iframes

    def get_scanbox_injections(self, search_start_time):
        scanbox_regex = re.compile("(\/.\/\?.)|(\/.\/.\.php\?.)|(\/.\/.\recv.php\?.)", re.IGNORECASE)
        scanbox_elements = Element.objects.filter(Q(event_time__gte=search_start_time), Q(tag_name='script') | Q(tag_name='iframe'), Q(uri__regex=scanbox_regex.pattern))
        return scanbox_elements

    def get_evercookie_scripts(self, search_start_time):
        evercookie_script_regex = re.compile("evercookie", re.IGNORECASE)
        evercookie_uri_regex = re.compile("(evercookie_png.php)|(evercookie_etag.php)|(evercookie_cache.php)", re.IGNORECASE)
        evercookie_scripts = Element.objects.filter(Q(event_time__gte=search_start_time), Q(uri__regex=r'evercookie') | (Q(tag_name='script') & Q(uri__regex=evercookie_script_regex.pattern)))
        return evercookie_scripts
        
    def get_cart_id_injections(self, search_start_time):
        cart_regex = re.compile("\\/\\?cart_id=[0-9]+$", re.IGNORECASE)
        cart_elements = Element.objects.filter(Q(event_time__gte=search_start_time), Q(tag_name='script') | Q(tag_name='iframe'), Q(uri__regex=cart_regex.pattern))
        return cart_elements
        
    def get_clicky(self, search_start_time):
        clicky_regex = re.compile("clicky_site_ids", re.IGNORECASE | re.MULTILINE)
        clicky_elements = Element.objects.filter(Q(event_time__gte=search_start_time), Q(tag_name='script'), Q(raw__regex=clicky_regex.pattern))
        return clicky_elements

    def get_shell_injections(self, search_start_time):
        shell_regex = re.compile("(\/r57.php)|(r57shell)|(\/c99.php)|(c99shell)", re.IGNORECASE)
        shell_elements = Element.objects.filter(Q(event_time__gte=search_start_time), Q(tag_name='script') | Q(tag_name='iframe'), Q(uri__regex=shell_regex.pattern))
        return shell_elements

    def get_pastebin_injections(self, search_start_time):
        pastebin_regex = re.compile("pastebin\.", re.IGNORECASE)
        #pastebin_elements = Element.objects.filter(Q(event_time__gte=search_start_time), Q(tag_name='script') | Q(tag_name='iframe'), Q(uri__regex=pastebin_regex))
        pastebin_elements = Element.objects.filter(Q(event_time__gte=search_start_time), Q(tag_name='script') | Q(tag_name='iframe'), Q(uri__regex=pastebin_regex.pattern))
        return pastebin_elements

    def get_vbscript_injections(self, search_start_time):
        vbscript_regex = re.compile('VBScript', re.IGNORECASE)
        vbscript_elements = Element.objects.filter(Q(event_time__gte=search_start_time), Q(attr_language__regex=vbscript_regex.pattern))
        return vbscript_elements

    def get_email_disclosures(self, search_start_time):
        email_regex = re.compile("[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9.-]@[a-zA-Z0-9][a-zA-Z0-9._-]*[a-zA-Z0-9]\.[a-zA-Z]{2,4}$", re.IGNORECASE)
        email_elements = Element.objects.filter(Q(event_time__gte=search_start_time), Q(uri__regex=email_regex.pattern))
        return email_elements

    def get_hidden_iframes_css(self, search_start_time):
        ret_elements = []
        hidden_links = Element.objects.filter(Q(tag_name="iframe") & Q(css_class__isnull=False))

        for link in hidden_links:
            print link.id
            hidden = False
            if hasattr(link,'css_attr_top') and hasattr(link,'attr_height'):
                try:
                    #calculate the actual position of this iframe: calculate based off the css 'top' attribute the inline 'height' value
                    true_position = int(link.css_attr_top) + int(link.attr_height)
                    if true_position <= 0:
                        hidden = True
                except:
                    print "Could not convert to an integer height: ", str(link.attr_height)
                    print link.raw
            elif hasattr(link, 'css_attr_bottom') and hasattr(link,'attr_height'):
                try:
                    #calculate the actual position of this iframe: calculate based off the css 'bottom' attribute the inline 'height' value
                    true_position = int(link.css_attr_bottom) + int(link.attr_height)
                    if true_position <= 0:
                        hidden = True
                except:
                    print "Could not convert to an integer height: ", str(link.attr_height)
                    print link.raw
            elif hasattr(link,'css_attr_left') in hasattr(link,'attr_width'):
                try:
                    #calculate the actual position of this iframe: calculate based off the css 'left' attribute the inline 'width' value
                    true_position = int(link.css_attr_left) + int(link.attr_width)
                    if true_position <= 0:
                        hidden = True

                except:
                    #print "Could not convert to an integer width: ", str(link.attr_width)
                    print link.raw

            elif hasattr(link, 'css_attr_left') and hasattr(link, 'attr_width'):
                try:
                    #calculate the actual position of this iframe: calculate based off the css 'right' attribute the inline 'width' value
                    true_position = int(link.css_attr_right) + int(link.attr_width)
                    if true_position <= 0:
                        hidden = True

                except:
                    print "Could not convert to an integer width: ", str(link.attr_width)
                    print link.raw


            if hidden == True and link.uri:
                css_elements = Element.objects.filter(Q(event_time__gte=search_start_time), Q(tag_name='style'), Q(referer=link.referer), Q(css_class=link.css_class))
                if css_elements is not None and len(css_elements) >= 1:
                    link.raw = css_elements[0].raw + "\n" + link.raw
                    ret_elements.append(link)
        return ret_elements
