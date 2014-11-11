
import os
import sys
import ConfigParser
import subprocess
import tempfile
from socle.boards.generic import GenericBoard
from socle.menu import choice

class SunxiBoard(GenericBoard):
    NAME = "SUNXI"

    # Resetting such board configuration is not possible
    DEFAULT_FEX = None

    # List of boot partitions to probe
    BOOT_PARTITIONS = (
        ("Internal NAND",   "/dev/nand1"),
        ("MicroSD card",    "/dev/mmcblk0p1")
    )

    DISP_MODE_CHOICES = (
        ("Disabled", -1),
        ("HDMI-only", 0),
        ("VGA-only", 1),
        ("Dualhead", 2),
        ("Xinerama", 3),
        ("Clone", 4)
    )

    # HDMI output choices
    SCREEN0_OUTPUT_MODE_CHOICES = (
        ("480i", 0),
        ("576i", 1),
        ("480p", 2),
        ("576p", 3),
        ("720p @ 50Hz", 4),
        ("720p @ 60Hz", 5),
        ("1080i @ 50Hz", 7),
        ("1080p @ 24Hz", 8),
        ("1080p @ 50Hz", 9),
        ("1080p @ 60Hz", 10),
    )

    # VGA output choices
    SCREEN1_OUTPUT_MODE_CHOICES = (
        ("1680x1050", 0),
        ("1440x900", 1),
        ("1360x768", 2),
        ("1280x1024", 3),
        ("1024x768", 4),
        ("800x600", 5),
        ("640x480", 6),
        ("1920x1080", 10),
        ("1280x720", 11)
    )
    
    def __init__(self, script_bin_filename):
        self.script_bin_filename = script_bin_filename
        self.load()

    @classmethod
    def instantiate(cls):
        
        target = choice(
			[(t,bd) for (t,bd) in cls.BOOT_PARTITIONS if os.path.exists(bd)],
            "Target",
            "With this utility you can configure software intalled on internal NAND or SD card")
        mountpoint = tempfile.mkdtemp()
        cmd = "mount", target, mountpoint
        subprocess.call(cmd)
        
        
        return cls(os.path.join(mountpoint, "script.bin"))



    def mainmenu(self):
        return (
            ("Reconfigure video outputs", self.reconfigure_video_outputs),
            ("Reconfigure GPIO pins",     self.reconfigure_gpio)
        )

    def load(self):

        script_fex = tempfile.mktemp()

        subprocess.call(("bin2fex", self.script_bin_filename, script_fex))


        self.fex = ConfigParser.RawConfigParser()
        self.fex.readfp(open(script_fex))
        self.fex.set("usbc0", "usb_used", "1")
        self.fex.set("usbc0", "usb_port_type", "1")
        self.fex.set("usbc0", "usb_detect_type", "0")
        self.save()
        
    def reset(self):
        self.fex.readp(open(self.DEFAULT_FEX))
        
    def save(self):
        script_fex = tempfile.mktemp()
        with open(script_fex, "wb") as configfile:
            self.fex.write(configfile)
        subprocess.call(("fex2bin", script_fex, self.script_bin_filename))

    def reconfigure_video_outputs(self):
        disp_mode = choice(
            self.DISP_MODE_CHOICES,
            "Video output",
            "Select video output mode")
        disp_init_enable = int(disp_mode >= 0)
        
        self.fex.set("disp_init", "disp_mode", disp_mode)
        self.fex.set("disp_init", "disp_init_enable", disp_init_enable)
        if disp_init_enable:
            if disp_mode == 0 or disp_mode >= 2:
                screen0_output_mode = choice(
                    self.SCREEN0_OUTPUT_MODE_CHOICES,
                    "HDMI output resolution",
                    "Select HDMI output resolution")
                self.fex.set("disp_init", "screen0_output_type", "3")
                self.fex.set("disp_init", "screen0_output_mode", screen0_output_mode)

            else:
                self.fex.set("disp_init", "screen0_output_type", "0")

                
            if disp_mode >= 1:
                screen1_output_mode = choice(
                    self.SCREEN1_OUTPUT_MODE_CHOICES,
                    "VGA output resolution",
                    "Select VGA output resolution")
                self.fex.set("disp_init", "screen1_output_type", "4")
                self.fex.set("disp_init", "screen1_output_mode", screen1_output_mode)
            else:
                self.fex.set("disp_init", "screen1_output_type", "0")


            # Hack
            if disp_mode == 1:
                self.fex.set("disp_init", "disp_mode", "0")
                self.fex.set("disp_init", "screen0_output_type", "4")
                self.fex.set("disp_init", "screen1_output_type", "0")
                self.fex.set("disp_init", "screen0_output_mode", screen1_output_mode)
                
            self.fex.set("disp_init", "fb0_scaler_mode_enable", "0")
            self.fex.set("disp_init", "fb1_scaler_mode_enable", "0")

        self.save()

    def reconfigure_gpio(self):
        # UART0 reserved for console, reconfigurable
        # UART1 inactive (?)
        # UART2 reserved for Bluetooth (?)
        # UART3 configurable
        # UART4 configurable
        # UART5 inactive
        # UART6 inactive
        # UART7 configurable

        UART3_TYPE_CHOICES = (
            ("Disabled", 0),
            ("Enabled", 2),
        )

        UART4_TYPE_CHOICES = (
            ("Disabled", 0),
            ("2pin", 2),
            ("4pin", 4),
        )
            
        UART7_TYPE_CHOICES = UART3_TYPE_CHOICES

        uart3_type = choice(
            UART3_TYPE_CHOICES,
            "UART3 configuration",
            "Select UART3 operation mode")
        if uart3_type > 0:
            self.fex.set("uart_para3", "uart_used", "1")
            self.fex.set("uart_para3", "uart_port", "3")
            self.fex.set("uart_para3", "uart_type", uart3_type)
        else:
            self.fex.set("uart_para3", "uart_used", "0")

        uart4_type = choice(
            UART4_TYPE_CHOICES,
            "UART4 configuration",
            "Select UART4 operation mode")
        if uart4_type > 0:
            self.fex.set("uart_para4", "uart_used", "1")
            self.fex.set("uart_para4", "uart_port", "4")
            self.fex.set("uart_para4", "uart_type", uart4_type)
        else:
            self.fex.set("uart_para4", "uart_used", "0")
            
        uart7_type = choice(
            UART7_TYPE_CHOICES,
            "UART7 configuration",
            "Select UART7 operation mode")
        if uart7_type > 0:
            self.fex.set("uart_para7", "uart_used", "1")
            self.fex.set("uart_para7", "uart_port", "7")
            self.fex.set("uart_para7", "uart_type", uart7_type)
        else:
            self.fex.set("uart_para7", "uart_used", "0")

        self.save()
               
if __name__ == "__main__":
    """
    It would be nice to keep "python sunxi.py /path/to/sysconfig.bin" working :)
    """
    sys_config_filename, = sys.argv[1:]
    board = SunxiBoard(sys_config_filename)
    board.reconfigure_video_outputs()
    board.reconfigure_gpio()
    board.save()
