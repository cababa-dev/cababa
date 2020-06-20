// トップページFAQのトグル処理
$('.question').on('click', function (e) {
    var targetId = $(e.currentTarget).attr('id');
    var toggleTarget = $('div[aria-labelledby="' + targetId + '"]');
    toggleTarget.toggle(100);
});

// 選択オプションがクリックされたとき
// select multipleフィールドから選択された項目を削除したり追加したりする
$('.condition-option').on('click', function (e) {
    e.preventDefault();
    var clickedTarget = $(e.currentTarget);
    var targetFieldName = $(e.currentTarget).attr('data-target');
    var targetFieldValue = $(e.currentTarget).attr('data-value');
    var targetField = $('select[name="'+targetFieldName+'"] option[value="'+targetFieldValue+'"]');

    if (clickedTarget.hasClass('selected')) {
        clickedTarget.removeClass('selected');
        targetField.removeAttr('selected');
    } else {
        clickedTarget.addClass('selected');
        targetField.attr('selected', true);
    }
});

// 条件クリア
$('#condition-clear').on('click', function (e) {
    // フリーワードで探す
    $('.condition-body input[name="keyword"]').prop('value', '');
    // 出勤日時で探す
    $('.condition-body input[name="whole_date"]').removeAttr('checked');
    $('.condition-body select[name="date"]').prop('selectedIndex', 0);
    $('.condition-body select[name="time"]').prop('selectedIndex', 0);
    // 体型から探す
    for (var option of $('.condition-body select[name="body"] option')) {        
        $(option).removeAttr('selected');
    }
    // 年齢から探す
    for (var option of $('.condition-body select[name="age"] option')) {
        $(option).removeAttr('selected');
    }
    // 複数選択を解除
    for (var option of $('.condition-option')) {
        $(option).removeClass('selected');
    }
});