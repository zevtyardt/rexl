class Auxilary(object):
    def do_nmap__auxilary(self, param):
        """Utility for network discovery and security auditing"""
        self.do_shell("nmap " + param)

    def do_sqlmap__auxilary(self, param):
        """Automatic SQL injection and database takeover tool"""
        self.do_shell("sqlmap " + param)

    def do_youtube_dl__auxilary(self, param):
        """Youtube video downloader"""
        self.do_shell("youtube-dl " + param)
