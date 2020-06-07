$('.question').on('click', function (e) {
    var targetId = $(e.currentTarget).attr('id');
    var toggleTarget = $('div[aria-labelledby="' + targetId + '"]');
    toggleTarget.toggle(100);
});