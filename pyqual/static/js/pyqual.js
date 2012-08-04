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
                html += '<td><input type="checkbox" id="test_id-' + val['test_id'] + '" /></td>';
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
            $('#test-database').html('');
            $('#test-database').append($("<option />").val(-1).text(''));
            $.each(data, function(key, val) {
                html += '<tr id="' + val['database_id'] + '">';
                html += '<td><a onclick="site.getDatabaseDetail(' + val['database_id'] + '); return false;" href="#database:' + val['database_id'] + '">' + val['database_id'] + '</a></td>'
                html += '<td><a onclick="site.getDatabaseDetail(' + val['database_id'] + '); return false;" href="#database:' + val['database_id'] + '">' + val['name'] + '</a></td>';
                html += '<td>' + val['username'] + '</td>';
                html += '<td>' + val['hostname'] + ':' + val['port'] + '</td>';
                html += '<td>' + val['active'] + '</td>';
                html += '</tr>';

                // Test detail dropdown
                var option = $("<option />").val(this.database_id).text(this.name);
                $('#test-database').append(option);
            });

            $('table#databaselist tbody').html(html);
        });
    },
    loadUsers: function() {
        $.getJSON('j/user', function(data) {
            var html = '';

            $.each(data, function(key, val) {
                html += '<tr id="' + val['user_id'] + '">';
                html += '<td><a onclick="site.getUserDetail(' + val['user_id'] + '); return false;" href="#user:' + val['user_id'] + '">' + val['user_id'] + '</a></td>';
                html += '<td><a onclick="site.getUserDetail(' + val['user_id'] + '); return false;" href="#user:' + val['user_id'] + '">' + val['username'] + '</a></td>';
                html += '<td>' + val['email'] + '</td>';
                html += '</tr>';
            });

            $('table#userlist tbody').html(html);
        });
    },
    loadSchedules: function() {
        $.getJSON('j/schedule', function(data) {
            $('#test-schedule').html('');
            $('#test-schedule').append($("<option />").val(-1).text(''));
            $.each(data, function() {
                var option = $("<option />").val(this.schedule_id).text(this.name);
                $('#test-schedule').append(option);
            });
        });
    },
    loadTestTypes: function() {
        $.getJSON('j/test-type', function(data) {
            $('#test-type').html('');
            $('#test-type').append($("<option />").val(-1).text(''));
            $.each(data, function() {
                var option = $("<option />").val(this.test_type_id).text(this.name);
                $('#test-type').append(option);
            });
        });
    },
    loadAll: function() {
        this.loadTests();
        this.loadDatabases();
        this.loadUsers();
        this.loadSchedules();
        this.loadTestTypes();
    },
    getTestDetail: function(test_id) {
        var selected = {};
        var test_id = test_id || null;
        // If there's no test_id, assume we're adding a new one
        if (test_id) {
            $.getJSON('j/test/' + test_id, function(data) {
                selected['database_id'] = data['database_id'];
                selected['schedule_id'] = data['schedule_id'];
                selected['test_type_id'] = data['test_type_id'];
                //option.attr('selected', 'selected');
                $('#test-id').val(data['test_id']);
                $('#test-name').val(data['name']);
                $('#test-lastrun').val(data['lastrun']);
                $('#test-sql').val(data['sql']);
                $('#test-python').val(data['python']);
                $('#test-database').val(data['database_id']);
                $('#test-schedule').val(data['schedule_id']);
                $('#test-type').val(data['test_type_id']);
            });
        } else {
            $('#test-detail-form input, #test-detail-form textarea, #test-detail-form select').val('');
        }
        
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
                    $('#test-detail').modal('hide');
                } else {
                    $('#test-detail-alert').alert();
                    $('#test-detail-alert .alert-heading').html('Save Failed!');
                    $('#test-detail-alert .alert-body').html(data['message']);
                    $('#test-detail-alert').removeClass('hide') 
                }
            },
            dataType: 'json'
        });
    },
    getUserDetail: function(user_id) {
        var selected = {};
        var user_id = user_id || null;
        // If there's no test_id, assume we're adding a new one
        if (user_id) {
            $.getJSON('j/user/' + user_id, function(data) {
                $('#user-id').val(data['user_id']);
                $('#user-username').val(data['username']);
                $('#user-origUsername').val(data['username']);
                $('#user-email').val(data['email']);
            });
        } else {
            $('#user-detail-form input, #user-detail-form textarea, #user-detail-form select').val('');
        }
        
        $('#user-detail').modal({
            backdrop: true,
            keyboard: true
        });
    },
    saveUser: function(testForm) {
        // validation
        var valid = true;
        testForm.find('#user-password').val() != testForm.find('#user-password2').val() ? valid = false : true;
        isNaN(parseFloat(testForm.find('#user-id').val())) || !isFinite(testForm.find('#user-id').val()) ? valid = false : true;

        url = 'j/user/' + testForm.find('#user-id').val();
        data = {
            'username':     testForm.find('#user-username').val(),
            'email':        testForm.find('#user-email').val(),
            'password':     testForm.find('#user-password').val()
        }
        $.ajax({
            type: 'POST',
            url: url,
            data: data,
            success: function(data, status, jq) {
                if (data['result'] == 'success') {
                    showResult(data);
                    $('#user-detail').modal('hide');
                } else {
                    $('#user-detail-alert').alert();
                    $('#user-detail-alert .alert-heading').html('Save Failed!');
                    $('#usert-detail-alert .alert-body').html(data['message']);
                    $('#user-detail-alert').removeClass('hide') 
                }
            },
            dataType: 'json'
        });
    },
    getDatabaseDetail: function(database_id) {
        var database_id = database_id || null;
        // If there's no database_id, assume we're adding a new one
        if (database_id) {
            $.getJSON('j/database/' + database_id, function(data) {
                alert(data['database_id']);
                $('#database-id').val(data['database_id']);
                $('#database-name').val(data['name']);
                $('#database-username').val(data['username']);
                $('#database-password').val(data['password']);
                $('#database-hostname').val(data['hostname']);
                $('#database-port').val(data['port']);
                $('#database-active').val(data['active']);
            });
        } else {
            $('#database-detail-form input, #database-detail-form textarea, #database-detail-form select').val('');
        }
        
        $('#database-detail').modal({
            backdrop: true,
            keyboard: true
        });
    },
    saveDatabase: function(testForm) {
        url = 'j/database/' + testForm.find('#database-id').val();
        data = {
            'database_id':  testForm.find('#database-id').val(),
            'name':         testForm.find('#databaset-name').val(),
            'username':     testForm.find('#database-username').val(),
            'password':     testForm.find('#database-password').val(),
            'hostname':     testForm.find('#database-hostname').val(),
            'port':         testForm.find('#database-port').val(),
            'active':       testForm.find('#database-active').val()
        }
        $.ajax({
            type: 'POST',
            url: url,
            data: data,
            success: function(data, status, jq) {
                if (data['result'] == 'success') {
                    showResult(data);
                    $('#database-detail').modal('hide');
                } else {
                    $('#database-detail-alert').alert();
                    $('#database-detail-alert .alert-heading').html('Save Failed!');
                    $('#database-detail-alert .alert-body').html(data['message']);
                    $('#database-detail-alert').removeClass('hide') 
                }
            },
            dataType: 'json'
        });
    }
 };
 var PqValid = function () {
    this.version = Pq.version;
 };
 PqValid.prototype = {
    checkUsername: function(username) {
        var available = false;
        $.ajax({
            url: 'j/check-user/' + username, 
            data: {},
            async: false,
            success: function(data) {
                available = data['available'];
            },
            dataType: 'json'
        });
        return available;
    },
    checkPassword: function(pass1, pass2) {
        return pass1 == pass2 ? true : false;
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
     * Behavior
     ***/
    $('textarea.code').tabby();

    /***
     * Operations
     ***/
    $('#tests .btn-add-test').button();
    $('#tests .btn-add-test').click(function() {
        $(this).button('loading');
        /*$('#test-detail-form input').each(function() {
            $(this).val('');
        });*/
        site.getTestDetail();
        //$('#test-detail').modal();
        //$('#test-detail').removeClass('hide');
        $(this).button('reset');
    });
    $('#test-detail-form').submit(function() {
        site.saveTest($('#test-detail-form'));
        return false;
    });
    $('#database-detail-form').submit(function() {
        site.saveDatabase($('#database-detail-form'));
        return false;
    });
    $('#user-detail-form').submit(function() {
        site.saveUser($('#user-detail-form'));
        return false;
    });

    /***
     * Validation
     ***/
    v = new PqValid()
    $.validator.addMethod("uniqueUser", function(value, element) { 
        return this.optional(element) || v.checkUsername(value); 
    }, "Username must be unique.");
    $("#user-detail-form").validate({
        /*errorContainer: '#errors',
        errorLabelContainer: '#errors ul',
        wrapper: 'li',*/
        debug: true,
        rules: {
            'user-username': {
                required: true,
                uniqueUser: {
                    depends: function() {
                        if ($('#user-id').val() != '' && $('#user-origUsername').val() == $('#user-username').val()) {
                            return false
                        } else {
                            return true
                        }
                    }
                }
            },
            'user-email': {
                required: true,
                email: true
            },
            'user-password': {
                /*depends: v.checkPassword($('#user-password').val(), $('#user-password2').val())*/
                equalTo: '#user-password2'
            },
            'user-password2': {
                /*depends: v.checkPassword($('#user-password').val(), $('#user-password2').val())*/
                equalTo: '#user-password'
            }
        },
        messages: {
            'user-username': "Username is required and must be unique.",
            'user-password': 'Passwords must match.'
        }
    });
});