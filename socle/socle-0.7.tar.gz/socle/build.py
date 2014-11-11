
import os
import shutil
from socle import facts


"""
General workflow for bootstrapping a system:

1. Hard-link /var/cache/apt/archives/*_{all,target_arch}.deb to /var/cache/socle/rootfs/var/cache/apt/archvies/ for faster execution
2. Run debootstrap first stage (or febootstrap or download root filesystem tarball to /var/cache/socle/rootfs)
3. Copy QEMU static emulation binaries
4. Run debootstrap stage 2


General workflow for chroot, the point is to contaminate /var/cache/socle/rootfs/blah/ as less as possible:

0. CHROOT=/var/cache/socle/chroot/blah
1. Bind /var/cache/socle/rootfs/blah to $CHROOT if neccessary
2. Bind /dev to $CHROOT/dev if necessary
3. Bind /proc to $CHROOT/proc if necessary
4. Bind /sys $CHROOT/sys if necessary
5. Optionally bind /home to $CHROOT/home (eg. if you want to run git commit etc)
6. Mount tmpfs over $CHROOT/var/cache/apt
7. Bind $CHROOT/var/cache/apt/archives/ for faster downloads
8. Check if QEMU static emulation binaries are present, copy if necessary
9. Set PS1 environment variable so there is clear indication which chroot we're in
10. Run: chroot $CHROOT /bin/bash
11. Kill chroot processes (?)
12. Unmount stuff
13. Remove QEMU binaries?


General root filesystem tarball generation:

1. Removing APT list caches not necessary if tmpfs is used at $CHROOT/var/cache/apt
2. Removing downloaded pacakges not necessary if $CHROOT/var/cache/apt/archives/ is bound from host
3. Remove QEMU static binary (?)
4. Remove *~, *.part, *.save, *.dpkg-new (?)
4. Magic not required since chroot mounted at different path than the actual rootfs directory
5. tar cvjf /var/cache/socle/tarballs/blah.tar.gz /var/cache/socle/rootfs/blah


Generating microSD card snapshot:

1. losetup to setup loopback device
2. Transfer u-boot to the right offset
3. Possibly use some partitioning library to create partitions in the loopback device
4. Probe for new partitions
5. Create FAT32 filesystem for first partition
6. Create ext4 filesystem for second partition
7. Mount FAT32 filesystem
8. Mount ext4 filesystem
9. Copy kernel to FAT32 filesystem
10. rsync -av /var/cache/socle/rootfs/blah/ /mnt/mmcblk0p2/
11. Unmount filesystems
12. Run: sync

Misc:
1. Chrooted processes can be listed via /proc/%d/root symlink, eg kill processes upon exiting chroot
 
"""

SOCLE_ROOT_FILESYSTEMS = "/var/cache/socle/rootfs"
SOCLE_CHROOTS = "/var/cache/socle/chroot"
SOCLE_BUILD_PROFILES = os.path.join(os.path.dirname(__file__), "profiles"), "/etc/socle/profiles", "~/.socle/profiles/"

# Map Linux ARCH to Debian's architecture
DEBIAN_ARCHITECTURES = (
    ("x86_64", "amd64"),
    ("i386",   "i386"),
    ("arm",    "armel"),
    ("arm",    "armhf")
)

DEBOOTSTRAP_SCRIPTS = {
    "Debian": (
        ("wheezy",  "Wheezy"),
        ("jessie",  "Jessie"),
        ("sid",     "Experimental")
    ),
    "Ubuntu": (
        ("precise", "Precise Pangolin 12.04 LTS"),
        ("quantal", "Quantal Quetzal 12.10"),
        ("raring",  "Raring Ringtail 13.04"),
        ("saucy",   "Saucy Salamander 13.10"),
        ("trusty",  "Trusty Tahr 14.04 LTS"),
        ("utopic",  "Utopic Unicorn 14.10"),
    )
}

from menu import choice, form, CanceledException
import menu
from subprocess import call

