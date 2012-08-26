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
        linecount += Math.ceil( l / cols );
    });
    if (linecount > maxrows) { linecount = maxrows; }
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
    login: function(username, password) {
        data = {
            'username': username,
            'password': password
        };
        $.ajax({
            type: 'POST',
            url: '/login',
            data: data,
            success: function(data, status, jq) {
                if (data['result'] == 'success') {
                    window.location = '/';
                } else {
                    $('#login-alert').alert();
                    $('#login-alert .alert-heading').html('Login Failed!');
                    $('#login-alert .alert-body').html(data['message']);
                    $('#login-alert').removeClass('hide') 
                }
            },
            dataType: 'json'
        });
    },
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

            $('table#testlist').tablesorter({
                cssHeader: 'sort',
                cssAsc: 'sort asc',
                cssDesc: 'sort desc',
                headers: { 0: { sorter: false} }
            });
        });
    },
    loadDatabases: function() {
        $.getJSON('j/database', function(data) {
            var html = '';
            $('#test-database').html('');
            $('#test-database').append($("<option />").val(-1).text(''));
            $.each(data, function(key, val) {
                html += '<tr id="' + val['database_id'] + '">';
                html += '<td><input type="checkbox" id="database_id-' + val['database_id'] + '" /></td>';
                html += '<td><a onclick="site.getDatabaseDetail(' + val['database_id'] + '); fakeUrl(\'#database:' + val['database_id'] + '\'); return false;" href="#database:' + val['database_id'] + '">' + val['database_id'] + '</a></td>'
                html += '<td><a onclick="site.getDatabaseDetail(' + val['database_id'] + '); fakeUrl(\'#database:' + val['database_id'] + '\'); return false;" href="#database:' + val['database_id'] + '">' + val['name'] + '</a></td>';
                html += '<td>' + val['username'] + '</td>';
                html += '<td>' + val['hostname'] + ':' + val['port'] + '</td>';
                html += '<td>' + val['active'] + '</td>';
                html += '</tr>';

                // Test detail dropdown
                var option = $("<option />").val(this.database_id).text(this.name);
                $('#test-database').append(option);
            });

            $('table#databaselist tbody').html(html);

            $('table#databaselist').tablesorter({
                cssAsc: 'sort asc',
                cssDesc: 'sort desc',
                cssHeader: 'sort',
                headers: { 0: { sorter: false} }
            });
        });
    },
    loadUsers: function() {
        $.getJSON('j/user', function(data) {
            var html = '';

            $.each(data, function(key, val) {
                html += '<tr id="' + val['user_id'] + '">';
                html += '<td><input type="checkbox" id="user_id-' + val['user_id'] + '" /></td>';
                html += '<td><a onclick="site.getUserDetail(' + val['user_id'] + '); fakeUrl(\'#user:' + val['user_id'] + '\'); return false;" href="#user:' + val['user_id'] + '">' + val['user_id'] + '</a></td>';
                html += '<td><a onclick="site.getUserDetail(' + val['user_id'] + '); fakeUrl(\'#user:' + val['user_id'] + '\'); return false;" href="#user:' + val['user_id'] + '">' + val['username'] + '</a></td>';
                html += '<td>' + val['email'] + '</td>';
                html += '</tr>';
            });

            $('table#userlist tbody').html(html);

            $('table#userlist').tablesorter({
                cssAsc: 'sort asc',
                cssDesc: 'sort desc',
                cssHeader: 'sort',
                headers: { 0: { sorter: false} }
            });
        });
    },
    loadLogs: function(page) {
        if (!page) { page = 1; }
        currentPage = page;

        url = 'j/log?total=50&page=' + page;
        $.getJSON(url, function(data) {
            var html = '';

            /*** Generate the pager **/
            var totalPages = data['meta']['pages'];

            // Figure out the pages we want to display in the pager
            if (totalPages < 6) {
                var pages = []
                for (i=1;i<=totalPages;i++) {
                    pages.push(i);
                }
            } else if (currentPage < 3) {
                var pages = [1,2,3,4,5];
            } else {
                var pages = [page - 2, page - 1, page];
                if (totalPages >= page + 1) {
                    pages.push(page + 1);
                }
                if (totalPages >= page + 2) {
                    pages.push(page + 2);
                }
            }

            var disablePages = '';
            var disableNext = '';
            var disablePrev = '';

            // figure out if we need to disable any congrols
            // and what the next and prev is
            if (totalPages == 1) { disablePages = 'disabled'; }
            if (currentPage < totalPages) { nextPage = currentPage + 1; } else { disableNext = 'disabled'; }
            if (currentPage == 1) { disablePrev = 'disabled'; nextPage = currentPage + 1; }

            // generate the pager html
            var pagerHtml = '<ul><li class="' + disablePages + ' ' + disablePrev + '"><a href="#">&#171;</a></li>';
            $.each(pages, function(key, val) {
                if (val == currentPage) {
                    css = 'disabled';
                } else { css = ''; }
                pagerHtml += '<li class="' + css + '"><a href="#logs" onclick="site.loadLogs(' + val + ');">' + val + '</a></li>';
            });
            pagerHtml += '<li class="' + disablePages + ' ' + disableNext + '"><a href="#" onclick="site.loadLogs(' + nextPage + ');">&#187;</a></li></ul>'

            // Populate the logs page
            $.each(data['logs'], function(key, val) {
                css = '';
                if (val['log_type_id'] == 2) {
                    css = 'warning';
                } else if (val['log_type_id'] == 3) {
                    css = 'error';
                }
                html += '<tr id="' + val['log_id'] + '" class="' + css + '">';
                html += '<td>' + val['log_id'] + '</td>';
                html += '<td>' + val['log_type'] + '</td>';
                html += '<td><a onclick="site.getTestDetail(' + val['test_id'] + '); return false;" href="#test:' + val['test_id'] + '" href="#">' + val['test_name'] + '</a></td>';
                html += '<td>' + val['message'] + '</td>';
                html += '<td>' + val['stamp'] + '</td>';
                html += '<td>' + val['notify'] + '</td>';
                html += '</tr>';
            });

            // display generated html
            $('table#loglist tbody').html(html);
            $('#logs .pagination').html(pagerHtml);
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
        this.loadLogs();
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
                $('#test-cc').val(data['cc']);
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
        resizeCodeTextarea($('textarea.code'));
    },
    saveTest: function(testForm) {
        url = 'j/test/' + testForm.find('#test-id').val();
        data = {
            'name':         testForm.find('#test-name').val(),
            'schedule_id':  testForm.find('#test-schedule').val(),
            'database_id':  testForm.find('#test-database').val(),
            'test_type_id': testForm.find('#test-type').val(),
            'cc':           testForm.find('#test-cc').val(),
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
    deleteTest: function(test_id) {
        if (test_id) {
            $.ajax({
                type: 'DELETE',
                url: 'j/test/' + test_id,
                success: function(data, status, jq) {
                    showResult(data);
                },
                dataType: 'json'
            });
        }
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

        url = 'j/user';
        data = {
            'user_id':      testForm.find('#user-id').val(),
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
                    $('#user-detail-alert .alert-body').html(data['message']);
                    $('#user-detail-alert').removeClass('hide') 
                }
            },
            dataType: 'json'
        });
    },
    deleteUser: function(user_id) {
        if (user_id) {
            $.ajax({
                type: 'DELETE',
                url: 'j/user/' + user_id,
                success: function(data, status, jq) {
                    showResult(data);
                },
                dataType: 'json'
            });
        }
    },
    getDatabaseDetail: function(database_id) {
        var database_id = database_id || null;
        // If there's no database_id, assume we're adding a new one
        if (database_id) {
            $.getJSON('j/database/' + database_id, function(data) {
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
        url = 'j/database';
        data = {
            'database_id':  testForm.find('#database-id').val(),
            'name':         testForm.find('#database-name').val(),
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
    },
    deleteDatabase: function(database_id) {
        if (database_id) {
            $.ajax({
                type: 'DELETE',
                url: 'j/database/' + database_id,
                success: function(data, status, jq) {
                    showResult(data);
                },
                dataType: 'json'
            });
        }
    },
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

    loc = String(window.location);
    pMatch = loc.match(/\#([A-Za-z0-9\-]+):*([0-9]*)/);
    if (pMatch) {
        if (pMatch[1] == 'test-detail') {
            $('#tests').show();
            $('.nav .tab').removeClass('active');
            $('#tests-tab').addClass('active');
            site.getTestDetail(pMatch[2]);
        } else if (pMatch[1] == 'database') {
            $('#databases').show();
            $('.nav .tab').removeClass('active');
            $('#databasess-tab').addClass('active');
            site.getDatabaseDetail(pMatch[2]);
        } else if (pMatch[1] == 'user') {
            $('#users').show();
            $('.nav .tab').removeClass('active');
            $('#users-tab').addClass('active');
            site.getUserDetail(pMatch[2]);
        } else if (pMatch[0]) {
            $(pMatch[0]).show();
            $('.nav .tab').removeClass('active');
            $(pMatch[0] + '-tab').addClass('active');
        } else  {
            $('div#tests').show();
        }
    } else  {
        $('div#tests').show();
    }

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
        $(pMatch[0] + '-tab').addClass('active');
    });
    
    /***
     * Display
     ***/
    // keep code textareas the right size
    $('textarea.code').focus(resizeCodeTextarea).change(resizeCodeTextarea).keydown(resizeCodeTextarea);

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
        site.getTestDetail();
        $(this).button('reset');
    });
    $('#tests .btn-delete-test').button();
    $('#tests .btn-delete-test').click(function() {
        $(this).button('loading');
        $('#tests input[type=checkbox]').each(function() {
            if (!$(this).hasClass('check-all')) {
                if ($(this).is(':checked')) {
                    var id = $(this).attr('id');
                    var idPat = /test_id-([0-9]+)/;
                    var matches = id.match(idPat);
                    if (matches) {
                        var test_id = matches[1];
                        site.deleteTest(test_id);
                    }
                }
            }
        });
        $(this).button('reset');
    });
    $('#users .btn-add-user').button();
    $('#users .btn-add-user').click(function() {
        $(this).button('loading');
        site.getUserDetail();
        $(this).button('reset');
    });
    $('#users .btn-delete-user').button();
    $('#users .btn-delete-user').click(function() {
        $(this).button('loading');
        $('#users input[type=checkbox]').each(function() {
            if (!$(this).hasClass('check-all')) {
                if ($(this).is(':checked')) {
                    var id = $(this).attr('id');
                    var idPat = /user_id-([0-9]+)/;
                    var matches = id.match(idPat);
                    if (matches) {
                        var user_id = matches[1];
                        site.deleteUser(user_id);
                    }
                }
            }
        });
        $(this).button('reset');
    });
    $('#databases .btn-add-database').button();
    $('#databases .btn-add-database').click(function() {
        $(this).button('loading');
        site.getDatabaseDetail();
        $(this).button('reset');
    });
    $('#databases .btn-delete-database').button();
    $('#databases .btn-delete-database').click(function() {
        $(this).button('loading');
        $('#databases input[type=checkbox]').each(function() {
            if (!$(this).hasClass('check-all')) {
                if ($(this).is(':checked')) {
                    var id = $(this).attr('id');
                    var idPat = /database_id-([0-9]+)/;
                    var matches = id.match(idPat);
                    if (matches) {
                        var database_id = matches[1];
                        site.deleteDatabase(database_id);
                    }
                }
            }
        });
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
    $('#login-form #username').focus();
    $('#login-form').submit(function() {
        site.login($('#login-form #username').val(), $('#login-form #password').val());
        return false;
    });

    /***
     * Validation
     ***/
    v = new PqValid()
    $.validator.addMethod("uniqueUser", function(value, element) { 
        return this.optional(element) || v.checkUsername(value); 
    }, "Username must be unique.");
    if ($("#user-detail-form").length > 0) {
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
    }
});