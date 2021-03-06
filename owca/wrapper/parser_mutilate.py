# Copyright (c) 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from io import TextIOWrapper
from typing import List, Dict
import re
from owca.metrics import Metric, MetricType
from owca.wrapper import wrapper_main
from owca.wrapper.parser import readline_with_check

EOF_line = "Stop-Mutilate-Now"


def parse(input: TextIOWrapper, regexp: str, separator: str = None,
          labels: Dict[str, str] = {}, metric_name_prefix: str = '') -> List[Metric]:
    """Custom parse function for mutilate
        #type       avg     std     min     5th    10th    90th    95th    99th
        read      801.9   155.0   304.5   643.7   661.1  1017.8  1128.2  1386.5
        update    804.6   157.8   539.4   643.4   661.2  1026.1  1136.1  1404.3
        op_q        1.0     0.0     1.0     1.0     1.0     1.1     1.1     1.1

        Total QPS = 159578.5 (1595835 / 10.0s)

        Misses = 0 (0.0%)
        Skipped TXs = 0 (0.0%)

        RX  382849511 bytes :   36.5 MB/s
        TX   67524708 bytes :    6.4 MB/s
    """

    new_metrics = []
    new_line = readline_with_check(input, EOF_line)
    if "read" in new_line:
        read = re.search(r'read\s*[0-9]+\.[0-9]+[ ]*[0-9]' +
                         r'+\.[0-9]+[ ]*[0-9]+\.[0-9]+[ ]*[0-9]+\.[0-9]+[ ]*[0-9]+\.[0-9]' +
                         r'+[ ]*[0-9]+\.[0-9]+[ ]*[0-9]+\.[0-9]+[ ]*([0-9]+\.[0-9]+)[ ]*',
                         new_line)
        p95 = float(read.group(1))
        new_metrics.append(
            Metric(metric_name_prefix + 'read_p99', p95,
                   type=MetricType.GAUGE, labels=labels,
                   help="99th percentile of read latency"))
    if "Total QPS" in new_line:
        read_qps = re.search(r'Total QPS = ([0-9]*\.[0-9])', new_line)
        if read_qps is not None:
            qps = float(read_qps.group(1))
            new_metrics.append(Metric(
                metric_name_prefix + 'qps', qps, type=MetricType.GAUGE,
                labels=labels, help="QPS"))
    return new_metrics


if __name__ == "__main__":
    wrapper_main.main(parse)
