class PluginFactory():

    def instance(cls):
        """get instance of plugin"""
        m = __import__("plugins."+cls.lower(), globals(), locals(), cls)
        c = getattr(m, cls)
        return c()