import pytest
import time
import platform
import datetime
import sys

from _pytest.runner import pytest_runtest_setup
from _pytest.runner import runtestprotocol
from _pytest.runner import pytest_runtest_teardown

_total = 0
_executed = 0
_pass = 0
_fail = 0
_skip = 0
_error = 0
_xpass = 0
_xfail = 0
_current_error = ""
_suite_name = None
_test_name = None
_test_status = None
_test_start_time = None
_excution_time = 0
_test_metrics_content = ""
_suite_metrics_content = ""
_duration = 0
_previous_suite_name = "None"
_initial_trigger = True
_spass_tests = 0
_sfail_tests = 0
_sskip_tests = 0
_serror_tests = 0
_sxfail_tests = 0
_sxpass_tests = 0

def pytest_addoption(parser):
    group = parser.getgroup('metrics')
    group.addoption(
        '--menable',
        action='store',
        dest='menable',
        default="False",
        help='Enable or disable metrics report'
    )
    group.addoption(
        '--mlogo',
        action='store',
        dest='mlogo',
        default="https://i.ibb.co/k4YktNP/testingfox.jpg",
        help='Logo to use in metrics report'
    )

def pytest_runtest_setup(item):
    global _test_start_time
    _test_start_time = time.time()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    global _suite_name
    _suite_name = rep.nodeid.split("::")[0]

    if _initial_trigger :
        update_previous_suite_name()
        set_initial_trigger()
    
    if str(_previous_suite_name) != str(_suite_name):
        append_suite_metrics_row(_previous_suite_name)
        update_previous_suite_name()
        reset_counts()
    else:
        update_counts(rep)
    
    if rep.when == "call" and rep.passed:
        if hasattr(rep, "wasxfail"):
            increment_xpass()
            update_test_status("xPASS")
            global _current_error
            update_test_error("")
        else:
            increment_pass()
            update_test_status("PASS")
            update_test_error("")
    
    if rep.failed:
        if getattr(rep, "when", None) == "call":
            if hasattr(rep, "wasxfail"):
                increment_xpass()
                update_test_status("xPASS")
                update_test_error("")
            else:
                increment_fail()
                update_test_status("FAIL")
                if rep.longrepr:
                    for line in rep.longreprtext.splitlines():
                        exception = line.startswith("E   ")
                        if exception:
                            update_test_error(line.replace("E    ",""))
        else:
            increment_error()
            update_test_status("ERROR")
            if rep.longrepr:
                for line in rep.longreprtext.splitlines():
                    update_test_error(line)
    
    if rep.skipped:
        if hasattr(rep, "wasxfail"):
            increment_xfail()
            update_test_status("xFAIL")
            if rep.longrepr:
                for line in rep.longreprtext.splitlines():
                    exception = line.startswith("E   ")
                    if exception:
                        update_test_error(line.replace("E    ",""))
        else:
            increment_skip()
            update_test_status("SKIP")
            if rep.longrepr:
                for line in rep.longreprtext.splitlines():
                    update_test_error(line)
        
def pytest_runtest_teardown(item, nextitem):

    _test_end_time = time.time()

    global _test_name
    _test_name = item.name

    global _duration
    _duration = _test_end_time - _test_start_time

    # create list to save content
    append_test_metrics_row()

def pytest_sessionfinish(session):
    append_suite_metrics_row(_suite_name)
    reset_counts()
    
@pytest.hookimpl(hookwrapper=True)
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    yield

    if config.option.menable == "True":

        global _excution_time
        _excution_time = time.time() - terminalreporter._sessionstarttime
        
        global _total
        _total =  _pass + _fail + _xpass + _xfail + _skip + _error

        global _executed
        _executed = _pass + _fail + _xpass + _xfail

        # create live logs report and close
        live_logs_file = open('pytest_metrics.html','w')
        message = get_updated_template_text(str(config.option.mlogo))
        live_logs_file.write(message)
        live_logs_file.close()

