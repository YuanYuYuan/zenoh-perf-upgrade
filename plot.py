#!/usr/bin/env python3

import pandas as pd
import plotly.express as px
import os
from glob import glob
from pathlib import Path
from tap import Tap


class MyArgParser(Tap):
    # log dir
    log_dir: Path = Path('./outputs')
    # output dir
    out_dir: Path = Path('./plots')
    # experiment name
    exp_name: str = "z_put_thr + z_sub_thr"


def load_data(exp_dir: str, exp_tag: str = None) -> pd.DataFrame:
    data = pd.concat([
        pd.read_csv(f)
        for f in glob(os.path.join(exp_dir, '*.log'))
    ])
    data = data.groupby(['size'], as_index=False).agg({'messages': ['mean', 'std']})
    data.columns = ['size', 'mean', 'std']
    if exp_tag:
        data['exp'] = exp_tag
    return data


def load_usage(exp_dir: Path, n_peers: int) -> pd.DataFrame:
    data = pd.read_csv(
        os.path.join(exp_dir, '%d/usage.txt' % n_peers),
        sep='\\s+',
        skiprows=1,
        names=['t', 'CPU', 'MEM', 'VMEM']
    )
    data['n_peers'] = n_peers
    data['MA_CPU'] = data['CPU'].rolling(30).mean()
    return data


args = MyArgParser().parse_args()
os.makedirs(args.out_dir, exist_ok=True)
v5 = load_data(os.path.join(args.log_dir, 'v5/logs'), '0.5.0-beta.9')
v6 = load_data(os.path.join(args.log_dir, 'v6/logs'), '0.6.0-dev')
data = pd.concat([v5, v6])


v6['mean'] = v6['mean'] / v5['mean'] * 100

fig = px.line(
    v6,
    x='size',
    y='mean',
    log_x=True,
    labels={
        'size': 'Payload size (bytes)',
        'mean': 'Msg/sec ratio',
    },
    title='Throughput Comparison (' + args.exp_name + ') Ratio (v6 / v5)'
)
file_name = os.path.join(args.out_dir, 'throughput-comparison-in-ratio')
fig.write_html(file_name + '.html')
fig.write_image(file_name + '.jpeg')
fig.show()


fig = px.line(
    data,
    x='size',
    y='mean',
    error_y='std',
    color='exp',
    log_x=True,
    log_y=True,
    labels={
        'size': 'Payload size (bytes)',
        'mean': 'Msg/sec',
        'exp': 'Zenoh Ver.'
    },
    title='Throughput Comparison (' + args.exp_name + ')'
)
file_name = os.path.join(args.out_dir, 'throughput-comparison')
fig.write_html(file_name + '.html')
fig.write_image(file_name + '.jpeg')
fig.show()
