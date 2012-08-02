/* Pyqual
 *
 * Copyright 2012       '"Mike Shultz" <mike@mikeshultz.com>'
 */

fakeUrl = function (anchor) {
    href = location.href;
    href = href.replace(/\#[A-Za-z0-9\-].*/, '');
    if (anchor) {
        href += anchor
    }
    location.href = href;
    return false;
};

resizeCodeTextarea = function(textarea) {
    var str = $(this).val();
    var cols = 54;
    var linecount = 0;
    var maxrows = 14;
    var lines = str.split("\n");
    $.each(str.split("\n"), function(l) {
        console.log(l);
        linecount += Math.ceil( l / cols );
    });
    if (linecount > maxrows) { linecount = maxrows; }
    console.log(cols + ' - ' + linecount + ' - ' + $(this).val());
    $(this).attr('rows', String(linecount + 2));
};

showResult = function(data) {
    if (data['result'] == 'success') {
        $('#alert .alert-heading').html('Success!');
        $('#alert .alert-body').html(data['message']);
        $('#alert').show();
    }
};

var pagePattern = /#[A-Za-z0-9\-].*/;

var Pq = function() {
    this.version = 'a0727';
};

Pq.prototype = {
    loadTests: function() {
        $.getJSON('j/test', function(data) {
            var html = '';

            $.each(data, function(key, val) {
                html += '<tr id="' + val['test_id'] + '">';
                html += '<td><a onclick="site.getTestDetail(' + val['test_id'] + '); return false;" href="#test-detail:' + val['test_id'] + '">' + val['test_id'] + '</a></td>';
                html += '<td><a onclick="site.getTestDetail(' + val['test_id'] + '); return false;" href="#test-detail:' + val['test_id'] + '">' + val['name'] + '</a></td>';
                html += '<td>' + val['schedule_name'] + '</td>';
                html += '<td>' + (val['lastrun'] ? val['lastrun'] : '') + '</td>';
                html += '<td>' + (val['database_name'] ? val['database_name'] : '<em class="muted">None Set</em> <span class="badge badge-important">!</span>') + '</td>';
                html += '</tr>';
            });

            $('table#testlist tbody').html(html);
        });
    },
    loadDatabases: function() {
        $.getJSON('j/database', function(data) {
            var html = '';

            $.each(data, function(key, val) {
                html += '<tr id="' + val['database_id'] + '">';
                html += '<td><a href="#database:' + val['database_id'] + '">' + val['database_id'] + '</a></td>'
                html += '<td><a href="#database:' + val['database_id'] + '">' + val['name'] + '</a></td>';
                html += '<td>' + val['username'] + '</td>';
                html += '<td>' + val['hostname'] + ':' + val['port'] + '</td>';
                html += '<td>' + val['active'] + '</td>';
                html += '</tr>';
            });

            $('table#databaselist tbody').html(html);
        });
    },
    loadUsers: function() {
        $.getJSON('j/user', function(data) {
            var html = '';

            $.each(data, function(key, val) {
                html += '<tr id="' + val['user_id'] + '">';
                html += '<td><a href="#user:' + val['user_id'] + '">' + val['user_id'] + '</a></td>';
                html += '<td><a href="#user:' + val['user_id'] + '">' + val['username'] + '</a></td>';
                html += '<td>' + val['email'] + '</td>';
                html += '</tr>';
            });

            $('table#userlist tbody').html(html);
        });
    },
    loadAll: function() {
        this.loadTests();
        this.loadDatabases();
        this.loadUsers();
    },
    getTestDetail: function(test_id) {
        var selected = {};
        $.getJSON('j/test/' + test_id, function(data) {
            selected['database_id'] = data['database_id'];
            selected['schedule_id'] = data['schedule_id'];
            selected['test_type_id'] = data['test_type_id'];

            $('#test-id').val(data['test_id']);
            $('#test-name').val(data['name']);
            $('#test-lastrun').val(data['lastrun']);
            $('#test-sql').val(data['sql']);
            $('#test-python').val(data['python']);
        });
        $.getJSON('j/database', function(data) {
            $('#test-database').html('');
            $.each(data, function() {
                var option = $("<option />").val(this.database_id).text(this.name);
                if (selected['database_id'] == this.database_id) {
                    option.attr('selected', 'selected');
                }
                $('#test-database').append(option);
            });
        });
        $.getJSON('j/schedule', function(data) {
            $('#test-schedule').html('');
            $.each(data, function() {
                var option = $("<option />").val(this.schedule_id).text(this.name);
                if (selected['schedule_id'] == this.schedule_id) {
                    option.attr('selected', 'selected');
                }
                $('#test-schedule').append(option);
            });
        });
        $.getJSON('j/test-type', function(data) {
            $('#test-type').html('');
            $.each(data, function() {
                var option = $("<option />").val(this.test_type_id).text(this.name);
                if (selected['test_type_id'] == this.test_type_id) {
                    option.attr('selected', 'selected');
                }
                $('#test-type').append(option);
            });
        });
        $('#test-detail').modal({
            backdrop: true,
            keyboard: true
        }).css({
           'width': function () { 
               return ($(document).width() * .9) + 'px';  
           },
           'margin-left': function () { 
               return -($(this).width() / 2); 
           }
        });
    },
    saveTest: function(testForm) {
        url = 'j/test/' + testForm.find('#test-id').val();
        data = {
            'name':         testForm.find('#test-name').val(),
            'schedule_id':  testForm.find('#test-schedule').val(),
            'database_id':  testForm.find('#test-database').val(),
            'test_type_id': testForm.find('#test-type').val(),
            'sql':          testForm.find('#test-sql').val(),
            'python':       testForm.find('#test-python').val()
        }
        $.ajax({
            type: 'POST',
            url: url,
            data: data,
            success: function(data, status, jq) {
                if (data['result'] == 'success') {
                    showResult(data);
                } else {
                    $('#test-detail-alert .alert-heading').html('Save Failed!');
                    $('#test-detail-alert .alert-body').html(data['message']);
                    $('#test-detail-alert').show();
                }
            },
            dataType: 'json'
        });
    }
 };

$(document).ready(function() {
    $('#firstload').alert('close');
    site = new Pq();
    site.loadAll();
    $('div#tests').show();

    /***
     * Navigation 
     ***/
    $('.nav li a').click(function() {
        var page = $(this).attr('href');
        $('.page').hide();
        $(page).show();
        fakeUrl(page);
        $('.nav .tab').removeClass('active');
        pMatch = page.match(/\#([A-Za-z0-9\-].*)/);
        console.log(pMatch[0] + '-tab');
        $(pMatch[0] + '-tab').addClass('active');
    });
    
    /***
     * Display
     ***/
    // keep code textareas the right size
    $('textarea.code').change(resizeCodeTextarea).keydown(resizeCodeTextarea);

    /***
     * Operations
     ***/
    $('#test-detail-form').submit(function() {
        site.saveTest($('#test-detail-form'));
        return false;
    });
});