def append_suite_metrics_row(name):
    suite_row_text = """
        <tr>
            <td style="width: 25%;">__sname__</td>
            <td style="width: 10%; text-align:center;">__spass__</td>
            <td style="width: 10%; text-align:center;">__sfail__</td>
            <td style="width: 10%; text-align:center;">__sskip__</td>
            <td style="width: 10%; text-align:center;">__sxpass__</td>
            <td style="width: 10%; text-align:center;">__sxfail__</td>
            <td style="width: 10%; text-align:center;">__serror__</td>
        </tr>
    """
    suite_row_text = suite_row_text.replace("__sname__",str(name))
    suite_row_text = suite_row_text.replace("__spass__",str(_spass_tests))
    suite_row_text = suite_row_text.replace("__sfail__",str(_sfail_tests))
    suite_row_text = suite_row_text.replace("__sskip__",str(_sskip_tests))
    suite_row_text = suite_row_text.replace("__sxpass__",str(_sxpass_tests))
    suite_row_text = suite_row_text.replace("__sxfail__",str(_sxfail_tests))
    suite_row_text = suite_row_text.replace("__serror__",str(_serror_tests))

    global _suite_metrics_content
    _suite_metrics_content += suite_row_text

def append_test_metrics_row():
    test_row_text = """
        <tr>
            <td style="width: 25%;">__sname__</td>
            <td style="width: 25%;">__name__</td>
            <td style="width: 10%; text-align:center;">__stat__</td>
            <td style="width: 10%; text-align:center;">__dur__</td>
            <td style="width: 30%;">__msg__</td>
        </tr>
    """
    test_row_text = test_row_text.replace("__sname__",str(_suite_name))
    test_row_text = test_row_text.replace("__name__",str(_test_name))
    test_row_text = test_row_text.replace("__stat__",str(_test_status))
    test_row_text = test_row_text.replace("__dur__",str(round(_duration,2)))
    test_row_text = test_row_text.replace("__msg__",str(_current_error))

    global _test_metrics_content
    _test_metrics_content += test_row_text

def get_updated_template_text(logo_url):
    template_text = get_html_template()
    template_text = template_text.replace("__custom_logo__", logo_url)
    template_text = template_text.replace("__execution_time__", str(round(_excution_time, 2)))
    template_text = template_text.replace("__executed_by__", str(platform.uname()[1]))
    template_text = template_text.replace("__os_name__", str(platform.uname()[0]))
    template_text = template_text.replace("__python_version__", str(sys.version.split(' ')[0]))
    template_text = template_text.replace("__generated_date__", str(datetime.datetime.now().strftime("%b %d %Y, %H:%M")))
    template_text = template_text.replace("__total__", str(_total))
    template_text = template_text.replace("__executed__", str(_executed))
    template_text = template_text.replace("__pass__", str(_pass))
    template_text = template_text.replace("__fail__", str(_fail))
    template_text = template_text.replace("__skip__", str(_skip))
    template_text = template_text.replace("__error__", str(_error))
    template_text = template_text.replace("__xpass__", str(_xpass))
    template_text = template_text.replace("__xfail__", str(_xfail))
    template_text = template_text.replace("__suite_metrics_row__", str(_suite_metrics_content))
    template_text = template_text.replace("__test_metrics_row__", str(_test_metrics_content))
    return template_text

def set_initial_trigger():
    global _initial_trigger
    _initial_trigger = False

def update_previous_suite_name():
    global _previous_suite_name
    _previous_suite_name = _suite_name

def update_counts(rep):
    global _sfail_tests, _spass_tests, _sskip_tests, _serror_tests, _sxfail_tests, _sxpass_tests
    
    if rep.when == "call" and rep.passed:
        if hasattr(rep, "wasxfail"):
            _sxpass_tests += 1
        else:
            _spass_tests += 1
    
    if rep.failed:
        if getattr(rep, "when", None) == "call":
            if hasattr(rep, "wasxfail"):
                _sxpass_tests += 1
            else:
                _sfail_tests += 1
        else:
            _serror_tests += 1
    
    if rep.skipped:
        if hasattr(rep, "wasxfail"):
            _sxfail_tests += 1
        else:
            _sskip_tests += 1

def reset_counts():
    global _sfail_tests, _spass_tests, _sskip_tests, _serror_tests, _sxfail_tests, _sxpass_tests
    _spass_tests  = 0
    _sfail_tests  = 0
    _sskip_tests = 0
    _serror_tests = 0
    _sxfail_tests = 0
    _sxpass_tests = 0

def update_test_error(msg):
    global _current_error
    _current_error = msg

def update_test_status(status):
    global _test_status
    _test_status = status

def increment_xpass():
    global _xpass
    _xpass += 1

def increment_xfail():
    global _xfail
    _xfail += 1

