import os
import sys
import pkg_resources

def locate(filename):
    path = pkg_resources.resource_filename(__name__, 'klue_docker_templates/%s' % filename)
    if not os.path.isfile(path):
        path = os.path.join(os.path.dirname(sys.modules[__name__].__file__), filename)
    return path
