$(document).ready(function () {
    $("#id_fallback_req").change(function () {
        if ($(this).val() === "") {
            $('#fallback_activities').hide();
        } else if ($(this).val() === "yes") {
            $('#fallback_activities').show();
        } else {
            $('#fallback_activities').hide();

        }
    });
    $("#id_fallback_req").trigger("change")

    $("#id_anomalies_addressed_insp").change(function () {
        if ($(this).val() === "") {
            $('#anomalies_addressed_insp_list').hide();
        } else if ($(this).val() === "yes") {
            $('#anomalies_addressed_insp_list').show();
        } else {
            $('#anomalies_addressed_insp_list').hide();

        }
    });
    $("#id_anomalies_addressed_insp").trigger("change")

    $("#id_arethereanomalies").change(function () {
        if ($(this).val() === "") {
            $('#anomalies_list').hide();
            $('#commit_annomalies').hide();
            $('#commit_inspection').hide();
        } else if ($(this).val() === "yes") {
            $('#anomalies_list').show();
            $('#commit_annomalies').show();
            $('#commit_inspection').hide();
        } else {
            $('#anomalies_list').hide();
            $('#commit_annomalies').hide();
            $('#commit_inspection').show();

        }
    });
    $("#id_arethereanomalies").trigger("change")

    $("#id_modulecomm_ci").change(function () {
        if ($(this).val() === "") {
            $('#modulecom_not_rsn').hide();
        } else if ($(this).val() === "yes") {
            $('#modulecom_not_rsn').hide();
        } else {
            $('#modulecom_not_rsn').show();

        }
    });
    $("#id_modulecomm_ci").trigger("change")

    $("#id_zera_test").change(function () {
        if ($(this).val() === "") {
            $('#id_redphase_zera').hide();
            $('#id_yellowphase_zera').hide();
            $('#id_bluephase_zera').hide();
            $('#zera').hide();
        } else if ($(this).val() === "no") {
            $('#id_redphase_zera').hide();
            $('#id_yellowphase_zera').hide();
            $('#id_bluephase_zera').hide();
        } else {
            $('#id_redphase_zera').show();
            $('#id_yellowphase_zera').show();
            $('#id_bluephase_zera').show();

        }
    });
    $("#id_zera_test").trigger("change")

    $("#id_reverse_consumption").change(function () {
        if ($(this).val() === "") {
            $('#reverse_consumption_rsn').hide();
        } else if ($(this).val() === "no") {
            $('#reverse_consumption_rsn').hide();
        } else {
            $('#reverse_consumption_rsn').show();

        }
    });
    $("#id_reverse_consumption").trigger("change")

    $("#id_ctratio_ci_match").change(function () {
        if ($(this).val() === "none") {
            $('#ctratio_ci_match_rsn').hide();
        } else if ($(this).val() === "no") {
            $('#ctratio_ci_match_rsn').show();
        } else {
            $('#ctratio_ci_match_rsn').hide();

        }
    });
    $("#id_ctratio_ci_match").trigger("change")

    $("#id_smartmeter").change(function () {
        if ($(this).val() === "") {
            $('#module-information').hide();
            $('#ctratio_ci').hide();
            $('#ctratio_ci_match').hide();
            $('#moduleinstalled').hide();
            $('#id_ctchamber_seal_b4').show();
            $('#id_ctchamber_seal_after').show();
            $('#ct-chamber-AMR').show();
        } else if ($(this).val() === "no") {
            $('#module-information').hide();
            $('#ctratio_ci').hide();
            $('#ctratio_ci_match').hide();
            $('#moduleinstalled').hide();
            $('#id_ctchamber_seal_b4').show();
            $('#id_ctchamber_seal_after').show();
            $('#ct-chamber-AMR').show();
        } else {
            $('#module-information').show();
            $('#ctratio_ci').show();
            $('#ctratio_ci_match').show();
            $('#moduleinstalled').show();
            $('#id_ctchamber_seal_b4').hide();
            $('#id_ctchamber_seal_after').hide();
            $('#ct-chamber-AMR').hide();

        }
    });
    $("#id_smartmeter").trigger("change")

    $("#id_moduleinstalled").change(function () {
        if ($(this).val() === "none") {
            $('#module-information').hide();

        } else if ($(this).val() === "no") {
            $('#module-information').hide();

        } else {
            $('#module-information').show();

        }
    });
    $("#id_moduleinstalled").trigger("change")


    $("#id_solar_installed").change(function () {
        if ($(this).val() === "no") {
            $('#solar-installation').hide();

        } else if ($(this).val() === "yes") {
            $('#solar-installation').show();

        } else {
            $('#solar-installation').hide();

        }
    });
    $("#id_solar_installed").trigger("change")


})






