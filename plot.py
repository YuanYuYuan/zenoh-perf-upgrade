#!/usr/bin/env python3

import pandas as pd
import plotly.express as px
import os
from glob import glob
from pathlib import Path
from tap import Tap


class MyArgParser(Tap):
    # log dir
    log_dir: Path = Path('./logs')
    # output dir
    out_dir: Path = Path('./outputs')


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

args = MyArgParser().parse_args()
os.makedirs(args.out_dir, exist_ok=True)
v5 = load_data(os.path.join(args.log_dir, 'v5'), '0.5.0-beta.9')
v6 = load_data(os.path.join(args.log_dir, 'v6'), '0.6.0-dev')
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
    title='Throughput Comparison (z_put_thr + z_sub_thr) in Ratio (v6 / v5)'
)
fig.write_html(os.path.join(args.out_dir, 'throughput-comparison-in-ratio.html'))
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
    title='Throughput Comparison (z_put_thr + z_sub_thr)'
)
fig.write_html(os.path.join(args.out_dir, 'throughput-comparison.html'))
fig.show()
