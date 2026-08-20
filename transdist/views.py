from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import (
    Transdist_insp,
    Transdist_subsations,
    Feeder_inspection,
    Power_tx_inspection,
    Aux_tx_inspection,
    Feeder_inspection_outgoing,
    Sixtysix_kv_customer,
    Sixtysix_kv_substation,
    Sixtysix_kv_meter,
    Sixtysix_kv_sealing,
    Sixtysix_kv_testeqipment,
    Sixtysix_kv_current,
Sixtysix_kv_ctvt_redphase,
Sixtysix_kv_ctvt_yellowphase,
Sixtysix_kv_ctvt_bluephase,
Sixtysix_kv_meter_readings,
Sixtysix_kv_otherinfo
)
from user.models import UserProfile
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from .forms import (
    TransdistForm,
    Feeder_inspectionForm,
    Power_tx_inspectionForm,
    Aux_tx_inspectionForm,
    Feeder_inspection_outgoingForm,
    SixtysixTargetForm,
    Sixtysix_kv_inspectionForm,
    Sixtysix_kv_meteringForm,
    Sixtysix_kv_sealingForm,
    Sixtysix_kv_testequipmentForm,
    Sixtysix_kv_currentForm,
Sixtysix_kv_ctvt_redForm,
Sixtysix_kv_ctvt_yellowForm,
Sixtysix_kv_ctvt_blueForm,
Sixtysix_kv_meterreadingsForm,
Sixtysix_otherinfoForm,
SixtysixSubmitForm,

)
from django_pandas.io import read_frame
from django.db.models import F, Q, Count
from django.db.models.functions import Coalesce
from itertools import chain
from django_pandas.io import read_frame
import plotly
import plotly.express as px
import plotly.graph_objects as go
import json
import pandas as pd
import datetime
from datetime import timedelta, date

@login_required(login_url="login")
def sixtysix_print(request, pk=None):
    inspection = Sixtysix_kv_substation.objects.select_related('sixtysix_meter','sixtysix_sealing','sixtysix_testeqp').get(customer_id=pk)
    customer = Sixtysix_kv_customer.objects.get(id=pk)
    context ={
        'customer' : customer,
        'inspection' : inspection
    }

    return render(request, 'sistysix/inspection_print.html', context)

@login_required(login_url="login")
def sixtysix_delete(request, pk):
    inspection  = Sixtysix_kv_substation.objects.get(customer_id=pk)
    customer = Sixtysix_kv_customer.objects.get(id=pk)

    if request.user.userprofile != inspection.inspectedby:
        messages.error(request, 'The Inspection can only be deleted by the person who created')
        return redirect('transdist:sixtysix-customers')

    if request.method =='POST':
        with transaction.atomic():
            inspection.delete()
            customer.status = False
            customer.type =0
            customer.save()
        messages.success(request, 'The Inspection was deleted successfully')
        return redirect('transdist:sixtysix-customers')
    context = {'object' : customer}
    return render(request, 'transdist/transdist_delete_confirmation.html', context)

@login_required(login_url="login")
def sixtysix_update_finalsubmission(request, pk=None):
    customer = Sixtysix_kv_customer.objects.get(id=pk)
    inspection = Sixtysix_kv_substation.objects.get(customer_id=pk)

    if request.user.userprofile != inspection.inspectedby:
        messages.error(request, 'The Inspection can only be submitted by the person who created')
        return redirect('transdist:sixtysix-customers')

    campaign = request.user.userprofile.campaign
    if campaign == "transdist" or campaign == 'lp':
        if request.method == "POST":
            inspection.save_status =True
            customer.status = True
            customer.type= 2
            inspection.save()
            customer.save()
            messages.success(
                request, "The Final Inspection Data has been submitted successfully"
            )
            return redirect("transdist:sixtysix-customers")

        else:
            m_form = SixtysixSubmitForm(instance=customer)
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:my-dashboard")
@login_required(login_url="login")
def sixtysix_update_otherinfo(request, pk=None):
    cust = Sixtysix_kv_substation.objects.get(customer_id=pk)
    customer = Sixtysix_kv_otherinfo.objects.get(customer=cust)

    campaign = request.user.userprofile.campaign
    m_form = Sixtysix_otherinfoForm(request.POST, request.FILES,instance=customer)
    if campaign == "transdist" or campaign == 'lp':
        if request.method == "POST":
            if m_form.is_valid():
                zerov = m_form.save(commit=False)
                zerov.customer = customer.customer
                zerov.aux_supp_meter = m_form.cleaned_data["aux_supp_meter"]
                zerov.aux_supp_meterno = m_form.cleaned_data["aux_supp_meterno"]
                zerov.certificates = m_form.cleaned_data["certificates"]
                zerov.team_members = m_form.cleaned_data["team_members"]
                zerov.overall_rem = m_form.cleaned_data["overall_rem"]
                zerov.declaration = m_form.cleaned_data["declaration"]
                zerov.inspectedby = request.user.userprofile
                zerov.save()
                messages.success(
                    request, "The Other Information Data saved successfully saved."
                )
                return redirect("transdist:sixtysix-update" ,pk)

            else:
                messages.error(
                    request, "There was an error in submitting your inspection."
                )
                print("invalid form")
                print(m_form.errors)

        else:
            m_form = Sixtysix_otherinfoForm(instance=customer)
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:my-dashboard")

@login_required(login_url="login")
def sixtysix_update_meter_readings(request, pk=None):
    cust = Sixtysix_kv_substation.objects.get(customer_id=pk)
    customer = Sixtysix_kv_meter_readings.objects.get(customer=cust)

    campaign = request.user.userprofile.campaign
    m_form = Sixtysix_kv_meterreadingsForm(request.POST, request.FILES,instance=customer)
    if campaign == "transdist" or campaign == 'lp':
        if request.method == "POST":
            if m_form.is_valid():
                zerov = m_form.save(commit=False)
                zerov.customer = customer.customer
                zerov.meter_time_curr = m_form.cleaned_data["meter_time_curr"]
                zerov.meter_time_mem = m_form.cleaned_data["meter_time_mem"]
                zerov.meter_date_cur = m_form.cleaned_data["meter_date_cur"]
                zerov.meter_date_mem = m_form.cleaned_data["meter_date_mem"]
                zerov.imp_180_cur = m_form.cleaned_data["imp_180_cur"]
                zerov.imp_180_mem = m_form.cleaned_data["imp_180_mem"]
                zerov.reading_180_img = m_form.cleaned_data["reading_180_img"]
                zerov.exp_280_cur = m_form.cleaned_data["exp_280_cur"]
                zerov.exp_280_mem = m_form.cleaned_data["exp_280_mem"]
                zerov.reading_280_img = m_form.cleaned_data["reading_280_img"]
                zerov.kva_960_cur = m_form.cleaned_data["kva_960_cur"]
                zerov.kva_960_mem = m_form.cleaned_data["kva_960_mem"]
                zerov.kw_150_cur = m_form.cleaned_data["kw_150_cur"]
                zerov.kw_150_mem = m_form.cleaned_data["kw_150_mem"]
                zerov.r_phase_v = m_form.cleaned_data["r_phase_v"]
                zerov.y_phase_v = m_form.cleaned_data["y_phase_v"]
                zerov.b_phase_v = m_form.cleaned_data["b_phase_v"]
                zerov.r_phase_c = m_form.cleaned_data["r_phase_c"]
                zerov.y_phase_c = m_form.cleaned_data["y_phase_c"]
                zerov.b_phase_c = m_form.cleaned_data["b_phase_c"]
                zerov.pw_f = m_form.cleaned_data["pw_f"]
                zerov.ct_vt_match = m_form.cleaned_data["ct_vt_match"]
                zerov.m_remarks = m_form.cleaned_data["m_remarks"]
                zerov.inspectedby = request.user.userprofile
                zerov.save()
                messages.success(
                    request, "The Meter Readings Data saved successfully saved."
                )
                return redirect("transdist:sixtysix-update" ,pk)

            else:
                messages.error(
                    request, "There was an error in submitting your inspection."
                )
                print("invalid form")
                print(m_form.errors)

        else:
            m_form = Sixtysix_kv_meterreadingsForm(instance=customer)
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:my-dashboard")

