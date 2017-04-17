Malspider
===================

Malspider is a web spidering framework that inspects websites for characteristics of compromise. Malspider has three purposes:

 - **Website Integrity Monitoring**: monitor your organization's website (or your personal website) for potentially malicious changes.
 - **Generate Threat Intelligence:** keep an eye on previously compromised sites, currently compromised sites, or sites that may be targeted by various threat actors.
 - **Validate Web Compromises**: Is this website still compromised? 

#### What can Malspider detect?
Malspider has built-in detection for characteristics of compromise like hidden iframes, reconnaisance frameworks, vbscript injection, email address disclosure, etc. As we find stuff we will continue to add classifications to this tool and we hope you will do the same. Malspider will be a much better tool if CIRT teams and security practioners around the world contribute to the project. 

#### What's next? How can I help?
As mentioned above, it is very important to get help from other security practioners. Outside of adding classifications/signatures to the tool, here is a list of enhancements that would benefit the project and the broader infosec community. Don't feel contrained to this list, though.
 - Monitor website for historical changes (ie. a script tag was added today)
 - Develop a better mechanism for adding signatures/classifications
 - Attempt to download and store malware hosted on compromised sites

#### Join the community
Join the official mailing list: https://groups.google.com/forum/#!forum/malspider for support and to talk with other users.


### Installation Prerequisites
-------------
Please make sure these technologies are installed before continuing:

 - Python 2.7.6
 - Updated version of pip
 - mysql

**Note:** If your server already has specific versions of these components installed, you can use a **virtualenv** to create an isolated python environment.

Tested and working on minimal installations of:
- [x] Ubuntu 14
- [x] CentOS 6
- [x] CentOS 7


### (Quick) Installation
-------------------
Start the installation process by running **"./quick_install"** from the command line.  **Please read the prompts carefully!!**

Malspider comes with a **quick_install** script found in the root directory. This scripts attempts to makes the installation process as painless as possible by completing the following steps:

 1. **Install Database**: creates a database titled 'malspider', creates a new mysql user, and applies db schema.
 2. **Install Dependencies**: installs ALL dependencies and modules required by Malspider.
 3. **Django Migrations**:  applies django migrations to the database (necessary for the web app).
 4. **Create Web Admin User**: creates an administrative user for the web application.
 5. **Add Access Control**: creates iptables rules to block port 6802 (used by the daemon) and open port 8080 (web app).
 6. **Add Cronjobs**: creates crontab entries to schedule jobs, analyze data, and purge the database after a period of time.

 
