import nose
import os

def runTests():
    r"""Run all tests"""
    # Get directory of current file
    cfd = os.path.dirname(os.path.realpath(__file__))
    # Get current working directory
    cwd = os.getcwd()
    # Change current working directory to 'cfd'
    os.chdir(cfd)
    # Run all tests
    result = nose.run(argv = [cfd,"--verbosity=2"])
    # Change current working directory to its previous state
    os.chdir(cwd)

    return result

if __name__ == "__main__":
    runTests()
