#!/usr/bin/env bash

PUB_P2P_NICE="-10"
PUB_P2P_CPUS="0,1"

SUB_P2P_NICE="-10"
SUB_P2P_CPUS="2,3"

TEST_CONF="myTestConfig"
TEST_TIME="30"
LOCALHOST="127.0.0.1"
LOCATOR_P2P="tcp/$LOCALHOST:7447"

if [ $# -ne 1 ]; then
    echo "Usage: ./p2p.sh CONFIG.sh"
    exit 1
fi

source $1
LOG_DIR="logs/$ZENOH_PERF_VER"
mkdir -p $LOG_DIR

trap ctrl_c INT

function ctrl_c() {
    cleanup
    exit
}

function cleanup() {
    killall -9 zn_sub_thr
    killall -9 z_sub_thr
    killall -9 zn_pub_thr
    killall -9 z_put_thr
}

for P in {0..27}; do
    PAYLOAD=$((8*2**P))
    DATE=$(date +%Y%m%d.%H%M%S)
    LOG_FILE="${LOG_DIR}/${PAYLOAD}.log"

    echo "\nTesting $PAYLOAD bytes. ID: $DATE"
    echo 'layer,scenario,test,name,size,messages' > $LOG_FILE

    # echo ">>> Starting zenoh test on SUB... $DATE"
    # sleep 1
    # nice $SUB_P2P_NICE taskset -c $SUB_P2P_CPUS \
    #     $ZENOH_PERF_DIR/target/release/z_sub_thr \
    #     --scenario $TEST_CONF \
    #     --mode peer \
    #     --locator $LOCATOR_P2P \
    #     --payload $PAYLOAD \
    #     --name $DATE >> $LOG_FILE &

    # sleep 5
    # echo ">>> Starting zenoh test on PUB... $DATE"
    # nice $PUB_P2P_NICE taskset -c $PUB_P2P_CPUS timeout $TEST_TIME \
    #     $ZENOH_PERF_DIR/target/release/z_put_thr \
    #     --mode peer \
    #     --locator $LOCATOR_P2P \
    #     --payload $PAYLOAD

    # killall -9 z_sub_thr
    # sleep 1


    # ZENOH.NET
    echo ">>> Starting zenoh.net test on SUB... $DATE"
    sleep 1
    nice $SUB_P2P_NICE taskset -c $SUB_P2P_CPUS \
        $ZENOH_PERF_DIR/target/release/zn_sub_thr \
        --scenario $TEST_CONF \
        --mode peer \
        --locator $LOCATOR_P2P \
        --payload $PAYLOAD \
        --name $DATE >> $LOG_FILE &

    sleep 5
    echo ">>> Starting zenoh.net test on PUB... $DATE"
    nice $PUB_P2P_NICE taskset -c $PUB_P2P_CPUS timeout $TEST_TIME \
        $ZENOH_PERF_DIR/target/release/zn_pub_thr \
        --mode peer \
        --locator $LOCATOR_P2P \
        --payload $PAYLOAD

    killall -9 zn_sub_thr
    sleep 1

done
