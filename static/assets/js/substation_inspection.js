
$(document).ready(function () {
    $("#id_noofcircuits").change(function () {
        if ($(this).val() === "") {
            $('#circuit1_substation').hide();
            $('#circuit2_substation').hide();
            $('#circuit3_substation').hide();

        } else if ($(this).val() === '1') {
            $('#circuit1_substation').show();
            $('#circuit2_substation').hide();
            $('#circuit3_substation').hide();

        } else if ($(this).val() === '2') {
            $('#circuit2_substation').show();
            $('#circuit1_substation').hide();
            $('#circuit3_substation').hide();

        } else if ($(this).val() === '3') {
            $('#circuit3_substation').show();
            $('#circuit2_substation').hide();
            $('#circuit1_substation').hide();

        }else{
            $('#circuit1_substation').hide();
            $('#circuit2_substation').hide();
            $('#circuit3_substation').hide();
        }

    });

    $("#id_noofcircuits").trigger("change")

    $("#id_hvearth_intact").change(function () {
        if ($(this).val() === "") {
            $('#hvearth_intact').hide();
        } else if ($(this).val() === "yes") {
            $('#hvearth_intact').show();

        } else if ($(this).val() === "no") {
            $('#hvearth_intact').hide();
        }

    });
    $("#id_hvearth_intact").trigger("change")

    $("#id_neutralearth_intact").change(function () {
        if ($(this).val() === "") {
            $('#neutralearth_intact').hide();
        } else if ($(this).val() === "yes") {
            $('#neutralearth_intact').show();

        } else if ($(this).val() === "no") {
            $('#neutralearth_intact').hide();
        }

    });
    $("#id_neutralearth_intact").trigger("change")

    $("#id_surgearrestors").change(function () {
        if ($(this).val() === "") {
            $('#surgearrestors').hide();
        } else if ($(this).val() === "yes") {
            $('#surgearrestors').show();

        } else if ($(this).val() === "no") {
            $('#surgearrestors').hide();
        }

    });
    $("#id_surgearrestors").trigger("change")

    $("#id_arcinghorns").change(function () {
        if ($(this).val() === "") {
            $('#arcinghorns').hide();
        } else if ($(this).val() === "yes") {
            $('#arcinghorns').show();

        } else if ($(this).val() === "no") {
            $('#arcinghorns').hide();
        }

    });
    $("#id_arcinghorns").trigger("change")

    $("#id_txloading").change(function () {
        if ($(this).val() === "") {
            $('#txloading_yes').hide();
            $('#load_distributionby').hide();
        } else if ($(this).val() === "yes") {
            $('#load_distributionby').hide();
            $('#txloading_yes').show();

        } else if ($(this).val() === "no") {
            $('#load_distributionby').show();
            $('#txloading_yes').hide();
        }

    });
    $("#id_txloading").trigger("change")



})