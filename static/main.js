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


// お嬢詳細画面の出勤情報：時間の表示設定
function switchAvailbleTime(selectedDate=undefined, timeValues=[]) {
    // 空の場合に表示するパラグラフ
    var emptyParagraph = $('p#empty-available-time');
    // 一旦すべての時間を非表示にする
    var listItems = $('ul.available_time li');
    for (var item of listItems) {
        $(item).css('display', 'none');
    }

    if (timeValues.length == 0 ) {
        // 空の場合
        emptyParagraph.css('display', '');
    } else {
        // 予約できる日時がある場合
        for (var item of timeValues) {   
            emptyParagraph.css('display', 'none');  
            $('ul.available_time li.date-'+selectedDate).css('display', '')
        }
    }
}

// お嬢詳細画面の出勤情報：日付を選択したとき
$('select[name=available_date]').on('change', function (e) {
    var selectedValue = $(e.currentTarget).val();
    var timeItems = $('li.date-'+selectedValue);

    // すべて選択されていない状態にする
    var listItems = $('ul.available_time li');
    for (var item of listItems) {
        $(item).removeClass('active');
    }
    
    var timeValues = [];
    for (var item of timeItems) {
        var value = $(item).data("value");
        timeValues.push(value);
    }
    switchAvailbleTime(selectedValue, timeValues);
    $('.hostess-detail button[type=submit]').prop('disabled', true);
});

// お嬢詳細画面の出勤情報：日時ボタンをクリックしたとき
$('ul.available_time li').on('click', function (e) {
    var selectedItem = $(e.currentTarget);
    // 他のボタンからactiveを削除
    var listItems = $('ul.available_time li');
    for (var item of listItems) {
        $(item).removeClass('active');
    }
    selectedItem.addClass('active');
    // selectフォームの値を変更
    var value = selectedItem.data('value');
    $('select[name=available_time]').value = value;
    $('.hostess-detail button[type=submit]').prop('disabled', false);
});