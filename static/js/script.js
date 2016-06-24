$(document).ready(function(){
    jQuery(window).load(function(){
        $('.js-photo').each(function(index, el) {
            $(this).css('background-image', 'url(' + $(this).data('src') + ')');
        });

        $(document).on('click', '.js-photo-tag', function(event) {
            event.stopPropagation();
            event.preventDefault();

            var tag = $(this).data('tag');
            var form = $('.js-form');

            form.find('.js-form-tags option:selected, .js-form-ex-tags option:selected').prop('selected', false);
            form.find('.js-form-tags option[value=' + tag + ']').prop('selected', true);
            form.find('.js-form-tags').trigger('change');
            $('.js-submit').trigger('click');
        });

        $(document).on('change', '.js-form-tags, .js-form-ex-tags, .js-order', function(event) {
            $('.js-form .js-page').val('1');
        });

        $(document).on('click', '.js-like-button', function(event) {
            var photoId = $(this).data('pid');
            var inc = $(this).data('inc');
            var input = $(this).parents('.js-photo-row').find('.js-rating');

            if (photoId && inc) {
                $.get('/ajax/like/photo/' + photoId + '/value/' + inc + '/', function(data) {
                    var response = jQuery.parseJSON(data);
                    if (Number.isInteger(response)) {
                        input.text(response);
                    }
                });
            }
        });

        $(document).on('click', '.js-submit', function(event) {
            event.stopPropagation();
            event.preventDefault();
            cleanAndSumbit();
        });

        $(document).on('click', '.js-go-to-page', function(event) {
            event.stopPropagation();
            event.preventDefault();
            var page = $(this).data('page');
            var input = $('.js-page');
            if (page > input.data('max')) page = input.data('max');
            if (page < 1) page = 1;
            input.val(page);
            $('.js-submit').trigger('click');
        });


        function cleanAndSumbit(){
            var form = $('.js-form');

            var ordering = form.find('.js-order')
            if (ordering.find('option:first').prop('selected')) {
                form.find('.js-order option').attr('disabled', 'disabled')
            }

            var page = form.find('.js-page');
            if (!page.val() || page.val() == '1') {
                page.attr('disabled', 'disabled')
            }

            form.submit();
        }
    });
});