@login_required(login_url="login")
def sixtysix_update_ctvt_bluephase(request, pk=None):
    cust = Sixtysix_kv_substation.objects.get(customer_id=pk)
    customer = Sixtysix_kv_ctvt_bluephase.objects.get(customer=cust)

    campaign = request.user.userprofile.campaign
    m_form = Sixtysix_kv_ctvt_blueForm(request.POST, request.FILES,instance=customer)
    if campaign == "transdist" or campaign == 'lp':
        if request.method == "POST":
            if m_form.is_valid():
                zerov = m_form.save(commit=False)
                zerov.customer = customer.customer
                zerov.sn_ct = m_form.cleaned_data["sn_ct"]
                zerov.sn_vt = m_form.cleaned_data["sn_vt"]
                zerov.man_ct = m_form.cleaned_data["man_ct"]
                zerov.man_vt = m_form.cleaned_data["man_vt"]
                zerov.yom_ct = m_form.cleaned_data["yom_ct"]
                zerov.yom_vt = m_form.cleaned_data["yom_vt"]
                zerov.rated_v_ct = m_form.cleaned_data["rated_v_ct"]
                zerov.rated_v_vt = m_form.cleaned_data["rated_v_vt"]
                zerov.cores_ct = m_form.cleaned_data["cores_ct"]
                zerov.cores_vt = m_form.cleaned_data["cores_vt"]
                zerov.con_core_ct = m_form.cleaned_data["con_core_ct"]
                zerov.con_core_vt = m_form.cleaned_data["con_core_vt"]
                zerov.meter_core_ct = m_form.cleaned_data["meter_core_ct"]
                zerov.meter_core_vt = m_form.cleaned_data["meter_core_vt"]
                zerov.nameplate_ratio_ct = m_form.cleaned_data["nameplate_ratio_ct"]
                zerov.nameplate_ratio_vt = m_form.cleaned_data["nameplate_ratio_vt"]
                zerov.acc_meter_core_ct = m_form.cleaned_data["acc_meter_core_ct"]
                zerov.acc_meter_core_vt = m_form.cleaned_data["acc_meter_core_vt"]
                zerov.test_eqp_ct = m_form.cleaned_data["test_eqp_ct"]
                zerov.test_eqp_vt = m_form.cleaned_data["test_eqp_vt"]
                zerov.meas_trn_rt_ct = m_form.cleaned_data["meas_trn_rt_ct"]
                zerov.meas_trn_rt_vt = m_form.cleaned_data["meas_trn_rt_vt"]
                zerov.ration_dev_ct = m_form.cleaned_data["ration_dev_ct"]
                zerov.ration_dev_vt = m_form.cleaned_data["ration_dev_vt"]
                zerov.rem_ct = m_form.cleaned_data["rem_ct"]
                zerov.rem_vt = m_form.cleaned_data["rem_vt"]
                zerov.inspectedby = request.user.userprofile
                zerov.save()
                messages.success(
                    request, "The CT&VT Blue Phase Data saved successfully saved."
                )
                return redirect("transdist:sixtysix-update" ,pk)

            else:
                messages.error(
                    request, "There was an error in submitting your inspection."
                )
                print("invalid form")
                print(m_form.errors)

        else:
            m_form = Sixtysix_kv_ctvt_blueForm(instance=customer)
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:my-dashboard")
@login_required(login_url="login")
def sixtysix_update_ctvt_yellowphase(request, pk=None):
    cust = Sixtysix_kv_substation.objects.get(customer_id=pk)
    customer = Sixtysix_kv_ctvt_yellowphase.objects.get(customer=cust)

    campaign = request.user.userprofile.campaign
    m_form = Sixtysix_kv_ctvt_yellowForm(request.POST, request.FILES,instance=customer)
    if campaign == "transdist" or campaign == 'lp':
        if request.method == "POST":
            if m_form.is_valid():
                zerov = m_form.save(commit=False)
                zerov.customer = customer.customer
                zerov.sn_ct = m_form.cleaned_data["sn_ct"]
                zerov.sn_vt = m_form.cleaned_data["sn_vt"]
                zerov.man_ct = m_form.cleaned_data["man_ct"]
                zerov.man_vt = m_form.cleaned_data["man_vt"]
                zerov.yom_ct = m_form.cleaned_data["yom_ct"]
                zerov.yom_vt = m_form.cleaned_data["yom_vt"]
                zerov.rated_v_ct = m_form.cleaned_data["rated_v_ct"]
                zerov.rated_v_vt = m_form.cleaned_data["rated_v_vt"]
                zerov.cores_ct = m_form.cleaned_data["cores_ct"]
                zerov.cores_vt = m_form.cleaned_data["cores_vt"]
                zerov.con_core_ct = m_form.cleaned_data["con_core_ct"]
                zerov.con_core_vt = m_form.cleaned_data["con_core_vt"]
                zerov.meter_core_ct = m_form.cleaned_data["meter_core_ct"]
                zerov.meter_core_vt = m_form.cleaned_data["meter_core_vt"]
                zerov.nameplate_ratio_ct = m_form.cleaned_data["nameplate_ratio_ct"]
                zerov.nameplate_ratio_vt = m_form.cleaned_data["nameplate_ratio_vt"]
                zerov.acc_meter_core_ct = m_form.cleaned_data["acc_meter_core_ct"]
                zerov.acc_meter_core_vt = m_form.cleaned_data["acc_meter_core_vt"]
                zerov.test_eqp_ct = m_form.cleaned_data["test_eqp_ct"]
                zerov.test_eqp_vt = m_form.cleaned_data["test_eqp_vt"]
                zerov.meas_trn_rt_ct = m_form.cleaned_data["meas_trn_rt_ct"]
                zerov.meas_trn_rt_vt = m_form.cleaned_data["meas_trn_rt_vt"]
                zerov.ration_dev_ct = m_form.cleaned_data["ration_dev_ct"]
                zerov.ration_dev_vt = m_form.cleaned_data["ration_dev_vt"]
                zerov.rem_ct = m_form.cleaned_data["rem_ct"]
                zerov.rem_vt = m_form.cleaned_data["rem_vt"]
                zerov.inspectedby = request.user.userprofile
                zerov.save()
                messages.success(
                    request, "The CT&VT Yellow Phase Data saved successfully saved."
                )
                return redirect("transdist:sixtysix-update" ,pk)

            else:
                messages.error(
                    request, "There was an error in submitting your inspection."
                )
                print("invalid form")
                print(m_form.errors)

        else:
            m_form = Sixtysix_kv_ctvt_yellowForm(instance=customer)
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:my-dashboard")

