//
// Copyright (c) 2017, 2020 ADLINK Technology Inc.
//
// This program and the accompanying materials are made available under the
// terms of the Eclipse Public License 2.0 which is available at
// http://www.eclipse.org/legal/epl-2.0, or the Apache License, Version 2.0
// which is available at https://www.apache.org/licenses/LICENSE-2.0.
//
// SPDX-License-Identifier: EPL-2.0 OR Apache-2.0
//
// Contributors:
//   ADLINK zenoh team, <zenoh@adlink-labs.tech>
//
use async_std::{task, sync::Arc};
use std::{
    path::PathBuf,
    sync::atomic::{AtomicUsize, Ordering},
    time::Duration,
    str::FromStr,
};
use structopt::StructOpt;
use zenoh::{
    prelude::{Locator, Value},
    config::{
        Config,
        whatami::WhatAmI,
    }
};


#[derive(Debug, StructOpt)]
#[structopt(name = "z_put_thr")]
struct Opt {
    #[structopt(short, long, help = "locator(s), e.g. --locator tcp/127.0.0.1:7447 tcp/127.0.0.1:7448")]
    locator: Vec<Locator>,
    #[structopt(short, long, help = "peer, router, or client")]
    mode: String,
    #[structopt(short, long, help = "payload size (bytes)")]
    payload: usize,
    #[structopt(short = "t", long, help = "print the counter")]
    print: bool,
    #[structopt(long = "conf", help = "configuration file (json5)")]
    config: Option<PathBuf>,
}

const KEY_EXPR: &str = "/test/thr";

#[async_std::main]
async fn main() {
    // Initiate logging
    env_logger::init();

    // Parse the args
    let Opt {
        locator,
        mode,
        payload,
        print,
        config
    } = Opt::from_args();

    let config = {
        let mut config: Config = if let Some(path) = config {
            json5::from_str(&async_std::fs::read_to_string(path).await.unwrap()).unwrap()
        } else {
            Config::default()
        };
        config.set_mode(Some(WhatAmI::from_str(&mode).unwrap())).unwrap();
        config.set_add_timestamp(Some(false)).unwrap();
        config.scouting.multicast.set_enabled(Some(false)).unwrap();
        config.peers.extend(locator);
        config
    };

    let value: Value = (0usize..payload)
        .map(|i| (i % 10) as u8)
        .collect::<Vec<u8>>()
        .into();

    let session = zenoh::open(config).await.unwrap();

    if print {
        let count = Arc::new(AtomicUsize::new(0));
        let c_count = count.clone();
        task::spawn(async move {
            loop {
                task::sleep(Duration::from_secs(1)).await;
                let c = count.swap(0, Ordering::Relaxed);
                if c > 0 {
                    println!("{} msg/s", c);
                }
            }
        });

        loop {
            session.put(KEY_EXPR, value.clone()).await.unwrap();
            c_count.fetch_add(1, Ordering::Relaxed);
        }
    } else {
        loop {
            session.put(KEY_EXPR, value.clone()).await.unwrap();
        }
    }
}
