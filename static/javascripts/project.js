$(function() {
	if (typeof window.projectScriptsInitialized !== 'undefined') {
		return;
	}
	
	window.projectScriptsInitialized = true;
	
	$(document).on('click', '.add-member', function(e) {
		e.preventDefault();
		$('form[name=membership-form] [name=employee]').val('');
		$('form[name=membership-form] [name=role]').val('');
		$('#membership-form-popup').modal('show');
		//$.toJSON({'a':1});
		return false;
	});
	
	$(document).on('click', '.manage-member', function(e) {
		e.preventDefault();
		var membershipEmployee = $(this).parents('.membership-item-form').find('[name=employee]').val();
		var membershipRole = $(this).parents('.membership-item-form').find('[name=role]').val();
		$('form[name=membership-form] [name=employee]').val(membershipEmployee);
		$('form[name=membership-form] [name=role]').val(membershipRole);
		$('#membership-form-popup').modal();
		//$.toJSON({'a':1});
		return false;
	});
	
	$(document).on('click', '.remove-member', function(e) {
		e.preventDefault();
		if (!confirm(_t('confirm:remove')+'\n'+_t('sure?'))) {
			return false;
		}
		var membershipEmployee = $(this).parents('[employee]').attr('employee');
		removeEmployee(membershipEmployee);
		return false;
	});
	
	$(document).on('submit', 'form[name=membership-form]', function(e) {
		e.preventDefault();
		$('form[name=membership-form] .error').removeClass('error');
		var membershipEmployee = $('form[name=membership-form] [name=employee]').val();
		var membershipRole = $('form[name=membership-form] [name=role]').val();
		if (!membershipEmployee) {
			$('form[name=membership-form] [name=employee]').addClass('error');
		}
		if (!membershipRole) {
			$('form[name=membership-form] [name=role]').addClass('error');
		}
		if ($('form[name=membership-form] .error').length>0) {
			return false;
		}
		submitEmployee(membershipEmployee, membershipRole);
		$('#membership-form-popup').modal('hide');
		return false;
	});
	
	$(document).on('submit', 'form[name=project-form]', function(e) {
		//e.preventDefault();
		var membershipObject = {};
		$('#member-list li form.membership-item-form').each(function() {
			var membershipNode = $(this);
			var membershipEmployee = membershipNode.find('[name=employee]').val();
			var membershipRole = membershipNode.find('[name=role]').val();
			membershipObject[membershipEmployee] = membershipRole;
		});
		var membershipObjectJSON = $.toJSON(membershipObject);
		$('form[name=project-form] [name=project_members]').val(membershipObjectJSON);
		//return false;
	});
});

removeEmployee = function(membershipEmployee) {
	$('#member-list li[employee="'+membershipEmployee+'"]').remove();
}

submitEmployee = function(membershipEmployee, membershipRole) {
	if (!$('#member-list li[employee="'+membershipEmployee+'"]').length) {
		$('#member-list').append(
			'<li employee="'+membershipEmployee+'">'+
				'<form class="membership-item-form">'+
					'<input readonly type="text" name="employee">'+
					' as <input readonly type="text" name="role">'+
					'<a href="javascript:void(0)" class="manage-member">'+_t('manage')+'</a>'+
					'<a href="javascript:void(0)" class="alert-danger remove-member">'+_t('remove')+'</a>'+
				'</form>'+
			'</li>'
		)
	}
	var membershipNode = $('#member-list li[employee="'+membershipEmployee+'"]');
	membershipNode.find('[name=employee]').val(membershipEmployee);
	membershipNode.find('[name=role]').val(membershipRole);
}
