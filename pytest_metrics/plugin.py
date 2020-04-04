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
        default="https://i.ibb.co/9qBkwDF/Testing-Fox-Logo.png",
        help='Logo to use in metrics report'
    )
    group.addoption(
        '--mtimestamp',
        action='store',
        dest='mtimestamp',
        default="False",
        help='Append timestamp to metrics report'
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
    try:
        _duration = _test_end_time - _test_start_time
    except Exception as e:
        print(e)
        _duration = 0
    # _duration = _test_end_time - _test_start_time

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
        if config.option.mtimestamp == "True":
            report_file_name = "pytest_metrics_" + str(datetime.datetime.now().strftime("%b_%d_%Y_%H_%M")) + ".html"
        else:
            report_file_name = "pytest_metrics.html"
        live_logs_file = open(report_file_name,'w')
        message = get_updated_template_text(str(config.option.mlogo))
        live_logs_file.write(message)
        live_logs_file.close()

def append_suite_metrics_row(name):
    suite_row_text = """
        <tr>
            <td style="word-wrap: break-word;max-width: 200px; white-space: normal; text-align:left">__sname__</td>
            <td>__spass__</td>
            <td>__sfail__</td>
            <td>__sskip__</td>
            <td>__sxpass__</td>
            <td>__sxfail__</td>
            <td>__serror__</td>
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
            <td style="word-wrap: break-word;max-width: 200px; white-space: normal; text-align:left">__sname__</td>
            <td style="word-wrap: break-word;max-width: 200px; white-space: normal; text-align:left">__name__</td>
            <td>__stat__</td>
            <td>__dur__</td>
            <td style="word-wrap: break-word;max-width: 200px; white-space: normal; text-align:left"">__msg__</td>
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
    # template_text = template_text.replace("__executed_by__", str(platform.uname()[1]))
    # template_text = template_text.replace("__os_name__", str(platform.uname()[0]))
    # template_text = template_text.replace("__python_version__", str(sys.version.split(' ')[0]))
    # template_text = template_text.replace("__generated_date__", str(datetime.datetime.now().strftime("%b %d %Y, %H:%M")))
    template_text = template_text.replace("__total__", str(_total))
    template_text = template_text.replace("__executed__", str(_executed))
    template_text = template_text.replace("__pass__", str(_pass))
    template_text = template_text.replace("__fail__", str(_fail))
    template_text = template_text.replace("__skip__", str(_skip))
    # template_text = template_text.replace("__error__", str(_error))
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
        <script src="https://code.jquery.com/jquery-3.3.1.js" type="text/javascript"></script>
        <!-- Bootstrap core Googleccharts -->
        <script src="https://www.gstatic.com/charts/loader.js" type="text/javascript"></script>
        <script type="text/javascript">
            google.charts.load('current', {
                packages: ['corechart']
            });
        </script>
        <!-- Bootstrap core Datatable-->
        <script src="https://cdn.datatables.net/1.10.19/js/jquery.dataTables.min.js" type="text/javascript"></script>
        <script src="https://cdn.datatables.net/buttons/1.5.2/js/dataTables.buttons.min.js" type="text/javascript"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.1.3/jszip.min.js" type="text/javascript"></script>
        <script src="https://cdn.datatables.net/buttons/1.5.2/js/buttons.html5.min.js" type="text/javascript"></script>
        <script src="https://cdn.datatables.net/buttons/1.5.2/js/buttons.print.min.js" type="text/javascript"></script>
        <script src="https://cdn.datatables.net/buttons/1.6.1/js/buttons.colVis.min.js" type="text/javascript"></script>
        <style>
            body {
                font-family: -apple-system, sans-serif;
                background-color: #eeeeee;
            }
            .sidenav {
                height: 100%;
                width: 240px;
                position: fixed;
                z-index: 1;
                top: 0;
                left: 0;
                background-color: white;
                overflow-x: hidden;
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
            .wrimagecard {
                margin-top: 0;
                margin-bottom: 0.6rem;
                border-radius: 10px;
                transition: all 0.3s ease;
                background-color: #f8f9fa;
            }
            .rowcard {
                padding-top: 10px;
                box-shadow: 12px 15px 20px 0px rgba(46, 61, 73, 0.15);
                border-radius: 15px;
                transition: all 0.3s ease;
                background-color: white;
            }
            .tablecard {
                background-color: white;
                font-size: 15px;
            }
            tr {
                height: 40px;
            }
            .dt-buttons {
                margin-left: 5px;
            }
            th, td, tr {
                text-align:center;
                vertical-align: middle;
            }
            .loader {
                position: fixed;
                left: 0px;
                top: 0px;
                width: 100%;
                height: 100%;
                z-index: 9999;
                background: url('https://i.ibb.co/cXnKsNR/Cube-1s-200px.gif') 50% 50% no-repeat rgb(249, 249, 249);
            }
        </style>
    </head>

    </html>

    <body>
        <div class="loader"></div>
        <div class="sidenav">
            <a><img class="wrimagecard" src="__custom_logo__" style="height:20vh;max-width:98%;" /></a>
            <a class="tablink" href="#" id="defaultOpen" onclick="openPage('dashboard', this, '#fc6666')">
                <i class="fa fa-dashboard" style="color:CORNFLOWERBLUE"></i> Dashboard</a>
            <a class="tablink" href="#" onclick="openPage('suiteMetrics', this, '#fc6666'); executeDataTable('#sm',2)">
                <i class="fa fa-th-large" style="color:CADETBLUE"></i> Suite Metrics</a>
            <a class="tablink" href="#" onclick="openPage('testMetrics', this, '#fc6666'); executeDataTable('#tm',3)">
                <i class="fa fa-list-alt" style="color:PALEVIOLETRED"></i> Test Metrics</a>
        </div>
        <div class="main col-md-9 ml-sm-auto col-lg-10 px-4">
            <div class="tabcontent" id="dashboard">
                <div class="d-flex flex-column flex-md-row align-items-center p-1 mb-3 bg-light border-bottom shadow-sm rowcard">
                    <h5 class="my-0 mr-md-auto font-weight-normal"><i class="fa fa-dashboard"></i> Dashboard</h5>
                    <nav class="my-2 my-md-0 mr-md-3" style="color:red">
                        <a class="p-2"><b style="color:black;">Execution Time:</b> __execution_time__ s</a>
                    </nav>
                </div>

                <div class="row rowcard">
                    <div class="col-md-4 border-right">
                        <table style="width:100%;height:200px;text-align: center;">
                            <tbody>
                                <tr style="height:60%">
                                    <td>
                                        <table style="width:100%">
                                            <tbody>
                                                <tr style="height:100%">
                                                    <td style="font-size:60px; color:rgb(105, 135, 219)">__total__</td>
                                                </tr>
                                                <tr>
                                                    <td>
                                                        <span style="color: #999999;font-size:12px">Total</span>
                                                    </td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </td>
                                </tr>
                                <tr style="height:25%">
                                    <td>
                                        <table style="width:100%">
                                            <tbody>
                                                <tr align="center" style="height:70%;font-size:25px" valign="middle">
                                                    <td style="width: 33%; color:rgb(17, 3, 3)">__executed__</td>
                                                    <td style="width: 33%; color:#96a74c">__skip__</td>
                                                </tr>
                                                <tr align="center" style="height:30%" valign="top">
                                                    <td style="width: 33%">
                                                        <span style="color: #999999;font-size:10px">Executed</span>
                                                    </td>
                                                    <td style="width: 33%">
                                                        <span style="color: #999999;font-size:10px">Skip</span>
                                                    </td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <div class="col-md-4 borders" data-toggle="tooltip">
                        <table style="width:100%;height:200px;text-align: center;">
                            <tbody>
                                <tr style="height:100%">
                                    <td>
                                        <table style="width:100%">
                                            <tbody>
                                                <tr style="height:100%">
                                                    <td style="font-size:60px; color:#2ecc71">__pass__</td>
                                                    <td style="font-size:60px; color:#fc6666">__fail__</td>
                                                </tr>
                                                <tr>
                                                    <td>
                                                        <span style="color: #999999;font-size:12px">Pass</span>
                                                    </td>
                                                    <td>
                                                        <span style="color: #999999;font-size:12px">Fail</span>
                                                    </td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <div class="col-md-4 border-left">
                        <table style="width:100%;height:200px;text-align: center;">
                            <tbody>
                                <tr style="height:100%">
                                    <td>
                                        <table style="width:100%">
                                            <tbody>
                                                <tr style="height:100%">
                                                    <td style="font-size:60px; color:#9e6b6b">__xpass__</td>
                                                    <td style="font-size:60px; color:#96a74c">__xfail__</td>
                                                </tr>
                                                <tr>
                                                    <td>
                                                        <span style="color: #999999;font-size:12px">xPass</span>
                                                    </td>
                                                    <td>
                                                        <span style="color: #999999;font-size:12px">xFail</span>
                                                    </td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                <hr/>
                <div class="row rowcard">
                    <div class="col-md-4"> <span style="font-weight:bold;color:gray">Test Status:</span>
                        <div id="testChartID" style="height:280px;width:auto;"></div>
                    </div>
                    <div class="col-md-8"> <span style="font-weight:bold;color:gray">Top 5 Suite Failures:</span>
                        <div id="suiteBarID" style="height:300px;width:auto;"></div>
                    </div>
                </div>
                <hr/>
                <div class="row rowcard">
                    <div class="col-md-12" style="height:450px;width:auto;"> <span style="font-weight:bold;color:gray">Top 10 Test Performance (sec):</span>
                        <div id="testsBarID" style="height:400px;width:auto;"></div>
                    </div>
                </div>
                <hr/>
                <div class="row">
                    <div class="col-md-12" style="width:auto;">
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
            </div>

            <div class="tabcontent" id="suiteMetrics">
                <h4><b><i class="fa fa-table"></i> Suite Metrics</b></h4>
                <hr/>
                <table class="table row-border tablecard" id="sm">
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
            <table class="table row-border tablecard" id="tm">
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

        <script>
            function createPieChart(pass_count, fail_count, xpass_count, xfail_count, ChartID, ChartName) {
                var status = [];
                status.push(['Status', 'Percentage']);
                status.push(['PASS', parseInt(pass_count)], ['FAIL', parseInt(fail_count)],
                 ['xPASS', parseInt(xpass_count)], ['xFAIL', parseInt(xfail_count)], );
                var data = google.visualization.arrayToDataTable(status);

                var options = {
                    pieHole: 0.6,
                    legend: 'bottom',
                    chartArea: {
                        width: "85%",
                        height: "80%"
                    },
                    colors: ['#2ecc71', '#fc6666', '#9e6b6b', '#96a74c'],
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
                    "lengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
                    buttons: [
                    {
                        extend:    'copyHtml5',
                        text:      '<i class="fa fa-files-o"></i>',
                        filename: function() {
                            return fileTitle + '-' + new Date().toLocaleString();
                        },
                        titleAttr: 'Copy',
                        exportOptions: {
                            columns: ':visible'
                        }
					},

                    {
                        extend:    'csvHtml5',
                        text:      '<i class="fa fa-file-text-o"></i>',
                        titleAttr: 'CSV',
                        filename: function() {
                            return fileTitle + '-' + new Date().toLocaleString();
                        },
                        exportOptions: {
                            columns: ':visible'
                        }
                    },

                    {
                        extend:    'excelHtml5',
                        text:      '<i class="fa fa-file-excel-o"></i>',
                        titleAttr: 'Excel',
                        filename: function() {
                            return fileTitle + '-' + new Date().toLocaleString();
                        },
                        exportOptions: {
                            columns: ':visible'
                        }
                    },
                    {
                        extend:    'print',
                        text:      '<i class="fa fa-print"></i>',
                        titleAttr: 'Print',
                        exportOptions: {
                            columns: ':visible',
                            alignment: 'left',
                        }
                    },
                    {
                        extend:    'colvis',
                        collectionLayout: 'fixed two-column',
                        text:      '<i class="fa fa-low-vision"></i>',
                        titleAttr: 'Hide Column',
                        exportOptions: {
                            columns: ':visible'
                        },
                        postfixButtons: [ 'colvisRestore' ]
                    },
                ],
                columnDefs: [ {
                    visible: false,
                } ]
                }
            );
        }
        </script>
        <script>
            function openPage(pageName,elmnt,color) {
                var i, tabcontent, tablinks;
                tabcontent = document.getElementsByClassName("tabcontent");
                for (i = 0; i < tabcontent.length; i++) {
                    tabcontent[i].style.display = "none";
                }
                tablinks = document.getElementsByClassName("tablink");
                for (i = 0; i < tablinks.length; i++) {
                    tablinks[i].style.color = "";
                }
                document.getElementById(pageName).style.display = "block";
                elmnt.style.color = color;

            }
            // Get the element with id="defaultOpen" and click on it
            document.getElementById("defaultOpen").click();
        </script>
        <script>
            // Get the element with id="defaultOpen" and click on it
            document.getElementById("defaultOpen").click();
        </script>
        <script>
            $(window).on('load',function(){$('.loader').fadeOut();});
        </script>
    </body>
	"""

	return my_template
