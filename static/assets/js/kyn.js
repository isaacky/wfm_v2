$(document).ready(function () {
    $("#id_poor_sags_cl_cond").change(function () {
        if ($(this).val() === "") {
            $('#id_midspanpole_req').hide();
            $('#id_retention_req').hide();
            $('#midspanpole_req').hide();
            $('#retention_req').hide();
            $('#retention-req-maintenance').hide();
            $('#retention-req-maintenance-done').hide();
        } else if ($(this).val() === "yes") {
            $('#id_midspanpole_req').show();
            $('#id_retention_req').show();
            $('#midspanpole_req').show();
            $('#retention_req').show();
            $('#retention-req-maintenance').show();
        } else if ($(this).val() === "no") {
            $('#id_midspanpole_req').hide();
            $('#id_retention_req').hide();
            $('#midspanpole_req').hide();
            $('#retention_req').hide();
            $('#retention-req-maintenance').hide();
        }

    });
    $("#id_poor_sags_cl_cond").trigger("change")

    $("#id_retention_req_status").change(function () {
        if ($(this).val() === "") {
            $('#retention-req-maintenance-done').hide();
        } else if ($(this).val() === "yes") {
            $('#retention-req-maintenance-done').show();

        } else if ($(this).val() === "no") {
            $('#retention-req-maintenance-done').hide();
        }
    });
    $("#id_retention_req_status").trigger("change")

    $("#id_lvline_veg").change(function () {
        if ($(this).val() === "") {
            $('#id_traceclear_span').hide();
            $('#traceclear_span').hide();
            $('#traceclear-span-maintenance').hide();
            $('#traceclear-span-maintenance-done').hide();
        } else if ($(this).val() === "yes") {
            $('#id_traceclear_span').show();
            $('#traceclear_span').show();
            $('#traceclear-span-maintenance').show();
        } else if ($(this).val() === "no") {
            $('#id_traceclear_span').hide();
            $('#traceclear_span').hide();
            $('#traceclear-span-maintenance').hide();
        }
    });
    $("#id_lvline_veg").trigger("change")

    $("#id_traceclear_span_status").change(function () {
        if ($(this).val() === "") {
            $('#traceclear-span-maintenance-done').hide();
        } else if ($(this).val() === "yes") {
            $('#traceclear-span-maintenance-done').show();

        } else if ($(this).val() === "no") {
            $('#traceclear-span-maintenance-done').hide();
        }
    });
    $("#id_traceclear_span_status").trigger("change")

    $("#id_conductors_uprate").change(function () {
        if ($(this).val() === "") {
            $('#id_conductors_uprate_span').hide();
            $('#conductors_uprate_span').hide();
            $('#conductors-uprate-span-maintained').hide();
            $('#conductors-uprate-span-maintained-done').hide();

        } else if ($(this).val() === "yes") {
            $('#id_conductors_uprate_span').show();
            $('#conductors_uprate_span').show();
            $('#conductors-uprate-span-maintained').show();

        } else if ($(this).val() === "no") {
            $('#id_conductors_uprate_span').hide();
            $('#conductors_uprate_span').hide();
            $('#conductors-uprate-span-maintained').hide();

        }

    });
    $("#id_conductors_uprate").trigger("change")

    $("#id_conductors_uprate_status").change(function () {
        if ($(this).val() === "") {
            $('#conductors-uprate-span-maintained-done').hide();
        } else if ($(this).val() === "yes") {
            $('#conductors-uprate-span-maintained-done').show();

        } else if ($(this).val() === "no") {
            $('#conductors-uprate-span-maintained-done').hide();
        }
    });
    $("#id_conductors_uprate_status").trigger("change")

    $("#id_pme_installed").change(function () {
        if ($(this).val() === "") {
            $('#id_pme_missing_poles').hide();
            $('#pme_missing_poles').hide();
            $('#pme-missing-poles-mainteained').hide();
            $('#pme-missing-poles-mainteained-done').hide();

        } else if ($(this).val() === "no") {
            $('#id_pme_missing_poles').show();
            $('#pme_missing_poles').show();
            $('#pme-missing-poles-mainteained').show();

        } else if ($(this).val() === "yes") {
            $('#id_pme_missing_poles').hide();
            $('#pme_missing_poles').hide();
            $('#pme-missing-poles-mainteained').hide();
        }

    });
    $("#id_pme_installed").trigger("change")

    $("#id_pme_missing_poles_status").change(function () {
        if ($(this).val() === "") {
            $('#pme-missing-poles-mainteained-done').hide();
        } else if ($(this).val() === "yes") {
            $('#pme-missing-poles-mainteained-done').show();

        } else if ($(this).val() === "no") {
            $('#pme-missing-poles-mainteained-done').hide();
        }
    });
    $("#id_pme_missing_poles_status").trigger("change")

    $("#id_lv_overdistance").change(function () {
        if ($(this).val() === "") {
            $('#id_lv_overdistance_l').hide();
            $('#lv_overdistance_l').hide();
            $('#lv-overdistance-l-maintained').hide();
            $('#lv-overdistance-l-maintained-done').hide();

        } else if ($(this).val() === "yes") {
            $('#id_lv_overdistance_l').show();
            $('#lv_overdistance_l').show();
            $('#lv-overdistance-l-maintained').show();

        } else if ($(this).val() === "no") {
            $('#id_lv_overdistance_l').hide();
            $('#lv_overdistance_l').hide();
            $('#lv-overdistance-l-maintained').hide();

        }

    });
    $("#id_lv_overdistance").trigger("change")

    $("#id_lv_overdistance_l_status").change(function () {
        if ($(this).val() === "") {
            $('#lv-overdistance-l-maintained-done').hide();
        } else if ($(this).val() === "yes") {
            $('#lv-overdistance-l-maintained-done').show();

        } else if ($(this).val() === "no") {
            $('#lv-overdistance-l-maintained-done').hide();
        }
    });
    $("#id_lv_overdistance_l_status").trigger("change")

    $("#id_illegal_connections").change(function () {
        if ($(this).val() === "") {
            $('#id_illegal_connections_l').hide();
            $('#illegal_connections_l').hide();
            $('#illegal-connections-l-maintained').hide();
            $('#illegal-connections-l-maintained-done').hide();

        } else if ($(this).val() === "yes") {
            $('#id_illegal_connections_l').show();
            $('#illegal_connections_l').show();
            $('#illegal-connections-l-maintained').show();

        } else if ($(this).val() === "no") {
            $('#id_illegal_connections_l').hide();
            $('#illegal_connections_l').hide();
            $('#illegal-connections-l-maintained').hide();

        }

    });
    $("#id_illegal_connections").trigger("change")

    $("#id_illegal_connections_l_status").change(function () {
        if ($(this).val() === "") {
            $('#illegal-connections-l-maintained-done').hide();
        } else if ($(this).val() === "yes") {
            $('#illegal-connections-l-maintained-done').show();

        } else if ($(this).val() === "no") {
            $('#illegal-connections-l-maintained-done').hide();
        }
    });
    $("#id_illegal_connections_l_status").trigger("change")

    $("#id_reconducturing_pvc").change(function () {
        if ($(this).val() === "") {
            $('#id_reconducturing_pvc_l').hide();
            $('#reconducturing_pvc_l').hide();
            $('#reconducturing-pvc-l-maintenance').hide();
            $('#reconducturing-pvc-l-maintenance-done').hide();

        } else if ($(this).val() === "yes") {
            $('#id_reconducturing_pvc_l').show();
            $('#reconducturing_pvc_l').show();
            $('#reconducturing-pvc-l-maintenance').show();

        } else if ($(this).val() === "no") {
            $('#id_reconducturing_pvc_l').hide();
            $('#reconducturing_pvc_l').hide();
            $('#reconducturing-pvc-l-maintenance').hide();

        }

    });
    $("#id_reconducturing_pvc").trigger("change")

    $("#id_reconducturing_pvc_l_status").change(function () {
        if ($(this).val() === "") {
            $('#reconducturing-pvc-l-maintenance-done').hide();
        } else if ($(this).val() === "yes") {
            $('#reconducturing-pvc-l-maintenance-done').show();

        } else if ($(this).val() === "no") {
            $('#reconducturing-pvc-l-maintenance-done').hide();
        }
    });
    $("#id_reconducturing_pvc_l_status").trigger("change")

    $("#id_circuits").change(function () {
        if ($(this).val() === "") {
            $('#circuit1').hide();
            $('#circuit2').hide();
            $('#circuit3').hide();

        } else if ($(this).val() === '1') {
            $('#circuit1').show();
            $('#circuit2').hide();
            $('#circuit3').hide();

        } else if ($(this).val() === '2') {
            $('#circuit2').show();
            $('#circuit1').hide();
            $('#circuit3').hide();

        } else if ($(this).val() === '3') {
            $('#circuit3').show();
            $('#circuit2').hide();
            $('#circuit1').hide();

        }

    });
    $("#id_circuits").trigger("change")

    $("#id_noofcircuits").change(function () {
        if ($(this).val() === "") {
            $('#circuit1').hide();
            $('#circuit2').hide();
            $('#circuit3').hide();

        } else if ($(this).val() === '1') {
            $('#circuit1').show();
            $('#circuit2').hide();
            $('#circuit3').hide();

        } else if ($(this).val() === '2') {
            $('#circuit2').show();
            $('#circuit1').hide();
            $('#circuit3').hide();

        } else if ($(this).val() === '3') {
            $('#circuit3').show();
            $('#circuit2').hide();
            $('#circuit1').hide();

        }

    });
    $("#id_noofcircuits").trigger("change")

    $("#id_poshomills_onsingle_p").change(function () {
        if ($(this).val() === "") {
            $('#id_poshomills_onsingle_p_n').hide();
            $('#poshomills_onsingle_p_n').hide();
            $('#poshomills-onsingle-p-n-maintained').hide();
            $('#poshomills-onsingle-p-n-maintained-done').hide();

        } else if ($(this).val() === "yes") {
            $('#id_poshomills_onsingle_p_n').show();
            $('#poshomills_onsingle_p_n').show();
            $('#poshomills-onsingle-p-n-maintained').show();

        } else if ($(this).val() === "no") {
            $('#id_poshomills_onsingle_p_n').hide();
            $('#poshomills_onsingle_p_n').hide();
            $('#poshomills-onsingle-p-n-maintained').hide();

        }

    });
    $("#id_poshomills_onsingle_p").trigger("change")

    $("#id_poshomills_onsingle_p_n_status").change(function () {
        if ($(this).val() === "") {
            $('#poshomills-onsingle-p-n-maintained-done').hide();
        } else if ($(this).val() === "yes") {
            $('#poshomills-onsingle-p-n-maintained-done').show();

        } else if ($(this).val() === "no") {
            $('#poshomills-onsingle-p-n-maintained-done').hide();
        }
    });
    $("#id_poshomills_onsingle_p_n_status").trigger("change")

    $("#id_tx_status").change(function () {
        if ($(this).val() === " ") {
            $('#refubby').hide();
            $('#workshop').hide();
            $('#contractor').hide();
        } else if ($(this).val() === "refurbished") {
            $('#refubby').show();
            $('#contractor').hide();

        } else if ($(this).val() === "new") {
            $('#refubby').hide();
            $('#contractor').hide();
            $('#workshop').hide();

        } else {
            $('#refubby').hide();
            $('#contractor').hide();
            $('#workshop').hide();

        }
    });
    $("#id_tx_status").trigger("change")


})