@login_required(login_url="login")
def sixtysix_update_ctvt_redphase(request, pk=None):
    cust = Sixtysix_kv_substation.objects.get(customer_id=pk)
    customer = Sixtysix_kv_ctvt_redphase.objects.get(customer=cust)

    campaign = request.user.userprofile.campaign
    m_form = Sixtysix_kv_ctvt_redForm(request.POST, request.FILES,instance=customer)
    if campaign == "transdist" or campaign == 'lp':
        if request.method == "POST":
            if m_form.is_valid():
                zerov = m_form.save(commit=False)
                zerov.customer = customer.customer
                zerov.sn_ct = m_form.cleaned_data["sn_ct"]
                zerov.sn_vt = m_form.cleaned_data["sn_vt"]
                zerov.man_ct = m_form.cleaned_data["man_ct"]
                zerov.man_vt = m_form.cleaned_data["man_vt"]
                zerov.yom_ct = m_form.cleaned_data["yom_ct"]
                zerov.yom_vt = m_form.cleaned_data["yom_vt"]
                zerov.rated_v_ct = m_form.cleaned_data["rated_v_ct"]
                zerov.rated_v_vt = m_form.cleaned_data["rated_v_vt"]
                zerov.cores_ct = m_form.cleaned_data["cores_ct"]
                zerov.cores_vt = m_form.cleaned_data["cores_vt"]
                zerov.con_core_ct = m_form.cleaned_data["con_core_ct"]
                zerov.con_core_vt = m_form.cleaned_data["con_core_vt"]
                zerov.meter_core_ct = m_form.cleaned_data["meter_core_ct"]
                zerov.meter_core_vt = m_form.cleaned_data["meter_core_vt"]
                zerov.nameplate_ratio_ct = m_form.cleaned_data["nameplate_ratio_ct"]
                zerov.nameplate_ratio_vt = m_form.cleaned_data["nameplate_ratio_vt"]
                zerov.acc_meter_core_ct = m_form.cleaned_data["acc_meter_core_ct"]
                zerov.acc_meter_core_vt = m_form.cleaned_data["acc_meter_core_vt"]
                zerov.test_eqp_ct = m_form.cleaned_data["test_eqp_ct"]
                zerov.test_eqp_vt = m_form.cleaned_data["test_eqp_vt"]
                zerov.meas_trn_rt_ct = m_form.cleaned_data["meas_trn_rt_ct"]
                zerov.meas_trn_rt_vt = m_form.cleaned_data["meas_trn_rt_vt"]
                zerov.ration_dev_ct = m_form.cleaned_data["ration_dev_ct"]
                zerov.ration_dev_vt = m_form.cleaned_data["ration_dev_vt"]
                zerov.rem_ct = m_form.cleaned_data["rem_ct"]
                zerov.rem_vt = m_form.cleaned_data["rem_vt"]
                zerov.inspectedby = request.user.userprofile
                zerov.save()
                messages.success(
                    request, "The CT&VT Red Phase Data saved successfully saved."
                )
                return redirect("transdist:sixtysix-update" ,pk)

            else:
                messages.error(
                    request, "There was an error in submitting your inspection."
                )
                print("invalid form")
                print(m_form.errors)

        else:
            m_form = Sixtysix_kv_sealingForm(instance=customer)
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:my-dashboard")
@login_required(login_url="login")
def sixtysix_update_current(request, pk=None):
    cust = Sixtysix_kv_substation.objects.get(customer_id=pk)
    customer = Sixtysix_kv_current.objects.get(customer=cust)

    campaign = request.user.userprofile.campaign
    m_form = Sixtysix_kv_currentForm(request.POST, request.FILES,instance=customer)
    if campaign == "transdist" or campaign == 'lp':
        if request.method == "POST":
            if m_form.is_valid():
                zerov = m_form.save(commit=False)
                zerov.customer = customer.customer
                zerov.rphase_amcoder = m_form.cleaned_data["rphase_amcoder"]
                zerov.rphase_meter = m_form.cleaned_data["rphase_meter"]
                zerov.rphase_zera = m_form.cleaned_data["rphase_zera"]
                zerov.yphase_amcoder = m_form.cleaned_data["yphase_amcoder"]
                zerov.yphase_meter = m_form.cleaned_data["yphase_meter"]
                zerov.yphase_zera = m_form.cleaned_data["yphase_zera"]
                zerov.bphase_amcoder = m_form.cleaned_data["bphase_amcoder"]
                zerov.bphase_meter = m_form.cleaned_data["bphase_meter"]
                zerov.bphase_zera = m_form.cleaned_data["bphase_zera"]
                zerov.inspectedby = request.user.userprofile
                zerov.save()
                messages.success(
                    request, "The Current Verification Data saved successfully saved."
                )
                return redirect("transdist:sixtysix-update" ,pk)

            else:
                messages.error(
                    request, "There was an error in submitting your inspection."
                )
                print("invalid form")
                print(m_form.errors)

        else:
            m_form = Sixtysix_kv_sealingForm(instance=customer)
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:my-dashboard")

@login_required(login_url="login")
def sixtysix_update_testequipment(request, pk=None):
    cust = Sixtysix_kv_substation.objects.get(customer_id=pk)
    customer = Sixtysix_kv_testeqipment.objects.get(customer=cust)

    campaign = request.user.userprofile.campaign
    m_form = Sixtysix_kv_testequipmentForm(request.POST, request.FILES,instance=customer)
    if campaign == "transdist" or campaign == 'lp':
        if request.method == "POST":
            if m_form.is_valid():
                zerov = m_form.save(commit=False)
                zerov.customer = customer.customer
                zerov.zera_sn = m_form.cleaned_data["zera_sn"]
                zerov.ct_analyz_sn = m_form.cleaned_data["ct_analyz_sn"]
                zerov.vt_isa_sn = m_form.cleaned_data["vt_isa_sn"]
                zerov.amcoder_sn = m_form.cleaned_data["amcoder_sn"]
                zerov.error_t1 = m_form.cleaned_data["error_t1"]
                zerov.error_t2 = m_form.cleaned_data["error_t2"]
                zerov.error_t3 = m_form.cleaned_data["error_t3"]
                zerov.error_avg = m_form.cleaned_data["error_avg"]
                zerov.rem_error_test = m_form.cleaned_data["rem_error_test"]
                zerov.avg_per_err = m_form.cleaned_data["avg_per_err"]
                zerov.rem_reg_test = m_form.cleaned_data["rem_reg_test"]
                zerov.inspectedby = request.user.userprofile
                zerov.save()
                messages.success(
                    request, "The Equipment & Test Results saved successfully saved."
                )
                return redirect("transdist:sixtysix-update" ,pk)

            else:
                messages.error(
                    request, "There was an error in submitting your inspection."
                )
                print("invalid form")
                print(m_form.errors)

        else:
            m_form = Sixtysix_kv_sealingForm(instance=customer)
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:my-dashboard")

