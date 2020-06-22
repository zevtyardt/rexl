import shutil

class Auxilary(object):
    def which(self, cmd: str):
        if shutil.which(cmd):
            return True
        self.perror(f"ERROR: {cmd!r} is not installed")

    def do_nmap__auxilary(self, param):
        """Utility for network discovery and security auditing"""
        if self.which("nmap"):
            self.do_shell("nmap " + param)

    def do_sqlmap__auxilary(self, param):
        """Automatic SQL injection and database takeover tool"""
        if self.which("sqlmap"):
            self.do_shell("sqlmap " + param)

    def do_youtube_dl__auxilary(self, param):
        """Youtube video downloader"""
        if self.which("youtube-dl"):
            self.do_shell("youtube-dl " + param)
