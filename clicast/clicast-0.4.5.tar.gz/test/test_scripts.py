import pytest
import subprocess


@pytest.mark.parametrize("script", ['bin/cast-example'])
def test_script(script):

  try:
    subprocess.check_output([script, '-h'], stderr=subprocess.STDOUT)
  except subprocess.CalledProcessError as e:
    print e.output
    assert e.returncode == 0