@login_required(login_url="login")
def sixtysix_update_sealing(request, pk=None):
    cust = Sixtysix_kv_substation.objects.get(customer_id=pk)
    customer = Sixtysix_kv_sealing.objects.get(customer=cust)

    campaign = request.user.userprofile.campaign
    m_form = Sixtysix_kv_sealingForm(request.POST, request.FILES,instance=customer)
    if campaign == "transdist" or campaign == 'lp':
        if request.method == "POST":
            if m_form.is_valid():
                zerov = m_form.save(commit=False)
                zerov.customer = customer.customer
                zerov.prg_seal_init = m_form.cleaned_data["prg_seal_init"]
                zerov.prg_seal_fin = m_form.cleaned_data["prg_seal_fin"]
                zerov.term_sl_init = m_form.cleaned_data["term_sl_init"]
                zerov.term_sl_fin = m_form.cleaned_data["term_sl_fin"]
                zerov.testb_sl_init = m_form.cleaned_data["testb_sl_init"]
                zerov.testb_sl_fin = m_form.cleaned_data["testb_sl_fin"]
                zerov.body_sl_init = m_form.cleaned_data["body_sl_init"]
                zerov.body_sl_fin = m_form.cleaned_data["body_sl_fin"]
                zerov.vten_r_sl_init = m_form.cleaned_data["vten_r_sl_init"]
                zerov.vten_r_sl_fin = m_form.cleaned_data["vten_r_sl_fin"]
                zerov.vten_y_sl_init = m_form.cleaned_data["vten_y_sl_init"]
                zerov.vten_y_sl_fin = m_form.cleaned_data["vten_y_sl_fin"]
                zerov.vten_b_sl_init = m_form.cleaned_data["vten_b_sl_init"]
                zerov.vten_b_sl_fin = m_form.cleaned_data["vten_b_sl_fin"]
                zerov.cten_r_sl_init = m_form.cleaned_data["cten_r_sl_init"]
                zerov.cten_r_sl_fin = m_form.cleaned_data["cten_r_sl_fin"]
                zerov.cten_y_sl_init = m_form.cleaned_data["cten_y_sl_init"]
                zerov.cten_y_sl_fin = m_form.cleaned_data["cten_y_sl_fin"]
                zerov.cten_b_sl_init = m_form.cleaned_data["cten_b_sl_init"]
                zerov.cten_b_sl_fin = m_form.cleaned_data["cten_b_sl_fin"]
                zerov.marsha_kiosk_init = m_form.cleaned_data["marsha_kiosk_init"]
                zerov.marsha_kiosk_fin = m_form.cleaned_data["marsha_kiosk_fin"]
                zerov.inspectedby = request.user.userprofile
                zerov.save()
                messages.success(
                    request, "The Seal Data Details saved successfully saved."
                )
                return redirect("transdist:sixtysix-update" ,pk)

            else:
                messages.error(
                    request, "There was an error in submitting your inspection."
                )
                print("invalid form")
                print(m_form.errors)

        else:
            m_form = Sixtysix_kv_sealingForm(instance=customer)
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:my-dashboard")
@login_required(login_url="login")
def sixtysix_update_meter(request, pk=None):
    cust = Sixtysix_kv_substation.objects.get(customer_id=pk)
    customer = Sixtysix_kv_meter.objects.get(customer=cust)

    campaign = request.user.userprofile.campaign
    m_form = Sixtysix_kv_meteringForm(request.POST, request.FILES,instance=customer)
    if campaign == "transdist" or campaign == 'lp':
        if request.method == "POST":
            if m_form.is_valid():
                zerov = m_form.save(commit=False)
                zerov.customer = customer.customer
                zerov.feeder_name = m_form.cleaned_data["feeder_name"]
                zerov.conn_config = m_form.cleaned_data["conn_config"]
                zerov.meter_number = m_form.cleaned_data["meter_number"]
                zerov.manufacturer = m_form.cleaned_data["manufacturer"]
                zerov.meter_model = m_form.cleaned_data["meter_model"]
                zerov.yom = m_form.cleaned_data["yom"]
                zerov.meter_accuracy_class = m_form.cleaned_data["meter_accuracy_class"]
                zerov.progrm_ctr = m_form.cleaned_data["progrm_ctr"]
                zerov.progrm_vtr = m_form.cleaned_data["progrm_vtr"]
                zerov.meter_config = m_form.cleaned_data["meter_config"]
                zerov.inspectedby = request.user.userprofile
                zerov.save()
                messages.success(
                    request, "The Customer Details saved successfully saved."
                )
                return redirect("transdist:sixtysix-update" ,pk)

            else:
                messages.error(
                    request, "There was an error in submitting your inspection."
                )
                print("invalid form")
                print(m_form.errors)

        else:
            m_form = Sixtysix_kv_meteringForm(instance=customer)
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:my-dashboard")

@login_required(login_url="login")
def sixtysix_update_substation(request, pk=None):
    customer = Sixtysix_kv_substation.objects.get(customer_id=pk)

    campaign = request.user.userprofile.campaign
    m_form = Sixtysix_kv_inspectionForm(request.POST, request.FILES, instance=customer)
    if campaign == "transdist" or campaign == 'lp':
        if request.method == "POST":
            if m_form.is_valid():
                zerov = m_form.save(commit=False)
                zerov.customer = customer.customer
                zerov.longitude = m_form.cleaned_data["longitude"]
                zerov.latitude = m_form.cleaned_data["latitude"]
                zerov.substation_name = m_form.cleaned_data["substation_name"]
                zerov.transform_voltage = m_form.cleaned_data["transform_voltage"]
                zerov.no_tx_ss = m_form.cleaned_data["no_tx_ss"]
                zerov.tx_rating = m_form.cleaned_data["tx_rating"]
                zerov.no_hv_lines = m_form.cleaned_data["no_hv_lines"]
                zerov.no_mv_lines = m_form.cleaned_data["no_mv_lines"]
                zerov.inspectedby = request.user.userprofile
                zerov.save()
                messages.success(
                    request, "The Meter Section saved successfully saved."
                )
                return redirect("transdist:sixtysix-update" ,pk)

            else:
                messages.error(
                    request, "There was an error in submitting your inspection."
                )
                print("invalid form")
                print(m_form.errors)

        else:
            m_form = Sixtysix_kv_inspectionForm(instance=customer)
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:my-dashboard")

    # m_form = Sixtysix_kv_inspectionForm()
    context ={
        'customer' :customer,
        'form' : m_form

    }
    return render(request, "sistysix/sixtysix_update.html", context)
@login_required(login_url="login")
def sixtysix_update(request, pk=None):
    customer = Sixtysix_kv_customer.objects.get(pk=pk)
    inspection = Sixtysix_kv_substation.objects.get(customer=customer)
    meter = Sixtysix_kv_meter.objects.get(customer=inspection)
    equipment = Sixtysix_kv_testeqipment.objects.get(customer=inspection)
    seals = Sixtysix_kv_sealing.objects.get(customer=inspection)
    current = Sixtysix_kv_current.objects.get(customer=inspection)
    ctvt_redphase = Sixtysix_kv_ctvt_redphase.objects.get(customer=inspection)
    ctvt_yellowphase = Sixtysix_kv_ctvt_yellowphase.objects.get(customer=inspection)
    ctvt_bluephase = Sixtysix_kv_ctvt_bluephase.objects.get(customer=inspection)
    meter_readings = Sixtysix_kv_meter_readings.objects.get(customer=inspection)
    other_info = Sixtysix_kv_otherinfo.objects.get(customer=inspection)

    m_form = Sixtysix_kv_inspectionForm(instance=inspection)
    m_form1 = Sixtysix_kv_meteringForm(instance=meter)
    m_form2 = Sixtysix_kv_sealingForm(instance=seals)
    m_form3 = Sixtysix_kv_testequipmentForm(instance=equipment)
    m_form4 = Sixtysix_kv_currentForm(instance=current)
    m_form5 = Sixtysix_kv_ctvt_redForm(instance=ctvt_redphase)
    m_form6 = Sixtysix_kv_ctvt_yellowForm(instance=ctvt_yellowphase)
    m_form7 = Sixtysix_kv_ctvt_blueForm(instance=ctvt_bluephase)
    m_form8 = Sixtysix_kv_meterreadingsForm(instance=meter_readings)
    m_form9 = Sixtysix_otherinfoForm(instance=other_info)

    context ={
        'customer' :customer,
        'form' : m_form,
        'form1': m_form1,
        'form2': m_form2,
        'form3': m_form3,
        'form4': m_form4,
        'form5': m_form5,
        'form6': m_form6,
        'form7': m_form7,
        'form8': m_form8,
        'form9': m_form9

    }
    return render(request, "sistysix/sixtysix_update.html", context)

@login_required(login_url="login")
def sixty_six_inspection(request, pk=None):
    sixtysix = get_object_or_404(Sixtysix_kv_customer, id=pk)
    with transaction.atomic():
        new_inspection = Sixtysix_kv_substation.objects.create(
            customer=sixtysix,
            inspectedby=request.user.userprofile,
            county = request.user.userprofile.county,
            region=request.user.userprofile.region
        )
        new_inspection.save()
        new_meter = Sixtysix_kv_meter.objects.create(
            customer=new_inspection,
            inspectedby=request.user.userprofile,
        )
        new_sealing = Sixtysix_kv_sealing.objects.create(
            customer=new_inspection,
            inspectedby=request.user.userprofile,
        )
        new_testequipment = Sixtysix_kv_testeqipment.objects.create(
            customer=new_inspection,
            inspectedby=request.user.userprofile,
        )
        new_current = Sixtysix_kv_current.objects.create(
            customer=new_inspection,
            inspectedby=request.user.userprofile,
        )
        new_ctvt_rephase = Sixtysix_kv_ctvt_redphase.objects.create(
            customer=new_inspection,
            inspectedby=request.user.userprofile,
        )
        new_ctvt_yellowhase = Sixtysix_kv_ctvt_yellowphase.objects.create(
            customer=new_inspection,
            inspectedby=request.user.userprofile,
        )
        new_ctvt_bluephase = Sixtysix_kv_ctvt_bluephase.objects.create(
            customer=new_inspection,
            inspectedby=request.user.userprofile,
        )
        new_meter_readings = Sixtysix_kv_meter_readings.objects.create(
            customer=new_inspection,
            inspectedby=request.user.userprofile,
        )
        new_otherinfo = Sixtysix_kv_otherinfo.objects.create(
            customer=new_inspection,
            inspectedby=request.user.userprofile,
        )
        sixtysix.type = 1
        sixtysix.save()
        new_sealing.save()
        new_testequipment.save()
        new_current.save()
        new_ctvt_rephase.save()
        new_ctvt_yellowhase.save()
        new_ctvt_bluephase.save()
        new_meter_readings.save()
        new_otherinfo.save()

    if new_inspection and new_meter:
        messages.success(
            request,
            "A Draft of the New Inspection was saved successfully. Open to continue with the inspection",
        )
        return redirect("transdist:sixtysix-customers")

    context = {
        "inspection_id": new_inspection.id,
    }
    return render(request, "sistysix/sistysix_customers.html", context)

@login_required(login_url="login")
def sixty_six_not_in_target(request):
    campaign = request.user.userprofile.campaign
    if campaign == "transdist" or campaign == 'lp':
        if request.method == "POST":
            # user_form = UserForm(request.POST, instance=request.user)
            m_form = SixtysixTargetForm(request.POST, request.FILES)

            check = Sixtysix_kv_customer.objects.filter(meter_number=request.POST["meter_number"])
            if check:
                messages.error(request, "The Meter is already in the list.")
                return redirect("transdist:sixtysix-customers")

            if m_form.is_valid():
                # if m_form.cleaned_data['meterno'] is None:
                # messages.success(request, 'You need to take the Cordinates.')
                # return redirect('postpaid:mythreephase-list')
                #
                resolution = Sixtysix_kv_customer()
                resolution.meter_number = m_form.cleaned_data["meter_number"]
                resolution.account_number = m_form.cleaned_data["account_number"]
                resolution.new_account_number = m_form.cleaned_data["new_account_number"]
                resolution.name = m_form.cleaned_data["name"]
                resolution.user = request.user.userprofile
                resolution.county = request.user.userprofile.county
                resolution.region = request.user.userprofile.region
                resolution.save()
                messages.success(
                    request, "Account Saved Successfully."
                )
                return redirect("transdist:sixtysix-customers")

            else:
                messages.error(
                    request, "There was an error in submitting your inspection."
                )
                print("invalid form")
                print(m_form.errors)

        else:
            # user_form = UserForm(instance=request.user)

            m_form = SixtysixTargetForm()
        context = {
            "form": m_form,
        }
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:my-dashboard")

    return render(request, "sistysix/sistysix_customers.html", context)
@login_required(login_url="login")
def sistysix_search_by_meter(request):
    if request.user.is_authenticated:
        campaign = request.user.userprofile.campaign
        if campaign == "transdist" or campaign == 'lp':
            stations = Sixtysix_kv_customer.objects.select_related("region")

    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = stations.filter(meter_number__icontains=keyword)
    m_form = SixtysixTargetForm()
    context = {
        "meters": paged_uploads,
        'form' : m_form,
    }
    return render(request, "sistysix/sistysix_customers.html", context)
@login_required(login_url="login")
def sixtysix_customers(request):
    if request.user.is_authenticated:
        campaign = request.user.userprofile.campaign
    if campaign == "transdist" or campaign == 'lp':
        stations = Sixtysix_kv_customer.objects.select_related("county").values('type','new_account_number','id','account_number','county__name','name','meter_number')
        paginator = Paginator(stations, 10)
        page = request.GET.get("page")
        paged_uploads = paginator.get_page(page)
    else:
        messages.error(request, "Access denied.")
        return redirect("main:my-dashboard")

    context = {"meters": paged_uploads}
    return render(request, "sistysix/sistysix_customers.html", context)

@login_required(login_url="login")
def search_by_ssn_inspected(request):
    if request.user.is_authenticated:
        inspections = Transdist_insp.objects.select_related('transdist').filter(save_status=True).annotate(
            incomers=Count('transdist_inspection', distinct=True),
            outgoing=Count('transdist_inspection_outgoing', distinct=True),
            powertx=Count('transdist_inspection_powertx', distinct=True),
            auxtx=Count('transdist_inspection_auxtx', distinct=True),
        ).order_by(
            "-dtadd"
        )

    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = inspections.filter(transdist__name__icontains=keyword)
    context = {
        "data": paged_uploads,
    }
    return render(request, "transdist/transdist_inspections.html", context)

@login_required(login_url="login")
def auxtx_delete(request, pk):
    feederinspection = Aux_tx_inspection.objects.get(id=pk)

    if request.method == "POST":

        feederinspection.delete()
        messages.success(request, "The Outgoing Feeder Record was deleted successfully")
        return redirect("transdist:transdist-update", feederinspection.transdist_id)
    context = {"object": feederinspection.ssn}
    return render(request, "transdist/transdist_delete_confirmation.html", context)
    
@login_required(login_url="login")
def outgoing_delete(request, pk):
    feederinspection = Feeder_inspection_outgoing.objects.get(id=pk)

    if request.method == "POST":

        feederinspection.delete()
        messages.success(request, "The Outgoing Feeder Record was deleted successfully")
        return redirect("transdist:transdist-update", feederinspection.transdist_id)
    context = {"object": feederinspection.feeder_source}
    return render(request, "transdist/transdist_delete_confirmation.html", context)
    
@login_required(login_url="login")
def powertx_delete(request, pk):
    feederinspection = Power_tx_inspection.objects.get(id=pk)

    if request.method == "POST":

        feederinspection.delete()
        messages.success(request, "The PowerTX Record was deleted successfully")
        return redirect("transdist:transdist-update", feederinspection.transdist_id)
    context = {"object": feederinspection.powername}
    return render(request, "transdist/transdist_delete_confirmation.html", context)
    
@login_required(login_url="login")
def incomer_delete(request, pk):
    feederinspection = Feeder_inspection.objects.get(id=pk)

    if request.method == "POST":

        feederinspection.delete()
        messages.success(request, "The Incomer Record was deleted successfully")
        return redirect("transdist:transdist-update", feederinspection.transdist_id)
    context = {"object": feederinspection.feeder_source}
    return render(request, "transdist/transdist_delete_confirmation.html", context)


@login_required(login_url="login")
def transdist_delete(request, pk):
    lv = Transdist_insp.objects.get(id=pk)
    feederinspection = Feeder_inspection.objects.filter(transdist=lv)
    powertxinspections = Power_tx_inspection.objects.filter(transdist=lv)
    auxinspections = Aux_tx_inspection.objects.filter(transdist=lv)
    feeder_outgoing = Feeder_inspection_outgoing.objects.filter(transdist=lv)
    if request.method == "POST":
        lv.delete()
        feederinspection.delete()
        powertxinspections.delete()
        auxinspections.delete()
        feeder_outgoing.delete()
        messages.success(request, "The Substation Inspection was deleted successfully")
        return redirect("transdist:inspections-my")
    context = {"object": lv.id}
    return render(request, "transdist/transdist_delete_confirmation.html", context)


@login_required(login_url="login")
def transdist_dashboard(request):
    oveall_target = Transdist_subsations.objects.all()
    oveall_inspected = Transdist_insp.objects.values("id", "transdist", "dtadd").filter(save_status=True)

    def target_achievement():
        t_a = oveall_inspected.count()
        fig = go.Figure(
            data=[
                go.Bar(
                    name="Target",
                    x=["Target"],
                    y=[oveall_target.count()],
                ),
                go.Bar(name="Achieved ToDate", x=["Achieved ToDate"], y=[t_a]),
            ]
        )

        fig.update_layout(barmode="group")
        fig.update_layout(title_text="Overall Target vs Achievement")
        fig.update_traces(
            texttemplate="%{y}<br>",  # use '%{text}' to show only percentage
            textposition="outside",
        )
        fig.update_layout(
            title="Target vs Achievement",
            xaxis_tickfont_size=14,
            yaxis=dict(
                title="No Of Inspections",
                titlefont_size=16,
                tickfont_size=14,
            ),
            xaxis=dict(
                title="Year(2023/24)",
            ),
            legend=dict(
                bgcolor="rgba(255, 255, 255, 0)", bordercolor="rgba(255, 255, 255, 0)"
            ),
            barmode="group",
            bargap=0.15,  # gap between bars of adjacent location coordinates.
            bargroupgap=0.1,  # gap between bars of the same location coordinate.
        )
        fig_plot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return fig_plot

    def daily_trend():
        df = read_frame(oveall_inspected)
        df["dtadd"] = pd.to_datetime(df["dtadd"]).dt.date
        df = df.groupby(by="dtadd", as_index=False, sort=False)["transdist"].count()
        df = px.bar(
            df,
            x=df.dtadd,
            y=df.transdist,
            title="Daily Overall Inspections.",
            text_auto=True,
            text=df.transdist,
            labels={"meterno": "Meter Count", "dtadd": "Date"},
        )
        df_daolytrend = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)

        return df_daolytrend

    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_1 = date.today() - timedelta(days=2)
    yesterday_2 = date.today() - timedelta(days=3)

    regional_analytics = (
        Transdist_subsations.objects.values("region__name")
        .annotate(
            trdis_target=(Count("id", distinct=True)),
            trdis_inspected=(Count("id", distinct=True, filter=Q(status=True))),
            trdis_inspected_pending=(Count("id", distinct=True, filter=Q(status=False))),
            trdis_today=Count("id", distinct=True, filter=Q(transdist_target__dtupdate__date=today)),
            trdis_yesturday=Count("id",distinct=True, filter=Q(transdist_target__dtupdate__date=yesterday)),
            trdis_yesturday_1=Count("id",distinct=True, filter=Q(transdist_target__dtupdate__date=yesterday_1)),
            incomers=Count('transdist_target__transdist_inspection', distinct=True,filter=Q(transdist_target__save_status=True)),
            incomer_unmetered = Count('id', distinct=True, filter=Q(transdist_target__transdist_inspection__feeder_metered='no',transdist_target__save_status=True)),
            powertx=Count('transdist_target__transdist_inspection_powertx', distinct=True,filter=Q(transdist_target__save_status=True)),
            powertx_unmetered = Count('id', distinct=True, filter=Q(transdist_target__transdist_inspection_powertx__ismetered='no',transdist_target__save_status=True)),
            outgoing=Count('transdist_target__transdist_inspection_outgoing', distinct=True,filter=Q(transdist_target__save_status=True)),
            outgoing_unmetered = Count('id',distinct=True, filter=Q(transdist_target__transdist_inspection_outgoing__feeder_metered='no', transdist_target__save_status=True))
            # lp_yesturday_1=Count('id', filter=Q(lp_target__dtadd__date=yesterday_1)),
        )
        .order_by("region__name")
    )

    context = {
        "target_achievement": target_achievement(),
        "daily_trend_plot": daily_trend(),
        'regional_analytics': regional_analytics,
        'yesterday': yesterday,
        'yesterday_1': yesterday_1
    }
    return render(request, "transdist/transdist_dashboard.html", context)


@login_required(login_url="login")
def inspection_detail(request, pk=None):
    inspection = get_object_or_404(Transdist_insp, id=pk)
    feederinspection = Feeder_inspection.objects.filter(transdist=inspection)
    powertxinspections = Power_tx_inspection.objects.filter(transdist=inspection)
    auxinspections = Aux_tx_inspection.objects.filter(transdist=inspection)
    feederinspection_outgoing = Feeder_inspection_outgoing.objects.filter(transdist=inspection)

    context = {
        "lvinspection": inspection,
        "feederinspection": feederinspection,
        "powertxinspections": powertxinspections,
        "auxinspections": auxinspections,
        'feederinspection_outgoing': feederinspection_outgoing
    }
    return render(request, "transdist/inspection_detail.html", context)


@login_required(login_url="login")
def transdist_inspections(request):
    inspections = Transdist_insp.objects.select_related('transdist').filter(save_status=True).annotate(
        incomers=Count('transdist_inspection', distinct=True),
        outgoing=Count('transdist_inspection_outgoing', distinct=True),
        powertx=Count('transdist_inspection_powertx', distinct=True),
        auxtx=Count('transdist_inspection_auxtx', distinct=True),
    ).order_by(
        "-dtadd"
    )

    paginator = Paginator(inspections, 20)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)

    context = {"data": paged_uploads}
    return render(request, "transdist/transdist_inspections.html", context)


@login_required(login_url="login")
def auxtxinspection_new(request, pk=None):
    transdist = Transdist_insp.objects.get(id=pk)
    auxtx_form = Aux_tx_inspectionForm()
    sub_form = TransdistForm()

    if request.method == "POST":
        pole_form = Aux_tx_inspectionForm(
            request.POST,
            request.FILES,
        )

        if pole_form.is_valid():
            poled = pole_form.save(commit=False)
            poled.ssn = pole_form.cleaned_data["ssn"]
            poled.metered = pole_form.cleaned_data["metered"]
            poled.mounting_strx = pole_form.cleaned_data["mounting_strx"]
            poled.meternumber = pole_form.cleaned_data["meternumber"]
            poled.meterbrand = pole_form.cleaned_data["meterbrand"]
            poled.metermodel = pole_form.cleaned_data["metermodel"]
            poled.metertype = pole_form.cleaned_data["metertype"]
            poled.reading_180 = pole_form.cleaned_data["reading_180"]
            poled.reading_280 = pole_form.cleaned_data["reading_280"]
            poled.reading_180_img = pole_form.cleaned_data["reading_180_img"]
            poled.remarks = pole_form.cleaned_data["remarks"]
            poled.recommendation = pole_form.cleaned_data["recommendation"]
            poled.transdist = transdist
            poled.inspector = request.user.userprofile
            poled.save()

            messages.success(request, "The Aux TX Inspection was saved successfully.")
            return redirect("transdist:transdist-update", transdist.id)
        else:
            print("invalid form")
            print(pole_form.errors)
            messages.error(request, "There was an error submitting.")
            # print(Lvinsp_form.errors)
    else:
        pole_form = Aux_tx_inspectionForm()
        # lv_form = LvinspectionForm(instance=new_inspection)

    context = {
        "substation": transdist,
        "pole_form": pole_form,
        "sub_form": sub_form,
        "auxtx_form": auxtx_form,
    }
    return render(request, "transdist/inspectin_new.html", context)


@login_required(login_url="login")
def powertxinspection_new(request, pk=None):
    transdist = Transdist_insp.objects.get(id=pk)
    powertx_form = Power_tx_inspectionForm()
    sub_form = TransdistForm()

    if request.method == "POST":
        pole_form = Power_tx_inspectionForm(
            request.POST,
            request.FILES,
        )

        if pole_form.is_valid():
            poled = pole_form.save(commit=False)
            poled.powername = pole_form.cleaned_data["powername"]
            poled.istherenameplate = pole_form.cleaned_data["istherenameplate"]
            poled.nameplateimg = pole_form.cleaned_data["nameplateimg"]
            poled.rated_mva = pole_form.cleaned_data["rated_mva"]
            poled.noloadloss = pole_form.cleaned_data["noloadloss"]
            poled.loadloss = pole_form.cleaned_data["loadloss"]
            poled.metering_vt_ratio = pole_form.cleaned_data["metering_vt_ratio"]
            poled.metering_vt_class = pole_form.cleaned_data["metering_vt_class"]
            poled.metering_core_burden_vt = pole_form.cleaned_data["metering_core_burden_vt"]
            poled.metering_core_ctratio = pole_form.cleaned_data["metering_core_ctratio"]
            poled.metering_core_class_ct = pole_form.cleaned_data["metering_core_class_ct"]
            poled.metering_core_burden_ct = pole_form.cleaned_data["metering_core_burden_ct"]
            poled.ismetered = pole_form.cleaned_data["ismetered"]
            poled.meternumber = pole_form.cleaned_data["meternumber"]
            poled.meterbrand = pole_form.cleaned_data["meterbrand"]
            poled.metermodel = pole_form.cleaned_data["meterbrand"]
            poled.metertype = pole_form.cleaned_data["metertype"]
            poled.classofmeter = pole_form.cleaned_data["classofmeter"]
            poled.ct_ratio = pole_form.cleaned_data["ct_ratio"]
            poled.vt_ratio = pole_form.cleaned_data["vt_ratio"]
            poled.vt_ration_linked_meter = pole_form.cleaned_data[
                "vt_ration_linked_meter"
            ]
            poled.ct_ration_linked_meter = pole_form.cleaned_data[
                "ct_ration_linked_meter"
            ]
            poled.dt_visit = pole_form.cleaned_data["dt_visit"]
            poled.tm_visit = pole_form.cleaned_data["tm_visit"]
            poled.dt_on_meter_during_visit = pole_form.cleaned_data[
                "dt_on_meter_during_visit"
            ]
            poled.tm_on_meter_during_visit = pole_form.cleaned_data[
                "tm_on_meter_during_visit"
            ]
            poled.reading_180 = pole_form.cleaned_data["reading_180"]
            poled.reading_1801 = pole_form.cleaned_data["reading_1801"]
            poled.reading_280 = pole_form.cleaned_data["reading_280"]
            poled.reading_2801 = pole_form.cleaned_data["reading_2801"]
            poled.powerfactor = pole_form.cleaned_data["powerfactor"]
            poled.vlt_redphase = pole_form.cleaned_data["vlt_redphase"]
            poled.vlt_yellowphase = pole_form.cleaned_data["vlt_yellowphase"]
            poled.vlt_bluephase = pole_form.cleaned_data["vlt_bluephase"]
            poled.crnt_redphase = pole_form.cleaned_data["crnt_redphase"]
            poled.crnt_yellowphase = pole_form.cleaned_data["crnt_yellowphase"]
            poled.crnt_bluephase = pole_form.cleaned_data["crnt_bluephase"]
            poled.remarks = pole_form.cleaned_data["remarks"]
            poled.recommendation = pole_form.cleaned_data["recommendation"]
            poled.reading_180_img = pole_form.cleaned_data["reading_180_img"]
            poled.transdist = transdist
            poled.inspector = request.user.userprofile
            poled.save()

            messages.success(request, "The Power TX Inspection was saved successfully.")
            return redirect("transdist:transdist-update", transdist.id)
        else:
            print("invalid form")
            print(pole_form.errors)
            messages.error(request, "There was an error submitting.")
            # print(Lvinsp_form.errors)
    else:
        pole_form = Power_tx_inspectionForm()
        # lv_form = LvinspectionForm(instance=new_inspection)

    context = {
        "substation": transdist,
        "pole_form": pole_form,
        "sub_form": sub_form,
        "powertx_form": powertx_form,
    }
    return render(request, "transdist/inspectin_new.html", context)


@login_required(login_url="login")
def feeder_outgoing_inspection_new(request, pk=None):
    transdist = Transdist_insp.objects.get(id=pk)
    feeder_form = Feeder_inspection_outgoingForm()
    sub_form = TransdistForm()

    if request.method == "POST":
        pole_form = Feeder_inspection_outgoingForm(
            request.POST,
            request.FILES,
        )

        if pole_form.is_valid():
            poled = pole_form.save(commit=False)
            poled.feeder_source = pole_form.cleaned_data["feeder_source"]
            poled.metering_vt_ratio = pole_form.cleaned_data["metering_vt_ratio"]
            poled.feeder_metered = pole_form.cleaned_data["feeder_metered"]
            poled.meternumber = pole_form.cleaned_data["meternumber"]
            poled.meterbrand = pole_form.cleaned_data["meterbrand"]
            poled.metermodel = pole_form.cleaned_data["meterbrand"]
            poled.metertype = pole_form.cleaned_data["metertype"]
            poled.classofmeter = pole_form.cleaned_data["classofmeter"]
            poled.ct_ratio = pole_form.cleaned_data["ct_ratio"]
            poled.vt_ratio = pole_form.cleaned_data["vt_ratio"]
            poled.metering_core_ctratio = pole_form.cleaned_data[
                "metering_core_ctratio"
            ]
            poled.metering_core_class_ct = pole_form.cleaned_data[
                "metering_core_class_ct"
            ]
            poled.metering_core_burden_va = pole_form.cleaned_data[
                "metering_core_burden_va"
            ]
            poled.vt_ration_linked_yard = pole_form.cleaned_data[
                "vt_ration_linked_yard"
            ]
            poled.ct_ration_linked_yard = pole_form.cleaned_data[
                "ct_ration_linked_yard"
            ]
            poled.class_vt = pole_form.cleaned_data["class_vt"]
            poled.vt_burden_va = pole_form.cleaned_data["vt_burden_va"]
            poled.dt_visit = pole_form.cleaned_data["dt_visit"]
            poled.tm_visit = pole_form.cleaned_data["tm_visit"]
            poled.dt_on_meter_during_visit = pole_form.cleaned_data[
                "dt_on_meter_during_visit"
            ]
            poled.tm_on_meter_during_visit = pole_form.cleaned_data[
                "tm_on_meter_during_visit"
            ]
            poled.reading_180 = pole_form.cleaned_data["reading_180"]
            poled.reading_1801 = pole_form.cleaned_data["reading_1801"]
            poled.reading_280 = pole_form.cleaned_data["reading_280"]
            poled.reading_2801 = pole_form.cleaned_data["reading_2801"]
            poled.powerfactor = pole_form.cleaned_data["powerfactor"]
            poled.vlt_redphase = pole_form.cleaned_data["vlt_redphase"]
            poled.vlt_yellowphase = pole_form.cleaned_data["vlt_yellowphase"]
            poled.vlt_bluephase = pole_form.cleaned_data["vlt_bluephase"]
            poled.crnt_redphase = pole_form.cleaned_data["crnt_redphase"]
            poled.crnt_yellowphase = pole_form.cleaned_data["crnt_yellowphase"]
            poled.crnt_bluephase = pole_form.cleaned_data["crnt_bluephase"]
            poled.remarks = pole_form.cleaned_data["remarks"]
            poled.recommendation = pole_form.cleaned_data["recommendation"]
            poled.reading_180_img = pole_form.cleaned_data["reading_180_img"]
            poled.transdist = transdist
            poled.inspector = request.user.userprofile
            poled.save()

            messages.success(request, "The Feeder Inspection was saved successfully.")
            return redirect("transdist:transdist-update", transdist.id)
        else:
            print("invalid form")
            print(pole_form.errors)
            messages.error(request, "There was an error submitting.")
            # print(Lvinsp_form.errors)
    else:
        pole_form = Feeder_inspection_outgoingForm()
        # lv_form = LvinspectionForm(instance=new_inspection)

    context = {
        "substation": transdist,
        "pole_form": pole_form,
        "sub_form": sub_form,
        "feeder_outgoing_form": feeder_form,
    }
    return render(request, "transdist/inspectin_new.html", context)


