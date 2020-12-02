
from ..model.setting import _Settings
from .. import db


class SettingService():

    def getSetting(self):
        setting = _Settings.query.filter_by(id=1).first()
        if not setting:
            setting = _Settings()
            db.session.add(setting)
            db.session.commit()
        return setting

settingService = SettingService()