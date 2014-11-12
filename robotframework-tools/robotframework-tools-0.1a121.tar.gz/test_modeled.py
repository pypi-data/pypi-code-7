
# In[3]:

from robot.conf import RobotSettings
from robot.running import TestSuiteBuilder
from robot.running.runner import Runner


# In[4]:

from robottools.modeled import mTestSuite
from robottools import TestRobot


# In[5]:

r = TestRobot('Test')


# In[6]:

runner = Runner(r._output, RobotSettings())


# In[7]:

tsb = TestSuiteBuilder()


# In[8]:

ts = tsb.build('test.robot')


# In[9]:

ts = mTestSuite(ts)


# In[10]:

ts.source


# In[17]:

ts.tests[0].keywords[0]


# In[13]:

runner.visit_suite(ts)


# In[14]:

runner.result.return_code


# In[ ]:



