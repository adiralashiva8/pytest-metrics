# pytest-metrics


Plugin to create dashboard view report for pytest (no code changes)

[![PyPI version](https://badge.fury.io/py/pytest-metrics.svg)](https://badge.fury.io/py/pytest-metrics)
[![Downloads](https://pepy.tech/badge/pytest-metrics)](https://pepy.tech/project/pytest-metrics)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)]()
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)]()
[![Open Source Love png1](https://badges.frapsoft.com/os/v1/open-source.png?v=103)]()

---

Sample Report - [link](http://pytest-metrics.netlify.com)
> Best viewed in desktop

---

### Why Pytest-Metrics

 - Dashboard view of results
 - Suite/Class level statisitics
 - Search and Pagination of results
 - Export results to csv, excel and can save as pdf
 - Easy to share results
 - Free to use

---

### How it works:

 - Get execution details using `hooks` [link](https://docs.pytest.org/en/latest/_modules/_pytest/hookspec.html)
 - Create pytest-metrics report &
 - Saves in current folder

---

### How to use in project:

1. Install `pytest-metrics`
   
   > Case 1: Using pip
   ```
   pip install pytest-metrics
   ```
   
   > Case 2: Using `setup.py` (clone repo and run command in root)
   ```
   python setup.py install
   ```

   > Case 3: Install from git (changes in master)
   ```
   pip install git+https://github.com/adiralashiva8/pytest-metrics
   ```

2. Enable `metrics-report` while executing tests
    ```
    pytest --menable=True
    ```
    > Default value of `--menable` is `False`

3. Report with created after execution


**Note:** 

 - Customize logo by using following command

    ```
    pytest --menable=True --mlogo="https://www.mycompany/logo.png"
    ```
 - Append timestamp to metrics report

    ```
    pytest --menable=True --mtimestamp=True
    ```

---

*Thanks for using pytest-metrics!*

If you have any questions / suggestions / comments on this, please feel free to reach me at

 - Email: <a href="mailto:adiralashiva8@gmail.com?Subject=Pytest%20Metrics" target="_blank">`adiralashiva8@gmail.com`</a> 
 - LinkedIn: <a href="https://www.linkedin.com/in/shivaprasadadirala/" target="_blank">`shivaprasadadirala`</a>
 - Twitter: <a href="https://twitter.com/ShivaAdirala" target="_blank">`@ShivaAdirala`</a>

---

Found issue report [here](https://github.com/adiralashiva8/pytest-metrics/issues)

---

*Credits*

 - [Pytest-dev](https://github.com/pytest-dev)
 - [Stackoverflow](https://stackoverflow.com/questions/tagged/pytest)
 - [Datatable](https://datatables.net)
 - [GoogleCharts](https://developers.google.com/chart/interactive/docs/gallery)
 - [pytest-community]()

*Pytest-metrics* uses above items to create report

---

 :star: repo if you like it

 > Inspired from [robotframework-metrics](https://github.com/adiralashiva8/robotframework-metrics)
