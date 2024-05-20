#!/usr/bin/python3

import os
import re
import sys
import errno
from subprocess import Popen, PIPE
from util import platform as platform


def find_device(data, pciid):
    id = re.escape(pciid)
    m = re.search("^" + id + "\s(.*)$", data, re.MULTILINE)
    return m.group(1)


def pretty_size(size):
    size_strs = ['B', 'KiB', 'MiB', 'GiB', 'TiB']
    last_size = size
    fract_size = size
    num_divs = 0

    while size > 1:
        fract_size = last_size
        last_size = size
        size /= 1024
        num_divs += 1

    num_divs -= 1
    fraction = fract_size / 1024
    pretty = "%.2f" % fraction
    pretty = pretty + size_strs[num_divs]
    return pretty


def virtual_device(path):
    for dir in os.listdir(path):
        if re.search("device", dir):
            return 0
    return 1


class Device:

    def __str__(d):
        text = ""

        def print(t):
            nonlocal text
            text = text + t + '\n'

        print(d.diskname)
        print("\tHost: " + d.host)
        print("\tVendor: " + d.vendor)
        print("\tModel: " + d.model)
        print("\tSector size (bytes): " + d.sectorsize)
        print("\tSectors: " + d.sectors)
        size = d.total_size()
        pretty = pretty_size(size)
        print("\tTotal Size: " + pretty)
        print("\tRemovable: " + d.removable)
        print("\tDisk type: " + d.rotational)
        print("\tSupports discard: " + d.discard)
        if len(d.holders) > 0:
            print("\tHolders:")
            for h in d.holders:
                print("\t\t" + h)
        if len(d.partitions) > 0:
            print("\tPartitions:")
            for p in d.partitions:
                print("\t\t" + p.diskname)
                print("\t\t\tStart sector: " + p.start)
                print("\t\t\tSectors: " + p.sectors)
                size = p.total_size()
                pretty = pretty_size(size)
                print("\t\t\tTotal Size: " + pretty)
                if len(p.holders) > 0:
                    print("\t\t\tHolders:")
                    for h in p.holders:
                        print("\t\t\t\t" + h)
        return text
    __repr__ = __str__

    def __init__(self, pcidata, sysdir="", sysfs_no_links=0):
        self.sectorsize = ""
        self.sectors = ""
        self.rotational = ""
        self.sysdir = sysdir
        self.host = ""
        self.model = ""
        self.vendor = ""
        self.holders = []
        self.diskname = ""
        self.partitions = []
        self.removable = ""
        self.start = ""
        self.discard = ""
        self.sysfs_no_links = sysfs_no_links
        if pcidata is None:
            self.__populate_part_info()
        else:
            self.__populate_all(pcidata)

    def __populate_model(self):
        try:
            with open(self.sysdir + "/device/model") as f:
                self.model = f.read().rstrip()
        except IOError:
            # do nothing
            pass

    def __populate_vendor(self):
        try:
            with open(self.sysdir + "/device/vendor") as f:
                self.vendor = f.read().rstrip()
        except IOError:
            # do nothing
            pass

    def __populate_sectors(self):
        try:
            with open(self.sysdir + "/size") as f:
                self.sectors = f.read().rstrip()
        except IOError:
            self.sectors = 0

    def __populate_sector_size(self):
        try:
            with open(self.sysdir + "/queue/hw_sector_size") as f:
                self.sectorsize = f.read().rstrip()
        except IOError:
            # if this sysfs doesnt show us sectorsize then just assume 512
            self.sectorsize = "512"

    def __populate_rotational(self):
        try:
            with open(self.sysdir + "/queue/rotational") as f:
                rotation = f.read().rstrip()
        except IOError:
            self.rotational = "Could not determine rotational"
            return
        if rotation == "1":
            self.rotational = "Spinning disk"
        else:
            self.rotational = "SSD"

    def __populate_host(self, pcidata):
        if self.sysfs_no_links == 1:
            try:
                sysdir = os.readlink(os.path.join(self.sysdir, "device"))
            except:
                pass
        else:
            sysdir = self.sysdir
        m = re.match(".+/\d+:(\w+:\w+\.\w)/host\d+/\s*", sysdir)
        if m:
            pciid = m.group(1)
            self.host = find_device(pcidata, pciid)
        else:
            self.host = ""

    def __populate_diskname(self):
        m = re.match(".*/(.+)$", self.sysdir)
        self.diskname = m.group(1)

    def __populate_holders(self):
        for dir in os.listdir(self.sysdir + "/holders"):
            if re.search("^dm-.*", dir):
                try:
                    with open(self.sysdir + "/holders/" + dir + "/dm/name") as f:
                        name = f.read().rstrip()
                    self.holders.append(name)
                except IOError:
                    self.holders.append(dir)
            else:
                self.holders.append(dir)

    def __populate_discard(self):
        try:
            with open(self.sysdir + "/queue/discard_granularity") as f:
                discard = f.read().rstrip()
            if discard == "0":
                self.discard = "No"
            else:
                self.discard = "Yes"
        except IOError:
            self.discard = "No"

    def __populate_start(self):
        try:
            with open(self.sysdir + "/start") as f:
                self.start = f.read().rstrip()
        except IOError:
            pass

    def __populate_partitions(self):
        for dir in os.listdir(self.sysdir):
            m = re.search("(" + self.diskname + "\d+)", dir)
            if m:
                partname = m.group(1)
                part = Device(None, self.sysdir + "/" + partname)
                self.partitions.append(part)

    def __populate_part_info(self):
        """ Only call this if we are a partition """
        self.__populate_diskname()
        self.__populate_holders()
        self.__populate_sectors()
        self.__populate_sector_size()
        self.__populate_start()

    def __populate_removable(self):
        try:
            with open(self.sysdir + "/removable") as f:
                remove = f.read().rstrip()
            if remove == "1":
                self.removable = "Yes"
            else:
                self.removable = "No"
        except IOError:
            self.removable = "No"

    def get_data_obj(self):
        doc = {
            "host": self.host,
            "model": self.model,
            "vendor": self.vendor,
            "diskname": self.diskname,
            "removable": self.removable,
            "rotational": self.rotational,
            "discard": self.discard,
            "start": self.start,
            "sysdir": self.sysdir,
            "holders": self.holders,
            "sectors": self.sectors,
            "sectorsize": self.sectorsize,
            "totalsize": self.total_size(),
            "partitions": [p.get_data_obj() for p in self.partitions],
        }
        return doc

    def total_size(self):
        try:
            return float(self.sectors) * float(self.sectorsize)
        except:
            raise Exception("Could not determine size of device")

    def __populate_all(self, pcidata):
        self.__populate_diskname()
        self.__populate_holders()
        self.__populate_partitions()
        self.__populate_removable()
        self.__populate_model()
        self.__populate_vendor()
        self.__populate_sectors()
        self.__populate_sector_size()
        self.__populate_rotational()
        self.__populate_discard()
        self.__populate_host(pcidata)


