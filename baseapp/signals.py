from django.db import transaction
from django.db.models import F
from django.utils.timezone import now

from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from decimal import Decimal

