from lib import pybixlib
import traceback
from p_class import plugins


class CustomPlugin(plugins.plugin):

    def __init__(self, uuid, taskConf, agentType):
        plugins.plugin.__init__(
            self, uuid, taskConf, agentType)
        self.obj = None

    def getData(self):
        try:
            redata = {"foo": "bar"}
        except Exception:
            pybixlib.error(self.logHead + traceback.format_exc())
            self.errorInfoDone(traceback.format_exc())
            redata = {}
        finally:
            self.setData({'agentType': self.agentType, 'uuid': self.uuid,
                          'code': self.code, 'time': self.getCurTime(),
                          'data': redata, 'error_info': self.error_info})
            self.intStatus()