def get_list() -> [Device]:
    if platform.get() != platform.PLATFORM_TYPE.LINUX:
        raise NotImplementedError("Platform not supported")

    p = Popen(["lspci"], stdout=PIPE)
    err = p.wait()
    if err:
        print("Error running lspci")
        sys.exit()
    pcidata = p.stdout.read().decode('utf-8')

    sysfs_no_links = 0
    devices = []

    if len(sys.argv) > 1:
        m = re.match("/dev/(\D+)\d*", sys.argv[1])
        if m:
            block = m.group(1)
        else:
            block = sys.argv[1]

        try:
            path = os.readlink(os.path.join("/sys/block/", block))
        except OSError as e:
            if e.errno == errno.EINVAL:
                path = block
            else:
                print("Invalid device name " + block)
                sys.exit()
        d = Device(pcidata,  os.path.join("/sys/block", path))
        devices.append(d)
    else:
        for block in os.listdir("/sys/block"):
            try:
                if sysfs_no_links == 0:
                    path = os.readlink(os.path.join("/sys/block/", block))
                else:
                    path = block
            except OSError as e:
                if e.errno == errno.EINVAL:
                    path = block
                    sysfs_no_links = 1
                else:
                    continue
            if re.search("virtual", path):
                continue
            if sysfs_no_links == 1:
                sysdir = os.path.join("/sys/block", path)
                if virtual_device(sysdir) == 1:
                    continue
            d = Device(pcidata, os.path.join(
                "/sys/block", path), sysfs_no_links)
            devices.append(d)
    return devices

    for d in devices:
        print(d)


__all__ = [get_list, Device, pretty_size]

if __name__ == "__main__":
    print(get_list())