def increment_pass():
    global _pass
    _pass += 1

def increment_fail():
    global _fail
    _fail += 1

def increment_skip():
    global _skip
    _skip += 1

def increment_error():
    global _error
    _error += 1

def get_html_template():
	my_template = """
	<!DOCTYPE doctype html>
    <html lang="en">
    <head>
        <link href="https://img.icons8.com/flat_round/64/000000/bar-chart.png" rel="shortcut icon" type="image/x-icon" />
        <title>Pytest Metrics</title>
        <meta charset="utf-8" />
        <meta content="width=device-width, initial-scale=1" name="viewport" />
        <link href="https://cdn.datatables.net/1.10.19/css/jquery.dataTables.min.css" rel="stylesheet" />
        <link href="https://cdn.datatables.net/buttons/1.5.2/css/buttons.dataTables.min.css" rel="stylesheet" />
        <link href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.1.3/css/bootstrap.min.css" rel="stylesheet" />
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css" rel="stylesheet" />
        <script src="https://code.jquery.com/jquery-3.3.1.js" type="text/javascript">
        </script>
        <!-- Bootstrap core Googleccharts -->
        <script src="https://www.gstatic.com/charts/loader.js" type="text/javascript">
        </script>
        <script type="text/javascript">
            google.charts.load('current', {
                        packages: ['corechart']
                    });
        </script>
        <!-- Bootstrap core Datatable-->
        <script src="https://cdn.datatables.net/1.10.19/js/jquery.dataTables.min.js" type="text/javascript">
        </script>
        <script src="https://cdn.datatables.net/buttons/1.5.2/js/dataTables.buttons.min.js" type="text/javascript">
        </script>
        <script src="https://cdn.datatables.net/buttons/1.5.2/js/buttons.flash.min.js" type="text/javascript">
        </script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.1.3/jszip.min.js" type="text/javascript">
        </script>
        <script src="https://cdn.datatables.net/buttons/1.5.2/js/buttons.html5.min.js" type="text/javascript">
        </script>
        <script src="https://cdn.datatables.net/buttons/1.5.2/js/buttons.print.min.js" type="text/javascript">
        </script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.0/js/bootstrap.min.js"></script>
        <style>
            body {
                font-family: -apple-system, sans-serif;
            }
                    
            .sidenav {
                height: 100%;
                width: 220px;
                position: fixed;
                z-index: 1;
                top: 0;
                left: 0;
                background-color: white;
                overflow-x: hidden;
                border-style: ridge;
            }
            
            .sidenav a {
                padding: 12px 10px 8px 12px;
                text-decoration: none;
                font-size: 18px;
                color: Black;
                display: block;
            }
            
            .main {
                padding-top: 10px;
            }
            
            @media screen and (max-height: 450px) {
                .sidenav {
                    padding-top: 15px;
                }
                .sidenav a {
                    font-size: 18px;
                }
            }
            
            .tile {
                width: 100%;
                float: left;
                margin: 0px;
                list-style: none;
                font-size: 30px;
                color: #FFF;
                -moz-border-radius: 5px;
                -webkit-border-radius: 5px;
                margin-bottom: 5px;
                position: relative;
                text-align: center;
                color: white!important;
            }
            
            .tile.tile-fail {
                background: #f44336!important;
            }
            
            .tile.tile-pass {
                background: #4CAF50!important;
            }
            
            .tile.tile-info {
                background: #009688!important;
            }
            
            .tile.tile-head {
                background: #616161!important;
            }
            
            .dt-buttons {
                margin-left: 5px;
            }
            
            .loader {
                position: fixed;
                left: 0px;
                top: 0px;
                width: 100%;
                height: 100%;
                z-index: 9999;
                background: url('https://www.downgraf.com/wp-content/uploads/2014/09/02-loading-blossom-2x.gif') 50% 50% no-repeat rgb(249, 249, 249);
            }
        </style>
    </head>

    </html>

    <body>
        <div class="loader"></div>
        <div class="sidenav">
            <a><img src="__custom_logo__" style="height:25vh;max-width:98%;" /></a>
            <a class="tablink" href="#" id="defaultOpen" onclick="openPage('dashboard', this, 'orange')"> <i class="fa fa-dashboard"></i> Dashboard</a>
            <a class="tablink" href="#" onclick="openPage('suiteMetrics', this, 'orange'); executeDataTable('#sm',5)"> <i class="fa fa-th-large"></i> Suite Metrics</a>
            <a class="tablink" href="#" onclick="openPage('testMetrics', this, 'orange'); executeDataTable('#tm',2)"> <i class="fa fa-list-alt"></i> Test Metrics</a>
            <a class="tablink" href="#" onclick="openPage('statistics', this, 'orange');"> <i class="fa fa-envelope-o"></i> Email</a>
        </div>
        <div class="main col-md-9 ml-sm-auto col-lg-10 px-4">
            <div class="tabcontent" id="dashboard">
                <div class="d-flex flex-column flex-md-row align-items-center p-1 mb-3 bg-light border-bottom shadow-sm">
                    <h5 class="my-0 mr-md-auto font-weight-normal"><i class="fa fa-dashboard"></i> Dashboard</h5>
                    <nav class="my-2 my-md-0 mr-md-3" style="color:red"> <a class="p-2"><b style="color:black;">Execution Time:</b> __execution_time__ s</a>
                        <a class="p-2">
                            <button type="button" class="btn" data-toggle="modal" data-target="#myModal"><i class="fa fa-desktop"></i> View Info</button>
                            <!-- The Modal -->
                            <div class="modal" id="myModal">
                                <div class="modal-dialog">
                                    <div class="modal-content">
                                        <!-- Modal Header -->
                                        <div class="modal-header">
                                            <h4 class="modal-title">Execution Info</h4>
                                            <button type="button" class="close" data-dismiss="modal">&times;</button>
                                        </div>
                                        <!-- Modal body -->
                                        <div class="modal-body">
                                            <table class="table">
                                                <tbody>
                                                    </tr>
                                                    <tr>
                                                        <td>Executed By:</td>
                                                        <td>__executed_by__</td>
                                                    </tr>
                                                    <tr>
                                                        <td>OS Name:</td>
                                                        <td>__os_name__</td>
                                                    </tr>
                                                    <tr>
                                                        <td>Python Version:</td>
                                                        <td>__python_version__</td>
                                                    </tr>
                                                    <tr>
                                                        <td>Generated Time:</td>
                                                        <td>__generated_date__</td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                        <!-- Modal footer -->
                                        <div class="modal-footer">
                                            <button type="button" class="btn btn-danger" data-dismiss="modal">Close</button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </a>
                    </nav>
                </div>
                <div class="row">
                    <div class="col-md-3"> <a class="tile tile-head">__total__<p style="font-size:12px">Total</p></a></div>
                    <div class="col-md-3"> <a class="tile tile-info">__executed__<p style="font-size:12px">Executed</p></a></div>
                    <div class="col-md-3"> <a class="tile tile-pass">__pass__<p style="font-size:12px">Pass</p></a></div>
                    <div class="col-md-3"> <a class="tile tile-fail">__fail__<p style="font-size:12px">Fail</p></a></div>
                </div>
                <div class="row">
                    <div class="col-md-3"> <a class="tile tile-head">__skip__<p style="font-size:12px">Skip</p></a></div>
                    <div class="col-md-3"> <a class="tile tile-info">__error__<p style="font-size:12px">Error</p></a></div>
                    <div class="col-md-3"> <a class="tile tile-pass">__xpass__<p style="font-size:12px">xPass</p></a></div>
                    <div class="col-md-3"> <a class="tile tile-fail">__xfail__<p style="font-size:12px">xFail</p></a></div>
                </div>
            
                <hr/>
                <div class="row">
                    <div class="col-md-4" style="background-color:white;height:350px;width:auto;border:groove;"> <span style="font-weight:bold">Test Status:</span>
                        <div id="testChartID" style="height:280px;width:auto;"></div>
                    </div>
                    <div class="col-md-8" style="background-color:white;height:350px;width:auto;border:groove;"> <span style="font-weight:bold">Top 5 Suite Failures:</span>
                        <div id="suiteBarID" style="height:300px;width:auto;"></div>
                    </div>
                </div>
                <hr/>
                <div class="row">
                    <div class="col-md-12" style="background-color:white;height:450px;width:auto;border:groove;"> <span style="font-weight:bold">Top 10 Test Performance (sec):</span>
                        <div id="testsBarID" style="height:400px;width:auto;"></div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-12" style="height:25px;width:auto;">
                        <p class="text-muted" style="text-align:center;font-size:9px"> <a href="https://github.com/adiralashiva8/pytest-metrics" target="_blank">pytest-metrics</a>
                        </p>
                    </div>
                </div>
                <script>
                    window.onload = function() {
                        executeDataTable('#sm', 2);
                        executeDataTable('#tm', 3);
                        createBarGraph('#sm', 0, 2, 5, 'suiteBarID', 'Failure ', 'Suite');
                        createPieChart(__pass__, __fail__, __xpass__, __xfail__, 'testChartID', 'Tests Status:');
                        createBarGraph('#tm', 1, 3, 10, 'testsBarID', 'Elapsed Time (s) ', 'Test');
                    };
                </script>
                <script>
                    function openInNewTab(url, element_id) {
                        var element_id = element_id;
                        var win = window.open(url, '_blank');
                        win.focus();
                        $('body').scrollTo(element_id);
                    }
                </script>
            </div>
        
            <div class="tabcontent" id="suiteMetrics">
                <h4><b><i class="fa fa-table"></i> Suite Metrics</b></h4>
                <hr/>
                <table class="table table-striped table-bordered" id="sm">
                    <thead>
                        <tr>
                            <th>Suite</th>
                            <th>Pass</th>
                            <th>Fail</th>
                            <th>Skip</th>
                            <th>xPass</th>
                            <th>xFail</th>
                            <th>Error</th>
                        </tr>
                    </thead>
                    <tbody>
                        __suite_metrics_row__
                    </tbody>
                </table>
                <div class="row">
                    <div class="col-md-12" style="height:25px;width:auto;"></div>
                </div>
            </div>
        <div class="tabcontent" id="testMetrics">
            <h4><b><i class="fa fa-table"></i> Test Metrics</b></h4>
            <hr/>
            <table class="table table-striped table-bordered" id="tm">
                <thead>
                    <tr>
                        <th>Suite</th>
                        <th>Test Case</th>
                        <th>Status</th>
                        <th>Time (s)</th>
                        <th>Error Message</th>
                    </tr>
                </thead>
                <tbody>
                    __test_metrics_row__
                </tbody>
            </table>
            <div class="row">
                <div class="col-md-12" style="height:25px;width:auto;"></div>
            </div>
        </div>
        
        <div class="tabcontent" id="statistics">
            <h4><b><i class="fa fa-table"></i> Email Statistics</b></h4>
            <hr/>
            <button class="btn btn-primary active inner" id="create" onclick="this.style.visibility= 'hidden';" role="button"> <i class="fa fa-cogs">
        </i> Generate Statistics Email</button>
            <a class="btn btn-primary active inner" download="message.eml" id="downloadlink" role="button" style="display: none; width: 300px;"> <i class="fa fa-download">
        </i> Click Here To Download Email</a>
        <textarea class="col-md-12" id="textbox" style="height: 400px; padding:1em;">
To: myemail1234@email.com
Subject: Automation Execution Status
X-Unsent: 1
Content-Type: text/html
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Test Email Sample</title>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type"/>
<meta content="IE=edge" http-equiv="X-UA-Compatible"/>
<meta content="width=device-width, initial-scale=1.0 " name="viewport"/>
    <style>
        body {
            background-color:#F2F2F2; 
        }
        body, html, table {
            font-family: Courier New, Arial, sans-serif;
            font-size: 1em; 
        }
        .pastdue { color: crimson; }
        table {
            padding: 5px;
            margin-left: 30px;
            width: 800px;
        }
        thead {
            text-align: center;
            font-size: 1.1em;        
            background-color: #B0C4DE;
            font-weight: bold;
            color: #2D2C2C;
        }
        tbody {
            text-align: center;
        }
        th {
            width: 25%;
            word-wrap:break-word;
        }
    </style>
</head>
<body>
    <p>Hi Team,</p>
    <p>Following are the last build execution status</p>
    <p></p>
    <table>
        <tbody>
            <tr>
                <td style="text-align:left; padding-left:5px;color:#0b6690;">
                    <h2>Pytest Report</h2>
                </td>
                <td style="text-align:right; padding-right:10px;color:#0b6690;">
                    <h3>Duration (s): __execution_time__</h3>
                </td>
            </tr>
        </tbody>
    </table>
    <table>
        <tr>
            <td></td>
        </tr>
    </table>
    <table>
        <tbody>
        <tr>
            <td style="background-color:#616161; color:white; width:25%">
                <table style="width:100%;">
                    <tbody>
                        <tr>
                            <td style="text-align:center; color:white;font-size: 32px;">__total__</td>
                        </tr>
                        <tr>
                            <td style="text-align:center; color:white;font-size: 14px;">Total</td>
                        </tr>
                    </tbody>
                </table>
            </td>
            <td style="background-color:#009688; color:white; width:25%">
                <table style="width:100%;">
                    <tbody>
                        <tr>
                            <td style="text-align:center; color:white;font-size: 32px;">__executed__</td>
                        </tr>
                        <tr>
                            <td style="text-align:center; color:white;font-size: 14px;">Executed</td>
                        </tr>
                    </tbody>
                </table>
            </td>
            <td style="background-color:#4CAF50; color:white; width:25%">
                <table style="width:100%;">
                    <tbody>
                        <tr>
                            <td style="text-align:center; color:white;font-size: 32px;">__pass__</td>
                        </tr>
                        <tr>
                            <td style="text-align:center; color:white;font-size: 14px;">Pass</td>
                        </tr>
                    </tbody>
                </table>
            </td>
            <td style="background-color:#f44336; color:white; width:25%">
                <table style="width:100%;">
                    <tbody>
                        <tr>
                            <td style="text-align:center; color:white;font-size: 32px;">__fail__</td>
                        </tr>
                        <tr>
                            <td style="text-align:center; color:white;font-size: 14px;">Fail</td>
                        </tr>
                    </tbody>
                </table>
            </td>
        </tr>
        <tr>
            <td style="background-color:#616161; color:white; width:25%">
                <table style="width:100%;">
                    <tbody>
                        <tr>
                            <td style="text-align:center; color:white;font-size: 32px;">__skip__</td>
                        </tr>
                        <tr>
                            <td style="text-align:center; color:white;font-size: 14px;">Skip</td>
                        </tr>
                    </tbody>
                </table>
            </td>
            <td style="background-color:#009688; color:white; width:25%">
                <table style="width:100%;">
                    <tbody>
                        <tr>
                            <td style="text-align:center; color:white;font-size: 32px;">__error__</td>
                        </tr>
                        <tr>
                            <td style="text-align:center; color:white;font-size: 14px;">Error</td>
                        </tr>
                    </tbody>
                </table>
            </td>
            <td style="background-color:#4CAF50; color:white; width:25%">
                <table style="width:100%;">
                    <tbody>
                        <tr>
                            <td style="text-align:center; color:white;font-size: 32px;">__xpass__</td>
                        </tr>
                        <tr>
                            <td style="text-align:center; color:white;font-size: 14px;">xPass</td>
                        </tr>
                    </tbody>
                </table>
            </td>
            <td style="background-color:#f44336; color:white; width:25%">
                <table style="width:100%;">
                    <tbody>
                        <tr>
                            <td style="text-align:center; color:white;font-size: 32px;">__xfail__</td>
                        </tr>
                        <tr>
                            <td style="text-align:center; color:white;font-size: 14px;">Fail</td>
                        </tr>
                    </tbody>
                </table>
            </td>
        </tr>
        </tbody>
    </table>
    <table>
        <tr>
            <td></td>
        </tr>
    </table>
    <p>Please refer Pytest Metrics report for detailed statistics.<p>
    <strong>Team QA</strong>
</p></p></body></html></textarea>
        </div>
        </div>
        <script>
            (function() {
                var textFile = null,
                    makeTextFile = function(text) {
                        var data = new Blob([text], {
                            type: 'text/plain'
                        });
                        if (textFile !== null) {
                            window.URL.revokeObjectURL(textFile);
                        }
                        textFile = window.URL.createObjectURL(data);
                        return textFile;
                    };

                var create = document.getElementById('create'),
                    textbox = document.getElementById('textbox');
                create.addEventListener('click', function() {
                    var link = document.getElementById('downloadlink');
                    link.href = makeTextFile(textbox.value);
                    link.style.display = 'block';
                }, false);
            })();
        </script>
        <script>
            function createPieChart(pass_count, fail_count, xpass_count, xfail_count, ChartID, ChartName) {
                var status = [];
                status.push(['Status', 'Percentage']);
                status.push(['PASS', parseInt(pass_count)], ['FAIL', parseInt(fail_count)],
                 ['xPASS', parseInt(xpass_count)], ['xFAIL', parseInt(xfail_count)], );
                var data = google.visualization.arrayToDataTable(status);

                var options = {
                    pieHole: 0.6,
                    legend: 'none',
                    chartArea: {
                        width: "95%",
                        height: "90%"
                    },
                    colors: ['GREEN', 'RED', 'LIMEGREEN', 'FIREBRICK'],
                };

                var chart = new google.visualization.PieChart(document.getElementById(ChartID));
                chart.draw(data, options);
            }
        </script>
        <script>
            function createBarGraph(tableID, keyword_column, time_column, limit, ChartID, Label, type) {
                var status = [];
                css_selector_locator = tableID + ' tbody >tr'
                var rows = $(css_selector_locator);
                var columns;
                var myColors = [
                    '#4F81BC',
                    '#C0504E',
                    '#9BBB58',
                    '#24BEAA',
                    '#8064A1',
                    '#4AACC5',
                    '#F79647',
                    '#815E86',
                    '#76A032',
                    '#34558B'
                ];
                status.push([type, Label, {
                    role: 'annotation'
                }, {
                    role: 'style'
                }]);
                for (var i = 0; i < rows.length; i++) {
                    if (i == Number(limit)) {
                        break;
                    }
                    //status = [];
                    name_value = $(rows[i]).find('td');

                    time = ($(name_value[Number(time_column)]).html());
                    keyword = ($(name_value[Number(keyword_column)]).html()).trim();
                    status.push([keyword, parseFloat(time), parseFloat(time), myColors[i]]);
                }
                var data = google.visualization.arrayToDataTable(status);

                var options = {
                    legend: 'none',
                    chartArea: {
                        width: "92%",
                        height: "75%"
                    },
                    bar: {
                        groupWidth: '90%'
                    },
                    annotations: {
                        alwaysOutside: true,
                        textStyle: {
                            fontName: 'Comic Sans MS',
                            fontSize: 13,
                            bold: true,
                            italic: true,
                            color: "black", // The color of the text.
                        },
                    },
                    hAxis: {
                        textStyle: {
                            fontName: 'Arial',
                            fontSize: 10,
                        }
                    },
                    vAxis: {
                        gridlines: {
                            count: 10
                        },
                        textStyle: {
                            fontName: 'Comic Sans MS',
                            fontSize: 10,
                        }
                    },
                };

                // Instantiate and draw the chart.
                var chart = new google.visualization.ColumnChart(document.getElementById(ChartID));
                chart.draw(data, options);
            }
        </script>
        <script>
            function executeDataTable(tabname, sortCol) {
                var fileTitle;
                switch (tabname) {
                    case "#sm":
                        fileTitle = "SuiteMetrics";
                        break;
                    case "#tm":
                        fileTitle = "TestMetrics";
                        break;
                    default:
                        fileTitle = "metrics";
                }

                $(tabname).DataTable({
                    retrieve: true,
                    "order": [
                        [Number(sortCol), "desc"]
                    ],
                    dom: 'l<".margin" B>frtip',
                    buttons: [
                        'copy', {
                            extend: 'csv',
                            filename: function() {
                                return fileTitle + '-' + new Date().toLocaleString();
                            },
                            title: '',
                        }, {
                            extend: 'excel',
                            filename: function() {
                                return fileTitle + '-' + new Date().toLocaleString();
                            },
                            title: '',
                        }, {
                            extend: 'print',
                            title: '',
                        },
                    ],
                });
            }
        </script>
        <script>
            function openPage(pageName, elmnt, color) {
                var i, tabcontent, tablinks;
                tabcontent = document.getElementsByClassName("tabcontent");
                for (i = 0; i < tabcontent.length; i++) {
                    tabcontent[i].style.display = "none";
                }
                tablinks = document.getElementsByClassName("tablink");
                for (i = 0; i < tablinks.length; i++) {
                    tablinks[i].style.backgroundColor = "";
                }
                document.getElementById(pageName).style.display = "block";
                elmnt.style.backgroundColor = color;

            }
            // Get the element with id="defaultOpen" and click on it
            document.getElementById("defaultOpen").click();
        </script>
        <script>
            // Get the element with id="defaultOpen" and click on it
            document.getElementById("defaultOpen").click();
        </script>
        <script>
            $(window).on('load', function() {
                $('.loader').fadeOut();
            });
        </script>
    </body>
	"""

	return my_template