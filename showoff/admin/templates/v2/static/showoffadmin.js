var SHOWOFFADMIN = SHOWOFFADMIN || {};

(function(ns) {
    'use strict';

    var _images = [];

    var _cfg = {
        'base_url': 'http://showoff_admin',
        'album': 'default'
    };

    var init = function(cfg, images) {
        $.extend(_cfg, cfg);
        _images = images;

        $('.rotate').on('click', function(event) {
            event.preventDefault();
            var d = new Date();
            var index = $(this).data('index')
            rotate($(this).data('steps'), $('#img-' + index).data('filename'));
            $('#img-' + index).src = $('#img-' + index).src + '?' + d.getTime();
        });

        $('#rotate-all-images').on('click', function(event) {
            event.preventDefault();
            return rotate_all_images(0);
        });

        $('.toggle-publish').each(function(index, value) {
            var icon = ($(this).data('value') == 'yes') ? 'ok' : 'remove';
            $(this).html(glyph(icon));
        });

        $('.toggle-publish').on('click', function(event) {
            event.preventDefault();
            return toggle_publish($(this));
        });

        $('.toggle-bool').each(function(index, value) {
            var icon = ($(this).data('value') == 'yes') ? 'ok' : 'remove';
            $(this).html(glyph(icon));
        });

        $('.toggle-bool').on('click', function(event) {
            event.preventDefault();
            return toggle_bool($(this));
        });
    };

    var init_edit_users = function() {
        $('.delete-user').on('click', function(event) {
            event.preventDefault();
            var i = $(this).data('index')
            if (confirm('Are you sure you want to delete user "' + $(this).data('username') + '"?')) {
                var url = album_url() + 'remove_user/' + $(this).data('username') + '/'
                var result = $.getJSON(url, false, function() {
                    $('#user-' + i).remove();
                });
            }
        });
    };

    var get = function(key) {
        return _cfg[key];
    };

    var set = function(key, value) {
        _cfg[key] = value;
    };

    var album_url = function() {
        return ns.get('base_url') + ns.get('album') + '/';
    };

    var file_url = function(filename) {
        return album_url() + filename + '/'
    };

    var glyph = function(icon) {
        return '<span class="glyphicon glyphicon-' + icon + '"></span>';
    };

    var toggle = function(element, url) {
        $(element).html('please wait ...');
        var new_value = (element.data('value') == 'yes') ? 'no' : 'yes';
        var result = $.getJSON(url, false, function() {
            var icon = (new_value == 'yes') ? 'ok' : 'remove';
            var new_text = glyph(icon)

            $(element).data('value', new_value);
            $(element).html(new_text);
        });
    };

    var toggle_publish = function(element) {
        var url = file_url(element.data('filename')) + 'toggle_publish';
        var new_value = (element.data('value') == 'yes') ? 'no' : 'yes';
        toggle(element, url);

        if (new_value == 'no') {
            element.parent().parent().removeClass('published');
        } else {
            element.parent().parent().addClass('published');
        }
    };

    var toggle_bool = function(element) {
        var new_value = (element.data('value') == 'yes') ? 'no' : 'yes';
        var url = album_url() + 'set/' + element.data('setting')  + '/' + new_value;
        toggle(element, url)
    };

    var _rotate_all_images = function(index) {
        var percentage_complete = Math.round((index * 100) / _images.length);
        $('#progress').html(percentage_complete + ' % done (' + index + ' of ' + _images.length + ': ' + _images[index] + ')');
        $.ajax({
            url: album_url() + 'rotate_exif/' + _images[index] + '/',
            context: document.body,
            success: function() {
                if (index < _images.length-1) {
                    _rotate_all_images(index+1);
                } else {
                    window.location.reload();
                }
            }
        });
    };

    var rotate_all_images = function(index) {
        if (confirm('This will rotate all images in the album according to EXIF specs. Are you sure?')) {
            $.blockUI({ message: '<h1>Rotating all images ...</h1><h2><span id="progress">0 percent complete</span></h2>'});
            _rotate_all_images(index);
        }
    };

    var rotate = function(steps, filename) {
        var url = file_url(filename) + 'rotate/' + steps + '/';
        $.blockUI({ message: '<h1>Rotating image ...</h1>'});
        $.ajax({
            url: url,
            context: document.body,
            success: function() {
                window.location.reload();
            }
        });
    };


    // export public functions
    ns.init = init;
    ns.init_edit_users = init_edit_users;
    ns.get = get;
    ns.set = set;
}(SHOWOFFADMIN));
