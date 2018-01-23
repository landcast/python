#!/usr/bin/env python

import os


class appconfig:
    '''config for sanic app, only UPPER CASE property will be added to config
    '''

    def __init__(self):
        self.upload_location = './uploadtemp'

    @property
    def UPLOAD_LOCATION(self):
        return self.upload_location

    @UPLOAD_LOCATION.setter
    def UPLOAD_LOCATION(self, newlocation):
        ''' check the newlocation exists, if not, create it first, then return
        '''
        if not os.path.exists(newlocation):
            # create the upload folder
            os.makedirs(newlocation)
        self.upload_location = newlocation
