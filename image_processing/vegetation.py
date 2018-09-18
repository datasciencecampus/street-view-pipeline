# standalone plugin demo
from plugin_factory import PluginFactory

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 3:
        print(sys.argv[0] + " <Plugin> <image file>")
        sys.exit(0)
        
    plugin = PluginFactory.instance(sys.argv[1])
    veg = plugin.vegetation_from_file(sys.argv[2])
    print("{:.2f}".format(veg))
