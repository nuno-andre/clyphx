# -*- coding: utf-8 -*-
# This file is part of ClyphX.
#
# ClyphX is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# ClyphX is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for
# more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ClyphX.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import absolute_import, unicode_literals

import Live
from .core import XComponent

BROWSER_TAGS = ('Drums', 'Instruments', 'Audio Effects', 'MIDI Effects', 'Max for Live')


class XM4LBrowserInterface(XComponent):
    '''XM4LBrowserInterface provides access to browser data and
    methods for use in M4L devices.

    NOTE: Lazy initialization is used, get_browser_tags method needs to
    be called first in order to use other methods.
    '''
    __module__ = __name__

    def __init__(self, parent):
        super(XM4LBrowserInterface, self).__init__(parent)
        self._selected_tag = None
        self._selected_device = None
        self._selected_folder = None
        self._selected_item = None
        self._browser = {}

    def disconnect(self):
        self._selected_tag = None
        self._selected_device = None
        self._selected_folder = None
        self._selected_item = None
        self._browser = None
        super(XM4LBrowserInterface, self).disconnect()

    def load_device(self):
        '''Loads the selected device if there is one.'''
        if self._selected_device:
            self.application().browser.load_item(self._selected_device['device'])

    def load_item(self):
        '''Loads the selected item if there is one.'''
        if self._selected_item:
            self.application().browser.load_item(self._selected_item)

    def activate_hotswap(self):
        '''Activates hotswap for the device selected in Live, finds the
        appropriate tag and device to use and returns the items for the
        device.
        '''
        device = self.song().view.selected_track.view.selected_device
        items = []
        if device:
            if self.application().view.browse_mode:
                self.application().view.toggle_browse()
            if device.class_name != 'PluginDevice' and not self._track_contains_browser():
                tag_to_use = None
                device_to_use = device.class_display_name
                if device.can_have_drum_pads:
                    tag_to_use = 'Drums'
                elif device.class_display_name.startswith('Max'):
                    tag_to_use = 'Max for Live'
                elif device.type == Live.Device.DeviceType.audio_effect:
                    tag_to_use = 'Audio Effects'
                elif device.type == Live.Device.DeviceType.midi_effect:
                    tag_to_use = 'MIDI Effects'
                elif device.type == Live.Device.DeviceType.instrument:
                    tag_to_use = 'Instruments'

                if tag_to_use and device_to_use:
                    self.application().view.toggle_browse()
                    self._selected_tag = self._browser[tag_to_use]
                    self._selected_device = self._selected_tag['devices'][device_to_use]
                    items = sorted(self._selected_device['folders'].keys()) + sorted(self._selected_device['items'])
        return items

    def deactivate_hotswap(self):
        '''Deactivates hotswap and closes the browser.'''
        if self.application().view.browse_mode:
            self.application().view.toggle_browse()
            self.application().view.hide_view('Browser')

    def select_non_folder_item(self, item_name):
        '''Stores an item that is not contained within a folder.'''
        self._selected_item = self._selected_device['items'][item_name]

    def select_folder_item(self, item_name):
        '''Stores an item that is contained within a folder.'''
        self._selected_item = self._selected_folder[item_name]

    def get_browser_tags(self):
        '''Returns the list of browser tags. Also, initializes browser
        if it hasn't already been initialized.
        '''
        if not self._browser:
            for tag in self.application().browser.tags:
                if tag.name in BROWSER_TAGS:
                    self._browser[tag.name] = {
                        'tag':     tag,
                        'devices': self._create_devices_for_tag(tag),
                    }
        return BROWSER_TAGS

    def get_devices_for_tag(self, tag_name):
        '''Returns the list of devices for the given tag and stores the
        tag.
        '''
        self._selected_tag = self._browser[tag_name]
        return sorted(self._selected_tag['devices'])

    def get_items_for_device(self, device_name):
        '''Returns the list of folders and items for the given device
        and stores the device.
        '''
        self._selected_device = self._selected_tag['devices'][device_name]
        return sorted(self._selected_device['folders'].keys()) + sorted(self._selected_device['items'])

    def get_items_for_folder(self, folder_name):
        '''Returns the list of items in the given folder and stores the folder.
        '''
        self._selected_folder = self._selected_device['folders'][folder_name]
        return sorted(self._selected_folder)

    def _track_contains_browser(self):
        '''Returns whether or not the selected track contains the Device
        Browser, in which case hotswapping isn't possble.
        '''
        for device in self.song().view.selected_track.devices:
            if device and device.name == 'Device Browser':
                return True
        return False

    def _create_devices_for_tag(self, tag):
        '''Creates dict of devices for the given tag. Special handling
        is needed for M4L tag, which only contains folders, and Drums
        tag, which ontains devices and folders.
        '''
        device_dict = {}
        if tag.name == 'Max for Live':
            for child in tag.children:
                if child.is_folder:
                    for device in child.children:
                        if device.is_device:
                            device_dict[child.name] = {
                                'device':  device,
                                'items':   self._create_items_for_device(child),
                                'folders': {},
                            }
                            break
        else:
            for child in tag.children:
                if child.is_device:
                    if tag.name == 'Drums':
                        device_dict[child.name] = {
                            'device':  child,
                            'items':   self._create_items_for_device(tag),
                            'folders': {},
                        }
                    else:
                        device_dict[child.name] = {
                            'device':  child,
                            'items':   self._create_items_for_device(child),
                            'folders': self._create_folders_for_device(child),
                        }
            if len(device_dict) == 1:
                device_dict[' '] = {}
        return device_dict

    def _create_items_for_device(self, device):
        '''Returns a dict of loadable items for the given device or
        folder.
        '''
        items = {c.name: c for c in device.children
                 if c.is_loadable and c.name != 'Drum Rack'}
        if len(items) == 1:
            items[' '] = {}
        return items

    def _create_folders_for_device(self, device):
        '''Creates dict of folders for the given device.'''
        return {'{} >'.format(c.name): self._create_items_for_device(c)
                for c in device.children if c.is_folder}
