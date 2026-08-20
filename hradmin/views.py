from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import Inventory_group, Inventory_list
from user.models import UserProfile
from main.models import Region, County
from mediumv.models import Mvinspection, Mvmaitenance
from mediumv.models import Mv_poledefects
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from .forms import InventoryGroupForm, InventoryListForm
from django.http import HttpResponse
from django_pandas.io import read_frame
from django.db.models import F, Q, Count, Sum
from django.db.models.functions import Coalesce
from itertools import chain
from django_pandas.io import read_frame
import numpy as np
from django.db import transaction
import plotly
import plotly.express as px
import plotly.graph_objects as go
import json
import pandas as pd
import datetime
from django.utils import formats
from datetime import timedelta, time, date, datetime
import csv
from django.utils import timezone

# Create your views here.
@login_required(login_url="login")
def inventory_new(request):
    campaign = request.user.userprofile.campaign
    if campaign == "hradmin" or campaign=="superadmin":
        if request.method == 'POST':
            form = InventoryListForm(request.POST)
            if form.is_valid():
                regis = form.save(commit=False)
                regis.tagid = form.cleaned_data['tagid']
                regis.inv_name = form.cleaned_data['inv_name']
                regis.inv_group = form.cleaned_data['inv_group']
                regis.county = form.cleaned_data['county']
                regis.office_station = form.cleaned_data['office_station']
                regis.condition = form.cleaned_data['condition']
                regis.dt_purchase = form.cleaned_data['dt_purchase']
                regis.purchase_price_vat_incl = form.cleaned_data['purchase_price_vat_incl']
                regis.purchase_price_vat_excl = form.cleaned_data['purchase_price_vat_excl']
                regis.reciepient_stid = form.cleaned_data['reciepient_stid']
                regis.description = form.cleaned_data['description']
                regis.department = form.cleaned_data['department']
                regis.quantity = form.cleaned_data['quantity']
                regis.supplier = form.cleaned_data['supplier']
                regis.lpo_number = form.cleaned_data['lpo_number']
                regis.ac_number = form.cleaned_data['ac_number']
                regis.internal_order = form.cleaned_data['internal_order']
                regis.minute_no = form.cleaned_data['minute_no']
                regis.inspector = request.user.userprofile

                regis.save()
                messages.success(request, 'The Inventory was saved successfully.')
                return redirect('hradmin:inventory-list')
            else:
                print('invalid form')
                print(form.errors)
        else:
            form = InventoryListForm()

    else:
        messages.error(request, "You are not configured. Kindly contact the System Admin.")
        return redirect("main:my-dashboard")

    context = {
        'form': form,
    }
    return render(request, 'hradmin/inventory_new.html', context)

@login_required(login_url="login")
def inventory_list(request):
    inventory_list = Inventory_list.objects.all()
    paginator = Paginator(inventory_list, 20)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)

    context = {
        "inventory_list": paged_uploads,
    }
    return render(request, "hradmin/inventory_list.html", context)

@login_required(login_url="login")
def inventory_group_edit(request,pk=None):
    campaign = request.user.userprofile.campaign
    invgroup = get_object_or_404(Inventory_group, pk=pk)

    if campaign == "hradmin" or campaign == "superadmin":
        if request.method == 'POST':
            form = InventoryGroupForm(request.POST, instance=invgroup)

            if form.is_valid():
                regis = form.save(commit=False)
                regis.name = form.cleaned_data['name']
                regis.description = form.cleaned_data['description']
                regis.save()
                messages.success(request, 'The Inventory Group has been Updated successfully.')
                return redirect('hradmin:inventory-groups-list')
            else:
                print('invalid form')
                print(form.errors)
        else:
            form = InventoryGroupForm(instance=invgroup)
    else:
        messages.error(request, 'You have not been configured. Contact System Admin.')
        return redirect('hradmin:inventory-groups-list')

    context = {
        'form': form,
         'invgroup' :invgroup

    }
    return render(request, 'hradmin/inventory_group_edit.html', context)

@login_required(login_url="login")
def inventory_group_new(request):
    campaign = request.user.userprofile.campaign
    if campaign == "hradmin" or campaign=="superadmin":
        if request.method == 'POST':
            form = InventoryGroupForm(request.POST)
            if form.is_valid():
                regis = form.save(commit=False)
                regis.name = form.cleaned_data['name']
                regis.description = form.cleaned_data['description']

                regis.save()
                messages.success(request, 'The Inventory Group was saved successfully.')
                return redirect('hradmin:inventory-groups-list')
            else:
                print('invalid form')
                print(form.errors)
        else:
            form = InventoryGroupForm()

    else:
        messages.error(request, "You are not configured. Kindly contact the System Admin.")
        return redirect("main:my-dashboard")

    context = {
        'form': form,
    }
    return render(request, 'hradmin/inventory_group_new.html', context)

@login_required(login_url="login")
def inventory_groups_list(request, pk=None):
    inventory_group = Inventory_group.objects.all()
    paginator = Paginator(inventory_group, 20)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)

    context = {
        "inventory_group": paged_uploads,
    }
    return render(request, "hradmin/inventory_groups.html", context)
