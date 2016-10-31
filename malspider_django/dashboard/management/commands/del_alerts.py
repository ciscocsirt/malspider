#  
#  Copyright (c) 2016-present, Cisco Systems, Inc. All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree. 
#

from django.core.management.base import BaseCommand, CommandError
from dashboard.models import Alert

from django.db.models import Q

class Command(BaseCommand):
    help = 'Removes ALL alerts.'

    def handle(self, *args, **options):
        Alert.objects.all().delete()
