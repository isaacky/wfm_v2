$(document).ready(function () {

     $("#id_hvearth_intact").change(function () {
        if ($(this).val() === "") {
            $('#hvearth_intact').hide();
            $('#hvearth_values_missing').hide();
        } else if ($(this).val() === "yes") {
            $('#hvearth_intact').show();
            $('#hvearth_values_missing').hide();

        } else if ($(this).val() === "no") {
            $('#hvearth_intact').hide();
            $('#hvearth_values_missing').show();
        }

    });
    $("#id_hvearth_intact").trigger("change")

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

    $("#id_refubby").change(function () {
        if ($(this).val() === " ") {
            $('#workshop').hide();
            $('#contractor').hide();
        } else if ($(this).val() === "kplc") {
            $('#workshop').show();
            $('#contractor').hide();

        } else if ($(this).val() === "contractor") {
            $('#contractor').show();
            $('#workshop').hide();

        } else {
            $('#workshop').hide();
            $('#contractor').hide();


        }
    });
    $("#id_refubby").trigger("change")

    $("#id_surgearrestors").change(function () {
        if ($(this).val() === "") {
            $('#surgearrestors').hide();
            $('#surge_arrestors_missing').hide();
        } else if ($(this).val() === "yes") {
            $('#surgearrestors').show();
            $('#surge_arrestors_missing').hide();

        } else if ($(this).val() === "no") {
            $('#surgearrestors').hide();
            $('#surge_arrestors_missing').show();
        }

    });
    $("#id_surgearrestors").trigger("change")



})