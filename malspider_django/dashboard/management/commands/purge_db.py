#  
#  Copyright (c) 2016-present, Cisco Systems, Inc. All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree. 
#

from django.core.management.base import BaseCommand, CommandError
from dashboard.models import Page
from dashboard.models import Element

from django.db.models import Q

class Command(BaseCommand):
    help = 'Removes all records from the following tables:  page, element. NOTE: alerts are NOT removed.'

    def handle(self, *args, **options):
        Page.objects.all().delete()
        Element.objects.all().delete()
