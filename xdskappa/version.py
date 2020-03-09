
def version_by_pkg():
    try:
        import pkg_resources
        try:
            return pkg_resources.get_distribution('xdskappa')
        except pkg_resources.DistributionNotFound:
            return 'Unknown version.'
        
    except ImportError:
        return 'Unknown, something is wrong with the Python installation'
    
    
    
try:
    import setuptools_scm
    got_version = setuptools_scm.get_version(root='..',relative_to=__file__)

except ImportError:
    got_version = version_by_pkg()

except Exception as e:
    got_version = version_by_pkg() 
    #'\nDevelopment version. Cannot get proper state,\n please install Git, and setuptools_scm and gitpython package.'

    print(e)
    
version = got_version

if __name__ == "__main__":
    print('Version: {}'.format(version))
