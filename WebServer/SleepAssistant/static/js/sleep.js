function sleepClick(value) {
	$('#id_is_sleep').prop('checked',value);
	$('#sleep_form_id').submit()
}

function getupClick() {
	$('#getup_form_id').submit()
}