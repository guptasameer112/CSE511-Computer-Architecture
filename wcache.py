# Heavily inspired by Gem5X Onchip wireless cache implementation

# Configure the M5 cache hierarchy config in one place
#

from __future__ import print_function

import m5
from m5.objects import *
from Caches import *

def config_cache(options, system):
    num_of_clusters = (options.num_cpus // options.l2_cluster_size)
    if ((options.num_cpus % options.l2_cluster_size)!=0):
        num_of_clusters = num_of_clusters + 1
    #
    # if True:
    dcache_class, icache_class, l2_cache_class, walk_cache_class = \
        L1_DCache, L1_ICache, L2Cache, None

        # if buildEnv['TARGET_ISA'] == 'x86':
        #     walk_cache_class = PageTableWalkerCache

    # Set the cache line size of the system
    system.cache_line_size = options.cacheline_size

    # If elastic trace generation is enabled, make sure the memory system is
    # minimal so that compute delays do not include memory access latencies.
    # Configure the compulsory L1 caches for the O3CPU, do not configure
    # any more caches.
   
    if options.l2cache:
        # Provide a clock for the L2 and the L1-to-L2 bus here as they
        # are not connected using addTwoLevelCacheHierarchy. Use the
        # same clock as the CPUs.
        #l2=[]
        #tol2bus=[]	
        system.l2 = [l2_cache_class(clk_domain=system.cpu_clk_domain,
                                    size=options.l2_size,
                                    assoc=options.l2_assoc)
                    for i in xrange(num_of_clusters)]

        # Definition example of a wireless bus between the L1 caches and the L2
        # cache in a cluster
        system.tol2bus = [WirelessL2XBar(clk_domain = system.cpu_clk_domain,
                                        bandwidth = options.wireless_bandwidth,
                                        mac_protocol = options.mac_protocol,
                                        retry_slot_size = options.retry_slot_size,
                                        backoff_ceil = options.backoff_ceil)
                        for i in xrange(num_of_clusters)]

        for i in xrange (num_of_clusters):
            # Connect the elements to the wireless L2 bus
            system.tol2bus[i].width = options.l2bus_width
            system.l2[i].cpu_side = system.tol2bus[i].master
            system.l2[i].mem_side = system.membus.slave

            # if options.spm:
            #     range_l2 = (long(system.load_offset)) + (long(Addr(options.mem_size)))
            #     system.l2[i].addr_ranges=AddrRange(0, size=range_l2)

    if options.memchecker:
        system.memchecker = MemChecker()

    for i in xrange(options.num_cpus):
        if options.caches:
            icache = icache_class(size=options.l1i_size,
                                  assoc=options.l1i_assoc)
            dcache = dcache_class(size=options.l1d_size,
                                  assoc=options.l1d_assoc)
         
            # If we have a walker cache specified, instantiate two
            # instances here
            if walk_cache_class:
                iwalkcache = walk_cache_class()
                dwalkcache = walk_cache_class()
            else:
                iwalkcache = None
                dwalkcache = None

            if options.memchecker:
                dcache_mon = MemCheckerMonitor(warn_only=True)
                dcache_real = dcache

                # Do not pass the memchecker into the constructor of
                # MemCheckerMonitor, as it would create a copy; we require
                # exactly one MemChecker instance.
                dcache_mon.memchecker = system.memchecker

                # Connect monitor
                dcache_mon.mem_side = dcache.cpu_side

                # Let CPU connect to monitors
                dcache = dcache_mon

            # When connecting the caches, the clock is also inherited
            # from the CPU in question
           
            # if True:
            system.cpu[i].addPrivateSplitL1Caches(icache, dcache,
                                                    iwalkcache, dwalkcache)

            if options.memchecker:
                # The mem_side ports of the caches haven't been connected yet.
                # Make sure connectAllPorts connects the right objects.
                system.cpu[i].dcache = dcache_real
                system.cpu[i].dcache_mon = dcache_mon

        # elif options.external_memory_system:
        
        system.cpu[i].createInterruptController()
        if options.l2cache:
            system.cpu[i].connectAllPorts(system.tol2bus[i//options.l2_cluster_size], system.membus)
        # elif options.external_memory_system:
        #     system.cpu[i].connectUncachedPorts(system.membus)
        else:
            system.cpu[i].connectAllPorts(system.membus)

    return system

# ExternalSlave provides a "port", but when that port connects to a cache,
# the connecting CPU SimObject wants to refer to its "cpu_side".
# The 'ExternalCache' class provides this adaptation by rewriting the name,
# eliminating distracting changes elsewhere in the config code.
# class ExternalCache(ExternalSlave):
#     def __getattr__(cls, attr):
#         if (attr == "cpu_side"):
#             attr = "port"
#         return super(ExternalSlave, cls).__getattr__(attr)

#     def __setattr__(cls, attr, value):
#         if (attr == "cpu_side"):
#             attr = "port"
#         return super(ExternalSlave, cls).__setattr__(attr, value)

# def ExternalCacheFactory(port_type):
#     def make(name):
#         return ExternalCache(port_data=name, port_type=port_type,
#                              addr_ranges=[AllMemory])
#     return make