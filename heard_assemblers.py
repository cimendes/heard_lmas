#!/usr/bin/env python3

import os 
import sys
import json
from glob import glob
import urllib.request
import re

# colors for each assembler
COLOURS = ['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99', '#e31a1c',
           '#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a', '#ebdb75', '#b15928']

html_template = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>LMAS Report</title>
  </head>
  <body style="background-color: #666666">
    <div id="root"></div>
    <script> const _assemblerPerformanceData = {0} </script>
    <script> const _referenceData = {1} </script>
    <script> const _sampleData = {2} </script>
    <script> const _mainDataTables = {3} </script>
    <script> const _mainDataPlots = {4} </script>
    <script> const _sampleList = {5} </script>
    <script> const _minContigSize = {6} </script>
    <script> const _overviewMD = {7} </script>
    <script src="./main.js"></script>
  </body>
</html>
"""
def process_assembler_performance(report_dir):
    # merge assemblerPerformanceData
    _assemblerPerformanceData = []
    assemblerPerformanceData = []
    assembler_performance_files = glob(report_dir + '/*/' + 'performance_metadata.json')
    for json_file in assembler_performance_files:
        with open(json_file) as json_fh:
            p_json = json.load(json_fh)
            assemblerPerformanceData = assemblerPerformanceData + p_json

    tempPerformanceData = {}
    for dictionary in assemblerPerformanceData:
        assembler = dictionary['assembler']
        if assembler not in tempPerformanceData.keys():
            tempPerformanceData[assembler] = dictionary
        else:
            for k,v in tempPerformanceData[assembler].items():
                if k == 'avgTime':
                    if v > tempPerformanceData[assembler]['avgTime']:
                        tempPerformanceData[assembler]['avgTime'] = v
                if k == 'cpus':
                    if v > tempPerformanceData[assembler]['cpus']:
                        tempPerformanceData[assembler]['cpus'] = v
                if k == 'max_rss':
                    if v > tempPerformanceData[assembler]['max_rss']:
                        tempPerformanceData[assembler]['max_rss'] = v
                if k == 'avgRead':
                    if v > tempPerformanceData[assembler]['avgRead']:
                        tempPerformanceData[assembler]['avgRead'] = v
                if k == 'avgWrite':
                    if v > tempPerformanceData[assembler]['avgWrite']:
                        tempPerformanceData[assembler]['avgWrite'] = v
    
    i = 0 # adjust IDs for table
    for k,v in tempPerformanceData.items():
        v['id'] = i
        _assemblerPerformanceData.append(v)
        i += 1
    
    return _assemblerPerformanceData

def parse_reference_data(HTML):
    _referenceData = {}
    for html_file in HTML:
        with open(html_file, "r", encoding='utf-8') as html_fh:
            for line in html_fh:
                if '_referenceData' in line:
                    dict_object = json.loads(re.search('({.+})', line).group(0).replace("'", '"'))
                    _referenceData.update(dict_object)
    if len(list(_referenceData.keys())) > 1:
        sys.exit("ERROR: Multiple references found.")
    return _referenceData

def parse_sample_data(HTML):
    _sampleData = {}
    for html_file in HTML:
        with open(html_file, "r", encoding='utf-8') as html_fh:
            for line in html_fh:
                if '_sampleData' in line:
                    dict_object = json.loads(re.search('({.+})', line).group(0).replace("'", '"'))
                    _sampleData.update(dict_object)
    return _sampleData

def merge_data_tables(report_dir):
    mainDataTables = dict()
    DataTables_files = glob(report_dir + '/*/' + 'pipeline_report_tables.json')
    for dt_file in DataTables_files:
        with open(dt_file) as dt_fh:
            dt_json = json.load(dt_fh)
            for k,v in dt_json.items():
                if k not in mainDataTables.keys():
                    mainDataTables[k] = v
                else:
                    for item in v['GlobalTable']:
                        mainDataTables[k]['GlobalTable'].append(item)
                    for species in v['ReferenceTables']:
                        for item in v['ReferenceTables'][species]:
                            for row in item:
                                try:
                                    mainDataTables[k]['ReferenceTables'][species][0].append(row)
                                except KeyError:
                                    sys.exit("ERROR: Species found do not match.")               
    return mainDataTables

def merge_data_plots(report_dir):
    mainDataPlots = dict()
    DataPlots_files = glob(report_dir + '/*/' + 'pipeline_report_plots.json')
    j = 0
    for dt_file in DataPlots_files:
        with open(dt_file) as dt_fh:
            dt_json = json.load(dt_fh)
            for k,v in dt_json.items():
                if k not in mainDataPlots.keys():
                    mainDataPlots[k] = v
                else:
                    j += 1
                    for plot_type in v['PlotData'].keys():
                        if plot_type == 'Global':
                            for item in v['PlotData']['Global']['contig_size']['data']:
                                mainDataPlots[k]['PlotData']['Global']['contig_size']['data'].append(item)
                            for item in v['PlotData']['Global']['gap_size']['data']:
                                mainDataPlots[k]['PlotData']['Global']['gap_size']['data'].append(item)
                            for item in v['PlotData']['Global']['misassembly']['data']:
                                mainDataPlots[k]['PlotData']['Global']['misassembly']['data'].append(item)
                        else:
                            i = 1
                            for item in v['PlotData'][plot_type]['completness']['data']:
                                item['marker']['color'] = COLOURS[i]
                                mainDataPlots[k]['PlotData'][plot_type]['completness']['data'].append(item)
                                i += 1
                            i = 1
                            for item in v['PlotData'][plot_type]['lx']['data']:
                                item['line']['color'] = COLOURS[i]
                                mainDataPlots[k]['PlotData'][plot_type]['lx']['data'].append(item)
                                i += 1
                            i = 1
                            for item in v['PlotData'][plot_type]['nax']['data']:
                                item['line']['color'] = COLOURS[i]
                                mainDataPlots[k]['PlotData'][plot_type]['nax']['data'].append(item)
                                i += 1
                            i = 1
                            for item in v['PlotData'][plot_type]['ngx']['data']:
                                item['line']['color'] = COLOURS[i]
                                mainDataPlots[k]['PlotData'][plot_type]['ngx']['data'].append(item)
                                i += 1
                            i = 1
                            for item in v['PlotData'][plot_type]['phred']['data']:
                                item['marker']['color'] = COLOURS[i]
                                mainDataPlots[k]['PlotData'][plot_type]['phred']['data'].append(item)
                            try:
                                for item in v['PlotData'][plot_type]['gaps']['data']:
                                    item['y'] = [j,j]
                                    mainDataPlots[k]['PlotData'][plot_type]['gaps']['data'].append(item)

                            except KeyError:
                                pass
                            try:
                                for item in v['PlotData'][plot_type]['snps']['data']:
                                    item['y'] = [j,j]
                                    mainDataPlots[k]['PlotData'][plot_type]['snps']['data'].append(item)
                            except KeyError:
                                pass
                            try:
                                for item in v['PlotData'][plot_type]['misassembly']['data']:
                                    item['y'] = [j,j]
                                    mainDataPlots[k]['PlotData'][plot_type]['misassembly']['data'].append(item)
                            except KeyError:
                                pass
    return mainDataPlots

def parse_min_len(HTML):
    min_len = {}
    for html_file in HTML:
        with open(html_file, "r", encoding='utf-8') as html_fh:
            for line in html_fh:
                if '_minContigSize' in line:
                    min_len[html_file] = line.split()[4]
    if len(set(min_len.values())) > 1:
        sys.exit("ERROR: Multiple values found for minimum contig length.")
    return list(min_len.values())[0]

def main(report_dir):

    main_HTML = glob(report_dir + '/*/' + 'index.html')
    if len(main_HTML) < 1:
        sys.exit('ERROR: LMAS report folders not found.')

    # merge assemblerPerformanceData
    _assemblerPerformanceData = process_assembler_performance(report_dir)
    #print(_assemblerPerformanceData)

    # get _referenceData
    _referenceData = parse_reference_data(main_HTML)

    # merge _sampleData
    _sampleData = parse_sample_data(main_HTML)

    # merge _mainDataTables
    _mainDataTables = merge_data_tables(report_dir)
    #print(_mainDataTables)

    # merge _mainDataPlots
    _mainDataPlots = merge_data_plots(report_dir)

    # get minimum contig size
    min_contig_size = parse_min_len(main_HTML)

    with open("src/index.html", "w") as html_fh:
        html_fh.write(html_template.format(json.dumps(_assemblerPerformanceData),
                                           json.dumps(_referenceData),
                                           json.dumps(_sampleData),
                                           json.dumps(_mainDataTables),
                                           json.dumps(_mainDataPlots),
                                           list(_mainDataTables.keys()),
                                           min_contig_size,
                                           '`Combined report of assemblers`'))

if __name__ == "__main__":

    if len(sys.argv) < 2:
        sys.exit("Usage: python heard_samples.py <directory with LMAS report folders>")
    if sys.argv[1] == '-h' or sys.argv[1] == '--help':
        sys.exit("Usage: python heard_samples.py <directory with LMAS report folders>")
    report_dir = sys.argv[1]
    main(report_dir)