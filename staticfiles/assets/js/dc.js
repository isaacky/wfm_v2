
     $(document).ready(function () {
         $("#id_dc_conf_type").change(function () {
             if ($(this).val() === "") {
                 $('#dc_reading').hide();
                 $('#dc_meterimg').hide();

             }else if ($(this).val() === 'postpaid') {
                  $('#dc_reading').show();
                  $('#dc_meterimg').show();

             }else if ($(this).val() === 'prepaid') {
                $('#dc_reading').hide();
                $('#dc_meterimg').hide();
             }

         });
          $("#id_dc_conf_type").trigger("change")

         $("#id_dc_meteringstatus").change(function () {

            if ($(this).val() === "") {
                $('#faultystatus').hide();
                $('#tamperedstatus').hide();
                $('#bypassstatus').hide();
                $('#dc_meterimg').hide();

            } else if ($(this).val() === "okay") {
                $('#metering-not-okay').hide();


            } else if ($(this).val() === "faulty") {

                $('#faultystatus').show();
                $('#tamperedstatus').hide();
                $('#bypassstatus').hide();
                $('#dc_meterimg').show();


            } else if ($(this).val() === "tampered") {
               $('#faultystatus').hide();
                $('#tamperedstatus').show();
                $('#bypassstatus').hide();
                $('#dc_meterimg').show();

            } else if ($(this).val() === "bypassed") {
                $('#faultystatus').hide();
                $('#tamperedstatus').hide();
                $('#bypassstatus').show();
                $('#dc_meterimg').show();

            } else if ($(this).val() === "nometer") {
                $('#faultystatus').hide();
                $('#tamperedstatus').hide();
                $('#bypassstatus').hide();
                $('#dc_meterimg').show();
            } else {
               $('#faultystatus').show();
                $('#tamperedstatus').show();
                $('#bypassstatus').show();
                $('#dc_meterimg').show();
            }
        });
        $("#id_dc_meteringstatus").trigger("change")

          $("#id_dc_installationstatus").change(function () {
            if ($(this).val() === "") {
                $('#notokaystatus').hide();
            } else if ($(this).val() === "okay") {
                $('#notokaystatus').hide();
            } else {
                $('#notokaystatus').show();
            }
        });
        $("#id_dc_installationstatus").trigger("change")



     })



