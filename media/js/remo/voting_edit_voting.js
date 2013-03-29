$(document).ready(function() {
    $('form.custom').on('click', '.voting-add-answer-button, .voting-add-pollradio-button, .voting-add-nominee-button, .voting-add-pollrange-button', function(event) {
        event.preventDefault();
        var button_obj = $(event.currentTarget);
        var formset_obj = button_obj.closest('.formset');
        var block_obj = formset_obj.find('.copyblock').first();
        var new_block_obj = block_obj.clone();
        var prefix = formset_obj.data('prefix');
        var total_forms_obj = formset_obj.parent().children('#id_' + prefix + '-TOTAL_FORMS');
        var append_after_obj = block_obj;
        if (block_obj.siblings('.copyblock').length > 0) {
            append_after_obj = block_obj.siblings('.copyblock').last();
        }

        function attr_update(selector, attr, prepend){
          new_block_obj.find(selector + prefix + "]").each(function (index, item) {
              var item_obj = $(item);
              var prologue_length = 2+prepend.length+prefix.length+total_forms_obj.val().length;
              var item_id = item_obj.attr(attr).substr(prologue_length);
              var dash = item_obj.attr(attr).substr(prologue_length-1, 1);
              newid = prepend + prefix + '-' + total_forms_obj.val() + dash + item_id;
              item_obj.attr(attr, newid);
          });
        }
        attr_update('[id*=id_', 'id', 'id_');
        attr_update('[name*=', 'name', '');
        attr_update('[data-prefix*=', 'data-prefix', '');

        new_block_obj.insertAfter(append_after_obj);

        // Cleanup
        new_block_obj.find('input,select,textarea,label').each(function (index, item) {
            var item_obj = $(item);
            if (item_obj.is('input:hidden')) {
                return;
            }
            if (item_obj.is('input:checkbox') || item_obj.is('input:radio')) {
                item_obj.attr('checked', false);
            } else if (item_obj.is('select')) {
                item_obj.val($('options:first', item_obj).val());
                item_obj.trigger('change');
            } else {
                item_obj.val('');
            }
        });

        total_forms_obj.val(parseInt(total_forms_obj.val(), 10) + 1);
    });

    // Move foundation elements to position.
    ['start', 'end'].forEach(function(obj) {
        ['0_month', '0_day', '0_year', '1_hour', '1_minute'].forEach(function(elem) {
            var destination = $('#' + obj + '-' + elem.substr(2));
            var form_elem = $('#id_' + obj + '_form_' + elem);
            var foundation_elem = form_elem.next().detach();

            form_elem.detach().appendTo(destination);
            foundation_elem.appendTo(destination);
        });
    });

    // Auto change end year, month, day when start changes.
    ['month', 'day', 'year'].forEach(function(when) {
        $('#id_start_form_0_' + when).change(function() {
            var obj = $('#id_end_form_0_' + when);
            obj.val($('#id_start_form_0_' + when).val());
            obj.trigger('change');
        });
    });
});
