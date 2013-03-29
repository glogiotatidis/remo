function hash_set_value(key, value) {
    // Set value for key in hash
    var hash = $(location).attr('hash').substring(2).toLowerCase().replace(/\/$/, '');
    var keys;
    var values;

    if (!value) {
        value = '';
    }

    if (hash.length > 0) {
        keys = hash.split('/').filter(function(element, index) { return (index % 2 === 0); });
        values = hash.split('/').filter(function(element, index) { return (index % 2 === 1); });
    }
    else {
        keys = [];
        values = [];
    }

    index_of_key = keys.indexOf(key);

    if (index_of_key > -1) {
        values[index_of_key] = value;
    }
    else {
        keys.push(key);
        values.push(value);
    }

    hash = '/';
    for (var i=0; i < keys.length; i++) {
        if (values[i].length > 0 ) {
            hash += keys[i] + '/' + values[i] + '/';
        }
    }

    $(location).attr('hash', hash);
}

function hash_get_value(key) {
    // Get value for key in hash
    var hash = $(location).attr('hash').substring(2).toLowerCase();
    var keys = hash.split('/').filter(function(element, index) { return (index % 2 === 0); });
    var values = hash.split('/').filter(function(element, index) { return (index % 2 === 1); });
    var index_of_key = keys.indexOf(key);
    if (index_of_key > -1) {
        return values[index_of_key].toLowerCase();
    }

    return;
}

function set_dropdown_value(elm, value) {
    elm.val(value);
    // We have to force trigger 'change' for foundation to update.
    elm.trigger('change');
}

function pad2(number) {
    // Pad numbers
    // snippet from
    // http://www.electrictoolbox.com/pad-number-two-digits-javascript/
    return (number < 10 ? '0' : '') + number;
}

function append_to_formset(event) {
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
};