def run_debootstrap(rootfs_path, script, arch, subarch):
    # throw exception if rootfs_path already exists
    print "debootstrapping", script+"/"+subarch, "to", rootfs_path

    menu.screen.finish()
    menu.screen = None

    # By default assume no QEMU emulation layer needed
    qemu_system = None

    # If architecture differs then it is actually needed
    if facts.ARCH != arch:
        qemu_system = "/usr/bin/qemu-system-" + arch + "-static"
        print "Host is", facts.ARCH, "and target is", arch, "so QEMU is required for second stage debootstrap"
        if not os.path.exists(qemu_system):
            raise RuntimeError("Could not find " + qemu_system)
        print "Found binary at", qemu_system

    # Run first stage debootstrap
    print(["/usr/sbin/debootstrap", "--foreign", "--arch=" + subarch, script, rootfs_path])
    call(["/usr/sbin/debootstrap", "--foreign", "--arch=" + subarch, script, rootfs_path])
    # TODO: check exit code

    # Copy QEMU binaries for cross-platform compatiliblity
    shutil.copy(qemu_system, os.path.join(rootfs_path, "usr/bin/"))

    # Run second stage debootstrap
    call(["/usr/sbin/chroot", rootfs_path, "/debootstrap/debootstrap", "--second-stage"])
    # TODO: check exit code


def debootstrap():
    # Select category: Ubuntu, Debian
    cat = choice(
        [(j,j) for j in DEBOOTSTRAP_SCRIPTS.keys()],
        "Select distribution",
        "Select distribution to bootstrap"
    )

    # Select release: wheezy, jessie, precise, trusty
    script = choice(
        [(j + " (" + k + ")",k) for (k,j) in DEBOOTSTRAP_SCRIPTS[cat]],
        "SoC image builder",
        "Choose your weapon",
        action_cancel="Exit")

    # Select architecture
    selected_subarch = choice(
        [(subarch, subarch) for arch,subarch in DEBIAN_ARCHITECTURES],
        "Architecture",
        "Select architecture, foreign architectures will be supported via binfmt and QEMU")

    # Figure out Linux arch corresponding to Debian architecture
    for arch, subarch in DEBIAN_ARCHITECTURES:
        if subarch == selected_subarch:
            break
    else:
        raise Exception("This should not happen")
    
    FIELDS = (
        ("Target name", script + "-" + subarch),
    )
    

    
    rootfs_directory_name, = form(
        FIELDS,
        "Target name",
        "Enter directory name to be used for the filesystem root")
        
    # TODO: Check that the path does NOT exist

    run_debootstrap(os.path.join(SOCLE_ROOT_FILESYSTEMS, rootfs_directory_name), script, arch, subarch)
    

def clone_root_filesystem():
    pass

def build_kernel():
    pass
    
def build_bootloader():
    pass

def enter_chroot():
    # Mount /dev, /proc, /sys if neccessary
    # Optionally bind /home

    rootfs = choice(
        [(j,j) for j in os.listdir(SOCLE_ROOT_FILESYSTEMS)],
        "Select distribution",
        "Select distribution to bootstrap"
    )

    pass

def build_image():
    # Images could be one of these
    # 1. SquashFS image of root filesystem
    # 2. Mount loopback device, create DOS partition table, 16MB FAT and remaining ext4 with 1GB chunking
    pass

def build_root_filesystem():
    methods = (
        ("debootstrap",                 debootstrap),
        ("febootstrap",                 NotImplemented),
        ("arch-bootstrap",              NotImplemented),
        ("Gentoo stage3 tarball",       NotImplemented))
    method = choice(
        methods,
        "Bootstrap",
        "Root filesystem bootstrap method")
    method()

def build_profile():
    profiles = set()
    for path in SOCLE_BUILD_PROFILES:
        if not os.path.exists(path):
            continue
        for filename in os.listdir(path):
            if not filename.endswith(".ini"):
                continue
            profiles.add(filename)
           
    profile = choice(
        [(j[:-4],j) for j in sorted(profiles)],
        "Select profile",
        "Select profile to build image"
    )
    
def mainloop():
    MAINMENU = (
        ("Use build profile",                build_profile),
        ("Build custom root filesystem",    build_root_filesystem),
        ("Clone root filesystem",           clone_root_filesystem),
        ("Enter chroot",                    enter_chroot),
        ("Build custom kernel",             build_kernel),
        ("Build custom bootloader",         build_bootloader),
        ("Build image",                     build_image),
    )

    for path in SOCLE_ROOT_FILESYSTEMS, SOCLE_CHROOTS:
        if not os.path.exists(path):
            os.makedirs(path)
    while True:
        try:
            action = choice(
                MAINMENU,
                "SoC image builder",
                "Currently building under ",
                action_cancel="Exit")
            action()
        except CanceledException:
            break

if __name__ == "__main__":
    mainloop()
