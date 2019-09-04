Using dhelm-pnf-chart-generator you can generate point and figure charts and save the charts into excel sheet. To generate the charts, you have to supply data to the project. You can supply data in either of the three ways. It supports three predefined data feeds. You need to have subscription from any of the following three datafeeds:
* Global Datafeed Websocket API
* Zerodha Kite developer API 
* Quandl API

## Compatibility
This project has been tested on python 3.7 and run using anaconda 4.6. It can run on other python versions as well.
## Getting Started
To generate point and figure chart first clone the library in your computer. Then navigate to the folder _**dhelm-pnf-chart-generator**_.
Then you have to execute the **dhelm_chart_generator.py** file to generate charts.
`py dhelm_chart_generator.py`
It is that simple. 
**However,** before you have to make certain settings.

### Requirements
Make sure that **pip** is installed.
To run the project successfully following packages have to be installed:
* pandas
* XlsxWriter
* pytz
* tzlocal
* DhelmGfeedClient
* Quandl
* kiteconnect
When you run the **dhelm_chart_generator.py** for the first time, these packages should get installed automatically.

You can find some sample charts in charts_gfeed, charts_kite and charts_quandl folders.

To find detailed usage guidelines read through the [wiki](https://github.com/kncsolutions/dhelm-pnf-chart-generator/wiki).

For any query and reporting bugs you can raise an [issue](https://github.com/kncsolutions/dhelm-pnf-chart-generator/issues), or you can
drop an email at developer@kncsolutions.in.