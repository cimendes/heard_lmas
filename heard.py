#!/usr/bin/env python3

import os 
import sys
import json
from glob import glob

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

def main(report_dir):

    # merge assemblerPerformanceData
    assembler_performance = []
    assembler_performance_files = glob(report_dir + '/*/' + 'performance_metadata.json')
    for json_file in assembler_performance_files:
        with open(json_file) as json_fh:
            p_json = json.load(json_fh)
            assembler_performance = assembler_performance + p_json

    i = 0 # adjust IDs for table
    new_assembler_performance = []
    for dictionary in assembler_performance:
        dictionary['id'] = i
        i += 1

    # merge _referenceData
    #TODO
    _referenceData = {"tiny_reference": {"Bacillus_subtilis": {"size": 4045677, "GC": 43.93890070808915}, "Staphylococcus_aureus": {"size": 2718780, "GC": 32.85863512310669}}}


    # merge _sampleData
    #TODO
    _sampleData = {"tiny": {"reads": 200000.0},
                   "tiny_new": {"reads": 200000.0}}

    # merge _mainDataTables
    mainDataTables = dict()
    DataTables_files = glob(report_dir + '/*/' + 'pipeline_report_tables.json')
    for dt_file in DataTables_files:
        with open(dt_file) as dt_fh:
            dt_json = json.load(dt_fh)
            mainDataTables.update(dt_json)

    # merge _mainDataPlots
    mainDataPlots = dict()
    DataPlots_files = glob(report_dir + '/*/' + 'pipeline_report_plots.json')
    for dt_file in DataPlots_files:
        with open(dt_file) as dt_fh:
            dt_json = json.load(dt_fh)
            mainDataPlots.update(dt_json)
    
    min_contig_size = 1000
    about_md_to_write = '`Combined report`'

    with open("src/index.html", "w") as html_fh:
        html_fh.write(html_template.format(json.dumps(new_assembler_performance),
                                           json.dumps(_referenceData),
                                           json.dumps(_sampleData),
                                           json.dumps(mainDataTables),
                                           json.dumps(mainDataPlots),
                                           list(mainDataTables.keys()),
                                           min_contig_size,
                                           about_md_to_write))

if __name__ == "__main__":

    report_dir = sys.argv[1]
    main(report_dir)