**Note**: _The quick_install script uses scripts found under the **install/** directory. If any of the above steps fail you can attempt to complete them manually using those scripts._

**Note**: _If you need a permanent or production installation of Malspider, please consider using Apache as your webserver. Production instlalation instructions will be released soon._

### (Quick) Start
-------------

Start Malspider by running **"./quick_start"** from the command line.

Malspider comes with a **quick_start** script found in the root directory. This script attempts to start the daemon and the web application.

Malspider can be accessed from your browser on port 8080 @ **http://0.0.0.0:8080**

**Note:** _If the daemon and/or the web app fails to start you can attempt to start them separately using the scripts found under the **start/** directory._


Using Malspider
===================
Interaction with Malspider happens via an easy-to-use dashboard accessible through your web browser. The dashboard enables you to view alerts, inspect injected code, add websites to monitor, and tune false positives. 

### Monitoring Websites
----
Add websites to crawl by navigating to the administrative panel @ http://0.0.0.0:8080/admin (or by clicking on the admin link from the dashboard). Click on **"Organizations"** and a new Organization.  You'll be prompted for the:

 - website name (ie. "Cisco Systems")
 - domain (ie. cisco.com)
 - industry/org category (ie. Energy, Political, Education, etc)

If you want to **bulk import** domains, create a csv file with a the following header and leave the first column blank (the id field):

id,org_name,category,domain<br />
,Cisco Systems,Technology,cisco.com

Click "IMPORT" instead of "ADD ORGANIZATION".

**NOTE**: _Websites are scheduled to be **crawled once every 24 hours** (at midnight) by a cronjob. If you want to crawl your list of websites more often than that you can **edit the crontab entry** that looks like this: "0 * * * * python your_path/manage.py manage_spiders"_

### Pages Per Domain
By default, Malspider crawls 20 pages per domain. This can be changed. You can crawl as many pages as you like (per domain) or you can crawl only the homepage of each site.

In the **malspider/settings.py** file you'll find a "PAGES_PER_DOMAIN" variable. Change this to your desired depth.

```python
### Limit pages crawled per domain ###
# 0 = crawl only the home page (start urls)
# X = crawl X pages beyond the home page
PAGES_PER_DOMAIN = 20
}
```

### Tuning False Positives
----
Login to the web app administrative panel @ http://0.0.0.0:8080/admin or click on the admin link from the dashboard.

Click on "Custom Whitelist" and add your entry there. This can be a full URL or a partial string. The analyzer won't generate any (new) alerts for elements that match patterns in the whitelist.

**NOTE**: _You will need to **delete** the old alerts that are false positives. You can do this again through the admin interface by selecting "Alerts" and deleting the entries you don't want._


### Anonymous Traffic
----
We recommend you tunnel all Malspider traffic through a proxy to hide the origin of your requests. Malspider supports a single proxy:

In **malspider/settings.py** change:

```python  
WEBDRIVER_OPTIONS = {
                'service_args': ['--debug=true', '--load-images=true', '--webdriver-loglevel=debug']
#                'service_args': ['--debug=true', '--load-images=true', '--webdriver-loglevel=debug', '--proxy=<address>','--proxy-type=<http,socks5,etc>']
    
}
```

to 
```python
WEBDRIVER_OPTIONS = {
#                'service_args': ['--debug=true', '--load-images=true', '--webdriver-loglevel=debug']
                 'service_args': ['--debug=true', '--load-images=true', '--webdriver-loglevel=debug', '--proxy=<address>','--proxy-type=<http,socks5,etc>']
    
}
```
and replace **address** with your proxy address and **proxy_type** with the type of proxy (**http, socks5**).


**TIP**: A more advanced (and preferred) setup is to load balance multiple proxies. Some services will do this for you. 

### Random User Agent Strings
----
Malspider randomly selects a user agent string from a list found at **malspider/resources/useragents.txt**. If you would like to add more user agents to the list then simply edit that text file.

**NOTE**: _After editing the text file you'll need to re-deploy the project to the daemon. You can do that by navigating to the root project directory and typing "**scrapyd-deploy**". This should successfully deploy the changes._

### Enable Screenshots
Malspider has built-in capabilities for taking screenshots of every page it crawls. Screenshots can be useful in a variety of situations, but this can cause a drastic increase in server space utilization. For that reason, screenshots are turned off by default. If you want to take screenshots then open *malspider/settings.py* and locate the following lines of code: 

```python
#screenshots
TAKE_SCREENSHOT = False
SCREENSHOT_LOCATION = '<full_file_path>'
```
Set TAKE_SCREENSHOT to _True_ and change _full_file_path_ to where you want the screenshots to be stored.


### Email Summary of Alerts
----
Turn on email summaries by opening the malspider_django/malspider_django/settings.py file, locating the email options (near the bottom of the file), uncommenting them (removing the preceding #) and supplying the appropriate values:

```
EMAIL_HOST=""
EMAIL_PORT=
```

To create an email summary, Admin Panel -> Email Alerts -> Add Email Alert. Supply a subject line "ie. Malspider Email Summary", a list of recipients (separated by newline), and the email frequency (hourly, daily, weekly).

### LDAP Authentication (disabled by default)
----
If enabled, Malspider will present the user with a login screen requiring auth credentials to view content. To configure LDAP, open <root>/malspider_django/malspider_django/settings.py and uncomment (remove the '#') the two lines in AUTHENTICATION_BACKENDS. 

```
AUTHENTICATION_BACKENDS = (
#    'django_auth_ldap.backend.LDAPBackend',
#    'django.contrib.auth.backends.ModelBackend',
)
```

Then edit the LDAP variables according to your environment. Here are some you should consider editing:

```
AUTH_LDAP_SERVER_URI = "ldap://example.com"

AUTH_LDAP_BIND_DN = "cn=cnexample,OU=groups,OU=groups,DC=example,DC=com"
AUTH_LDAP_BIND_PASSWORD = "<password>"
AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=group,dc=example,dc=com",
    ldap.SCOPE_SUBTREE, "(cn=%(user)s)")

# Set up the basic group parameters.
AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=groups,dc=example,dc=com",
    ldap.SCOPE_SUBTREE, "(objectClass=groupOfNames)"
)

AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(name_attr="cn")

# Simple group restrictions
#AUTH_LDAP_REQUIRE_GROUP = "cn=example2,ou=django,ou=groups,dc=example,dc=com"
#AUTH_LDAP_DENY_GROUP = "cn=disabled,ou=django,ou=groups,dc=example,dc=com"
``` 

NOTE: For a more professional, production grade install, we recommend you setup Malspider with apache or nginx and use SSL.

### Database Purging
----
The database can grow rather large very quickly. It is recommended that, for performance reasons, you delete data from the 'pages' table and the 'elements' table once per month... unless you have the storage space, of course. 

If you want to perform a monthly purge of the database then uncomment the following line in your crontab file:  0 0 1 * * python your_path/manage.py purge_db



