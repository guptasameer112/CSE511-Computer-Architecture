./build/ARM/gem5.opt --remote-gdb-port=0 -d ./output configs/example/fs_wirelessExample.py --cpu-clock=1GHz  --kernel=vmlinux  --machine-type=VExpress_GEM5_V1 --dtb-file=/home/ubuntu/project/On-Chip-Wireless/gem5-X-wireless/system/arm/dt/armv8_gem5_v1_1cpu.dtb -n 8 --disk-image=gem5_ubuntu16.img --caches --l2cache --l1i_size=32kB --l1d_size=32kB --l2_size=1MB --l2_assoc=2 --l2bus-wireless --l2_cluster_size=4 --mem-type=DDR4_2400_4x16 --mem-ranks=4  --mem-size=4GB  --sys-clock=1600MHz  --membus-wireless  --wireless-bandwidth=10GB/s --mac-protocol=token_pass