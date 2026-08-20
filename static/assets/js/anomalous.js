$(document).ready(function () {
  $('#id_faultystatus').change(function () {
    if ($(this).val() === ' ') {
      $('#new_meterno').hide()
      $('#id_new_meterno').hide()
    } else if ($(this).val() === 'replaced_faulty') {
      $('#id_new_meterno').show()
      $('#new_meterno').show()
    } else if ($(this).val() === 'replaced_tampered') {
      $('#id_new_meterno').show()
      $('#new_meterno').show()
    } else {
      $('#id_new_meterno').hide()
      $('#new_meterno').hide()
    }
  })
  $('#id_faultystatus').trigger('change')
})