@login_required(login_url="login")
def feederinspection_new(request, pk=None):
    transdist = Transdist_insp.objects.get(id=pk)
    feeder_form = Feeder_inspectionForm()
    sub_form = TransdistForm()

    if request.method == "POST":
        pole_form = Feeder_inspectionForm(
            request.POST,
            request.FILES,
        )

        if pole_form.is_valid():
            poled = pole_form.save(commit=False)
            poled.feeder_source = pole_form.cleaned_data["feeder_source"]
            poled.metering_vt_ratio = pole_form.cleaned_data["metering_vt_ratio"]
            poled.feeder_metered = pole_form.cleaned_data["feeder_metered"]
            poled.meternumber = pole_form.cleaned_data["meternumber"]
            poled.meterbrand = pole_form.cleaned_data["meterbrand"]
            poled.metermodel = pole_form.cleaned_data["meterbrand"]
            poled.metertype = pole_form.cleaned_data["metertype"]
            poled.classofmeter = pole_form.cleaned_data["classofmeter"]
            poled.ct_ratio = pole_form.cleaned_data["ct_ratio"]
            poled.vt_ratio = pole_form.cleaned_data["vt_ratio"]
            poled.metering_core_ctratio = pole_form.cleaned_data[
                "metering_core_ctratio"
            ]
            poled.metering_core_class_ct = pole_form.cleaned_data[
                "metering_core_class_ct"
            ]
            poled.metering_core_burden_va = pole_form.cleaned_data[
                "metering_core_burden_va"
            ]
            poled.vt_ration_linked_yard = pole_form.cleaned_data[
                "vt_ration_linked_yard"
            ]
            poled.ct_ration_linked_yard = pole_form.cleaned_data[
                "ct_ration_linked_yard"
            ]
            poled.class_vt = pole_form.cleaned_data["class_vt"]
            poled.vt_burden_va = pole_form.cleaned_data["vt_burden_va"]
            poled.dt_visit = pole_form.cleaned_data["dt_visit"]
            poled.tm_visit = pole_form.cleaned_data["tm_visit"]
            poled.dt_on_meter_during_visit = pole_form.cleaned_data[
                "dt_on_meter_during_visit"
            ]
            poled.tm_on_meter_during_visit = pole_form.cleaned_data[
                "tm_on_meter_during_visit"
            ]
            poled.reading_180 = pole_form.cleaned_data["reading_180"]
            poled.reading_1801 = pole_form.cleaned_data["reading_1801"]
            poled.reading_280 = pole_form.cleaned_data["reading_280"]
            poled.reading_2801 = pole_form.cleaned_data["reading_2801"]
            poled.powerfactor = pole_form.cleaned_data["powerfactor"]
            poled.vlt_redphase = pole_form.cleaned_data["vlt_redphase"]
            poled.vlt_yellowphase = pole_form.cleaned_data["vlt_yellowphase"]
            poled.vlt_bluephase = pole_form.cleaned_data["vlt_bluephase"]
            poled.crnt_redphase = pole_form.cleaned_data["crnt_redphase"]
            poled.crnt_yellowphase = pole_form.cleaned_data["crnt_yellowphase"]
            poled.crnt_bluephase = pole_form.cleaned_data["crnt_bluephase"]
            poled.remarks = pole_form.cleaned_data["remarks"]
            poled.recommendation = pole_form.cleaned_data["recommendation"]
            poled.reading_180_img = pole_form.cleaned_data["reading_180_img"]
            poled.transdist = transdist
            poled.inspector = request.user.userprofile
            poled.save()

            messages.success(request, "The Feeder Inspection was saved successfully.")
            return redirect("transdist:transdist-update", transdist.id)
        else:
            print("invalid form")
            print(pole_form.errors)
            messages.error(request, "There was an error submitting.")
            # print(Lvinsp_form.errors)
    else:
        pole_form = Feeder_inspectionForm()
        # lv_form = LvinspectionForm(instance=new_inspection)

    context = {
        "substation": transdist,
        "pole_form": pole_form,
        "sub_form": sub_form,
        "feeder_form": feeder_form,
    }
    return render(request, "transdist/inspectin_new.html", context)


@login_required(login_url="login")
def search_by_ssn(request):
    if request.user.is_authenticated:
        meters_list = Transdist_subsations.objects.select_related("region").filter(
            status=False
        )
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(name__icontains=keyword)
    context = {
        "meters": paged_uploads,
    }
    return render(request, "transdist/transdist_substations.html", context)


@login_required(login_url="login")
def transdist_stations(request):
    if request.user.is_authenticated:
        campaign = request.user.userprofile.campaign
    if campaign == "transdist" or campaign == 'lp':
        stations = Transdist_subsations.objects.select_related("region").filter(
            status=False
        )
        paginator = Paginator(stations, 10)
        page = request.GET.get("page")
        paged_uploads = paginator.get_page(page)
    else:
        messages.error(request, "Access denied.")
        return redirect("main:my-dashboard")

    context = {"meters": paged_uploads}
    return render(request, "transdist/transdist_substations.html", context)


@login_required(login_url="login")
def transdist_update(request, pk=None):
    inspection = get_object_or_404(Transdist_insp, id=pk)
    ssn = Transdist_subsations.objects.get(id=inspection.transdist.id)
    feeder_form = Feeder_inspectionForm()
    powertx_form = Power_tx_inspectionForm()
    auxtx_form = Aux_tx_inspectionForm()
    feeder_outgoing_form = Feeder_inspection_outgoingForm()
    feederinspectin = Feeder_inspection.objects.filter(transdist=inspection)
    powertxinspectin = Power_tx_inspection.objects.filter(transdist=inspection)
    auxtxinspectin = Aux_tx_inspection.objects.filter(transdist=inspection)
    feederinspection_outgoing = Feeder_inspection_outgoing.objects.filter(transdist=inspection)

    if request.method == "POST":
        sub_form = TransdistForm(request.POST, instance=inspection)
        if sub_form.is_valid():
            poled = sub_form.save(commit=False)
            poled.county = sub_form.cleaned_data["county"]
            poled.inspector = request.user.userprofile

            if request.POST.get("finalsubmission"):
                poled.save_status = True
                poled.save()
                ssn.status = True
                ssn.save()
                messages.success(
                    request, "The Substation Inspection was submitted successfully."
                )
                return redirect("transdist:inspections-my")

            elif request.POST.get("draft"):
                poled.save_status = False
                poled.save()
                messages.success(
                    request,
                    "The Substation Inspection was saved as a draft successfully.",
                )
                return redirect("transdist:inspections-my")
        else:
            print("invalid form")
            print(sub_form.errors)
    else:
        sub_form = TransdistForm(instance=inspection)

    context = {
        "substation": inspection,
        "sub_form": sub_form,
        "ssn": ssn,
        "feeder_form": feeder_form,
        "feederinspectin": feederinspectin,
        "powertx_form": powertx_form,
        "powertxinspectin": powertxinspectin,
        "auxtx_form": auxtx_form,
        "auxtxinspectin": auxtxinspectin,
        'feeder_outgoing_form': feeder_outgoing_form,
        'feederinspection_outgoing': feederinspection_outgoing
    }
    return render(request, "transdist/inspectin_new.html", context)


@login_required(login_url="login")
def inspections_my(request):
    myinsp = Transdist_insp.objects.select_related('transdist').filter(inspector=request.user.userprofile).annotate(
        incomers=Count('transdist_inspection', distinct=True),
        outgoing=Count('transdist_inspection_outgoing', distinct=True),
        powertx=Count('transdist_inspection_powertx', distinct=True),
        auxtx=Count('transdist_inspection_auxtx', distinct=True),
    ).order_by(
        "-dtadd"
    )


    paginator = Paginator(myinsp, 20)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)

    context = {"data": paged_uploads}
    return render(request, "transdist/myinspections.html", context)


@login_required(login_url="login")
def transdist_new(request, pk=None):
    ssn = get_object_or_404(Transdist_subsations, id=pk)
    any_pending = Transdist_insp.objects.filter(
        save_status=False, inspector=request.user.userprofile
    )

    if any_pending:
        messages.error(
            request,
            "You have an inspection that is saved as draft. Submit and click on new Inspection.",
        )
        return redirect("transdist:inspections-my")
    new_inspection = Transdist_insp.objects.create(
        transdist=ssn, inspector=request.user.userprofile
    )
    if new_inspection:
        messages.success(
            request,
            "A Draft of the New Inspection was saved successfully. Open to continue with the inspection",
        )
        return redirect("transdist:inspections-my")

    context = {
        "inspection_id": new_inspection.id,
    }
    return render(request, "lv/network_myinspections.html", context)
