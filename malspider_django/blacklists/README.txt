If you enable blacklist usage in malspider_django/settings.py any file in this directory
ending with .blacklist will be read and applied whenever the scraping results are analyzed.

The name of the file will be used as a hint in the alert (i.e. myblacklist.blacklist will result in an alert named
"BLACKLIST myblacklist".)

Each .blacklist file should contain one IP or domain name per line.